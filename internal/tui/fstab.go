package tui

import (
	"fmt"
	"strings"

	"charm.land/lipgloss/v2"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/fs/alloc"
	"github.com/Mariojamjam/practice-os/core/fs/diag"
	"github.com/Mariojamjam/practice-os/internal/render"
	"github.com/Mariojamjam/practice-os/internal/shell"
)

// fsView shows the directory tree beside the disk block map.
func (a *App) fsView(w, h int) string {
	if a.snap.err != nil {
		return styleFailed.Render("Cannot read the file system: " + a.snap.err.Error())
	}
	treeW := max(24, w/3)
	tree := strings.TrimRight(render.Result(shell.TreeResult{Root: a.snap.tree}, render.Options{ASCII: a.opts.ASCII}), "\n")
	left := lipgloss.NewStyle().Width(treeW).MaxWidth(treeW).MaxHeight(h).Render(tree)
	right := a.blockMap(max(20, w-treeW-2), h)
	return lipgloss.JoinHorizontal(lipgloss.Top, left, "  ", right)
}

func (a *App) blockMap(w, h int) string {
	r := a.snap.report
	g := a.glyphs()
	digits := len(fmt.Sprint(r.TotalBlocks - 1))
	perRow := max(4, (w-digits-2)/3)

	var b strings.Builder
	b.WriteString(styleTitle.Render(fmt.Sprintf("Disk map: %s allocation, %d blocks of %s",
		r.Strategy, r.TotalBlocks, config.FormatSize(int64(r.BlockSize)))) + "\n")

	rows := int((r.TotalBlocks + int64(perRow) - 1) / int64(perRow))
	maxRows := max(1, h-6)
	for row := range min(rows, maxRows) {
		fmt.Fprintf(&b, "%*d %s ", digits, row*perRow, styleMuted.Render(g.sep))
		for i := row * perRow; i < min((row+1)*perRow, int(r.TotalBlocks)); i++ {
			b.WriteString(a.cell(r.Blocks[i], r.BlockSize) + " ")
		}
		b.WriteByte('\n')
	}
	if rows > maxRows {
		b.WriteString(styleMuted.Render(fmt.Sprintf("… %d more rows (enlarge the window to see them)", rows-maxRows)) + "\n")
	}

	b.WriteString(a.legend() + "\n")
	used := r.TotalBlocks - r.FreeBlocks
	fmt.Fprintf(&b, "Used %d blocks (%d metadata, %d data) · %d free\n", used, r.MetaBlocks, used-r.MetaBlocks, r.FreeBlocks)
	fmt.Fprintf(&b, "Internal fragmentation %d B · external fragmentation %d B\n", r.Internal, r.External)
	b.WriteString(compactionLine(r))
	return lipgloss.NewStyle().MaxWidth(w).Render(b.String())
}

// cell draws one block: its kind's color, half-shaded when a data block is
// only partly used (internal fragmentation).
func (a *App) cell(blk diag.Block, blockSize int) string {
	g := a.glyphs()
	switch {
	case blk.Kind == diag.KindFree:
		return fg(colMuted).Render(g.free)
	case blk.Kind == diag.KindData && blk.Used < blockSize:
		return fg(colPartial).Render(g.partial)
	case blk.Kind == diag.KindData:
		return fg(colData).Render(g.full)
	}
	glyph := g.full
	if l, ok := g.letters[blk.Kind]; ok {
		glyph = l
	}
	return fg(blockColor(blk.Kind)).Render(glyph)
}

func (a *App) legend() string {
	g := a.glyphs()
	item := func(c lipgloss.Style, glyph, label string) string { return c.Render(glyph) + " " + label }
	meta := func(k diag.BlockKind) string {
		if l, ok := g.letters[k]; ok {
			return l
		}
		return g.full
	}
	items := []string{
		item(fg(colDir), meta(diag.KindDir), "directory"),
		item(fg(colInode), meta(diag.KindFileInode), "inode"),
		item(fg(colFAT), meta(diag.KindFAT), "FAT"),
		item(fg(colData), g.full, "data"),
		item(fg(colPartial), g.partial, "partly used"),
		item(fg(colMuted), g.free, "free"),
	}
	return strings.Join(items, "  ")
}

func compactionLine(r diag.Report) string {
	switch {
	case r.Strategy != alloc.Contiguous:
		return fmt.Sprintf("Compaction needed: NO (%s files need no contiguous space)", r.Strategy)
	case r.CompactionNeeded:
		return styleFailed.Render(fmt.Sprintf(
			"Compaction needed: YES (%d free holes; files over %d blocks do not fit; run compact)",
			len(r.FreeRuns), r.Largest))
	default:
		return "Compaction needed: NO (free space is contiguous)"
	}
}

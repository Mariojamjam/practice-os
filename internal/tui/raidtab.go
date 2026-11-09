package tui

import (
	"fmt"
	"path"
	"slices"
	"strings"

	"charm.land/lipgloss/v2"

	"github.com/Mariojamjam/practice-os/internal/device/ssd"
	"github.com/Mariojamjam/practice-os/internal/diag"
)

// raidView shows the array's disks side by side, stripe by stripe, and
// the wear of any SSDs.
func (a *App) raidView(w, h int) string {
	var parts []string
	if a.snap.raid != nil {
		parts = append(parts, a.raidColumns(w, h-len(a.snap.wear)-1))
		for _, wr := range a.snap.wear {
			parts = append(parts, wearLine(wr))
		}
	} else {
		for _, wr := range a.snap.wear {
			parts = append(parts, a.wearMap(wr, w, h/max(1, len(a.snap.wear))))
		}
	}
	if len(parts) == 0 {
		return styleMuted.Render("The device is a single HDD: there is no array and no flash to show.\n" +
			"Start with --preset stage2 for a RAID 5 of 3 disks, or --device ssd for an SSD.")
	}
	return clip(strings.Join(parts, "\n"), w)
}

func (a *App) raidColumns(w, h int) string {
	v := a.snap.raid
	state := styleOK.Render("healthy")
	failed := 0
	for _, d := range v.disks {
		if d.Failed {
			failed++
		}
	}
	if failed > 0 {
		state = styleFailed.Render(fmt.Sprintf("%d disk(s) failed", failed))
	}
	title := styleTitle.Render(fmt.Sprintf("%s · %d disks · capacity %d blocks · ", v.name, len(v.disks), v.capacity)) + state

	n := len(v.disks)
	colW := max(12, (w-2*(n-1))/n)
	rows := max(1, h-3)
	cols := make([]string, n)
	for i, d := range v.disks {
		var b strings.Builder
		head := styleOK.Render(d.Name + " OK")
		if d.Failed {
			head = styleFailed.Render(d.Name + " FAILED")
		}
		b.WriteString(head + "\n")
		for si, stripe := range v.stripes {
			if si == rows {
				b.WriteString(styleMuted.Render(fmt.Sprintf("… %d more stripes", len(v.stripes)-rows)) + "\n")
				break
			}
			b.WriteString(a.slotLabel(stripe[i].Offset, stripe[i].Block, stripe[i].Parity, d.Failed) + "\n")
		}
		cols[i] = lipgloss.NewStyle().Width(colW).MaxWidth(colW).Render(strings.TrimRight(b.String(), "\n"))
	}
	var row []string
	for i, c := range cols {
		if i > 0 {
			row = append(row, "  ")
		}
		row = append(row, c)
	}
	legend := styleMuted.Render("one row per stripe in use: data blocks with their owner, P = parity (XOR of the row)")
	return title + "\n" + lipgloss.JoinHorizontal(lipgloss.Top, row...) + "\n" + legend
}

func (a *App) slotLabel(stripe, block int64, parity, failed bool) string {
	label := fmt.Sprintf("s%03d ", stripe)
	switch {
	case parity:
		label += fg(colParity).Render("P parity")
	default:
		blk := diag.Block{Kind: diag.KindFree}
		if block >= 0 && block < int64(len(a.snap.report.Blocks)) {
			blk = a.snap.report.Blocks[block]
		}
		text := fmt.Sprintf("%03d %s", block, strings.ToLower(string(blk.Kind)))
		if blk.Path != "" {
			text += " " + path.Base(blk.Path)
			if blk.Kind == diag.KindData {
				text += fmt.Sprintf("#%d", blk.Seq)
			}
		}
		label += fg(blockColor(blk.Kind)).Render(text)
	}
	if failed {
		label = styleFailed.Render("✗ ") + label
	}
	return label
}

// wearMap draws an SSD's flash pages shaded by how often each was erased.
func (a *App) wearMap(wr ssd.Wear, w, h int) string {
	g := a.glyphs()
	var b strings.Builder
	b.WriteString(wearLine(wr) + "\n")
	hi := slices.Max(wr.Erases)
	perRow := max(4, (w-6)/3)
	rows := (len(wr.Erases) + perRow - 1) / perRow
	maxRows := max(1, h-3)
	for row := range min(rows, maxRows) {
		fmt.Fprintf(&b, "%4d %s ", row*perRow, styleMuted.Render(g.sep))
		for p := row * perRow; p < min((row+1)*perRow, len(wr.Erases)); p++ {
			level := 0
			if hi > 0 {
				level = wr.Erases[p] * (len(g.heat) - 1) / hi
			}
			c := colData
			if level >= 2 {
				c = colPartial
			}
			if wr.Erases[p] == 0 {
				c = colMuted
			}
			b.WriteString(fg(c).Render(g.heat[level]) + " ")
		}
		b.WriteByte('\n')
	}
	if rows > maxRows {
		b.WriteString(styleMuted.Render(fmt.Sprintf("… %d more rows", rows-maxRows)) + "\n")
	}
	b.WriteString(styleMuted.Render("darker = more erases; wear leveling keeps the pages even"))
	return b.String()
}

func wearLine(wr ssd.Wear) string {
	total := 0
	for _, e := range wr.Erases {
		total += e
	}
	return styleTitle.Render(fmt.Sprintf("%s · %d logical blocks on %d flash pages · erases: min %d, max %d, total %d",
		wr.Name, wr.Logical, wr.Physical, slices.Min(wr.Erases), slices.Max(wr.Erases), total))
}

package tui

import (
	"fmt"
	"strings"

	"charm.land/lipgloss/v2"

	"github.com/Mariojamjam/practice-os/core/storage/blockio"
	"github.com/Mariojamjam/practice-os/core/storage/sched"
	"github.com/Mariojamjam/practice-os/ui/render"
)

// ioView draws the last I/O each device served: the disk-arm path of each
// HDD over time, SSD page writes, and RAID events, plus what is queued.
func (a *App) ioView(w, h int) string {
	var blocks []string
	hdds := 0
	for _, f := range a.lastIO {
		if f.Sched != nil {
			hdds++
		}
	}
	budget := h - 2
	if hdds > 0 {
		budget = max(3, (h-2)/hdds-2)
	}
	for _, f := range a.lastIO {
		switch {
		case f.Kind == blockio.KindRAID:
			blocks = append(blocks, strings.TrimRight(render.IO([]blockio.Flush{f}, render.Options{}), "\n"))
		case f.Kind == blockio.KindSSD:
			blocks = append(blocks, ssdFlush(f))
		case f.Sched != nil:
			blocks = append(blocks, a.armPath(f, w, budget))
		}
	}
	if len(blocks) == 0 {
		blocks = append(blocks, styleMuted.Render(
			"No I/O served yet. File commands (mkdir, create, read_file…) issue block requests;\n"+
				"the disk serves them when the command ends, or on io_flush when io_defer is on.\n"+
				"For a standalone schedule, try: sched --queue 98,183,37,122,14 --head 53"))
	}
	if q := pendingLine(a.snap.pending); q != "" {
		blocks = append(blocks, q)
	}
	return clip(strings.Join(blocks, "\n"), w)
}

// armPath draws the head's path: one row per stop, with the head placed
// along a track axis, so the movement reads top to bottom over time.
func (a *App) armPath(f blockio.Flush, w, rows int) string {
	g := a.glyphs()
	res := *f.Sched
	tracks := a.k.Config.Disk.TrackCount()
	axisW := max(10, w-24)
	pos := func(t int) int {
		if tracks <= 1 {
			return 0
		}
		return t * (axisW - 1) / (tracks - 1)
	}

	var b strings.Builder
	b.WriteString(styleTitle.Render(fmt.Sprintf("%s · %s · head %d → %d · %d tracks moved · %d requests",
		f.Device, res.Algorithm.Title(), res.Start, res.End, res.Total, len(f.Requests))) + "\n")
	last := fmt.Sprint(tracks - 1)
	fmt.Fprintf(&b, "%6s 0%s%s\n", "track", strings.Repeat(g.axis, max(1, axisW-1-len(last))), last)

	type row struct {
		track       int
		glyph, note string
	}
	all := []row{{res.Start, g.head, "start"}}
	for _, s := range res.Stops {
		glyph, note := g.head, fmt.Sprintf("+%d", s.Move)
		switch s.Kind {
		case sched.Edge:
			glyph, note = g.edge, "edge"
		case sched.Jump:
			glyph, note = g.jump, "jump back"
		}
		all = append(all, row{s.Track, glyph, note})
	}
	all = all[:a.armFrame(len(all))]
	if len(all) > rows {
		skipped := len(all) - rows
		all = all[skipped:]
		b.WriteString(styleMuted.Render(fmt.Sprintf("%6s … %d earlier stops", "", skipped)) + "\n")
	}
	for _, r := range all {
		line := strings.Repeat(" ", pos(r.track)) + fg(colAccent).Render(r.glyph)
		pad := axisW - pos(r.track) - 1
		fmt.Fprintf(&b, "%6d %s%s %s\n", r.track, line, strings.Repeat(" ", max(0, pad)), styleMuted.Render(r.note))
	}
	return strings.TrimRight(b.String(), "\n")
}

func ssdFlush(f blockio.Flush) string {
	reads, writes := 0, 0
	var pages []string
	for _, r := range f.Requests {
		if r.Op == blockio.Read {
			reads++
			continue
		}
		writes++
		pages = append(pages, fmt.Sprintf("%d→%d", r.Block, r.Track))
	}
	line := styleTitle.Render(fmt.Sprintf("%s · %d reads, %d writes, %d pages erased · no head, no seek",
		f.Device, reads, writes, f.Erases))
	if len(pages) > 0 {
		line += "\n  writes (logical→page): " + strings.Join(pages, ", ")
	}
	return line
}

func pendingLine(pending []blockio.Flush) string {
	var parts []string
	for _, f := range pending {
		if n := len(f.Requests); n > 0 {
			parts = append(parts, fmt.Sprintf("%s: %d", f.Device, n))
		}
	}
	if len(parts) == 0 {
		return ""
	}
	return lipgloss.NewStyle().Foreground(colPartial).Render(
		"Queued, not served yet (io_defer on): " + strings.Join(parts, " · ") + " requests — run io_flush")
}

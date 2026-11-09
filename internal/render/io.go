package render

import (
	"fmt"
	"math"
	"reflect"
	"slices"
	"strconv"
	"strings"

	"github.com/Mariojamjam/practice-os/internal/blockio"
	"github.com/Mariojamjam/practice-os/internal/config"
	"github.com/Mariojamjam/practice-os/internal/device/ssd"
	"github.com/Mariojamjam/practice-os/internal/diag"
	"github.com/Mariojamjam/practice-os/internal/sched"
	"github.com/Mariojamjam/practice-os/internal/shell"
)

// IO renders the I/O flushes of a command (see shell.Shell.LastIO).
func IO(flushes []blockio.Flush, _ Options) string {
	var b strings.Builder
	for i, f := range flushes {
		if i > 0 {
			b.WriteByte('\n')
		}
		flush(&b, f)
	}
	return b.String()
}

func flush(b *strings.Builder, f blockio.Flush) {
	switch f.Kind {
	case blockio.KindRAID:
		// Identical consecutive events (the same block read again) are
		// shown once with a count.
		for i := 0; i < len(f.Events); {
			j := i + 1
			for j < len(f.Events) && reflect.DeepEqual(f.Events[j], f.Events[i]) {
				j++
			}
			line := event(f.Events[i])
			if j-i > 1 {
				line += fmt.Sprintf(" (x%d)", j-i)
			}
			fmt.Fprintf(b, "[%s] %s\n", f.Device, line)
			i = j
		}
	case blockio.KindSSD:
		fmt.Fprintf(b, "[I/O - %s] %s, served in arrival order (no head to move): [%s]\n",
			f.Device, plural(int64(len(f.Requests)), "request"), ssdRequests(f.Requests))
		fmt.Fprintf(b, "Flash pages erased: %d\n", f.Erases)
	default:
		fmt.Fprintf(b, "[I/O - %s] Pending read/write requests on tracks: [%s]\n", f.Device, hddRequests(f.Requests))
		if f.Sched != nil {
			headLine(b, *f.Sched)
			b.WriteByte('\n')
			schedule(b, *f.Sched)
		}
	}
}

func hddRequests(reqs []blockio.Request) string {
	parts := make([]string, len(reqs))
	for i, r := range reqs {
		parts[i] = fmt.Sprintf("%s %d", r.Op, r.Track)
	}
	return strings.Join(parts, ", ")
}

func ssdRequests(reqs []blockio.Request) string {
	parts := make([]string, len(reqs))
	for i, r := range reqs {
		page := fmt.Sprintf("page %d", r.Track)
		if r.Track == ssd.Unmapped {
			page = "unmapped"
		}
		parts[i] = fmt.Sprintf("%s %d->%s", r.Op, r.Block, page)
	}
	return strings.Join(parts, ", ")
}

func event(e blockio.Event) string {
	failed := fmt.Sprintf("Disk %d", e.Disk)
	switch {
	case e.Kind == blockio.DegradedRead && e.Parity:
		return fmt.Sprintf("%s has failed: block %d rebuilt by XOR of %s [OK]", failed, e.Block, disks(e.Sources))
	case e.Kind == blockio.DegradedRead:
		return fmt.Sprintf("%s has failed: block %d read from mirror %s [OK]", failed, e.Block, disks(e.Sources))
	case e.Parity:
		return fmt.Sprintf("%s has failed: block %d written through the parity, recomputed from %s [OK]", failed, e.Block, disks(e.Sources))
	default:
		return fmt.Sprintf("%s has failed: block %d written to %s only [OK]", failed, e.Block, disks(e.Sources))
	}
}

// disks formats 1-based disk numbers: "Disk 1", "Disk 1 and Disk 3",
// "Disk 1, Disk 2 and Disk 4".
func disks(nums []int) string {
	names := make([]string, len(nums))
	for i, n := range nums {
		names[i] = fmt.Sprintf("Disk %d", n)
	}
	if len(names) <= 1 {
		return strings.Join(names, "")
	}
	return strings.Join(names[:len(names)-1], ", ") + " and " + names[len(names)-1]
}

func headLine(b *strings.Builder, r sched.Result) {
	fmt.Fprintf(b, "Current head position: track %d", r.Start)
	if r.Algorithm == sched.SCAN || r.Algorithm == sched.CSCAN {
		// The direction only matters to the sweeping algorithms.
		fmt.Fprintf(b, " (moving %s)", directionOf(r))
	}
	b.WriteByte('\n')
}

// directionOf recovers the starting direction of a sweep from its path.
func directionOf(r sched.Result) sched.Direction {
	for _, s := range r.Stops {
		switch {
		case s.Track > r.Start:
			return sched.Up
		case s.Track < r.Start:
			return sched.Down
		}
	}
	return r.EndDir
}

func schedule(b *strings.Builder, r sched.Result) {
	fmt.Fprintf(b, "--- DISK SCHEDULING: %s ---\n", r.Algorithm.Title())
	if len(r.Stops) == 0 {
		b.WriteString("Nothing to serve.\n")
		return
	}
	order := []string{fmt.Sprint(r.Start)}
	var segments, moves []string
	prev := r.Start
	for _, s := range r.Stops {
		label := fmt.Sprint(s.Track)
		switch s.Kind {
		case sched.Edge:
			label += " (edge)"
		case sched.Jump:
			label += " (jump)"
		}
		order = append(order, label)
		segments = append(segments, fmt.Sprintf("|%d-%d|", prev, s.Track))
		moves = append(moves, fmt.Sprint(s.Move))
		prev = s.Track
	}
	fmt.Fprintf(b, "Service order  : %s\n", strings.Join(order, " -> "))
	fmt.Fprintf(b, "Head movement  : %s\n", strings.Join(segments, " + "))
	if len(moves) == 1 {
		fmt.Fprintf(b, "Total movement : %s\n", plural(int64(r.Total), "track"))
		return
	}
	fmt.Fprintf(b, "Total movement : %s = %s\n", strings.Join(moves, " + "), plural(int64(r.Total), "track"))
}

func schedResult(b *strings.Builder, r shell.SchedResult) {
	reqs := make([]string, len(r.Requests))
	for i, t := range r.Requests {
		reqs[i] = fmt.Sprint(t)
	}
	fmt.Fprintf(b, "[I/O] Pending requests on tracks: [%s]\n", strings.Join(reqs, ", "))
	headLine(b, r.Result)
	b.WriteByte('\n')
	schedule(b, r.Result)
}

func ioResult(b *strings.Builder, r shell.IOResult) {
	if len(r.Flushes) == 0 {
		b.WriteString("No pending I/O requests.\n")
		return
	}
	if !r.Pending {
		b.WriteString(IO(r.Flushes, Options{}))
		return
	}
	for _, f := range r.Flushes {
		switch f.Kind {
		case blockio.KindRAID:
			fmt.Fprintf(b, "[I/O QUEUE - %s] %s waiting to be reported\n", f.Device, plural(int64(len(f.Events)), "event"))
		case blockio.KindSSD:
			fmt.Fprintf(b, "[I/O QUEUE - %s] %s: [%s]\n", f.Device, plural(int64(len(f.Requests)), "request"), ssdRequests(f.Requests))
		default:
			fmt.Fprintf(b, "[I/O QUEUE - %s] %s on tracks: [%s]\n", f.Device, plural(int64(len(f.Requests)), "request"), hddRequests(f.Requests))
		}
	}
}

func raidStatus(b *strings.Builder, r shell.RAIDStatusResult) {
	fmt.Fprintf(b, "Active array: %s (%d physical disks, %s blocks) | capacity: %s (%s)\n",
		r.Name, len(r.Disks), config.FormatSize(int64(r.BlockSize)),
		plural(r.Capacity, "block"), config.FormatSize(r.Capacity*int64(r.BlockSize)))
	states := make([]string, len(r.Disks))
	for i, d := range r.Disks {
		state := "OK"
		if d.Failed {
			state = "FAILED"
		}
		states[i] = d.Name + ": " + state
	}
	b.WriteString(strings.Join(states, " | ") + "\n")

	title := "[I/O - DISK DISTRIBUTION]"
	if r.Path != "" {
		title = fmt.Sprintf("[I/O - DISK DISTRIBUTION OF '%s']", r.Path)
	}
	b.WriteString("\n" + title + "\n")
	if len(r.Stripes) == 0 {
		b.WriteString("No blocks in use.\n")
	}
	total := r.Report.TotalBlocks
	for _, stripe := range r.Stripes {
		fmt.Fprintf(b, "Stripe %s:\n", blockNum(stripe[0].Offset, total))
		var data []string
		for _, slot := range stripe {
			if !slot.Parity && !slices.Contains(data, blockNum(slot.Block, total)) {
				data = append(data, blockNum(slot.Block, total))
			}
		}
		for _, slot := range stripe {
			d := r.Disks[slot.Disk]
			var content string
			switch {
			case slot.Parity:
				content = fmt.Sprintf("[PARITY: XOR(block %s)]", strings.Join(data, ", block "))
			default:
				content = "[" + slotOwner(slot.Block, r.Report) + "]"
				if r.Level == 1 && slot.Disk > 0 {
					content += " (mirror)"
				}
			}
			if d.Failed {
				content += " (lost: disk failed)"
			}
			fmt.Fprintf(b, "  %s: %s\n", d.Name, content)
		}
	}
}

func slotOwner(block int64, report diag.Report) string {
	num := "block " + blockNum(block, report.TotalBlocks)
	if block < 0 || block >= int64(len(report.Blocks)) {
		return num
	}
	blk := report.Blocks[block]
	if blk.Kind == diag.KindFree {
		return num + ": free"
	}
	return fmt.Sprintf("%s: %s %s", num, blk.Kind, describe(blk, report))
}

func failResult(b *strings.Builder, r shell.FailResult) {
	fmt.Fprintf(b, "[SIMULATED FAILURE] Disk %d failed and its contents were wiped.\n", r.Disk)
	switch r.Level {
	case 0:
		fmt.Fprintf(b, "%s has no redundancy: data stored on Disk %d is lost.\n", r.Array, r.Disk)
	case 1:
		fmt.Fprintf(b, "%s is degraded: reads use the surviving mirrors.\n", r.Array)
	default:
		fmt.Fprintf(b, "%s is degraded: blocks on Disk %d are rebuilt by XOR of the other disks when read.\n", r.Array, r.Disk)
	}
}

func rebuildResult(b *strings.Builder, r shell.RebuildResult) {
	for _, rb := range r.Rebuilt {
		how := "copied from " + disks(rb.Sources)
		if rb.Parity {
			how = "rebuilt by XOR of " + disks(rb.Sources)
		}
		fmt.Fprintf(b, "[%s REBUILD] Disk %d replaced: %s %s [OK]\n", r.Array, rb.Disk, plural(rb.Blocks, "block"), how)
	}
}

func wearResult(b *strings.Builder, r shell.WearResult) {
	for i, w := range r.Wear {
		if i > 0 {
			b.WriteByte('\n')
		}
		fmt.Fprintf(b, "[SSD WEAR - %s] %d logical blocks on %d flash pages (%d spare)\n",
			w.Name, w.Logical, w.Physical, w.Physical-w.Logical)
		fmt.Fprintf(b, "Erases per page : %s\n", stats(w.Erases))
		fmt.Fprintf(b, "Writes per page : %s\n", stats(w.Programs))

		counts := map[int]int64{}
		for _, e := range w.Erases {
			counts[e]++
		}
		var levels []int
		for e := range counts {
			levels = append(levels, e)
		}
		slices.Sort(levels)
		var dist []string
		for _, e := range levels {
			dist = append(dist, fmt.Sprintf("%s: %s", plural(int64(e), "erase"), plural(counts[e], "page")))
		}
		fmt.Fprintf(b, "Distribution    : %s\n", strings.Join(dist, " | "))

		var mapped []string
		for l, p := range w.Mapping {
			if p != ssd.Unmapped {
				mapped = append(mapped, fmt.Sprintf("%d->%d", l, p))
			}
		}
		if len(mapped) == 0 {
			mapped = []string{"(nothing written yet)"}
		}
		fmt.Fprintf(b, "FTL (logical -> page): %s\n", strings.Join(mapped, ", "))
	}
}

func stats(xs []int) string {
	if len(xs) == 0 {
		return "-"
	}
	total := 0
	for _, x := range xs {
		total += x
	}
	avg := math.Round(float64(total)/float64(len(xs))*100) / 100
	return fmt.Sprintf("min %d | max %d | average %s", slices.Min(xs), slices.Max(xs),
		strconv.FormatFloat(avg, 'f', -1, 64))
}

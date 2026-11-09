package render_test

import (
	"strings"
	"testing"

	"github.com/Mariojamjam/practice-os/core/storage/blockio"
	"github.com/Mariojamjam/practice-os/core/storage/sched"
	"github.com/Mariojamjam/practice-os/core/storage/ssd"
	"github.com/Mariojamjam/practice-os/internal/render"
	"github.com/Mariojamjam/practice-os/internal/shell"
)

func contains(t *testing.T, got string, wants ...string) {
	t.Helper()
	for _, w := range wants {
		if !strings.Contains(got, w) {
			t.Errorf("missing %q in:\n%s", w, got)
		}
	}
}

func TestRAIDEvents(t *testing.T) {
	read := blockio.Event{Kind: blockio.DegradedRead, Block: 7, Disk: 2, Sources: []int{1, 3, 4}, Parity: true}
	got := render.IO([]blockio.Flush{{Device: "RAID 5", Kind: blockio.KindRAID, Events: []blockio.Event{
		read, read,
		{Kind: blockio.DegradedRead, Block: 3, Disk: 1, Sources: []int{2}},
		{Kind: blockio.DegradedWrite, Block: 3, Disk: 1, Sources: []int{2, 3}},
		{Kind: blockio.DegradedWrite, Block: 9, Disk: 2, Sources: []int{1, 3}, Parity: true},
	}}}, render.Options{})
	want := "[RAID 5] Disk 2 has failed: block 7 rebuilt by XOR of Disk 1, Disk 3 and Disk 4 [OK] (x2)\n" +
		"[RAID 5] Disk 1 has failed: block 3 read from mirror Disk 2 [OK]\n" +
		"[RAID 5] Disk 1 has failed: block 3 written to Disk 2 and Disk 3 only [OK]\n" +
		"[RAID 5] Disk 2 has failed: block 9 written through the parity, recomputed from Disk 1 and Disk 3 [OK]\n"
	if got != want {
		t.Errorf("got\n%s\nwant\n%s", got, want)
	}
}

func TestHDDAndSSDFlushes(t *testing.T) {
	res, err := sched.Schedule(sched.SSTF, 5, sched.Up, []int{3}, 10)
	if err != nil {
		t.Fatal(err)
	}
	got := render.IO([]blockio.Flush{
		{Device: "HDD", Kind: blockio.KindHDD, Requests: []blockio.Request{{Op: blockio.Read, Block: 3, Track: 3}}, Sched: &res},
		{Device: "SSD", Kind: blockio.KindSSD, Erases: 1, Requests: []blockio.Request{
			{Op: blockio.Read, Block: 0, Track: ssd.Unmapped},
			{Op: blockio.Write, Block: 2, Track: 17},
		}},
	}, render.Options{})
	contains(t, got,
		"[I/O - HDD] Pending read/write requests on tracks: [R 3]\n",
		"Current head position: track 5\n",
		"Service order  : 5 -> 3\n",
		"Total movement : 2 tracks\n",
		"\n[I/O - SSD] 2 requests, served in arrival order (no head to move): [R 0->unmapped, W 2->page 17]\n",
		"Flash pages erased: 1\n",
	)
}

func TestIOResult(t *testing.T) {
	if got := render.Result(shell.IOResult{Pending: true}, render.Options{}); got != "No pending I/O requests.\n" {
		t.Errorf("empty queue = %q", got)
	}
	got := render.Result(shell.IOResult{Pending: true, Flushes: []blockio.Flush{
		{Device: "RAID 1", Kind: blockio.KindRAID, Events: []blockio.Event{{}}},
		{Device: "Disk 1", Kind: blockio.KindHDD, Requests: []blockio.Request{{Op: blockio.Write, Block: 4, Track: 2}}},
	}}, render.Options{})
	want := "[I/O QUEUE - RAID 1] 1 event waiting to be reported\n[I/O QUEUE - Disk 1] 1 request on tracks: [W 2]\n"
	if got != want {
		t.Errorf("got\n%s\nwant\n%s", got, want)
	}
}

func TestFailAndRebuild(t *testing.T) {
	cases := map[int]string{
		0: "RAID 0 has no redundancy: data stored on Disk 2 is lost.\n",
		1: "RAID 1 is degraded: reads use the surviving mirrors.\n",
		5: "RAID 5 is degraded: blocks on Disk 2 are rebuilt by XOR of the other disks when read.\n",
	}
	for level, want := range cases {
		name := map[int]string{0: "RAID 0", 1: "RAID 1", 5: "RAID 5"}[level]
		got := render.Result(shell.FailResult{Array: name, Level: level, Disk: 2}, render.Options{})
		contains(t, got, "[SIMULATED FAILURE] Disk 2 failed and its contents were wiped.\n", want)
	}
	got := render.Result(shell.RebuildResult{Array: "RAID 1", Rebuilt: nil}, render.Options{})
	if got != "" {
		t.Errorf("nothing rebuilt = %q", got)
	}
}

func TestWear(t *testing.T) {
	got := render.Result(shell.WearResult{Wear: []ssd.Wear{{
		Name: "SSD", Logical: 2, Physical: 4,
		Erases:   []int{1, 0, 2, 0},
		Programs: []int{2, 1, 3, 0},
		Mapping:  []int64{1, ssd.Unmapped},
	}}}, render.Options{})
	want := "[SSD WEAR - SSD] 2 logical blocks on 4 flash pages (2 spare)\n" +
		"Erases per page : min 0 | max 2 | average 0.75\n" +
		"Writes per page : min 0 | max 3 | average 1.5\n" +
		"Distribution    : 0 erases: 2 pages | 1 erase: 1 page | 2 erases: 1 page\n" +
		"FTL (logical -> page): 0->1\n"
	if got != want {
		t.Errorf("got\n%s\nwant\n%s", got, want)
	}
}

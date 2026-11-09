package hdd_test

import (
	"errors"
	"testing"

	"github.com/Mariojamjam/practice-os/core/storage/blockio"
	"github.com/Mariojamjam/practice-os/core/storage/disk"
	"github.com/Mariojamjam/practice-os/core/storage/hdd"
	"github.com/Mariojamjam/practice-os/core/storage/sched"
)

func newHDD(t *testing.T, c hdd.Config, blocks int64) *hdd.HDD {
	t.Helper()
	h, err := hdd.New(disk.New(512, blocks), c)
	if err != nil {
		t.Fatal(err)
	}
	return h
}

func TestGeometry(t *testing.T) {
	h := newHDD(t, hdd.Config{Name: "HDD", Tracks: 10, BlocksPerTrack: 4, Scheduler: sched.FCFS, Direction: sched.Up}, 40)
	for b, want := range map[int64]int64{0: 0, 3: 0, 4: 1, 39: 9} {
		if got := h.Track(b); got != want {
			t.Errorf("Track(%d) = %d, want %d", b, got, want)
		}
	}
	if h.BlockCount() != 40 || h.BlockSize() != 512 || h.Tracks() != 10 || h.Name() != "HDD" {
		t.Error("geometry accessors")
	}
}

func TestQueueAndSchedule(t *testing.T) {
	h := newHDD(t, hdd.Config{Name: "HDD", Tracks: 200, BlocksPerTrack: 1, Scheduler: sched.SSTF, Head: 53, Direction: sched.Up}, 200)
	for _, b := range []int64{98, 183, 37} {
		if err := h.Write(b, []byte("x")); err != nil {
			t.Fatal(err)
		}
	}
	for _, b := range []int64{122, 14} {
		if _, err := h.Read(b); err != nil {
			t.Fatal(err)
		}
	}
	if _, err := h.Read(500); err == nil {
		t.Fatal("out-of-range read must fail")
	}

	pending := h.Pending()
	if len(pending) != 1 || len(pending[0].Requests) != 5 || pending[0].Sched != nil {
		t.Fatalf("pending = %+v", pending)
	}
	if r := pending[0].Requests[0]; r != (blockio.Request{Op: blockio.Write, Block: 98, Track: 98}) {
		t.Errorf("first request = %+v", r)
	}

	// The disk-scheduling scenario: SSTF from track 53.
	flushes := h.Flush()
	if len(flushes) != 1 || flushes[0].Sched == nil || flushes[0].Sched.Total != 208 {
		t.Fatalf("flush = %+v", flushes)
	}
	if h.Head() != 183 || h.Direction() != sched.Up || h.Pending() != nil || h.Flush() != nil {
		t.Errorf("after flush: head %d, pending %v", h.Head(), h.Pending())
	}

	// The head stays where the last flush left it.
	if _, err := h.Read(180); err != nil {
		t.Fatal(err)
	}
	if got := h.Flush()[0].Sched; got.Start != 183 || got.Total != 3 || h.Direction() != sched.Down {
		t.Errorf("second flush: %+v", got)
	}
}

func TestDataIsImmediate(t *testing.T) {
	h := newHDD(t, hdd.Config{Name: "HDD", Tracks: 4, BlocksPerTrack: 1, Scheduler: sched.FCFS, Direction: sched.Up}, 4)
	if err := h.Write(2, []byte("now")); err != nil {
		t.Fatal(err)
	}
	got, _ := h.Read(2) // still queued, but the data is already there
	if string(got[:3]) != "now" {
		t.Errorf("read = %q", got[:3])
	}
	h.Discard()
	if h.Pending() != nil {
		t.Error("Discard left requests")
	}
}

func TestInvalidConfig(t *testing.T) {
	cases := []hdd.Config{
		{Tracks: 0, BlocksPerTrack: 1, Scheduler: sched.FCFS, Direction: sched.Up},
		{Tracks: 3, BlocksPerTrack: 1, Scheduler: sched.FCFS, Direction: sched.Up},
		{Tracks: 4, BlocksPerTrack: 1, Scheduler: sched.FCFS, Direction: sched.Up, Head: 4},
		{Tracks: 4, BlocksPerTrack: 1, Scheduler: "look", Direction: sched.Up},
		{Tracks: 4, BlocksPerTrack: 1, Scheduler: sched.FCFS},
	}
	for _, c := range cases {
		if _, err := hdd.New(disk.New(512, 4), c); !errors.Is(err, hdd.ErrInvalid) {
			t.Errorf("%+v: error = %v", c, err)
		}
	}
}

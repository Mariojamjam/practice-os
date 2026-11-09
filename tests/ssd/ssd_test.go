package ssd_test

import (
	"errors"
	"slices"
	"testing"

	"github.com/Mariojamjam/practice-os/internal/blockio"
	"github.com/Mariojamjam/practice-os/internal/device/ssd"
	"github.com/Mariojamjam/practice-os/internal/disk"
)

func TestSpare(t *testing.T) {
	for logical, want := range map[int64]int64{4: 2, 16: 2, 17: 3, 200: 25} {
		if got := ssd.SpareFor(logical); got != want {
			t.Errorf("SpareFor(%d) = %d, want %d", logical, got, want)
		}
	}
}

func TestReadWrite(t *testing.T) {
	s := ssd.New("SSD", 512, 16)
	if s.BlockCount() != 16 || s.BlockSize() != 512 {
		t.Fatal("geometry")
	}
	got, err := s.Read(3)
	if err != nil || len(got) != 512 || got[0] != 0 {
		t.Fatalf("unwritten block: %v", err)
	}
	if err := s.Write(3, []byte("v1")); err != nil {
		t.Fatal(err)
	}
	if err := s.Write(3, []byte("v2")); err != nil {
		t.Fatal(err)
	}
	if got, _ := s.Read(3); string(got[:2]) != "v2" {
		t.Errorf("read = %q", got[:2])
	}
	if _, err := s.Read(16); !errors.Is(err, disk.ErrOutOfRange) {
		t.Errorf("out of range: %v", err)
	}
	if err := s.Write(0, make([]byte, 513)); !errors.Is(err, disk.ErrTooLarge) {
		t.Errorf("too large: %v", err)
	}

	w := s.Wear()
	// The first write went to page 0, the second to page 1, then page 0
	// (the stale version) was erased.
	if w.Mapping[3] != 1 || w.Erases[0] != 1 || w.Programs[0] != 1 || w.Programs[1] != 1 || w.Physical != 18 {
		t.Errorf("wear = %+v", w)
	}

	flushes := s.Flush()
	if len(flushes) != 1 || flushes[0].Kind != blockio.KindSSD || flushes[0].Erases != 1 || flushes[0].Sched != nil {
		t.Fatalf("flush = %+v", flushes)
	}
	reqs := flushes[0].Requests
	if len(reqs) != 4 || reqs[0].Track != ssd.Unmapped || reqs[1] != (blockio.Request{Op: blockio.Write, Block: 3, Track: 0}) {
		t.Errorf("requests = %+v", reqs)
	}
	if s.Flush() != nil {
		t.Error("second flush should be empty")
	}
}

// Rewriting one block over and over must spread erases over every page.
func TestWearLeveling(t *testing.T) {
	s := ssd.New("SSD", 512, 16)
	for i := range 100 {
		if err := s.Write(0, []byte{byte(i)}); err != nil {
			t.Fatal(err)
		}
	}
	w := s.Wear()
	if got, _ := s.Read(0); got[0] != 99 {
		t.Errorf("latest value = %d", got[0])
	}
	lo, hi := slices.Min(w.Erases), slices.Max(w.Erases)
	total := 0
	for _, e := range w.Erases {
		total += e
	}
	if total != 99 || hi-lo > 1 {
		t.Errorf("erases %v: total %d, spread %d..%d", w.Erases, total, lo, hi)
	}
}

func TestPendingAndDiscard(t *testing.T) {
	s := ssd.New("SSD", 512, 4)
	if s.Pending() != nil {
		t.Error("pending on a fresh SSD")
	}
	if err := s.Write(1, nil); err != nil {
		t.Fatal(err)
	}
	if p := s.Pending(); len(p) != 1 || len(p[0].Requests) != 1 {
		t.Errorf("pending = %+v", p)
	}
	s.Discard()
	if s.Pending() != nil || s.Flush() != nil {
		t.Error("Discard left work")
	}
}

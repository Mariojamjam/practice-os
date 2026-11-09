package raid_test

import (
	"bytes"
	"errors"
	"fmt"
	"testing"

	"github.com/Mariojamjam/practice-os/internal/blockio"
	"github.com/Mariojamjam/practice-os/internal/disk"
	"github.com/Mariojamjam/practice-os/internal/raid"
)

// checkParity verifies, straight from the disks, that every stripe's
// parity block is the XOR of its data blocks.
func checkParity(t *testing.T, r *raid.RAID, disks []*disk.Disk) {
	t.Helper()
	for s := range r.Stripes() {
		x := make([]byte, blockSize)
		for _, d := range disks {
			for i, b := range raw(t, d, s) {
				x[i] ^= b
			}
		}
		if !bytes.Equal(x, make([]byte, blockSize)) {
			t.Fatalf("stripe %d: parity is not the XOR of the data", s)
		}
	}
}

func parityDisks(r *raid.RAID) []int {
	var out []int
	for s := range r.Stripes() {
		for _, slot := range r.Stripe(s) {
			if slot.Parity {
				out = append(out, slot.Disk)
			}
		}
	}
	return out
}

func TestParityLayout(t *testing.T) {
	r4, _ := newArray(t, 4, 3, 4)
	if got := fmt.Sprint(parityDisks(r4)); got != "[2 2 2 2]" {
		t.Errorf("RAID 4 parity disks = %s", got)
	}
	r5, _ := newArray(t, 5, 3, 4)
	if got := fmt.Sprint(parityDisks(r5)); got != "[2 1 0 2]" {
		t.Errorf("RAID 5 parity disks = %s", got)
	}
	// Example 2.2: blocks 0 and 1 on disks 1 and 2, parity on disk 3.
	s0 := r5.Stripe(0)
	if s0[0].Block != 0 || s0[1].Block != 1 || !s0[2].Parity {
		t.Errorf("stripe 0 = %+v", s0)
	}
	// Stripe 1 has parity on disk 2, so its data is on disks 1 and 3.
	if s1 := r5.Stripe(1); s1[0].Block != 2 || !s1[1].Parity || s1[2].Block != 3 || r5.StripeOf(3) != 1 {
		t.Errorf("stripe 1 = %+v", s1)
	}
	if r5.BlockCount() != 8 || r5.Name() != "RAID 5" {
		t.Errorf("capacity %d", r5.BlockCount())
	}
}

func TestParityLevels(t *testing.T) {
	for _, level := range []int{4, 5} {
		for _, n := range []int{3, 4} {
			t.Run(fmt.Sprintf("RAID%d-%ddisks", level, n), func(t *testing.T) {
				r, disks := newArray(t, level, n, 6)
				fill(t, r, 1)
				verify(t, r, 1)
				checkParity(t, r, disks)

				for failed := range n {
					r, disks := newArray(t, level, n, 6)
					fill(t, r, 1)
					if err := r.Fail(failed); err != nil {
						t.Fatal(err)
					}
					verify(t, r, 1) // degraded reads rebuild by XOR
					fill(t, r, 2)   // degraded writes
					verify(t, r, 2)
					rebuilt, err := r.Rebuild()
					if err != nil || len(rebuilt) != 1 || rebuilt[0].Disk != failed+1 || !rebuilt[0].Parity {
						t.Fatalf("rebuild = %+v, %v", rebuilt, err)
					}
					if len(rebuilt[0].Sources) != n-1 {
						t.Errorf("sources = %v", rebuilt[0].Sources)
					}
					verify(t, r, 2)
					checkParity(t, r, disks)
				}
			})
		}
	}
}

func TestDegradedReadEvent(t *testing.T) {
	r, _ := newArray(t, 5, 3, 4)
	fill(t, r, 1)
	r.Discard()
	if err := r.Fail(1); err != nil {
		t.Fatal(err)
	}
	if _, err := r.Read(1); err != nil { // block 1 lives on disk 2
		t.Fatal(err)
	}
	flushes := r.Flush()
	if len(flushes) == 0 {
		t.Fatal("no events")
	}
	e := flushes[0].Events[0]
	if e.Kind != blockio.DegradedRead || e.Block != 1 || e.Disk != 2 || !e.Parity || fmt.Sprint(e.Sources) != "[1 3]" {
		t.Errorf("event = %+v", e)
	}
}

func TestTwoFailures(t *testing.T) {
	r, _ := newArray(t, 5, 3, 4)
	fill(t, r, 1)
	for _, i := range []int{0, 2} {
		if err := r.Fail(i); err != nil {
			t.Fatal(err)
		}
	}
	if _, err := r.Read(0); !errors.Is(err, raid.ErrArrayFailed) {
		t.Errorf("read: %v", err)
	}
	if err := r.Write(0, nil); !errors.Is(err, raid.ErrArrayFailed) {
		t.Errorf("write: %v", err)
	}
	if _, err := r.Rebuild(); !errors.Is(err, raid.ErrArrayFailed) {
		t.Errorf("rebuild: %v", err)
	}
}

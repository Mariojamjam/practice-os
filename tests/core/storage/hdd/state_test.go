package hdd_test

import (
	"errors"
	"reflect"
	"testing"

	"github.com/Mariojamjam/practice-os/core/storage/hdd"
	"github.com/Mariojamjam/practice-os/core/storage/sched"
)

func TestStateRoundTrip(t *testing.T) {
	cfg := hdd.Config{Name: "HDD", Tracks: 10, BlocksPerTrack: 1, Scheduler: sched.SSTF, Head: 5, Direction: sched.Up}
	h := newHDD(t, cfg, 10)
	if err := h.Write(8, []byte("data")); err != nil {
		t.Fatal(err)
	}
	h.Flush()                            // head moves to 8
	if _, err := h.Read(2); err != nil { // stays queued
		t.Fatal(err)
	}
	st := h.State()

	other := newHDD(t, cfg, 10)
	if err := other.SetState(st); err != nil {
		t.Fatal(err)
	}
	if other.Head() != 8 || !reflect.DeepEqual(other.Pending(), h.Pending()) {
		t.Errorf("head %d, pending %+v", other.Head(), other.Pending())
	}
	if got, _ := other.Read(8); string(got[:4]) != "data" {
		t.Errorf("block 8 = %q", got[:4])
	}

	st.Head = 10
	if err := other.SetState(st); !errors.Is(err, hdd.ErrInvalid) {
		t.Errorf("head outside the disk: %v", err)
	}
}

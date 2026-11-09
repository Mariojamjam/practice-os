package raid_test

import (
	"errors"
	"testing"

	"github.com/Mariojamjam/practice-os/core/storage/raid"
)

func TestStateRoundTrip(t *testing.T) {
	r, _ := newArray(t, 5, 3, 4)
	fill(t, r, 1)
	if err := r.Fail(1); err != nil {
		t.Fatal(err)
	}
	if _, err := r.Read(1); err != nil { // raises a degraded-read event
		t.Fatal(err)
	}
	st := r.State()
	other, _ := newArray(t, 5, 3, 4)
	if err := other.SetState(st); err != nil {
		t.Fatal(err)
	}
	if !other.Failed(1) || other.Failed(0) || len(other.Pending()) != 1 {
		t.Errorf("failed %v, pending %+v", other.Failed(1), other.Pending())
	}
	if err := other.SetState(raid.State{Failed: []bool{false}}); !errors.Is(err, raid.ErrInvalid) {
		t.Errorf("wrong disk count: %v", err)
	}
}

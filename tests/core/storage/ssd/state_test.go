package ssd_test

import (
	"errors"
	"reflect"
	"testing"

	"github.com/Mariojamjam/practice-os/core/storage/disk"
	"github.com/Mariojamjam/practice-os/core/storage/ssd"
)

func TestStateRoundTrip(t *testing.T) {
	s := ssd.New("SSD", 512, 8)
	for i := range 5 {
		if err := s.Write(2, []byte{byte(i)}); err != nil {
			t.Fatal(err)
		}
	}
	st := s.State()
	other := ssd.New("SSD", 512, 8)
	if err := other.SetState(st); err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(other.Wear(), s.Wear()) || !reflect.DeepEqual(other.Pending(), s.Pending()) {
		t.Error("wear or queue differ after restore")
	}
	if got, _ := other.Read(2); got[0] != 4 {
		t.Errorf("block 2 = %d", got[0])
	}
	// Writes keep leveling from the restored counters.
	if err := other.Write(2, []byte{9}); err != nil {
		t.Fatal(err)
	}

	bad := s.State()
	bad.FTL[0] = bad.FTL[2] // two blocks on one page
	if err := other.SetState(bad); !errors.Is(err, disk.ErrOutOfRange) {
		t.Errorf("inconsistent FTL: %v", err)
	}
	bad = s.State()
	bad.Erases = bad.Erases[:1]
	if err := other.SetState(bad); !errors.Is(err, disk.ErrOutOfRange) {
		t.Errorf("wrong size: %v", err)
	}
}

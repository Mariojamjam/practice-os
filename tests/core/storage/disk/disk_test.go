package disk_test

import (
	"bytes"
	"errors"
	"github.com/Mariojamjam/practice-os/core/storage/disk"
	"testing"
)

func TestDisk(t *testing.T) {
	d := disk.New(8, 4)
	if d.BlockSize() != 8 || d.BlockCount() != 4 {
		t.Fatalf("geometry = %d x %d", d.BlockSize(), d.BlockCount())
	}

	got, err := d.Read(0)
	if err != nil || !bytes.Equal(got, make([]byte, 8)) {
		t.Fatalf("new disk not zeroed: %v %v", got, err)
	}

	if err := d.Write(1, []byte("ABCDEFGH")); err != nil {
		t.Fatal(err)
	}
	if err := d.Write(1, []byte("xy")); err != nil {
		t.Fatal(err)
	}
	got, _ = d.Read(1)
	if want := []byte("xy\x00\x00\x00\x00\x00\x00"); !bytes.Equal(got, want) {
		t.Errorf("partial write must zero-fill: got %q, want %q", got, want)
	}

	got[0] = 'Z'
	again, _ := d.Read(1)
	if again[0] != 'x' {
		t.Error("Read must return a copy")
	}

	if err := d.Write(2, make([]byte, 9)); !errors.Is(err, disk.ErrTooLarge) {
		t.Errorf("oversized write: %v", err)
	}
	for _, b := range []int64{-1, 4} {
		if _, err := d.Read(b); !errors.Is(err, disk.ErrOutOfRange) {
			t.Errorf("Read(%d): %v", b, err)
		}
		if err := d.Write(b, nil); !errors.Is(err, disk.ErrOutOfRange) {
			t.Errorf("Write(%d): %v", b, err)
		}
	}
}

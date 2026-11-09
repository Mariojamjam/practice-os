package disk_test

import (
	"errors"
	"testing"

	"github.com/Mariojamjam/practice-os/core/storage/disk"
)

func TestBlocksRoundTrip(t *testing.T) {
	d := disk.New(4, 3)
	if err := d.Write(1, []byte("ab")); err != nil {
		t.Fatal(err)
	}
	saved := d.Blocks()
	saved[1][0] = 'X' // a copy: the disk is unchanged
	if got, _ := d.Read(1); got[0] != 'a' {
		t.Error("Blocks must return copies")
	}
	other := disk.New(4, 3)
	if err := other.SetBlocks(d.Blocks()); err != nil {
		t.Fatal(err)
	}
	if got, _ := other.Read(1); string(got[:2]) != "ab" {
		t.Errorf("restored %q", got)
	}
	if err := other.SetBlocks(make([][]byte, 2)); !errors.Is(err, disk.ErrOutOfRange) {
		t.Errorf("wrong block count: %v", err)
	}
	if err := other.SetBlocks([][]byte{make([]byte, 4), make([]byte, 5), make([]byte, 4)}); !errors.Is(err, disk.ErrTooLarge) {
		t.Errorf("wrong block size: %v", err)
	}
}

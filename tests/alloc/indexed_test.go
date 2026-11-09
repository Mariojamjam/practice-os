package alloc_test

import (
	"errors"
	"reflect"
	"testing"

	"github.com/Mariojamjam/practice-os/internal/alloc"
)

func TestIndexed(t *testing.T) {
	a, bm, d := newAlloc(t, alloc.Indexed, 4096, 16)

	// Example 1.2: a 10 KB file takes an inode block, then 3 data blocks.
	f := &alloc.Inode{Size: 10240}
	if err := a.Allocate(f, 3); err != nil {
		t.Fatal(err)
	}
	if f.Meta != 0 || !reflect.DeepEqual(f.Blocks, []int64{1, 2, 3}) {
		t.Fatalf("inode %d, blocks %v", f.Meta, f.Blocks)
	}
	if r := a.Ref(f); r != (alloc.Ref{A: 0}) {
		t.Errorf("Ref = %+v", r)
	}
	if raw, _ := d.Read(0); string(raw[:4]) != "INOD" {
		t.Errorf("inode block starts with %q", raw[:4])
	}

	// Size and index are persisted in the inode block.
	f.Size = 9000
	if err := a.Resize(f, 3); err != nil {
		t.Fatal(err)
	}
	loaded, err := a.Load(a.Ref(f), 0)
	if err != nil || loaded.Size != 9000 || loaded.Meta != 0 || !reflect.DeepEqual(loaded.Blocks, f.Blocks) {
		t.Fatalf("Load = %+v, %v", loaded, err)
	}

	if err := a.Free(f); err != nil || bm.FreeCount() != 16 {
		t.Errorf("Free: %v, free = %d", err, bm.FreeCount())
	}

	// An empty file still has its inode.
	empty := &alloc.Inode{}
	if err := a.Allocate(empty, 0); err != nil || empty.Meta < 0 || len(empty.Blocks) != 0 {
		t.Errorf("empty file: %+v %v", empty, err)
	}

	// The inode needs a block too: 15 free blocks hold at most 14 data blocks.
	if err := a.Allocate(&alloc.Inode{}, 15); !errors.Is(err, alloc.ErrNoSpace) {
		t.Errorf("no room for inode: %v", err)
	}
}

func TestIndexedLimits(t *testing.T) {
	a, _, d := newAlloc(t, alloc.Indexed, 512, 256)
	// A 512-byte inode has a 16-byte header and 4-byte pointers: 124 blocks.
	const maxBlocks = (512 - 16) / 4
	if err := a.Allocate(&alloc.Inode{}, maxBlocks+1); !errors.Is(err, alloc.ErrFileTooLarge) {
		t.Errorf("oversized file: %v", err)
	}
	if err := a.Allocate(&alloc.Inode{}, maxBlocks); err != nil {
		t.Errorf("largest file: %v", err)
	}
	f := &alloc.Inode{}
	if err := a.Allocate(f, 1); err != nil {
		t.Fatal(err)
	}
	if err := a.Resize(f, maxBlocks+1); !errors.Is(err, alloc.ErrFileTooLarge) {
		t.Errorf("oversized resize: %v", err)
	}
	if err := d.Write(f.Blocks[0], []byte("not an inode")); err != nil {
		t.Fatal(err)
	}
	if _, err := a.Load(alloc.Ref{A: uint32(f.Blocks[0])}, 0); !errors.Is(err, alloc.ErrCorrupt) {
		t.Errorf("loading a data block as inode: %v", err)
	}
}

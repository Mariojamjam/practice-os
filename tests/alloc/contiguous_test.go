package alloc_test

import (
	"errors"
	"reflect"
	"testing"

	"github.com/Mariojamjam/practice-os/internal/alloc"
)

func TestContiguous(t *testing.T) {
	a, bm, d := newAlloc(t, alloc.Contiguous, 512, 10)

	f1, f2 := &alloc.Inode{}, &alloc.Inode{}
	if err := a.Allocate(f1, 3); err != nil {
		t.Fatal(err)
	}
	if err := a.Allocate(f2, 2); err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(f1.Blocks, []int64{0, 1, 2}) || !reflect.DeepEqual(f2.Blocks, []int64{3, 4}) {
		t.Fatalf("blocks: %v %v", f1.Blocks, f2.Blocks)
	}
	if r := a.Ref(f1); r != (alloc.Ref{A: 0, B: 3}) {
		t.Errorf("Ref = %+v", r)
	}
	loaded, err := a.Load(a.Ref(f2), 1000)
	if err != nil || !reflect.DeepEqual(loaded.Blocks, f2.Blocks) || loaded.Size != 1000 || loaded.Meta != -1 {
		t.Errorf("Load = %+v, %v", loaded, err)
	}

	// Grow in place: blocks 5..6 follow f2 and are free.
	if err := a.Resize(f2, 4); err != nil || !reflect.DeepEqual(f2.Blocks, []int64{3, 4, 5, 6}) {
		t.Fatalf("grow in place: %v %v", f2.Blocks, err)
	}

	// Shrink f2, then grow f1: blocks after f1 are taken, so it relocates
	// to the first run that fits (5..8) and its data moves with it.
	if err := a.Resize(f2, 2); err != nil {
		t.Fatal(err)
	}
	for i, b := range f1.Blocks {
		if err := d.Write(b, []byte{byte('a' + i)}); err != nil {
			t.Fatal(err)
		}
	}
	if err := a.Resize(f1, 4); err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(f1.Blocks, []int64{5, 6, 7, 8}) {
		t.Fatalf("relocated blocks = %v", f1.Blocks)
	}
	for i, b := range f1.Blocks[:3] {
		got, _ := d.Read(b)
		if got[0] != byte('a'+i) {
			t.Errorf("block %d lost its data after relocation", b)
		}
	}
	if got := usedBlocks(bm); !reflect.DeepEqual(got, []int64{3, 4, 5, 6, 7, 8}) {
		t.Errorf("used = %v", got)
	}

	// 4 free blocks (0,1,2,9) but the largest run is 3: fragmentation.
	if err := a.Allocate(&alloc.Inode{}, 4); !errors.Is(err, alloc.ErrNoContiguousSpace) {
		t.Errorf("fragmented allocate: %v", err)
	}
	if err := a.Allocate(&alloc.Inode{}, 5); !errors.Is(err, alloc.ErrNoSpace) {
		t.Errorf("full allocate: %v", err)
	}

	if err := a.Free(f1); err != nil {
		t.Fatal(err)
	}
	if got := bm.FreeCount(); got != 8 {
		t.Errorf("FreeCount after Free = %d", got)
	}

	empty := &alloc.Inode{}
	if err := a.Allocate(empty, 0); err != nil || len(empty.Blocks) != 0 || a.Ref(empty) != (alloc.Ref{}) {
		t.Errorf("empty file: %+v %v", empty, err)
	}
}

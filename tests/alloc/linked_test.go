package alloc_test

import (
	"encoding/binary"
	"errors"
	"reflect"
	"testing"

	"github.com/Mariojamjam/practice-os/core/fs/alloc"
	"github.com/Mariojamjam/practice-os/core/storage/disk"
)

// fatEntry reads the FAT entry of block b straight from the disk: one
// little-endian uint32 per block, starting at block 0.
func fatEntry(t *testing.T, d *disk.Disk, b int64) uint32 {
	t.Helper()
	bs := int64(d.BlockSize())
	data, err := d.Read(b * 4 / bs)
	if err != nil {
		t.Fatal(err)
	}
	return binary.LittleEndian.Uint32(data[b*4%bs:])
}

func setFATEntry(t *testing.T, d *disk.Disk, b int64, v uint32) {
	t.Helper()
	bs := int64(d.BlockSize())
	data, err := d.Read(b * 4 / bs)
	if err != nil {
		t.Fatal(err)
	}
	binary.LittleEndian.PutUint32(data[b*4%bs:], v)
	if err := d.Write(b*4/bs, data); err != nil {
		t.Fatal(err)
	}
}

func TestLinked(t *testing.T) {
	// 512-byte blocks hold 128 FAT entries: 200 blocks need a 2-block FAT.
	a, bm, d := newAlloc(t, alloc.Linked, 512, 200)
	res, ok := a.(alloc.Reserver)
	if !ok || res.ReservedBlocks() != 2 || bm.IsFree(0) || bm.IsFree(1) || !bm.IsFree(2) {
		t.Fatal("FAT blocks not reserved")
	}
	if fatEntry(t, d, 0) != alloc.FATReserved || fatEntry(t, d, 1) != alloc.FATReserved {
		t.Error("FAT does not mark its own blocks as reserved")
	}

	f1, f2 := &alloc.Inode{}, &alloc.Inode{}
	if err := a.Allocate(f1, 2); err != nil {
		t.Fatal(err)
	}
	if err := a.Allocate(f2, 1); err != nil {
		t.Fatal(err)
	}
	// f1 grows past f2: the chain continues after it, non-contiguously.
	if err := a.Resize(f1, 4); err != nil {
		t.Fatal(err)
	}
	if want := []int64{2, 3, 5, 6}; !reflect.DeepEqual(f1.Blocks, want) {
		t.Fatalf("f1 = %v, want %v", f1.Blocks, want)
	}
	if r := a.Ref(f1); r != (alloc.Ref{A: 2}) {
		t.Errorf("Ref = %+v", r)
	}
	// The chain is on disk: following the FAT reproduces it.
	loaded, err := a.Load(a.Ref(f1), 0)
	if err != nil || !reflect.DeepEqual(loaded.Blocks, f1.Blocks) {
		t.Fatalf("Load = %v, %v", loaded, err)
	}
	for i, want := range []uint32{3, 5, 6, alloc.FATEOF} {
		if got := fatEntry(t, d, f1.Blocks[i]); got != want {
			t.Errorf("FAT[%d] = %#x, want %#x", f1.Blocks[i], got, want)
		}
	}

	if err := a.Resize(f1, 1); err != nil {
		t.Fatal(err)
	}
	if got := fatEntry(t, d, 2); got != alloc.FATEOF {
		t.Errorf("after shrink FAT[2] = %#x", got)
	}
	if got := fatEntry(t, d, 3); got != alloc.FATFree {
		t.Errorf("freed block FAT[3] = %#x", got)
	}

	meta, err := a.AllocMeta()
	if err != nil || fatEntry(t, d, meta) != alloc.FATEOF {
		t.Errorf("metadata block %d not marked in the FAT (%v)", meta, err)
	}

	if err := a.Allocate(&alloc.Inode{}, int(bm.FreeCount())+1); !errors.Is(err, alloc.ErrNoSpace) {
		t.Errorf("overfull allocate: %v", err)
	}
	if got, _ := a.Load(alloc.Ref{}, 0); len(got.Blocks) != 0 {
		t.Error("Ref{} must load as an empty file")
	}
}

func TestLinkedCorruptChain(t *testing.T) {
	a, _, d := newAlloc(t, alloc.Linked, 512, 16)
	f := &alloc.Inode{}
	if err := a.Allocate(f, 2); err != nil {
		t.Fatal(err)
	}
	setFATEntry(t, d, f.Blocks[1], uint32(f.Blocks[0])) // make a cycle
	if _, err := a.Load(a.Ref(f), 0); !errors.Is(err, alloc.ErrCorrupt) {
		t.Errorf("cyclic chain: %v", err)
	}
	setFATEntry(t, d, f.Blocks[1], 9999) // point outside the disk
	if _, err := a.Load(a.Ref(f), 0); !errors.Is(err, alloc.ErrCorrupt) {
		t.Errorf("out-of-range chain: %v", err)
	}
}

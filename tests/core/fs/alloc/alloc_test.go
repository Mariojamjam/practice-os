package alloc_test

import (
	"bytes"
	"errors"
	"reflect"
	"testing"

	"github.com/Mariojamjam/practice-os/core/fs/alloc"
	"github.com/Mariojamjam/practice-os/core/storage/disk"
)

func newAlloc(t *testing.T, name string, blockSize int, blocks int64) (alloc.Allocator, *alloc.Bitmap, *disk.Disk) {
	t.Helper()
	d := disk.New(blockSize, blocks)
	bm := alloc.NewBitmap(blocks)
	a, err := alloc.New(name, d, bm)
	if err != nil {
		t.Fatal(err)
	}
	return a, bm, d
}

func usedBlocks(bm *alloc.Bitmap) []int64 {
	var out []int64
	for b := range bm.Len() {
		if !bm.IsFree(b) {
			out = append(out, b)
		}
	}
	return out
}

func TestBitmap(t *testing.T) {
	bm := alloc.NewBitmap(8)
	for _, b := range []int64{0, 1, 4, 7} {
		bm.Set(b)
	}
	if got := bm.FreeCount(); got != 4 {
		t.Errorf("FreeCount = %d", got)
	}
	if got, want := bm.FreeRuns(), []alloc.Run{{Start: 2, Len: 2}, {Start: 5, Len: 2}}; !reflect.DeepEqual(got, want) {
		t.Errorf("FreeRuns = %v, want %v", got, want)
	}
	if s, ok := bm.FindRun(2); !ok || s != 2 {
		t.Errorf("FindRun(2) = %d, %v", s, ok)
	}
	if _, ok := bm.FindRun(3); ok {
		t.Error("FindRun(3) should fail")
	}
	if b, ok := bm.AllocOne(); !ok || b != 2 || bm.IsFree(2) {
		t.Errorf("AllocOne = %d, %v", b, ok)
	}
}

func TestUnknownStrategy(t *testing.T) {
	if _, err := alloc.New("fat32", disk.New(512, 4), alloc.NewBitmap(4)); !errors.Is(err, alloc.ErrUnknownStrategy) {
		t.Errorf("error = %v", err)
	}
}

func TestAllocMeta(t *testing.T) {
	for _, name := range alloc.Strategies() {
		t.Run(name, func(t *testing.T) {
			a, bm, _ := newAlloc(t, name, 512, 8)
			before := bm.FreeCount()
			b, err := a.AllocMeta()
			if err != nil || bm.IsFree(b) {
				t.Fatalf("AllocMeta = %d, %v", b, err)
			}
			if err := a.FreeMeta(b); err != nil || !bm.IsFree(b) || bm.FreeCount() != before {
				t.Errorf("FreeMeta: %v", err)
			}
		})
	}
}

// TestDataSurvivesResize checks, for every strategy, that growing and
// shrinking a file keeps its data blocks' contents in logical order.
func TestDataSurvivesResize(t *testing.T) {
	for _, name := range alloc.Strategies() {
		t.Run(name, func(t *testing.T) {
			a, _, d := newAlloc(t, name, 512, 32)
			f := &alloc.Inode{Size: 3 * 512}
			if err := a.Allocate(f, 3); err != nil {
				t.Fatal(err)
			}
			blocker := &alloc.Inode{}
			if err := a.Allocate(blocker, 1); err != nil { // forces relocation for contiguous
				t.Fatal(err)
			}
			for i, b := range a.Blocks(f) {
				if err := d.Write(b, bytes.Repeat([]byte{byte('A' + i)}, 512)); err != nil {
					t.Fatal(err)
				}
			}
			f.Size = 6 * 512
			if err := a.Resize(f, 6); err != nil {
				t.Fatal(err)
			}
			f.Size = 2 * 512
			if err := a.Resize(f, 2); err != nil {
				t.Fatal(err)
			}
			loaded, err := a.Load(a.Ref(f), f.Size)
			if err != nil {
				t.Fatal(err)
			}
			if len(loaded.Blocks) != 2 {
				t.Fatalf("loaded %d blocks", len(loaded.Blocks))
			}
			for i, b := range loaded.Blocks {
				got, _ := d.Read(b)
				if got[0] != byte('A'+i) {
					t.Errorf("logical block %d holds %q", i, got[0])
				}
			}
		})
	}
}

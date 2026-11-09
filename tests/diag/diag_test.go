package diag_test

import (
	"github.com/Mariojamjam/practice-os/internal/diag"
	"testing"

	"github.com/Mariojamjam/practice-os/internal/alloc"
	"github.com/Mariojamjam/practice-os/internal/disk"
	"github.com/Mariojamjam/practice-os/internal/fs"
)

func newFS(t *testing.T, strategy string) *fs.FS {
	t.Helper()
	f, err := fs.New(disk.New(4096, 16), strategy)
	if err != nil {
		t.Fatal(err)
	}
	return f
}

func must(t *testing.T, err error) {
	t.Helper()
	if err != nil {
		t.Fatal(err)
	}
}

func kinds(r diag.Report) []diag.BlockKind {
	out := make([]diag.BlockKind, len(r.Blocks))
	for i, b := range r.Blocks {
		out[i] = b.Kind
	}
	return out
}

// Example 1.2: /system/logs/app.log of 10 KB with indexed allocation.
func TestAnalyzeIndexedExample(t *testing.T) {
	f := newFS(t, alloc.Indexed)
	must(t, f.Mkdir("/system"))
	must(t, f.Mkdir("/system/logs"))
	must(t, f.Create("/system/logs/app.log", fs.Synthetic(0, 10240)))

	r, err := diag.Analyze(f)
	must(t, err)
	want := []diag.BlockKind{diag.KindRootInode, diag.KindDirInode, diag.KindDirInode, diag.KindFileInode, diag.KindData, diag.KindData, diag.KindData}
	for i, k := range want {
		if r.Blocks[i].Kind != k {
			t.Errorf("block %d = %s, want %s", i, r.Blocks[i].Kind, k)
		}
	}
	if b := r.Blocks[6]; b.Seq != 3 || b.Used != 2048 || b.Path != "/system/logs/app.log" {
		t.Errorf("last data block = %+v", b)
	}
	if len(r.Files) != 1 {
		t.Fatalf("files = %+v", r.Files)
	}
	fr := r.Files[0]
	if fr.Size != 10240 || fr.Allocated != 12288 || fr.Internal != 2048 || fr.LastBlock != 6 {
		t.Errorf("file report = %+v", fr)
	}
	if r.Internal != 2048 || r.MetaBlocks != 4 || r.FreeBlocks != 9 || r.External != 0 || r.CompactionNeeded {
		t.Errorf("report = %+v", r)
	}
}

func TestAnalyzeLinked(t *testing.T) {
	f := newFS(t, alloc.Linked)
	must(t, f.Create("/a", fs.Synthetic(0, 4096)))
	must(t, f.Create("/b", fs.Synthetic(0, 100)))
	must(t, f.Resize("/a", 8192)) // chain jumps over /b

	r, err := diag.Analyze(f)
	must(t, err)
	if got := kinds(r)[:5]; got[0] != diag.KindFAT || got[1] != diag.KindRootDir || got[2] != diag.KindData {
		t.Errorf("kinds = %v", got)
	}
	if r.Blocks[2].Next != 4 || r.Blocks[4].Next != -1 {
		t.Errorf("chain: 2 -> %d, 4 -> %d", r.Blocks[2].Next, r.Blocks[4].Next)
	}
	if r.External != 0 || r.CompactionNeeded {
		t.Errorf("linked allocation reported external fragmentation: %+v", r)
	}
}

func TestContiguousFragmentationAndCompaction(t *testing.T) {
	f := newFS(t, alloc.Contiguous)
	for _, name := range []string{"/a", "/b", "/c", "/d"} {
		must(t, f.Create(name, fs.Synthetic(0, 3*4096))) // blocks 1-3, 4-6, 7-9, 10-12
	}
	must(t, f.Remove("/b", false))
	must(t, f.Remove("/d", false))

	r, err := diag.Analyze(f)
	must(t, err)
	// Free runs: 4-6 (3 blocks) and 10-15 (6 blocks).
	if len(r.FreeRuns) != 2 || r.Largest != 6 || r.External != 3*4096 || !r.CompactionNeeded {
		t.Fatalf("before: runs %v, largest %d, external %d, needed %v", r.FreeRuns, r.Largest, r.External, r.CompactionNeeded)
	}

	res, err := diag.Compact(f)
	must(t, err)
	if len(res.Moves) != 1 || res.Moves[0].Path != "/c" || res.Moves[0].To[0] != 4 {
		t.Errorf("moves = %+v", res.Moves)
	}
	a := res.After
	if len(a.FreeRuns) != 1 || a.Largest != 9 || a.External != 0 || a.CompactionNeeded {
		t.Errorf("after: %+v", a)
	}
}

package render_test

import (
	"strings"
	"testing"

	"github.com/Mariojamjam/practice-os/core/fs"
	"github.com/Mariojamjam/practice-os/core/fs/alloc"
	"github.com/Mariojamjam/practice-os/core/fs/diag"
	"github.com/Mariojamjam/practice-os/ui/render"
	"github.com/Mariojamjam/practice-os/ui/shell"
)

func TestTreeASCII(t *testing.T) {
	root := shell.TreeNode{Name: "/", Kind: fs.KindDir, Children: []shell.TreeNode{
		{Name: "a", Kind: fs.KindDir, Children: []shell.TreeNode{{Name: "x", Kind: fs.KindFile, Size: 10}}},
		{Name: "b", Kind: fs.KindFile, Size: 2048},
	}}
	want := "[FILE SYSTEM TREE]\n/\n|-- a/ [DIR]\n|   `-- x (10 B) [FILE]\n`-- b (2 KB) [FILE]\n"
	if got := render.Result(shell.TreeResult{Root: root}, render.Options{ASCII: true}); got != want {
		t.Errorf("got\n%s\nwant\n%s", got, want)
	}
}

func TestFile(t *testing.T) {
	if got := render.Result(shell.FileResult{Path: "/t", Data: []byte("hi")}, render.Options{}); got != "hi\n" {
		t.Errorf("text = %q", got)
	}
	if got := render.Result(shell.FileResult{Path: "/t"}, render.Options{}); got != "(empty file)\n" {
		t.Errorf("empty = %q", got)
	}
	got := render.Result(shell.FileResult{Path: "/big", Data: fs.Synthetic(0, 2000)}, render.Options{})
	if !strings.HasPrefix(got, "'/big': 2000 bytes (2000 B); first 64 bytes:\n00000000  41 42 43") {
		t.Errorf("large file = %q", got)
	}
}

func TestNilAndError(t *testing.T) {
	if got := render.Result(nil, render.Options{}); got != "" {
		t.Errorf("nil result = %q", got)
	}
	if got := render.Error(fs.ErrNotFound); got != "error: no such file or directory\n" {
		t.Errorf("error = %q", got)
	}
}

// A disk of 1000 blocks pads block numbers to three digits; percentages
// keep one decimal; counts of one are singular.
func TestStatusFormatting(t *testing.T) {
	r := diag.Report{
		Strategy:    alloc.Indexed,
		BlockSize:   4096,
		TotalBlocks: 1000,
		Blocks:      make([]diag.Block, 1000),
		Files: []diag.FileReport{
			{Path: "/n.txt", Size: 10, Blocks: 1, Allocated: 4096, Internal: 4086, LastBlock: 7},
		},
		Internal:   4086,
		MetaBlocks: 1,
	}
	for i := range r.Blocks {
		r.Blocks[i] = diag.Block{Index: int64(i), Kind: diag.KindFree}
	}
	got := render.Result(shell.StatusResult{Report: r, Details: true}, render.Options{})
	for _, want := range []string{
		"Block size: 4 KB | Total blocks: 1000 (4000 KB)\n",
		"Block 000..999 : [FREE]\n",
		"  Allocated on disk      : 4096 bytes (1 block of 4 KB)\n",
		"  Internal fragmentation : 4086 bytes (99.8% waste in block 007)\n",
		"Metadata overhead            : 1 block (4 KB)\n",
	} {
		if !strings.Contains(got, want) {
			t.Errorf("missing %q in:\n%s", want, got)
		}
	}
}

func TestCompactionFormatting(t *testing.T) {
	after := diag.Report{Strategy: alloc.Contiguous, BlockSize: 4096, TotalBlocks: 16,
		FreeBlocks: 3, FreeRuns: []alloc.Run{{Start: 13, Len: 3}}, Largest: 3}
	res := diag.CompactResult{
		Before: diag.Report{External: 8192},
		After:  after,
		Moves:  []fs.Move{{Path: "/f", From: []int64{4, 5, 6, 9}, To: []int64{1, 2, 3, 4}}},
	}
	got := render.Result(shell.CompactResult{CompactResult: res}, render.Options{})
	want := "[DISK COMPACTION]\n" +
		"Moved '/f': blocks 04..06, 09 -> 01..04\n" +
		"Free space: 3 blocks in 1 run; largest run: 3 blocks (12 KB)\n" +
		"External fragmentation: 8192 bytes -> 0 bytes\n"
	if got != want {
		t.Errorf("got\n%s\nwant\n%s", got, want)
	}
}

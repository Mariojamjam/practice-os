package fs_test

import (
	"errors"
	"testing"

	"github.com/Mariojamjam/practice-os/core/fs"
	"github.com/Mariojamjam/practice-os/core/fs/alloc"
	"github.com/Mariojamjam/practice-os/core/storage/disk"
)

func TestOpenRestoresTheFileSystem(t *testing.T) {
	for _, strategy := range alloc.Strategies() {
		t.Run(strategy, func(t *testing.T) {
			d := disk.New(512, 64)
			f, err := fs.New(d, strategy)
			must(t, err)
			must(t, f.Mkdir("/d"))
			must(t, f.Create("/d/x", fs.Synthetic(0, 1500)))
			must(t, f.Chdir("/d"))
			st := f.State()

			// A second file system mounted on the same blocks sees everything.
			g, err := fs.Open(d, st)
			must(t, err)
			if g.Getwd() != "/d" || g.Strategy() != strategy || g.Bitmap().FreeCount() != f.Bitmap().FreeCount() {
				t.Errorf("cwd %q, strategy %s, free %d", g.Getwd(), g.Strategy(), g.Bitmap().FreeCount())
			}
			if got, err := g.Read("x"); err != nil || len(got) != 1500 {
				t.Fatalf("read: %d bytes, %v", len(got), err)
			}
			// And keeps working: new files do not overwrite old ones.
			must(t, g.Create("/y", fs.Synthetic(0, 700)))
			if got, _ := g.Read("/d/x"); len(got) != 1500 {
				t.Error("/d/x damaged by a new file")
			}
		})
	}
}

func TestOpenRejectsBadState(t *testing.T) {
	d := disk.New(512, 16)
	f, err := fs.New(d, alloc.Indexed)
	must(t, err)
	good := f.State()

	cases := []fs.State{
		{Strategy: alloc.Indexed, Root: 0},                       // root not marked used
		{Strategy: alloc.Indexed, Root: 0, Used: []int64{0, 99}}, // outside the disk
		{Strategy: alloc.Indexed, Root: 5, Used: []int64{0, 5}},  // not a directory block
		{Strategy: "fat32", Root: good.Root, Used: good.Used},    // unknown strategy
	}
	for i, st := range cases {
		if _, err := fs.Open(d, st); err == nil {
			t.Errorf("case %d: want error", i)
		}
	}
	gone := good
	gone.Cwd = "/missing"
	g, err := fs.Open(d, gone)
	if err != nil || g.Getwd() != "/" {
		t.Errorf("missing cwd: %q, %v", g.Getwd(), err)
	}
	if _, err := fs.Open(d, fs.State{Strategy: alloc.Indexed, Root: 3, Used: []int64{3}}); !errors.Is(err, fs.ErrCorrupt) {
		t.Errorf("zero block as root: %v", err)
	}
}

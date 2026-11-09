package tui

import (
	"slices"

	"github.com/Mariojamjam/practice-os/core/fs"
	"github.com/Mariojamjam/practice-os/core/fs/diag"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/core/storage/blockio"
	"github.com/Mariojamjam/practice-os/core/storage/raid"
	"github.com/Mariojamjam/practice-os/core/storage/ssd"
	"github.com/Mariojamjam/practice-os/internal/shell"
)

// snapshot is everything the tabs draw, read from the kernel with I/O
// recording muted so drawing never changes the simulation.
type snapshot struct {
	cwd     string
	tree    shell.TreeNode
	report  diag.Report
	pending []blockio.Flush
	raid    *raidView
	wear    []ssd.Wear
	err     error
}

type raidView struct {
	name     string
	level    int
	capacity int64
	disks    []shell.DiskState
	stripes  [][]raid.Slot
}

func takeSnapshot(k *kernel.Kernel) snapshot {
	snap := snapshot{cwd: k.FS.Getwd(), pending: k.Pending()}
	snap.err = k.Inspect(func() error {
		var err error
		if snap.tree, err = buildTree(k.FS, fs.Node{Path: "/", Name: "/", Kind: fs.KindDir}); err != nil {
			return err
		}
		snap.report, err = diag.Analyze(k.FS)
		return err
	})
	if r, ok := k.RAID(); ok {
		snap.raid = viewRAID(r, snap.report)
	}
	for _, s := range k.SSDs() {
		snap.wear = append(snap.wear, s.Wear())
	}
	return snap
}

func buildTree(f *fs.FS, n fs.Node) (shell.TreeNode, error) {
	t := shell.TreeNode{Name: n.Name, Kind: n.Kind, Size: n.Size}
	if n.Kind != fs.KindDir {
		return t, nil
	}
	children, err := f.List(n.Path)
	if err != nil {
		return t, err
	}
	for _, c := range children {
		ct, err := buildTree(f, c)
		if err != nil {
			return t, err
		}
		t.Children = append(t.Children, ct)
	}
	return t, nil
}

// viewRAID lists the array's health and the stripes holding used blocks.
func viewRAID(r *raid.RAID, report diag.Report) *raidView {
	v := &raidView{name: r.Name(), level: r.Level(), capacity: r.BlockCount()}
	for i, d := range r.Disks() {
		name := "Disk"
		if n, ok := d.(interface{ Name() string }); ok {
			name = n.Name()
		}
		v.disks = append(v.disks, shell.DiskState{Name: name, Failed: r.Failed(i)})
	}
	var stripes []int64
	for _, b := range report.Blocks {
		if b.Kind == diag.KindFree {
			continue
		}
		if s := r.StripeOf(b.Index); !slices.Contains(stripes, s) {
			stripes = append(stripes, s)
		}
	}
	slices.Sort(stripes)
	for _, s := range stripes {
		v.stripes = append(v.stripes, r.Stripe(s))
	}
	return v
}

// fileReport returns the fragmentation report of the file at abs.
func (s snapshot) fileReport(abs string) (diag.FileReport, bool) {
	for _, f := range s.report.Files {
		if f.Path == abs {
			return f, true
		}
	}
	return diag.FileReport{}, false
}

// blocksOf returns the blocks owned by abs, in disk order.
func (s snapshot) blocksOf(abs string) []diag.Block {
	var out []diag.Block
	for _, b := range s.report.Blocks {
		if b.Path == abs && b.Kind != diag.KindFree {
			out = append(out, b)
		}
	}
	return out
}

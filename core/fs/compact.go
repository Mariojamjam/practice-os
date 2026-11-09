package fs

import (
	"fmt"
	"math"
	"path"
	"slices"
	"sort"
)

// Move records how compaction relocated a node's blocks (metadata and data,
// in the order NodeBlocks returns them).
type Move struct {
	Path string
	From []int64
	To   []int64
}

// NodeBlocks returns every block n occupies: the directory block for a
// directory; the inode block (indexed allocation) followed by the data
// blocks for a file.
func (f *FS) NodeBlocks(n Node) ([]int64, error) {
	if n.Kind == KindDir {
		return []int64{n.Block}, nil
	}
	ino, err := f.Inode(n)
	if err != nil {
		return nil, err
	}
	var out []int64
	if ino.Meta >= 0 {
		out = append(out, ino.Meta)
	}
	return append(out, f.al.Blocks(ino)...), nil
}

// Compact rewrites the disk so used blocks are packed at the start, keeping
// the relative order of nodes on disk and the order of entries in each
// directory. It returns the nodes whose blocks moved.
//
// It works with every strategy: with contiguous allocation it removes
// external fragmentation; with linked and indexed allocation it also leaves
// each file's blocks in sequence.
func (f *FS) Compact() ([]Move, error) {
	type snap struct {
		node   Node
		data   []byte
		blocks []int64
		names  []string // directory entries, in order
	}
	var snaps []*snap
	err := f.Walk(func(n Node) error {
		s := &snap{node: n}
		var err error
		if s.blocks, err = f.NodeBlocks(n); err != nil {
			return err
		}
		if n.Kind == KindFile {
			if s.data, err = f.Read(n.Path); err != nil {
				return err
			}
		} else {
			children, err := f.List(n.Path)
			if err != nil {
				return err
			}
			for _, c := range children {
				s.names = append(s.names, c.Name)
			}
		}
		snaps = append(snaps, s)
		return nil
	})
	if err != nil {
		return nil, err
	}

	cwd := f.cwd
	if err := f.Format(f.Strategy()); err != nil {
		return nil, err
	}

	// Recreate nodes in their current disk order. A node whose parent sits
	// later on disk waits until the parent exists.
	firstBlock := func(s *snap) int64 {
		if len(s.blocks) == 0 {
			return math.MaxInt64
		}
		return s.blocks[0]
	}
	pending := slices.Clone(snaps[1:]) // snaps[0] is the root
	sort.SliceStable(pending, func(i, j int) bool { return firstBlock(pending[i]) < firstBlock(pending[j]) })
	created := map[string]bool{"/": true}
	for len(pending) > 0 {
		var next []*snap
		for _, s := range pending {
			if !created[path.Dir(s.node.Path)] {
				next = append(next, s)
				continue
			}
			var err error
			if s.node.Kind == KindDir {
				err = f.Mkdir(s.node.Path)
			} else {
				err = f.Create(s.node.Path, s.data)
			}
			if err != nil {
				return nil, fmt.Errorf("compaction: recreating %s: %w", s.node.Path, err)
			}
			created[s.node.Path] = true
		}
		if len(next) == len(pending) {
			return nil, fmt.Errorf("%w: compaction found orphaned entries", ErrCorrupt)
		}
		pending = next
	}

	var moves []Move
	for _, s := range snaps {
		n, err := f.Stat(s.node.Path)
		if err != nil {
			return nil, err
		}
		if n.Kind == KindDir {
			if err := f.reorder(n.Block, s.names); err != nil {
				return nil, err
			}
		}
		to, err := f.NodeBlocks(n)
		if err != nil {
			return nil, err
		}
		if !slices.Equal(s.blocks, to) {
			moves = append(moves, Move{Path: s.node.Path, From: s.blocks, To: to})
		}
	}
	f.cwd = cwd
	return moves, nil
}

// reorder sorts the entries of directory block b to follow names.
func (f *FS) reorder(b int64, names []string) error {
	entries, err := f.readDir(b)
	if err != nil {
		return err
	}
	sort.SliceStable(entries, func(i, j int) bool {
		return slices.Index(names, entries[i].name) < slices.Index(names, entries[j].name)
	})
	return f.writeDir(b, entries)
}

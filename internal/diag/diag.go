// Package diag inspects a file system on disk: it maps every block to its
// owner and role, measures internal and external fragmentation, decides
// whether compaction is needed, and runs it.
package diag

import (
	"github.com/Mariojamjam/practice-os/internal/alloc"
	"github.com/Mariojamjam/practice-os/internal/fs"
)

// BlockKind is the role of a disk block.
type BlockKind string

// Block roles. Directory blocks are called inodes under indexed allocation,
// where the directory block is the directory's inode.
const (
	KindFree      BlockKind = "FREE"
	KindFAT       BlockKind = "FAT"
	KindRootInode BlockKind = "ROOT_INODE"
	KindDirInode  BlockKind = "DIR_INODE"
	KindFileInode BlockKind = "FILE_INODE"
	KindRootDir   BlockKind = "ROOT_DIR"
	KindDir       BlockKind = "DIR"
	KindData      BlockKind = "DATA"
)

// Block describes one disk block.
type Block struct {
	Index int64
	Kind  BlockKind
	// Path is the owning file or directory ("" for free and FAT blocks).
	Path string
	// Seq is the 1-based position of a data block within its file.
	Seq int
	// Used is the number of file bytes stored in a data block.
	Used int
	// Next is the following block of the file (-1 for its last block).
	// It is the FAT chain under linked allocation.
	Next int64
}

// FileReport is the fragmentation analysis of one file.
type FileReport struct {
	Path string
	Size int64
	// Blocks is the number of data blocks.
	Blocks int
	// Allocated is Blocks × block size.
	Allocated int64
	// Internal is the unused space in the last data block.
	Internal int64
	// LastBlock is the last data block, or -1 for an empty file.
	LastBlock int64
}

// Report is a full analysis of the disk.
type Report struct {
	Strategy    string
	BlockSize   int
	TotalBlocks int64
	Blocks      []Block
	Files       []FileReport

	// Internal is the total internal fragmentation, in bytes.
	Internal int64
	// MetaBlocks counts blocks holding metadata: directories, inodes, FAT.
	MetaBlocks int64
	FreeBlocks int64
	// FreeRuns are the maximal runs of free blocks, in disk order.
	FreeRuns []alloc.Run
	// Largest is the length of the largest free run, in blocks.
	Largest int64
	// External is the free space outside the largest free run, in bytes:
	// space a contiguous file cannot use. Only contiguous allocation
	// suffers from it; it is 0 for the other strategies.
	External int64
	// CompactionNeeded is true when contiguous allocation has its free
	// space split into more than one run.
	CompactionNeeded bool
}

// Analyze scans the file system on disk.
func Analyze(f *fs.FS) (Report, error) {
	dev := f.Device()
	r := Report{
		Strategy:    f.Strategy(),
		BlockSize:   dev.BlockSize(),
		TotalBlocks: dev.BlockCount(),
		Blocks:      make([]Block, dev.BlockCount()),
	}
	for i := range r.Blocks {
		r.Blocks[i] = Block{Index: int64(i), Kind: KindFree, Next: -1}
	}
	if res, ok := f.Allocator().(alloc.Reserver); ok {
		for b := range res.ReservedBlocks() {
			r.Blocks[b].Kind = KindFAT
		}
	}

	indexed := r.Strategy == alloc.Indexed
	bs := int64(r.BlockSize)
	err := f.Walk(func(n fs.Node) error {
		if n.Kind == fs.KindDir {
			kind := KindDir
			switch {
			case n.Path == "/" && indexed:
				kind = KindRootInode
			case n.Path == "/":
				kind = KindRootDir
			case indexed:
				kind = KindDirInode
			}
			r.Blocks[n.Block].Kind, r.Blocks[n.Block].Path = kind, n.Path
			return nil
		}

		ino, err := f.Inode(n)
		if err != nil {
			return err
		}
		if ino.Meta >= 0 {
			r.Blocks[ino.Meta].Kind, r.Blocks[ino.Meta].Path = KindFileInode, n.Path
		}
		data := f.Allocator().Blocks(ino)
		for i, b := range data {
			blk := &r.Blocks[b]
			blk.Kind, blk.Path, blk.Seq = KindData, n.Path, i+1
			blk.Used = int(min(bs, ino.Size-int64(i)*bs))
			if i+1 < len(data) {
				blk.Next = data[i+1]
			}
		}
		fr := FileReport{
			Path:      n.Path,
			Size:      ino.Size,
			Blocks:    len(data),
			Allocated: int64(len(data)) * bs,
			LastBlock: -1,
		}
		fr.Internal = fr.Allocated - fr.Size
		if len(data) > 0 {
			fr.LastBlock = data[len(data)-1]
		}
		r.Files = append(r.Files, fr)
		r.Internal += fr.Internal
		return nil
	})
	if err != nil {
		return Report{}, err
	}

	for _, b := range r.Blocks {
		if b.Kind != KindFree && b.Kind != KindData {
			r.MetaBlocks++
		}
	}
	r.FreeBlocks = f.Bitmap().FreeCount()
	r.FreeRuns = f.Bitmap().FreeRuns()
	for _, run := range r.FreeRuns {
		r.Largest = max(r.Largest, run.Len)
	}
	if r.Strategy == alloc.Contiguous {
		r.External = (r.FreeBlocks - r.Largest) * bs
		r.CompactionNeeded = len(r.FreeRuns) > 1
	}
	return r, nil
}

// CompactResult is the outcome of Compact.
type CompactResult struct {
	Before, After Report
	Moves         []fs.Move
}

// Compact packs used blocks at the start of the disk and reports the state
// before and after.
func Compact(f *fs.FS) (CompactResult, error) {
	var res CompactResult
	var err error
	if res.Before, err = Analyze(f); err != nil {
		return res, err
	}
	if res.Moves, err = f.Compact(); err != nil {
		return res, err
	}
	res.After, err = Analyze(f)
	return res, err
}

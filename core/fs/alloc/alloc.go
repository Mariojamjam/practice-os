// Package alloc implements the physical block-allocation strategies:
// contiguous, linked (FAT) and indexed (i-node).
//
// Each strategy persists its own structures on the device (FAT table,
// inode blocks); only the free-block bitmap is kept in memory.
package alloc

import (
	"errors"
	"fmt"

	"github.com/Mariojamjam/practice-os/core/storage/device"
)

// Strategy names.
const (
	Contiguous = "contiguous"
	Linked     = "linked"
	Indexed    = "indexed"
)

var (
	// ErrNoSpace means there are not enough free blocks.
	ErrNoSpace = errors.New("no space left on disk")
	// ErrNoContiguousSpace means there are enough free blocks in total, but
	// no single free run is large enough (external fragmentation).
	ErrNoContiguousSpace = errors.New("no contiguous run of free blocks large enough (external fragmentation)")
	// ErrFileTooLarge means the file exceeds what one inode can index.
	ErrFileTooLarge = errors.New("file too large for a single-level index")
	// ErrCorrupt means on-disk allocation metadata is inconsistent.
	ErrCorrupt = errors.New("corrupt allocation metadata")
	// ErrUnknownStrategy is returned by New for an unknown strategy name.
	ErrUnknownStrategy = errors.New("unknown allocation strategy")
)

// Inode is the in-memory handle of a file's allocation.
type Inode struct {
	// Size is the file size in bytes. Allocate and Resize persist it where
	// the strategy keeps it (the inode block, for indexed allocation).
	Size int64
	// Meta is the inode block for indexed allocation, -1 otherwise.
	Meta int64
	// Blocks are the data blocks in logical order.
	Blocks []int64
}

// Ref is what a directory entry stores to find a file again. Its meaning
// depends on the strategy.
type Ref struct {
	A, B uint32
}

// Allocator is a block-allocation strategy.
type Allocator interface {
	// Name returns the strategy name.
	Name() string
	// Allocate gives a new inode nBlocks data blocks.
	Allocate(f *Inode, nBlocks int) error
	// Resize grows or shrinks f to nBlocks data blocks, preserving data.
	Resize(f *Inode, nBlocks int) error
	// Free releases every block of f.
	Free(f *Inode) error
	// Blocks returns the data blocks of f in logical order.
	Blocks(f *Inode) []int64
	// Ref returns what a directory entry must store to Load f later.
	Ref(f *Inode) Ref
	// Load rebuilds an inode from a Ref by reading the device.
	Load(r Ref, size int64) (*Inode, error)
	// AllocMeta allocates one metadata block (e.g. a directory).
	AllocMeta() (int64, error)
	// FreeMeta releases a block obtained from AllocMeta.
	FreeMeta(b int64) error
}

// Reserver is implemented by strategies that reserve blocks at the start of
// the disk for their own tables.
type Reserver interface {
	// ReservedBlocks returns how many leading blocks are reserved.
	ReservedBlocks() int64
}

// Strategies lists the available strategy names.
func Strategies() []string {
	return []string{Contiguous, Linked, Indexed}
}

// New creates the named strategy over dev, using bm as the free-block map,
// and writes any on-disk structure it needs. bm must be empty.
func New(name string, dev device.Device, bm *Bitmap) (Allocator, error) {
	switch name {
	case Contiguous:
		return &contiguous{dev: dev, bm: bm}, nil
	case Linked:
		return newLinked(dev, bm)
	case Indexed:
		return &indexed{dev: dev, bm: bm}, nil
	default:
		return nil, fmt.Errorf("%w: %q", ErrUnknownStrategy, name)
	}
}

// allocMeta is the AllocMeta implementation shared by strategies that keep
// no per-block table.
func allocMeta(bm *Bitmap) (int64, error) {
	b, ok := bm.AllocOne()
	if !ok {
		return 0, ErrNoSpace
	}
	return b, nil
}

// copyBlock copies the content of block from into block to.
func copyBlock(dev device.Device, from, to int64) error {
	data, err := dev.Read(from)
	if err != nil {
		return err
	}
	return dev.Write(to, data)
}

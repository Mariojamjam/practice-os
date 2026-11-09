package alloc

import (
	"encoding/binary"
	"fmt"

	"github.com/Mariojamjam/practice-os/core/storage/device"
)

// Inode block layout (little-endian):
//
//	[0:4)   magic "INOD"
//	[4:12)  file size in bytes
//	[12:16) number of data blocks
//	[16:)   data block numbers, one uint32 each
const (
	inodeMagic  = "INOD"
	inodeHeader = 16
)

// indexed gives every file an inode block holding its size and a
// single-level index of its data blocks. The directory entry stores
// Ref{A: inode block}. Data blocks can be anywhere, so files never need
// contiguous space; the largest file is limited by how many pointers fit in
// one block.
type indexed struct {
	dev device.Device
	bm  *Bitmap
}

func (x *indexed) Name() string { return Indexed }

// MaxBlocks returns how many data blocks one inode can index.
func (x *indexed) MaxBlocks() int {
	return (x.dev.BlockSize() - inodeHeader) / 4
}

func (x *indexed) Allocate(f *Inode, n int) error {
	if n > x.MaxBlocks() {
		return fmt.Errorf("%w: %d blocks, at most %d", ErrFileTooLarge, n, x.MaxBlocks())
	}
	if x.bm.FreeCount() < int64(n)+1 {
		return ErrNoSpace
	}
	// The inode is taken first, so it precedes its data on a fresh disk.
	f.Meta, _ = x.bm.AllocOne()
	f.Blocks = x.take(n)
	return x.writeInode(f)
}

func (x *indexed) Resize(f *Inode, n int) error {
	cur := len(f.Blocks)
	switch {
	case n > x.MaxBlocks():
		return fmt.Errorf("%w: %d blocks, at most %d", ErrFileTooLarge, n, x.MaxBlocks())
	case n < cur:
		for _, b := range f.Blocks[n:] {
			x.bm.Clear(b)
		}
		f.Blocks = f.Blocks[:n]
	case n > cur:
		if x.bm.FreeCount() < int64(n-cur) {
			return ErrNoSpace
		}
		f.Blocks = append(f.Blocks, x.take(n-cur)...)
	}
	// Always rewrite: the size may change even when the block count does not.
	return x.writeInode(f)
}

func (x *indexed) Free(f *Inode) error {
	for _, b := range f.Blocks {
		x.bm.Clear(b)
	}
	x.bm.Clear(f.Meta)
	f.Blocks, f.Meta = nil, -1
	return nil
}

func (x *indexed) Blocks(f *Inode) []int64 { return f.Blocks }

func (x *indexed) Ref(f *Inode) Ref { return Ref{A: uint32(f.Meta)} }

// Load reads the inode block; the size stored there is authoritative.
func (x *indexed) Load(r Ref, _ int64) (*Inode, error) {
	b := int64(r.A)
	if b >= x.dev.BlockCount() {
		return nil, fmt.Errorf("%w: inode block %d out of range", ErrCorrupt, b)
	}
	data, err := x.dev.Read(b)
	if err != nil {
		return nil, err
	}
	if string(data[:4]) != inodeMagic {
		return nil, fmt.Errorf("%w: block %d is not an inode", ErrCorrupt, b)
	}
	f := &Inode{
		Size: int64(binary.LittleEndian.Uint64(data[4:12])),
		Meta: b,
	}
	count := int(binary.LittleEndian.Uint32(data[12:16]))
	if count > x.MaxBlocks() {
		return nil, fmt.Errorf("%w: inode %d lists %d blocks", ErrCorrupt, b, count)
	}
	for i := range count {
		p := inodeHeader + 4*i
		f.Blocks = append(f.Blocks, int64(binary.LittleEndian.Uint32(data[p:p+4])))
	}
	return f, nil
}

func (x *indexed) AllocMeta() (int64, error) { return allocMeta(x.bm) }

func (x *indexed) FreeMeta(b int64) error {
	x.bm.Clear(b)
	return nil
}

func (x *indexed) take(n int) []int64 {
	blocks := make([]int64, n)
	for i := range blocks {
		blocks[i], _ = x.bm.AllocOne()
	}
	return blocks
}

func (x *indexed) writeInode(f *Inode) error {
	data := make([]byte, inodeHeader+4*len(f.Blocks))
	copy(data, inodeMagic)
	binary.LittleEndian.PutUint64(data[4:12], uint64(f.Size))
	binary.LittleEndian.PutUint32(data[12:16], uint32(len(f.Blocks)))
	for i, b := range f.Blocks {
		p := inodeHeader + 4*i
		binary.LittleEndian.PutUint32(data[p:p+4], uint32(b))
	}
	return x.dev.Write(f.Meta, data)
}

package alloc

import (
	"encoding/binary"
	"fmt"

	"github.com/Mariojamjam/practice-os/core/storage/device"
)

// FAT entry values.
const (
	FATFree     uint32 = 0
	FATEOF      uint32 = 0xFFFFFFFF
	FATReserved uint32 = 0xFFFFFFFE
)

// linked chains each file's blocks through a File Allocation Table stored
// in the first K blocks of the disk, one little-endian uint32 per block:
// FATFree, FATEOF (last block of a chain), FATReserved, or the next block.
// The directory entry stores Ref{A: first block}; block 0 always holds the
// FAT, so A == 0 means an empty file.
type linked struct {
	dev      device.Device
	bm       *Bitmap
	reserved int64
}

func newLinked(dev device.Device, bm *Bitmap) (*linked, error) {
	l, err := openLinked(dev, bm)
	if err != nil {
		return nil, err
	}
	for b := range l.reserved {
		if err := dev.Write(b, nil); err != nil {
			return nil, err
		}
	}
	for b := range l.reserved {
		if err := l.set(b, FATReserved); err != nil {
			return nil, err
		}
	}
	return l, nil
}

// openLinked attaches to a FAT already on the device and reserves its
// blocks in bm.
func openLinked(dev device.Device, bm *Bitmap) (*linked, error) {
	n, bs := dev.BlockCount(), int64(dev.BlockSize())
	reserved := (n*4 + bs - 1) / bs
	if reserved >= n {
		return nil, fmt.Errorf("%w: the FAT needs %d of %d blocks", ErrNoSpace, reserved, n)
	}
	for b := range reserved {
		bm.Set(b)
	}
	return &linked{dev: dev, bm: bm, reserved: reserved}, nil
}

func (l *linked) Name() string { return Linked }

// ReservedBlocks implements Reserver: the FAT occupies the leading blocks.
func (l *linked) ReservedBlocks() int64 { return l.reserved }

func (l *linked) Allocate(f *Inode, n int) error {
	f.Meta, f.Blocks = -1, nil
	if n == 0 {
		return nil
	}
	blocks, err := l.allocChain(n)
	if err != nil {
		return err
	}
	f.Blocks = blocks
	return nil
}

func (l *linked) Resize(f *Inode, n int) error {
	cur := len(f.Blocks)
	switch {
	case n == cur:
		return nil
	case cur == 0:
		return l.Allocate(f, n)
	case n < cur:
		for _, b := range f.Blocks[n:] {
			if err := l.release(b); err != nil {
				return err
			}
		}
		f.Blocks = f.Blocks[:n]
		if n > 0 {
			return l.set(f.Blocks[n-1], FATEOF)
		}
		return nil
	}
	more, err := l.allocChain(n - cur)
	if err != nil {
		return err
	}
	if err := l.set(f.Blocks[cur-1], uint32(more[0])); err != nil {
		return err
	}
	f.Blocks = append(f.Blocks, more...)
	return nil
}

func (l *linked) Free(f *Inode) error {
	for _, b := range f.Blocks {
		if err := l.release(b); err != nil {
			return err
		}
	}
	f.Blocks = nil
	return nil
}

func (l *linked) Blocks(f *Inode) []int64 { return f.Blocks }

func (l *linked) Ref(f *Inode) Ref {
	if len(f.Blocks) == 0 {
		return Ref{}
	}
	return Ref{A: uint32(f.Blocks[0])}
}

// Load follows the chain in the FAT, starting at r.A.
func (l *linked) Load(r Ref, size int64) (*Inode, error) {
	f := &Inode{Size: size, Meta: -1}
	if r.A == 0 {
		return f, nil
	}
	n := l.dev.BlockCount()
	b := int64(r.A)
	for range n {
		if b < l.reserved || b >= n {
			return nil, fmt.Errorf("%w: chain points to block %d", ErrCorrupt, b)
		}
		f.Blocks = append(f.Blocks, b)
		next, err := l.Next(b)
		if err != nil {
			return nil, err
		}
		if next == FATEOF {
			return f, nil
		}
		b = int64(next)
	}
	return nil, fmt.Errorf("%w: cycle in FAT chain starting at %d", ErrCorrupt, r.A)
}

// AllocMeta allocates a block and marks it as a one-block chain, so the FAT
// never shows a used block as free.
func (l *linked) AllocMeta() (int64, error) {
	b, err := allocMeta(l.bm)
	if err != nil {
		return 0, err
	}
	return b, l.set(b, FATEOF)
}

func (l *linked) FreeMeta(b int64) error { return l.release(b) }

// Next returns the FAT entry for block b.
func (l *linked) Next(b int64) (uint32, error) {
	blk, off := l.pos(b)
	data, err := l.dev.Read(blk)
	if err != nil {
		return 0, err
	}
	return binary.LittleEndian.Uint32(data[off:]), nil
}

// allocChain takes n free blocks first-fit and links them, ending in EOF.
func (l *linked) allocChain(n int) ([]int64, error) {
	if l.bm.FreeCount() < int64(n) {
		return nil, ErrNoSpace
	}
	blocks := make([]int64, n)
	for i := range blocks {
		blocks[i], _ = l.bm.AllocOne()
	}
	for i, b := range blocks {
		next := FATEOF
		if i+1 < len(blocks) {
			next = uint32(blocks[i+1])
		}
		if err := l.set(b, next); err != nil {
			return nil, err
		}
	}
	return blocks, nil
}

func (l *linked) release(b int64) error {
	l.bm.Clear(b)
	return l.set(b, FATFree)
}

func (l *linked) pos(b int64) (blk int64, off int) {
	p := b * 4
	bs := int64(l.dev.BlockSize())
	return p / bs, int(p % bs)
}

func (l *linked) set(b int64, v uint32) error {
	blk, off := l.pos(b)
	data, err := l.dev.Read(blk)
	if err != nil {
		return err
	}
	binary.LittleEndian.PutUint32(data[off:], v)
	return l.dev.Write(blk, data)
}

package alloc

import "github.com/Mariojamjam/practice-os/core/storage/device"

// contiguous stores each file in one run of adjacent blocks, chosen
// first-fit. The directory entry stores Ref{A: start, B: count}.
//
// Growing a file extends it in place when the following blocks are free,
// otherwise relocates it to the first run that fits. When free space exists
// but no run is large enough, it fails with ErrNoContiguousSpace: external
// fragmentation.
type contiguous struct {
	dev device.Device
	bm  *Bitmap
}

func (c *contiguous) Name() string { return Contiguous }

func (c *contiguous) Allocate(f *Inode, n int) error {
	f.Meta, f.Blocks = -1, nil
	if n == 0 {
		return nil
	}
	start, err := c.findRun(int64(n), 0)
	if err != nil {
		return err
	}
	f.Blocks = c.take(start, int64(n))
	return nil
}

func (c *contiguous) Resize(f *Inode, n int) error {
	cur := len(f.Blocks)
	switch {
	case n == cur:
		return nil
	case cur == 0:
		return c.Allocate(f, n)
	case n < cur:
		for _, b := range f.Blocks[n:] {
			c.bm.Clear(b)
		}
		f.Blocks = f.Blocks[:n]
		return nil
	}

	// Grow in place if the blocks right after the file are free.
	end := f.Blocks[cur-1] + 1
	extra := int64(n - cur)
	inPlace := end+extra <= c.bm.Len()
	for b := end; inPlace && b < end+extra; b++ {
		inPlace = c.bm.IsFree(b)
	}
	if inPlace {
		f.Blocks = append(f.Blocks, c.take(end, extra)...)
		return nil
	}

	// Otherwise relocate the whole file to the first run that fits.
	start, err := c.findRun(int64(n), int64(cur))
	if err != nil {
		return err
	}
	blocks := c.take(start, int64(n))
	for i, old := range f.Blocks {
		if err := copyBlock(c.dev, old, blocks[i]); err != nil {
			return err
		}
		c.bm.Clear(old)
	}
	f.Blocks = blocks
	return nil
}

func (c *contiguous) Free(f *Inode) error {
	for _, b := range f.Blocks {
		c.bm.Clear(b)
	}
	f.Blocks = nil
	return nil
}

func (c *contiguous) Blocks(f *Inode) []int64 { return f.Blocks }

func (c *contiguous) Ref(f *Inode) Ref {
	if len(f.Blocks) == 0 {
		return Ref{}
	}
	return Ref{A: uint32(f.Blocks[0]), B: uint32(len(f.Blocks))}
}

func (c *contiguous) Load(r Ref, size int64) (*Inode, error) {
	f := &Inode{Size: size, Meta: -1}
	if int64(r.A)+int64(r.B) > c.bm.Len() {
		return nil, ErrCorrupt
	}
	for i := range int64(r.B) {
		f.Blocks = append(f.Blocks, int64(r.A)+i)
	}
	return f, nil
}

func (c *contiguous) AllocMeta() (int64, error) { return allocMeta(c.bm) }

func (c *contiguous) FreeMeta(b int64) error {
	c.bm.Clear(b)
	return nil
}

// findRun finds a free run of n blocks. owned is how many blocks the caller
// already holds, so the error can tell "disk full" from "fragmented".
func (c *contiguous) findRun(n, owned int64) (int64, error) {
	if start, ok := c.bm.FindRun(n); ok {
		return start, nil
	}
	if c.bm.FreeCount()+owned >= n {
		return 0, ErrNoContiguousSpace
	}
	return 0, ErrNoSpace
}

// take marks n blocks from start as used and returns them.
func (c *contiguous) take(start, n int64) []int64 {
	blocks := make([]int64, n)
	for i := range n {
		blocks[i] = start + i
		c.bm.Set(start + i)
	}
	return blocks
}

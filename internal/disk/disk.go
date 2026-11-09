// Package disk implements the physical layer: an in-memory disk of
// fixed-size blocks that store real bytes.
package disk

import (
	"errors"
	"fmt"

	"github.com/Mariojamjam/practice-os/internal/device"
)

var (
	// ErrOutOfRange is returned for a block index outside the disk.
	ErrOutOfRange = errors.New("block out of range")
	// ErrTooLarge is returned when written data exceeds the block size.
	ErrTooLarge = errors.New("data larger than block")
)

// Disk is an in-memory block device.
type Disk struct {
	blockSize int
	blocks    [][]byte
}

var _ device.Device = (*Disk)(nil)

// New returns a zeroed disk of count blocks of blockSize bytes.
func New(blockSize int, count int64) *Disk {
	blocks := make([][]byte, count)
	for i := range blocks {
		blocks[i] = make([]byte, blockSize)
	}
	return &Disk{blockSize: blockSize, blocks: blocks}
}

// BlockSize implements device.Device.
func (d *Disk) BlockSize() int { return d.blockSize }

// BlockCount implements device.Device.
func (d *Disk) BlockCount() int64 { return int64(len(d.blocks)) }

// Read implements device.Device.
func (d *Disk) Read(b int64) ([]byte, error) {
	if err := d.check(b); err != nil {
		return nil, err
	}
	out := make([]byte, d.blockSize)
	copy(out, d.blocks[b])
	return out, nil
}

// Write implements device.Device.
func (d *Disk) Write(b int64, data []byte) error {
	if err := d.check(b); err != nil {
		return err
	}
	if len(data) > d.blockSize {
		return fmt.Errorf("block %d: %w (%d > %d bytes)", b, ErrTooLarge, len(data), d.blockSize)
	}
	n := copy(d.blocks[b], data)
	clear(d.blocks[b][n:])
	return nil
}

func (d *Disk) check(b int64) error {
	if b < 0 || b >= int64(len(d.blocks)) {
		return fmt.Errorf("block %d: %w (disk has %d blocks)", b, ErrOutOfRange, len(d.blocks))
	}
	return nil
}

// Package device defines the block-device abstraction the file system is
// written against. Disks, SSDs and RAID arrays all implement Device, so the
// file system never knows what is underneath it.
package device

// Device is a fixed-size array of fixed-size blocks.
type Device interface {
	// BlockSize returns the size of every block in bytes.
	BlockSize() int
	// BlockCount returns the number of blocks.
	BlockCount() int64
	// Read returns a copy of block b; its length is always BlockSize.
	Read(b int64) ([]byte, error)
	// Write stores data at the start of block b and zero-fills the rest.
	// len(data) must not exceed BlockSize.
	Write(b int64, data []byte) error
}

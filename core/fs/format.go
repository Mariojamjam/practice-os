package fs

import (
	"bytes"
	"encoding/binary"
	"fmt"

	"github.com/Mariojamjam/practice-os/core/fs/alloc"
)

// Directory block layout (little-endian):
//
//	[0:4)  magic "PDIR"
//	[4:6)  number of entries
//	[6:8)  reserved
//	[8:)   entries, entrySize bytes each
//
// Entry layout:
//
//	[0:44)  name, UTF-8, NUL-padded
//	[44]    kind (1 = file, 2 = directory)
//	[45:48) reserved
//	[48:56) size in bytes
//	[56:60) Ref.A
//	[60:64) Ref.B
//
// For a directory entry, Ref.A is the directory's block.
const (
	dirMagic      = "PDIR"
	dirHeaderSize = 8
	entrySize     = 64
	// MaxNameLen is the longest file or directory name, in bytes.
	MaxNameLen = 44
)

// Kind tells files and directories apart.
type Kind uint8

// Node kinds.
const (
	KindFile Kind = 1
	KindDir  Kind = 2
)

func (k Kind) String() string {
	if k == KindDir {
		return "directory"
	}
	return "file"
}

type entry struct {
	name string
	kind Kind
	size int64
	ref  alloc.Ref
}

func (e entry) block() int64 { return int64(e.ref.A) }

func encodeEntry(e entry, b []byte) {
	copy(b[0:MaxNameLen], e.name)
	b[44] = byte(e.kind)
	binary.LittleEndian.PutUint64(b[48:56], uint64(e.size))
	binary.LittleEndian.PutUint32(b[56:60], e.ref.A)
	binary.LittleEndian.PutUint32(b[60:64], e.ref.B)
}

func decodeEntry(b []byte) entry {
	return entry{
		name: string(bytes.TrimRight(b[0:MaxNameLen], "\x00")),
		kind: Kind(b[44]),
		size: int64(binary.LittleEndian.Uint64(b[48:56])),
		ref: alloc.Ref{
			A: binary.LittleEndian.Uint32(b[56:60]),
			B: binary.LittleEndian.Uint32(b[60:64]),
		},
	}
}

// DirCapacity returns how many entries fit in one directory block of
// blockSize bytes.
func DirCapacity(blockSize int) int {
	return (blockSize - dirHeaderSize) / entrySize
}

func encodeDir(entries []entry, blockSize int) ([]byte, error) {
	if len(entries) > DirCapacity(blockSize) {
		return nil, ErrDirectoryFull
	}
	data := make([]byte, dirHeaderSize+len(entries)*entrySize)
	copy(data, dirMagic)
	binary.LittleEndian.PutUint16(data[4:6], uint16(len(entries)))
	for i, e := range entries {
		off := dirHeaderSize + i*entrySize
		encodeEntry(e, data[off:off+entrySize])
	}
	return data, nil
}

func decodeDir(data []byte) ([]entry, error) {
	if len(data) < dirHeaderSize || string(data[:4]) != dirMagic {
		return nil, fmt.Errorf("%w: not a directory block", ErrCorrupt)
	}
	n := int(binary.LittleEndian.Uint16(data[4:6]))
	if dirHeaderSize+n*entrySize > len(data) {
		return nil, fmt.Errorf("%w: directory lists %d entries", ErrCorrupt, n)
	}
	entries := make([]entry, n)
	for i := range entries {
		off := dirHeaderSize + i*entrySize
		entries[i] = decodeEntry(data[off : off+entrySize])
	}
	return entries, nil
}

// Synthetic returns n bytes of deterministic filler content starting at
// byte offset off of a file: the alphabet A–Z repeated.
func Synthetic(off, n int64) []byte {
	out := make([]byte, n)
	for i := range out {
		out[i] = byte('A' + (off+int64(i))%26)
	}
	return out
}

// Package fs implements a hierarchical file system on top of a block
// device. All metadata (directories, plus inodes or the FAT depending on
// the allocation strategy) is stored in device blocks; the only in-memory
// state is the free-block bitmap, the root block and the working directory.
package fs

import (
	"errors"
	"fmt"
	"path"
	"strings"

	"github.com/Mariojamjam/practice-os/internal/alloc"
	"github.com/Mariojamjam/practice-os/internal/device"
)

var (
	// ErrNotFound means a path component does not exist.
	ErrNotFound = errors.New("no such file or directory")
	// ErrExists means the target name is already taken.
	ErrExists = errors.New("already exists")
	// ErrNotDir means a directory was expected.
	ErrNotDir = errors.New("not a directory")
	// ErrIsDir means a file was expected.
	ErrIsDir = errors.New("is a directory")
	// ErrNotEmpty means a directory has entries and recursion was not asked.
	ErrNotEmpty = errors.New("directory not empty")
	// ErrDirectoryFull means a directory block has no room for another entry.
	ErrDirectoryFull = errors.New("directory is full")
	// ErrNameTooLong means a name exceeds MaxNameLen bytes.
	ErrNameTooLong = fmt.Errorf("name longer than %d bytes", MaxNameLen)
	// ErrInvalidName means a name is empty, "." or "..".
	ErrInvalidName = errors.New("invalid name")
	// ErrInvalid means the operation is not allowed on that path.
	ErrInvalid = errors.New("invalid operation")
	// ErrDiskNotEmpty means the allocation strategy can only change on an empty disk.
	ErrDiskNotEmpty = errors.New("disk is not empty")
	// ErrCorrupt means on-disk metadata is inconsistent.
	ErrCorrupt = errors.New("corrupt file system")
)

// Node describes a file or directory.
type Node struct {
	Path string
	Name string
	Kind Kind
	// Size is the file size in bytes (0 for directories).
	Size int64
	// Block is the directory block, for directories.
	Block int64

	ref alloc.Ref
}

// FS is a file system mounted on a device.
type FS struct {
	dev  device.Device
	bm   *alloc.Bitmap
	al   alloc.Allocator
	root int64
	cwd  string
}

// New formats dev with the given allocation strategy and returns the file
// system.
func New(dev device.Device, strategy string) (*FS, error) {
	f := &FS{dev: dev}
	if err := f.Format(strategy); err != nil {
		return nil, err
	}
	return f, nil
}

// Format erases the device and creates an empty file system.
func (f *FS) Format(strategy string) error {
	for b := range f.dev.BlockCount() {
		if err := f.dev.Write(b, nil); err != nil {
			return err
		}
	}
	bm := alloc.NewBitmap(f.dev.BlockCount())
	al, err := alloc.New(strategy, f.dev, bm)
	if err != nil {
		return err
	}
	root, err := al.AllocMeta()
	if err != nil {
		return err
	}
	f.bm, f.al, f.root, f.cwd = bm, al, root, "/"
	return f.writeDir(root, nil)
}

// SetStrategy changes the allocation strategy. The disk must be empty.
func (f *FS) SetStrategy(strategy string) error {
	entries, err := f.readDir(f.root)
	if err != nil {
		return err
	}
	if len(entries) > 0 {
		return fmt.Errorf("%w: remove every file and directory before changing the allocation strategy", ErrDiskNotEmpty)
	}
	return f.Format(strategy)
}

// Device returns the underlying device.
func (f *FS) Device() device.Device { return f.dev }

// Bitmap returns the free-block map.
func (f *FS) Bitmap() *alloc.Bitmap { return f.bm }

// Allocator returns the allocation strategy.
func (f *FS) Allocator() alloc.Allocator { return f.al }

// Strategy returns the allocation strategy name.
func (f *FS) Strategy() string { return f.al.Name() }

// BlockSize returns the device block size.
func (f *FS) BlockSize() int { return f.dev.BlockSize() }

// Root returns the root directory block.
func (f *FS) Root() int64 { return f.root }

// Getwd returns the working directory.
func (f *FS) Getwd() string { return f.cwd }

// Chdir changes the working directory.
func (f *FS) Chdir(p string) error {
	abs := f.abs(p)
	l, err := f.lookup(abs)
	if err != nil {
		return pathErr(p, err)
	}
	if l.e.kind != KindDir {
		return pathErr(p, ErrNotDir)
	}
	f.cwd = abs
	return nil
}

// Stat describes the node at p.
func (f *FS) Stat(p string) (Node, error) {
	abs := f.abs(p)
	l, err := f.lookup(abs)
	if err != nil {
		return Node{}, pathErr(p, err)
	}
	return makeNode(abs, l.e), nil
}

// List returns the entries of directory p in on-disk order, or the node
// itself if p is a file.
func (f *FS) List(p string) ([]Node, error) {
	abs := f.abs(p)
	l, err := f.lookup(abs)
	if err != nil {
		return nil, pathErr(p, err)
	}
	if l.e.kind != KindDir {
		return []Node{makeNode(abs, l.e)}, nil
	}
	entries, err := f.readDir(l.e.block())
	if err != nil {
		return nil, err
	}
	nodes := make([]Node, len(entries))
	for i, e := range entries {
		nodes[i] = makeNode(path.Join(abs, e.name), e)
	}
	return nodes, nil
}

// Walk calls fn for every node, depth-first in on-disk order, starting with
// the root directory.
func (f *FS) Walk(fn func(Node) error) error {
	rootNode := makeNode("/", f.rootEntry())
	if err := fn(rootNode); err != nil {
		return err
	}
	return f.walk(rootNode, fn)
}

func (f *FS) walk(dir Node, fn func(Node) error) error {
	children, err := f.List(dir.Path)
	if err != nil {
		return err
	}
	for _, c := range children {
		if err := fn(c); err != nil {
			return err
		}
		if c.Kind == KindDir {
			if err := f.walk(c, fn); err != nil {
				return err
			}
		}
	}
	return nil
}

// Inode loads the allocation of file n.
func (f *FS) Inode(n Node) (*alloc.Inode, error) {
	if n.Kind != KindFile {
		return nil, pathErr(n.Path, ErrIsDir)
	}
	return f.al.Load(n.ref, n.Size)
}

// Mkdir creates directory p. Its parent must exist.
func (f *FS) Mkdir(p string) error {
	abs := f.abs(p)
	parent, entries, name, err := f.prepareCreate(abs, true)
	if err != nil {
		return pathErr(p, err)
	}
	b, err := f.al.AllocMeta()
	if err != nil {
		return pathErr(p, err)
	}
	if err := f.writeDir(b, nil); err != nil {
		return err
	}
	entries = append(entries, entry{name: name, kind: KindDir, ref: alloc.Ref{A: uint32(b)}})
	return f.writeDir(parent, entries)
}

// Create creates file p with the given content. Its parent must exist.
func (f *FS) Create(p string, data []byte) error {
	abs := f.abs(p)
	parent, entries, name, err := f.prepareCreate(abs, true)
	if err != nil {
		return pathErr(p, err)
	}
	ino := &alloc.Inode{Size: int64(len(data))}
	if err := f.al.Allocate(ino, f.blocksFor(ino.Size)); err != nil {
		return pathErr(p, err)
	}
	if err := f.writeData(ino, data, 0); err != nil {
		return err
	}
	entries = append(entries, entry{name: name, kind: KindFile, size: ino.Size, ref: f.al.Ref(ino)})
	return f.writeDir(parent, entries)
}

// Read returns the content of file p.
func (f *FS) Read(p string) ([]byte, error) {
	abs := f.abs(p)
	l, err := f.lookup(abs)
	if err != nil {
		return nil, pathErr(p, err)
	}
	if l.e.kind != KindFile {
		return nil, pathErr(p, ErrIsDir)
	}
	return f.readFile(l.e)
}

// Append adds data to the end of file p.
func (f *FS) Append(p string, data []byte) error {
	old, err := f.Read(p)
	if err != nil {
		return err
	}
	return f.setContent(p, append(old, data...), int64(len(old)))
}

// Overwrite replaces the content of file p.
func (f *FS) Overwrite(p string, data []byte) error {
	if _, err := f.Read(p); err != nil {
		return err
	}
	return f.setContent(p, data, 0)
}

// Resize truncates file p, or extends it with synthetic content.
func (f *FS) Resize(p string, size int64) error {
	old, err := f.Read(p)
	if err != nil {
		return err
	}
	cur := int64(len(old))
	if size <= cur {
		return f.setContent(p, old[:size], size)
	}
	return f.setContent(p, append(old, Synthetic(cur, size-cur)...), cur)
}

// Remove deletes p. A non-empty directory needs recursive.
func (f *FS) Remove(p string, recursive bool) error {
	abs := f.abs(p)
	if abs == "/" {
		return pathErr(p, fmt.Errorf("%w: cannot remove the root directory", ErrInvalid))
	}
	if f.cwd == abs || strings.HasPrefix(f.cwd, abs+"/") {
		return pathErr(p, fmt.Errorf("%w: cannot remove the working directory or one of its parents", ErrInvalid))
	}
	l, err := f.lookup(abs)
	if err != nil {
		return pathErr(p, err)
	}
	if l.e.kind == KindDir && !recursive {
		children, err := f.readDir(l.e.block())
		if err != nil {
			return err
		}
		if len(children) > 0 {
			return pathErr(p, ErrNotEmpty)
		}
	}
	if err := f.freeTree(l.e); err != nil {
		return err
	}
	entries, err := f.readDir(l.parent)
	if err != nil {
		return err
	}
	return f.writeDir(l.parent, append(entries[:l.idx], entries[l.idx+1:]...))
}

// Move renames or moves src to dst. If dst is an existing directory, src
// is moved into it. Only directory entries change; data stays in place.
func (f *FS) Move(src, dst string) error {
	sAbs, dAbs := f.abs(src), f.abs(dst)
	if sAbs == "/" {
		return pathErr(src, fmt.Errorf("%w: cannot move the root directory", ErrInvalid))
	}
	sl, err := f.lookup(sAbs)
	if err != nil {
		return pathErr(src, err)
	}
	if dl, err := f.lookup(dAbs); err == nil {
		if dl.e.kind != KindDir {
			return pathErr(dst, ErrExists)
		}
		dAbs = path.Join(dAbs, sl.e.name)
	}
	if dAbs == sAbs {
		return nil
	}
	if sl.e.kind == KindDir && strings.HasPrefix(dAbs, sAbs+"/") {
		return pathErr(dst, fmt.Errorf("%w: cannot move a directory into itself", ErrInvalid))
	}

	// A rename inside the same directory needs no extra room.
	sameDir := path.Dir(dAbs) == path.Dir(sAbs)
	parent, entries, name, err := f.prepareCreate(dAbs, !sameDir)
	if err != nil {
		return pathErr(dst, err)
	}
	moved := sl.e
	moved.name = name
	if parent == sl.parent {
		entries[sl.idx] = moved
		if err := f.writeDir(parent, entries); err != nil {
			return err
		}
	} else {
		if err := f.writeDir(parent, append(entries, moved)); err != nil {
			return err
		}
		old, err := f.readDir(sl.parent)
		if err != nil {
			return err
		}
		if err := f.writeDir(sl.parent, append(old[:sl.idx], old[sl.idx+1:]...)); err != nil {
			return err
		}
	}
	if f.cwd == sAbs || strings.HasPrefix(f.cwd, sAbs+"/") {
		f.cwd = dAbs + strings.TrimPrefix(f.cwd, sAbs)
	}
	return nil
}

// loc is where an entry lives: the directory block holding it and its index.
// The root has parent -1.
type loc struct {
	parent int64
	idx    int
	e      entry
}

func (f *FS) rootEntry() entry {
	return entry{name: "/", kind: KindDir, ref: alloc.Ref{A: uint32(f.root)}}
}

// lookup resolves an absolute, clean path by reading directory blocks.
func (f *FS) lookup(abs string) (loc, error) {
	cur := loc{parent: -1, idx: -1, e: f.rootEntry()}
	if abs == "/" {
		return cur, nil
	}
	for _, part := range strings.Split(abs[1:], "/") {
		if cur.e.kind != KindDir {
			return loc{}, ErrNotDir
		}
		dir := cur.e.block()
		entries, err := f.readDir(dir)
		if err != nil {
			return loc{}, err
		}
		found := false
		for i, e := range entries {
			if e.name == part {
				cur, found = loc{parent: dir, idx: i, e: e}, true
				break
			}
		}
		if !found {
			return loc{}, ErrNotFound
		}
	}
	return cur, nil
}

// prepareCreate checks that abs can be created: its parent is a directory
// with room (if needRoom), and the name is valid and free. It returns the parent block,
// its entries and the new name.
func (f *FS) prepareCreate(abs string, needRoom bool) (int64, []entry, string, error) {
	dir, name := path.Split(abs)
	if err := validName(name); err != nil {
		return 0, nil, "", err
	}
	pl, err := f.lookup(path.Clean(dir))
	if err != nil {
		return 0, nil, "", err
	}
	if pl.e.kind != KindDir {
		return 0, nil, "", ErrNotDir
	}
	entries, err := f.readDir(pl.e.block())
	if err != nil {
		return 0, nil, "", err
	}
	for _, e := range entries {
		if e.name == name {
			return 0, nil, "", ErrExists
		}
	}
	if needRoom && len(entries) >= DirCapacity(f.BlockSize()) {
		return 0, nil, "", fmt.Errorf("%w: %d entries per directory with %d-byte blocks",
			ErrDirectoryFull, DirCapacity(f.BlockSize()), f.BlockSize())
	}
	return pl.e.block(), entries, name, nil
}

func validName(name string) error {
	switch {
	case name == "" || name == "." || name == ".." || strings.ContainsRune(name, 0):
		return fmt.Errorf("%w: %q", ErrInvalidName, name)
	case len(name) > MaxNameLen:
		return ErrNameTooLong
	}
	return nil
}

// setContent stores data as the new content of file p, writing blocks from
// byte offset from onwards (earlier blocks are unchanged).
func (f *FS) setContent(p string, data []byte, from int64) error {
	l, err := f.lookup(f.abs(p))
	if err != nil {
		return pathErr(p, err)
	}
	ino, err := f.al.Load(l.e.ref, l.e.size)
	if err != nil {
		return err
	}
	ino.Size = int64(len(data))
	if err := f.al.Resize(ino, f.blocksFor(ino.Size)); err != nil {
		return pathErr(p, err)
	}
	if err := f.writeData(ino, data, from); err != nil {
		return err
	}
	entries, err := f.readDir(l.parent)
	if err != nil {
		return err
	}
	entries[l.idx].size, entries[l.idx].ref = ino.Size, f.al.Ref(ino)
	return f.writeDir(l.parent, entries)
}

func (f *FS) readFile(e entry) ([]byte, error) {
	ino, err := f.al.Load(e.ref, e.size)
	if err != nil {
		return nil, err
	}
	out := make([]byte, 0, ino.Size)
	for _, b := range f.al.Blocks(ino) {
		data, err := f.dev.Read(b)
		if err != nil {
			return nil, err
		}
		out = append(out, data...)
	}
	if int64(len(out)) < ino.Size {
		return nil, fmt.Errorf("%w: file has %d bytes in blocks, size says %d", ErrCorrupt, len(out), ino.Size)
	}
	return out[:ino.Size], nil
}

func (f *FS) writeData(ino *alloc.Inode, data []byte, from int64) error {
	bs := int64(f.BlockSize())
	blocks := f.al.Blocks(ino)
	for i := from / bs; i < int64(len(blocks)); i++ {
		end := min((i+1)*bs, int64(len(data)))
		if err := f.dev.Write(blocks[i], data[i*bs:end]); err != nil {
			return err
		}
	}
	return nil
}

func (f *FS) freeTree(e entry) error {
	if e.kind == KindFile {
		ino, err := f.al.Load(e.ref, e.size)
		if err != nil {
			return err
		}
		return f.al.Free(ino)
	}
	children, err := f.readDir(e.block())
	if err != nil {
		return err
	}
	for _, c := range children {
		if err := f.freeTree(c); err != nil {
			return err
		}
	}
	return f.al.FreeMeta(e.block())
}

func (f *FS) readDir(b int64) ([]entry, error) {
	data, err := f.dev.Read(b)
	if err != nil {
		return nil, err
	}
	entries, err := decodeDir(data)
	if err != nil {
		return nil, fmt.Errorf("block %d: %w", b, err)
	}
	return entries, nil
}

func (f *FS) writeDir(b int64, entries []entry) error {
	data, err := encodeDir(entries, f.BlockSize())
	if err != nil {
		return err
	}
	return f.dev.Write(b, data)
}

func (f *FS) blocksFor(size int64) int {
	bs := int64(f.BlockSize())
	return int((size + bs - 1) / bs)
}

// abs turns p into a clean absolute path relative to the working directory.
func (f *FS) abs(p string) string {
	if p == "" {
		return f.cwd
	}
	if !path.IsAbs(p) {
		p = path.Join(f.cwd, p)
	}
	return path.Clean(p)
}

func makeNode(abs string, e entry) Node {
	n := Node{Path: abs, Name: e.name, Kind: e.kind, Size: e.size, ref: e.ref}
	if e.kind == KindDir {
		n.Block, n.Size = e.block(), 0
	}
	return n
}

func pathErr(p string, err error) error {
	return fmt.Errorf("%s: %w", p, err)
}

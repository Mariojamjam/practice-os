package shell

import (
	"github.com/Mariojamjam/practice-os/core/fs"
	"github.com/Mariojamjam/practice-os/core/fs/diag"
	"github.com/Mariojamjam/practice-os/core/storage/blockio"
	"github.com/Mariojamjam/practice-os/core/storage/raid"
	"github.com/Mariojamjam/practice-os/core/storage/sched"
	"github.com/Mariojamjam/practice-os/core/storage/ssd"
)

// Result is the typed outcome of a command. Interfaces decide how to show
// it: package render turns it into text, the TUI draws it.
type Result interface {
	result()
}

// PathResult is a path, e.g. from pwd.
type PathResult struct {
	Path string
}

// ListResult is the content of a directory (or a single file) from ls.
type ListResult struct {
	Path    string
	Entries []fs.Node
}

// TreeNode is a node of a TreeResult.
type TreeNode struct {
	Name     string
	Kind     fs.Kind
	Size     int64
	Children []TreeNode
}

// TreeResult is a directory tree from tree.
type TreeResult struct {
	Root TreeNode
}

// FileResult is the content of a file from read_file.
type FileResult struct {
	Path string
	Data []byte
}

// StatusResult is a disk analysis from fs_status.
type StatusResult struct {
	Report  diag.Report
	Details bool
}

// CompactResult is the outcome of compact.
type CompactResult struct {
	diag.CompactResult
}

// MessageResult is a plain informational message.
type MessageResult struct {
	Text string
}

// SchedResult is a standalone disk-arm schedule from sched.
type SchedResult struct {
	sched.Result
	// Tracks is the number of tracks on the disk.
	Tracks int
}

// IOResult reports I/O requests from io_flush (served) or io_queue
// (Pending: still queued).
type IOResult struct {
	Pending bool
	Flushes []blockio.Flush
}

// DiskState is the health of one disk in an array.
type DiskState struct {
	Name   string
	Failed bool
}

// RAIDStatusResult describes a disk array and the stripes in use.
type RAIDStatusResult struct {
	Name      string
	Level     int
	Disks     []DiskState
	BlockSize int
	// Capacity is the array's usable size, in blocks.
	Capacity int64
	// Path limits Stripes to the stripes of one file or directory ("" for all).
	Path    string
	Stripes [][]raid.Slot
	// Report tells who owns each logical block.
	Report diag.Report
}

// FailResult reports a simulated disk failure.
type FailResult struct {
	Array string
	Level int
	// Disk is the 1-based disk number.
	Disk int
}

// RebuildResult reports the disks restored by rebuild.
type RebuildResult struct {
	Array   string
	Rebuilt []raid.Rebuilt
}

// WearResult reports SSD wear.
type WearResult struct {
	Wear []ssd.Wear
}

func (PathResult) result()       {}
func (SchedResult) result()      {}
func (IOResult) result()         {}
func (RAIDStatusResult) result() {}
func (FailResult) result()       {}
func (RebuildResult) result()    {}
func (WearResult) result()       {}
func (ListResult) result()       {}
func (TreeResult) result()       {}
func (FileResult) result()       {}
func (StatusResult) result()     {}
func (CompactResult) result()    {}
func (MessageResult) result()    {}

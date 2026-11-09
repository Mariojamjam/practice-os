package shell

import (
	"github.com/Mariojamjam/practice-os/internal/diag"
	"github.com/Mariojamjam/practice-os/internal/fs"
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

func (PathResult) result()    {}
func (ListResult) result()    {}
func (TreeResult) result()    {}
func (FileResult) result()    {}
func (StatusResult) result()  {}
func (CompactResult) result() {}
func (MessageResult) result() {}

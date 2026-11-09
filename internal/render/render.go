// Package render turns shell results into plain text for terminals,
// scripts and golden tests.
package render

import (
	"encoding/hex"
	"fmt"
	"strings"
	"unicode"
	"unicode/utf8"

	"github.com/Mariojamjam/practice-os/internal/alloc"
	"github.com/Mariojamjam/practice-os/internal/config"
	"github.com/Mariojamjam/practice-os/internal/diag"
	"github.com/Mariojamjam/practice-os/internal/fs"
	"github.com/Mariojamjam/practice-os/internal/shell"
)

// Options controls rendering.
type Options struct {
	// ASCII replaces box-drawing characters with plain ASCII.
	ASCII bool
}

// maxInlineFile is the largest text file read_file prints in full.
const maxInlineFile = 1024

// Result renders a command result. A nil result renders as "".
// Non-empty output always ends with a newline.
func Result(r shell.Result, o Options) string {
	var b strings.Builder
	switch r := r.(type) {
	case nil:
		return ""
	case shell.PathResult:
		b.WriteString(r.Path + "\n")
	case shell.MessageResult:
		b.WriteString(r.Text + "\n")
	case shell.ListResult:
		for _, n := range r.Entries {
			b.WriteString(nodeLabel(n.Name, n.Kind, n.Size) + "\n")
		}
	case shell.TreeResult:
		tree(&b, r.Root, o)
	case shell.FileResult:
		file(&b, r)
	case shell.StatusResult:
		if r.Details {
			details(&b, r.Report)
		} else {
			summary(&b, r.Report)
		}
	case shell.CompactResult:
		compaction(&b, r.CompactResult)
	default:
		fmt.Fprintf(&b, "%v\n", r)
	}
	return b.String()
}

// Error renders a command error.
func Error(err error) string {
	return "error: " + err.Error() + "\n"
}

func nodeLabel(name string, kind fs.Kind, size int64) string {
	if kind == fs.KindDir {
		return name + "/ [DIR]"
	}
	return fmt.Sprintf("%s (%s) [FILE]", name, config.FormatSize(size))
}

func tree(b *strings.Builder, root shell.TreeNode, o Options) {
	b.WriteString("[FILE SYSTEM TREE]\n")
	switch {
	case root.Kind != fs.KindDir:
		b.WriteString(nodeLabel(root.Name, root.Kind, root.Size) + "\n")
		return
	case root.Name == "/":
		b.WriteString("/\n")
	default:
		b.WriteString(root.Name + "/\n")
	}
	branch, last, pipe := "├── ", "└── ", "│   "
	if o.ASCII {
		branch, last, pipe = "|-- ", "`-- ", "|   "
	}
	var walk func(children []shell.TreeNode, prefix string)
	walk = func(children []shell.TreeNode, prefix string) {
		for i, c := range children {
			connector, next := branch, pipe
			if i == len(children)-1 {
				connector, next = last, "    "
			}
			b.WriteString(prefix + connector + nodeLabel(c.Name, c.Kind, c.Size) + "\n")
			walk(c.Children, prefix+next)
		}
	}
	walk(root.Children, "")
}

func file(b *strings.Builder, r shell.FileResult) {
	if len(r.Data) == 0 {
		b.WriteString("(empty file)\n")
		return
	}
	if len(r.Data) <= maxInlineFile && isText(r.Data) {
		b.Write(r.Data)
		if r.Data[len(r.Data)-1] != '\n' {
			b.WriteByte('\n')
		}
		return
	}
	n := min(len(r.Data), 64)
	fmt.Fprintf(b, "'%s': %d bytes (%s); first %d bytes:\n", r.Path, len(r.Data),
		config.FormatSize(int64(len(r.Data))), n)
	b.WriteString(hex.Dump(r.Data[:n]))
}

func isText(data []byte) bool {
	if !utf8.Valid(data) {
		return false
	}
	for _, r := range string(data) {
		if !unicode.IsPrint(r) && r != '\n' && r != '\t' && r != '\r' {
			return false
		}
	}
	return true
}

func geometry(b *strings.Builder, r diag.Report) {
	fmt.Fprintf(b, "Block size: %s | Total blocks: %d (%s)\n",
		config.FormatSize(int64(r.BlockSize)), r.TotalBlocks, config.FormatSize(int64(r.BlockSize)*r.TotalBlocks))
}

func summary(b *strings.Builder, r diag.Report) {
	fmt.Fprintf(b, "Allocation strategy: %s\n", r.Strategy)
	geometry(b, r)
	used := r.TotalBlocks - r.FreeBlocks
	fmt.Fprintf(b, "Used blocks: %d (%d metadata, %d data) | Free blocks: %d\n",
		used, r.MetaBlocks, used-r.MetaBlocks, r.FreeBlocks)
	fmt.Fprintf(b, "Internal fragmentation: %d bytes\n", r.Internal)
	fmt.Fprintf(b, "External fragmentation: %s\n", external(r))
	fmt.Fprintf(b, "Compaction needed: %s\n", compactionNeeded(r))
}

func details(b *strings.Builder, r diag.Report) {
	geometry(b, r)
	fmt.Fprintf(b, "\n[DISK ALLOCATION MAP (%s)]\n", r.Strategy)
	blockMap(b, r)

	b.WriteString("\n--- FRAGMENTATION REPORT ---\n")
	if len(r.Files) == 0 {
		b.WriteString("No files.\n")
	}
	bs := int64(r.BlockSize)
	for _, f := range r.Files {
		fmt.Fprintf(b, "File '%s'\n", f.Path)
		fmt.Fprintf(b, "  Size                   : %d bytes (%s)\n", f.Size, config.FormatSize(f.Size))
		fmt.Fprintf(b, "  Allocated on disk      : %d bytes (%s of %s)\n", f.Allocated, plural(int64(f.Blocks), "block"), config.FormatSize(bs))
		if f.Internal > 0 {
			fmt.Fprintf(b, "  Internal fragmentation : %d bytes (%s%% waste in block %s)\n",
				f.Internal, percent(f.Internal, bs), blockNum(f.LastBlock, r.TotalBlocks))
		} else {
			b.WriteString("  Internal fragmentation : 0 bytes\n")
		}
	}
	fmt.Fprintf(b, "Total internal fragmentation : %d bytes\n", r.Internal)
	fmt.Fprintf(b, "External fragmentation       : %s\n", external(r))
	fmt.Fprintf(b, "Metadata overhead            : %s (%s)\n", plural(r.MetaBlocks, "block"), config.FormatSize(r.MetaBlocks*bs))
	fmt.Fprintf(b, "Compaction needed            : %s\n", compactionNeeded(r))
}

// blockMap prints one line per block, collapsing runs of free blocks.
func blockMap(b *strings.Builder, r diag.Report) {
	type line struct{ left, right string }
	var lines []line
	for i := 0; i < len(r.Blocks); i++ {
		blk := r.Blocks[i]
		if blk.Kind == diag.KindFree {
			j := i
			for j+1 < len(r.Blocks) && r.Blocks[j+1].Kind == diag.KindFree {
				j++
			}
			left := "Block " + blockNum(int64(i), r.TotalBlocks)
			if j > i {
				left += ".." + blockNum(int64(j), r.TotalBlocks)
			}
			lines = append(lines, line{left, "[FREE]"})
			i = j
			continue
		}
		left := fmt.Sprintf("Block %s [%s]", blockNum(blk.Index, r.TotalBlocks), blk.Kind)
		lines = append(lines, line{left, describe(blk, r)})
	}
	width := 0
	for _, l := range lines {
		width = max(width, len(l.left))
	}
	for _, l := range lines {
		fmt.Fprintf(b, "%-*s : %s\n", width, l.left, l.right)
	}
}

func describe(blk diag.Block, r diag.Report) string {
	switch blk.Kind {
	case diag.KindFAT:
		return "file allocation table"
	case diag.KindRootInode, diag.KindRootDir, diag.KindDirInode, diag.KindDir:
		return fmt.Sprintf("directory '%s'", blk.Path)
	case diag.KindFileInode:
		return fmt.Sprintf("file '%s'", blk.Path)
	case diag.KindData:
		s := fmt.Sprintf("'%s' (block %d - %d bytes used", blk.Path, blk.Seq, blk.Used)
		if r.Strategy == alloc.Linked {
			if blk.Next >= 0 {
				s += ", next: " + blockNum(blk.Next, r.TotalBlocks)
			} else {
				s += ", end of chain"
			}
		}
		return s + ")"
	}
	return ""
}

func external(r diag.Report) string {
	if r.Strategy != alloc.Contiguous {
		return "0 bytes"
	}
	switch len(r.FreeRuns) {
	case 0:
		return "0 bytes (no free space)"
	case 1:
		return "0 bytes (free space is contiguous)"
	}
	return fmt.Sprintf("%d bytes (%s in %d runs; largest run: %s)",
		r.External, plural(r.FreeBlocks, "free block"), len(r.FreeRuns), plural(r.Largest, "block"))
}

func compactionNeeded(r diag.Report) string {
	switch {
	case r.Strategy == alloc.Linked:
		return "NO (linked allocation: files need not be contiguous)"
	case r.Strategy == alloc.Indexed:
		return "NO (indexed allocation: files need not be contiguous)"
	case r.CompactionNeeded:
		return fmt.Sprintf("YES (free space is split into %d runs; a file larger than %s cannot be stored; run 'compact')",
			len(r.FreeRuns), plural(r.Largest, "block"))
	case r.FreeBlocks == 0:
		return "NO (no free space)"
	}
	return "NO (free space is contiguous)"
}

func compaction(b *strings.Builder, c diag.CompactResult) {
	b.WriteString("[DISK COMPACTION]\n")
	if len(c.Moves) == 0 {
		b.WriteString("Nothing to move: used blocks are already packed at the start of the disk.\n")
	}
	total := c.After.TotalBlocks
	for _, m := range c.Moves {
		fmt.Fprintf(b, "Moved '%s': blocks %s -> %s\n", m.Path, blockList(m.From, total), blockList(m.To, total))
	}
	fmt.Fprintf(b, "Free space: %s in %s; largest run: %s (%s)\n",
		plural(c.After.FreeBlocks, "block"), plural(int64(len(c.After.FreeRuns)), "run"), plural(c.After.Largest, "block"),
		config.FormatSize(c.After.Largest*int64(c.After.BlockSize)))
	if c.After.Strategy == alloc.Contiguous {
		fmt.Fprintf(b, "External fragmentation: %d bytes -> %d bytes\n", c.Before.External, c.After.External)
	}
}

// blockNum formats a block index zero-padded to the width of the disk's
// largest index (at least two digits).
func blockNum(b, total int64) string {
	width := max(2, len(fmt.Sprint(total-1)))
	return fmt.Sprintf("%0*d", width, b)
}

// blockList formats blocks compactly: "04..06, 09".
func blockList(blocks []int64, total int64) string {
	var parts []string
	for i := 0; i < len(blocks); {
		j := i
		for j+1 < len(blocks) && blocks[j+1] == blocks[j]+1 {
			j++
		}
		part := blockNum(blocks[i], total)
		if j > i {
			part += ".." + blockNum(blocks[j], total)
		}
		parts = append(parts, part)
		i = j + 1
	}
	return strings.Join(parts, ", ")
}

// percent formats part/whole as a percentage with at most one decimal.
func percent(part, whole int64) string {
	s := fmt.Sprintf("%.1f", float64(part)*100/float64(whole))
	return strings.TrimSuffix(s, ".0")
}

// plural formats a count with a noun, adding "s" unless the count is 1.
func plural(n int64, noun string) string {
	if n == 1 {
		return "1 " + noun
	}
	return fmt.Sprintf("%d %ss", n, noun)
}

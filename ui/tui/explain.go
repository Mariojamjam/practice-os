package tui

import (
	"errors"
	"fmt"
	"path"
	"strings"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/fs"
	"github.com/Mariojamjam/practice-os/core/fs/alloc"
	"github.com/Mariojamjam/practice-os/core/fs/diag"
	"github.com/Mariojamjam/practice-os/core/storage/raid"
	"github.com/Mariojamjam/practice-os/ui/shell"
)

// explain returns a plain-language sentence about what a command did to
// the disk, or "" when the command's own output says it all.
func explain(a *App, line string, _ shell.Result, err error, before snapshot) string {
	words, _ := shell.Tokenize(line)
	if len(words) == 0 {
		return ""
	}
	if err != nil {
		switch {
		case errors.Is(err, alloc.ErrNoContiguousSpace):
			return "There is enough free space in total, but it is split into holes and none is large enough. " +
				"Run compact to pack the used blocks together."
		case errors.Is(err, alloc.ErrNoSpace):
			return "The disk is full: remove files, or start with a larger disk (--blocks)."
		case errors.Is(err, raid.ErrDataLost):
			return "RAID 0 keeps no redundancy: what was on the failed disk is gone."
		case errors.Is(err, fs.ErrDirectoryFull):
			return "A directory occupies one block, so it holds a limited number of entries."
		}
		return ""
	}

	snap := a.snap
	target := firstPath(words[1:])
	abs := target
	if abs != "" && !path.IsAbs(abs) {
		abs = path.Join(before.cwd, abs)
	}
	abs = path.Clean(abs)
	bs := int64(snap.report.BlockSize)

	switch words[0] {
	case "mkdir":
		if blocks := snap.blocksOf(abs); len(blocks) == 1 {
			return fmt.Sprintf("%s takes block %d, which stores its directory entries.", abs, blocks[0].Index)
		}
	case "create", "write_file", "update":
		fr, ok := snap.fileReport(abs)
		if !ok {
			return ""
		}
		if fr.Blocks == 0 {
			return fmt.Sprintf("%s is empty: it uses no data blocks.", abs)
		}
		var nums []string
		for _, b := range snap.blocksOf(abs) {
			if b.Kind == diag.KindData {
				nums = append(nums, fmt.Sprint(b.Index))
			}
		}
		used := bs - fr.Internal
		return fmt.Sprintf("%s: %d bytes in %d blocks of %s (blocks %s). The last block holds %d of %d bytes, so %d bytes are internal fragmentation.",
			abs, fr.Size, fr.Blocks, config.FormatSize(bs), strings.Join(nums, ", "), used, bs, fr.Internal)
	case "rm":
		freed := snap.report.FreeBlocks - before.report.FreeBlocks
		return fmt.Sprintf("%d blocks were freed; %d of %d blocks are free now.", freed, snap.report.FreeBlocks, snap.report.TotalBlocks)
	case "mv":
		return "Only the directory entries changed: the data stayed in the same blocks."
	}
	return ""
}

// firstPath returns the first positional argument, skipping flags and the
// value of --size.
func firstPath(args []string) string {
	for i := 0; i < len(args); i++ {
		switch {
		case args[i] == "--size":
			i++
		case strings.HasPrefix(args[i], "-"):
		default:
			return args[i]
		}
	}
	return ""
}

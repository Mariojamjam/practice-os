package shell

import (
	"errors"
	"fmt"

	"github.com/spf13/pflag"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/fs"
	"github.com/Mariojamjam/practice-os/core/fs/diag"
)

// fsCommands are the file-system commands (Stage 1).
var fsCommands = map[string]command{
	"pwd": {
		usage: "pwd",
		run: func(s *Shell, _ *pflag.FlagSet, _ []string) (Result, error) {
			return PathResult{Path: s.k.FS.Getwd()}, nil
		},
	},
	"cd": {
		usage: "cd [PATH]",
		args:  [2]int{0, 1},
		run: func(s *Shell, _ *pflag.FlagSet, args []string) (Result, error) {
			target := "/"
			if len(args) == 1 {
				target = args[0]
			}
			return nil, s.k.FS.Chdir(target)
		},
	},
	"ls": {
		usage: "ls [PATH]",
		args:  [2]int{0, 1},
		run: func(s *Shell, _ *pflag.FlagSet, args []string) (Result, error) {
			p := pathArg(args)
			n, err := s.k.FS.Stat(p)
			if err != nil {
				return nil, err
			}
			entries, err := s.k.FS.List(p)
			if err != nil {
				return nil, err
			}
			return ListResult{Path: n.Path, Entries: entries}, nil
		},
	},
	"tree": {
		usage: "tree [PATH]",
		args:  [2]int{0, 1},
		run: func(s *Shell, _ *pflag.FlagSet, args []string) (Result, error) {
			n, err := s.k.FS.Stat(pathArg(args))
			if err != nil {
				return nil, err
			}
			root, err := buildTree(s.k.FS, n)
			if err != nil {
				return nil, err
			}
			root.Name = n.Path
			return TreeResult{Root: root}, nil
		},
	},
	"mkdir": {
		usage: "mkdir PATH",
		args:  [2]int{1, 1},
		run: func(s *Shell, _ *pflag.FlagSet, args []string) (Result, error) {
			return nil, s.k.FS.Mkdir(args[0])
		},
	},
	"create": {
		usage: `create PATH --size SIZE | create PATH "TEXT"`,
		flags: func(fl *pflag.FlagSet) { fl.String("size", "", "file size, e.g. 10KB (synthetic content)") },
		args:  [2]int{1, 2},
		run: func(s *Shell, fl *pflag.FlagSet, args []string) (Result, error) {
			data, err := contentArg(fl, args)
			if err != nil {
				return nil, err
			}
			return nil, s.k.FS.Create(args[0], data)
		},
	},
	"read_file": {
		usage: "read_file PATH",
		args:  [2]int{1, 1},
		run: func(s *Shell, _ *pflag.FlagSet, args []string) (Result, error) {
			n, err := s.k.FS.Stat(args[0])
			if err != nil {
				return nil, err
			}
			data, err := s.k.FS.Read(args[0])
			if err != nil {
				return nil, err
			}
			return FileResult{Path: n.Path, Data: data}, nil
		},
	},
	"write_file": {
		usage: `write_file PATH "TEXT" [--truncate] | write_file PATH --size SIZE`,
		flags: func(fl *pflag.FlagSet) {
			fl.String("size", "", "overwrite with SIZE bytes of synthetic content")
			fl.Bool("truncate", false, "overwrite instead of appending")
		},
		args: [2]int{1, 2},
		run: func(s *Shell, fl *pflag.FlagSet, args []string) (Result, error) {
			truncate, _ := fl.GetBool("truncate")
			if truncate && len(args) < 2 {
				return nil, errors.New("--truncate needs TEXT")
			}
			data, err := contentArg(fl, args)
			if err != nil {
				return nil, err
			}
			if fl.Changed("size") || truncate {
				return nil, s.k.FS.Overwrite(args[0], data)
			}
			return nil, s.k.FS.Append(args[0], data)
		},
	},
	"update": {
		usage: "update PATH --size SIZE",
		flags: func(fl *pflag.FlagSet) { fl.String("size", "", "new file size (truncates or extends)") },
		args:  [2]int{1, 1},
		run: func(s *Shell, fl *pflag.FlagSet, args []string) (Result, error) {
			if !fl.Changed("size") {
				return nil, errors.New("--size is required")
			}
			size, err := sizeFlag(fl)
			if err != nil {
				return nil, err
			}
			return nil, s.k.FS.Resize(args[0], size)
		},
	},
	"rm": {
		usage: "rm [-r] PATH",
		flags: func(fl *pflag.FlagSet) { fl.BoolP("recursive", "r", false, "remove directories and their content") },
		args:  [2]int{1, 1},
		run: func(s *Shell, fl *pflag.FlagSet, args []string) (Result, error) {
			recursive, _ := fl.GetBool("recursive")
			return nil, s.k.FS.Remove(args[0], recursive)
		},
	},
	"mv": {
		usage: "mv SRC DST",
		args:  [2]int{2, 2},
		run: func(s *Shell, _ *pflag.FlagSet, args []string) (Result, error) {
			return nil, s.k.FS.Move(args[0], args[1])
		},
	},
	"fs_status": {
		usage: "fs_status [--details]",
		flags: func(fl *pflag.FlagSet) { fl.Bool("details", false, "show the block map and per-file report") },
		run: func(s *Shell, fl *pflag.FlagSet, _ []string) (Result, error) {
			details, _ := fl.GetBool("details")
			r, err := diag.Analyze(s.k.FS)
			if err != nil {
				return nil, err
			}
			return StatusResult{Report: r, Details: details}, nil
		},
	},
	"compact": {
		usage: "compact",
		run: func(s *Shell, _ *pflag.FlagSet, _ []string) (Result, error) {
			res, err := diag.Compact(s.k.FS)
			if err != nil {
				return nil, err
			}
			return CompactResult{CompactResult: res}, nil
		},
	},
	"set_alloc": {
		usage: "set_alloc contiguous|linked|indexed",
		args:  [2]int{1, 1},
		run: func(s *Shell, _ *pflag.FlagSet, args []string) (Result, error) {
			if err := s.k.FS.SetStrategy(args[0]); err != nil {
				return nil, err
			}
			return MessageResult{Text: fmt.Sprintf("Allocation strategy is now %s; the disk was formatted.", args[0])}, nil
		},
	},
}

func pathArg(args []string) string {
	if len(args) == 1 {
		return args[0]
	}
	return ""
}

// contentArg returns the content given either as TEXT (args[1]) or with
// --size (synthetic). Exactly one of them is required.
func contentArg(fl *pflag.FlagSet, args []string) ([]byte, error) {
	hasText, hasSize := len(args) == 2, fl.Changed("size")
	switch {
	case hasText && hasSize:
		return nil, errors.New("give either TEXT or --size, not both")
	case hasText:
		return []byte(args[1]), nil
	case hasSize:
		size, err := sizeFlag(fl)
		if err != nil {
			return nil, err
		}
		return fs.Synthetic(0, size), nil
	default:
		return nil, errors.New("give the content as TEXT or with --size")
	}
}

func sizeFlag(fl *pflag.FlagSet) (int64, error) {
	v, _ := fl.GetString("size")
	return config.ParseSize(v)
}

func buildTree(f *fs.FS, n fs.Node) (TreeNode, error) {
	t := TreeNode{Name: n.Name, Kind: n.Kind, Size: n.Size}
	if n.Kind != fs.KindDir {
		return t, nil
	}
	children, err := f.List(n.Path)
	if err != nil {
		return t, err
	}
	for _, c := range children {
		ct, err := buildTree(f, c)
		if err != nil {
			return t, err
		}
		t.Children = append(t.Children, ct)
	}
	return t, nil
}

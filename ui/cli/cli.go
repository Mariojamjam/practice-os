// Package cli defines the practice-os command line: the root command opens
// the terminal UI or runs commands given with -c, and subcommands offer an
// interactive shell, script files and the embedded demos. Global flags
// build the configuration.
package cli

import (
	"errors"
	"fmt"
	"io/fs"
	"os"
	"strings"

	"github.com/spf13/cobra"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/image"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/ui/render"
	"github.com/Mariojamjam/practice-os/ui/script"
	"github.com/Mariojamjam/practice-os/ui/shell"
	"github.com/Mariojamjam/practice-os/ui/tui"
)

// flags are the global flags; each one overrides the config only when set.
type flags struct {
	config, preset, image, blockSize, alloc, device, sched, animation string
	blocks, disks, head                                               int
	seed                                                              int64
	ascii                                                             bool
	commands                                                          string
}

// NewRootCmd returns the practice-os root command.
func NewRootCmd() *cobra.Command {
	f := &flags{}
	root := &cobra.Command{
		Use:   "practice-os [flags]",
		Short: "An educational operating-system simulator",
		Long: "practice-os simulates the main subsystems of an operating system:\n" +
			"file system, I/O and RAID, security, memory and processes.\n\n" +
			"Without arguments it opens the terminal UI; with -c it runs the given\n" +
			"commands and prints a transcript. Pick a reference setup with --preset\n" +
			"(" + strings.Join(config.Presets(), ", ") + ") and override any setting with the flags below.",
		Example: "  practice-os --preset stage2\n" +
			"  practice-os -c \"mkdir /docs; create /docs/a.txt --size 10KB; fs_status --details\"\n" +
			"  practice-os shell --image session.json\n" +
			"  practice-os run scenario.txt\n" +
			"  practice-os demo disk-scheduling",
		Args:          cobra.NoArgs,
		SilenceUsage:  true,
		SilenceErrors: false,
		RunE: func(cmd *cobra.Command, _ []string) error {
			if cmd.Flags().Changed("command") {
				cmds, err := shell.SplitCommands(f.commands)
				if err != nil {
					return err
				}
				return runCommands(cmd, f, cmds)
			}
			return session(cmd, f, func(k *kernel.Kernel) error {
				return tui.Run(k, tui.Options{ASCII: k.Config.UI.ASCII, Preset: k.Config.Preset, Animation: k.Config.UI.Animation})
			})
		},
	}
	root.Flags().StringVarP(&f.commands, "command", "c", "", `run commands separated by ';' and print a transcript, e.g. -c "mkdir /a; tree"`)

	pf := root.PersistentFlags()
	pf.StringVar(&f.config, "config", "", "config file (default: ./"+config.FileName+" if present)")
	pf.StringVar(&f.preset, "preset", "", "preset: "+strings.Join(config.Presets(), ", "))
	pf.StringVar(&f.image, "image", "", "state image: loaded at start if it exists, saved when the session ends")
	pf.StringVar(&f.blockSize, "block-size", "", "disk block size, e.g. 4KB")
	pf.IntVar(&f.blocks, "blocks", 0, "blocks per disk")
	pf.StringVar(&f.alloc, "alloc", "", "allocation strategy: contiguous, linked or indexed")
	pf.StringVar(&f.device, "device", "", "storage device: hdd, ssd or raid")
	pf.IntVar(&f.disks, "disks", 0, "number of disks in the RAID array")
	pf.StringVar(&f.sched, "sched", "", "disk-arm scheduler: fcfs, sstf, scan or cscan")
	pf.IntVar(&f.head, "head", 0, "initial head track")
	pf.Int64Var(&f.seed, "seed", 0, "random seed")
	pf.BoolVar(&f.ascii, "ascii", false, "draw with plain ASCII characters")
	pf.StringVar(&f.animation, "animation", "", "TUI animation speed: off, slow, normal or fast")

	root.AddCommand(newShellCmd(f), newRunCmd(f), newDemoCmd(f))
	return root
}

// ErrCommandsFailed is returned when some commands of a script failed.
var ErrCommandsFailed = errors.New("commands failed")

// runCommands runs commands in a session and prints their transcript.
func runCommands(cmd *cobra.Command, f *flags, cmds []string) error {
	return session(cmd, f, func(k *kernel.Kernel) error {
		failed, err := script.Run(shell.New(k), cmds, cmd.OutOrStdout(), render.Options{ASCII: k.Config.UI.ASCII})
		if err != nil {
			return err
		}
		if failed > 0 {
			return fmt.Errorf("%d of %d %w", failed, len(cmds), ErrCommandsFailed)
		}
		return nil
	})
}

// session builds the kernel (from --image when the file exists, otherwise
// from the configuration), runs fn, and saves the image afterwards when
// --image is set, even if fn failed.
func session(cmd *cobra.Command, f *flags, fn func(*kernel.Kernel) error) error {
	k, err := openKernel(cmd, f)
	if err != nil {
		return err
	}
	runErr := fn(k)
	if f.image != "" {
		if err := image.SaveFile(k, f.image); err != nil {
			return errors.Join(runErr, fmt.Errorf("saving %s: %w", f.image, err))
		}
		(&printer{w: cmd.ErrOrStderr()}).printf("State saved to %s\n", f.image)
	}
	return runErr
}

func openKernel(cmd *cobra.Command, f *flags) (*kernel.Kernel, error) {
	if f.image != "" {
		k, err := image.LoadFile(f.image)
		switch {
		case err == nil:
			(&printer{w: cmd.ErrOrStderr()}).printf("State loaded from %s (its saved settings are used)\n", f.image)
			return k, nil
		case !errors.Is(err, fs.ErrNotExist):
			return nil, fmt.Errorf("loading %s: %w", f.image, err)
		}
	}
	cfg, err := loadConfig(cmd, f)
	if err != nil {
		return nil, err
	}
	return kernel.New(cfg)
}

func loadConfig(cmd *cobra.Command, f *flags) (config.Config, error) {
	changed := cmd.Flags().Changed
	var o config.Overrides
	if changed("preset") {
		o.Preset = &f.preset
	}
	if changed("block-size") {
		size, err := config.ParseSize(f.blockSize)
		if err != nil {
			return config.Config{}, err
		}
		o.BlockSize = &size
	}
	if changed("blocks") {
		o.Blocks = &f.blocks
	}
	if changed("alloc") {
		o.Alloc = &f.alloc
	}
	if changed("device") {
		o.Device = &f.device
	}
	if changed("disks") {
		o.Disks = &f.disks
	}
	if changed("sched") {
		o.Scheduler = &f.sched
	}
	if changed("head") {
		o.Head = &f.head
	}
	if changed("seed") {
		o.Seed = &f.seed
	}
	if changed("ascii") {
		o.ASCII = &f.ascii
	}
	if changed("animation") {
		o.Animation = &f.animation
	}
	return config.Load(config.Options{Path: f.config, Overrides: o})
}

// isTerminal reports whether r is an interactive terminal.
func isTerminal(r any) bool {
	file, ok := r.(*os.File)
	if !ok {
		return false
	}
	info, err := file.Stat()
	return err == nil && info.Mode()&os.ModeCharDevice != 0
}

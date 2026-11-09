// Package cli defines the practice-os command line: the root command opens
// the terminal UI, and global flags build the configuration.
package cli

import (
	"github.com/spf13/cobra"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/ui/tui"
)

// flags are the global flags; each one overrides the config only when set.
type flags struct {
	config, preset, blockSize, alloc, device, sched string
	blocks, disks, head                             int
	seed                                            int64
	ascii                                           bool
}

// NewRootCmd returns the practice-os root command.
func NewRootCmd() *cobra.Command {
	var f flags
	cmd := &cobra.Command{
		Use:   "practice-os [flags]",
		Short: "An educational operating-system simulator",
		Long: "practice-os simulates the main subsystems of an operating system:\n" +
			"file system, I/O and RAID, security, memory and processes.\n\n" +
			"Without arguments it opens the terminal UI. Pick a reference setup with\n" +
			"--preset (" + joinPresets() + ") and override any setting with the flags below.",
		Args:         cobra.NoArgs,
		SilenceUsage: true,
		RunE: func(cmd *cobra.Command, _ []string) error {
			cfg, err := loadConfig(cmd, f)
			if err != nil {
				return err
			}
			k, err := kernel.New(cfg)
			if err != nil {
				return err
			}
			return tui.Run(k, tui.Options{ASCII: cfg.UI.ASCII, Preset: cfg.Preset})
		},
	}
	fl := cmd.Flags()
	fl.StringVar(&f.config, "config", "", "config file (default: ./"+config.FileName+" if present)")
	fl.StringVar(&f.preset, "preset", "", "preset: "+joinPresets())
	fl.StringVar(&f.blockSize, "block-size", "", "disk block size, e.g. 4KB")
	fl.IntVar(&f.blocks, "blocks", 0, "blocks per disk")
	fl.StringVar(&f.alloc, "alloc", "", "allocation strategy: contiguous, linked or indexed")
	fl.StringVar(&f.device, "device", "", "storage device: hdd, ssd or raid")
	fl.IntVar(&f.disks, "disks", 0, "number of disks in the RAID array")
	fl.StringVar(&f.sched, "sched", "", "disk-arm scheduler: fcfs, sstf, scan or cscan")
	fl.IntVar(&f.head, "head", 0, "initial head track")
	fl.Int64Var(&f.seed, "seed", 0, "random seed")
	fl.BoolVar(&f.ascii, "ascii", false, "draw with plain ASCII characters")
	return cmd
}

func loadConfig(cmd *cobra.Command, f flags) (config.Config, error) {
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
	return config.Load(config.Options{Path: f.config, Overrides: o})
}

func joinPresets() string {
	out := ""
	for i, p := range config.Presets() {
		if i > 0 {
			out += ", "
		}
		out += p
	}
	return out
}

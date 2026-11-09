// Package kernel wires the simulator's subsystems together from a
// configuration. Interfaces (shell, TUI) talk to the kernel, never to a
// half-assembled set of packages.
package kernel

import (
	"github.com/Mariojamjam/practice-os/internal/config"
	"github.com/Mariojamjam/practice-os/internal/disk"
	"github.com/Mariojamjam/practice-os/internal/fs"
)

// Kernel owns every simulated subsystem.
type Kernel struct {
	Config config.Config
	FS     *fs.FS
}

// New builds a kernel: a freshly formatted disk and file system.
func New(cfg config.Config) (*Kernel, error) {
	if err := cfg.Validate(); err != nil {
		return nil, err
	}
	d := disk.New(int(cfg.Disk.BlockSize), int64(cfg.Disk.Blocks))
	f, err := fs.New(d, cfg.FS.Alloc)
	if err != nil {
		return nil, err
	}
	return &Kernel{Config: cfg, FS: f}, nil
}

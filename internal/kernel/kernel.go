// Package kernel wires the simulator's subsystems together from a
// configuration. Interfaces (shell, TUI) talk to the kernel, never to a
// half-assembled set of packages.
package kernel

import (
	"fmt"

	"github.com/Mariojamjam/practice-os/internal/blockio"
	"github.com/Mariojamjam/practice-os/internal/config"
	"github.com/Mariojamjam/practice-os/internal/device"
	"github.com/Mariojamjam/practice-os/internal/device/hdd"
	"github.com/Mariojamjam/practice-os/internal/device/ssd"
	"github.com/Mariojamjam/practice-os/internal/disk"
	"github.com/Mariojamjam/practice-os/internal/fs"
	"github.com/Mariojamjam/practice-os/internal/raid"
	"github.com/Mariojamjam/practice-os/internal/sched"
)

// Kernel owns every simulated subsystem.
type Kernel struct {
	Config config.Config
	FS     *fs.FS
	// Device is the storage under the file system: an HDD, an SSD or a
	// RAID array of either.
	Device device.Device
	// Defer keeps I/O requests queued across commands until Flush.
	Defer bool
	// Trace asks interfaces to show each command's I/O.
	Trace bool
}

// New builds a kernel: the configured storage device, formatted with a
// fresh file system. The I/O of formatting is discarded; queues start
// empty.
func New(cfg config.Config) (*Kernel, error) {
	if err := cfg.Validate(); err != nil {
		return nil, err
	}
	dev, err := buildDevice(cfg)
	if err != nil {
		return nil, err
	}
	f, err := fs.New(dev, cfg.FS.Alloc)
	if err != nil {
		return nil, err
	}
	k := &Kernel{Config: cfg, FS: f, Device: dev, Defer: cfg.IO.Defer, Trace: cfg.IO.Trace}
	k.Discard()
	return k, nil
}

// Flush serves every queued I/O request and reports how.
func (k *Kernel) Flush() []blockio.Flush {
	if f, ok := k.Device.(blockio.Flusher); ok {
		return f.Flush()
	}
	return nil
}

// Pending reports the queued I/O requests without serving them.
func (k *Kernel) Pending() []blockio.Flush {
	if f, ok := k.Device.(blockio.Flusher); ok {
		return f.Pending()
	}
	return nil
}

// Discard drops queued I/O requests.
func (k *Kernel) Discard() {
	if f, ok := k.Device.(blockio.Flusher); ok {
		f.Discard()
	}
}

// Inspect runs fn with I/O recording muted, so interfaces can read the
// file system (to draw a tree or a block map) without queueing simulated
// requests, moving heads or raising RAID events. Data reads still work,
// including reconstruction from a failed RAID disk.
func (k *Kernel) Inspect(fn func() error) error {
	if m, ok := k.Device.(blockio.Muter); ok {
		m.SetMuted(true)
		defer m.SetMuted(false)
	}
	return fn()
}

// RAID returns the disk array, if the device is one.
func (k *Kernel) RAID() (*raid.RAID, bool) {
	r, ok := k.Device.(*raid.RAID)
	return r, ok
}

// SSDs returns the SSDs in use: the device itself, or the array's members.
func (k *Kernel) SSDs() []*ssd.SSD {
	var out []*ssd.SSD
	devs := []device.Device{k.Device}
	if r, ok := k.RAID(); ok {
		devs = r.Disks()
	}
	for _, d := range devs {
		if s, ok := d.(*ssd.SSD); ok {
			out = append(out, s)
		}
	}
	return out
}

func buildDevice(cfg config.Config) (device.Device, error) {
	switch cfg.IO.Device {
	case config.DeviceHDD:
		return buildDisk(cfg, config.DeviceHDD, "HDD")
	case config.DeviceSSD:
		return buildDisk(cfg, config.DeviceSSD, "SSD")
	case config.DeviceRAID:
		members := make([]device.Device, cfg.RAID.Disks)
		for i := range members {
			d, err := buildDisk(cfg, cfg.RAID.Member, fmt.Sprintf("Disk %d", i+1))
			if err != nil {
				return nil, err
			}
			members[i] = d
		}
		return raid.New(cfg.RAID.Level, members)
	}
	return nil, fmt.Errorf("%w: io.device %q", config.ErrInvalidConfig, cfg.IO.Device)
}

func buildDisk(cfg config.Config, kind, name string) (device.Device, error) {
	bs, blocks := int(cfg.Disk.BlockSize), int64(cfg.Disk.Blocks)
	if kind == config.DeviceSSD {
		return ssd.New(name, bs, blocks), nil
	}
	dir, err := sched.ParseDirection(cfg.IO.Direction)
	if err != nil {
		return nil, err
	}
	return hdd.New(disk.New(bs, blocks), hdd.Config{
		Name:           name,
		Tracks:         cfg.Disk.TrackCount(),
		BlocksPerTrack: cfg.Disk.BlocksPerTrack,
		Scheduler:      sched.Algorithm(cfg.IO.Scheduler),
		Head:           cfg.IO.Head,
		Direction:      dir,
	})
}

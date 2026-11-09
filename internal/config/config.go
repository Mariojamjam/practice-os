// Package config defines the simulator configuration and loads it from
// built-in defaults, an embedded preset, a YAML file and explicit overrides,
// in that order of precedence.
package config

import (
	"errors"
	"fmt"
	"slices"

	"go.yaml.in/yaml/v3"
)

// Allocation strategy names accepted in fs.alloc.
const (
	AllocContiguous = "contiguous"
	AllocLinked     = "linked"
	AllocIndexed    = "indexed"
)

// AllocStrategies lists the valid allocation strategy names.
var AllocStrategies = []string{AllocContiguous, AllocLinked, AllocIndexed}

// Storage device kinds accepted in io.device and raid.member.
const (
	DeviceHDD  = "hdd"
	DeviceSSD  = "ssd"
	DeviceRAID = "raid"
)

// Devices lists the valid io.device values.
var Devices = []string{DeviceHDD, DeviceSSD, DeviceRAID}

// RAIDMembers lists the valid raid.member values.
var RAIDMembers = []string{DeviceHDD, DeviceSSD}

// Schedulers lists the valid io.scheduler values.
var Schedulers = []string{"fcfs", "sstf", "scan", "cscan"}

// Directions lists the valid io.direction values.
var Directions = []string{"up", "down"}

// RAIDLevels lists the valid raid.level values.
var RAIDLevels = []int{0, 1, 4, 5}

// Limits enforced by Validate.
const (
	MinBlockSize = 512
	MaxBlockSize = 64 * 1024
	MinBlocks    = 4
	MaxBlocks    = 1 << 20
	MaxRAIDDisks = 16
)

// Config is the complete simulator configuration.
type Config struct {
	Preset string `yaml:"preset"`
	Seed   int64  `yaml:"seed"`
	Disk   Disk   `yaml:"disk"`
	FS     FS     `yaml:"fs"`
	IO     IO     `yaml:"io"`
	RAID   RAID   `yaml:"raid"`
	UI     UI     `yaml:"ui"`
}

// Disk configures each simulated physical disk.
type Disk struct {
	BlockSize Size `yaml:"block_size"`
	Blocks    int  `yaml:"blocks"`
	// Tracks is the number of tracks of an HDD; 0 derives it from
	// Blocks and BlocksPerTrack.
	Tracks         int `yaml:"tracks"`
	BlocksPerTrack int `yaml:"blocks_per_track"`
}

// TrackCount returns the number of tracks, deriving it when Tracks is 0.
func (d Disk) TrackCount() int {
	if d.Tracks > 0 {
		return d.Tracks
	}
	bpt := max(d.BlocksPerTrack, 1)
	return (d.Blocks + bpt - 1) / bpt
}

// IO configures the storage device and its request queue.
type IO struct {
	// Device is hdd, ssd or raid.
	Device string `yaml:"device"`
	// Scheduler is the HDD disk-arm algorithm: fcfs, sstf, scan or cscan.
	Scheduler string `yaml:"scheduler"`
	// Head is the initial track of the HDD head.
	Head int `yaml:"head"`
	// Direction is the initial head direction: up or down.
	Direction string `yaml:"direction"`
	// Defer keeps requests queued across commands until io_flush.
	Defer bool `yaml:"defer"`
	// Trace prints the I/O requests and their scheduling after each command.
	Trace bool `yaml:"trace"`
}

// RAID configures the disk array used when io.device is raid.
type RAID struct {
	Level int `yaml:"level"`
	Disks int `yaml:"disks"`
	// Member is the kind of each disk in the array: hdd or ssd.
	Member string `yaml:"member"`
}

// FS configures the file system.
type FS struct {
	Alloc string `yaml:"alloc"`
}

// UI configures presentation.
type UI struct {
	ASCII bool `yaml:"ascii"`
}

// Size is a byte count that YAML accepts either as a number or as a human
// size string such as "4KB".
type Size int64

// UnmarshalYAML implements yaml.Unmarshaler.
func (s *Size) UnmarshalYAML(value *yaml.Node) error {
	if value.Kind != yaml.ScalarNode {
		return fmt.Errorf("line %d: size must be a scalar", value.Line)
	}
	n, err := ParseSize(value.Value)
	if err != nil {
		return fmt.Errorf("line %d: %w", value.Line, err)
	}
	*s = Size(n)
	return nil
}

// MarshalYAML implements yaml.Marshaler.
func (s Size) MarshalYAML() (any, error) {
	return FormatSize(int64(s)), nil
}

// Default returns the built-in configuration.
func Default() Config {
	return Config{
		Seed: 42,
		Disk: Disk{BlockSize: Size(4 * KB), Blocks: 16, BlocksPerTrack: 1},
		FS:   FS{Alloc: AllocIndexed},
		IO:   IO{Device: DeviceHDD, Scheduler: "sstf", Direction: "up"},
		RAID: RAID{Level: 5, Disks: 3, Member: DeviceHDD},
	}
}

// ErrInvalidConfig wraps every validation failure.
var ErrInvalidConfig = errors.New("invalid configuration")

// Validate checks that the configuration is usable.
func (c Config) Validate() error {
	bs := int64(c.Disk.BlockSize)
	if bs < MinBlockSize || bs > MaxBlockSize || bs&(bs-1) != 0 {
		return fmt.Errorf("%w: disk.block_size must be a power of two between %s and %s, got %s",
			ErrInvalidConfig, FormatSize(MinBlockSize), FormatSize(MaxBlockSize), FormatSize(bs))
	}
	if c.Disk.Blocks < MinBlocks || c.Disk.Blocks > MaxBlocks {
		return fmt.Errorf("%w: disk.blocks must be between %d and %d, got %d",
			ErrInvalidConfig, MinBlocks, MaxBlocks, c.Disk.Blocks)
	}
	if !slices.Contains(AllocStrategies, c.FS.Alloc) {
		return fmt.Errorf("%w: fs.alloc must be one of %v, got %q", ErrInvalidConfig, AllocStrategies, c.FS.Alloc)
	}
	return c.validateIO()
}

func (c Config) validateIO() error {
	d := c.Disk
	switch {
	case d.BlocksPerTrack < 1:
		return fmt.Errorf("%w: disk.blocks_per_track must be at least 1, got %d", ErrInvalidConfig, d.BlocksPerTrack)
	case d.Tracks < 0:
		return fmt.Errorf("%w: disk.tracks must not be negative, got %d", ErrInvalidConfig, d.Tracks)
	case d.TrackCount()*d.BlocksPerTrack < d.Blocks:
		return fmt.Errorf("%w: %d tracks of %d blocks cannot hold %d blocks",
			ErrInvalidConfig, d.TrackCount(), d.BlocksPerTrack, d.Blocks)
	}
	io := c.IO
	switch {
	case !slices.Contains(Devices, io.Device):
		return fmt.Errorf("%w: io.device must be one of %v, got %q", ErrInvalidConfig, Devices, io.Device)
	case !slices.Contains(Schedulers, io.Scheduler):
		return fmt.Errorf("%w: io.scheduler must be one of %v, got %q", ErrInvalidConfig, Schedulers, io.Scheduler)
	case !slices.Contains(Directions, io.Direction):
		return fmt.Errorf("%w: io.direction must be one of %v, got %q", ErrInvalidConfig, Directions, io.Direction)
	case io.Head < 0 || io.Head >= d.TrackCount():
		return fmt.Errorf("%w: io.head must be a track between 0 and %d, got %d", ErrInvalidConfig, d.TrackCount()-1, io.Head)
	}
	r := c.RAID
	minDisks := 2
	if r.Level == 4 || r.Level == 5 {
		minDisks = 3
	}
	switch {
	case !slices.Contains(RAIDLevels, r.Level):
		return fmt.Errorf("%w: raid.level must be one of %v, got %d", ErrInvalidConfig, RAIDLevels, r.Level)
	case r.Disks < minDisks || r.Disks > MaxRAIDDisks:
		return fmt.Errorf("%w: RAID %d needs between %d and %d disks, got %d",
			ErrInvalidConfig, r.Level, minDisks, MaxRAIDDisks, r.Disks)
	case !slices.Contains(RAIDMembers, r.Member):
		return fmt.Errorf("%w: raid.member must be one of %v, got %q", ErrInvalidConfig, RAIDMembers, r.Member)
	}
	return nil
}

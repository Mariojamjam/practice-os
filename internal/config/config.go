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

// Limits enforced by Validate.
const (
	MinBlockSize = 512
	MaxBlockSize = 64 * 1024
	MinBlocks    = 4
	MaxBlocks    = 1 << 20
)

// Config is the complete simulator configuration.
type Config struct {
	Preset string `yaml:"preset"`
	Seed   int64  `yaml:"seed"`
	Disk   Disk   `yaml:"disk"`
	FS     FS     `yaml:"fs"`
	UI     UI     `yaml:"ui"`
}

// Disk configures the simulated physical disk.
type Disk struct {
	BlockSize Size `yaml:"block_size"`
	Blocks    int  `yaml:"blocks"`
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
		Disk: Disk{BlockSize: Size(4 * KB), Blocks: 16},
		FS:   FS{Alloc: AllocIndexed},
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
	return nil
}

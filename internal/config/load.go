package config

import (
	"bytes"
	"embed"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"go.yaml.in/yaml/v3"
)

// FileName is the config file looked up in the working directory when no
// explicit path is given.
const FileName = "practice-os.yaml"

//go:embed presets/*.yaml
var presetFS embed.FS

// Presets returns the names of the embedded presets, sorted.
func Presets() []string {
	entries, err := presetFS.ReadDir("presets")
	if err != nil {
		return nil
	}
	var names []string
	for _, e := range entries {
		names = append(names, strings.TrimSuffix(e.Name(), ".yaml"))
	}
	sort.Strings(names)
	return names
}

// Overrides holds values set explicitly (e.g. by CLI flags). Nil fields are
// left untouched.
type Overrides struct {
	Preset    *string
	Seed      *int64
	BlockSize *int64
	Blocks    *int
	Alloc     *string
	ASCII     *bool
}

// Options controls Load.
type Options struct {
	// Path is an explicit config file. If empty, Dir/practice-os.yaml is
	// used when it exists.
	Path string
	// Dir is where the default config file is looked up ("." if empty).
	Dir string
	// Overrides are applied last.
	Overrides Overrides
}

// Load builds the configuration with precedence:
// built-in defaults < preset < config file < overrides.
//
// The preset is taken from Overrides.Preset, else from the file's "preset"
// key. It is applied before the file, so the file can refine it.
func Load(opts Options) (Config, error) {
	file, err := readConfigFile(opts)
	if err != nil {
		return Config{}, err
	}

	cfg := Default()

	preset := ""
	if file != nil {
		var head struct {
			Preset string `yaml:"preset"`
		}
		// Lenient here: only the preset key matters; the strict pass comes later.
		if err := yaml.Unmarshal(file, &head); err != nil {
			return Config{}, fmt.Errorf("%w: %w", ErrInvalidConfig, err)
		}
		preset = head.Preset
	}
	if opts.Overrides.Preset != nil {
		preset = *opts.Overrides.Preset
	}
	if preset != "" {
		data, err := presetFS.ReadFile("presets/" + preset + ".yaml")
		if err != nil {
			return Config{}, fmt.Errorf("%w: unknown preset %q (available: %s)",
				ErrInvalidConfig, preset, strings.Join(Presets(), ", "))
		}
		if err := decodeStrict(data, &cfg); err != nil {
			return Config{}, fmt.Errorf("preset %s: %w", preset, err)
		}
	}

	if file != nil {
		if err := decodeStrict(file, &cfg); err != nil {
			return Config{}, err
		}
	}
	cfg.Preset = preset

	applyOverrides(&cfg, opts.Overrides)
	if err := cfg.Validate(); err != nil {
		return Config{}, err
	}
	return cfg, nil
}

func readConfigFile(opts Options) ([]byte, error) {
	path := opts.Path
	explicit := path != ""
	if !explicit {
		dir := opts.Dir
		if dir == "" {
			dir = "."
		}
		path = filepath.Join(dir, FileName)
	}
	data, err := os.ReadFile(path)
	switch {
	case err == nil:
		return data, nil
	case !explicit && errors.Is(err, os.ErrNotExist):
		return nil, nil
	default:
		return nil, fmt.Errorf("reading config: %w", err)
	}
}

// decodeStrict decodes YAML into v, rejecting unknown keys so typos surface.
func decodeStrict(data []byte, v any) error {
	dec := yaml.NewDecoder(bytes.NewReader(data))
	dec.KnownFields(true)
	if err := dec.Decode(v); err != nil && !errors.Is(err, io.EOF) {
		return fmt.Errorf("%w: %w", ErrInvalidConfig, err)
	}
	return nil
}

func applyOverrides(cfg *Config, o Overrides) {
	if o.Seed != nil {
		cfg.Seed = *o.Seed
	}
	if o.BlockSize != nil {
		cfg.Disk.BlockSize = Size(*o.BlockSize)
	}
	if o.Blocks != nil {
		cfg.Disk.Blocks = *o.Blocks
	}
	if o.Alloc != nil {
		cfg.FS.Alloc = *o.Alloc
	}
	if o.ASCII != nil {
		cfg.UI.ASCII = *o.ASCII
	}
}

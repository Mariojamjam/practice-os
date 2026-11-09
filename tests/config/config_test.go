package config_test

import (
	"errors"
	"github.com/Mariojamjam/practice-os/internal/config"
	"os"
	"path/filepath"
	"testing"
)

func TestParseSize(t *testing.T) {
	tests := []struct {
		in   string
		want int64
	}{
		{"0", 0},
		{"2048", 2048},
		{"512B", 512},
		{"10KB", 10240},
		{"10 KB", 10240},
		{"4kib", 4096},
		{"1MB", 1 << 20},
		{" 2 MiB ", 2 << 20},
	}
	for _, tt := range tests {
		got, err := config.ParseSize(tt.in)
		if err != nil || got != tt.want {
			t.Errorf("ParseSize(%q) = %d, %v; want %d", tt.in, got, err, tt.want)
		}
	}
	for _, bad := range []string{"", "KB", "10GB", "1.5KB", "-1", "10 K B", "99999999999999999999"} {
		if _, err := config.ParseSize(bad); !errors.Is(err, config.ErrInvalidSize) {
			t.Errorf("ParseSize(%q) error = %v, want config.ErrInvalidSize", bad, err)
		}
	}
}

func TestFormatSize(t *testing.T) {
	tests := []struct {
		in   int64
		want string
	}{
		{0, "0 B"},
		{512, "512 B"},
		{1500, "1500 B"},
		{4096, "4 KB"},
		{10240, "10 KB"},
		{65536, "64 KB"},
		{1 << 20, "1 MB"},
	}
	for _, tt := range tests {
		if got := config.FormatSize(tt.in); got != tt.want {
			t.Errorf("FormatSize(%d) = %q, want %q", tt.in, got, tt.want)
		}
	}
}

func writeFile(t *testing.T, dir, content string) string {
	t.Helper()
	p := filepath.Join(dir, config.FileName)
	if err := os.WriteFile(p, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	return p
}

func ptr[T any](v T) *T { return &v }

func TestLoadPrecedence(t *testing.T) {
	t.Run("defaults when nothing is given", func(t *testing.T) {
		cfg, err := config.Load(config.Options{Dir: t.TempDir()})
		if err != nil {
			t.Fatal(err)
		}
		if cfg.Disk.BlockSize != config.Size(4*config.KB) || cfg.Disk.Blocks != 16 || cfg.FS.Alloc != config.AllocIndexed || cfg.Preset != "" {
			t.Errorf("unexpected defaults: %+v", cfg)
		}
	})

	t.Run("preset over defaults", func(t *testing.T) {
		cfg, err := config.Load(config.Options{Dir: t.TempDir(), Overrides: config.Overrides{Preset: ptr("stage1")}})
		if err != nil {
			t.Fatal(err)
		}
		if cfg.Preset != "stage1" || cfg.Disk.Blocks != 16 {
			t.Errorf("unexpected config: %+v", cfg)
		}
	})

	t.Run("file over preset, file selects preset", func(t *testing.T) {
		dir := t.TempDir()
		writeFile(t, dir, "preset: stage1\ndisk:\n  blocks: 32\n")
		cfg, err := config.Load(config.Options{Dir: dir})
		if err != nil {
			t.Fatal(err)
		}
		if cfg.Preset != "stage1" || cfg.Disk.Blocks != 32 || cfg.Disk.BlockSize != config.Size(4*config.KB) {
			t.Errorf("unexpected config: %+v", cfg)
		}
	})

	t.Run("overrides over file", func(t *testing.T) {
		dir := t.TempDir()
		writeFile(t, dir, "disk:\n  block_size: 1KB\nfs:\n  alloc: linked\n")
		cfg, err := config.Load(config.Options{Dir: dir, Overrides: config.Overrides{Alloc: ptr(config.AllocContiguous), Blocks: ptr(8)}})
		if err != nil {
			t.Fatal(err)
		}
		if cfg.FS.Alloc != config.AllocContiguous || cfg.Disk.Blocks != 8 || cfg.Disk.BlockSize != config.Size(config.KB) {
			t.Errorf("unexpected config: %+v", cfg)
		}
	})

	t.Run("explicit path", func(t *testing.T) {
		p := writeFile(t, t.TempDir(), "disk:\n  blocks: 64\n")
		cfg, err := config.Load(config.Options{Path: p, Dir: t.TempDir()})
		if err != nil {
			t.Fatal(err)
		}
		if cfg.Disk.Blocks != 64 {
			t.Errorf("blocks = %d, want 64", cfg.Disk.Blocks)
		}
	})
}

func TestLoadErrors(t *testing.T) {
	tests := []struct {
		name string
		file string
		opts config.Overrides
	}{
		{"unknown preset", "", config.Overrides{Preset: ptr("nope")}},
		{"unknown key", "disk:\n  blokcs: 8\n", config.Overrides{}},
		{"bad size", "disk:\n  block_size: big\n", config.Overrides{}},
		{"block size not power of two", "disk:\n  block_size: 3000\n", config.Overrides{}},
		{"block size too small", "disk:\n  block_size: 256\n", config.Overrides{}},
		{"too few blocks", "disk:\n  blocks: 2\n", config.Overrides{}},
		{"bad strategy", "fs:\n  alloc: fat32\n", config.Overrides{}},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			dir := t.TempDir()
			if tt.file != "" {
				writeFile(t, dir, tt.file)
			}
			if _, err := config.Load(config.Options{Dir: dir, Overrides: tt.opts}); !errors.Is(err, config.ErrInvalidConfig) {
				t.Errorf("error = %v, want config.ErrInvalidConfig", err)
			}
		})
	}

	if _, err := config.Load(config.Options{Path: filepath.Join(t.TempDir(), "missing.yaml")}); err == nil {
		t.Error("missing explicit config file: want error")
	}
}

func TestPresets(t *testing.T) {
	names := config.Presets()
	if len(names) == 0 || names[0] != "stage1" {
		t.Fatalf("Presets() = %v", names)
	}
	for _, name := range names {
		if _, err := config.Load(config.Options{Dir: t.TempDir(), Overrides: config.Overrides{Preset: ptr(name)}}); err != nil {
			t.Errorf("preset %s: %v", name, err)
		}
	}
}

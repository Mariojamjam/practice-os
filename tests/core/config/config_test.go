package config_test

import (
	"errors"
	"github.com/Mariojamjam/practice-os/core/config"
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

func TestTrackCount(t *testing.T) {
	tests := []struct {
		disk config.Disk
		want int
	}{
		{config.Disk{Blocks: 16, BlocksPerTrack: 1}, 16},
		{config.Disk{Blocks: 17, BlocksPerTrack: 4}, 5},
		{config.Disk{Blocks: 16, Tracks: 200, BlocksPerTrack: 1}, 200},
	}
	for _, tt := range tests {
		if got := tt.disk.TrackCount(); got != tt.want {
			t.Errorf("%+v.TrackCount() = %d, want %d", tt.disk, got, tt.want)
		}
	}
}

func TestStage2Preset(t *testing.T) {
	cfg, err := config.Load(config.Options{Dir: t.TempDir(), Overrides: config.Overrides{Preset: ptr("stage2")}})
	if err != nil {
		t.Fatal(err)
	}
	want := config.IO{Device: config.DeviceRAID, Scheduler: "sstf", Head: 53, Direction: "up", Trace: true}
	if cfg.IO != want || cfg.RAID != (config.RAID{Level: 5, Disks: 3, Member: config.DeviceHDD}) {
		t.Errorf("io %+v, raid %+v", cfg.IO, cfg.RAID)
	}
	if cfg.Disk.TrackCount() != 200 || cfg.Disk.Blocks != 200 {
		t.Errorf("disk %+v", cfg.Disk)
	}
}

func TestIOOverrides(t *testing.T) {
	cfg, err := config.Load(config.Options{Dir: t.TempDir(), Overrides: config.Overrides{
		Device: ptr(config.DeviceSSD), Disks: ptr(4), Scheduler: ptr("cscan"), Head: ptr(7),
	}})
	if err != nil {
		t.Fatal(err)
	}
	if cfg.IO.Device != config.DeviceSSD || cfg.RAID.Disks != 4 || cfg.IO.Scheduler != "cscan" || cfg.IO.Head != 7 {
		t.Errorf("overrides not applied: %+v %+v", cfg.IO, cfg.RAID)
	}
}

func TestIOValidation(t *testing.T) {
	tests := []struct {
		name string
		file string
	}{
		{"zero blocks per track", "disk:\n  blocks_per_track: 0\n"},
		{"tracks too few", "disk:\n  blocks: 16\n  tracks: 3\n  blocks_per_track: 4\n"},
		{"unknown device", "io:\n  device: tape\n"},
		{"unknown scheduler", "io:\n  scheduler: look\n"},
		{"unknown direction", "io:\n  direction: left\n"},
		{"head outside the disk", "io:\n  head: 16\n"},
		{"unknown RAID level", "raid:\n  level: 3\n"},
		{"RAID 5 with two disks", "raid:\n  level: 5\n  disks: 2\n"},
		{"RAID 1 with one disk", "raid:\n  level: 1\n  disks: 1\n"},
		{"unknown RAID member", "raid:\n  member: tape\n"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			dir := t.TempDir()
			writeFile(t, dir, tt.file)
			if _, err := config.Load(config.Options{Dir: dir}); !errors.Is(err, config.ErrInvalidConfig) {
				t.Errorf("error = %v, want ErrInvalidConfig", err)
			}
		})
	}
	dir := t.TempDir()
	writeFile(t, dir, "raid:\n  level: 0\n  disks: 2\n  member: ssd\n")
	if _, err := config.Load(config.Options{Dir: dir}); err != nil {
		t.Errorf("RAID 0 of two SSDs: %v", err)
	}
}

package image_test

import (
	"bytes"
	"errors"
	"path/filepath"
	"reflect"
	"strings"
	"testing"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/fs/diag"
	"github.com/Mariojamjam/practice-os/core/image"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/core/storage/hdd"
)

func build(t *testing.T, edit func(*config.Config)) *kernel.Kernel {
	t.Helper()
	cfg := config.Default()
	edit(&cfg)
	k, err := kernel.New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	f := k.FS
	for _, step := range []error{
		f.Mkdir("/docs"),
		f.Create("/docs/a.txt", []byte("hello")),
		f.Create("/big", bytes.Repeat([]byte("x"), 9000)),
		f.Chdir("/docs"),
	} {
		if step != nil {
			t.Fatal(step)
		}
	}
	k.Flush()
	return k
}

func roundTrip(t *testing.T, k *kernel.Kernel) *kernel.Kernel {
	t.Helper()
	var buf bytes.Buffer
	if err := image.Save(k, &buf); err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(buf.String(), `"version": 1`) {
		t.Error("image has no version")
	}
	got, err := image.Load(&buf)
	if err != nil {
		t.Fatal(err)
	}
	return got
}

func report(t *testing.T, k *kernel.Kernel) diag.Report {
	t.Helper()
	var r diag.Report
	if err := k.Inspect(func() (err error) { r, err = diag.Analyze(k.FS); return err }); err != nil {
		t.Fatal(err)
	}
	return r
}

func TestRoundTrip(t *testing.T) {
	cases := map[string]func(*config.Config){
		"hdd":   func(c *config.Config) { c.IO.Head, c.Disk.Tracks = 3, 40 },
		"ssd":   func(c *config.Config) { c.IO.Device = config.DeviceSSD },
		"raid5": func(c *config.Config) { c.IO.Device = config.DeviceRAID },
		"raid1-ssds": func(c *config.Config) {
			c.IO.Device, c.RAID.Level, c.RAID.Member = config.DeviceRAID, 1, config.DeviceSSD
		},
		"linked":     func(c *config.Config) { c.FS.Alloc = config.AllocLinked },
		"contiguous": func(c *config.Config) { c.FS.Alloc = config.AllocContiguous },
	}
	for name, edit := range cases {
		t.Run(name, func(t *testing.T) {
			k := build(t, edit)
			k.Defer, k.Trace = true, true
			if _, err := k.FS.Read("/big"); err != nil { // leaves requests queued
				t.Fatal(err)
			}
			got := roundTrip(t, k)
			// Compare the queues before reading anything from the loaded copy.
			if !reflect.DeepEqual(got.Pending(), k.Pending()) {
				t.Error("queued requests differ after loading")
			}

			if got.FS.Getwd() != "/docs" || !got.Defer || !got.Trace || got.Config != k.Config {
				t.Errorf("cwd %q defer %v trace %v", got.FS.Getwd(), got.Defer, got.Trace)
			}
			if data, err := got.FS.Read("a.txt"); err != nil || string(data) != "hello" {
				t.Errorf("a.txt = %q, %v", data, err)
			}
			if !reflect.DeepEqual(report(t, got), report(t, k)) {
				t.Error("disk map differs after loading")
			}
			for i, s := range k.SSDs() {
				if !reflect.DeepEqual(got.SSDs()[i].Wear(), s.Wear()) {
					t.Errorf("SSD %d wear differs", i)
				}
			}
			if h, ok := k.Device.(*hdd.HDD); ok && got.Device.(*hdd.HDD).Head() != h.Head() {
				t.Error("head position differs")
			}
		})
	}
}

func TestFailedDiskSurvives(t *testing.T) {
	k := build(t, func(c *config.Config) { c.IO.Device = config.DeviceRAID })
	r, _ := k.RAID()
	if err := r.Fail(1); err != nil {
		t.Fatal(err)
	}
	got := roundTrip(t, k)
	gr, _ := got.RAID()
	if !gr.Failed(1) {
		t.Fatal("failed disk restored as healthy")
	}
	if data, err := got.FS.Read("/docs/a.txt"); err != nil || string(data) != "hello" {
		t.Errorf("degraded read after loading: %q, %v", data, err)
	}
	if _, err := gr.Rebuild(); err != nil {
		t.Error(err)
	}
}

func TestFiles(t *testing.T) {
	k := build(t, func(*config.Config) {})
	path := filepath.Join(t.TempDir(), "disk.img")
	if err := image.SaveFile(k, path); err != nil {
		t.Fatal(err)
	}
	got, err := image.LoadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := got.FS.Stat("/big"); err != nil {
		t.Error(err)
	}
	if _, err := image.LoadFile(filepath.Join(t.TempDir(), "missing.img")); err == nil {
		t.Error("missing file: want error")
	}
}

func TestInvalidImages(t *testing.T) {
	for name, doc := range map[string]string{
		"not json":       "hello",
		"wrong version":  `{"version": 99}`,
		"bad config":     `{"version": 1, "config": {"disk": {"block_size": 3}}}`,
		"device missing": `{"version": 1, "config": ` + defaultConfigJSON(t) + `, "device": {"kind": "ssd"}}`,
	} {
		if _, err := image.Load(strings.NewReader(doc)); !errors.Is(err, image.ErrInvalid) {
			t.Errorf("%s: error = %v", name, err)
		}
	}
}

func defaultConfigJSON(t *testing.T) string {
	t.Helper()
	var buf bytes.Buffer
	if err := image.Save(build(t, func(*config.Config) {}), &buf); err != nil {
		t.Fatal(err)
	}
	s := buf.String()
	start := strings.Index(s, `"config": `) + len(`"config": `)
	end := strings.Index(s, `,
 "defer"`)
	return s[start:end]
}

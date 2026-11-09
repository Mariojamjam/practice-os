package kernel_test

import (
	"testing"

	"github.com/Mariojamjam/practice-os/internal/blockio"
	"github.com/Mariojamjam/practice-os/internal/config"
	"github.com/Mariojamjam/practice-os/internal/device/hdd"
	"github.com/Mariojamjam/practice-os/internal/device/ssd"
	"github.com/Mariojamjam/practice-os/internal/kernel"
)

func newKernel(t *testing.T, edit func(*config.Config)) *kernel.Kernel {
	t.Helper()
	cfg := config.Default()
	edit(&cfg)
	k, err := kernel.New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	return k
}

func TestDevices(t *testing.T) {
	tests := []struct {
		name  string
		edit  func(*config.Config)
		kinds []string // device kinds expected in the flush after a mkdir
		ssds  int
	}{
		{"hdd", func(*config.Config) {}, []string{blockio.KindHDD}, 0},
		{"ssd", func(c *config.Config) { c.IO.Device = config.DeviceSSD }, []string{blockio.KindSSD}, 1},
		{"raid5 of hdds", func(c *config.Config) { c.IO.Device = config.DeviceRAID },
			[]string{blockio.KindHDD, blockio.KindHDD, blockio.KindHDD}, 0},
		{"raid1 of ssds", func(c *config.Config) {
			c.IO.Device, c.RAID.Level, c.RAID.Disks, c.RAID.Member = config.DeviceRAID, 1, 2, config.DeviceSSD
		}, []string{blockio.KindSSD, blockio.KindSSD}, 2},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := newKernel(t, tt.edit)
			if k.Pending() != nil {
				t.Error("formatting I/O was not discarded")
			}
			if err := k.FS.Mkdir("/d"); err != nil {
				t.Fatal(err)
			}
			flushes := k.Flush()
			var kinds []string
			for _, f := range flushes {
				if len(f.Requests) > 0 {
					kinds = append(kinds, f.Kind)
				}
			}
			if len(kinds) != len(tt.kinds) {
				t.Fatalf("flushes from %v, want %v", kinds, tt.kinds)
			}
			for i := range kinds {
				if kinds[i] != tt.kinds[i] {
					t.Errorf("flush %d from %s, want %s", i, kinds[i], tt.kinds[i])
				}
			}
			if got := len(k.SSDs()); got != tt.ssds {
				t.Errorf("SSDs() = %d, want %d", got, tt.ssds)
			}
			_, isRAID := k.RAID()
			if isRAID != (k.Config.IO.Device == config.DeviceRAID) {
				t.Error("RAID()")
			}
		})
	}
}

func TestHDDFromConfig(t *testing.T) {
	k := newKernel(t, func(c *config.Config) {
		c.Disk.Blocks, c.Disk.Tracks, c.Disk.BlocksPerTrack = 16, 8, 2
		c.IO.Scheduler, c.IO.Head, c.IO.Direction = "scan", 5, "down"
		c.IO.Defer, c.IO.Trace = true, true
	})
	h, ok := k.Device.(*hdd.HDD)
	if !ok {
		t.Fatalf("device is %T", k.Device)
	}
	if h.Tracks() != 8 || h.Track(15) != 7 || h.Head() != 5 || h.Scheduler() != "scan" || h.Direction().String() != "down" {
		t.Errorf("hdd: tracks %d head %d dir %v", h.Tracks(), h.Head(), h.Direction())
	}
	if !k.Defer || !k.Trace {
		t.Error("defer and trace come from the config")
	}
	if err := k.FS.Create("/f", []byte("x")); err != nil {
		t.Fatal(err)
	}
	if p := k.Pending(); len(p) != 1 || len(p[0].Requests) == 0 {
		t.Errorf("pending = %+v", p)
	}
	k.Discard()
	if k.Pending() != nil {
		t.Error("Discard left requests")
	}
}

func TestSSDCapacity(t *testing.T) {
	k := newKernel(t, func(c *config.Config) { c.IO.Device = config.DeviceSSD })
	s := k.SSDs()[0]
	if s.BlockCount() != 16 || s.Wear().Physical != 16+ssd.SpareFor(16) {
		t.Errorf("logical %d, physical %d", s.BlockCount(), s.Wear().Physical)
	}
}

func TestInspectIsSilent(t *testing.T) {
	for _, device := range config.Devices {
		t.Run(device, func(t *testing.T) {
			k := newKernel(t, func(c *config.Config) { c.IO.Device, c.IO.Defer = device, true })
			if err := k.FS.Create("/f", []byte("data")); err != nil {
				t.Fatal(err)
			}
			if r, ok := k.RAID(); ok {
				if err := r.Fail(0); err != nil {
					t.Fatal(err)
				}
			}
			before := count(k.Pending())
			err := k.Inspect(func() error {
				data, err := k.FS.Read("/f") // a degraded read on the RAID
				if err == nil && string(data) != "data" {
					t.Errorf("read %q", data)
				}
				return err
			})
			if err != nil {
				t.Fatal(err)
			}
			if after := count(k.Pending()); after != before {
				t.Errorf("Inspect queued work: %d -> %d", before, after)
			}
			if _, err := k.FS.Read("/f"); err != nil {
				t.Fatal(err)
			}
			if after := count(k.Pending()); after <= before {
				t.Error("recording did not resume after Inspect")
			}
		})
	}
}

// count totals pending requests and RAID events.
func count(flushes []blockio.Flush) int {
	n := 0
	for _, f := range flushes {
		n += len(f.Requests) + len(f.Events)
	}
	return n
}

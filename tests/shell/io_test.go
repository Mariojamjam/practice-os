package shell_test

import (
	"errors"
	"testing"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/core/storage/blockio"
	"github.com/Mariojamjam/practice-os/core/storage/sched"
	"github.com/Mariojamjam/practice-os/ui/shell"
)

func shellWith(t *testing.T, edit func(*config.Config)) *shell.Shell {
	t.Helper()
	cfg := config.Default()
	edit(&cfg)
	k, err := kernel.New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	return shell.New(k)
}

func exec(t *testing.T, s *shell.Shell, line string) shell.Result {
	t.Helper()
	r, err := s.Exec(line)
	if err != nil {
		t.Fatalf("Exec(%q): %v", line, err)
	}
	return r
}

func TestSchedCommand(t *testing.T) {
	s := shellWith(t, func(c *config.Config) { c.Disk.Tracks, c.IO.Head = 200, 53 })
	r := exec(t, s, "sched --queue 98,183,37,122,14").(shell.SchedResult)
	if r.Algorithm != sched.SSTF || r.Start != 53 || r.Total != 208 || r.Tracks != 200 {
		t.Errorf("sched = %+v", r)
	}
	r = exec(t, s, "sched --queue 98,183,37,122,14 --head 0 --alg fcfs").(shell.SchedResult)
	if r.Start != 0 || r.Total != 98+85+146+85+108 {
		t.Errorf("fcfs = %+v", r)
	}
	for _, line := range []string{"sched", "sched --queue 300", "sched --queue 1 --alg look", "sched --queue x"} {
		if _, err := s.Exec(line); err == nil {
			t.Errorf("Exec(%q): want error", line)
		}
	}
}

func TestTraceAndDefer(t *testing.T) {
	s := shellWith(t, func(*config.Config) {})
	exec(t, s, "mkdir /a")
	if s.LastIO() != nil {
		t.Error("trace off: no I/O expected")
	}
	exec(t, s, "io_trace on")
	exec(t, s, "mkdir /b")
	io := s.LastIO()
	if len(io) != 1 || io[0].Kind != blockio.KindHDD || len(io[0].Requests) == 0 || io[0].Sched == nil {
		t.Fatalf("trace = %+v", io)
	}

	exec(t, s, "io_defer on")
	exec(t, s, "mkdir /c")
	exec(t, s, "mkdir /d")
	if s.LastIO() != nil {
		t.Error("deferred requests must not be flushed")
	}
	q := exec(t, s, "io_queue").(shell.IOResult)
	if !q.Pending || len(q.Flushes) != 1 || q.Flushes[0].Sched != nil {
		t.Fatalf("io_queue = %+v", q)
	}
	queued := len(q.Flushes[0].Requests)
	f := exec(t, s, "io_flush").(shell.IOResult)
	if f.Pending || len(f.Flushes) != 1 || len(f.Flushes[0].Requests) != queued || f.Flushes[0].Sched == nil {
		t.Errorf("io_flush = %+v", f)
	}
	if q := exec(t, s, "io_queue").(shell.IOResult); len(q.Flushes) != 0 {
		t.Errorf("queue after flush = %+v", q)
	}
	if _, err := s.Exec("io_defer maybe"); !errors.Is(err, shell.ErrUsage) {
		t.Errorf("io_defer maybe: %v", err)
	}
}

func TestRAIDCommands(t *testing.T) {
	s := shellWith(t, func(c *config.Config) {
		c.IO.Device, c.Disk.Blocks, c.Disk.Tracks = config.DeviceRAID, 32, 32
	})
	exec(t, s, "mkdir /data")
	exec(t, s, "create /data/sheet.csv --size 8KB")

	st := exec(t, s, "raid_status /data/sheet.csv").(shell.RAIDStatusResult)
	if st.Name != "RAID 5" || len(st.Disks) != 3 || st.Disks[1].Name != "Disk 2" || st.Capacity != 64 || st.Path != "/data/sheet.csv" {
		t.Fatalf("raid_status = %+v", st)
	}
	if len(st.Stripes) == 0 || len(st.Stripes[0]) != 3 {
		t.Fatalf("stripes = %+v", st.Stripes)
	}
	all := exec(t, s, "raid_status").(shell.RAIDStatusResult)
	if len(all.Stripes) < len(st.Stripes) {
		t.Errorf("all stripes %d < file stripes %d", len(all.Stripes), len(st.Stripes))
	}

	if f := exec(t, s, "fail_disk 2").(shell.FailResult); f.Disk != 2 || f.Level != 5 {
		t.Errorf("fail_disk = %+v", f)
	}
	if st := exec(t, s, "raid_status").(shell.RAIDStatusResult); !st.Disks[1].Failed {
		t.Error("disk 2 not reported as failed")
	}
	data := exec(t, s, "read_file /data/sheet.csv").(shell.FileResult)
	if len(data.Data) != 8192 {
		t.Fatalf("degraded read returned %d bytes", len(data.Data))
	}
	events := s.LastIO() // trace is off, but RAID events always show
	if len(events) != 1 || events[0].Kind != blockio.KindRAID || len(events[0].Events) == 0 {
		t.Errorf("events = %+v", events)
	}

	rb := exec(t, s, "rebuild").(shell.RebuildResult)
	if len(rb.Rebuilt) != 1 || rb.Rebuilt[0].Disk != 2 || rb.Array != "RAID 5" {
		t.Errorf("rebuild = %+v", rb)
	}
	for _, line := range []string{"fail_disk 9", "fail_disk two", "rebuild", "ssd_wear"} {
		if _, err := s.Exec(line); err == nil {
			t.Errorf("Exec(%q): want error", line)
		}
	}
}

func TestSSDWear(t *testing.T) {
	s := shellWith(t, func(c *config.Config) { c.IO.Device = config.DeviceSSD })
	exec(t, s, "create /f --size 4KB")
	exec(t, s, `write_file /f "more"`)
	w := exec(t, s, "ssd_wear").(shell.WearResult)
	if len(w.Wear) != 1 || w.Wear[0].Name != "SSD" || w.Wear[0].Physical != 18 {
		t.Fatalf("wear = %+v", w)
	}
	erases := 0
	for _, e := range w.Wear[0].Erases {
		erases += e
	}
	if erases == 0 {
		t.Error("rewriting a file must erase stale pages")
	}
	if _, err := s.Exec("raid_status"); err == nil {
		t.Error("raid_status on an SSD: want error")
	}
}

func TestFlushed(t *testing.T) {
	s := shellWith(t, func(*config.Config) {})
	exec(t, s, "mkdir /a")
	if s.LastIO() != nil || len(s.Flushed()) != 1 || s.Flushed()[0].Sched == nil {
		t.Errorf("trace off: LastIO %v, Flushed %+v", s.LastIO(), s.Flushed())
	}
	exec(t, s, "io_defer on")
	exec(t, s, "mkdir /b")
	if s.Flushed() != nil {
		t.Error("deferred: nothing is flushed")
	}
	exec(t, s, "io_flush")
	if f := s.Flushed(); len(f) != 1 || len(f[0].Requests) == 0 {
		t.Errorf("io_flush: Flushed = %+v", f)
	}
}

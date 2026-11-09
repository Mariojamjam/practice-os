package raid_test

import (
	"bytes"
	"errors"
	"reflect"
	"testing"

	"github.com/Mariojamjam/practice-os/internal/blockio"
	"github.com/Mariojamjam/practice-os/internal/device"
	"github.com/Mariojamjam/practice-os/internal/device/hdd"
	"github.com/Mariojamjam/practice-os/internal/disk"
	"github.com/Mariojamjam/practice-os/internal/raid"
	"github.com/Mariojamjam/practice-os/internal/sched"
)

const blockSize = 64

func newArray(t *testing.T, level, n int, perDisk int64) (*raid.RAID, []*disk.Disk) {
	t.Helper()
	var disks []*disk.Disk
	var devs []device.Device
	for range n {
		d := disk.New(blockSize, perDisk)
		disks = append(disks, d)
		devs = append(devs, d)
	}
	r, err := raid.New(level, devs)
	if err != nil {
		t.Fatal(err)
	}
	return r, disks
}

// content returns the distinct test payload of logical block b.
func content(b int64, version byte) []byte {
	return bytes.Repeat([]byte{byte(b), version}, blockSize/2)
}

func fill(t *testing.T, r *raid.RAID, version byte) {
	t.Helper()
	for b := range r.BlockCount() {
		if err := r.Write(b, content(b, version)); err != nil {
			t.Fatalf("write %d: %v", b, err)
		}
	}
}

func verify(t *testing.T, r *raid.RAID, version byte) {
	t.Helper()
	for b := range r.BlockCount() {
		got, err := r.Read(b)
		if err != nil {
			t.Fatalf("read %d: %v", b, err)
		}
		if !bytes.Equal(got, content(b, version)) {
			t.Fatalf("block %d holds wrong data", b)
		}
	}
}

func raw(t *testing.T, d *disk.Disk, off int64) []byte {
	t.Helper()
	data, err := d.Read(off)
	if err != nil {
		t.Fatal(err)
	}
	return data
}

func TestNewValidation(t *testing.T) {
	two := []device.Device{disk.New(blockSize, 4), disk.New(blockSize, 4)}
	cases := []struct {
		level int
		disks []device.Device
	}{
		{3, two},
		{1, two[:1]},
		{0, []device.Device{disk.New(blockSize, 4), disk.New(blockSize, 5)}},
		{0, []device.Device{disk.New(blockSize, 4), disk.New(2*blockSize, 4)}},
	}
	for _, c := range cases {
		if _, err := raid.New(c.level, c.disks); !errors.Is(err, raid.ErrInvalid) {
			t.Errorf("level %d with %d disks: %v", c.level, len(c.disks), err)
		}
	}
}

func TestRAID0(t *testing.T) {
	r, disks := newArray(t, 0, 3, 4)
	if r.BlockCount() != 12 || r.Name() != "RAID 0" {
		t.Fatalf("capacity %d", r.BlockCount())
	}
	fill(t, r, 1)
	verify(t, r, 1)
	// Striping: block b lives on disk b mod 3, at offset b / 3.
	for b := range int64(12) {
		if !bytes.Equal(raw(t, disks[b%3], b/3), content(b, 1)) {
			t.Errorf("block %d is not on disk %d offset %d", b, b%3, b/3)
		}
	}
	if s := r.Stripe(1); s[2].Block != 5 || s[2].Parity || r.StripeOf(5) != 1 {
		t.Errorf("stripe 1 = %+v", s)
	}

	if err := r.Fail(1); err != nil {
		t.Fatal(err)
	}
	if _, err := r.Read(1); !errors.Is(err, raid.ErrDataLost) {
		t.Errorf("read from failed disk: %v", err)
	}
	if _, err := r.Read(0); err != nil {
		t.Errorf("other disks still readable: %v", err)
	}
	if _, err := r.Rebuild(); !errors.Is(err, raid.ErrDataLost) {
		t.Errorf("rebuild: %v", err)
	}
}

func TestRAID1(t *testing.T) {
	r, disks := newArray(t, 1, 3, 4)
	if r.BlockCount() != 4 {
		t.Fatalf("capacity %d", r.BlockCount())
	}
	fill(t, r, 1)
	for b := range int64(4) {
		for i, d := range disks {
			if !bytes.Equal(raw(t, d, b), content(b, 1)) {
				t.Errorf("disk %d does not mirror block %d", i, b)
			}
		}
	}

	if _, err := r.Rebuild(); !errors.Is(err, raid.ErrNotFailed) {
		t.Errorf("rebuild of a healthy array: %v", err)
	}
	if err := r.Fail(0); err != nil {
		t.Fatal(err)
	}
	if err := r.Fail(0); !errors.Is(err, raid.ErrInvalid) {
		t.Errorf("failing twice: %v", err)
	}
	if !r.Failed(0) || !bytes.Equal(raw(t, disks[0], 0), make([]byte, blockSize)) {
		t.Fatal("failed disk was not wiped")
	}
	verify(t, r, 1) // served by the mirrors
	fill(t, r, 2)   // degraded writes go to the survivors

	flushes := r.Flush()
	if len(flushes) == 0 || flushes[0].Kind != blockio.KindRAID {
		t.Fatalf("no RAID events: %+v", flushes)
	}
	ev := flushes[0].Events
	if want := (blockio.Event{Kind: blockio.DegradedRead, Block: 0, Disk: 1, Sources: []int{2}}); !reflect.DeepEqual(ev[0], want) {
		t.Errorf("first event = %+v", ev[0])
	}
	if last := ev[len(ev)-1]; last.Kind != blockio.DegradedWrite || last.Disk != 1 {
		t.Errorf("last event = %+v", last)
	}

	rebuilt, err := r.Rebuild()
	if err != nil || len(rebuilt) != 1 || rebuilt[0].Disk != 1 || rebuilt[0].Blocks != 4 || rebuilt[0].Sources[0] != 2 {
		t.Fatalf("rebuild = %+v, %v", rebuilt, err)
	}
	if r.Failed(0) || !bytes.Equal(raw(t, disks[0], 3), content(3, 2)) {
		t.Error("disk 1 not restored")
	}

	for i := range 3 {
		if err := r.Fail(i); err != nil {
			t.Fatal(err)
		}
	}
	if _, err := r.Read(0); !errors.Is(err, raid.ErrArrayFailed) {
		t.Errorf("all mirrors failed: %v", err)
	}
}

func TestMemberQueues(t *testing.T) {
	var devs []device.Device
	for i := range 2 {
		h, err := hdd.New(disk.New(blockSize, 10), hdd.Config{
			Name: []string{"Disk 1", "Disk 2"}[i], Tracks: 10, BlocksPerTrack: 1,
			Scheduler: sched.FCFS, Head: 0, Direction: sched.Up,
		})
		if err != nil {
			t.Fatal(err)
		}
		devs = append(devs, h)
	}
	r, err := raid.New(1, devs)
	if err != nil {
		t.Fatal(err)
	}
	if err := r.Write(5, []byte("x")); err != nil {
		t.Fatal(err)
	}
	if p := r.Pending(); len(p) != 2 || p[1].Device != "Disk 2" {
		t.Fatalf("pending = %+v", p)
	}
	flushes := r.Flush()
	if len(flushes) != 2 || flushes[0].Sched.Total != 5 || flushes[1].Sched.Total != 5 {
		t.Errorf("each disk moves its own head: %+v", flushes)
	}
	if err := r.Write(1, nil); err != nil {
		t.Fatal(err)
	}
	r.Discard()
	if r.Pending() != nil {
		t.Error("Discard left requests")
	}
}

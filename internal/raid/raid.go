// Package raid combines several block devices into one array (RAID) that
// is itself a block device, so the file system never knows it is there.
//
// Disks are numbered from 0 in the API and from 1 in user-facing events,
// as in "Disk 1".
package raid

import (
	"errors"
	"fmt"

	"github.com/Mariojamjam/practice-os/internal/blockio"
	"github.com/Mariojamjam/practice-os/internal/device"
)

var (
	// ErrInvalid reports a bad array configuration or argument.
	ErrInvalid = errors.New("invalid RAID operation")
	// ErrDataLost means data lived only on a failed disk (RAID 0).
	ErrDataLost = errors.New("data lost: the array has no redundancy for a failed disk")
	// ErrArrayFailed means more disks failed than the level tolerates.
	ErrArrayFailed = errors.New("array failed: too many failed disks")
	// ErrNotFailed means there is no failed disk to rebuild.
	ErrNotFailed = errors.New("no failed disk to rebuild")
)

// Slot is one disk's block in a stripe.
type Slot struct {
	// Disk is the 0-based disk index.
	Disk   int
	Offset int64
	// Block is the array's logical block stored here, or -1 for parity.
	Block  int64
	Parity bool
}

// Rebuilt describes a disk restored by Rebuild.
type Rebuilt struct {
	// Disk is the 1-based disk number.
	Disk   int
	Blocks int64
	// Sources are the 1-based disks the data came from.
	Sources []int
	// Parity is true when Sources were combined by XOR.
	Parity bool
}

// RAID is a disk array.
type RAID struct {
	level  int
	disks  []device.Device
	failed []bool
	events []blockio.Event
}

var (
	_ device.Device   = (*RAID)(nil)
	_ blockio.Flusher = (*RAID)(nil)
)

// MinDisks returns the minimum number of disks for a level.
func MinDisks(level int) int {
	if level == 4 || level == 5 {
		return 3
	}
	return 2
}

// New builds an array of the given level over disks of identical geometry.
func New(level int, disks []device.Device) (*RAID, error) {
	if !supported(level) {
		return nil, fmt.Errorf("%w: RAID level %d is not supported", ErrInvalid, level)
	}
	if len(disks) < MinDisks(level) {
		return nil, fmt.Errorf("%w: RAID %d needs at least %d disks, got %d", ErrInvalid, level, MinDisks(level), len(disks))
	}
	for _, d := range disks[1:] {
		if d.BlockSize() != disks[0].BlockSize() || d.BlockCount() != disks[0].BlockCount() {
			return nil, fmt.Errorf("%w: all disks must have the same geometry", ErrInvalid)
		}
	}
	return &RAID{level: level, disks: disks, failed: make([]bool, len(disks))}, nil
}

func supported(level int) bool { return level == 0 || level == 1 }

// Name returns the array's display name, e.g. "RAID 5".
func (r *RAID) Name() string { return fmt.Sprintf("RAID %d", r.level) }

// Level returns the RAID level.
func (r *RAID) Level() int { return r.level }

// Disks returns the member devices.
func (r *RAID) Disks() []device.Device { return r.disks }

// Failed reports whether disk i (0-based) has failed.
func (r *RAID) Failed(i int) bool { return r.failed[i] }

// BlockSize implements device.Device.
func (r *RAID) BlockSize() int { return r.disks[0].BlockSize() }

// BlockCount implements device.Device: the usable capacity.
func (r *RAID) BlockCount() int64 {
	per, n := r.perDisk(), int64(len(r.disks))
	if r.level == 0 {
		return per * n
	}
	return per
}

// Stripes returns the number of stripes (rows across the disks).
func (r *RAID) Stripes() int64 { return r.perDisk() }

// StripeOf returns the stripe holding logical block b.
func (r *RAID) StripeOf(b int64) int64 {
	if r.level == 0 {
		return b / int64(len(r.disks))
	}
	return b
}

// Stripe returns the slots of stripe s, one per disk, in disk order.
func (r *RAID) Stripe(s int64) []Slot {
	n := int64(len(r.disks))
	slots := make([]Slot, n)
	for i := range slots {
		block := s // RAID 1: every disk mirrors block s
		if r.level == 0 {
			block = s*n + int64(i)
		}
		slots[i] = Slot{Disk: i, Offset: s, Block: block}
	}
	return slots
}

// Read implements device.Device.
func (r *RAID) Read(b int64) ([]byte, error) {
	if err := r.check(b); err != nil {
		return nil, err
	}
	if r.level == 0 {
		d, off := r.locate0(b)
		if r.failed[d] {
			return nil, fmt.Errorf("block %d on Disk %d: %w", b, d+1, ErrDataLost)
		}
		return r.disks[d].Read(off)
	}
	src := r.firstHealthy()
	if src < 0 {
		return nil, ErrArrayFailed
	}
	if src > 0 {
		r.event(blockio.DegradedRead, b, 0, []int{src})
	}
	return r.disks[src].Read(b)
}

// Write implements device.Device.
func (r *RAID) Write(b int64, data []byte) error {
	if err := r.check(b); err != nil {
		return err
	}
	if r.level == 0 {
		d, off := r.locate0(b)
		if r.failed[d] {
			return fmt.Errorf("block %d on Disk %d: %w", b, d+1, ErrDataLost)
		}
		return r.disks[d].Write(off, data)
	}
	if r.firstHealthy() < 0 {
		return ErrArrayFailed
	}
	var healthy []int
	for i, d := range r.disks {
		if r.failed[i] {
			continue
		}
		healthy = append(healthy, i)
		if err := d.Write(b, data); err != nil {
			return err
		}
	}
	for i := range r.disks {
		if r.failed[i] {
			r.event(blockio.DegradedWrite, b, i, healthy)
			break
		}
	}
	return nil
}

// Fail simulates the failure of disk i (0-based): its contents are wiped,
// so anything read back afterwards must come from redundancy.
func (r *RAID) Fail(i int) error {
	if i < 0 || i >= len(r.disks) {
		return fmt.Errorf("%w: no Disk %d (the array has %d)", ErrInvalid, i+1, len(r.disks))
	}
	if r.failed[i] {
		return fmt.Errorf("%w: Disk %d has already failed", ErrInvalid, i+1)
	}
	d := r.disks[i]
	for off := range d.BlockCount() {
		if err := d.Write(off, nil); err != nil {
			return err
		}
	}
	if f, ok := d.(blockio.Flusher); ok {
		f.Discard() // a dead disk serves nothing
	}
	r.failed[i] = true
	return nil
}

// Rebuild replaces every failed disk with a blank one and restores its
// contents from redundancy.
func (r *RAID) Rebuild() ([]Rebuilt, error) {
	var out []Rebuilt
	for i := range r.disks {
		if !r.failed[i] {
			continue
		}
		if r.level == 0 {
			return nil, fmt.Errorf("rebuilding disk %d: %w", i+1, ErrDataLost)
		}
		src := r.firstHealthy()
		if src < 0 {
			return nil, ErrArrayFailed
		}
		for off := range r.perDisk() {
			data, err := r.disks[src].Read(off)
			if err != nil {
				return nil, err
			}
			if err := r.disks[i].Write(off, data); err != nil {
				return nil, err
			}
		}
		r.failed[i] = false
		out = append(out, Rebuilt{Disk: i + 1, Blocks: r.perDisk(), Sources: []int{src + 1}})
	}
	if len(out) == 0 {
		return nil, ErrNotFailed
	}
	return out, nil
}

// Flush serves every disk's queue. RAID events, if any, come first.
func (r *RAID) Flush() []blockio.Flush {
	var out []blockio.Flush
	if len(r.events) > 0 {
		out = append(out, blockio.Flush{Device: r.Name(), Kind: blockio.KindRAID, Events: r.events})
		r.events = nil
	}
	for _, d := range r.disks {
		if f, ok := d.(blockio.Flusher); ok {
			out = append(out, f.Flush()...)
		}
	}
	return out
}

// Pending reports queued requests on every disk, and pending RAID events.
func (r *RAID) Pending() []blockio.Flush {
	var out []blockio.Flush
	if len(r.events) > 0 {
		out = append(out, blockio.Flush{Device: r.Name(), Kind: blockio.KindRAID, Events: append([]blockio.Event(nil), r.events...)})
	}
	for _, d := range r.disks {
		if f, ok := d.(blockio.Flusher); ok {
			out = append(out, f.Pending()...)
		}
	}
	return out
}

// Discard drops every queued request and event.
func (r *RAID) Discard() {
	r.events = nil
	for _, d := range r.disks {
		if f, ok := d.(blockio.Flusher); ok {
			f.Discard()
		}
	}
}

func (r *RAID) perDisk() int64 { return r.disks[0].BlockCount() }

func (r *RAID) locate0(b int64) (int, int64) {
	n := int64(len(r.disks))
	return int(b % n), b / n
}

func (r *RAID) firstHealthy() int {
	for i, f := range r.failed {
		if !f {
			return i
		}
	}
	return -1
}

func (r *RAID) event(kind blockio.EventKind, b int64, disk int, sources []int) {
	e := blockio.Event{Kind: kind, Block: b, Disk: disk + 1}
	for _, s := range sources {
		e.Sources = append(e.Sources, s+1)
	}
	r.events = append(r.events, e)
}

func (r *RAID) check(b int64) error {
	if b < 0 || b >= r.BlockCount() {
		return fmt.Errorf("%w: block %d outside the array (%d blocks)", ErrInvalid, b, r.BlockCount())
	}
	return nil
}

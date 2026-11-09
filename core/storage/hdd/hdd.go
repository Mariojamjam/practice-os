// Package hdd simulates a hard disk drive: a disk whose blocks sit on
// tracks, with a single head that a scheduler moves between them.
package hdd

import (
	"errors"
	"fmt"
	"slices"

	"github.com/Mariojamjam/practice-os/core/storage/blockio"
	"github.com/Mariojamjam/practice-os/core/storage/device"
	"github.com/Mariojamjam/practice-os/core/storage/disk"
	"github.com/Mariojamjam/practice-os/core/storage/sched"
)

// ErrInvalid reports an unusable HDD configuration.
var ErrInvalid = errors.New("invalid HDD configuration")

// Config describes the drive's geometry and head.
type Config struct {
	// Name is the display name, e.g. "HDD" or "Disk 1".
	Name           string
	Tracks         int
	BlocksPerTrack int
	Scheduler      sched.Algorithm
	// Head and Direction are the head's initial state.
	Head      int
	Direction sched.Direction
}

// HDD is a block device with tracks and a scheduled head.
type HDD struct {
	d    *disk.Disk
	cfg  Config
	head int
	dir  sched.Direction
	q    blockio.Queue
}

var (
	_ device.Device   = (*HDD)(nil)
	_ blockio.Flusher = (*HDD)(nil)
	_ blockio.Muter   = (*HDD)(nil)
)

// New wraps d with the given geometry.
func New(d *disk.Disk, c Config) (*HDD, error) {
	switch {
	case c.BlocksPerTrack < 1 || c.Tracks < 1:
		return nil, fmt.Errorf("%w: %d tracks of %d blocks", ErrInvalid, c.Tracks, c.BlocksPerTrack)
	case int64(c.Tracks)*int64(c.BlocksPerTrack) < d.BlockCount():
		return nil, fmt.Errorf("%w: %d tracks of %d blocks cannot hold %d blocks",
			ErrInvalid, c.Tracks, c.BlocksPerTrack, d.BlockCount())
	case c.Head < 0 || c.Head >= c.Tracks:
		return nil, fmt.Errorf("%w: head at track %d of %d", ErrInvalid, c.Head, c.Tracks)
	case !slices.Contains(sched.Algorithms(), c.Scheduler):
		return nil, fmt.Errorf("%w: scheduler %q", ErrInvalid, c.Scheduler)
	case c.Direction != sched.Up && c.Direction != sched.Down:
		return nil, fmt.Errorf("%w: direction %d", ErrInvalid, c.Direction)
	}
	return &HDD{d: d, cfg: c, head: c.Head, dir: c.Direction}, nil
}

// Name returns the display name.
func (h *HDD) Name() string { return h.cfg.Name }

// Tracks returns the number of tracks.
func (h *HDD) Tracks() int { return h.cfg.Tracks }

// Scheduler returns the scheduling algorithm.
func (h *HDD) Scheduler() sched.Algorithm { return h.cfg.Scheduler }

// Head returns the head's current track.
func (h *HDD) Head() int { return h.head }

// Direction returns the head's current direction.
func (h *HDD) Direction() sched.Direction { return h.dir }

// Track returns the track holding block b.
func (h *HDD) Track(b int64) int64 { return b / int64(h.cfg.BlocksPerTrack) }

// BlockSize implements device.Device.
func (h *HDD) BlockSize() int { return h.d.BlockSize() }

// BlockCount implements device.Device.
func (h *HDD) BlockCount() int64 { return h.d.BlockCount() }

// Read implements device.Device and queues a read request.
func (h *HDD) Read(b int64) ([]byte, error) {
	data, err := h.d.Read(b)
	if err == nil {
		h.q.Add(blockio.Request{Op: blockio.Read, Block: b, Track: h.Track(b)})
	}
	return data, err
}

// Write implements device.Device and queues a write request.
func (h *HDD) Write(b int64, data []byte) error {
	err := h.d.Write(b, data)
	if err == nil {
		h.q.Add(blockio.Request{Op: blockio.Write, Block: b, Track: h.Track(b)})
	}
	return err
}

// Flush serves the queue with the configured scheduler and moves the head.
func (h *HDD) Flush() []blockio.Flush {
	reqs := h.q.Drain()
	if len(reqs) == 0 {
		return nil
	}
	tracks := make([]int, len(reqs))
	for i, r := range reqs {
		tracks[i] = int(r.Track)
	}
	res, err := sched.Schedule(h.cfg.Scheduler, h.head, h.dir, tracks, h.cfg.Tracks)
	if err != nil {
		panic(err) // unreachable: New validated the geometry and every track comes from Track
	}
	h.head, h.dir = res.End, res.EndDir
	return []blockio.Flush{{Device: h.cfg.Name, Kind: blockio.KindHDD, Requests: reqs, Sched: &res}}
}

// Pending reports the queued requests.
func (h *HDD) Pending() []blockio.Flush {
	if h.q.Len() == 0 {
		return nil
	}
	return []blockio.Flush{{Device: h.cfg.Name, Kind: blockio.KindHDD, Requests: h.q.Pending()}}
}

// Discard drops queued requests.
func (h *HDD) Discard() { h.q.Drain() }

// SetMuted implements blockio.Muter.
func (h *HDD) SetMuted(m bool) { h.q.SetMuted(m) }

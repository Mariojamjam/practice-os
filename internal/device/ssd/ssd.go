// Package ssd simulates a solid-state drive: flash pages that wear out as
// they are erased, managed by a flash translation layer (FTL) with wear
// leveling.
//
// Simplifications: one flash page holds one file-system block, the erase
// unit is a single page, and a page is erased as soon as it becomes stale.
package ssd

import (
	"fmt"

	"github.com/Mariojamjam/practice-os/internal/blockio"
	"github.com/Mariojamjam/practice-os/internal/device"
	"github.com/Mariojamjam/practice-os/internal/disk"
)

// Unmapped marks a logical block that was never written.
const Unmapped = -1

// SpareFor returns how many spare pages an SSD with logical blocks has:
// 12.5% over-provisioning, at least 2. Spare pages let every write go to a
// fresh page before the old one is erased.
func SpareFor(logical int64) int64 {
	return max(2, (logical+7)/8)
}

// SSD is a block device on flash memory. It has no head: requests are
// served in arrival order and cost no seek.
//
// Writes never overwrite a page in place. Each write goes to the free
// page with the fewest erases (wear leveling); the page that held the old
// version is then erased, which wears it a little more.
type SSD struct {
	name     string
	flash    *disk.Disk
	logical  int64
	ftl      []int64 // logical block -> physical page, or Unmapped
	owner    []int64 // physical page -> logical block, or Unmapped (free)
	erases   []int
	programs []int
	q        blockio.Queue
	erased   int // erases since the last flush
}

var (
	_ device.Device   = (*SSD)(nil)
	_ blockio.Flusher = (*SSD)(nil)
)

// New returns an empty SSD exposing logical blocks of blockSize bytes.
func New(name string, blockSize int, logical int64) *SSD {
	physical := logical + SpareFor(logical)
	s := &SSD{
		name:     name,
		flash:    disk.New(blockSize, physical),
		logical:  logical,
		ftl:      make([]int64, logical),
		owner:    make([]int64, physical),
		erases:   make([]int, physical),
		programs: make([]int, physical),
	}
	for i := range s.ftl {
		s.ftl[i] = Unmapped
	}
	for i := range s.owner {
		s.owner[i] = Unmapped
	}
	return s
}

// Name returns the display name.
func (s *SSD) Name() string { return s.name }

// BlockSize implements device.Device.
func (s *SSD) BlockSize() int { return s.flash.BlockSize() }

// BlockCount implements device.Device: the logical capacity.
func (s *SSD) BlockCount() int64 { return s.logical }

// Read implements device.Device. A never-written block reads as zeros.
func (s *SSD) Read(b int64) ([]byte, error) {
	if err := s.check(b); err != nil {
		return nil, err
	}
	p := s.ftl[b]
	s.q.Add(blockio.Request{Op: blockio.Read, Block: b, Track: p})
	if p == Unmapped {
		return make([]byte, s.BlockSize()), nil
	}
	return s.flash.Read(p)
}

// Write implements device.Device: the data goes to the least-worn free
// page, and the page holding the previous version is erased.
func (s *SSD) Write(b int64, data []byte) error {
	if err := s.check(b); err != nil {
		return err
	}
	p := s.leastWornFree()
	if err := s.flash.Write(p, data); err != nil {
		return err
	}
	s.programs[p]++
	old := s.ftl[b]
	s.ftl[b], s.owner[p] = p, b
	if old != Unmapped {
		s.owner[old] = Unmapped
		if err := s.flash.Write(old, nil); err != nil {
			return err
		}
		s.erases[old]++
		s.erased++
	}
	s.q.Add(blockio.Request{Op: blockio.Write, Block: b, Track: p})
	return nil
}

// Wear is a snapshot of the flash state.
type Wear struct {
	Name     string
	Logical  int64
	Physical int64
	// Erases and Programs count erase and write cycles per physical page.
	Erases   []int
	Programs []int
	// Mapping is the FTL: logical block -> physical page, or Unmapped.
	Mapping []int64
}

// Wear returns the current wear state.
func (s *SSD) Wear() Wear {
	return Wear{
		Name:     s.name,
		Logical:  s.logical,
		Physical: s.flash.BlockCount(),
		Erases:   append([]int(nil), s.erases...),
		Programs: append([]int(nil), s.programs...),
		Mapping:  append([]int64(nil), s.ftl...),
	}
}

// Flush serves queued requests in arrival order (no seek) and reports the
// pages erased since the last flush.
func (s *SSD) Flush() []blockio.Flush {
	reqs, erased := s.q.Drain(), s.erased
	s.erased = 0
	if len(reqs) == 0 && erased == 0 {
		return nil
	}
	return []blockio.Flush{{Device: s.name, Kind: blockio.KindSSD, Requests: reqs, Erases: erased}}
}

// Pending reports queued requests.
func (s *SSD) Pending() []blockio.Flush {
	if s.q.Len() == 0 {
		return nil
	}
	return []blockio.Flush{{Device: s.name, Kind: blockio.KindSSD, Requests: s.q.Pending(), Erases: s.erased}}
}

// Discard drops queued requests.
func (s *SSD) Discard() {
	s.q.Drain()
	s.erased = 0
}

func (s *SSD) leastWornFree() int64 {
	best := int64(Unmapped)
	for p, owner := range s.owner {
		if owner == Unmapped && (best == Unmapped || s.erases[p] < s.erases[best]) {
			best = int64(p)
		}
	}
	return best // spare pages guarantee a free page
}

func (s *SSD) check(b int64) error {
	if b < 0 || b >= s.logical {
		return fmt.Errorf("block %d: %w (SSD has %d blocks)", b, disk.ErrOutOfRange, s.logical)
	}
	return nil
}

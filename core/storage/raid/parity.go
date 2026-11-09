package raid

import (
	"fmt"

	"github.com/Mariojamjam/practice-os/core/storage/blockio"
)

// Parity layout. Each stripe s holds N-1 data blocks and one parity block,
// the XOR of the data blocks, so any single lost block equals the XOR of
// the other N-1.
//
//   - RAID 4 keeps parity on the last disk.
//   - RAID 5 rotates it: stripe s puts parity on disk N-1-(s mod N), so
//     stripe 0 uses the last disk, stripe 1 the one before, and so on.
//
// Data blocks fill the remaining disks in order: logical block b is data
// block b mod (N-1) of stripe b / (N-1).

func (r *RAID) parityLevel() bool { return r.level == 4 || r.level == 5 }

func (r *RAID) parityDisk(s int64) int {
	n := len(r.disks)
	if r.level == 4 {
		return n - 1
	}
	return n - 1 - int(s%int64(n))
}

// dataDisks returns the disks holding data in stripe s, in order.
func (r *RAID) dataDisks(s int64) []int {
	p := r.parityDisk(s)
	out := make([]int, 0, len(r.disks)-1)
	for i := range r.disks {
		if i != p {
			out = append(out, i)
		}
	}
	return out
}

func (r *RAID) parityStripe(s int64) []Slot {
	slots := make([]Slot, len(r.disks))
	p := r.parityDisk(s)
	slots[p] = Slot{Disk: p, Offset: s, Block: -1, Parity: true}
	for k, d := range r.dataDisks(s) {
		slots[d] = Slot{Disk: d, Offset: s, Block: s*int64(len(r.disks)-1) + int64(k)}
	}
	return slots
}

func (r *RAID) locateParity(b int64) (disk int, stripe int64) {
	k := int64(len(r.disks) - 1)
	s := b / k
	return r.dataDisks(s)[b%k], s
}

func (r *RAID) failedCount() int {
	n := 0
	for _, f := range r.failed {
		if f {
			n++
		}
	}
	return n
}

// readParity reads block b; if its disk failed, it rebuilds the block as
// the XOR of the other disks in the stripe.
func (r *RAID) readParity(b int64) ([]byte, error) {
	d, s := r.locateParity(b)
	if !r.failed[d] {
		return r.disks[d].Read(s)
	}
	if r.failedCount() > 1 {
		return nil, ErrArrayFailed
	}
	data, sources, err := r.xorOthers(s, d)
	if err != nil {
		return nil, err
	}
	r.parityEvent(blockio.DegradedRead, b, d, sources)
	return data, nil
}

// writeParity writes block b and keeps the stripe's parity consistent.
//
// With every disk healthy it is a read-modify-write (the small-write
// penalty): read the old data and old parity, then write the new data and
// parity = old parity XOR old data XOR new data. If the data disk failed,
// only the parity is updated, from the other data blocks; if the parity
// disk failed, only the data is written.
func (r *RAID) writeParity(b int64, data []byte) error {
	if r.failedCount() > 1 {
		return ErrArrayFailed
	}
	buf := make([]byte, r.BlockSize())
	if len(data) > len(buf) {
		return fmt.Errorf("%w: %d bytes do not fit in a %d-byte block", ErrInvalid, len(data), len(buf))
	}
	copy(buf, data)
	d, s := r.locateParity(b)
	p := r.parityDisk(s)

	switch {
	case r.failed[p]:
		return r.disks[d].Write(s, buf)
	case r.failed[d]:
		parity := buf
		var sources []int
		for _, o := range r.dataDisks(s) {
			if o == d {
				continue
			}
			other, err := r.disks[o].Read(s)
			if err != nil {
				return err
			}
			xorInto(parity, other)
			sources = append(sources, o)
		}
		if err := r.disks[p].Write(s, parity); err != nil {
			return err
		}
		r.parityEvent(blockio.DegradedWrite, b, d, append(sources, p))
		return nil
	}

	oldData, err := r.disks[d].Read(s)
	if err != nil {
		return err
	}
	parity, err := r.disks[p].Read(s)
	if err != nil {
		return err
	}
	xorInto(parity, oldData)
	xorInto(parity, buf)
	if err := r.disks[d].Write(s, buf); err != nil {
		return err
	}
	return r.disks[p].Write(s, parity)
}

// rebuildParity restores failed disk i stripe by stripe from the XOR of
// the other disks.
func (r *RAID) rebuildParity(i int) (Rebuilt, error) {
	if r.failedCount() > 1 {
		return Rebuilt{}, ErrArrayFailed
	}
	var sources []int
	for s := range r.perDisk() {
		data, src, err := r.xorOthers(s, i)
		if err != nil {
			return Rebuilt{}, err
		}
		if err := r.disks[i].Write(s, data); err != nil {
			return Rebuilt{}, err
		}
		sources = src
	}
	r.failed[i] = false
	rb := Rebuilt{Disk: i + 1, Blocks: r.perDisk(), Parity: true}
	for _, src := range sources {
		rb.Sources = append(rb.Sources, src+1)
	}
	return rb, nil
}

// xorOthers returns the XOR of block s on every disk except skip, and the
// disks it read.
func (r *RAID) xorOthers(s int64, skip int) ([]byte, []int, error) {
	out := make([]byte, r.BlockSize())
	var sources []int
	for o, dev := range r.disks {
		if o == skip {
			continue
		}
		data, err := dev.Read(s)
		if err != nil {
			return nil, nil, err
		}
		xorInto(out, data)
		sources = append(sources, o)
	}
	return out, sources, nil
}

func (r *RAID) parityEvent(kind blockio.EventKind, b int64, disk int, sources []int) {
	if r.muted {
		return
	}
	r.event(kind, b, disk, sources)
	r.events[len(r.events)-1].Parity = true
}

func xorInto(dst, src []byte) {
	for i := range dst {
		dst[i] ^= src[i]
	}
}

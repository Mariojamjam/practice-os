// Package blockio models I/O requests between the file system and storage
// devices.
//
// Devices perform every read and write immediately, so data is always
// correct, and also record each one as a Request in a queue. Flushing the
// queue simulates how the device serves those requests: for an HDD, the
// order chosen by the disk-arm scheduler and how far the head moves.
package blockio

import "github.com/Mariojamjam/practice-os/core/storage/sched"

// Op is a request type.
type Op byte

// Request types.
const (
	Read  Op = 'R'
	Write Op = 'W'
)

func (o Op) String() string { return string(o) }

// Request is one block I/O issued to a device.
type Request struct {
	Op    Op
	Block int64
	// Track is where the request lands: the HDD track, or the SSD physical
	// page it was mapped to.
	Track int64
}

// Queue holds requests in arrival order.
type Queue struct {
	reqs  []Request
	muted bool
}

// Add appends a request, unless the queue is muted.
func (q *Queue) Add(r Request) {
	if !q.muted {
		q.reqs = append(q.reqs, r)
	}
}

// SetMuted stops (true) or resumes (false) recording requests.
func (q *Queue) SetMuted(m bool) { q.muted = m }

// Len returns the number of pending requests.
func (q *Queue) Len() int { return len(q.reqs) }

// Pending returns a copy of the pending requests.
func (q *Queue) Pending() []Request { return append([]Request(nil), q.reqs...) }

// Set replaces the pending requests, for restoring a saved queue.
func (q *Queue) Set(reqs []Request) { q.reqs = append([]Request(nil), reqs...) }

// Drain removes and returns every pending request.
func (q *Queue) Drain() []Request {
	r := q.reqs
	q.reqs = nil
	return r
}

// Device kinds reported in a Flush.
const (
	KindHDD  = "hdd"
	KindSSD  = "ssd"
	KindRAID = "raid"
)

// EventKind classifies RAID events.
type EventKind string

// RAID events.
const (
	// DegradedRead: a block on a failed disk was read from redundancy
	// (rebuilt by XOR, or read from a mirror).
	DegradedRead EventKind = "degraded-read"
	// DegradedWrite: a block on a failed disk was written by updating the
	// redundancy only (parity, or the surviving mirrors).
	DegradedWrite EventKind = "degraded-write"
)

// Event is something notable a RAID array did while serving requests.
type Event struct {
	Kind EventKind
	// Block is the array's logical block.
	Block int64
	// Disk is the failed disk (1-based).
	Disk int
	// Sources are the disks (1-based) used instead of it.
	Sources []int
	// Parity is true when Sources were combined by XOR with parity.
	Parity bool
}

// Flush reports how one device served (or still holds) its requests.
type Flush struct {
	// Device is the device's display name, e.g. "HDD" or "Disk 2".
	Device string
	// Kind is KindHDD, KindSSD or KindRAID.
	Kind     string
	Requests []Request
	// Sched is the HDD schedule; nil when nothing was scheduled.
	Sched *sched.Result
	// Erases is the number of flash pages an SSD erased.
	Erases int
	// Events are RAID events, for KindRAID.
	Events []Event
}

// Muter is implemented by devices that can stop recording requests and
// events, so their contents can be inspected without leaving simulated I/O
// behind.
type Muter interface {
	SetMuted(bool)
}

// Flusher is implemented by devices that queue requests.
type Flusher interface {
	// Flush serves every pending request and reports how.
	Flush() []Flush
	// Pending reports the requests waiting to be served.
	Pending() []Flush
	// Discard drops pending requests without serving them.
	Discard()
}

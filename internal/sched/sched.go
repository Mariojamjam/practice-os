// Package sched implements disk-arm scheduling algorithms as pure
// functions: given pending track requests and the head position, it
// returns the order in which the head visits them and how far it moves.
package sched

import (
	"errors"
	"fmt"
	"sort"
)

// Algorithm is a disk-arm scheduling algorithm.
type Algorithm string

// Algorithms.
const (
	FCFS  Algorithm = "fcfs"
	SSTF  Algorithm = "sstf"
	SCAN  Algorithm = "scan"
	CSCAN Algorithm = "cscan"
)

// Algorithms lists every algorithm.
func Algorithms() []Algorithm { return []Algorithm{FCFS, SSTF, SCAN, CSCAN} }

// Title returns the algorithm's display name.
func (a Algorithm) Title() string {
	switch a {
	case FCFS:
		return "FCFS (First-Come, First-Served)"
	case SSTF:
		return "SSTF (Shortest Seek Time First)"
	case SCAN:
		return "SCAN (Elevator)"
	case CSCAN:
		return "C-SCAN (Circular SCAN)"
	}
	return string(a)
}

// Direction is the direction the head moves in.
type Direction int

// Directions: Up moves towards higher tracks.
const (
	Up   Direction = 1
	Down Direction = -1
)

func (d Direction) String() string {
	if d == Down {
		return "down"
	}
	return "up"
}

// ParseDirection parses "up" or "down".
func ParseDirection(s string) (Direction, error) {
	switch s {
	case "up":
		return Up, nil
	case "down":
		return Down, nil
	}
	return Up, fmt.Errorf("%w: direction %q (want up or down)", ErrInvalid, s)
}

// StopKind tells why the head stopped at a track.
type StopKind int

// Stop kinds.
const (
	// Serve is a pending request being served.
	Serve StopKind = iota
	// Edge is the head reaching the first or last track before turning
	// (SCAN) or wrapping around (C-SCAN).
	Edge
	// Jump is C-SCAN's return to the opposite edge, serving nothing.
	Jump
)

// Stop is one point on the head's path.
type Stop struct {
	Track int
	Kind  StopKind
	// Move is the distance travelled from the previous point.
	Move int
}

// Result is a computed schedule.
type Result struct {
	Algorithm Algorithm
	// Start is the head's track before serving.
	Start int
	// Requests are the pending tracks in arrival order.
	Requests []int
	// Stops is the head's path after Start.
	Stops []Stop
	// Total is the total head movement, in tracks.
	Total int
	// End and EndDir are the head's track and direction afterwards.
	End    int
	EndDir Direction
}

var (
	// ErrInvalid reports bad input.
	ErrInvalid = errors.New("invalid scheduling input")
)

// Schedule orders requests (tracks, in arrival order) for a disk with
// tracks tracks, starting at head and moving in dir.
//
// SCAN and C-SCAN follow the textbook: the head travels to the edge of the
// disk before turning (SCAN) or jumping to the opposite edge (C-SCAN), but
// only when requests remain on the other side. C-SCAN's jump counts as
// head movement.
func Schedule(alg Algorithm, head int, dir Direction, requests []int, tracks int) (Result, error) {
	if head < 0 || head >= tracks {
		return Result{}, fmt.Errorf("%w: head %d outside tracks 0..%d", ErrInvalid, head, tracks-1)
	}
	for _, t := range requests {
		if t < 0 || t >= tracks {
			return Result{}, fmt.Errorf("%w: track %d outside 0..%d", ErrInvalid, t, tracks-1)
		}
	}
	if dir != Up && dir != Down {
		return Result{}, fmt.Errorf("%w: direction %d", ErrInvalid, dir)
	}

	p := path{pos: head, dir: dir}
	switch alg {
	case FCFS:
		for _, t := range requests {
			p.visit(t, Serve)
		}
	case SSTF:
		sstf(&p, requests)
	case SCAN:
		scan(&p, requests, tracks, false)
	case CSCAN:
		scan(&p, requests, tracks, true)
	default:
		return Result{}, fmt.Errorf("%w: unknown algorithm %q", ErrInvalid, alg)
	}
	return Result{
		Algorithm: alg,
		Start:     head,
		Requests:  append([]int(nil), requests...),
		Stops:     p.stops,
		Total:     p.total,
		End:       p.pos,
		EndDir:    p.dir,
	}, nil
}

type path struct {
	pos   int
	dir   Direction
	stops []Stop
	total int
}

func (p *path) visit(t int, kind StopKind) {
	move := t - p.pos
	switch {
	case kind == Jump:
		// C-SCAN keeps its sweep direction across the jump.
	case move > 0:
		p.dir = Up
	case move < 0:
		p.dir = Down
	}
	if move < 0 {
		move = -move
	}
	p.stops = append(p.stops, Stop{Track: t, Kind: kind, Move: move})
	p.total += move
	p.pos = t
}

func sstf(p *path, requests []int) {
	pending := append([]int(nil), requests...)
	for len(pending) > 0 {
		best := 0
		for i, t := range pending {
			d, bd := abs(t-p.pos), abs(pending[best]-p.pos)
			if d < bd || (d == bd && t < pending[best]) {
				best = i
			}
		}
		p.visit(pending[best], Serve)
		pending = append(pending[:best], pending[best+1:]...)
	}
}

func scan(p *path, requests []int, tracks int, circular bool) {
	var ahead, behind []int // relative to the starting direction
	for _, t := range requests {
		if (p.dir == Up && t >= p.pos) || (p.dir == Down && t <= p.pos) {
			ahead = append(ahead, t)
		} else {
			behind = append(behind, t)
		}
	}
	dir := p.dir
	sortDir(ahead, dir)
	for _, t := range ahead {
		p.visit(t, Serve)
	}
	if len(behind) == 0 {
		p.dir = dir
		return
	}
	edge, opposite := tracks-1, 0
	if dir == Down {
		edge, opposite = 0, tracks-1
	}
	p.visit(edge, Edge)
	if circular {
		p.visit(opposite, Jump)
		p.dir = dir
		sortDir(behind, dir)
	} else {
		sortDir(behind, -dir)
	}
	for _, t := range behind {
		p.visit(t, Serve)
	}
	if circular {
		p.dir = dir
	} else {
		p.dir = -dir
	}
}

func sortDir(ts []int, dir Direction) {
	sort.Slice(ts, func(i, j int) bool {
		if dir == Up {
			return ts[i] < ts[j]
		}
		return ts[i] > ts[j]
	})
}

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

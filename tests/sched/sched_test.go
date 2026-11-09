package sched_test

import (
	"errors"
	"reflect"
	"testing"

	"github.com/Mariojamjam/practice-os/internal/sched"
)

func tracksOf(r sched.Result) []int {
	var out []int
	for _, s := range r.Stops {
		out = append(out, s.Track)
	}
	return out
}

func schedule(t *testing.T, alg sched.Algorithm, head int, dir sched.Direction, reqs []int) sched.Result {
	t.Helper()
	r, err := sched.Schedule(alg, head, dir, reqs, 200)
	if err != nil {
		t.Fatal(err)
	}
	return r
}

// Reference Example 2.1.
func TestExample21SSTF(t *testing.T) {
	r := schedule(t, sched.SSTF, 53, sched.Up, []int{98, 183, 37, 122, 14})
	if got, want := tracksOf(r), []int{37, 14, 98, 122, 183}; !reflect.DeepEqual(got, want) {
		t.Errorf("order = %v, want %v", got, want)
	}
	var moves []int
	for _, s := range r.Stops {
		moves = append(moves, s.Move)
	}
	if want := []int{16, 23, 84, 24, 61}; !reflect.DeepEqual(moves, want) {
		t.Errorf("moves = %v, want %v", moves, want)
	}
	if r.Total != 208 || r.End != 183 || r.EndDir != sched.Up {
		t.Errorf("total %d, end %d %v", r.Total, r.End, r.EndDir)
	}
}

// The textbook queue (Silberschatz): 98, 183, 37, 122, 14, 124, 65, 67
// with the head at 53 on a 200-track disk.
func TestTextbookQueue(t *testing.T) {
	queue := []int{98, 183, 37, 122, 14, 124, 65, 67}
	tests := []struct {
		alg   sched.Algorithm
		dir   sched.Direction
		order []int
		total int
		end   sched.Direction
	}{
		{sched.FCFS, sched.Up, []int{98, 183, 37, 122, 14, 124, 65, 67}, 640, sched.Up},
		{sched.SSTF, sched.Up, []int{65, 67, 37, 14, 98, 122, 124, 183}, 236, sched.Up},
		// Towards 0: 53 -> 0 is 53, then 0 -> 183 is 183.
		{sched.SCAN, sched.Down, []int{37, 14, 0, 65, 67, 98, 122, 124, 183}, 236, sched.Up},
		// Towards 199: 146 up, 162 back down to 37.
		{sched.SCAN, sched.Up, []int{65, 67, 98, 122, 124, 183, 199, 37, 14}, 331, sched.Down},
		// Up to 199 (146), jump to 0 (199), then up to 37 (37).
		{sched.CSCAN, sched.Up, []int{65, 67, 98, 122, 124, 183, 199, 0, 14, 37}, 382, sched.Up},
		{sched.CSCAN, sched.Down, []int{37, 14, 0, 199, 183, 124, 122, 98, 67, 65}, 386, sched.Down},
	}
	for _, tt := range tests {
		t.Run(string(tt.alg)+"-"+tt.dir.String(), func(t *testing.T) {
			r := schedule(t, tt.alg, 53, tt.dir, queue)
			if got := tracksOf(r); !reflect.DeepEqual(got, tt.order) {
				t.Errorf("order = %v, want %v", got, tt.order)
			}
			if r.Total != tt.total || r.EndDir != tt.end {
				t.Errorf("total %d dir %v, want %d %v", r.Total, r.EndDir, tt.total, tt.end)
			}
		})
	}
}

func TestStopKinds(t *testing.T) {
	r := schedule(t, sched.CSCAN, 50, sched.Up, []int{60, 10})
	want := []sched.Stop{
		{Track: 60, Kind: sched.Serve, Move: 10},
		{Track: 199, Kind: sched.Edge, Move: 139},
		{Track: 0, Kind: sched.Jump, Move: 199},
		{Track: 10, Kind: sched.Serve, Move: 10},
	}
	if !reflect.DeepEqual(r.Stops, want) {
		t.Errorf("stops = %+v", r.Stops)
	}
}

func TestEdgeCases(t *testing.T) {
	for _, alg := range sched.Algorithms() {
		r := schedule(t, alg, 10, sched.Up, nil)
		if len(r.Stops) != 0 || r.Total != 0 || r.End != 10 || r.EndDir != sched.Up {
			t.Errorf("%s with no requests: %+v", alg, r)
		}
		// Requests only ahead: no trip to the edge.
		r = schedule(t, alg, 10, sched.Up, []int{10, 12})
		if r.Total != 2 || tracksOf(r)[len(r.Stops)-1] != 12 {
			t.Errorf("%s ahead only: %+v", alg, r)
		}
	}
	// SSTF ties go to the lower track.
	r := schedule(t, sched.SSTF, 50, sched.Up, []int{60, 40})
	if tracksOf(r)[0] != 40 || r.EndDir != sched.Up {
		t.Errorf("tie: %v, dir %v", tracksOf(r), r.EndDir)
	}
}

func TestInvalidInput(t *testing.T) {
	cases := []struct {
		alg  sched.Algorithm
		head int
		reqs []int
	}{
		{sched.FCFS, 200, nil},
		{sched.FCFS, -1, nil},
		{sched.FCFS, 0, []int{200}},
		{"look", 0, nil},
	}
	for _, c := range cases {
		if _, err := sched.Schedule(c.alg, c.head, sched.Up, c.reqs, 200); !errors.Is(err, sched.ErrInvalid) {
			t.Errorf("%+v: error = %v", c, err)
		}
	}
	if _, err := sched.ParseDirection("left"); !errors.Is(err, sched.ErrInvalid) {
		t.Errorf("ParseDirection: %v", err)
	}
	if d, _ := sched.ParseDirection("down"); d != sched.Down {
		t.Error("ParseDirection(down)")
	}
}

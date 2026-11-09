package alloc

// Bitmap tracks which blocks are in use. It is controller state kept in
// memory, like a superblock; everything else lives on disk.
type Bitmap struct {
	used []bool
}

// Run is a sequence of consecutive blocks.
type Run struct {
	Start int64
	Len   int64
}

// NewBitmap returns a bitmap of n free blocks.
func NewBitmap(n int64) *Bitmap {
	return &Bitmap{used: make([]bool, n)}
}

// Len returns the number of blocks tracked.
func (m *Bitmap) Len() int64 { return int64(len(m.used)) }

// IsFree reports whether block b is free.
func (m *Bitmap) IsFree(b int64) bool { return !m.used[b] }

// Set marks block b as used.
func (m *Bitmap) Set(b int64) { m.used[b] = true }

// Clear marks block b as free.
func (m *Bitmap) Clear(b int64) { m.used[b] = false }

// FreeCount returns the number of free blocks.
func (m *Bitmap) FreeCount() int64 {
	var n int64
	for _, u := range m.used {
		if !u {
			n++
		}
	}
	return n
}

// AllocOne marks and returns the first free block (first-fit).
func (m *Bitmap) AllocOne() (int64, bool) {
	for b, u := range m.used {
		if !u {
			m.used[b] = true
			return int64(b), true
		}
	}
	return 0, false
}

// FindRun returns the start of the first run of n free blocks (first-fit)
// without marking it.
func (m *Bitmap) FindRun(n int64) (int64, bool) {
	for _, r := range m.FreeRuns() {
		if r.Len >= n {
			return r.Start, true
		}
	}
	return 0, false
}

// FreeRuns returns every maximal run of free blocks, in disk order.
func (m *Bitmap) FreeRuns() []Run {
	var runs []Run
	for b := int64(0); b < m.Len(); b++ {
		if m.used[b] {
			continue
		}
		if n := len(runs); n > 0 && runs[n-1].Start+runs[n-1].Len == b {
			runs[n-1].Len++
		} else {
			runs = append(runs, Run{Start: b, Len: 1})
		}
	}
	return runs
}

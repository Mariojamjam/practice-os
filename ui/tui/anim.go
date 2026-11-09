package tui

import (
	"fmt"
	"strings"
	"time"

	tea "charm.land/bubbletea/v2"

	"github.com/Mariojamjam/practice-os/core/storage/raid"
)

// animation replays something that already happened in the simulation,
// one frame per tick, so it can be followed: the disk arm visiting each
// stop, or a RAID disk being rebuilt block by block. The simulation state
// is final from the start; only the drawing catches up. Esc skips it.
type animation struct {
	id      int
	frame   int
	frames  int
	rebuilt []raid.Rebuilt // set for a rebuild animation
}

type animTick struct{ id int }

// rebuildFrames is how many steps a rebuild progress bar takes.
const rebuildFrames = 20

func (a *App) interval() time.Duration {
	switch a.opts.Animation {
	case "off":
		return 0
	case "slow":
		return 300 * time.Millisecond
	case "fast":
		return 40 * time.Millisecond
	}
	return 120 * time.Millisecond
}

// Animating reports whether an animation is playing.
func (a *App) Animating() bool { return a.anim != nil }

// startArm animates the head paths of the last flushes.
func (a *App) startArm() tea.Cmd {
	frames := 0
	for _, f := range a.lastIO {
		if f.Sched != nil {
			frames = max(frames, len(f.Sched.Stops)+1)
		}
	}
	return a.start(frames, nil)
}

// startRebuild animates a rebuild's progress.
func (a *App) startRebuild(rebuilt []raid.Rebuilt) tea.Cmd {
	return a.start(rebuildFrames, rebuilt)
}

func (a *App) start(frames int, rebuilt []raid.Rebuilt) tea.Cmd {
	a.anim = nil
	if a.interval() == 0 || frames < 2 {
		return nil
	}
	a.animID++
	a.anim = &animation{id: a.animID, frame: 1, frames: frames, rebuilt: rebuilt}
	return a.tick()
}

func (a *App) tick() tea.Cmd {
	id := a.anim.id
	return tea.Tick(a.interval(), func(time.Time) tea.Msg { return animTick{id: id} })
}

// advance moves to the next frame and schedules the following one.
func (a *App) advance(msg animTick) tea.Cmd {
	if a.anim == nil || msg.id != a.anim.id {
		return nil // a skipped or replaced animation
	}
	a.anim.frame++
	if a.anim.frame >= a.anim.frames {
		a.anim = nil
		return nil
	}
	return a.tick()
}

// armFrame returns how many stops of a head path to draw (all of them when
// nothing is animating).
func (a *App) armFrame(stops int) int {
	if a.anim == nil || a.anim.rebuilt != nil {
		return stops
	}
	return min(stops, a.anim.frame)
}

// rebuildProgress draws the progress bars of a rebuild animation.
func (a *App) rebuildProgress(w int) string {
	if a.anim == nil || a.anim.rebuilt == nil {
		return ""
	}
	g := a.glyphs()
	barW := max(10, min(40, w-40))
	var b strings.Builder
	for _, rb := range a.anim.rebuilt {
		done := rb.Blocks * int64(a.anim.frame) / int64(a.anim.frames)
		filled := int(int64(barW) * done / rb.Blocks)
		how := "copying from the mirror"
		if rb.Parity {
			how = "XOR of the other disks"
		}
		fmt.Fprintf(&b, "Rebuilding Disk %d [%s%s] %d/%d blocks (%s)\n", rb.Disk,
			fg(colPartial).Render(strings.Repeat(g.full[:len(g.full)/2], filled)),
			styleMuted.Render(strings.Repeat(g.free[:len(g.free)/2], barW-filled)),
			done, rb.Blocks, how)
	}
	return strings.TrimRight(b.String(), "\n")
}

// rebuilding reports whether disk i (0-based) is shown as being rebuilt.
func (a *App) rebuilding(i int) bool {
	if a.anim == nil {
		return false
	}
	for _, rb := range a.anim.rebuilt {
		if rb.Disk == i+1 {
			return true
		}
	}
	return false
}

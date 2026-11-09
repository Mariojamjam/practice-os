package tui_test

import (
	"testing"

	tea "charm.land/bubbletea/v2"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/ui/tui"
)

func animatedApp(t *testing.T, speed string, edit func(*config.Config)) *tui.App {
	t.Helper()
	cfg := config.Default()
	edit(&cfg)
	k, err := kernel.New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	return tui.New(k, tui.Options{Animation: speed})
}

// play runs an animation to its end by delivering each tick.
func play(t *testing.T, a *tui.App, cmd tea.Cmd) int {
	t.Helper()
	frames := 0
	for cmd != nil {
		frames++
		if frames > 1000 {
			t.Fatal("animation never ends")
		}
		_, cmd = a.Update(cmd())
	}
	return frames
}

func TestArmAnimation(t *testing.T) {
	a := animatedApp(t, "fast", func(*config.Config) {})
	cmd := a.Exec("sched --queue 9,2,14 --head 5")
	if cmd == nil || !a.Animating() {
		t.Fatal("sched did not start an animation")
	}
	if frames := play(t, a, cmd); frames != 3 { // start + 3 stops = 4 frames, 3 ticks
		t.Errorf("ticks = %d", frames)
	}
	if a.Animating() {
		t.Error("animation still running")
	}
	if cmd := a.Exec("mkdir /a"); cmd == nil {
		t.Error("serving I/O should animate the head")
	}
}

func TestRebuildAnimation(t *testing.T) {
	a := animatedApp(t, "fast", func(c *config.Config) { c.IO.Device = config.DeviceRAID })
	a.Exec("create /f --size 8KB")
	a.Exec("fail_disk 2")
	cmd := a.Exec("rebuild")
	if cmd == nil || !a.Animating() {
		t.Fatal("rebuild did not start an animation")
	}
	if got := play(t, a, cmd); got < 2 {
		t.Errorf("rebuild animation ended after %d ticks", got)
	}
}

func TestSkipAndOff(t *testing.T) {
	a := animatedApp(t, "slow", func(*config.Config) {})
	cmd := a.Exec("sched --queue 9,2,14")
	a.Update(tea.KeyPressMsg{Code: tea.KeyEscape})
	if a.Animating() {
		t.Fatal("esc did not skip the animation")
	}
	if _, next := a.Update(cmd()); next != nil {
		t.Error("a tick from a skipped animation must be ignored")
	}

	off := animatedApp(t, "off", func(*config.Config) {})
	if cmd := off.Exec("sched --queue 9,2,14"); cmd != nil || off.Animating() {
		t.Error("animation off must not animate")
	}
	if cmd := off.Exec("pwd"); cmd != nil {
		t.Error("a command without I/O must not animate")
	}
}

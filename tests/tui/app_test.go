package tui_test

import (
	"strings"
	"testing"

	tea "charm.land/bubbletea/v2"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/internal/tui"
)

func newApp(t *testing.T, edit func(*config.Config)) (*tui.App, *kernel.Kernel) {
	t.Helper()
	cfg := config.Default()
	edit(&cfg)
	k, err := kernel.New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	return tui.New(k, tui.Options{}), k
}

func key(code rune) tea.KeyPressMsg { return tea.KeyPressMsg{Code: code} }

func typeText(a *tui.App, s string) {
	for _, r := range s {
		a.Update(tea.KeyPressMsg{Code: r, Text: string(r)})
	}
}

func logHas(a *tui.App, want string) bool {
	return strings.Contains(strings.Join(a.Log(), "\n"), want)
}

func TestCommandsRunThroughTheShell(t *testing.T) {
	a, k := newApp(t, func(*config.Config) {})
	typeText(a, "mkdir /docs")
	a.Update(key(tea.KeyEnter))
	if a.Input() != "" {
		t.Errorf("input not cleared: %q", a.Input())
	}
	if _, err := k.FS.Stat("/docs"); err != nil {
		t.Fatalf("mkdir did not run: %v", err)
	}
	a.Exec("create /docs/a.txt --size 10KB")
	a.Exec("tree")
	a.Exec("rm /nope")
	for _, want := range []string{"> mkdir /docs", "> tree", "a.txt (10 KB) [FILE]", "error: /nope: no such file or directory"} {
		if !logHas(a, want) {
			t.Errorf("log is missing %q", want)
		}
	}
	if !logHas(a, "2048 bytes are internal fragmentation") {
		t.Error("no explanation after create")
	}
	a.Exec("   ")
	if logHas(a, "> \n") {
		t.Error("blank lines must not be logged")
	}
}

func TestTabs(t *testing.T) {
	a, _ := newApp(t, func(*config.Config) {})
	if got := strings.Join(a.Tabs(), ","); got != "FS,I/O,RAID/SSD" || a.Tab() != tui.TabFS {
		t.Fatalf("tabs %s, active %s", got, a.Tab())
	}
	a.Update(key(tea.KeyTab))
	if a.Tab() != tui.TabIO {
		t.Errorf("after tab: %s", a.Tab())
	}
	a.Update(key(tea.KeyTab))
	a.Update(key(tea.KeyTab))
	if a.Tab() != tui.TabFS {
		t.Errorf("tab must wrap around: %s", a.Tab())
	}
	a.Update(tea.KeyPressMsg{Code: tea.KeyTab, Mod: tea.ModShift})
	if a.Tab() != tui.TabRAID {
		t.Errorf("after shift+tab: %s", a.Tab())
	}
}

func TestHistory(t *testing.T) {
	a, _ := newApp(t, func(*config.Config) {})
	a.Exec("pwd")
	a.Exec("ls /")
	a.Update(key(tea.KeyUp))
	if a.Input() != "ls /" {
		t.Errorf("up: %q", a.Input())
	}
	a.Update(key(tea.KeyUp))
	a.Update(key(tea.KeyUp)) // stays on the oldest entry
	if a.Input() != "pwd" {
		t.Errorf("up twice: %q", a.Input())
	}
	a.Update(key(tea.KeyDown))
	a.Update(key(tea.KeyDown))
	if a.Input() != "" {
		t.Errorf("down past the newest entry: %q", a.Input())
	}
}

// Drawing the tabs reads the file system; it must not queue simulated I/O.
func TestRefreshLeavesNoIO(t *testing.T) {
	for _, device := range config.Devices {
		t.Run(device, func(t *testing.T) {
			a, k := newApp(t, func(c *config.Config) { c.IO.Device = device })
			a.Exec("io_defer on")
			a.Exec("create /f --size 4KB")
			before := pending(k)
			if before == 0 {
				t.Fatal("create queued nothing")
			}
			a.Exec("pwd")
			a.Update(tea.WindowSizeMsg{Width: 80, Height: 24})
			_ = a.View()
			if after := pending(k); after != before {
				t.Errorf("pending requests %d -> %d", before, after)
			}
		})
	}
}

func pending(k *kernel.Kernel) int {
	n := 0
	for _, f := range k.Pending() {
		n += len(f.Requests)
	}
	return n
}

func TestRAIDFailureIsLogged(t *testing.T) {
	a, _ := newApp(t, func(c *config.Config) { c.IO.Device = config.DeviceRAID })
	a.Exec("create /f --size 8KB")
	a.Exec("fail_disk 2")
	a.Exec("read_file /f")
	if !logHas(a, "rebuilt by XOR") {
		t.Error("degraded read not reported")
	}
	a.Exec("rebuild")
	if !logHas(a, "Disk 2 replaced") {
		t.Error("rebuild not reported")
	}
}

func TestQuit(t *testing.T) {
	a, _ := newApp(t, func(*config.Config) {})
	_, cmd := a.Update(tea.KeyPressMsg{Code: 'c', Mod: tea.ModCtrl})
	if cmd == nil {
		t.Fatal("ctrl+c returned no command")
	}
	if _, ok := cmd().(tea.QuitMsg); !ok {
		t.Error("ctrl+c does not quit")
	}
}

func TestViewInEveryTab(t *testing.T) {
	for _, preset := range config.Presets() {
		cfg, err := config.Load(config.Options{Dir: t.TempDir(), Overrides: config.Overrides{Preset: &preset}})
		if err != nil {
			t.Fatal(err)
		}
		k, err := kernel.New(cfg)
		if err != nil {
			t.Fatal(err)
		}
		a := tui.New(k, tui.Options{ASCII: true})
		a.Exec("create /f --size 10KB")
		for range a.Tabs() {
			if a.View().Content == "" {
				t.Errorf("%s: empty view on tab %s", preset, a.Tab())
			}
			a.Update(key(tea.KeyTab))
		}
	}
}

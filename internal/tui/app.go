// Package tui is the terminal user interface of practice-os, built with
// Bubble Tea. It runs every command through the same shell as the other
// interfaces and draws the simulator state in tabs, one per subsystem.
package tui

import (
	"strings"

	"charm.land/bubbles/v2/textinput"
	"charm.land/bubbles/v2/viewport"
	tea "charm.land/bubbletea/v2"

	"github.com/Mariojamjam/practice-os/internal/blockio"
	"github.com/Mariojamjam/practice-os/internal/kernel"
	"github.com/Mariojamjam/practice-os/internal/render"
	"github.com/Mariojamjam/practice-os/internal/shell"
)

// Tab names.
const (
	TabFS   = "FS"
	TabIO   = "I/O"
	TabRAID = "RAID/SSD"
)

// Options configures the interface.
type Options struct {
	// ASCII replaces box-drawing and block characters with plain ASCII.
	ASCII bool
	// Preset is shown in the header.
	Preset string
}

// App is the Bubble Tea model of the interface.
type App struct {
	k    *kernel.Kernel
	sh   *shell.Shell
	opts Options

	tabs []string
	tab  int

	input   textinput.Model
	log     viewport.Model
	lines   []string
	history []string
	histPos int

	snap   snapshot
	lastIO []blockio.Flush // last flushes that served requests, for the I/O tab

	width, height int
}

var _ tea.Model = (*App)(nil)

// New returns the interface for kernel k.
func New(k *kernel.Kernel, opts Options) *App {
	in := textinput.New()
	in.Prompt = "> "
	in.Placeholder = "type a command, e.g. mkdir /docs   (tab: switch view, ctrl+c: quit)"
	in.Focus()

	a := &App{
		k:     k,
		sh:    shell.New(k),
		opts:  opts,
		tabs:  []string{TabFS, TabIO, TabRAID},
		input: in,
		log:   viewport.New(),
		width: 100, height: 32,
	}
	a.log.SoftWrap = true
	a.appendLog("Welcome to practice-os. Commands run on the simulated disk; the tabs above show its state.",
		"Try: mkdir /docs, create /docs/a.txt --size 10KB, fs_status --details, sched --queue 98,183,37 --head 53.")
	a.refresh()
	a.layout()
	return a
}

// Run starts the interface on the terminal and blocks until it quits.
func Run(k *kernel.Kernel, opts Options) error {
	_, err := tea.NewProgram(New(k, opts)).Run()
	return err
}

// Tabs returns the tab names, in order.
func (a *App) Tabs() []string { return append([]string(nil), a.tabs...) }

// Tab returns the active tab's name.
func (a *App) Tab() string { return a.tabs[a.tab] }

// Log returns every line written to the output log.
func (a *App) Log() []string { return append([]string(nil), a.lines...) }

// Input returns the text in the command bar.
func (a *App) Input() string { return a.input.Value() }

// Init implements tea.Model.
func (a *App) Init() tea.Cmd { return textinput.Blink }

// Update implements tea.Model.
func (a *App) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		a.width, a.height = msg.Width, msg.Height
		a.layout()
		return a, nil
	case tea.KeyPressMsg:
		switch msg.String() {
		case "ctrl+c", "ctrl+d":
			return a, tea.Quit
		case "enter":
			line := a.input.Value()
			a.input.Reset()
			a.Exec(line)
			return a, nil
		case "tab":
			a.tab = (a.tab + 1) % len(a.tabs)
			return a, nil
		case "shift+tab":
			a.tab = (a.tab + len(a.tabs) - 1) % len(a.tabs)
			return a, nil
		case "up":
			a.browseHistory(-1)
			return a, nil
		case "down":
			a.browseHistory(1)
			return a, nil
		case "pgup":
			a.log.PageUp()
			return a, nil
		case "pgdown":
			a.log.PageDown()
			return a, nil
		}
	}
	var cmd tea.Cmd
	a.input, cmd = a.input.Update(msg)
	return a, cmd
}

// Exec runs one command line, logs its output and an explanation, and
// refreshes every tab.
func (a *App) Exec(line string) {
	line = strings.TrimSpace(line)
	if line == "" {
		return
	}
	a.history = append(a.history, line)
	a.histPos = len(a.history)

	before := a.snap
	res, err := a.sh.Exec(line)
	ropts := render.Options{ASCII: a.opts.ASCII}
	out := render.Result(res, ropts)
	if err != nil {
		out = render.Error(err)
	}
	if io := render.IO(a.sh.LastIO(), ropts); io != "" {
		if out != "" {
			out += "\n"
		}
		out += io
	}
	if served(a.sh.Flushed()) {
		a.lastIO = a.sh.Flushed()
	}
	a.refresh()

	entry := []string{"> " + line}
	if out = strings.TrimRight(out, "\n"); out != "" {
		entry = append(entry, out)
	}
	if note := explain(a, line, res, err, before); note != "" {
		entry = append(entry, "i "+note)
	}
	a.appendLog(entry...)
}

// served reports whether any flush did work worth drawing.
func served(flushes []blockio.Flush) bool {
	for _, f := range flushes {
		if len(f.Requests) > 0 || len(f.Events) > 0 {
			return true
		}
	}
	return false
}

func (a *App) refresh() { a.snap = takeSnapshot(a.k) }

func (a *App) browseHistory(step int) {
	if len(a.history) == 0 {
		return
	}
	a.histPos = min(max(a.histPos+step, 0), len(a.history))
	if a.histPos == len(a.history) {
		a.input.SetValue("")
	} else {
		a.input.SetValue(a.history[a.histPos])
	}
	a.input.CursorEnd()
}

func (a *App) appendLog(lines ...string) {
	for _, l := range lines {
		a.lines = append(a.lines, strings.Split(l, "\n")...)
	}
	a.lines = append(a.lines, "")
	a.log.SetContent(strings.Join(a.lines, "\n"))
	a.log.GotoBottom()
}

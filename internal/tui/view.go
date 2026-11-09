package tui

import (
	"fmt"
	"strings"

	tea "charm.land/bubbletea/v2"
	"charm.land/lipgloss/v2"

	"github.com/Mariojamjam/practice-os/internal/config"
)

// Fixed rows: header, tab bar, two separators, input and help line.
const chromeRows = 6

func (a *App) bodyHeight() int {
	return max(6, (a.height-chromeRows)*3/5)
}

func (a *App) layout() {
	logH := max(3, a.height-chromeRows-a.bodyHeight())
	a.log.SetWidth(a.width)
	a.log.SetHeight(logH)
	a.input.SetWidth(max(10, a.width-3))
	a.log.GotoBottom()
}

// View implements tea.Model.
func (a *App) View() tea.View {
	w, h := a.width, a.bodyHeight()
	var body string
	switch a.Tab() {
	case TabFS:
		body = a.fsView(w, h)
	case TabIO:
		body = a.ioView(w, h)
	case TabRAID:
		body = a.raidView(w, h)
	}
	body = lipgloss.NewStyle().Width(w).Height(h).MaxWidth(w).MaxHeight(h).Render(body)
	sep := styleMuted.Render(strings.Repeat(a.glyphs().axis, w))

	v := tea.NewView(lipgloss.JoinVertical(lipgloss.Left,
		a.header(), a.tabBar(), sep, body, sep, a.log.View(), a.input.View(), a.help(),
	))
	v.AltScreen = true
	v.WindowTitle = "practice-os"
	return v
}

func (a *App) header() string {
	cfg := a.k.Config
	device := cfg.IO.Device
	switch device {
	case config.DeviceRAID:
		device = fmt.Sprintf("RAID %d of %d %ss", cfg.RAID.Level, cfg.RAID.Disks, cfg.RAID.Member)
	case config.DeviceHDD:
		device = fmt.Sprintf("HDD, %d tracks", cfg.Disk.TrackCount())
	case config.DeviceSSD:
		device = "SSD"
	}
	preset := a.opts.Preset
	if preset == "" {
		preset = "default"
	}
	parts := []string{
		"practice-os",
		"preset " + preset,
		"alloc " + a.k.FS.Strategy(),
		device,
		"sched " + cfg.IO.Scheduler,
		"trace " + onOffWord(a.k.Trace),
		"defer " + onOffWord(a.k.Defer),
		"cwd " + a.snap.cwd,
	}
	line := " " + strings.Join(parts, " │ ") + " "
	if a.opts.ASCII {
		line = " " + strings.Join(parts, " | ") + " "
	}
	return styleHeader.Width(a.width).MaxWidth(a.width).Render(line)
}

func (a *App) tabBar() string {
	var parts []string
	for i, t := range a.tabs {
		label := fmt.Sprintf(" %s ", t)
		if i == a.tab {
			parts = append(parts, styleTabActive.Render(label))
		} else {
			parts = append(parts, styleTab.Render(label))
		}
	}
	return strings.Join(parts, " ")
}

func (a *App) help() string {
	return styleMuted.Width(a.width).MaxWidth(a.width).Render(
		"enter run · tab/shift+tab switch view · ↑/↓ history · pgup/pgdn scroll log · ctrl+c quit")
}

func onOffWord(b bool) string {
	if b {
		return "on"
	}
	return "off"
}

// clip cuts every line of s to width w.
func clip(s string, w int) string {
	return lipgloss.NewStyle().MaxWidth(w).Render(s)
}

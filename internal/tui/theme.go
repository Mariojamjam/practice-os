package tui

import (
	"image/color"

	"charm.land/lipgloss/v2"

	"github.com/Mariojamjam/practice-os/internal/diag"
)

// Colors use the 16 basic ANSI colors so they follow the terminal theme.
var (
	colAccent  = lipgloss.Color("6")
	colMuted   = lipgloss.Color("8")
	colFAT     = lipgloss.Color("5")
	colDir     = lipgloss.Color("4")
	colInode   = lipgloss.Color("6")
	colData    = lipgloss.Color("2")
	colPartial = lipgloss.Color("3")
	colParity  = lipgloss.Color("13")
	colFailed  = lipgloss.Color("1")
	colOK      = lipgloss.Color("2")
)

var (
	styleHeader    = lipgloss.NewStyle().Bold(true).Reverse(true)
	styleTabActive = lipgloss.NewStyle().Bold(true).Underline(true).Foreground(colAccent)
	styleTab       = lipgloss.NewStyle().Foreground(colMuted)
	styleMuted     = lipgloss.NewStyle().Foreground(colMuted)
	styleTitle     = lipgloss.NewStyle().Bold(true)
	styleFailed    = lipgloss.NewStyle().Bold(true).Foreground(colFailed)
	styleOK        = lipgloss.NewStyle().Foreground(colOK)
)

func fg(c color.Color) lipgloss.Style { return lipgloss.NewStyle().Foreground(c) }

// glyphs are the characters used to draw blocks and paths.
type glyphs struct {
	full, partial, free string
	head, edge, jump    string
	axis, sep           string
	letters             map[diag.BlockKind]string
	heat                []string
}

var unicodeGlyphs = glyphs{
	full: "██", partial: "▓▓", free: "░░",
	head: "●", edge: "◆", jump: "↺",
	axis: "─", sep: "│",
	heat: []string{"░░", "▒▒", "▓▓", "██"},
}

var asciiGlyphs = glyphs{
	full: "##", partial: "++", free: "..",
	head: "o", edge: "*", jump: "^",
	axis: "-", sep: "|",
	letters: map[diag.BlockKind]string{
		diag.KindFAT: "FF", diag.KindRootInode: "RR", diag.KindRootDir: "RR",
		diag.KindDirInode: "DD", diag.KindDir: "DD", diag.KindFileInode: "II",
	},
	heat: []string{"..", "::", "++", "##"},
}

func (a *App) glyphs() glyphs {
	if a.opts.ASCII {
		return asciiGlyphs
	}
	return unicodeGlyphs
}

// blockColor is the color of a block kind on the disk map.
func blockColor(k diag.BlockKind) color.Color {
	switch k {
	case diag.KindFAT:
		return colFAT
	case diag.KindRootInode, diag.KindRootDir, diag.KindDirInode, diag.KindDir:
		return colDir
	case diag.KindFileInode:
		return colInode
	case diag.KindData:
		return colData
	}
	return colMuted
}

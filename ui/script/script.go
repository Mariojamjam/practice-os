// Package script runs sequences of shell commands (script files, -c
// arguments, demos) and writes a transcript in the course specification's
// format: each command echoed as "> command", followed by its output.
package script

import (
	"fmt"
	"io"
	"strings"

	"github.com/Mariojamjam/practice-os/ui/render"
	"github.com/Mariojamjam/practice-os/ui/shell"
)

// Lines returns the commands of a script: one per line, skipping blank
// lines and # comments.
func Lines(src string) []string {
	var out []string
	for _, line := range strings.Split(src, "\n") {
		line = strings.TrimSpace(line)
		if line != "" && !strings.HasPrefix(line, "#") {
			out = append(out, line)
		}
	}
	return out
}

// Preset returns the preset named by a "# preset: NAME" comment, or "".
func Preset(src string) string {
	for _, line := range strings.Split(src, "\n") {
		if name, ok := strings.CutPrefix(strings.TrimSpace(line), "# preset:"); ok {
			return strings.TrimSpace(name)
		}
	}
	return ""
}

// Output runs one command line with sh and returns what it printed: its
// result or error, then its I/O (when traced, or RAID events). The text
// ends with a newline unless it is empty.
func Output(sh *shell.Shell, line string, o render.Options) (string, error) {
	res, err := sh.Exec(line)
	out := render.Result(res, o)
	if err != nil {
		out = render.Error(err)
	}
	if io := render.IO(sh.LastIO(), o); io != "" {
		if out != "" {
			out += "\n"
		}
		out += io
	}
	return out, err
}

// Run executes each command with sh and writes the transcript to w: the
// echoed command, its output and a blank line. Every command runs even if
// an earlier one fails; Run returns how many failed.
func Run(sh *shell.Shell, commands []string, w io.Writer, o render.Options) (failed int, err error) {
	for _, line := range commands {
		out, cmdErr := Output(sh, line, o)
		if cmdErr != nil {
			failed++
		}
		if out != "" {
			out += "\n"
		}
		if _, err := fmt.Fprintf(w, "> %s\n%s", line, out); err != nil {
			return failed, err
		}
	}
	return failed, nil
}

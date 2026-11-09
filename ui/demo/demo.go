// Package demo embeds the reference scenarios: the examples from the
// course specification and a few more that show each mechanism. Each is
// a script whose "# preset: NAME" comment picks its configuration
// (stage1 when absent).
package demo

import (
	"embed"
	"fmt"
	"sort"
	"strings"

	"github.com/Mariojamjam/practice-os/ui/script"
)

//go:embed scripts/*.txt
var scripts embed.FS

// DefaultPreset is used by scripts without a "# preset:" comment.
const DefaultPreset = "stage1"

// Demo is one embedded scenario.
type Demo struct {
	// Name is the script name, e.g. "example-1.2".
	Name string
	// Title is the first comment line, describing the scenario.
	Title string
	// Preset is the configuration the scenario runs with.
	Preset string
	// Source is the script text.
	Source string
}

// Commands returns the scenario's commands.
func (d Demo) Commands() []string { return script.Lines(d.Source) }

// All returns every scenario, sorted by name.
func All() []Demo {
	entries, err := scripts.ReadDir("scripts")
	if err != nil {
		return nil
	}
	var out []Demo
	for _, e := range entries {
		data, err := scripts.ReadFile("scripts/" + e.Name())
		if err != nil {
			continue
		}
		out = append(out, parse(strings.TrimSuffix(e.Name(), ".txt"), string(data)))
	}
	sort.Slice(out, func(i, j int) bool { return out[i].Name < out[j].Name })
	return out
}

// Find returns the scenario with the given name. Reference examples can
// also be named by their number: "1.2" is "example-1.2".
func Find(name string) (Demo, error) {
	for _, d := range All() {
		if d.Name == name || d.Name == "example-"+name {
			return d, nil
		}
	}
	var names []string
	for _, d := range All() {
		names = append(names, d.Name)
	}
	return Demo{}, fmt.Errorf("unknown demo %q (available: %s, or all)", name, strings.Join(names, ", "))
}

func parse(name, src string) Demo {
	d := Demo{Name: name, Source: src, Preset: script.Preset(src)}
	if d.Preset == "" {
		d.Preset = DefaultPreset
	}
	for _, line := range strings.Split(src, "\n") {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "# preset:") {
			continue
		}
		if title, ok := strings.CutPrefix(line, "#"); ok {
			d.Title = strings.TrimSpace(title)
			break
		}
	}
	return d
}

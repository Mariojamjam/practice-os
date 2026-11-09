package shell_test

import (
	"flag"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/Mariojamjam/practice-os/internal/config"
	"github.com/Mariojamjam/practice-os/internal/kernel"
	"github.com/Mariojamjam/practice-os/internal/render"
	"github.com/Mariojamjam/practice-os/internal/shell"
)

var update = flag.Bool("update", false, "rewrite the golden files with the current output")

// TestGolden runs every testdata/golden/NAME.txt script through the shell
// with the stage1 preset and compares the transcript with NAME.golden.
// Regenerate with: go test ./tests/shell -update
func TestGolden(t *testing.T) {
	scripts, err := filepath.Glob(filepath.Join("testdata", "golden", "*.txt"))
	if err != nil || len(scripts) == 0 {
		t.Fatalf("no golden scripts found (%v)", err)
	}
	for _, script := range scripts {
		name := strings.TrimSuffix(filepath.Base(script), ".txt")
		t.Run(name, func(t *testing.T) {
			src, err := os.ReadFile(script)
			if err != nil {
				t.Fatal(err)
			}
			got := transcript(t, string(src))
			golden := strings.TrimSuffix(script, ".txt") + ".golden"
			if *update {
				if err := os.WriteFile(golden, []byte(got), 0o644); err != nil {
					t.Fatal(err)
				}
				return
			}
			want, err := os.ReadFile(golden)
			if err != nil {
				t.Fatalf("%v (run with -update to create it)", err)
			}
			if got != string(want) {
				t.Errorf("output differs from %s\n--- got ---\n%s\n--- want ---\n%s", golden, got, want)
			}
		})
	}
}

// transcript runs a script and returns its output in the reference format:
// each command echoed as "> command", followed by its output and a blank
// line. Comments and blank lines are not echoed.
func transcript(t *testing.T, src string) string {
	t.Helper()
	preset := "stage1"
	cfg, err := config.Load(config.Options{Dir: t.TempDir(), Overrides: config.Overrides{Preset: &preset}})
	if err != nil {
		t.Fatal(err)
	}
	k, err := kernel.New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	sh := shell.New(k)

	var b strings.Builder
	for _, line := range strings.Split(src, "\n") {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		b.WriteString("> " + line + "\n")
		res, err := sh.Exec(line)
		out := render.Result(res, render.Options{})
		if err != nil {
			out = render.Error(err)
		}
		if out != "" {
			b.WriteString(out + "\n")
		}
	}
	return b.String()
}

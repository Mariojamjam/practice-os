package cli_test

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/Mariojamjam/practice-os/ui/cli"
)

// run executes practice-os with args and stdin, returning stdout, stderr
// and the error.
func run(t *testing.T, stdin string, args ...string) (string, string, error) {
	t.Helper()
	cmd := cli.NewRootCmd()
	var out, errOut strings.Builder
	cmd.SetArgs(args)
	cmd.SetIn(strings.NewReader(stdin))
	cmd.SetOut(&out)
	cmd.SetErr(&errOut)
	err := cmd.Execute()
	return out.String(), errOut.String(), err
}

func TestCommandFlag(t *testing.T) {
	out, _, err := run(t, "", "-c", `mkdir /docs; create /docs/a.txt "hi"; cat /docs/a.txt`)
	if err != nil {
		t.Fatal(err)
	}
	want := "> mkdir /docs\n> create /docs/a.txt \"hi\"\n> cat /docs/a.txt\nhi\n\n"
	if out != want {
		t.Errorf("transcript:\n%s\nwant:\n%s", out, want)
	}
	if _, _, err := run(t, "", "-c", "pwd; rm /nope"); !errors.Is(err, cli.ErrCommandsFailed) {
		t.Errorf("failing command: %v", err)
	}
	if _, _, err := run(t, "", "--preset", "nope", "-c", "pwd"); err == nil {
		t.Error("bad preset: want error")
	}
}

func TestFlagsReachTheConfig(t *testing.T) {
	out, _, err := run(t, "", "--alloc", "linked", "--blocks", "32", "-c", "fs_status")
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(out, "Allocation strategy: linked") || !strings.Contains(out, "Total blocks: 32") {
		t.Errorf("flags not applied:\n%s", out)
	}
}

func TestRun(t *testing.T) {
	file := filepath.Join(t.TempDir(), "s.txt")
	if err := os.WriteFile(file, []byte("# a scenario\nmkdir /a\n\nls /\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	out, _, err := run(t, "", "run", file)
	if err != nil || out != "> mkdir /a\n> ls /\na/ [DIR]\n\n" {
		t.Errorf("run: %q, %v", out, err)
	}
	if _, _, err := run(t, "", "run", filepath.Join(t.TempDir(), "missing.txt")); err == nil {
		t.Error("missing script: want error")
	}
}

func TestShellReadsStdin(t *testing.T) {
	out, _, err := run(t, "mkdir /a; cd /a\npwd\nexit\npwd\n", "shell")
	if err != nil {
		t.Fatal(err)
	}
	if out != "/a\n" { // piped input: no prompt or banner, and exit stops
		t.Errorf("shell output = %q", out)
	}
}

func TestDemo(t *testing.T) {
	list, _, err := run(t, "", "demo")
	if err != nil || !strings.Contains(list, "disk-scheduling") || !strings.Contains(list, "[preset stage2]") {
		t.Errorf("demo list: %q, %v", list, err)
	}
	out, _, err := run(t, "", "demo", "disk-scheduling")
	if err != nil || !strings.Contains(out, "=== disk-scheduling") || !strings.Contains(out, "= 208 tracks") {
		t.Errorf("demo disk-scheduling: %v\n%s", err, out)
	}
	all, _, err := run(t, "", "demo", "all", "--ascii")
	if err != nil || strings.Count(all, "=== ") < 7 || strings.Contains(all, "└──") {
		t.Errorf("demo all: %v", err)
	}
	if _, _, err := run(t, "", "demo", "2.1"); err == nil {
		t.Error("unknown demo: want error")
	}
}

func TestImageKeepsStateBetweenRuns(t *testing.T) {
	img := filepath.Join(t.TempDir(), "state.json")
	_, errOut, err := run(t, "", "--image", img, "--device", "ssd", "-c", "mkdir /kept; create /kept/f \"data\"")
	if err != nil || !strings.Contains(errOut, "State saved to") {
		t.Fatalf("first run: %v, %q", err, errOut)
	}
	out, errOut, err := run(t, "", "--image", img, "-c", "cat /kept/f")
	if err != nil || out != "> cat /kept/f\ndata\n\n" || !strings.Contains(errOut, "State loaded from") {
		t.Errorf("second run: %q, %q, %v", out, errOut, err)
	}
	if err := os.WriteFile(img, []byte("not json"), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, _, err := run(t, "", "--image", img, "-c", "pwd"); err == nil {
		t.Error("corrupt image: want error")
	}
}

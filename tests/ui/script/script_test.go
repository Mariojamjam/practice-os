package script_test

import (
	"reflect"
	"strings"
	"testing"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/ui/render"
	"github.com/Mariojamjam/practice-os/ui/script"
	"github.com/Mariojamjam/practice-os/ui/shell"
)

func TestLinesAndPreset(t *testing.T) {
	src := "# preset: stage2\n\n  mkdir /a  \n# a comment\ntree\n"
	if got := script.Lines(src); !reflect.DeepEqual(got, []string{"mkdir /a", "tree"}) {
		t.Errorf("Lines = %q", got)
	}
	if got := script.Preset(src); got != "stage2" {
		t.Errorf("Preset = %q", got)
	}
	if got := script.Preset("mkdir /a"); got != "" {
		t.Errorf("no preset: %q", got)
	}
}

func TestRun(t *testing.T) {
	k, err := kernel.New(config.Default())
	if err != nil {
		t.Fatal(err)
	}
	var out strings.Builder
	failed, err := script.Run(shell.New(k), []string{"mkdir /a", "rm /nope", "pwd"}, &out, render.Options{})
	if err != nil || failed != 1 {
		t.Fatalf("failed = %d, err = %v", failed, err)
	}
	want := "> mkdir /a\n" +
		"> rm /nope\nerror: /nope: no such file or directory\n\n" +
		"> pwd\n/\n\n"
	if out.String() != want {
		t.Errorf("transcript:\n%s\nwant:\n%s", out.String(), want)
	}
}

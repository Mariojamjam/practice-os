package demo_test

import (
	"flag"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/ui/demo"
	"github.com/Mariojamjam/practice-os/ui/render"
	"github.com/Mariojamjam/practice-os/ui/script"
	"github.com/Mariojamjam/practice-os/ui/shell"
)

var update = flag.Bool("update", false, "rewrite the golden files with the current output")

// TestGolden runs every embedded scenario with its preset and compares the
// transcript with testdata/NAME.golden. Regenerate with:
// go test ./tests/ui/demo -update
func TestGolden(t *testing.T) {
	demos := demo.All()
	if len(demos) == 0 {
		t.Fatal("no embedded scenarios")
	}
	for _, d := range demos {
		t.Run(d.Name, func(t *testing.T) {
			cfg, err := config.Load(config.Options{Dir: t.TempDir(), Overrides: config.Overrides{Preset: &d.Preset}})
			if err != nil {
				t.Fatal(err)
			}
			k, err := kernel.New(cfg)
			if err != nil {
				t.Fatal(err)
			}
			var out strings.Builder
			if _, err := script.Run(shell.New(k), d.Commands(), &out, render.Options{}); err != nil {
				t.Fatal(err)
			}
			golden := filepath.Join("testdata", d.Name+".golden")
			if *update {
				if err := os.WriteFile(golden, []byte(out.String()), 0o644); err != nil {
					t.Fatal(err)
				}
				return
			}
			want, err := os.ReadFile(golden)
			if err != nil {
				t.Fatalf("%v (run with -update to create it)", err)
			}
			if out.String() != string(want) {
				t.Errorf("output differs from %s\n--- got ---\n%s\n--- want ---\n%s", golden, out.String(), want)
			}
		})
	}
}

func TestFind(t *testing.T) {
	d, err := demo.Find("indexed-allocation")
	if err != nil || d.Preset != "stage1" || !strings.Contains(d.Title, "ndexed allocation") {
		t.Errorf("Find(indexed-allocation) = %+v, %v", d, err)
	}
	d, err = demo.Find("raid5-recovery")
	if err != nil || d.Preset != "stage2" || !strings.Contains(d.Title, "RAID 5") || len(d.Commands()) == 0 {
		t.Errorf("Find(raid5-recovery) = %+v, %v", d, err)
	}
	if _, err := demo.Find("2.2"); err == nil {
		t.Error("numbers are not demo names")
	}
	if _, err := demo.Find("nope"); err == nil || !strings.Contains(err.Error(), "directory-tree") {
		t.Errorf("unknown demo: %v", err)
	}
}

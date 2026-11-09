package shell_test

import (
	"errors"
	"testing"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/ui/shell"
)

func newShell(t *testing.T) *shell.Shell {
	t.Helper()
	k, err := kernel.New(config.Default())
	if err != nil {
		t.Fatal(err)
	}
	return shell.New(k)
}

func TestExecErrors(t *testing.T) {
	s := newShell(t)
	tests := []struct {
		line string
		want error
	}{
		{"nope", shell.ErrUnknownCommand},
		{"mkdir", shell.ErrUsage},
		{"mkdir /a /b", shell.ErrUsage},
		{"pwd --bogus", shell.ErrUsage},
		{`echo "x`, shell.ErrSyntax},
	}
	for _, tt := range tests {
		if _, err := s.Exec(tt.line); !errors.Is(err, tt.want) {
			t.Errorf("Exec(%q) error = %v, want %v", tt.line, err, tt.want)
		}
	}
	for _, line := range []string{
		"create /f",                // no content
		`create /f "x" --size 1KB`, // both
		"create /f --size huge",    // bad size
		"update /f",                // --size missing
		`write_file /f --truncate`, // --truncate without TEXT
		`write_file /missing "x"`,  // no such file
		"set_alloc fat32",          // unknown strategy
		"read_file /",              // directory
	} {
		if _, err := s.Exec(line); err == nil {
			t.Errorf("Exec(%q): want error", line)
		}
	}
}

func TestExecFileCommands(t *testing.T) {
	s := newShell(t)
	run := func(line string) shell.Result {
		t.Helper()
		r, err := s.Exec(line)
		if err != nil {
			t.Fatalf("Exec(%q): %v", line, err)
		}
		return r
	}
	run("mkdir /docs")
	run("cd docs")
	if r := run("pwd"); r != (shell.PathResult{Path: "/docs"}) {
		t.Errorf("pwd = %+v", r)
	}
	run(`create note.txt "hello"`)
	run(`write_file note.txt " world"`)
	if r := run("cat note.txt").(shell.FileResult); string(r.Data) != "hello world" || r.Path != "/docs/note.txt" {
		t.Errorf("cat = %+v", r)
	}
	run(`write_file note.txt "reset" --truncate`)
	run("update note.txt --size 8")
	if r := run("read_file note.txt").(shell.FileResult); string(r.Data) != "resetFGH" {
		t.Errorf("after update = %q", r.Data)
	}
	run("mv note.txt /note.txt")
	run("cd /")
	if r := run("ls").(shell.ListResult); len(r.Entries) != 2 || r.Entries[1].Name != "note.txt" {
		t.Errorf("ls = %+v", r.Entries)
	}
	run("rm -r /docs")
	tree := run("tree").(shell.TreeResult)
	if len(tree.Root.Children) != 1 || tree.Root.Name != "/" {
		t.Errorf("tree = %+v", tree)
	}
	if r := run("fs_status").(shell.StatusResult); r.Details || len(r.Report.Files) != 1 {
		t.Errorf("fs_status = %+v", r)
	}
}

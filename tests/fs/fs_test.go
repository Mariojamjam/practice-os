package fs_test

import (
	"bytes"
	"errors"
	"reflect"
	"strings"
	"testing"

	"github.com/Mariojamjam/practice-os/internal/alloc"
	"github.com/Mariojamjam/practice-os/internal/disk"
	"github.com/Mariojamjam/practice-os/internal/fs"
)

func newFS(t *testing.T, strategy string, blockSize int, blocks int64) *fs.FS {
	t.Helper()
	f, err := fs.New(disk.New(blockSize, blocks), strategy)
	if err != nil {
		t.Fatal(err)
	}
	return f
}

func must(t *testing.T, err error) {
	t.Helper()
	if err != nil {
		t.Fatal(err)
	}
}

func names(t *testing.T, f *fs.FS, p string) []string {
	t.Helper()
	nodes, err := f.List(p)
	must(t, err)
	var out []string
	for _, n := range nodes {
		out = append(out, n.Name)
	}
	return out
}

func TestCorruptDirectory(t *testing.T) {
	f := newFS(t, alloc.Indexed, 512, 16)
	must(t, f.Mkdir("/d"))
	n, err := f.Stat("/d")
	must(t, err)
	must(t, f.Device().Write(n.Block, []byte("garbage")))
	if _, err := f.List("/d"); !errors.Is(err, fs.ErrCorrupt) {
		t.Errorf("listing a corrupt directory block: %v", err)
	}
}

func TestSynthetic(t *testing.T) {
	if got := string(fs.Synthetic(24, 4)); got != "YZAB" {
		t.Errorf("Synthetic = %q", got)
	}
}

func TestPaths(t *testing.T) {
	f := newFS(t, alloc.Indexed, 512, 64)
	must(t, f.Mkdir("/system"))
	must(t, f.Mkdir("/system/logs"))
	must(t, f.Chdir("/system"))
	must(t, f.Create("logs/app.log", []byte("hello")))

	for _, p := range []string{"/system/logs/app.log", "logs/app.log", "./logs/../logs/app.log", "../system/logs/app.log"} {
		data, err := f.Read(p)
		if err != nil || string(data) != "hello" {
			t.Errorf("Read(%q) = %q, %v", p, data, err)
		}
	}
	must(t, f.Chdir(".."))
	if f.Getwd() != "/" {
		t.Errorf("cwd = %q", f.Getwd())
	}
	must(t, f.Chdir("../../system/logs")) // ".." above root stays at root
	if f.Getwd() != "/system/logs" {
		t.Errorf("cwd = %q", f.Getwd())
	}

	errs := []struct {
		err  error
		want error
	}{
		{f.Chdir("/nope"), fs.ErrNotFound},
		{f.Chdir("/system/logs/app.log"), fs.ErrNotDir},
		{f.Mkdir("/a/b"), fs.ErrNotFound},
		{f.Mkdir("/system"), fs.ErrExists},
		{f.Create("/system/logs/app.log/x", nil), fs.ErrNotDir},
		{f.Mkdir("/" + strings.Repeat("n", fs.MaxNameLen+1)), fs.ErrNameTooLong},
		{f.Mkdir("/system/.."), fs.ErrInvalidName},
	}
	for i, tt := range errs {
		if !errors.Is(tt.err, tt.want) {
			t.Errorf("case %d: error = %v, want %v", i, tt.err, tt.want)
		}
	}
	if _, err := f.Read("/system"); !errors.Is(err, fs.ErrIsDir) {
		t.Errorf("Read dir: %v", err)
	}
}

func TestContentOperations(t *testing.T) {
	for _, strategy := range alloc.Strategies() {
		t.Run(strategy, func(t *testing.T) {
			f := newFS(t, strategy, 512, 64)
			must(t, f.Create("/a", []byte("abc")))
			must(t, f.Append("/a", []byte("def")))
			got, _ := f.Read("/a")
			if string(got) != "abcdef" {
				t.Fatalf("after append: %q", got)
			}

			big := fs.Synthetic(0, 2000) // 4 blocks of 512 B
			must(t, f.Create("/b", []byte("x")))
			must(t, f.Overwrite("/a", big))
			if got, _ := f.Read("/a"); !bytes.Equal(got, big) {
				t.Fatal("overwrite lost data")
			}

			must(t, f.Resize("/a", 700))
			if got, _ := f.Read("/a"); !bytes.Equal(got, big[:700]) {
				t.Fatal("truncate lost data")
			}
			must(t, f.Resize("/a", 1000))
			want := append(big[:700:700], fs.Synthetic(700, 300)...)
			if got, _ := f.Read("/a"); !bytes.Equal(got, want) {
				t.Fatal("extend wrote wrong content")
			}
			n, _ := f.Stat("/a")
			if n.Size != 1000 {
				t.Errorf("size = %d", n.Size)
			}
			if got, _ := f.Read("/b"); string(got) != "x" {
				t.Errorf("neighbour file changed: %q", got)
			}
		})
	}
}

func TestRemoveFreesBlocks(t *testing.T) {
	for _, strategy := range alloc.Strategies() {
		t.Run(strategy, func(t *testing.T) {
			f := newFS(t, strategy, 512, 64)
			free := f.Bitmap().FreeCount()
			must(t, f.Mkdir("/d"))
			must(t, f.Mkdir("/d/e"))
			must(t, f.Create("/d/e/f", fs.Synthetic(0, 1500)))
			must(t, f.Create("/d/g", nil))

			if err := f.Remove("/d", false); !errors.Is(err, fs.ErrNotEmpty) {
				t.Errorf("non-recursive remove: %v", err)
			}
			must(t, f.Chdir("/d/e"))
			if err := f.Remove("/d", true); !errors.Is(err, fs.ErrInvalid) {
				t.Errorf("removing a parent of cwd: %v", err)
			}
			must(t, f.Chdir("/"))
			if err := f.Remove("/", true); !errors.Is(err, fs.ErrInvalid) {
				t.Errorf("removing root: %v", err)
			}
			must(t, f.Remove("/d", true))
			if got := f.Bitmap().FreeCount(); got != free {
				t.Errorf("free blocks = %d, want %d", got, free)
			}
			if len(names(t, f, "/")) != 0 {
				t.Error("root not empty")
			}
		})
	}
}

func TestMove(t *testing.T) {
	f := newFS(t, alloc.Indexed, 512, 64)
	must(t, f.Mkdir("/a"))
	must(t, f.Mkdir("/b"))
	must(t, f.Create("/a/x", []byte("data")))

	must(t, f.Move("/a/x", "/a/y")) // rename
	must(t, f.Move("/a/y", "/b"))   // into existing directory
	if got := names(t, f, "/b"); !reflect.DeepEqual(got, []string{"y"}) {
		t.Errorf("/b = %v", got)
	}
	if got, _ := f.Read("/b/y"); string(got) != "data" {
		t.Errorf("moved content = %q", got)
	}
	must(t, f.Chdir("/b"))
	must(t, f.Move("/b", "/a/b2"))
	if f.Getwd() != "/a/b2" {
		t.Errorf("cwd after moving it = %q", f.Getwd())
	}
	if err := f.Move("/a", "/a/b2/inside"); !errors.Is(err, fs.ErrInvalid) {
		t.Errorf("move into itself: %v", err)
	}
	must(t, f.Create("/c", nil))
	if err := f.Move("/a", "/c"); !errors.Is(err, fs.ErrExists) {
		t.Errorf("move onto file: %v", err)
	}
}

func TestDirectoryFull(t *testing.T) {
	f := newFS(t, alloc.Indexed, 512, 64)
	capacity := fs.DirCapacity(512) // 7
	for i := range capacity {
		must(t, f.Create("/"+string(rune('a'+i)), nil))
	}
	if err := f.Mkdir("/full"); !errors.Is(err, fs.ErrDirectoryFull) {
		t.Errorf("error = %v", err)
	}
	must(t, f.Move("/a", "/renamed")) // renaming in a full directory works
}

func TestSetStrategy(t *testing.T) {
	f := newFS(t, alloc.Indexed, 512, 64)
	must(t, f.SetStrategy(alloc.Linked))
	if f.Strategy() != alloc.Linked || f.Root() != 1 {
		t.Errorf("strategy %s, root %d", f.Strategy(), f.Root())
	}
	must(t, f.Create("/x", nil))
	if err := f.SetStrategy(alloc.Contiguous); !errors.Is(err, fs.ErrDiskNotEmpty) {
		t.Errorf("error = %v", err)
	}
}

func TestCompact(t *testing.T) {
	for _, strategy := range alloc.Strategies() {
		t.Run(strategy, func(t *testing.T) {
			f := newFS(t, strategy, 512, 64)
			must(t, f.Mkdir("/d"))
			files := map[string][]byte{}
			for i, name := range []string{"/a", "/b", "/d/c", "/e"} {
				files[name] = fs.Synthetic(int64(i), int64(300*(i+1)))
				must(t, f.Create(name, files[name]))
			}
			must(t, f.Remove("/b", false))
			delete(files, "/b")
			must(t, f.Chdir("/d"))
			before := names(t, f, "/")

			moves, err := f.Compact()
			must(t, err)
			if len(moves) == 0 {
				t.Error("nothing moved")
			}
			for name, want := range files {
				if got, err := f.Read(name); err != nil || !bytes.Equal(got, want) {
					t.Errorf("%s changed after compaction (%v)", name, err)
				}
			}
			if got := names(t, f, "/"); !reflect.DeepEqual(got, before) {
				t.Errorf("entry order %v, want %v", got, before)
			}
			if f.Getwd() != "/d" {
				t.Errorf("cwd = %q", f.Getwd())
			}
			if runs := f.Bitmap().FreeRuns(); len(runs) != 1 {
				t.Errorf("free space not contiguous: %v", runs)
			}
		})
	}
}

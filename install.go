//go:build ignore

// install.go builds practice-os and installs it as a command.
//
// Prerequisite: Go (the version in go.mod) installed and on PATH. practice-os
// is built from source, so Go is required to install and update it.
//
// Run from the repository root, on any OS:
//
//	go run install.go              install into GOBIN, or GOPATH/bin
//	go run install.go -dir DIR     install into DIR
//	go run install.go -uninstall   remove the installed binary
//
// It never edits PATH. If the install directory is not on PATH, it prints the
// exact line to add for your OS and shell.
package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

func main() {
	dir := flag.String("dir", "", "install directory (default: GOBIN, or GOPATH/bin)")
	uninstall := flag.Bool("uninstall", false, "remove the installed practice-os binary")
	flag.Parse()

	if err := run(*dir, *uninstall); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}

type goEnv struct {
	GOBIN     string
	GOPATH    string
	GOMOD     string
	GOVERSION string
}

func run(dirFlag string, uninstall bool) error {
	env, err := readGoEnv()
	if err != nil {
		return err
	}
	dir, err := installDir(dirFlag, env)
	if err != nil {
		return err
	}
	bin := filepath.Join(dir, binaryName())

	if uninstall {
		switch err := os.Remove(bin); {
		case err == nil:
			fmt.Println("Removed", bin)
		case errors.Is(err, os.ErrNotExist):
			fmt.Println("Nothing to remove:", bin, "does not exist.")
		default:
			return err
		}
		return nil
	}

	root, err := moduleRoot(env)
	if err != nil {
		return err
	}

	fmt.Printf("practice-os is built from source and requires Go (using %s).\n", env.GOVERSION)
	fmt.Println("Building and installing into", dir)
	cmd := exec.Command("go", "install", "./cmd/practice-os")
	cmd.Dir = root
	cmd.Env = append(os.Environ(), "GOBIN="+dir)
	cmd.Stdout, cmd.Stderr = os.Stdout, os.Stderr
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("go install failed: %w", err)
	}
	fmt.Println("Installed", bin)

	if onPath(dir) {
		fmt.Println("Done. Run: practice-os --help")
		return nil
	}
	fmt.Printf("\n%s is not on your PATH. Add it once:\n\n%s\n\n", dir, pathHint(dir))
	fmt.Println("Then open a new terminal and run: practice-os --help")
	return nil
}

func readGoEnv() (goEnv, error) {
	var env goEnv
	out, err := exec.Command("go", "env", "-json", "GOBIN", "GOPATH", "GOMOD", "GOVERSION").Output()
	if err != nil {
		return env, fmt.Errorf("could not run 'go env'; practice-os requires Go installed and on PATH: %w", err)
	}
	if err := json.Unmarshal(out, &env); err != nil {
		return env, fmt.Errorf("parsing go env output: %w", err)
	}
	return env, nil
}

func moduleRoot(env goEnv) (string, error) {
	errNotRepo := errors.New("run this from the practice-os repository root: go run install.go")
	if env.GOMOD == "" || env.GOMOD == os.DevNull {
		return "", errNotRepo
	}
	root := filepath.Dir(env.GOMOD)
	if _, err := os.Stat(filepath.Join(root, "cmd", "practice-os")); err != nil {
		return "", errNotRepo
	}
	return root, nil
}

func installDir(dirFlag string, env goEnv) (string, error) {
	switch {
	case dirFlag != "":
		return filepath.Abs(dirFlag)
	case env.GOBIN != "":
		return env.GOBIN, nil
	}
	paths := filepath.SplitList(env.GOPATH)
	if len(paths) == 0 || paths[0] == "" {
		return "", errors.New("cannot determine install directory: GOBIN and GOPATH are empty")
	}
	return filepath.Join(paths[0], "bin"), nil
}

func binaryName() string {
	if runtime.GOOS == "windows" {
		return "practice-os.exe"
	}
	return "practice-os"
}

func onPath(dir string) bool {
	for _, p := range filepath.SplitList(os.Getenv("PATH")) {
		if p != "" && samePath(p, dir) {
			return true
		}
	}
	return false
}

func samePath(a, b string) bool {
	a, b = filepath.Clean(a), filepath.Clean(b)
	if runtime.GOOS == "windows" {
		return strings.EqualFold(a, b)
	}
	return a == b
}

// pathHint returns the command that adds dir to PATH for the current OS and shell.
func pathHint(dir string) string {
	if runtime.GOOS == "windows" {
		return "  Settings > \"Edit environment variables for your account\" > Path > New > " + dir
	}
	switch filepath.Base(os.Getenv("SHELL")) {
	case "fish":
		return fmt.Sprintf("  fish_add_path %q", dir)
	case "zsh":
		return fmt.Sprintf("  echo 'export PATH=\"%s:$PATH\"' >> ~/.zshrc", dir)
	case "bash":
		profile := "~/.bashrc"
		if runtime.GOOS == "darwin" {
			profile = "~/.bash_profile"
		}
		return fmt.Sprintf("  echo 'export PATH=\"%s:$PATH\"' >> %s", dir, profile)
	default:
		return fmt.Sprintf("  echo 'export PATH=\"%s:$PATH\"' >> ~/.profile", dir)
	}
}

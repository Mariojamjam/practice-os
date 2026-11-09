# practice-os

An educational operating-system simulator written in Go. It models an OS in
layered stages: file system, I/O and RAID, security, memory, and processes.
You can drive it from a terminal UI, an interactive shell, or one-shot CLI
commands.

> **Status:** rewrite in progress.

The original Python file-system simulator is preserved at the
`legacy-python` tag.

## Install

> **Prerequisite: [Go](https://go.dev/dl/) must be installed and on your
> `PATH`** (the version in `go.mod` or newer). practice-os is built from
> source, so Go is required to install, update and run it from the
> repository.

From the repository root, on Linux, macOS or Windows:

```
go run install.go
```

This builds `practice-os` and installs it into your Go bin directory
(`GOBIN`, or `GOPATH/bin`). The installer never edits your `PATH`: if that
directory is not on it, the installer prints the exact line to add for your
OS and shell. Then use it from anywhere:

```
practice-os <command> [args] [flags]
```

| Option | Effect |
|---|---|
| `go run install.go -dir DIR` | install into `DIR` instead |
| `go run install.go -uninstall` | remove the installed binary |

The repository also ships a devcontainer with Go included: open it in VS
Code (or any Dev Containers client) and `practice-os` is installed when the
container is created.

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

## Usage

```
practice-os                    open the terminal UI (default settings)
practice-os --preset stage1    Stage 1 examples: 16 blocks of 4 KB, indexed allocation
practice-os --preset stage2    Stage 2 examples: RAID 5 of 3 HDDs, SSTF, I/O trace on
practice-os --device ssd       any setting can be overridden; see practice-os --help
```

The UI has three views (FS, I/O and RAID/SSD; `tab` switches) above a
command log and a command bar. Commands follow the reference spec, for
example:

```
mkdir /system
create /system/logs.txt --size 10KB
write_file /system/logs.txt "New record"
fs_status --details
sched --queue 98,183,37,122,14 --head 53 --alg sstf
fail_disk 2
rebuild
```

`↑`/`↓` browse the command history, `pgup`/`pgdn` scroll the log and
`ctrl+c` quits.

The repository also ships a devcontainer with Go included: open it in VS
Code (or any Dev Containers client) and `practice-os` is installed when the
container is created.

# practice-os

An educational operating-system simulator written in Go. It models an OS in
layered stages, each building on the previous ones, and makes every
mechanism visible: which block a file landed in, how the disk arm moves,
how a RAID array survives a failed disk.

| Stage | Subsystem | Status |
|---|---|---|
| 1 | File system: directory tree, CRUD, contiguous / linked (FAT) / indexed (i-node) allocation, fragmentation, compaction | done |
| 2 | I/O: request queues, FCFS / SSTF / SCAN / C-SCAN disk scheduling, SSD wear leveling, RAID 0 / 1 / 4 / 5 | done |
| 3 | Security: user and kernel mode, users and groups, permissions, encryption at rest, integrity scanning | planned |
| 4 | Memory: reserved and paged regions, address translation, page faults, page replacement | planned |
| 5 | Processes: lifecycle, syscalls, mutexes, priority + Round-Robin scheduling, metrics | planned |

The original Python file-system simulator is preserved at the
`legacy-python` tag.

## Install

> **Prerequisite: [Go](https://go.dev/dl/) installed and on your `PATH`**
> (the version in `go.mod` or newer). practice-os is built from source.

From the repository root, on Linux, macOS or Windows:

```
go run install.go
```

It installs `practice-os` into your Go bin directory. If that directory is
not on your `PATH`, the installer prints the exact line to add for your OS
and shell. `go run install.go -uninstall` removes it.

The repository also ships a devcontainer with Go included: open it in VS
Code (or any Dev Containers client) and `practice-os` is ready.

## Use

Open the terminal UI:

```
practice-os
```

Then type commands in the bar at the bottom, one at a time:

```
mkdir /docs
```

```
create /docs/a.txt --size 10KB
```

```
fs_status --details
```

Or watch a built-in scenario:

```
practice-os demo raid5-recovery
```

**[docs/commands.md](docs/commands.md)** has every command, ready-to-paste
walkthroughs (fragmentation, FAT, disk scheduling, RAID failure, SSD wear,
saved sessions) and all flags.

## Configuration

Settings come from built-in defaults, then a preset (`--preset stage1` or
`stage2`), then a YAML file, then command-line flags.
[`practice-os.example.yaml`](practice-os.example.yaml) documents every
key; copy it to `practice-os.yaml` to use it.

## Development

Only Go is needed; everything runs the same on Linux, macOS and Windows.

```
go test ./...
```

```
go tool golangci-lint run
```

Regenerate the golden files after changing output (then review the diff):

```
go test ./tests/ui/demo -update
```

```
cmd/practice-os/   main only
core/              the simulated OS: config, kernel, image, storage/, fs/
ui/                shell, render, script, demo, tui, cli
tests/             tests, mirroring core/ and ui/
```

See [docs/architecture.md](docs/architecture.md) for how the pieces fit
together.

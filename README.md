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

You can drive it from a terminal UI, an interactive shell, scripts or
one-shot commands. The original Python file-system simulator is preserved
at the `legacy-python` tag.

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
OS and shell.

| Option | Effect |
|---|---|
| `go run install.go -dir DIR` | install into `DIR` instead |
| `go run install.go -uninstall` | remove the installed binary |

Without installing, every command below also works as
`go run ./cmd/practice-os …` from the repository root.

The repository also ships a devcontainer with Go included: open it in VS
Code (or any Dev Containers client) and `practice-os` is installed when the
container is created.

## Quick start

```
practice-os --preset stage1      # terminal UI with the Stage 1 setup
practice-os --preset stage2      # RAID 5 of 3 HDDs, SSTF, I/O trace on
practice-os demo                 # list the built-in scenarios
practice-os demo disk-scheduling # SSTF vs FCFS, SCAN and C-SCAN
```

In the terminal UI, type commands in the bar at the bottom, for example:

```
mkdir /system
create /system/app.log --size 10KB
fs_status --details
sched --queue 98,183,37,122,14 --head 53 --alg sstf
```

## Ways to run it

| Command | What it does |
|---|---|
| `practice-os` | Terminal UI: FS, I/O and RAID/SSD views, a command log and a command bar |
| `practice-os -c "cmd; cmd"` | Run commands and print a transcript (`> cmd` followed by its output) |
| `practice-os shell` | Interactive shell, one command per line; `exit` or `ctrl+d` leaves. With piped input it prints only the output |
| `practice-os run FILE` | Run a script: one command per line, `#` comments |
| `practice-os demo [NAME\|all]` | List or run built-in scenarios, each with its own preset |

`-c` and `run` exit with an error status if any command failed (every
command still runs).

### Global flags

| Flag | Meaning |
|---|---|
| `--config FILE` | Configuration file (default: `./practice-os.yaml` if present) |
| `--preset NAME` | `stage1` or `stage2` |
| `--image FILE` | Load the whole state from `FILE` if it exists (its saved settings are used) and save it when the session ends |
| `--block-size`, `--blocks` | Disk geometry, e.g. `--block-size 1KB --blocks 64` |
| `--alloc` | `contiguous`, `linked` or `indexed` |
| `--device`, `--disks` | `hdd`, `ssd` or `raid`; number of RAID disks |
| `--sched`, `--head` | Disk-arm algorithm and initial head track |
| `--seed` | Random seed |
| `--ascii` | Plain ASCII instead of box-drawing characters |
| `--animation` | TUI animation speed: `off`, `slow`, `normal`, `fast` |

For example, `practice-os shell --image session.json` keeps your files,
disk heads and RAID state between sessions.

## Commands

Command names follow the reference specification.

**File system**

| Command | |
|---|---|
| `pwd`, `cd [PATH]`, `ls [PATH]`, `tree [PATH]` | Navigate; absolute and relative paths (`.`, `..`) |
| `mkdir PATH` | Create a directory (its parent must exist) |
| `create PATH --size SIZE` \| `create PATH "TEXT"` | Create a file with synthetic content of SIZE bytes, or with TEXT |
| `read_file PATH` (alias `cat`) | Show a file; binary or large files as a hexdump |
| `write_file PATH "TEXT" [--truncate]` | Append TEXT, or overwrite with `--truncate` |
| `write_file PATH --size SIZE` | Overwrite with SIZE bytes of synthetic content |
| `update PATH --size SIZE` | Truncate or extend |
| `rm [-r] PATH`, `mv SRC DST` | Remove; move or rename |
| `fs_status [--details]` | Usage summary, or the block map and fragmentation report |
| `compact` | Pack used blocks at the start of the disk |
| `set_alloc contiguous\|linked\|indexed` | Change the allocation strategy (empty disk only) |

**I/O and devices**

| Command | |
|---|---|
| `sched --queue T1,T2,… [--head N] [--alg A]` | Schedule arbitrary tracks and show the head movement |
| `io_trace on\|off` | Show each command's requests and their scheduling |
| `io_defer on\|off`, `io_queue`, `io_flush` | Keep requests queued across commands, inspect them, serve them |
| `raid_status [PATH]` | Array health and how blocks (or one file's blocks) spread over the disks |
| `fail_disk N`, `rebuild` | Simulate a disk failure; rebuild it from redundancy |
| `ssd_wear` | Erase counts per flash page and the FTL mapping |

### Terminal UI keys

`enter` runs the command · `tab` / `shift+tab` switch view · `↑` / `↓`
browse history · `pgup` / `pgdn` scroll the log · `esc` skips an animation
· `ctrl+c` quits.

## Configuration

Settings come from built-in defaults, then a preset, then a YAML file,
then command-line flags. [`practice-os.example.yaml`](practice-os.example.yaml)
documents every key; copy it to `practice-os.yaml` (ignored by git) to use
it.

## Built-in scenarios

| Name | Scenario |
|---|---|
| `directory-tree` | Creating directories and a file, then displaying the tree |
| `indexed-allocation` | Indexed allocation: the block map and fragmentation analysis |
| `disk-scheduling` | SSTF scheduling (208 tracks), compared with FCFS, SCAN and C-SCAN |
| `raid5-recovery` | RAID 5 block distribution, disk failure and XOR recovery |
| `contiguous-fragmentation` | External fragmentation blocking a file until `compact` |
| `linked-fat` | A growing file's FAT chain skipping over another file |
| `fs-io-trace` | File-system commands issuing disk requests, served by SSTF |

Each scenario's output is a golden test, so `practice-os demo NAME` prints
exactly what the tests check.

## Development

Only Go is needed; everything runs the same on Linux, macOS and Windows.

```
go build ./...                          build
go test ./...                           all tests
go test ./tests/core/fs -run TestMove   one test
go test ./tests/ui/demo -update         regenerate golden files (review the diff)
go vet ./...                            vet
go tool golangci-lint run               lint (pinned in go.mod)
go run ./cmd/practice-os                run without installing
```

```
cmd/practice-os/   main only
core/              the simulated OS: config, kernel, image, storage/, fs/
ui/                shell, render, script, demo, tui, cli
tests/             tests, mirroring core/ and ui/
```

See [docs/architecture.md](docs/architecture.md) for how the pieces fit
together.

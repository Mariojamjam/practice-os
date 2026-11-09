# Commands

Every block below can be copied and pasted as is. Blocks marked
**terminal** go in your shell; blocks marked **simulator** go in the
practice-os command bar (TUI) or in `practice-os shell`, one line at a
time.

If practice-os is not installed, replace `practice-os` with
`go run ./cmd/practice-os` and run it from the repository root.

- [Running practice-os](#running-practice-os)
- [Walkthroughs](#walkthroughs)
- [Simulator command reference](#simulator-command-reference)
- [Flags](#flags)
- [Terminal UI keys](#terminal-ui-keys)

## Running practice-os

Open the terminal UI (**terminal**):

```
practice-os
```

With the Stage 1 setup (16 blocks of 4 KB, indexed allocation):

```
practice-os --preset stage1
```

With the Stage 2 setup (RAID 5 of 3 HDDs, SSTF, I/O trace on):

```
practice-os --preset stage2
```

Run a few commands and print a transcript:

```
practice-os -c 'mkdir /docs; create /docs/a.txt --size 10KB; tree'
```

Interactive shell (leave with `exit` or `ctrl+d`):

```
practice-os shell
```

Run a script file (one command per line, `#` comments):

```
practice-os run scenario.txt
```

Keep the state between sessions in a file:

```
practice-os shell --image session.json
```

List the built-in scenarios, then run one or all:

```
practice-os demo
```

```
practice-os demo disk-scheduling
```

```
practice-os demo all
```

## Walkthroughs

Each walkthrough is one **terminal** line. To follow it step by step,
open the TUI with the same flags and type the commands between quotes one
at a time.

### Files and the block map

```
practice-os --preset stage1 -c 'mkdir /system; mkdir /system/logs; create /system/logs/app.log --size 10KB; tree; fs_status --details'
```

The map shows each block's role; the last data block of `app.log` holds
2048 of 4096 bytes: internal fragmentation.

### Reading, writing and moving

```
practice-os -c 'mkdir /notes; create /notes/todo.txt "buy disks"; write_file /notes/todo.txt " and a fan"; cat /notes/todo.txt; mv /notes/todo.txt /todo.txt; ls /; rm -r /notes; tree'
```

### External fragmentation and compaction

```
practice-os --alloc contiguous -c 'create /a --size 8KB; create /b --size 12KB; create /c --size 8KB; rm /b; create /big --size 20KB; fs_status --details; compact; create /big --size 20KB; fs_status'
```

The first `create /big` fails: there is enough free space, but not in one
run. `compact` packs the files together and the second one succeeds. The
run ends with `Error: 1 of 9 commands failed`, as intended.

### Linked allocation (FAT)

```
practice-os --alloc linked -c 'create /report.txt --size 6KB; create /notes.txt "first line"; write_file /report.txt --size 14KB; fs_status --details'
```

`report.txt` grows past `notes.txt`: the map shows its FAT chain jumping
over it (`next: 04`, `next: 06`).

### Disk-arm scheduling

```
practice-os --blocks 200 -c 'sched --queue 98,183,37,122,14 --head 53 --alg sstf; sched --queue 98,183,37,122,14 --head 53 --alg fcfs; sched --queue 98,183,37,122,14 --head 53 --alg scan; sched --queue 98,183,37,122,14 --head 53 --alg cscan'
```

SSTF moves the head 208 tracks; FCFS 469, SCAN 331, C-SCAN 382.

### Disk requests from file operations

```
practice-os -c 'io_trace on; mkdir /logs; create /logs/app.log --size 10KB; write_file /logs/app.log "New record"'
```

Requests from several commands, served together:

```
practice-os -c 'io_defer on; create /a.txt "first"; create /b.txt "second"; io_queue; io_flush'
```

### RAID 5: failure and recovery

```
practice-os --preset stage2 -c 'io_trace off; mkdir /data; create /data/sheet.csv --size 8KB; raid_status /data/sheet.csv; fail_disk 2; read_file /data/sheet.csv; rebuild; raid_status'
```

After `fail_disk 2` the file is still readable: each lost block is
rebuilt by XOR of the other two disks.

### SSD wear leveling

```
practice-os --device ssd -c 'create /log --size 4KB; write_file /log --size 4KB; write_file /log --size 4KB; write_file /log --size 4KB; ssd_wear'
```

Each rewrite goes to a fresh flash page and the old one is erased; the
erases spread across the pages.

### Saving a session

```
practice-os --preset stage2 --image session.json -c 'mkdir /kept; create /kept/f "still here"; fail_disk 2'
```

```
practice-os --image session.json -c 'cat /kept/f; raid_status'
```

The second run starts from the saved state, failed disk included.

## Simulator command reference

Paths can be absolute (`/a/b`) or relative to the working directory
(`b`, `../a`). Sizes accept `B`, `KB`, `KiB`, `MB`, `MiB` (`KB` = 1024
bytes). Several commands can share a line, separated by `;`.

### Navigation

| Command | Description |
|---|---|
| `pwd` | Print the working directory |
| `cd [PATH]` | Change the working directory (`/` by default) |
| `ls [PATH]` | List a directory |
| `tree [PATH]` | Show the directory tree |

```
cd /system/logs
```

### Files and directories

| Command | Description |
|---|---|
| `mkdir PATH` | Create a directory; its parent must exist |
| `create PATH --size SIZE` | Create a file of SIZE bytes of synthetic content (A–Z repeated) |
| `create PATH "TEXT"` | Create a file containing TEXT |
| `read_file PATH`, `cat PATH` | Show a file; binary or large files as a hexdump |
| `write_file PATH "TEXT"` | Append TEXT |
| `write_file PATH "TEXT" --truncate` | Replace the content with TEXT |
| `write_file PATH --size SIZE` | Replace the content with SIZE bytes of synthetic content |
| `update PATH --size SIZE` | Truncate or extend to SIZE |
| `rm PATH` | Remove a file or an empty directory |
| `rm -r PATH` | Remove a directory and everything in it |
| `mv SRC DST` | Move or rename; into DST if it is a directory |

```
create /hello.txt "Hello, disk"
```

```
write_file /hello.txt " and blocks" --truncate
```

### Disk and allocation

| Command | Description |
|---|---|
| `fs_status` | Usage, fragmentation and whether compaction is needed |
| `fs_status --details` | Block-by-block map and per-file fragmentation report |
| `compact` | Pack used blocks at the start of the disk |
| `set_alloc contiguous` / `linked` / `indexed` | Change the allocation strategy (empty disk only; formats it) |

```
fs_status --details
```

### I/O and scheduling

| Command | Description |
|---|---|
| `sched --queue T1,T2,…` | Schedule tracks with the configured algorithm and head |
| `sched --queue T1,T2,… --head N --alg A` | Choose the head and the algorithm (`fcfs`, `sstf`, `scan`, `cscan`) |
| `io_trace on` / `off` | Show each command's disk requests and their scheduling |
| `io_defer on` / `off` | Keep requests queued across commands |
| `io_queue` | Show the queued requests |
| `io_flush` | Serve the queued requests |

```
sched --queue 98,183,37,122,14 --head 53 --alg sstf
```

### RAID and SSD

| Command | Description |
|---|---|
| `raid_status` | Array health and how used blocks spread over the disks |
| `raid_status PATH` | The same, for one file's blocks |
| `fail_disk N` | Fail disk N (1-based): its contents are wiped |
| `rebuild` | Restore failed disks from the others |
| `ssd_wear` | Erases and writes per flash page, and the FTL mapping |

```
fail_disk 2
```

## Flags

Flags go before or after the subcommand and override the configuration
file (`./practice-os.yaml` or `--config FILE`).

| Flag | Values |
|---|---|
| `--preset` | `stage1`, `stage2` |
| `--config` | a YAML file; see `practice-os.example.yaml` |
| `--image` | a state file: loaded if it exists, saved when the session ends |
| `--block-size` | `512B` … `64KB`, a power of two |
| `--blocks` | blocks per disk |
| `--alloc` | `contiguous`, `linked`, `indexed` |
| `--device` | `hdd`, `ssd`, `raid` |
| `--disks` | disks in the RAID array |
| `--sched` | `fcfs`, `sstf`, `scan`, `cscan` |
| `--head` | initial head track |
| `--seed` | random seed |
| `--ascii` | plain ASCII drawing |
| `--animation` | `off`, `slow`, `normal`, `fast` |

```
practice-os --device raid --disks 4 --sched cscan --animation slow
```

## Terminal UI keys

| Key | Action |
|---|---|
| `enter` | Run the command |
| `tab` / `shift+tab` | Next / previous view (FS, I/O, RAID/SSD) |
| `↑` / `↓` | Command history |
| `pgup` / `pgdn` | Scroll the log |
| `esc` | Skip the current animation |
| `ctrl+c` | Quit |

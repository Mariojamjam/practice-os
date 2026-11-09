# Architecture

practice-os is split into the simulated operating system (`core/`) and
the interfaces that talk to the user (`ui/`). The core never imports the
interfaces, so the same simulation runs behind the terminal UI, the shell,
scripts and tests.

```
             ┌──────────────────────── ui/ ────────────────────────┐
  user ────► │ cli ─► tui · shell REPL · run · -c · demo           │
             │          │                                          │
             │          ▼                                          │
             │   script ─► shell ── typed results ──► render       │
             └──────────┬──────────────────────────────────────────┘
                        │ commands
             ┌──────────▼──────────────── core/ ───────────────────┐
             │ kernel  (built from config; restored by image)      │
             │   │                                                 │
             │   ▼                                                 │
             │ fs ─ alloc ─ diag                (Stage 1)          │
             │   │  device.Device                                  │
             │   ▼                                                 │
             │ storage: hdd · ssd · raid ─ blockio · sched ─ disk  │
             │                                   (Stage 2)         │
             └─────────────────────────────────────────────────────┘
```

## Packages

| Package | Responsibility |
|---|---|
| `core/config` | Settings, embedded presets, YAML loading, validation |
| `core/kernel` | Builds the device and file system from a config; flushes, inspects |
| `core/image` | Saves and loads the whole state as versioned JSON |
| `core/storage/disk` | Fixed-size blocks holding real bytes |
| `core/storage/device` | The `Device` interface everything above storage uses |
| `core/storage/blockio` | I/O requests, queues, flush reports, RAID events |
| `core/storage/sched` | FCFS, SSTF, SCAN, C-SCAN as pure functions |
| `core/storage/hdd` | Tracks and a scheduled head |
| `core/storage/ssd` | Flash pages, FTL, wear leveling |
| `core/storage/raid` | RAID 0/1/4/5 over member devices |
| `core/fs` | Directory tree, paths, CRUD, compaction |
| `core/fs/alloc` | Contiguous, linked (FAT) and indexed (i-node) allocation |
| `core/fs/diag` | Block map, fragmentation, compaction needs |
| `ui/shell` | The single command interpreter; returns typed results |
| `ui/render` | Results and I/O as text |
| `ui/script` | Runs command sequences into transcripts |
| `ui/demo` | Embedded scenarios (the reference examples and more) |
| `ui/tui` | Bubble Tea interface |
| `ui/cli` | Cobra commands and flags |

## Dependency rules

- `core` never imports `ui`.
- Blocks depend only downwards: `kernel → fs → storage`. Future stages
  follow the same rule (`process → memory → storage`, `security → fs`).
- Inside a block, siblings share interfaces (`device.Device`,
  `blockio.Flusher`) rather than importing each other.
- Only `core/kernel` knows every block and wires them together.
- Every command goes through `ui/shell`; nothing else parses commands.
- Formatting lives in `ui/render` (text) and `ui/tui` (visuals); core types
  only expose data.

## The file system on disk

Everything except a small controller state (free-block bitmap, root block,
working directory) lives in device blocks, so RAID, SSD remapping and
future encryption see real metadata.

- **Directory block:** a header (`PDIR`, entry count) followed by 64-byte
  entries: name (up to 44 bytes), kind, size, and a `Ref` that the
  allocation strategy interprets. A directory occupies one block.
- **Contiguous:** the entry stores the first block and the length. Files
  are placed first-fit and relocated when they cannot grow in place; when
  free space exists but no run is large enough, allocation fails with
  external fragmentation.
- **Linked (FAT):** the table fills the first blocks of the disk, one
  `uint32` per block (free, end of chain, reserved, or next block). The
  entry stores the first block.
- **Indexed (i-node):** each file has an inode block (`INOD`, size, block
  count, then one `uint32` pointer per data block); with indexed
  allocation a directory's block is its inode. The entry stores the inode
  block. The index is single-level.

`diag` walks this structure to classify every block and measure internal
fragmentation (unused bytes in each file's last block) and external
fragmentation (free space outside the largest free run, which only
contiguous allocation suffers from).

## The I/O model

Devices perform every read and write immediately, so data is always
correct, and record each one as a request in a queue. A flush serves the
queue and reports how:

- **HDD:** the configured algorithm orders the requests by track; the
  head's track and direction persist between flushes. SCAN and C-SCAN go
  to the disk edge before turning or wrapping, and C-SCAN's jump counts as
  movement.
- **SSD:** no head and no seek. Writes go to the least-worn free page and
  the old page is erased; 12.5% spare pages make room.
- **RAID:** each member keeps its own queue (and head). The array reports
  events: degraded reads rebuilt by XOR or read from a mirror, degraded
  writes. RAID 4 keeps parity on the last disk; RAID 5 rotates it to disk
  `N-1-(s mod N)` for stripe `s`.

The shell flushes when each command ends unless `io_defer` is on.
Interfaces read the file system through `kernel.Inspect`, which mutes
request recording, so drawing the state never changes it.

## State images

`core/image` writes the configuration, the I/O settings, the file system's
controller state and each device's state (blocks in base64, heads, queues,
SSD wear, RAID health) as JSON with a `version` field. Loading rebuilds
the kernel from the saved configuration, restores every device and mounts
the file system without writing to it.

## Tests

Tests live in `tests/`, mirroring `core/` and `ui/`, as external packages
that use only exported APIs; internal details are checked through what can
be observed, such as bytes on disk or rendered output. Each built-in
scenario is also a golden test: its transcript must match
`tests/ui/demo/testdata/NAME.golden` byte for byte.

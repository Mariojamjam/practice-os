package shell

import (
	"errors"
	"fmt"
	"slices"
	"strconv"

	"github.com/spf13/pflag"

	"github.com/Mariojamjam/practice-os/core/fs/diag"
	"github.com/Mariojamjam/practice-os/core/storage/raid"
	"github.com/Mariojamjam/practice-os/core/storage/sched"
)

// ioCommands are the I/O, scheduling, RAID and SSD commands (Stage 2).
var ioCommands = map[string]command{
	"sched": {
		usage: "sched --queue T1,T2,... [--head TRACK] [--alg fcfs|sstf|scan|cscan]",
		flags: func(fl *pflag.FlagSet) {
			fl.IntSlice("queue", nil, "pending tracks, in arrival order")
			fl.Int("head", 0, "head track (default: io.head)")
			fl.String("alg", "", "algorithm (default: io.scheduler)")
		},
		run: func(s *Shell, fl *pflag.FlagSet, _ []string) (Result, error) {
			cfg := s.k.Config
			queue, _ := fl.GetIntSlice("queue")
			if len(queue) == 0 {
				return nil, errors.New("--queue is required, e.g. --queue 98,183,37")
			}
			head := cfg.IO.Head
			if fl.Changed("head") {
				head, _ = fl.GetInt("head")
			}
			alg := sched.Algorithm(cfg.IO.Scheduler)
			if fl.Changed("alg") {
				name, _ := fl.GetString("alg")
				alg = sched.Algorithm(name)
			}
			dir, err := sched.ParseDirection(cfg.IO.Direction)
			if err != nil {
				return nil, err
			}
			tracks := cfg.Disk.TrackCount()
			res, err := sched.Schedule(alg, head, dir, queue, tracks)
			if err != nil {
				return nil, err
			}
			return SchedResult{Result: res, Tracks: tracks}, nil
		},
	},
	"io_defer": {
		usage: "io_defer on|off",
		args:  [2]int{1, 1},
		run: func(s *Shell, _ *pflag.FlagSet, args []string) (Result, error) {
			on, err := onOff(args[0])
			if err != nil {
				return nil, err
			}
			s.k.Defer = on
			if on {
				return MessageResult{Text: "I/O requests now stay queued until io_flush."}, nil
			}
			return MessageResult{Text: "I/O requests are now served at the end of each command."}, nil
		},
	},
	"io_trace": {
		usage: "io_trace on|off",
		args:  [2]int{1, 1},
		run: func(s *Shell, _ *pflag.FlagSet, args []string) (Result, error) {
			on, err := onOff(args[0])
			if err != nil {
				return nil, err
			}
			s.k.Trace = on
			if on {
				return MessageResult{Text: "I/O trace on: each command shows its requests and their scheduling."}, nil
			}
			return MessageResult{Text: "I/O trace off."}, nil
		},
	},
	"io_flush": {
		usage: "io_flush",
		run: func(s *Shell, _ *pflag.FlagSet, _ []string) (Result, error) {
			return IOResult{Flushes: s.k.Flush()}, nil
		},
	},
	"io_queue": {
		usage: "io_queue",
		run: func(s *Shell, _ *pflag.FlagSet, _ []string) (Result, error) {
			return IOResult{Pending: true, Flushes: s.k.Pending()}, nil
		},
	},
	"raid_status": {
		usage: "raid_status [PATH]",
		args:  [2]int{0, 1},
		run: func(s *Shell, _ *pflag.FlagSet, args []string) (Result, error) {
			r, err := array(s)
			if err != nil {
				return nil, err
			}
			report, err := diag.Analyze(s.k.FS)
			if err != nil {
				return nil, err
			}
			res := RAIDStatusResult{
				Name: r.Name(), Level: r.Level(), BlockSize: r.BlockSize(),
				Capacity: r.BlockCount(), Report: report,
			}
			for i, d := range r.Disks() {
				res.Disks = append(res.Disks, DiskState{Name: diskName(d, i), Failed: r.Failed(i)})
			}
			var blocks []int64
			if len(args) == 1 {
				n, err := s.k.FS.Stat(args[0])
				if err != nil {
					return nil, err
				}
				res.Path = n.Path
				if blocks, err = s.k.FS.NodeBlocks(n); err != nil {
					return nil, err
				}
			} else {
				for _, b := range report.Blocks {
					if b.Kind != diag.KindFree {
						blocks = append(blocks, b.Index)
					}
				}
			}
			var stripes []int64
			for _, b := range blocks {
				if st := r.StripeOf(b); !slices.Contains(stripes, st) {
					stripes = append(stripes, st)
				}
			}
			slices.Sort(stripes)
			for _, st := range stripes {
				res.Stripes = append(res.Stripes, r.Stripe(st))
			}
			return res, nil
		},
	},
	"fail_disk": {
		usage: "fail_disk N",
		args:  [2]int{1, 1},
		run: func(s *Shell, _ *pflag.FlagSet, args []string) (Result, error) {
			r, err := array(s)
			if err != nil {
				return nil, err
			}
			n, err := strconv.Atoi(args[0])
			if err != nil {
				return nil, fmt.Errorf("disk number %q: %w", args[0], ErrUsage)
			}
			if err := r.Fail(n - 1); err != nil {
				return nil, err
			}
			return FailResult{Array: r.Name(), Level: r.Level(), Disk: n}, nil
		},
	},
	"rebuild": {
		usage: "rebuild",
		run: func(s *Shell, _ *pflag.FlagSet, _ []string) (Result, error) {
			r, err := array(s)
			if err != nil {
				return nil, err
			}
			rebuilt, err := r.Rebuild()
			if err != nil {
				return nil, err
			}
			return RebuildResult{Array: r.Name(), Rebuilt: rebuilt}, nil
		},
	},
	"ssd_wear": {
		usage: "ssd_wear",
		run: func(s *Shell, _ *pflag.FlagSet, _ []string) (Result, error) {
			ssds := s.k.SSDs()
			if len(ssds) == 0 {
				return nil, fmt.Errorf("no SSD in use (io.device is %s)", s.k.Config.IO.Device)
			}
			var res WearResult
			for _, d := range ssds {
				res.Wear = append(res.Wear, d.Wear())
			}
			return res, nil
		},
	},
}

func array(s *Shell) (*raid.RAID, error) {
	r, ok := s.k.RAID()
	if !ok {
		return nil, fmt.Errorf("no RAID array in use (io.device is %s)", s.k.Config.IO.Device)
	}
	return r, nil
}

func diskName(d any, i int) string {
	if n, ok := d.(interface{ Name() string }); ok {
		return n.Name()
	}
	return fmt.Sprintf("Disk %d", i+1)
}

func onOff(v string) (bool, error) {
	switch v {
	case "on":
		return true, nil
	case "off":
		return false, nil
	}
	return false, fmt.Errorf("%w: expected on or off, got %q", ErrUsage, v)
}

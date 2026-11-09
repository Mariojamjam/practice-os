// Package shell is the single command interpreter of the simulator. The
// REPL, scripts, demos and the TUI all execute commands through it and get
// typed results back.
package shell

import (
	"errors"
	"fmt"
	"io"
	"sort"

	"github.com/spf13/pflag"

	"github.com/Mariojamjam/practice-os/internal/blockio"
	"github.com/Mariojamjam/practice-os/internal/kernel"
)

var (
	// ErrUnknownCommand is returned for a command name that does not exist.
	ErrUnknownCommand = errors.New("unknown command")
	// ErrUsage is returned when a command's arguments are wrong.
	ErrUsage = errors.New("invalid arguments")
)

// Shell executes command lines against a kernel.
type Shell struct {
	k       *kernel.Kernel
	lastIO  []blockio.Flush
	flushed []blockio.Flush
}

// New returns a shell bound to k.
func New(k *kernel.Kernel) *Shell {
	return &Shell{k: k}
}

// Kernel returns the kernel the shell operates on.
func (s *Shell) Kernel() *kernel.Kernel { return s.k }

// command is one shell command.
type command struct {
	usage string
	// flags declares the command's flags; nil means none.
	flags func(*pflag.FlagSet)
	// args is the accepted number of positional arguments: [min, max].
	args [2]int
	run  func(s *Shell, fl *pflag.FlagSet, args []string) (Result, error)
}

// commands holds every shell command, by name.
var commands = merge(fsCommands, ioCommands)

func merge(sets ...map[string]command) map[string]command {
	out := map[string]command{}
	for _, set := range sets {
		for name, c := range set {
			out[name] = c
		}
	}
	return out
}

// aliases maps alternative names to command names.
var aliases = map[string]string{
	"cat": "read_file",
}

// Commands returns the names of all commands, sorted.
func Commands() []string {
	names := make([]string, 0, len(commands))
	for name := range commands {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

// LastIO returns the I/O of the last Exec: every flush when the kernel's
// trace is on, otherwise only RAID events (failures are always worth
// showing). It is empty while requests are deferred.
func (s *Shell) LastIO() []blockio.Flush { return s.lastIO }

// Flushed returns every flush of the last Exec, whatever the trace
// setting: what each device served when the command ended (or, for
// io_flush, what the command itself served).
func (s *Shell) Flushed() []blockio.Flush { return s.flushed }

// Exec runs one command line. Blank lines and comments return (nil, nil);
// so do commands that succeed silently, like mkdir.
//
// Unless the kernel defers I/O, the requests the command issued are
// flushed when it ends; see LastIO.
func (s *Shell) Exec(line string) (Result, error) {
	s.lastIO, s.flushed = nil, nil
	res, err := s.exec(line)
	if !s.k.Defer {
		s.flushed = s.k.Flush()
		s.lastIO = s.visibleIO(s.flushed)
	}
	if r, ok := res.(IOResult); ok && !r.Pending {
		s.flushed = append(r.Flushes, s.flushed...)
	}
	return res, err
}

func (s *Shell) visibleIO(flushes []blockio.Flush) []blockio.Flush {
	if s.k.Trace {
		return flushes
	}
	var events []blockio.Flush
	for _, f := range flushes {
		if len(f.Events) > 0 {
			events = append(events, f)
		}
	}
	return events
}

func (s *Shell) exec(line string) (Result, error) {
	words, err := Tokenize(line)
	if err != nil || len(words) == 0 {
		return nil, err
	}
	name := words[0]
	if target, ok := aliases[name]; ok {
		name = target
	}
	cmd, ok := commands[name]
	if !ok {
		return nil, fmt.Errorf("%w: %s", ErrUnknownCommand, words[0])
	}

	fl := pflag.NewFlagSet(name, pflag.ContinueOnError)
	fl.SetOutput(io.Discard)
	if cmd.flags != nil {
		cmd.flags(fl)
	}
	if err := fl.Parse(words[1:]); err != nil {
		return nil, usageError(cmd, err)
	}
	args := fl.Args()
	if len(args) < cmd.args[0] || len(args) > cmd.args[1] {
		return nil, usageError(cmd, nil)
	}
	return cmd.run(s, fl, args)
}

func usageError(cmd command, cause error) error {
	if cause != nil {
		return fmt.Errorf("%w: %w (usage: %s)", ErrUsage, cause, cmd.usage)
	}
	return fmt.Errorf("%w (usage: %s)", ErrUsage, cmd.usage)
}

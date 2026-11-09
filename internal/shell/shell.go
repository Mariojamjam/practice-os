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
	k *kernel.Kernel
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

// Exec runs one command line. Blank lines and comments return (nil, nil);
// so do commands that succeed silently, like mkdir.
func (s *Shell) Exec(line string) (Result, error) {
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

package cli

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/spf13/cobra"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/ui/demo"
	"github.com/Mariojamjam/practice-os/ui/render"
	"github.com/Mariojamjam/practice-os/ui/script"
	"github.com/Mariojamjam/practice-os/ui/shell"
)

func newShellCmd(f *flags) *cobra.Command {
	return &cobra.Command{
		Use:   "shell",
		Short: "Interactive command shell (one command per line; exit or ctrl+d to leave)",
		Args:  cobra.NoArgs,
		RunE: func(cmd *cobra.Command, _ []string) error {
			return session(cmd, f, func(k *kernel.Kernel) error {
				return repl(cmd, k)
			})
		},
	}
}

// repl reads commands line by line. With a terminal it prints a banner and
// a prompt showing the working directory; with piped input it only prints
// command output.
func repl(cmd *cobra.Command, k *kernel.Kernel) error {
	in, out := cmd.InOrStdin(), &printer{w: cmd.OutOrStdout()}
	interactive := isTerminal(in)
	sh := shell.New(k)
	opts := render.Options{ASCII: k.Config.UI.ASCII}
	if interactive {
		out.printf("practice-os shell. Commands follow the reference spec (mkdir, create, fs_status…);\n")
		out.printf("separate several with ';'. Type exit or press ctrl+d to leave.\n")
	}
	sc := bufio.NewScanner(in)
	for {
		if interactive {
			out.printf("%s> ", k.FS.Getwd())
		}
		if !sc.Scan() {
			break
		}
		line := strings.TrimSpace(sc.Text())
		if line == "exit" || line == "quit" {
			break
		}
		cmds, err := shell.SplitCommands(line)
		if err != nil {
			out.printf("%s", render.Error(err))
			continue
		}
		for _, c := range cmds {
			text, _ := script.Output(sh, c, opts)
			out.printf("%s", text)
		}
	}
	if interactive {
		out.printf("\n")
	}
	if err := sc.Err(); err != nil {
		return err
	}
	return out.err
}

func newRunCmd(f *flags) *cobra.Command {
	return &cobra.Command{
		Use:   "run FILE",
		Short: "Run a script of commands (one per line, # comments) and print a transcript",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			src, err := os.ReadFile(args[0])
			if err != nil {
				return err
			}
			return runCommands(cmd, f, script.Lines(string(src)))
		},
	}
}

func newDemoCmd(f *flags) *cobra.Command {
	return &cobra.Command{
		Use:   "demo [NAME|all]",
		Short: "Run the built-in scenarios (list them without NAME)",
		Long: "Runs a built-in scenario with its own preset and prints its transcript.\n" +
			"Configuration flags and --image are ignored; --ascii applies.",
		Args: cobra.MaximumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			out := &printer{w: cmd.OutOrStdout()}
			if len(args) == 0 {
				out.printf("Built-in scenarios (run with: practice-os demo NAME, or all):\n")
				for _, d := range demo.All() {
					out.printf("  %-26s %s [preset %s]\n", d.Name, d.Title, d.Preset)
				}
				return out.err
			}
			demos := demo.All()
			if args[0] != "all" {
				d, err := demo.Find(args[0])
				if err != nil {
					return err
				}
				demos = []demo.Demo{d}
			}
			for i, d := range demos {
				if i > 0 {
					out.printf("\n")
				}
				if err := runDemo(cmd, f, d); err != nil {
					return err
				}
			}
			return out.err
		},
	}
}

// runDemo prints a scenario's header and transcript. Errors inside the
// scenario are part of the demonstration, so they do not fail the command.
func runDemo(cmd *cobra.Command, f *flags, d demo.Demo) error {
	cfg, err := config.Load(config.Options{NoFile: true, Overrides: config.Overrides{Preset: &d.Preset}})
	if err != nil {
		return err
	}
	k, err := kernel.New(cfg)
	if err != nil {
		return err
	}
	out := &printer{w: cmd.OutOrStdout()}
	out.printf("=== %s: %s [preset %s] ===\n\n", d.Name, d.Title, d.Preset)
	if out.err != nil {
		return out.err
	}
	_, err = script.Run(shell.New(k), d.Commands(), out.w, render.Options{ASCII: f.ascii})
	return err
}

// printer writes formatted text and keeps the first write error.
type printer struct {
	w   io.Writer
	err error
}

func (p *printer) printf(format string, a ...any) {
	if p.err == nil {
		_, p.err = fmt.Fprintf(p.w, format, a...)
	}
}

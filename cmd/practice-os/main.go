// Command practice-os is an educational operating-system simulator.
package main

import (
	"os"

	"github.com/spf13/cobra"
)

func main() {
	if err := newRootCmd().Execute(); err != nil {
		os.Exit(1)
	}
}

func newRootCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "practice-os <command> [args] [flags]",
		Short: "An educational operating-system simulator",
		Long: "practice-os simulates the main subsystems of an operating system:\n" +
			"file system, I/O and RAID, security, memory and processes.",
		SilenceUsage: true,
		RunE: func(cmd *cobra.Command, _ []string) error {
			return cmd.Help()
		},
	}
}

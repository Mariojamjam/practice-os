// Command practice-os is an educational operating-system simulator.
package main

import (
	"os"

	"github.com/Mariojamjam/practice-os/ui/cli"
)

func main() {
	if err := cli.NewRootCmd().Execute(); err != nil {
		os.Exit(1)
	}
}

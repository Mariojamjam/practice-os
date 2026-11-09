package config

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
)

// Size units. As in the reference spec, KB means 1024 bytes.
const (
	KB int64 = 1024
	MB int64 = 1024 * KB
)

var unitFactors = map[string]int64{
	"":    1,
	"B":   1,
	"KB":  KB,
	"KIB": KB,
	"MB":  MB,
	"MIB": MB,
}

// ErrInvalidSize is returned by ParseSize for malformed input.
var ErrInvalidSize = errors.New("invalid size")

// ParseSize parses a human size such as "10KB", "4 KiB", "512B" or "2048".
// Units are case-insensitive; KB and KiB both mean 1024 bytes.
func ParseSize(s string) (int64, error) {
	t := strings.TrimSpace(s)
	i := 0
	for i < len(t) && t[i] >= '0' && t[i] <= '9' {
		i++
	}
	if i == 0 {
		return 0, fmt.Errorf("%w: %q", ErrInvalidSize, s)
	}
	n, err := strconv.ParseInt(t[:i], 10, 64)
	if err != nil {
		return 0, fmt.Errorf("%w: %q", ErrInvalidSize, s)
	}
	factor, ok := unitFactors[strings.ToUpper(strings.TrimSpace(t[i:]))]
	if !ok {
		return 0, fmt.Errorf("%w: %q (units: B, KB, KiB, MB, MiB)", ErrInvalidSize, s)
	}
	if n > (1<<62)/factor {
		return 0, fmt.Errorf("%w: %q is too large", ErrInvalidSize, s)
	}
	return n * factor, nil
}

// FormatSize formats a byte count using the largest unit that divides it
// exactly: "10 KB", "4 MB", "1500 B".
func FormatSize(n int64) string {
	switch {
	case n >= MB && n%MB == 0:
		return fmt.Sprintf("%d MB", n/MB)
	case n >= KB && n%KB == 0:
		return fmt.Sprintf("%d KB", n/KB)
	default:
		return fmt.Sprintf("%d B", n)
	}
}

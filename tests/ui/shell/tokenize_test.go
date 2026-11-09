package shell_test

import (
	"errors"
	"reflect"
	"testing"

	"github.com/Mariojamjam/practice-os/ui/shell"
)

func TestTokenize(t *testing.T) {
	tests := []struct {
		in   string
		want []string
	}{
		{"", nil},
		{"   ", nil},
		{"# a comment", nil},
		{"  # indented comment", nil},
		{"mkdir /a", []string{"mkdir", "/a"}},
		{"  ls\t /a  ", []string{"ls", "/a"}},
		{`write_file /f "Hello, world"`, []string{"write_file", "/f", "Hello, world"}},
		{`echo 'it''s'`, []string{"echo", "its"}},
		{`echo 'a "b" \n'`, []string{"echo", `a "b" \n`}},
		{`echo "say \"hi\" \\ ok"`, []string{"echo", `say "hi" \ ok`}},
		{`echo a\ b`, []string{"echo", "a b"}},
		{`echo ""`, []string{"echo", ""}},
		{`echo a#b`, []string{"echo", "a#b"}},
	}
	for _, tt := range tests {
		got, err := shell.Tokenize(tt.in)
		if err != nil || !reflect.DeepEqual(got, tt.want) {
			t.Errorf("shell.Tokenize(%q) = %q, %v; want %q", tt.in, got, err, tt.want)
		}
	}
	for _, bad := range []string{`echo "open`, `echo 'open`, `echo trailing\`} {
		if _, err := shell.Tokenize(bad); !errors.Is(err, shell.ErrSyntax) {
			t.Errorf("shell.Tokenize(%q) error = %v", bad, err)
		}
	}
}

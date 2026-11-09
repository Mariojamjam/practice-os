package shell

import (
	"errors"
	"strings"
)

// ErrSyntax is returned for malformed command lines.
var ErrSyntax = errors.New("syntax error")

// Tokenize splits a command line into words. Single quotes keep everything
// literally; double quotes allow \" and \\ escapes; outside quotes a
// backslash escapes the next character. A line whose first non-blank
// character is # is a comment and yields no words.
func Tokenize(line string) ([]string, error) {
	if strings.HasPrefix(strings.TrimSpace(line), "#") {
		return nil, nil
	}
	var (
		words   []string
		cur     strings.Builder
		inWord  bool
		quote   rune
		escaped bool
	)
	for _, r := range line {
		switch {
		case escaped:
			cur.WriteRune(r)
			escaped = false
		case quote == '\'':
			if r == '\'' {
				quote = 0
			} else {
				cur.WriteRune(r)
			}
		case quote == '"':
			switch r {
			case '"':
				quote = 0
			case '\\':
				escaped = true
			default:
				cur.WriteRune(r)
			}
		case r == '\'' || r == '"':
			quote, inWord = r, true
		case r == '\\':
			escaped, inWord = true, true
		case r == ' ' || r == '\t':
			if inWord {
				words = append(words, cur.String())
				cur.Reset()
				inWord = false
			}
		default:
			cur.WriteRune(r)
			inWord = true
		}
	}
	switch {
	case quote != 0:
		return nil, errors.Join(ErrSyntax, errors.New("unterminated quote"))
	case escaped:
		return nil, errors.Join(ErrSyntax, errors.New("trailing backslash"))
	}
	if inWord {
		words = append(words, cur.String())
	}
	return words, nil
}

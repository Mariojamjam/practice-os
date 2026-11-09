package blockio_test

import (
	"reflect"
	"testing"

	"github.com/Mariojamjam/practice-os/core/storage/blockio"
)

func TestQueue(t *testing.T) {
	var q blockio.Queue
	reqs := []blockio.Request{
		{Op: blockio.Read, Block: 4, Track: 4},
		{Op: blockio.Write, Block: 1, Track: 1},
	}
	for _, r := range reqs {
		q.Add(r)
	}
	pending := q.Pending()
	if q.Len() != 2 || !reflect.DeepEqual(pending, reqs) {
		t.Fatalf("pending = %v", pending)
	}
	pending[0].Block = 99
	if q.Pending()[0].Block != 4 {
		t.Error("Pending must return a copy")
	}
	if got := q.Drain(); !reflect.DeepEqual(got, reqs) || q.Len() != 0 {
		t.Errorf("drain = %v, left %d", got, q.Len())
	}
	if blockio.Read.String() != "R" || blockio.Write.String() != "W" {
		t.Error("Op.String")
	}
}

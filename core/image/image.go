// Package image saves the whole simulator state to a versioned JSON file
// and loads it back, so a session can continue later: configuration,
// every disk's blocks (base64), heads, queues, SSD wear, RAID health and
// the file system's controller state.
package image

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"github.com/Mariojamjam/practice-os/core/config"
	"github.com/Mariojamjam/practice-os/core/fs"
	"github.com/Mariojamjam/practice-os/core/kernel"
	"github.com/Mariojamjam/practice-os/core/storage/device"
	"github.com/Mariojamjam/practice-os/core/storage/hdd"
	"github.com/Mariojamjam/practice-os/core/storage/raid"
	"github.com/Mariojamjam/practice-os/core/storage/ssd"
)

// Version is the image format version.
const Version = 1

// ErrInvalid reports an image that cannot be loaded.
var ErrInvalid = errors.New("invalid state image")

// Image is the JSON document.
type Image struct {
	Version int           `json:"version"`
	Config  config.Config `json:"config"`
	Defer   bool          `json:"defer"`
	Trace   bool          `json:"trace"`
	FS      fs.State      `json:"fs"`
	Device  Device        `json:"device"`
}

// Device is the saved state of one device; a RAID holds its disks.
type Device struct {
	Kind  string      `json:"kind"`
	HDD   *hdd.State  `json:"hdd,omitempty"`
	SSD   *ssd.State  `json:"ssd,omitempty"`
	RAID  *raid.State `json:"raid,omitempty"`
	Disks []Device    `json:"disks,omitempty"`
}

// Save writes the kernel's state as JSON.
func Save(k *kernel.Kernel, w io.Writer) error {
	dev, err := saveDevice(k.Device)
	if err != nil {
		return err
	}
	img := Image{
		Version: Version, Config: k.Config, Defer: k.Defer, Trace: k.Trace,
		FS: k.FS.State(), Device: dev,
	}
	enc := json.NewEncoder(w)
	enc.SetIndent("", " ")
	return enc.Encode(img)
}

// Load reads a JSON image and rebuilds the kernel it describes.
func Load(r io.Reader) (*kernel.Kernel, error) {
	var img Image
	if err := json.NewDecoder(r).Decode(&img); err != nil {
		return nil, fmt.Errorf("%w: %w", ErrInvalid, err)
	}
	if img.Version != Version {
		return nil, fmt.Errorf("%w: version %d, this build reads version %d", ErrInvalid, img.Version, Version)
	}
	k, err := kernel.New(img.Config)
	if err != nil {
		return nil, fmt.Errorf("%w: %w", ErrInvalid, err)
	}
	if err := loadDevice(k.Device, img.Device); err != nil {
		return nil, fmt.Errorf("%w: %w", ErrInvalid, err)
	}
	err = k.Inspect(func() error { // mounting reads the root without simulated I/O
		f, err := fs.Open(k.Device, img.FS)
		k.FS = f
		return err
	})
	if err != nil {
		return nil, fmt.Errorf("%w: %w", ErrInvalid, err)
	}
	k.Defer, k.Trace = img.Defer, img.Trace
	return k, nil
}

// SaveFile writes the image to path atomically (a temporary file renamed
// over it).
func SaveFile(k *kernel.Kernel, path string) error {
	tmp, err := os.CreateTemp(filepath.Dir(path), filepath.Base(path)+".*.tmp")
	if err != nil {
		return err
	}
	defer func() { _ = os.Remove(tmp.Name()) }()
	if err := Save(k, tmp); err != nil {
		_ = tmp.Close()
		return err
	}
	if err := tmp.Close(); err != nil {
		return err
	}
	return os.Rename(tmp.Name(), path)
}

// LoadFile reads the image at path.
func LoadFile(path string) (*kernel.Kernel, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer func() { _ = f.Close() }()
	return Load(f)
}

func saveDevice(d device.Device) (Device, error) {
	switch d := d.(type) {
	case *hdd.HDD:
		st := d.State()
		return Device{Kind: config.DeviceHDD, HDD: &st}, nil
	case *ssd.SSD:
		st := d.State()
		return Device{Kind: config.DeviceSSD, SSD: &st}, nil
	case *raid.RAID:
		st := d.State()
		out := Device{Kind: config.DeviceRAID, RAID: &st}
		for _, member := range d.Disks() {
			m, err := saveDevice(member)
			if err != nil {
				return Device{}, err
			}
			out.Disks = append(out.Disks, m)
		}
		return out, nil
	}
	return Device{}, fmt.Errorf("cannot save a %T", d)
}

func loadDevice(d device.Device, s Device) error {
	switch d := d.(type) {
	case *hdd.HDD:
		if s.HDD == nil {
			return fmt.Errorf("expected an HDD, the image has %q", s.Kind)
		}
		return d.SetState(*s.HDD)
	case *ssd.SSD:
		if s.SSD == nil {
			return fmt.Errorf("expected an SSD, the image has %q", s.Kind)
		}
		return d.SetState(*s.SSD)
	case *raid.RAID:
		if s.RAID == nil || len(s.Disks) != len(d.Disks()) {
			return fmt.Errorf("expected a RAID of %d disks, the image has %q", len(d.Disks()), s.Kind)
		}
		for i, member := range d.Disks() {
			if err := loadDevice(member, s.Disks[i]); err != nil {
				return fmt.Errorf("disk %d: %w", i+1, err)
			}
		}
		return d.SetState(*s.RAID)
	}
	return fmt.Errorf("cannot load a %T", d)
}

package main

import (
	"fmt"

	"github.com/anacrolix/torrent"

	flags "github.com/jessevdk/go-flags"
)

type cliOptions struct {
	DataDir    string   `long:"datadir" description:"Where to read and write data" required:"true"`
	ListenAddr string   `long:"listen" description:"Listen address" value-name:"HOST:PORT" required:"true"`
	Peers      []string `long:"peers" description:"Peers to connect to" value-name:"HOST:PORT" required:"true"`
	Torrent    string   `long:"torrent" description:"Torrent file to load" required:"true"`
}

func newConfig(opts cliOptions) *torrent.Config {
	c := &torrent.Config{
		DataDir:           opts.DataDir,
		DisableEncryption: true,
		DisableTrackers:   true,
	}
	return c
}

func main() {
	var opts cliOptions
	_, err := flags.Parse(&opts)
	if err != nil {
		panic(err)
	}

	cfg := newConfig(opts)
	cl, err := torrent.NewClient(cfg)
	if err != nil {
		panic(err)
	}

	torrent, err := cl.AddTorrentFromFile(opts.Torrent)
	if err != nil {
		panic(err)
	}

	infohash := torrent.InfoHash()
	fmt.Printf("Loaded torrent %s with info hash %v\n", torrent.Name(), infohash)

	cl.Close()
}

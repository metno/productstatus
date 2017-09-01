package main

import "github.com/anacrolix/torrent"

func newConfig() *torrent.Config {
	c := &torrent.Config{}
	return c
}

func main() {
	cfg := newConfig()
	cl, err := torrent.NewClient(cfg)
	if err != nil {
		panic(err)
	}
	cl.Close()
}

package main

import (
	"fmt"
	"net"
	"strconv"
	"time"

	"code.cloudfoundry.org/bytefmt"

	"github.com/anacrolix/torrent"

	flags "github.com/jessevdk/go-flags"
)

type cliOptions struct {
	DataDir    string   `long:"datadir" description:"Where to read and write data" required:"true"`
	ListenAddr string   `long:"listen" description:"Listen address" value-name:"HOST:PORT" required:"true"`
	Peers      []string `long:"peers" description:"Peers to connect to" value-name:"HOST:PORT"`
	Torrent    string   `long:"torrent" description:"Torrent file to load" required:"true"`
}

func newConfig(opts cliOptions) *torrent.Config {
	c := &torrent.Config{
		DataDir:           opts.DataDir,
		DisableEncryption: true,
		DisableTrackers:   true,
		ListenAddr:        opts.ListenAddr,
		NoDHT:             true,
		Seed:              true,
	}
	return c
}

func makePeer(hostport string) (*torrent.Peer, error) {
	host, portStr, err := net.SplitHostPort(hostport)
	if err != nil {
		return nil, err
	}

	port, err := strconv.Atoi(portStr)
	if err != nil || port < 1 || port > 65535 {
		return nil, fmt.Errorf("Wrong format for port, expected an integer between 1-65535")
	}

	ips, err := net.LookupIP(host)
	if len(ips) == 0 || err != nil {
		return nil, err
	}

	return &torrent.Peer{
		IP:   ips[0],
		Port: port,
	}, nil
}

func makePeers(hostports []string) []torrent.Peer {
	peers := make([]torrent.Peer, 0)

	for _, hostport := range hostports {
		peer, err := makePeer(hostport)
		if err != nil {
			fmt.Printf("Not adding peer %s: %s\n", hostport, err)
			continue
		}
		peers = append(peers, *peer)
	}

	return peers
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

	peers := makePeers(opts.Peers)
	torrent.AddPeers(peers)
	torrent.DownloadAll()

	start := time.Now()
	length := torrent.Length()

	for {
		completed := torrent.BytesCompleted()
		percentComplete := float64(completed) / float64(length) * 100

		speed := 0
		if percentComplete < 100 {
			since := time.Since(start)
			secs := since.Seconds()
			if secs > 0 {
				speed = int(float64(completed) / secs)
			}
		}

		fmt.Printf("\033[2K")
		fmt.Printf("\r%3.0f%% complete [%7s/%7s] [speed: %7s/s] [seeding: %t] [peers: %d]",
			percentComplete,
			bytefmt.ByteSize(uint64(completed)),
			bytefmt.ByteSize(uint64(length)),
			bytefmt.ByteSize(uint64(speed)),
			torrent.Seeding(),
			torrent.Stats().TotalPeers,
		)

		time.Sleep(1 * time.Second)
	}

	cl.Close()
}

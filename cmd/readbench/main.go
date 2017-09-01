// readbench is a command-line utility that benchmarks the read performance on
// a system, as seen by a user. It allows for multi-threaded reads, and the
// user can optionally set a larger blocksize.

package main

import (
	"flag"
	"fmt"
	"io"
	"math"
	"os"
	"time"

	"code.cloudfoundry.org/bytefmt"
)

type worker struct {
	index     int
	path      string
	offset    int64
	size      int64
	read      int64
	readTotal int64
	err       error
	finished  bool
}

var (
	blockSize   = flag.Int("blocksize", 8192, "How many bytes to read in one single read operation")
	fileName    = flag.String("file", "/dev/null", "Input file")
	workerCount = flag.Int("workers", 8, "How many goroutines to spawn")
)

func workRoutine(work worker, status chan worker) {
	f, err := os.Open(work.path)
	if err != nil {
		work.err = fmt.Errorf("Cannot open file: %s", err)
		status <- work
		return
	}
	defer f.Close()

	_, err = f.Seek(work.offset, 0)
	if err != nil {
		work.err = fmt.Errorf("Cannot seek to file offset %d: %s", work.offset, err)
		status <- work
		return
	}

	buf := make([]byte, *blockSize)

	for {
		read, err := f.Read(buf)
		work.read = int64(read)
		work.readTotal += work.read
		status <- work

		if err == io.EOF || work.readTotal >= work.size {
			work.finished = true
			break
		} else if err != nil {
			work.err = fmt.Errorf("Error during file read: %s\n", err)
			break
		}
	}

	status <- work
}

func main() {
	flag.Parse()

	f, err := os.Open(*fileName)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	info, err := f.Stat()
	if err != nil {
		panic(err)
	}

	// Split file into equally-sized chunks.
	size := info.Size()
	partSize := size / int64(*workerCount)
	remainder := math.Remainder(float64(partSize), float64(*blockSize))
	alignedSize := partSize - int64(remainder)

	fmt.Printf("File size is %d bytes\n", size)
	fmt.Printf("Using %d workers\n", *workerCount)

	status := make(chan worker, 1024)
	workers := make([]worker, *workerCount)

	for i := 0; i < *workerCount; i++ {
		offset := alignedSize * int64(i)
		w := worker{i, *fileName, offset, alignedSize, 0, 0, nil, false}
		go workRoutine(w, status)
		fmt.Printf("Worker %2d: reading %d bytes from start position %d\n", w.index+1, w.size, w.offset)
		workers[i] = w
	}

	read := int64(0)
	remaining := *workerCount
	start := time.Now()
	ticker := time.NewTicker(100 * time.Millisecond)

	printStats := func() {
		since := time.Since(start)
		secs := since.Seconds()
		speed := uint64(0)
		if secs > 0 {
			speed = uint64(float64(read) / secs)
		}
		fmt.Printf("\033[2K")
		fmt.Printf("\r[elapsed: %6s] [read: %7s/%7s] [speed: %7s/s]",
			since.String(),
			bytefmt.ByteSize(uint64(read)),
			bytefmt.ByteSize(uint64(size)),
			bytefmt.ByteSize(uint64(speed)))
	}

OUTER:
	for {
		select {
		case w := <-status:
			workers[w.index] = w
			if w.err != nil {
				fmt.Printf("Worker %d returned error: %s\n", w.err)
				remaining -= 1
				continue
			}
			read += w.read
			if w.finished {
				remaining -= 1
			}
			if remaining == 0 {
				break OUTER
			}
		case <-ticker.C:
			printStats()
		}
	}

	printStats()
	fmt.Printf("\n")
}

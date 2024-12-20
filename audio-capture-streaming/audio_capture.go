package main

import (
	"encoding/binary"
	"log"
	"math"
	"time"

	"github.com/gordonklaus/portaudio"
	"github.com/gorilla/websocket"
)

const bufferSize = 4096

func streamAudio(conn *websocket.Conn) {
	portaudio.Initialize()
	defer portaudio.Terminate()

	stream, err := portaudio.OpenDefaultStream(1, 0, 44100, bufferSize, audioCallback)
	if err != nil {
		log.Println("Failed to open audio stream:", err)
		return
	}
	defer stream.Close()

	err = stream.Start()
	if err != nil {
		log.Println("Failed to start audio stream:", err)
		return
	}

	buffer := make([]float32, bufferSize)
	for {
		if err := stream.Read(); err != nil {
			log.Println("Error reading audio stream:", err)
			break
		}

		err := conn.WriteMessage(websocket.BinaryMessage, bufferToBytes(buffer))
		if err != nil {
			log.Println("WebSocket write error:", err)
			break
		}

		time.Sleep(time.Millisecond * 10)
	}

	stream.Stop()
}

func bufferToBytes(buffer []float32) []byte {
	bytes := make([]byte, len(buffer)*4)
	for i, v := range buffer {
		binary.LittleEndian.PutUint32(bytes[i*4:], math.Float32bits(v))
	}
	return bytes
}

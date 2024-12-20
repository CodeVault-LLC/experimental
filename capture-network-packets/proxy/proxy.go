package main

import (
	"crypto/tls"
	"fmt"
	"io"
	"log"
	"net"
	"os"
)

// KeyLogWriter writes TLS session keys to a file
type KeyLogWriter struct {
	file *os.File
}

func (w *KeyLogWriter) Write(p []byte) (n int, err error) {
	return w.file.Write(p)
}

// ProxyHandler handles the proxy connection
func proxyHandler(clientConn net.Conn, targetHost string, targetPort string, keyLogWriter *KeyLogWriter) {
	// Set up the TLS configuration with key logging
	tlsConfig := &tls.Config{
		InsecureSkipVerify: true, // Skips server verification for the demo
		KeyLogWriter:       keyLogWriter,
	}

	// Connect to the remote server (target)
	remoteConn, err := tls.Dial("tcp", fmt.Sprintf("%s:%s", targetHost, targetPort), tlsConfig)
	if err != nil {
		log.Printf("Error connecting to remote server: %v", err)
		clientConn.Close()
		return
	}
	defer remoteConn.Close()

	// Start proxying the data
	go func() {
		_, err := io.Copy(remoteConn, clientConn) // Copy client data to remote
		if err != nil {
			log.Printf("Error proxying data to remote: %v", err)
		}
	}()
	go func() {
		_, err := io.Copy(clientConn, remoteConn) // Copy remote data to client
		if err != nil {
			log.Printf("Error proxying data to client: %v", err)
		}
	}()

	// Block until connection is closed
	select {}
}

func main() {
	// Open the key log file
	keyLogFile, err := os.Create("tls_keys.log")
	if err != nil {
		log.Fatalf("Error creating TLS key log file: %v", err)
	}
	defer keyLogFile.Close()

	// Set up the key log writer
	keyLogWriter := &KeyLogWriter{file: keyLogFile}

	// Start listening for incoming connections
	listenAddr := "localhost:8080" // Proxy listens on this address
	listener, err := net.Listen("tcp", listenAddr)
	if err != nil {
		log.Fatalf("Error starting listener: %v", err)
	}
	defer listener.Close()

	log.Printf("Listening on %s...\n", listenAddr)

	for {
		// Accept incoming client connections
		clientConn, err := listener.Accept()
		if err != nil {
			log.Printf("Error accepting connection: %v", err)
			continue
		}

		// Proxy each connection to the target (example: Google's HTTPS server)
		go proxyHandler(clientConn, "www.google.com", "443", keyLogWriter)
	}
}

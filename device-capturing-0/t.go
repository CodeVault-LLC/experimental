package main

import (
	"crypto/tls"
	"log"
	"net/http"
	"os"
)

func main() {
	os.Setenv("SSLKEYLOGFILE", "tlskeys.log")

	// Create a custom transport with TLS configuration
	transport := &http.Transport{
		TLSClientConfig: &tls.Config{
			KeyLogWriter: createKeyLogFile(),
		},
	}

	client := &http.Client{Transport: transport}

	// Example request
	resp, err := client.Get("https://example.com")
	if err != nil {
		log.Fatalf("Request failed: %v", err)
	}
	defer resp.Body.Close()
}

// createKeyLogFile creates the log file for storing TLS keys
func createKeyLogFile() *os.File {
	file, err := os.OpenFile("tlskeys.log", os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		log.Fatalf("Failed to create key log file: %v", err)
	}
	return file
}

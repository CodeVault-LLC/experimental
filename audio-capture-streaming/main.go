package main

import (
	"embed"
	"html/template"
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

//go:embed index.html
var content embed.FS

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

func main() {
	// Serve static HTML page
	http.HandleFunc("/", serveHomePage)
	// Set up WebSocket API endpoint for audio streaming
	http.HandleFunc("/ws", handleWebSocket)

	// Start HTTP server
	log.Println("Starting server on :8080")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}

func serveHomePage(w http.ResponseWriter, r *http.Request) {
	tmpl, err := template.ParseFS(content, "index.html")
	if err != nil {
		http.Error(w, "Failed to load page", http.StatusInternalServerError)
		return
	}
	tmpl.Execute(w, nil)
}

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Error upgrading WebSocket:", err)
		return
	}
	defer conn.Close()

	// Start audio stream to the WebSocket connection
	go streamAudio(conn)
}

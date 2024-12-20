package main

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"log"
	"net"
)

func main() {
	const address = "127.0.0.1:65432"

	// Generate RSA key pair
	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		log.Fatalf("Error generating RSA keys: %v", err)
	}
	publicKey := &privateKey.PublicKey

	// Serialize the public key to PEM format
	publicKeyBytes := x509.MarshalPKCS1PublicKey(publicKey)
	publicPem := pem.EncodeToMemory(&pem.Block{
		Type:  "RSA PUBLIC KEY",
		Bytes: publicKeyBytes,
	})

	// Start listening on the specified port
	listener, err := net.Listen("tcp", address)
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
	fmt.Println("Server is listening on", address)

	for {
		conn, err := listener.Accept()
		if err != nil {
			log.Printf("Connection error: %v", err)
			continue
		}
		go handleConnection(conn, privateKey, publicPem)
	}
}

func handleConnection(conn net.Conn, privateKey *rsa.PrivateKey, publicPem []byte) {
	defer conn.Close()
	fmt.Println("Connection established")

	// Send public key to client
	_, err := conn.Write(publicPem)
	if err != nil {
		log.Printf("Error sending public key: %v", err)
		return
	}
	fmt.Println("Public key sent to client")

	// Receive data from client
	buffer := make([]byte, 4096)
	n, err := conn.Read(buffer)
	if err != nil {
		log.Printf("Error reading data: %v", err)
		return
	}

	// Split the received data into encrypted AES key and encrypted message
	data := buffer[:n]
	parts := bytes.Split(data, []byte("||"))
	if len(parts) != 2 {
		log.Println("Invalid data format")
		return
	}
	encryptedAESKey := parts[0]
	encryptedMessage := parts[1]

	// Decrypt the AES key
	aesKey, err := rsa.DecryptOAEP(
		sha256.New(),
		rand.Reader,
		privateKey,
		encryptedAESKey,
		nil,
	)

	if err != nil {
		log.Printf("Error decrypting AES key: %v", err)
		return
	}

	// Decrypt the message using AES
	iv := encryptedMessage[:16]
	ciphertext := encryptedMessage[16:]
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		log.Printf("Error creating AES cipher: %v", err)
		return
	}

	stream := cipher.NewCFBDecrypter(block, iv)
	plaintext := make([]byte, len(ciphertext))
	stream.XORKeyStream(plaintext, ciphertext)

	fmt.Printf("Decrypted message: %s\n", plaintext)
}

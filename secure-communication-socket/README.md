# secure-communication-socket
Secure communication socket is a project that tests how to securely connect a golang server and a golang client using a secure socket communication methodology.

## Purpose
Project [Xenomorph](https://github.com/CodeVault-LLC/xenomorph) had issues with making a secure connection between client and server without using a certificate. The main issues came with how we give out the *secure token* to the user, and how they handled it to the server.

## How it works
The server is created using Golang's `net` package, and the client is created using Python's `socket` package. Since this is a mini-project, we are not going to handle anything else, other then just decrypting a message. The server in this instance for learning purposes, it will generate a RSA key pair, and send the public key to the client once it connects. The client will then encrypt a message using the public key, and send it back to the server. The server will then decrypt the message using the private key, and print it out.

## Status
The project was a success, and we learned the key mistakes we made in project [Xenomorph](https://github.com/CodeVault-LLC/xenomorph).

Potential future updates may include:
- Adding more security pairs, such as SSL/TLS.
- Adding more security features, such as hashing and salting.

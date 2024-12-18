package main

import (
	"crypto/tls"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"sync"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcap"
	"github.com/google/gopacket/pcapgo"
)

var DefaultConfig *tls.Config
var fileMutex sync.Mutex

type KeyLogWriter struct {
	file *os.File
}

func (w *KeyLogWriter) Write(p []byte) (n int, err error) {
	return w.file.Write(p)
}

func createTLSKeyLogFile() *os.File {
	keyLogFile, err := os.Create("tls_keys.log")
	if err != nil {
		log.Fatalf("Error creating TLS key log file: %v", err)
	}

	DefaultConfig = &tls.Config{
		KeyLogWriter: keyLogFile,
	}

	return keyLogFile
}

func processPacket(packet gopacket.Packet, logFile *os.File) {
	ipLayer := packet.Layer(layers.LayerTypeIPv4)
	tcpLayer := packet.Layer(layers.LayerTypeTCP)

	if ipLayer == nil || tcpLayer == nil {
		return
	}

	ip, _ := ipLayer.(*layers.IPv4)
	tcp, _ := tcpLayer.(*layers.TCP)

	// Only allow HTTP traffic (TCP port 80)
	if tcp.DstPort != 80 && tcp.SrcPort != 80 {
		return // Skip HTTPS traffic (port 443) and other traffic
	}

	logEntry := fmt.Sprintf("Connection: SourceIP=%s DestIP=%s DestPort=%d\n",
		ip.SrcIP, ip.DstIP, tcp.DstPort)

	fileMutex.Lock()
	defer fileMutex.Unlock()
	logFile.WriteString(logEntry)

	appLayer := packet.ApplicationLayer()
	if appLayer != nil {
		payloadEntry := fmt.Sprintf("Payload: %s\n", string(appLayer.Payload()))
		logFile.WriteString(payloadEntry)
	}
}

func savePacketToFile(packet gopacket.Packet, fileName string) {
	f, err := os.OpenFile(fileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Error opening file for packet saving: %v", err)
	}
	defer f.Close()

	writer := pcapgo.NewWriter(f)
	if err := writer.WriteFileHeader(65536, layers.LinkTypeEthernet); err != nil {
		log.Fatalf("Error writing pcap header: %v", err)
	}

	writer.WritePacket(packet.Metadata().CaptureInfo, packet.Data())
}

// Proxy handler for HTTP requests (port 80)
func proxyHandler(clientConn net.Conn, targetHost string, targetPort string, keyLogWriter *KeyLogWriter) {
	// Proxying logic for HTTP (no TLS)
	remoteConn, err := net.Dial("tcp", fmt.Sprintf("%s:%s", targetHost, targetPort))
	if err != nil {
		log.Printf("Error connecting to remote server: %v", err)
		clientConn.Close()
		return
	}
	defer remoteConn.Close()

	go func() {
		_, err := io.Copy(remoteConn, clientConn)
		if err != nil {
			log.Printf("Error proxying data to remote: %v", err)
		}
	}()
	go func() {
		_, err := io.Copy(clientConn, remoteConn)
		if err != nil {
			log.Printf("Error proxying data to client: %v", err)
		}
	}()

	select {}
}

func listenForDevice(device string, logFile *os.File) {
	handle, err := pcap.OpenLive(device, 65536, true, pcap.BlockForever)
	if err != nil {
		log.Printf("Error opening device %s: %v\n", device, err)
		return
	}
	defer handle.Close()

	// Update filter to only capture HTTP traffic (port 80)
	filter := "tcp port 80"
	if err := handle.SetBPFFilter(filter); err != nil {
		log.Printf("Error setting filter on device %s: %v\n", device, err)
		return
	}
	log.Printf("Filter set on device %s: %s\n", device, filter)

	packetSource := gopacket.NewPacketSource(handle, handle.LinkType())

	for packet := range packetSource.Packets() {
		processPacket(packet, logFile)
		savePacketToFile(packet, "captured_traffic.pcap")
	}
}

func main() {
	logFile, err := os.OpenFile("network_traffic.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Error opening log file: %v", err)
	}
	defer logFile.Close()
	log.SetOutput(logFile)

	keyLogFile := createTLSKeyLogFile()
	defer keyLogFile.Close()

	// Start HTTP proxy listener (on port 8080)
	go func() {
		proxyListener, err := net.Listen("tcp", "localhost:8080")
		if err != nil {
			log.Fatalf("Error starting proxy listener: %v", err)
		}
		defer proxyListener.Close()

		log.Printf("HTTP Proxy listening on localhost:8080")

		for {
			clientConn, err := proxyListener.Accept()
			if err != nil {
				log.Printf("Error accepting proxy connection: %v", err)
				continue
			}

			// Handle HTTP traffic (port 80)
			go proxyHandler(clientConn, "www.google.com", "80", &KeyLogWriter{file: keyLogFile})
		}
	}()

	// Start packet capture from devices
	devices, err := pcap.FindAllDevs()
	if err != nil {
		log.Fatalf("Error finding devices: %v", err)
	}

	if len(devices) == 0 {
		log.Fatalf("No devices found. Ensure you have the necessary permissions.")
	}

	var wg sync.WaitGroup

	// Capture packets on all devices and filter only HTTP traffic
	for _, device := range devices {
		log.Printf("Device: %s", device.Name)
		if len(device.Addresses) > 0 {
			wg.Add(1)
			go func(devName string) {
				defer wg.Done()
				listenForDevice(devName, logFile)
			}(device.Name)
		}
	}

	wg.Wait()
}

package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/grandcat/zeroconf"
	"tinygo.org/x/bluetooth"
)

// Device struct to store different device types
type Device struct {
	Address string
	Name    string
	Type    string
	Service string // For mDNS devices (e.g., TVs)
}

// Store devices in a slice
var discoveredDevices []Device

// Bluetooth adapter (for BLE)
var adapter = bluetooth.DefaultAdapter

// DiscoverBluetoothDevices discovers nearby Bluetooth Low Energy devices
func discoverBluetoothDevices() {
	fmt.Println("\nScanning for Bluetooth devices...")

	must("enable BLE interface", adapter.Enable())

	err := adapter.Scan(func(adapter *bluetooth.Adapter, device bluetooth.ScanResult) {
		// Check if this device is already discovered
		address := device.Address.String()
		if !deviceExists(address) {
			// Store the discovered Bluetooth device
			deviceInfo := Device{
				Address: address,
				Name:    device.LocalName(),
				Type:    "Bluetooth",
			}
			discoveredDevices = append(discoveredDevices, deviceInfo)
			// Log the found device
			fmt.Printf("Discovered Bluetooth device: %s - %s\n", address, device.LocalName())
		}
	})

	if err != nil {
		log.Fatalf("Failed to scan: %v\n", err)
	}
}

// discoverTvs discovers TV and other devices via mDNS (Zeroconf)
func discoverTvs() {
	fmt.Println("\nScanning for TVs and other devices...")

	// Start Zeroconf service browsing
	server, err := zeroconf.NewResolver(nil)
	if err != nil {
		log.Fatalf("Failed to start Zeroconf: %v\n", err)
	}

	serviceType := "_http._tcp.local." // This is a typical service for TVs

	// Handle discovered services
	// Create a channel to receive the discovered services
	serviceChannel := make(chan *zeroconf.ServiceEntry)

	// Start Zeroconf service browsing
	server.Browse(context.Background(), serviceType, "local.", serviceChannel)

	// Handle discovered services
	go func() {
		for result := range serviceChannel {
			address := result.AddrIPv4[0].String()
			// Check if this device is already discovered
			if !deviceExists(address) {
				// Store the discovered TV/other device
				deviceInfo := Device{
					Address: address,
					Name:    result.ServiceInstanceName(),
					Type:    "TV/Network Device",
					Service: result.Service,
				}
				discoveredDevices = append(discoveredDevices, deviceInfo)
				// Log the found device
				fmt.Printf("Discovered TV/Network device: %s - %s\n", address, result.ServiceInstanceName())
			}
		}
	}()

	// Sleep to allow some time for discovery
	time.Sleep(10 * time.Second)
}

// Check if the device already exists in the discovered list
func deviceExists(address string) bool {
	for _, device := range discoveredDevices {
		if device.Address == address {
			return true
		}
	}
	return false
}

func main() {
	// Discover Bluetooth devices (using BLE)
	discoverBluetoothDevices()

	// Discover TVs and other devices on the local network using mDNS
	discoverTvs()

	// After discovery, log all found devices
	fmt.Println("\nAll discovered devices:")
	for _, device := range discoveredDevices {
		fmt.Printf("Device Type: %s, Name: %s, Address: %s\n", device.Type, device.Name, device.Address)
		if device.Service != "" {
			fmt.Printf("Service: %s\n", device.Service)
		}
	}
}

// Helper function to panic on errors
func must(action string, err error) {
	if err != nil {
		panic("failed to " + action + ": " + err.Error())
	}
}

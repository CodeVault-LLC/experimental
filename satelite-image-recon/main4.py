import collections.abc

import bluetooth
#import pyudev
from zeroconf import Zeroconf, ServiceBrowser
import time

def discover_bluetooth_devices():
    print("\nScanning for Bluetooth devices...")
    nearby_devices = bluetooth.discover_devices(lookup_names=True, device_id=0)
    print("Found Bluetooth devices:")
    print(nearby_devices)
    for addr, name in nearby_devices:
        print(f"Address: {addr}, Name: {name}")


# def list_usb_devices():
#     context = pyudev.Context()
#     print("\nListing all USB devices:")
#     for device in context.list_devices(subsystem='usb'):
#         print(f"Device: {device}, ID: {device.device_node}, Type: {device.get('ID_MODEL')}, Vendor: {device.get('ID_VENDOR')}")

def discover_tvs():
    zeroconf = Zeroconf()
    print("\nScanning for TVs and other devices...")

    service_type = "_http._tcp.local."  # Common service type for TVs
    browser = ServiceBrowser(zeroconf, service_type, handlers=[lambda zc, service_type, name: print(f"Discovered device: {name}")])

    time.sleep(10)
    zeroconf.close()

if __name__ == "__main__":
    discover_bluetooth_devices()
    #list_usb_devices()
    discover_tvs()

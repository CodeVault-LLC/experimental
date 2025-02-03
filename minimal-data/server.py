import socket
from util import decode_text, encoded_to_bytes, bytes_to_encoded, encode_text

def start_udp_server():
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 5000))
    print("UDP server listening on port 5000...")

    while True:
        # Receive data (max 1024 bytes)
        data, addr = server_socket.recvfrom(1024)
        print(f"Received raw data from {addr}: {data}")

        # Convert bytes to encoded list
        encoded = bytes_to_encoded(data)

        # Decode the encoded list into text
        text = decode_text(encoded)
        print(f"Decoded text: {text}")

        # Remove the first word
        response_text = text.split(' ', 1)[-1]  # Remove first word
        print(f"Response text: {response_text}")

        # Encode the response text into binary
        response_data = encoded_to_bytes(encode_text(response_text))

        # Send response back
        server_socket.sendto(response_data, addr)

if __name__ == '__main__':
    start_udp_server()

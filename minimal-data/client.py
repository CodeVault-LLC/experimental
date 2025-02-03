import socket
from util import encode_text, encoded_to_bytes, decode_text, bytes_to_encoded

def send_udp_data():
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Encode "Hello World" into binary
    text = "Hello World"
    encoded = encode_text(text)
    data = encoded_to_bytes(encoded)
    print(f"Original text: {text}")
    print(f"Encoded data: {data}")

    # Send data to the server
    client_socket.sendto(data, ('localhost', 5000))

    # Receive response (max 1024 bytes)
    response, _ = client_socket.recvfrom(1024)
    print(f"Received raw response: {response}")

    # Convert bytes to encoded list
    encoded_response = bytes_to_encoded(response)

    # Decode the response into text
    response_text = decode_text(encoded_response)
    print(f"Decoded response: {response_text}")

    client_socket.close()

if __name__ == '__main__':
    send_udp_data()

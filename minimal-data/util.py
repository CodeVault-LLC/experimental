import typing

# Extended encoding scheme to include space and uppercase letters
CHAR_TO_BITS = {chr(i): i - ord('a') for i in range(ord('a'), ord('z') + 1)}
CHAR_TO_BITS[' '] = 26  # Add space
BITS_TO_CHAR = {v: k for k, v in CHAR_TO_BITS.items()}

def encode_text(text: str) -> typing.List[int]:
    encoded = []
    for char in text.lower():
        if char in CHAR_TO_BITS:
            encoded.append(CHAR_TO_BITS[char])
    return encoded

def decode_text(encoded: typing.List[int]) -> str:
    return ''.join([BITS_TO_CHAR[bits] for bits in encoded])

def encoded_to_bytes(encoded: typing.List[int]) -> bytes:
    return bytes(encoded)

def bytes_to_encoded(data: bytes) -> typing.List[int]:
    return list(data)

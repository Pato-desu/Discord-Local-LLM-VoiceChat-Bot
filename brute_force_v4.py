import nacl.bindings
import struct

def brute_force_v4():
    try:
        with open("failed_packet.bin", "rb") as f:
            packet = f.read()
        with open("failed_key.txt", "r") as f:
            key_hex = f.read().strip()
            key = bytes.fromhex(key_hex)
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    header = packet[:12]
    short_nonce = packet[-4:]
    
    has_extension = bool(header[0] & 0x10)
    ext_header_len = 0
    if has_extension:
        ext_len_words = int.from_bytes(packet[14:16], byteorder="big")
        ext_header_len = 4 + 4 * ext_len_words

    # Payloads to try
    payloads = [
        ("Data after Extension", packet[12 + ext_header_len : -4]),
        ("Data including Extension", packet[12 : -4]),
    ]

    # AADs to try
    aads = [
        ("Header only (12 bytes)", header),
        ("Header + Extension", packet[: 12 + ext_header_len]),
        ("Empty AAD", b""),
    ]

    print(f"--- Starting Brute Force v4 ---")
    
    # 1. Try XChaCha20 (24-byte nonce)
    print("\nTesting XChaCha20 (24-byte nonce)...")
    nonces_24 = [
        ("ShortNonce + 20 zeros", bytes(short_nonce + b"\x00" * 20)),
        ("20 zeros + ShortNonce", bytes(b"\x00" * 20 + short_nonce)),
        ("Header + ShortNonce + 8 zeros", bytes(header + short_nonce + b"\x00" * 8)),
        ("ShortNonce + Header + 8 zeros", bytes(short_nonce + header + b"\x00" * 8)),
        ("Header + 12 zeros", bytes(header + b"\x00" * 12)),
    ]

    for p_name, payload in payloads:
        for a_name, aad in aads:
            for n_name, nonce in nonces_24:
                try:
                    decrypted = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                        bytes(payload), bytes(aad), bytes(nonce), key
                    )
                    print(f"SUCCESS (XChaCha20)! P:{p_name} A:{a_name} N:{n_name}")
                    return
                except: pass

    # 2. Try ChaCha20 (12-byte nonce)
    print("\nTesting ChaCha20 (12-byte nonce)...")
    nonces_12 = [
        ("Header", header),
        ("ShortNonce + 8 zeros", bytes(short_nonce + b"\x00" * 8)),
        ("8 zeros + ShortNonce", bytes(b"\x00" * 8 + short_nonce)),
    ]

    for p_name, payload in payloads:
        for a_name, aad in aads:
            for n_name, nonce in nonces_12:
                try:
                    decrypted = nacl.bindings.crypto_aead_chacha20poly1305_ietf_decrypt(
                        bytes(payload), bytes(aad), bytes(nonce), key
                    )
                    print(f"SUCCESS (ChaCha20)! P:{p_name} A:{a_name} N:{n_name}")
                    return
                except: pass

    print("\nAll combinations failed.")

if __name__ == "__main__":
    brute_force_v4()

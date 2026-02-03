import nacl.bindings
import struct

def analyze_and_brute_force():
    try:
        with open("failed_packet.bin", "rb") as f:
            packet = f.read()
        with open("failed_key.txt", "r") as f:
            key_hex = f.read().strip()
            key = bytes.fromhex(key_hex)
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    print(f"Full Packet Hex: {packet.hex()}")
    
    header = packet[:12]
    data = packet[12:]
    
    # Check for extension bit
    has_extension = bool(header[0] & 0x10)
    print(f"Has Extension: {has_extension}")
    
    ext_header_len = 0
    if has_extension:
        # RTP extension starts at byte 12
        # 2 bytes ID, 2 bytes length (in 32-bit words)
        ext_id = data[:2]
        ext_len_words = int.from_bytes(data[2:4], byteorder="big")
        ext_header_len = 4 + 4 * ext_len_words
        print(f"Extension ID: {ext_id.hex()}, Length (words): {ext_len_words}, Total Ext Len: {ext_header_len}")

    # The nonce is the last 4 bytes
    short_nonce = packet[-4:]
    # The encrypted data is between the header (including extension) and the nonce
    payload = packet[12 + ext_header_len : -4]
    
    print(f"Payload length: {len(payload)}")
    
    # Try different AADs
    aads = [
        ("Header only (12 bytes)", header),
        ("Header + Extension", packet[: 12 + ext_header_len]),
    ]
    
    # Try different Nonces
    nonces = []
    n_start = bytearray(24)
    n_start[:4] = short_nonce
    nonces.append(("Beginning (Standard)", bytes(n_start)))
    
    n_end = bytearray(24)
    n_end[20:] = short_nonce
    nonces.append(("End", bytes(n_end)))

    print("\n--- Starting Brute Force v2 ---")
    for a_name, aad in aads:
        for n_name, nonce in nonces:
            try:
                decrypted = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                    bytes(payload), bytes(aad), bytes(nonce), key
                )
                print(f"SUCCESS! AAD: {a_name}, Nonce: {n_name}")
                print(f"Decrypted (hex): {decrypted.hex()}")
                return
            except Exception as e:
                # print(f"Failed: AAD={a_name}, Nonce={n_name} ({e})")
                pass

    print("\nAll combinations failed. Trying one more thing: maybe the extension is part of the encrypted data but the AAD is still just the 12 byte header?")
    # This is what we tried before, but let's be explicit.
    
    print("No success.")

if __name__ == "__main__":
    analyze_and_brute_force()

import nacl.bindings
import struct

def brute_force_v3():
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
    
    # Check for extension
    has_extension = bool(header[0] & 0x10)
    ext_header_len = 0
    if has_extension:
        ext_len_words = int.from_bytes(packet[14:16], byteorder="big")
        ext_header_len = 4 + 4 * ext_len_words

    # Variations of Payload
    payloads = [
        ("Data after Extension", packet[12 + ext_header_len : -4]),
        ("Data including Extension", packet[12 : -4]),
    ]

    # Variations of AAD
    header_no_ext = bytearray(header)
    header_no_ext[0] &= 0xEF # Clear the extension bit
    
    aads = [
        ("Header only (12 bytes)", header),
        ("Header + Extension", packet[: 12 + ext_header_len]),
        ("Header (No Ext Bit)", bytes(header_no_ext)),
        ("Empty AAD", b""),
    ]

    # Variations of Nonce (24 bytes)
    nonces = []
    
    # Big Endian
    n_be_start = bytearray(24)
    n_be_start[:4] = short_nonce
    nonces.append(("Big Endian (Start)", bytes(n_be_start)))
    
    n_be_end = bytearray(24)
    n_be_end[20:] = short_nonce
    nonces.append(("Big Endian (End)", bytes(n_be_end)))
    
    # Little Endian
    short_nonce_le = short_nonce[::-1]
    n_le_start = bytearray(24)
    n_le_start[:4] = short_nonce_le
    nonces.append(("Little Endian (Start)", bytes(n_le_start)))
    
    n_le_end = bytearray(24)
    n_le_end[20:] = short_nonce_le
    nonces.append(("Little Endian (End)", bytes(n_le_end)))

    print(f"--- Starting Brute Force v3 ---")
    print(f"Packet: {packet.hex()}")
    print(f"Has Extension: {has_extension}, Ext Len: {ext_header_len}")

    for p_name, payload in payloads:
        for a_name, aad in aads:
            for n_name, nonce in nonces:
                try:
                    decrypted = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                        bytes(payload), bytes(aad), bytes(nonce), key
                    )
                    print(f"\nSUCCESS!")
                    print(f"Payload: {p_name}")
                    print(f"AAD: {a_name}")
                    print(f"Nonce: {n_name}")
                    print(f"Decrypted (hex): {decrypted.hex()}")
                    return
                except:
                    pass

    print("\nAll combinations failed.")

if __name__ == "__main__":
    brute_force_v3()

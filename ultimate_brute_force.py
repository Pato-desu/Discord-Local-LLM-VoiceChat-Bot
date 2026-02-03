import nacl.bindings
import struct

def ultimate_brute_force():
    try:
        with open("failed_packet.bin", "rb") as f:
            packet = f.read()
        with open("failed_key.txt", "r") as f:
            key_hex = f.read().strip()
            key = bytes.fromhex(key_hex)
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    print(f"--- ULTIMATE BRUTE FORCE ---")
    print(f"Packet Hex: {packet.hex()}")
    print(f"Key: {key_hex}")

    header = packet[:12]
    short_nonce = packet[-4:]
    
    # RTP Header fields
    seq_num = struct.unpack('>H', header[2:4])[0]
    timestamp = struct.unpack('>I', header[4:8])[0]
    ssrc = struct.unpack('>I', header[8:12])[0]

    # Extension check
    has_extension = bool(header[0] & 0x10)
    ext_header_len = 0
    if has_extension:
        ext_len_words = int.from_bytes(packet[14:16], byteorder="big")
        ext_header_len = 4 + 4 * ext_len_words
    
    # 1. Payload Variations
    payload_vars = [
        ("Data after Ext (Standard)", packet[12 + ext_header_len : -4]),
        ("Data incl Ext (Encrypted Ext?)", packet[12 : -4]),
        ("Full data (No short nonce?)", packet[12:]),
        ("Full data after Ext", packet[12 + ext_header_len :]),
    ]

    # 2. AAD Variations
    header_no_ext_bit = bytearray(header)
    header_no_ext_bit[0] &= 0xEF
    
    aad_vars = [
        ("Header only (12b)", header),
        ("Header + Ext", packet[: 12 + ext_header_len]),
        ("Header (No Ext Bit)", bytes(header_no_ext_bit)),
        ("Empty AAD", b""),
        ("First byte cleared", b"\x00" + header[1:]),
    ]

    # 3. Nonce Variations (24 bytes for XChaCha20)
    nonces_24 = []
    
    # Short Nonce based
    n = bytearray(24)
    n[:4] = short_nonce
    nonces_24.append(("ShortNonce (Start)", bytes(n)))
    
    n = bytearray(24)
    n[20:] = short_nonce
    nonces_24.append(("ShortNonce (End)", bytes(n)))

    n = bytearray(24)
    n[:4] = short_nonce[::-1]
    nonces_24.append(("ShortNonce LE (Start)", bytes(n)))

    # Header based
    n = bytearray(24)
    n[:12] = header
    nonces_24.append(("Header (Start)", bytes(n)))

    n = bytearray(24)
    n[12:] = header
    nonces_24.append(("Header (End)", bytes(n)))

    # Sequence Number based
    n = bytearray(24)
    n[:4] = struct.pack('>I', seq_num)
    nonces_24.append(("SeqNum BE (Start)", bytes(n)))

    # 4. Nonce Variations (12 bytes for ChaCha20)
    nonces_12 = [
        ("Header", header),
        ("ShortNonce + 8 zeros", short_nonce + b"\x00" * 8),
        ("8 zeros + ShortNonce", b"\x00" * 8 + short_nonce),
        ("SeqNum BE + 8 zeros", struct.pack('>I', seq_num) + b"\x00" * 8),
    ]

    # --- EXECUTION ---
    print(f"Testing {len(payload_vars) * len(aad_vars) * (len(nonces_24) + len(nonces_12))} combinations...")

    for p_name, payload in payload_vars:
        if not payload: continue
        for a_name, aad in aad_vars:
            # Try XChaCha20
            for n_name, nonce in nonces_24:
                try:
                    decrypted = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                        bytes(payload), bytes(aad), bytes(nonce), key
                    )
                    print(f"\n!!! SUCCESS (XChaCha20) !!!")
                    print(f"Payload: {p_name}\nAAD: {a_name}\nNonce: {n_name}")
                    print(f"Decrypted: {decrypted.hex()[:64]}...")
                    return
                except: pass
            
            # Try ChaCha20
            for n_name, nonce in nonces_12:
                try:
                    decrypted = nacl.bindings.crypto_aead_chacha20poly1305_ietf_decrypt(
                        bytes(payload), bytes(aad), bytes(nonce), key
                    )
                    print(f"\n!!! SUCCESS (ChaCha20) !!!")
                    print(f"Payload: {p_name}\nAAD: {a_name}\nNonce: {n_name}")
                    print(f"Decrypted: {decrypted.hex()[:64]}...")
                    return
                except: pass

    print("\nAll combinations failed. The mystery remains.")

if __name__ == "__main__":
    ultimate_brute_force()

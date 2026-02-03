import nacl.bindings
import struct

def nuclear_brute_force():
    try:
        with open("failed_packet.bin", "rb") as f:
            packet = f.read()
        with open("failed_key.txt", "r") as f:
            key_hex = f.read().strip()
            key = bytes.fromhex(key_hex)
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    print(f"--- NUCLEAR BRUTE FORCE ---")
    print(f"Packet Length: {len(packet)}")
    
    # We will try every possible slice for AAD and Payload
    # And every possible 4-byte slice for Nonce
    
    # 1. Nonce candidates (4 bytes)
    nonce_candidates = []
    for i in range(len(packet) - 3):
        nonce_candidates.append((f"Slice at {i}", packet[i:i+4]))
    
    # Also try the sequence number from the header
    seq_num = packet[2:4]
    nonce_candidates.append(("SeqNum BE", struct.pack('>I', struct.unpack('>H', seq_num)[0])))
    
    # 2. AAD candidates
    aad_candidates = [
        ("Empty", b""),
        ("Header (12b)", packet[:12]),
        ("Header (No Ext Bit)", bytes([packet[0] & 0xEF]) + packet[1:12]),
    ]
    # Try all possible header lengths
    for i in range(1, 33):
        aad_candidates.append((f"First {i} bytes", packet[:i]))

    # 3. Payload candidates
    # Usually starts after header (12) or extension (24)
    # Usually ends before nonce (last 4)
    payload_candidates = [
        ("After 12, before last 4", packet[12:-4]),
        ("After 24, before last 4", packet[24:-4]),
        ("After 12, to end", packet[12:]),
        ("After 24, to end", packet[24:]),
    ]

    print(f"Testing {len(nonce_candidates) * len(aad_candidates) * len(payload_candidates) * 2} combinations...")

    for p_name, payload in payload_candidates:
        if not payload or len(payload) < 16: continue # Need at least a tag
        for a_name, aad in aad_candidates:
            for n_name, short_nonce in nonce_candidates:
                # Try XChaCha20 (24-byte nonce)
                for pos in [0, 20]: # Try at start and end of 24-byte buffer
                    nonce_24 = bytearray(24)
                    nonce_24[pos:pos+4] = short_nonce
                    try:
                        decrypted = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                            bytes(payload), bytes(aad), bytes(nonce_24), key
                        )
                        print(f"\n!!! NUCLEAR SUCCESS (XChaCha20) !!!")
                        print(f"Payload: {p_name}\nAAD: {a_name}\nNonce Source: {n_name}\nNonce Pos: {pos}")
                        return
                    except: pass

                # Try ChaCha20 (12-byte nonce)
                for pos in [0, 8]:
                    nonce_12 = bytearray(12)
                    nonce_12[pos:pos+4] = short_nonce
                    try:
                        decrypted = nacl.bindings.crypto_aead_chacha20poly1305_ietf_decrypt(
                            bytes(payload), bytes(aad), bytes(nonce_12), key
                        )
                        print(f"\n!!! NUCLEAR SUCCESS (ChaCha20) !!!")
                        print(f"Payload: {p_name}\nAAD: {a_name}\nNonce Source: {n_name}\nNonce Pos: {pos}")
                        return
                    except: pass

    print("\nNuclear option failed. This is officially a mystery.")

if __name__ == "__main__":
    nuclear_brute_force()

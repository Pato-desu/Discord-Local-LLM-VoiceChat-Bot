import nacl.bindings
import struct

def brute_force():
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
    data = packet[12:]
    payload = data[:-4]
    short_nonce = data[-4:]

    print(f"Packet length: {len(packet)}")
    print(f"Header: {header.hex()}")
    print(f"Short Nonce: {short_nonce.hex()}")
    print(f"Payload length: {len(payload)}")
    print(f"Key: {key_hex}")

    # Variations to try
    nonces = []
    
    # 1. Nonce at beginning (Standard)
    n1 = bytearray(24)
    n1[:4] = short_nonce
    nonces.append(("Beginning (Standard)", bytes(n1)))
    
    # 2. Nonce at end
    n2 = bytearray(24)
    n2[20:] = short_nonce
    nonces.append(("End", bytes(n2)))

    # 3. Nonce is just the 4 bytes (should fail as it needs 24)
    # n3 = short_nonce
    
    # 4. Nonce is 4 bytes padded with something else?
    # Maybe the sequence number or timestamp is involved?
    seq = header[2:4]
    ts = header[4:8]
    ssrc = header[8:12]
    
    n4 = bytearray(24)
    n4[:4] = short_nonce
    n4[4:8] = ssrc
    nonces.append(("ShortNonce + SSRC", bytes(n4)))

    aads = [
        ("Full Header", header),
        ("Empty AAD", b""),
        ("Header without first byte", header[1:]),
    ]

    print("\n--- Starting Brute Force ---")
    for n_name, nonce in nonces:
        for a_name, aad in aads:
            try:
                decrypted = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                    bytes(payload), bytes(aad), bytes(nonce), key
                )
                print(f"SUCCESS! Nonce: {n_name}, AAD: {a_name}")
                print(f"Decrypted (hex): {decrypted.hex()[:64]}...")
                return
            except Exception as e:
                # print(f"Failed: Nonce={n_name}, AAD={a_name} ({e})")
                pass

    print("\nAll standard combinations failed. Trying non-IETF version...")
    for n_name, nonce in nonces:
        for a_name, aad in aads:
            try:
                # Some systems might use the non-IETF version which has different nonce size requirements
                # but our check_nacl_bindings said IETF is 24 bytes.
                pass
            except:
                pass

    print("Brute force finished. No success.")

if __name__ == "__main__":
    brute_force()

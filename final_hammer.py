import nacl.bindings
import struct

def final_hammer():
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

    # The library source shows it skips the extension BEFORE decryption.
    # This means the extension is NOT encrypted.
    # If it's not encrypted, it MUST be part of the AAD.
    
    payload = packet[12 + ext_header_len : -4]
    aad = packet[: 12 + ext_header_len]
    
    print(f"--- FINAL HAMMER ---")
    print(f"Payload Len: {len(payload)}, AAD Len: {len(aad)}")

    # Try every possible 24-byte nonce construction using the 4-byte short_nonce
    # and the 12-byte header.
    
    constructions = [
        ("ShortNonce + 20 zeros", bytes(short_nonce + b"\x00" * 20)),
        ("20 zeros + ShortNonce", bytes(b"\x00" * 20 + short_nonce)),
        ("Header + ShortNonce + 8 zeros", bytes(header + short_nonce + b"\x00" * 8)),
        ("ShortNonce + Header + 8 zeros", bytes(short_nonce + header + b"\x00" * 8)),
        ("Header + 8 zeros + ShortNonce", bytes(header + b"\x00" * 8 + short_nonce)),
        ("8 zeros + Header + ShortNonce", bytes(b"\x00" * 8 + header + short_nonce)),
        ("ShortNonce + 8 zeros + Header", bytes(short_nonce + b"\x00" * 8 + header)),
        ("8 zeros + ShortNonce + Header", bytes(b"\x00" * 8 + short_nonce + header)),
    ]

    for c_name, nonce in constructions:
        try:
            decrypted = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                bytes(payload), bytes(aad), bytes(nonce), key
            )
            print(f"\n!!! SUCCESS !!!")
            print(f"Construction: {c_name}")
            print(f"Decrypted: {decrypted.hex()[:64]}...")
            return
        except: pass

    print("\nFinal Hammer failed. One last check: maybe the extension IS encrypted but the library is wrong?")
    payload_alt = packet[12 : -4]
    aad_alt = header
    for c_name, nonce in constructions:
        try:
            decrypted = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                bytes(payload_alt), bytes(aad_alt), bytes(nonce), key
            )
            print(f"\n!!! SUCCESS (Alt) !!!")
            print(f"Construction: {c_name}")
            return
        except: pass

    print("No luck.")

if __name__ == "__main__":
    final_hammer()

import nacl.bindings
import pprint

print("--- nacl.bindings AEAD functions ---")
aead_funcs = [f for f in dir(nacl.bindings) if "aead" in f.lower()]
pprint.pprint(aead_funcs)

# Check nonce sizes
try:
    print(f"IETF Nonce Size: {nacl.bindings.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES}")
except:
    pass

try:
    # This might be the one for 24 bytes
    print(f"XChaCha20 Nonce Size: {nacl.bindings.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES}")
except:
    pass

# Let's check if there's a non-IETF version
try:
    print(f"Non-IETF Nonce Size: {nacl.bindings.crypto_aead_xchacha20poly1305_NPUBBYTES}")
except:
    pass

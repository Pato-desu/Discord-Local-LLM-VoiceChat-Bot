import interactions.api.voice.encryption as enc
import nacl
import sys

print(f"nacl_imported value: {enc.nacl_imported}")

# Check if we can actually use nacl
try:
    import nacl.secret
    import nacl.utils
    print("nacl.secret and nacl.utils are accessible.")
except Exception as e:
    print(f"Error accessing nacl: {e}")

# Search for mode strings in the module
print("\nSearching for encryption mode strings in interactions.api.voice.encryption...")
for attr in dir(enc):
    val = getattr(enc, attr)
    if isinstance(val, str) and ("aead" in val.lower() or "poly" in val.lower()):
        print(f"  - {attr}: {val}")

# Check the Encryption class if it exists
if hasattr(enc, "Encryption"):
    print("\nAttributes in Encryption class:")
    print(dir(enc.Encryption))

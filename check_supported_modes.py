import interactions.api.voice.encryption as enc
import sys

print(f"Encryption.SUPPORTED: {enc.Encryption.SUPPORTED}")

# Check if there's any other class or attribute that might have AEAD
print("\nChecking all attributes in interactions.api.voice.encryption for 'aead' or 'chacha':")
for attr in dir(enc):
    val = getattr(enc, attr)
    if isinstance(val, str) and ("aead" in val.lower() or "chacha" in val.lower()):
        print(f"  - {attr}: {val}")
    elif isinstance(val, list):
        for item in val:
            if isinstance(item, str) and ("aead" in item.lower() or "chacha" in item.lower()):
                print(f"  - {attr} (list item): {item}")

# Check if we can find where the selection happens
import interactions.api.voice.gateway as gateway
print("\nAttributes in interactions.api.voice.gateway:")
print(dir(gateway))

import interactions
import nacl
import interactions.api.voice.encryption as enc
import sys

print(f"Python version: {sys.version}")
print(f"Interactions version: {interactions.__version__}")
try:
    import nacl.secret
    print("PyNaCl (nacl) is installed and importable.")
except ImportError:
    print("PyNaCl (nacl) is NOT installed or NOT importable.")

print("\nAvailable attributes in interactions.api.voice.encryption:")
print(dir(enc))

try:
    from interactions.api.voice.encryption import EncryptionMode
    print("\nEncryptionMode enum members:")
    for mode in EncryptionMode:
        print(f"  - {mode.name}: {mode.value}")
except ImportError:
    print("\nEncryptionMode NOT found in interactions.api.voice.encryption")
except Exception as e:
    print(f"\nError accessing EncryptionMode: {e}")

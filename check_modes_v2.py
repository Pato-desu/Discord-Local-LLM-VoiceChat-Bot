import interactions
import interactions.api.voice.encryption as encryption
import nacl

print(f"interactions.py version: {interactions.__version__}")
print(f"nacl_imported: {encryption.nacl_imported}")

try:
    # In newer versions of interactions.py, Encryption might have a SUPPORTED attribute
    # or we can check the class itself
    print("\nAttributes in interactions.api.voice.encryption.Encryption:")
    print(dir(encryption.Encryption))
    
    if hasattr(encryption.Encryption, "SUPPORTED"):
        print(f"\nSUPPORTED modes: {encryption.Encryption.SUPPORTED}")
except Exception as e:
    print(f"Error inspecting Encryption class: {e}")

try:
    # Check if AEAD modes are mentioned in the file
    import inspect
    source = inspect.getsource(encryption)
    print("\nSearching for 'aead' in encryption.py source:")
    if "aead" in source.lower():
        print("✅ 'aead' found in source code!")
    else:
        print("❌ 'aead' NOT found in source code.")
except Exception as e:
    print(f"Error reading source: {e}")

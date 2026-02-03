import interactions.api.voice.encryption as encryption
import inspect

print(f"Attributes in interactions.api.voice.encryption:")
for name, obj in inspect.getmembers(encryption):
    if not name.startswith("__"):
        print(f"- {name}: {type(obj)}")

try:
    from interactions.api.voice.encryption import EncryptionMode
    print("\nEncryptionMode found!")
except ImportError:
    print("\nEncryptionMode NOT found in interactions.api.voice.encryption")

# Try to find where EncryptionMode is
import interactions.api.voice as voice
print(f"\nAttributes in interactions.api.voice:")
for name, obj in inspect.getmembers(voice):
    if not name.startswith("__"):
        print(f"- {name}: {type(obj)}")

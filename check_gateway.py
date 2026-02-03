import interactions.api.voice.encryption as encryption
import interactions.api.voice.voice_gateway as gateway
import inspect

print(f"nacl_imported value: {encryption.nacl_imported}")

print("\nAttributes in interactions.api.voice.voice_gateway:")
for name, obj in inspect.getmembers(gateway):
    if not name.startswith("__"):
        if name == "EncryptionMode":
             print(f"- {name}: {type(obj)}")
             for m_name, m_obj in inspect.getmembers(obj):
                 if not m_name.startswith("__"):
                     print(f"  - {m_name}")
        else:
             # Just list names to avoid clutter
             pass

# Let's try to find EncryptionMode in the gateway module specifically
try:
    from interactions.api.voice.voice_gateway import EncryptionMode
    print("\nEncryptionMode found in voice_gateway!")
    for mode in EncryptionMode:
        print(f"- {mode.name}: {mode.value}")
except ImportError:
    print("\nEncryptionMode NOT found in voice_gateway")

# Check for any other mode related constants
for name in dir(gateway):
    if "MODE" in name.upper():
        print(f"Found potential mode constant: {name} = {getattr(gateway, name)}")

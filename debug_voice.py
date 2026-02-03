import interactions
from interactions.api.voice.encryption import EncryptionMode
import nacl

print(f"interactions.py version: {interactions.__version__}")
print(f"PyNaCl version: {nacl.__version__}")

try:
    from interactions.api.voice.encryption import EncryptionMode
    print("\nSupported Encryption Modes in interactions.py:")
    for mode in EncryptionMode:
        print(f"- {mode.name}: {mode.value}")
except Exception as e:
    print(f"Error inspecting EncryptionMode: {e}")

# Check if interactions.py thinks it has encryption support
try:
    # In interactions.py 5.x, voice encryption is handled in the voice state
    # We can check if the necessary classes are available
    from interactions.api.voice.audio import AudioVolume
    print("\nVoice components seem to be available.")
except ImportError as e:
    print(f"\n❌ Voice components missing: {e}")

print("\nTesting if nacl is accessible to interactions.py...")
try:
    import nacl.secret
    import nacl.utils
    print("✅ nacl.secret and nacl.utils are importable.")
except Exception as e:
    print(f"❌ nacl submodules failed: {e}")

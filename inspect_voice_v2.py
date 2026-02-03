import interactions
import interactions.api.voice as voice
import interactions.api.voice.encryption as encryption
import inspect
import sys

print(f"Python version: {sys.version}")
print(f"Interactions version: {interactions.__version__}")

def list_members(obj, name):
    print(f"\n--- Members of {name} ---")
    try:
        for member_name, member_obj in inspect.getmembers(obj):
            if not member_name.startswith("__"):
                print(f"{member_name}: {type(member_obj)}")
    except Exception as e:
        print(f"Error listing members of {name}: {e}")

list_members(voice, "interactions.api.voice")
list_members(encryption, "interactions.api.voice.encryption")

print("\n--- Checking for EncryptionMode ---")
try:
    from interactions.api.voice.encryption import EncryptionMode
    print("Found in interactions.api.voice.encryption")
    for mode in EncryptionMode:
        print(f"  - {mode.name}: {mode.value}")
except ImportError:
    print("NOT found in interactions.api.voice.encryption")
except Exception as e:
    print(f"Error checking EncryptionMode in encryption: {e}")

try:
    from interactions.api.voice.models import EncryptionMode
    print("Found in interactions.api.voice.models")
except ImportError:
    print("NOT found in interactions.api.voice.models")

print("\n--- Checking for AEAD support in Recorder ---")
try:
    from interactions.api.voice.recorder import Recorder
    # Check if Recorder has AEAD related methods or attributes
    list_members(Recorder, "interactions.api.voice.recorder.Recorder")
except ImportError:
    print("Recorder NOT found")

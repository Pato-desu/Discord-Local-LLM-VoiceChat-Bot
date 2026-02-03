import inspect
import interactions.api.voice.encryption as enc
import interactions.api.voice.recorder as rec

try:
    print("--- Encryption.decrypt Source ---")
    print(inspect.getsource(enc.Decryption.decrypt))
except Exception as e:
    print(f"Error: {e}")

try:
    print("\n--- Recorder Source (Partial) ---")
    # List all methods in Recorder to find the packet handler
    for name, member in inspect.getmembers(rec.Recorder, predicate=inspect.isfunction):
        if "packet" in name.lower() or "receive" in name.lower():
            print(f"\nMethod: {name}")
            print(inspect.getsource(member))
except Exception as e:
    print(f"Error: {e}")

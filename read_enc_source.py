import inspect
import interactions.api.voice.encryption as enc

try:
    print("--- Encryption Source ---")
    print(inspect.getsource(enc.Encryption))
    print("\n--- Decryption Source ---")
    print(inspect.getsource(enc.Decryption))
except Exception as e:
    print(f"Error: {e}")

import inspect
import interactions.api.voice.audio as aud
import interactions.api.voice.encryption as enc

try:
    print("--- audio.py (RawInputAudio) Source ---")
    print(inspect.getsource(aud.RawInputAudio))
except Exception as e:
    print(f"Error reading RawInputAudio: {e}")

try:
    print("\n--- encryption.py (Decryption) Source ---")
    print(inspect.getsource(enc.Decryption))
except Exception as e:
    print(f"Error reading Decryption: {e}")

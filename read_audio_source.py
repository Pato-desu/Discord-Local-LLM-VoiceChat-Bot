import inspect
import interactions.api.voice.audio as aud

try:
    print("--- RawInputAudio Source ---")
    print(inspect.getsource(aud.RawInputAudio))
except Exception as e:
    print(f"Error: {e}")

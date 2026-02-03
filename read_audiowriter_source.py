import inspect
import interactions.api.voice.audio as aud

try:
    print("--- AudioWriter Source ---")
    print(inspect.getsource(aud.AudioWriter))
except Exception as e:
    print(f"Error: {e}")

import inspect
import interactions.api.voice.recorder as rec

try:
    print("--- Recorder Source ---")
    print(inspect.getsource(rec.Recorder))
except Exception as e:
    print(f"Error reading Recorder: {e}")

try:
    print("\n--- Searching for AudioWriter in recorder.py ---")
    for name, obj in inspect.getmembers(rec):
        if "writer" in name.lower():
            print(f"Found: {name}")
            print(inspect.getsource(obj))
except Exception as e:
    print(f"Error searching for writer: {e}")

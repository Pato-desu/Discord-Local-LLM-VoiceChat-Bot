import inspect
import interactions.api.voice.recorder as rec

try:
    print("--- Recorder Methods ---")
    for name, member in inspect.getmembers(rec.Recorder, predicate=inspect.isfunction):
        print(f"\nMethod: {name}")
        try:
            print(inspect.getsource(member))
        except:
            print("Could not get source.")
except Exception as e:
    print(f"Error: {e}")

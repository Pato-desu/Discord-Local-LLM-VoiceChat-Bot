import interactions.api.voice.voice_gateway as vg
import inspect

print("--- Searching for 'decrypt' in VoiceGateway ---")
for name, member in inspect.getmembers(vg.VoiceGateway, predicate=inspect.isfunction):
    try:
        source = inspect.getsource(member)
        if "decrypt(" in source:
            print(f"Found 'decrypt(' in method: {name}")
            print(source)
    except:
        pass

print("\n--- Searching for 'decrypt' in other voice modules ---")
import interactions.api.voice.recorder as rec
for name, member in inspect.getmembers(rec.Recorder, predicate=inspect.isfunction):
    try:
        source = inspect.getsource(member)
        if "decrypt(" in source:
            print(f"Found 'decrypt(' in Recorder method: {name}")
            print(source)
    except:
        pass

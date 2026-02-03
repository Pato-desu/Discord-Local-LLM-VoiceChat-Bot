import interactions.api.voice.voice_gateway as vg
import inspect

print("--- Searching for 'encrypt' in VoiceGateway ---")
for name, member in inspect.getmembers(vg.VoiceGateway, predicate=inspect.isfunction):
    try:
        source = inspect.getsource(member)
        if "encrypt(" in source:
            print(f"Found 'encrypt(' in method: {name}")
            print(source)
    except:
        pass

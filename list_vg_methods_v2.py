import interactions.api.voice.voice_gateway as vg
import inspect

print("--- VoiceGateway Methods ---")
for name, member in inspect.getmembers(vg.VoiceGateway, predicate=inspect.isfunction):
    print(name)

print("\n--- VoiceGateway Attributes ---")
print(dir(vg.VoiceGateway))

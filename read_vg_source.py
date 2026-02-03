import interactions.api.voice.voice_gateway as vg
import inspect

try:
    print("--- VoiceGateway Source ---")
    print(inspect.getsource(vg.VoiceGateway))
except Exception as e:
    print(f"Error: {e}")

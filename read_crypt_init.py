import interactions.api.voice.encryption as enc
import inspect

# Read the source of the Crypt class and its __init__
try:
    source = inspect.getsource(enc.Crypt)
    print("--- Crypt Class Source ---")
    print(source)
except Exception as e:
    print(f"Error getting Crypt source: {e}")

try:
    source = inspect.getsource(enc.Crypt.__init__)
    print("\n--- Crypt.__init__ Source ---")
    print(source)
except Exception as e:
    print(f"Error getting Crypt.__init__ source: {e}")

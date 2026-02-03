import interactions
import nacl
import nacl.secret
import sys

print(f"Python version: {sys.version}")
print(f"interactions.py version: {getattr(interactions, '__version__', 'unknown')}")
try:
    # Test PyNaCl
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    box = nacl.secret.SecretBox(key)
    print("✅ PyNaCl functionality test passed.")
except Exception as e:
    print(f"❌ PyNaCl functionality test failed: {e}")

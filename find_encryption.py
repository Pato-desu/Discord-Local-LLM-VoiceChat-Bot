import interactions
import pkgutil
import importlib

def find_attribute(package_name, attr_name):
    package = importlib.import_module(package_name)
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, attr_name):
                print(f"Found {attr_name} in {module_name}")
        except Exception:
            pass

print("Searching for 'EncryptionMode' in interactions package...")
find_attribute("interactions", "EncryptionMode")

print("\nSearching for 'SUPPORTED_MODES' or similar...")
find_attribute("interactions", "SUPPORTED_MODES")

import interactions.api.voice.encryption as enc
print(f"\nChecking interactions.api.voice.encryption.Encryption attributes:")
try:
    print(dir(enc.Encryption))
except Exception as e:
    print(f"Error: {e}")

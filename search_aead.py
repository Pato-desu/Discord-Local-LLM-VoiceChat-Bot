import interactions
import pkgutil
import importlib

def search_text(package_name, text):
    package = importlib.import_module(package_name)
    found = False
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        try:
            # We can't read the source directly easily, but we can check attributes
            module = importlib.import_module(module_name)
            for name in dir(module):
                if text.lower() in name.lower():
                    print(f"Found '{text}' in attribute '{name}' of module {module_name}")
                    found = True
        except Exception:
            pass
    return found

print("Searching for 'aead' in interactions package...")
if not search_text("interactions", "aead"):
    print("No 'aead' attributes found.")

print("\nSearching for 'xchacha' in interactions package...")
if not search_text("interactions", "xchacha"):
    print("No 'xchacha' attributes found.")

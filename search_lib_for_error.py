import os

lib_path = r"C:\Users\patri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\interactions"

print(f"Searching for 'error while encoding' in {lib_path}...")

found = False
for root, dirs, files in os.walk(lib_path):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "error while encoding" in content.lower():
                        print(f"Found in: {path}")
                        found = True
            except:
                pass

if not found:
    print("String not found. Searching for 'encoding'...")
    for root, dirs, files in os.walk(lib_path):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if "encoding" in content.lower():
                            # Just print the first few to avoid spam
                            pass 
                except:
                    pass

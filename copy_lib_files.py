import shutil
import os

lib_path = r"C:\Users\patri\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\interactions\api\voice"

files_to_copy = ["encryption.py", "audio.py"]

for f in files_to_copy:
    src = os.path.join(lib_path, f)
    dst = os.path.join(os.getcwd(), f"lib_{f}")
    try:
        shutil.copy(src, dst)
        print(f"Copied {f} to {dst}")
    except Exception as e:
        print(f"Error copying {f}: {e}")

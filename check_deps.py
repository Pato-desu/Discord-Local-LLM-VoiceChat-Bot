import importlib
import sys

dependencies = [
    "interactions",
    "faster_whisper",
    "TTS",
    "dotenv",
    "nacl",  # This is PyNaCl
    "google.generativeai",
    "torch"
]

print("--- DEPENDENCY CHECK ---")
missing = []
for dep in dependencies:
    try:
        importlib.import_module(dep)
        print(f"✅ {dep} is installed.")
    except ImportError:
        print(f"❌ {dep} is MISSING.")
        missing.append(dep)

if missing:
    print(f"\nMissing dependencies: {', '.join(missing)}")
    if "nacl" in missing:
        print("CRITICAL: PyNaCl is required for voice support. Run 'pip install PyNaCl'")
else:
    print("\nAll core dependencies are present.")

import interactions.api.voice.encryption as enc
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- Crypt Class Attributes ---")
print(dir(enc.Crypt))

print("\n--- Encryption Class Attributes ---")
print(dir(enc.Encryption))

# List available Gemini models
print("\n--- Available Gemini Models ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

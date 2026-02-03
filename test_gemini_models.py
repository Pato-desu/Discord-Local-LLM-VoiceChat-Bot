import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("No API key found in .env")
    exit()

genai.configure(api_key=api_key)

models_to_test = [
    'models/gemini-3-flash-preview',
    'models/gemini-2.5-flash-preview',
    'models/gemini-1.5-flash',
    'models/gemini-1.5-flash-latest',
    'models/gemini-pro'
]

print("--- Testing Gemini Models ---")
for model_name in models_to_test:
    try:
        print(f"Testing {model_name}...", end=" ", flush=True)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, are you working?")
        print(f"SUCCESS! Response: {response.text[:50]}...")
    except Exception as e:
        print(f"FAILED: {e}")

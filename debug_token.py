import os
import asyncio
from dotenv import load_dotenv
from interactions import Client, Intents

# Load .env
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

print("--- TOKEN DEBUG INFO ---")
if token:
    print(f"Token found: Yes")
    print(f"Token length: {len(token)}")
    print(f"Token start: {token[:5]}...")
    print(f"Token end: ...{token[-5:]}")
    print(f"Contains spaces: {' ' in token}")
    print(f"Is printable: {token.isprintable()}")
else:
    print("Token found: No")
    exit(1)

print("\n--- ATTEMPTING LOGIN ---")
bot = Client(intents=Intents.DEFAULT)

@bot.listen()
async def on_startup():
    print("✅ Login successful!")
    await bot.stop()

try:
    bot.start(token)
except Exception as e:
    print(f"❌ Login failed: {e}")

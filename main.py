import os
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import re
from pathlib import Path
from datetime import datetime
import struct

# Add current directory to PATH for ffmpeg
os.environ["PATH"] += os.pathsep + os.getcwd()
# Bypass Coqui TTS license prompt
os.environ["COQUI_TOS_AGREED"] = "1"

import interactions
from interactions import (
    Client,
    slash_command,
    SlashContext,
    SlashCommandOption,
    SlashCommandChoice,
    OptionType,
    Intents,
    Button,
    ButtonStyle,
    ActionRow,
    Embed,
)
from interactions.api.events import Ready
from interactions.api.voice.audio import AudioVolume

# Global flag to capture only one packet
packet_captured = False

# ── Monkey-patch for AEAD encryption support ──────────────────────────────────
def patch_interactions_voice():
    """
    Patches interactions.py to support aead_xchacha20_poly1305_rtpsize.
    Includes packet capture for debugging.
    """
    try:
        from interactions.api.voice.encryption import Encryption, Decryption, Crypt
        import nacl.bindings
        
        # 1. Patch Crypt.__init__ to store the secret key
        _original_init = Crypt.__init__
        def _patched_init(self, secret_key) -> None:
            _original_init(self, secret_key)
            self._secret_key = bytes(secret_key)
            self._incr_nonce = 0
            logger.info(f"Crypt initialized with key length: {len(self._secret_key)}")
        Crypt.__init__ = _patched_init

        # 2. Define the new encryption method
        def _encrypt_aead_xchacha20_poly1305_rtpsize(self, header: bytes, data) -> bytes:
            nonce = bytearray(24)
            nonce[:4] = struct.pack('>I', self._incr_nonce)
            self._incr_nonce = (self._incr_nonce + 1) & 0xFFFFFFFF
            
            encrypted = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_encrypt(
                bytes(data), bytes(header), bytes(nonce), self._secret_key
            )
            return header + encrypted + nonce[:4]

        # 3. Define the new decryption method with capture
        def _decrypt_aead_xchacha20_poly1305_rtpsize(self, header: bytes, data) -> bytes:
            global packet_captured
            payload = data[:-4]
            short_nonce = data[-4:]
            
            # Standard attempt
            nonce = bytearray(24)
            nonce[:4] = short_nonce
            
            try:
                return nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                    bytes(payload), bytes(header), bytes(nonce), self._secret_key
                )
            except Exception as e:
                # Capture the first failed voice packet for analysis
                if not packet_captured and len(payload) > 50:
                    packet_captured = True
                    try:
                        with open("failed_packet.bin", "wb") as f:
                            f.write(header + data)
                        with open("failed_key.txt", "w") as f:
                            f.write(self._secret_key.hex())
                        logger.info("!!! CAPTURED FAILED PACKET AND KEY TO failed_packet.bin and failed_key.txt !!!")
                    except Exception as capture_err:
                        logger.error(f"Failed to capture packet: {capture_err}")
                
                # Re-throwing with the full error message for the user
                raise RuntimeError(f"Decryption failed: {e}")

        # 4. Patch Encryption.encrypt to handle the new mode
        _original_encrypt = Encryption.encrypt
        def _patched_encrypt(self, mode: str, header: bytes, data) -> bytes:
            if mode == "aead_xchacha20_poly1305_rtpsize":
                return _encrypt_aead_xchacha20_poly1305_rtpsize(self, header, data)
            return _original_encrypt(self, mode, header, data)

        # 5. Patch Decryption.decrypt to handle the new mode
        _original_decrypt = Decryption.decrypt
        def _patched_decrypt(self, mode: str, header: bytes, data) -> bytes:
            if mode == "aead_xchacha20_poly1305_rtpsize":
                return _decrypt_aead_xchacha20_poly1305_rtpsize(self, header, data)
            return _original_decrypt(self, mode, header, data)

        # Inject everything
        Encryption.encrypt = _patched_encrypt
        Decryption.decrypt = _patched_decrypt
        
        # Update supported modes
        if "aead_xchacha20_poly1305_rtpsize" not in Encryption.SUPPORTED:
            Encryption.SUPPORTED = ("aead_xchacha20_poly1305_rtpsize",) + Encryption.SUPPORTED
            
        logger.info("Successfully applied full AEAD monkey-patch with capture.")
    except Exception as e:
        logger.error(f"Failed to patch interactions.py: {e}")

# ── Imports and setup ─────────────────────────────────────────────────────────
from faster_whisper import WhisperModel
from TTS.api import TTS
from dotenv import load_dotenv, set_key
import google.generativeai as genai
import torch

# Fix for PyTorch 2.6+ breaking TTS with weights_only=True default
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

# ── Logging configuration ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler("bot.log", maxBytes=5*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DiscordBot")

# Apply the patch immediately
patch_interactions_voice()

# ── Load environment variables ────────────────────────────────────────────────
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if DISCORD_TOKEN:
    DISCORD_TOKEN = DISCORD_TOKEN.strip()

if not DISCORD_TOKEN or not GUILD_ID:
    logger.error("Missing DISCORD_TOKEN or GUILD_ID in .env")
    exit(1)

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    logger.warning("GOOGLE_API_KEY not found in environment variables.")

# ── Configuration ─────────────────────────────────────────────────────────────
MODEL_SIZE = "base"
LANGUAGE = "en"
ROLE = "You are a helpful, witty, and friendly AI assistant named Saya. You are chatting with users in a Discord voice channel. Keep your responses concise and conversational."

# TTS settings
TTS_MODE = os.getenv("TTS_MODE", "default")
CURRENT_SPEAKER_WAV = os.getenv("SELECTED_FILE_PATH", "./sample/sample_default.wav")
AUDIO_DIR = Path(os.path.abspath("./audio"))
AUDIO_DIR.mkdir(exist_ok=True)

# Global state
bot = Client(intents=Intents.ALL)
stt_model = WhisperModel(MODEL_SIZE, device="cuda" if torch.cuda.is_available() else "cpu", compute_type="float16" if torch.cuda.is_available() else "int8")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to("cuda" if torch.cuda.is_available() else "cpu")

is_connected = False
current_channel = None
recording_lock = asyncio.Lock()
is_playing_response = False

# ── Bot Events ────────────────────────────────────────────────────────────────

@bot.listen(Ready)
async def on_ready():
    global is_connected, current_channel
    is_connected = False
    
    logger.info(f"Bot is ready! Logged in as {bot.user.username}")
    
    # Wait for cache to populate and gateway to stabilize
    logger.info("Waiting 10s for gateway to stabilize and cache to populate...")
    await asyncio.sleep(10)

    try:
        logger.info(f"Fetching guild with ID: {GUILD_ID}")
        guild = await bot.fetch_guild(GUILD_ID)
    except Exception as e:
        logger.error(f"Failed to fetch guild: {e}")
        return

    if not guild:
        logger.error(f"Could not find guild with ID {GUILD_ID}.")
        return

    # Auto-connect logic
    logger.info("Scanning channels for auto-connection...")
    all_states = guild.voice_states
    target_channel = None
    
    for channel in guild.channels:
        if channel.type != interactions.ChannelType.GUILD_VOICE:
            continue
            
        # Filter voice states for this channel
        members_in_channel = [vs for vs in all_states if vs.channel and vs.channel.id == channel.id]
        logger.info(f"Channel '{channel.name}' (ID: {channel.id}) has {len(members_in_channel)} members.")
        
        if len(members_in_channel) == 1:
            target_channel = channel
            logger.info(f"Found suitable channel: {channel.name}")
            break
    
    if target_channel:
        try:
            logger.info(f"Attempting to auto-connect to channel: {target_channel.name}")
            voice = await target_channel.connect()
            is_connected = True
            current_channel = target_channel
            logger.info("Successfully connected to voice.")
            
            # Voice recording is now enabled - encryption issues have been fixed
            asyncio.create_task(start_recording(voice, str(AUDIO_DIR)))
            
        except Exception as e:
            logger.error(f"Failed to auto-connect: {e}")
    else:
        logger.info("No suitable channel found for auto-connection (need exactly 1 person in a channel).")

async def reconnect_voice(channel):
    try:
        if channel:
            logger.info(f"Attempting to reconnect to {channel.name}...")
            return await channel.connect()
        logger.error("Channel not found for reconnect.")
    except Exception as e:
        logger.error(f"Error reconnecting to voice channel: {e}")
    return None

async def start_recording(voice_state, output_dir: str):
    global current_channel, is_playing_response
    
    if hasattr(start_recording, "_is_running") and start_recording._is_running:
        return
    start_recording._is_running = True

    try:
        while is_connected:
            if not voice_state or not voice_state.ws or not voice_state.ws.socket:
                voice_state = await reconnect_voice(current_channel) if current_channel else None
                if not voice_state:
                    logger.error("Failed to restore connection. Retrying in 5s...")
                    await asyncio.sleep(5)
                    continue

            if is_playing_response:
                await asyncio.sleep(1)
                continue

            try:
                async with recording_lock:
                    logger.debug("Starting recording cycle...")
                    await voice_state.start_recording(output_dir=output_dir, encoding="wav")
                    await asyncio.sleep(3)
                    await voice_state.stop_recording()
                    logger.debug("Stopped recording cycle.")

                recordings = list(voice_state.recorder.output.items())
                for user_id, file in recordings:
                    audio_path = file.get("path") if isinstance(file, dict) else file
                    if audio_path and os.path.exists(audio_path):
                        asyncio.create_task(process_audio_for_user(voice_state, user_id, audio_path))

            except Exception as e:
                logger.error(f"Error in recording cycle: {e}")
                await asyncio.sleep(1)
            
            await asyncio.sleep(0.5)

    finally:
        start_recording._is_running = False
        logger.info("Recording loop exited.")

async def transcribe_audio(audio_path: str) -> str:
    def _transcribe_blocking(path):
        segments, info = stt_model.transcribe(path, language=LANGUAGE, beam_size=5)
        return segments, info

    try:
        segments, info = await asyncio.to_thread(_transcribe_blocking, audio_path)
        texts = [seg.text for seg in segments if hasattr(seg, 'text')]
        return " ".join(texts)
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        return ""

async def process_audio_for_user(voice_state, user_id: int, audio_path: str):
    global is_playing_response
    full_text = await transcribe_audio(audio_path)
    if not full_text.strip():
        return

    logger.info(f"User said: {full_text}")
    is_playing_response = True
    
    try:
        await voice_state.play(AudioVolume("trigger.wav"))
    except:
        pass

    if TTS_MODE == "default":
        await generate_and_play_response(voice_state, user_id, full_text)
    else:
        await generate_and_play_voiceclone_response(voice_state, user_id, full_text, CURRENT_SPEAKER_WAV)

async def generate_gemini_response(text: str) -> str:
    # LOCKED to the only working model for this account
    model_name = 'models/gemini-3-flash-preview'
    
    try:
        logger.info(f"Generating response with model: {model_name}")
        model = genai.GenerativeModel(model_name)
        full_prompt = f"System Role: {ROLE}\n\nUser: {text}"
        response = await asyncio.to_thread(model.generate_content, full_prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return "I'm sorry, I encountered an error while thinking."

async def generate_and_play_response(voice_state, user_id, text: str):
    global is_playing_response
    answer = await generate_gemini_response(text)
    logger.info(f"Gemini reply: {answer}")

    sentences = re.split(r'(?<=[\.!\?])\s+', answer.strip())
    if not sentences:
        is_playing_response = False
        return

    ts = datetime.now().strftime("%Y%m%d%H%M%S")

    def tts_to_file(sentence, idx):
        out = AUDIO_DIR / f"response_{ts}_{idx}.wav"
        tts.tts_to_file(text=sentence, speaker="Ana Florence", language=LANGUAGE, file_path=str(out))
        return str(out)

    is_playing_response = True
    try:
        first_wav = await asyncio.to_thread(tts_to_file, sentences[0], 0)
        play_task = asyncio.create_task(voice_state.play(AudioVolume(first_wav)))
        for idx, sent in enumerate(sentences[1:], start=1):
            next_wav = await asyncio.to_thread(tts_to_file, sent, idx)
            await play_task
            play_task = asyncio.create_task(voice_state.play(AudioVolume(next_wav)))
        await play_task
    except Exception as e:
        logger.error(f"Error in TTS playback: {e}")
    finally:
        is_playing_response = False

async def generate_and_play_voiceclone_response(voice_state, user_id, text: str, speaker_wav: str):
    global is_playing_response
    answer = await generate_gemini_response(text)
    logger.info(f"Gemini reply: {answer}")

    sentences = re.split(r'(?<=[\.!\?])\s+', answer.strip())
    if not sentences:
        is_playing_response = False
        return

    ts = datetime.now().strftime("%Y%m%d%H%M%S")

    def tts_clone_to_file(sentence, idx):
        out = AUDIO_DIR / f"clone_{ts}_{idx}.wav"
        tts.tts_to_file(text=sentence, speaker_wav=speaker_wav, language=LANGUAGE, file_path=str(out))
        return str(out)

    is_playing_response = True
    try:
        first_wav = await asyncio.to_thread(tts_clone_to_file, sentences[0], 0)
        play_task = asyncio.create_task(voice_state.play(AudioVolume(first_wav)))
        for idx, sent in enumerate(sentences[1:], start=1):
            next_wav = await asyncio.to_thread(tts_clone_to_file, sent, idx)
            await play_task
            play_task = asyncio.create_task(voice_state.play(AudioVolume(next_wav)))
        await play_task
    except Exception as e:
        logger.error(f"Error in TTS playback: {e}")
    finally:
        is_playing_response = False

@slash_command(name="join", description="Connect to a voice channel.")
async def join(ctx: SlashContext):
    global is_connected, current_channel
    if is_connected:
        return await ctx.send("I'm already connected.")
    if not ctx.author.voice:
        return await ctx.send("❗ Please join a voice channel and try again.")

    vs = await ctx.author.voice.channel.connect()
    is_connected = True
    current_channel = ctx.author.voice.channel
    await ctx.send("✅ Connected.")
    # Recording is now enabled - encryption issues have been fixed
    asyncio.create_task(start_recording(vs, str(AUDIO_DIR)))


@slash_command(name="leave", description="Disconnect from the voice channel.")
async def leave(ctx: SlashContext):
    global is_connected, current_channel
    if ctx.voice_state:
        await ctx.voice_state.disconnect()
        is_connected = False
        current_channel = None
        await ctx.send("🛑 Disconnected.")
    else:
        await ctx.send("🤷 I'm not connected.")

@slash_command(
    name="saya_tts",
    description="Switch TTS mode: default or clone",
    options=[
        SlashCommandOption(
            name="mode",
            description="Select TTS mode",
            required=True,
            type=OptionType.STRING,
            choices=[
                SlashCommandChoice(name="default", value="default"),
                SlashCommandChoice(name="clone",   value="clone"),
            ],
        )
    ]
)
async def saya_tts(ctx: SlashContext, mode: str):
    global TTS_MODE
    if mode not in ("default", "clone"):
        return await ctx.send("❗ Invalid mode.", ephemeral=True)
    TTS_MODE = mode
    set_key(".env", "TTS_MODE", mode)
    await ctx.send(f"✅ TTS mode set to: `{mode}`")

try:
    bot.start(DISCORD_TOKEN)
except Exception as e:
    logger.error(f"Bot failed to start: {e}")
    raise
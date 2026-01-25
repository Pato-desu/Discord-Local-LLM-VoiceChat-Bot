# External Integrations

**Analysis Date:** 2026-01-25

## APIs & External Services

**Discord API:**
- interactions.py library - WebSocket-based voice gateway and HTTP API communication
  - SDK/Client: interactions (handles voice recording, playback, encryption)
  - Auth: `DISCORD_TOKEN` environment variable
  - Endpoints: Discord Gateway (voice) and REST API (slash commands)

**Google Generative AI (Gemini):**
- LLM conversational responses via Google's Gemini API
  - Service: models/gemini-3-flash-preview (locked to this model per code comments in `main.py` line 267)
  - SDK/Client: google-generativeai library
  - Auth: `GOOGLE_API_KEY` environment variable
  - Usage: Generate conversational responses to user input in `generate_gemini_response()` function (`main.py` lines 265-277)

## Data Storage

**Databases:**
- None - Stateless application

**File Storage:**
- Local filesystem only
  - Temporary audio recordings: `./audio/` directory
  - Sample voice files for cloning: `./sample/` directory
    - Default: `./sample/sample_default.wav`
    - Configurable via `SELECTED_FILE_PATH` environment variable
  - Generated TTS responses: `./audio/response_*.wav` files
  - Voice clone responses: `./audio/clone_*.wav` files
  - Logging: `./bot.log` (rotating file handler, 5MB max per file, 5 backups)

**Caching:**
- None - Models loaded into memory at startup
  - Whisper STT model ("base" size) loaded in `main.py` line 113
  - Coqui TTS XTTS v2 model loaded in `main.py` line 114
  - Google Generative AI models loaded on-demand via API

## Authentication & Identity

**Auth Provider:**
- Discord Token-based (OAuth2) - Bot uses token from `DISCORD_TOKEN`
- Google API Key - Service account key for Generative AI
- No user authentication - Bot operates at guild/server level via `GUILD_ID`

**Implementation:**
- Discord: Token provided in `.env` and loaded via `dotenv.load_dotenv()` at `main.py` line 82
- Google: API key configured via `genai.configure(api_key=GOOGLE_API_KEY)` at `main.py` line 96
- Validation occurs at startup - missing tokens cause `exit(1)` at `main.py` lines 88-93

## Monitoring & Observability

**Error Tracking:**
- None - No external error tracking service

**Logs:**
- File-based logging via RotatingFileHandler to `./bot.log`
- Console output via StreamHandler
- Log level: INFO
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Max size: 5MB per file, 5 backup files retained
- Logger name: "DiscordBot"

## CI/CD & Deployment

**Hosting:**
- Local machine deployment via Windows batch script `bot.bat`
- No cloud platform integration

**CI Pipeline:**
- None

## Environment Configuration

**Required env vars:**
- `DISCORD_TOKEN` - Bot authentication token (required, exits if missing)
- `GUILD_ID` - Discord server ID (required, exits if missing)
- `GOOGLE_API_KEY` - Google Gemini API key (optional, warns if missing but continues)

**Optional env vars:**
- `TTS_MODE` - "default" or "clone" (defaults to "default")
- `SELECTED_FILE_PATH` - Path to speaker WAV for voice cloning (defaults to "./sample/sample_default.wav")
- `LANGUAGE` - Language code for Whisper and TTS (defaults to "en")
- `ROLE` - System prompt for Gemini LLM (defaults to predefined assistant persona)

**Secrets location:**
- `.env` file in project root (not committed to git per `.gitignore`)

## Webhooks & Callbacks

**Incoming:**
- Discord Gateway events (Ready event at `main.py` line 124)
- Voice state changes via interactions.py framework

**Outgoing:**
- Discord API: Slash command responses via `ctx.send()` calls
- Discord voice: Audio playback via `voice_state.play()` calls
- Model responses: Generated TTS audio files written to disk

## Voice Channel Operations

**Recording:**
- Recording initiated via `voice_state.start_recording()` in `start_recording()` function (`main.py` lines 189-231)
- 3-second recording cycles in loop
- Output: WAV format audio files
- Encryption: Handled by interactions.py with patched Crypt class (`main.py` lines 33-50)
- User audio isolated by user_id and stored in recorder output dictionary

**Playback:**
- Audio playback via `voice_state.play(AudioVolume(file_path))` calls
- Supported format: WAV files
- Volume control: AudioVolume wrapper around file paths
- Sequential playback of sentences split by regex pattern `(?<=[\.!\?])\s+`

## Model Integrations

**Speech-to-Text:**
- Provider: OpenAI Whisper (via faster-whisper library)
- Model: "base" size (configurable via MODEL_SIZE variable)
- Device: CUDA (float16) if available, CPU (int8) fallback
- Language: Configurable via LANGUAGE variable (defaults to "en")
- Implementation: `transcribe_audio()` function (`main.py` lines 233-244)

**Text-to-Speech:**
- Provider: Coqui TTS XTTS v2 (multilingual, multi-dataset)
- Default voice: "Ana Florence"
- Voice cloning: Custom WAV file input via speaker_wav parameter
- Device: CUDA if available, CPU fallback
- Implementation: `generate_and_play_response()` and `generate_and_play_voiceclone_response()` functions (`main.py` lines 279-339)

---

*Integration audit: 2026-01-25*

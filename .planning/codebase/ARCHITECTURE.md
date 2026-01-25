# Architecture

**Analysis Date:** 2026-01-25

## Pattern Overview

**Overall:** Event-Driven Monolithic Architecture with Asynchronous I/O

**Key Characteristics:**
- Single-file application (`main.py`) with all logic colocated
- Event-driven design using Discord bot framework (`interactions.py`)
- Asynchronous/concurrent processing with asyncio
- Three-stage audio pipeline: recording → transcription → response generation → synthesis → playback
- Global state management for connection and playback flags

## Layers

**Presentation Layer (Discord API):**
- Purpose: Handle Discord bot interactions and voice channel operations
- Location: `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py` (lines 341-390)
- Contains: Slash command handlers (`/join`, `/leave`, `/saya_tts`)
- Depends on: `interactions` library, voice state objects
- Used by: Discord client, channel members triggering commands

**Audio Input Layer (Recording & Transcription):**
- Purpose: Capture voice audio from Discord and convert to text
- Location: `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py` (lines 189-244)
- Contains: Recording loop (`start_recording`), transcription function (`transcribe_audio`)
- Depends on: `faster_whisper` (STT model), voice state recorder, asyncio
- Used by: Response generation layer

**LLM Response Layer (AI Generation):**
- Purpose: Generate conversational responses using Google Gemini API
- Location: `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py` (lines 265-277)
- Contains: Gemini API integration (`generate_gemini_response`)
- Depends on: `google.generativeai`, system role configuration
- Used by: Audio output layer

**Audio Output Layer (Text-to-Speech & Playback):**
- Purpose: Convert text responses to speech and play in voice channel
- Location: `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py` (lines 279-339)
- Contains: Two TTS modes - default speaker and voice cloning, audio playback
- Depends on: `TTS` (Coqui library), sentence splitting, audio directory
- Used by: Voice state for Discord playback

**Infrastructure & Setup Layer:**
- Purpose: Initialize models, logging, configuration, encryption patches
- Location: `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py` (lines 1-120, 392-396)
- Contains: Model loading, logging configuration, environment variables, voice encryption patching
- Depends on: PyTorch, logging, dotenv, os/Path utilities
- Used by: All other layers

## Data Flow

**Voice Interaction Flow:**

1. **Connection Initialization** (`on_ready` event, lines 123-177)
   - Bot starts, listens for Ready event
   - Fetches Discord guild and scans voice channels
   - Auto-connects to channel with exactly 1 member
   - Spawns recording task

2. **Audio Capture Loop** (`start_recording`, lines 189-231)
   - Continuously records 3-second audio chunks from all users in channel
   - Stores recordings in `recorder.output` dictionary keyed by user_id
   - Checks `is_playing_response` flag to avoid overlapping I/O
   - Triggers processing for each new recording

3. **Transcription** (`process_audio_for_user`, `transcribe_audio`, lines 246-244)
   - Extracts audio file path from recorder output
   - Runs Whisper model in thread pool to convert speech to text
   - Returns transcribed text or empty string if failed

4. **LLM Response Generation** (`generate_gemini_response`, lines 265-277)
   - Sends user text + system role prompt to Gemini 3.5 Flash API
   - Awaits response in thread pool
   - Returns AI-generated reply or error message

5. **Text-to-Speech Synthesis** (`generate_and_play_response` or `generate_and_play_voiceclone_response`, lines 279-339)
   - Splits response into sentences (split on `.!?`)
   - Generates WAV file for each sentence using Coqui TTS
   - Sequentially plays audio files while next sentence is being synthesized
   - Sets `is_playing_response` flag during playback

6. **Playback** (via `voice_state.play(AudioVolume)`, lines 256-258, 299-303, 330-334)
   - Feeds synthesized audio to Discord voice connection
   - Manages sequential playback of sentence chunks

**State Management:**

```
Global State Variables:
├── is_connected: bool (connection status)
├── current_channel: Channel object (active voice channel)
├── is_playing_response: bool (prevents recording during playback)
├── recording_lock: asyncio.Lock (synchronizes recording access)
├── TTS_MODE: str ("default" or "clone")
├── CURRENT_SPEAKER_WAV: str (voice clone reference file path)
├── stt_model: WhisperModel (loaded Whisper base model)
├── tts: TTS (loaded Coqui XTTS v2 model)
└── bot: Client (Discord bot instance)
```

## Key Abstractions

**Voice Connection State:**
- Purpose: Encapsulates Discord voice channel connection and recording state
- Examples: `voice_state` object passed through event handlers
- Pattern: Object with methods like `start_recording()`, `stop_recording()`, `play()`, `disconnect()`

**Audio Recording Loop:**
- Purpose: Manages continuous recording cycle with error recovery
- Pattern: Async function that runs indefinitely, checks connection state, handles reconnection
- Key mechanism: `recording_lock` prevents concurrent recording operations; `is_playing_response` prevents recording during bot speech

**TTS Pipeline:**
- Purpose: Abstracts sentence-by-sentence audio synthesis
- Pattern: Split text → generate file for each chunk → queue playback sequentially
- Abstraction: Handles both default speaker and voice cloning modes transparently

**Encryption Patching:**
- Purpose: Workaround for voice encryption handling in interactions.py library
- Pattern: Monkey-patches `Crypt.__init__` to properly store secret key
- Location: `patch_interactions_voice()` function (lines 33-50)

## Entry Points

**Bot Startup:**
- Location: `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py` (lines 392-396)
- Triggers: Script execution via `bot.bat` or direct Python invocation
- Responsibilities: Initialize all global models, patch encryption, establish Discord connection

**Ready Event:**
- Location: `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py` (lines 123-177)
- Triggers: Discord bot ready after authentication
- Responsibilities: Fetch guild, find suitable voice channel, auto-connect and start recording

**Slash Commands:**
- `/join` (lines 341-354): User manually joins voice channel
- `/leave` (lines 357-366): User disconnects bot from channel
- `/saya_tts` (lines 368-390): Switch between default and voice clone TTS modes

**Recording Loop (Background Task):**
- Location: `start_recording()` async function (lines 189-231)
- Spawned by: `on_ready` or `/join` command
- Responsibilities: Continuous recording, connection monitoring, audio file routing

## Error Handling

**Strategy:** Graceful degradation with logging

**Patterns:**

- **Voice Connection Failures:** Automatic reconnection attempt with 5-second retry interval (lines 179-187, 199-203)
- **Recording Errors:** Log error, continue loop, attempt reconnection if needed (lines 223-225)
- **Transcription Failures:** Return empty string, skip audio processing (lines 242-243)
- **Gemini API Failures:** Return error message, continue conversation (lines 276-277)
- **TTS Failures:** Log error but continue playback cycle; try next sentence (lines 305-306, 336-337)
- **General Exceptions:** Try-catch blocks with logging at each async boundary; finally blocks ensure state cleanup

## Cross-Cutting Concerns

**Logging:**
- Framework: Python `logging` with `RotatingFileHandler`
- Configuration: Lines 68-75, logs to `bot.log` (5MB rotated, 5 backups) and stderr
- Usage: INFO for major events, DEBUG for recording cycles, ERROR for failures
- Logger instance: `logger = logging.getLogger("DiscordBot")` (line 76)

**Validation:**
- Token validation: Check DISCORD_TOKEN and GUILD_ID on startup (lines 84-93)
- Mode validation: Slash command validates TTS mode is "default" or "clone" (line 386)
- Audio path validation: Check file exists before processing (line 220)
- No structured input validation framework; relies on exception handling

**Authentication:**
- Discord: Token-based via environment variable (line 84)
- Google Gemini: API key-based via environment variable (line 86)
- No application-level session management; Discord library handles token refresh

**Concurrency & Synchronization:**
- Recording lock: Prevents concurrent `start_recording()` and `stop_recording()` calls (line 210)
- Playback flag: `is_playing_response` prevents recording during bot speech (lines 205-207, 253, 296, 327)
- One recording loop per voice connection (singleton pattern via `start_recording._is_running` flag)

---

*Architecture analysis: 2026-01-25*

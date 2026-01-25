# Codebase Structure

**Analysis Date:** 2026-01-25

## Directory Layout

```
Discord-Local-LLM-VoiceChat-Bot/
├── main.py                          # Main bot application (395 lines)
├── requirements.txt                 # Python dependencies
├── bot.bat                          # Windows batch startup script
├── .env                             # Environment variables (Discord token, Google API key, Guild ID)
├── README.md                        # Project documentation
├── .gitignore                       # Git ignore rules
│
├── audio/                           # Generated TTS output directory
│   ├── response_[timestamp]_[idx].wav
│   └── clone_[timestamp]_[idx].wav
│
├── sample/                          # Sample audio files for voice cloning reference
│   └── sample_default.wav           # Default speaker voice sample
│
├── [Debug/Test Scripts Root]        # Development debugging and troubleshooting scripts
│   ├── brute_force_*.py             # Encryption key recovery attempts
│   ├── check_*.py                   # Dependency and environment verification
│   ├── debug_*.py                   # Voice/token debugging utilities
│   ├── read_*.py                    # Library inspection scripts
│   └── [other diagnostic scripts]   # Various inspection/testing utilities
│
└── [System Directories]
    ├── .git/                        # Git repository metadata
    ├── .venv_backup/                # Backup virtual environment (not committed)
    ├── .planning/                   # GSD planning artifacts
    ├── .claude/                     # Claude configuration
    └── __pycache__/                 # Python bytecode cache
```

## Directory Purposes

**Project Root:**
- Purpose: Main application package, configuration, and entry point
- Contains: Core application logic, startup scripts, configuration files
- Key files: `main.py` (complete application), `.env` (secrets), `requirements.txt` (dependencies)

**`audio/` Directory:**
- Purpose: Runtime output for generated TTS audio files
- Contains: Timestamped WAV files from TTS synthesis (`response_*.wav`, `clone_*.wav`)
- Generated: Yes, at runtime by Coqui TTS
- Committed: No, generated files, not in repository
- Cleanup: Manual deletion needed; no auto-cleanup mechanism

**`sample/` Directory:**
- Purpose: Reference audio files for voice cloning mode
- Contains: Pre-recorded voice samples used as reference for XTTS speaker cloning
- Key files: `sample_default.wav` (default reference voice)
- Generated: No
- Committed: Yes (part of repository)
- Usage: Path referenced in `CURRENT_SPEAKER_WAV` environment variable; can be customized

**Debug/Test Scripts Root:**
- Purpose: Development-time troubleshooting and diagnostics (not part of production application)
- Contains: Encryption verification, dependency checking, library inspection, debug utilities
- Pattern: Individual scripts prefixed with `brute_force_`, `check_`, `debug_`, `read_`, `search_`, `find_`, `inspect_`, `print_`, `list_`, `nuclear_`, `ultimate_`, `final_hammer_`
- Not imported: These are standalone utilities, not part of main.py execution path

## Key File Locations

**Entry Points:**
- `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py`: Main application; instantiates Discord bot, loads models, defines all event handlers and command logic
- `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/bot.bat`: Windows startup batch script; activates venv and runs main.py

**Configuration:**
- `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/.env`: Environment variables (DISCORD_TOKEN, GUILD_ID, GOOGLE_API_KEY, TTS_MODE, SELECTED_FILE_PATH)
- `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/requirements.txt`: Python package dependencies (interactions.py, faster-whisper, TTS, python-dotenv, aiohttp, PyNaCl, google-generativeai, transformers)

**Core Logic:**
- `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py`: All application logic
  - Lines 1-120: Imports, model initialization, configuration, logging setup
  - Lines 123-177: `on_ready()` event handler for auto-connection
  - Lines 179-244: Recording loop and audio transcription pipeline
  - Lines 265-339: LLM response generation and TTS synthesis/playback
  - Lines 341-390: Slash command handlers
  - Lines 392-396: Bot startup

**Testing:**
- No test files; testing is manual or via debug scripts
- Test scripts located in project root (various `check_*.py`, `debug_*.py`, etc.)

**Generated Output:**
- `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/audio/`: TTS synthesis output
- `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/bot.log`: Application logs (rotating, 5MB max)

## Naming Conventions

**Files:**
- Main application: `main.py` (single monolithic file)
- Batch scripts: `*.bat` (Windows startup scripts)
- Configuration: `.env` (environment variables, `.gitignore`)
- Documentation: `*.md` (README.md, markdown)
- Debugging utilities: `check_*.py`, `debug_*.py`, `read_*.py`, `find_*.py`, etc. (descriptive prefix + purpose)

**Directories:**
- Audio output: `audio/` (lowercase, single purpose)
- Sample files: `sample/` (lowercase, single purpose)
- Hidden/system: `.git/`, `.venv_backup/`, `.planning/`, `.claude/` (dotfile convention for non-source)
- Cache: `__pycache__/` (Python standard cache)

**Functions & Classes (within main.py):**
- Event handlers: `on_*` prefix (e.g., `on_ready`)
- Async pipelines: Descriptive verb phrases (e.g., `start_recording`, `transcribe_audio`, `generate_gemini_response`)
- Slash commands: Command name prefix (e.g., `join`, `leave`, `saya_tts`)
- Helper functions: Descriptive names (e.g., `patch_interactions_voice`, `reconnect_voice`)

**Variables:**
- Global state: UPPERCASE (e.g., `DISCORD_TOKEN`, `GUILD_ID`, `MODEL_SIZE`, `LANGUAGE`, `TTS_MODE`)
- Configuration constants: UPPERCASE (e.g., `AUDIO_DIR`, `CURRENT_SPEAKER_WAV`, `ROLE`)
- Runtime state: lowercase or mixed case (e.g., `is_connected`, `current_channel`, `recording_lock`, `is_playing_response`)
- Local/temporary: lowercase (e.g., `voice_state`, `full_text`, `answer`, `sentences`)

## Where to Add New Code

**New Feature (Within Voice Interaction Flow):**
- Primary code: `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py` (add function + hook into pipeline)
- Consider insertion points:
  - Audio input modifications: Add function after `transcribe_audio()` (line 244)
  - LLM modifications: Add function near `generate_gemini_response()` (line 265)
  - Audio output modifications: Add function near TTS functions (lines 279-339)
  - New commands: Add slash command handler before bot startup (before line 392)

**New Voice Command:**
- Location: `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py` (lines 341-390, after `/saya_tts` command)
- Pattern: Use `@slash_command` decorator; implement async function with `ctx: SlashContext` parameter
- Example structure:
  ```python
  @slash_command(name="command_name", description="Description")
  async def command_name(ctx: SlashContext, param: str):
      # Access current voice state: ctx.voice_state
      # Send response: await ctx.send("message")
  ```

**New Model or Service Integration:**
- Location: `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py` (lines 52-114 for imports and initialization)
- Pattern:
  1. Add import at top (lines 52-57)
  2. Add environment variable to .env
  3. Initialize model instance as global variable (lines 112-114)
  4. Create wrapper function to use it
  5. Hook into pipeline

**Utilities or Helpers:**
- Location: `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/main.py` (lines 33-50 for utility patches, or create new section)
- Note: No separate module structure; add inline or as standalone debug script if experimental

**Configuration Changes:**
- Environment variables: Edit `C:/Users/patri/Documents/Repositories/Discord-Local-LLM-VoiceChat-Bot/.env`
- Hardcoded constants: Edit lines 100-109 (MODEL_SIZE, LANGUAGE, ROLE, TTS_MODE, CURRENT_SPEAKER_WAV, AUDIO_DIR)

## Special Directories

**`.venv_backup/` Directory:**
- Purpose: Backup of Python virtual environment (contains site-packages, Python interpreter)
- Generated: Yes
- Committed: No (excluded by .gitignore)
- Usage: Fallback if primary venv corrupted; takes substantial disk space (gigabytes)

**`__pycache__/` Directory:**
- Purpose: Python bytecode cache for faster imports
- Generated: Yes, automatically by Python
- Committed: No (excluded by .gitignore)
- Cleanup: Safe to delete; will be regenerated

**`.planning/codebase/` Directory:**
- Purpose: GSD (Get Shit Done) analysis documents
- Contents: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md
- Generated: Yes, by analysis tools
- Committed: Yes, part of documentation

**`audio/` Directory:**
- Purpose: Generated TTS audio output
- Pattern: Timestamped files with indices for multi-sentence responses
  - `response_[YYYYMMDDHHMMSS]_[index].wav`: Default speaker TTS
  - `clone_[YYYYMMDDHHMMSS]_[index].wav`: Voice-cloned TTS
- Cleanup: Manual; consider periodic cleanup of old files (no auto-deletion)

---

*Structure analysis: 2026-01-25*

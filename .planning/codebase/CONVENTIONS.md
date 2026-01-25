# Coding Conventions

**Analysis Date:** 2026-01-25

## Naming Patterns

**Files:**
- Snake case with descriptive names: `main.py`, `check_deps.py`, `debug_voice.py`
- Utility/test scripts follow descriptive pattern: `brute_force_v2.py`, `test_gemini_models.py`, `final_hammer.py`
- Patch/analysis scripts use prefixes: `check_*`, `debug_*`, `read_*`, `search_*`, `inspect_*`

**Functions:**
- Snake case throughout: `patch_interactions_voice()`, `start_recording()`, `transcribe_audio()`, `process_audio_for_user()`
- Private/internal functions prefixed with underscore: `_original_torch_load`, `_patched_torch_load`, `_transcribe_blocking()`
- Async functions use same naming convention: `async def generate_gemini_response()`, `async def start_recording()`

**Variables:**
- Global state constants use UPPER_SNAKE_CASE: `MODEL_SIZE`, `LANGUAGE`, `DISCORD_TOKEN`, `GUILD_ID`, `GOOGLE_API_KEY`, `TTS_MODE`, `CURRENT_SPEAKER_WAV`, `AUDIO_DIR`, `ROLE`
- Boolean flags use is/has prefix: `is_connected`, `is_playing_response`, `has_extension`
- Regular variables use snake_case: `recording_lock`, `current_channel`, `stt_model`, `tts`, `bot`, `logger`
- Loop variables are concise: `user_id`, `file`, `sent`, `idx`, `channel`

**Types/Classes:**
- Imported from libraries, not defined in main codebase (minimal custom classes)
- Built-in/library types used directly: `Client`, `SlashContext`, `Embed`, `Button`

## Code Style

**Formatting:**
- No automatic formatter detected (no .prettierrc, pyproject.toml, or .flake8)
- Indentation: 4 spaces (Python standard)
- Line length: Not enforced (lines extend to ~100+ chars in some cases)
- String style: Double quotes preferred in f-strings and regular strings

**Linting:**
- No linter configuration file detected
- Code follows PEP 8 informally but not strictly enforced

## Import Organization

**Order (observed in `main.py`):**

1. Standard library imports (os, asyncio, logging, re, pathlib, datetime, struct)
2. Third-party library imports (interactions, faster_whisper, TTS, dotenv, google.generativeai, torch)
3. Relative/conditional imports and setup code

**Pattern:**
```python
import os
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import re
from pathlib import Path
from datetime import datetime
import struct

# Environmental setup
os.environ["PATH"] += os.pathsep + os.getcwd()
os.environ["COQUI_TOS_AGREED"] = "1"

# Framework imports
import interactions
from interactions import (
    Client,
    slash_command,
    SlashContext,
    ...
)

# Domain-specific imports
from faster_whisper import WhisperModel
from TTS.api import TTS
from dotenv import load_dotenv, set_key
```

**Path Aliases:**
- No path aliases detected (no tsconfig.json, PYTHONPATH configuration)
- Direct imports from installed packages

## Error Handling

**Patterns:**
- Try/except blocks used throughout for fault tolerance
- Bare `except:` clauses used for non-critical failures (lines 257-258 in audio playback)
- Named exception catching with logging:
  ```python
  except Exception as e:
      logger.error(f"Failed to fetch guild: {e}")
  ```
- Try/except/finally for resource cleanup:
  ```python
  try:
      # operation
  except Exception as e:
      logger.error(f"Error: {e}")
  finally:
      # cleanup
      start_recording._is_running = False
  ```
- Exit on critical failures:
  ```python
  if not DISCORD_TOKEN or not GUILD_ID:
      logger.error("Missing DISCORD_TOKEN or GUILD_ID in .env")
      exit(1)
  ```

**No custom exception classes detected** - relies on built-in exceptions from libraries

## Logging

**Framework:** Python `logging` module

**Configuration (`main.py`, lines 68-76):**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler("bot.log", maxBytes=5*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DiscordBot")
```

**Patterns:**
- INFO level for operational events: `logger.info(f"Bot is ready! Logged in as {bot.user.username}")`
- WARNING for optional/missing configs: `logger.warning("GOOGLE_API_KEY not found in environment variables.")`
- ERROR for failures and exceptions: `logger.error(f"Failed to fetch guild: {e}")`
- DEBUG for detailed flow tracking: `logger.debug("Starting recording cycle...")`
- File rotation: 5MB max size with 5 backups kept
- Both file (`bot.log`) and console output

## Comments

**When to Comment:**
- Section headers use comment blocks with dashes for organization:
  ```python
  # ── Voice encryption setup ──────────────────────────────────
  # ── Bot Events ────────────────────────────────────────────────────────────────
  ```
- Inline comments explain non-obvious logic:
  ```python
  # Check for extension bit
  has_extension = bool(header[0] & 0x10)
  ```
- Comments explain workarounds and patches:
  ```python
  # Fix for PyTorch 2.6+ breaking TTS with weights_only=True default
  # Basic voice encryption setup.
  ```

**JSDoc/TSDoc:**
- Docstrings used minimally
- Function docstrings present for patched functions:
  ```python
  def patch_interactions_voice():
      """
      Basic voice encryption setup.
      """
  ```
- Most functions lack docstrings

## Function Design

**Size:** Functions range from 5-50 lines. Recording loop is longer (~45 lines).

**Parameters:**
- Explicit parameters preferred
- Type hints not used (no annotations detected)
- Async functions use standard parameter patterns
- Global state accessed via `global` keyword when needed

**Return Values:**
- Mostly async operations that return task handles or None
- String returns for transcription: `await transcribe_audio()` → `str`
- Exception handling instead of None returns (functions don't return error codes)

## Module Design

**Exports:**
- Single entry point: `bot.start(DISCORD_TOKEN)` at module bottom
- No `__all__` definition detected
- All functions at module level (no class organization)

**Barrel Files:**
- Not applicable (single main.py module)
- Utility scripts are standalone (not imported)

## Async/Await Patterns

**Asyncio Usage:**
- Event-driven architecture with `@bot.listen(Ready)` decorator
- Slash commands decorated with `@slash_command()`
- Async context managers: `async with recording_lock:`
- Task creation: `asyncio.create_task(start_recording(vs, str(AUDIO_DIR)))`
- Blocking operations wrapped in threads: `await asyncio.to_thread(_transcribe_blocking, audio_path)`
- Sleep for retries: `await asyncio.sleep(5)`

**Concurrency Patterns:**
- Global lock for recording: `recording_lock = asyncio.Lock()`
- Flag-based state management: `is_playing_response`, `is_connected`
- Task tracking with function attributes: `start_recording._is_running = True`

## Configuration Management

**Environment Variables:**
- Loaded via `load_dotenv()` from .env file
- Retrieved with defaults: `os.getenv("TTS_MODE", "default")`
- Type conversion not applied (all strings)
- Validation on startup for required vars

**Configuration Constants:**
- Module-level constants for static config: `MODEL_SIZE = "base"`, `LANGUAGE = "en"`
- System config via Path: `AUDIO_DIR = Path(os.path.abspath("./audio"))`

## Code Quality Observations

**Strengths:**
- Consistent error handling with logging
- Clear variable naming (descriptive, followable)
- Organized import sections
- Modular async task design

**Areas for Improvement:**
- No type hints (would improve IDE support)
- No docstrings for most functions
- Bare except clauses in some places
- No input validation on function parameters
- Global state management could use encapsulation

---

*Convention analysis: 2026-01-25*

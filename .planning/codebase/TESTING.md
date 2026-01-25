# Testing Patterns

**Analysis Date:** 2026-01-25

## Test Framework

**Runner:**
- No test framework detected (pytest, unittest, or vitest not in requirements)
- Manual testing scripts present: `test_gemini_models.py`, `check_deps.py`, `debug_voice.py`

**Assertion Library:**
- Not applicable (no automated test framework)

**Run Commands:**
```bash
# No automated test suite available
# Manual verification only:
python check_deps.py              # Verify dependencies installed
python test_gemini_models.py      # Test Gemini API connectivity
python debug_voice.py             # Debug voice encryption/encoding
```

## Test File Organization

**Location:**
- Ad-hoc test scripts at root level, not co-located with source
- Scripts prefixed with `test_`, `check_`, `debug_`, `inspect_` for identification

**Naming:**
- `test_gemini_models.py` - API model verification
- `check_deps.py` - Dependency validation
- `check_encryption_final.py` - Encryption verification
- `debug_voice.py` - Voice component debugging
- `inspect_crypt_and_models.py` - Library inspection
- `debug_token.py` - Token validation

**Structure:**
```
C:\Users\patri\Documents\Repositories\Discord-Local-LLM-VoiceChat-Bot/
├── main.py                         # Application code
├── test_gemini_models.py           # Manual test
├── check_deps.py                   # Dependency check
├── debug_voice.py                  # Voice debugging
└── [other manual test scripts]
```

## Test Structure

**No automated test suite pattern** - Code uses manual verification scripts.

**Manual Test Pattern (`check_deps.py`):**
```python
import importlib
import sys

dependencies = [
    "interactions",
    "faster_whisper",
    "TTS",
    # ...
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
else:
    print("\nAll core dependencies are present.")
```

**Manual Test Pattern (`test_gemini_models.py`):**
```python
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
    # ...
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
```

## Mocking

**Framework:** Not used

**Patterns:**
- Manual library patching for testing/debugging:
  ```python
  _original_torch_load = torch.load
  def _patched_torch_load(*args, **kwargs):
      if 'weights_only' not in kwargs:
          kwargs['weights_only'] = False
      return _original_torch_load(*args, **kwargs)
  torch.load = _patched_torch_load
  ```

- Interactions.py voice encryption patch:
  ```python
  def patch_interactions_voice():
      try:
          from interactions.api.voice.encryption import Crypt
          _original_init = Crypt.__init__
          def _patched_init(self, secret_key) -> None:
              _original_init(self, secret_key)
              self._secret_key = bytes(secret_key)
              logger.info(f"Crypt initialized with key length: {len(self._secret_key)}")
          Crypt.__init__ = _patched_init
          logger.info("Voice encryption initialized successfully.")
      except Exception as e:
          logger.error(f"Failed to initialize voice encryption: {e}")
  ```

**What to Mock:**
- External library behavior for compatibility (PyTorch, interactions.py encryption)
- Not observed for API calls or local operations in test scripts

**What NOT to Mock:**
- Network calls (test scripts make real API calls to Gemini)
- File I/O (real files checked: `failed_packet.bin`, `.env`)
- Environment setup (real .env file read)

## Fixtures and Factories

**Test Data:**
- Real audio files stored in `./sample/` directory
- Sample file used for voice cloning: `./sample/sample_default.wav`
- Binary data files for encryption testing: `failed_packet.bin`, `failed_key.txt`

**No factory/fixture pattern** - Scripts use file I/O directly:
```python
with open("failed_packet.bin", "rb") as f:
    packet = f.read()
with open("failed_key.txt", "r") as f:
    key_hex = f.read().strip()
    key = bytes.fromhex(key_hex)
```

**Location:**
- Sample files: `./sample/`
- Test data files: Root directory (alongside scripts)

## Coverage

**Requirements:** Not enforced - no coverage tool configured

**View Coverage:**
- Not applicable (no test framework)

## Test Types

**Unit Tests:**
- Not present - no unit test framework

**Integration Tests:**
- Manual scripts test integrations:
  - `test_gemini_models.py` - Tests Gemini API connectivity
  - `debug_voice.py` - Tests voice encryption/encoding
  - `check_deps.py` - Tests dependency availability
  - Brute force scripts (`brute_force_v2.py`, `final_hammer.py`) test encryption parsing

**E2E Tests:**
- Not automated
- Application tested manually by running `python main.py` and using Discord commands

## Verification Scripts

**Dependency Verification (`check_deps.py`):**
- Imports each required dependency
- Reports missing packages
- Used before initial bot startup

**API Connectivity Testing (`test_gemini_models.py`):**
- Tests multiple Gemini model versions
- Requires valid `.env` with `GOOGLE_API_KEY`
- Verifies API responsiveness

**Voice Debug (`debug_voice.py`):**
- Checks PyNaCl and interactions.py versions
- Verifies encryption mode support
- Validates voice components availability
- Tests nacl submodule accessibility

**Encryption Debugging (`brute_force_v2.py`, `final_hammer.py`):**
- Brute force tests decryption combinations
- Tests different AAD (Associated Authenticated Data) construction
- Tests different nonce constructions with XChaCha20-Poly1305
- Used to troubleshoot voice packet encryption

## Logging for Debugging

**Logger Configuration:**
- `logging.basicConfig()` sets INFO level for normal operation
- File logging: `RotatingFileHandler("bot.log", maxBytes=5*1024*1024, backupCount=5)`
- Console output via `StreamHandler()`
- Logger name: `"DiscordBot"`

**Debug Output:**
- `logger.debug()` calls for detailed flow tracking (recording cycles)
- `logger.info()` for operational events
- `logger.error()` for failures
- `logger.warning()` for missing optional config

**Manual Debugging Tools:**
```python
print(f"Full Packet Hex: {packet.hex()}")           # inspect_voice_v2.py
print(f"Payload length: {len(payload)}")            # brute_force_v2.py
print(f"!!! SUCCESS !!!")                           # final_hammer.py (debug output)
```

## Testing Checklist

**Before Deployment:**
1. Run `check_deps.py` - verify all required packages installed
2. Run `test_gemini_models.py` - verify Gemini API key is valid and API accessible
3. Run `debug_voice.py` - verify voice encryption components available
4. Test `/join` command manually - verify bot can connect to voice
5. Test `/leave` command manually - verify bot can disconnect
6. Test `/saya_tts` command manually - verify TTS mode switching
7. Monitor `bot.log` for errors during voice chat

## Current Testing Gaps

**Unautomated Testing:**
- Voice recording and transcription (manual testing only)
- TTS audio generation (manual testing only)
- Gemini response generation (manual testing only)
- Voice playback (manual testing only)
- Auto-connect on ready event (manual testing)
- Discord command parsing (relies on interactions.py)
- Encryption/decryption of voice packets (encryption module patched, not fully tested)

**No Automated Coverage:**
- No unit tests for any core functions
- No integration test suite
- No regression test suite
- No CI/CD pipeline detected

---

*Testing analysis: 2026-01-25*

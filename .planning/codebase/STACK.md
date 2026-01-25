# Technology Stack

**Analysis Date:** 2026-01-25

## Languages

**Primary:**
- Python 3.10+ - Full application implementation in `main.py`

## Runtime

**Environment:**
- Python 3.10+
- CUDA 12.1 (required for GPU acceleration with NVIDIA GPUs)
- FFmpeg (for audio encoding/decoding)

**Package Manager:**
- pip
- Lockfile: Not present (uses `requirements.txt`)

## Frameworks

**Core:**
- interactions.py - Discord bot framework for slash commands, voice connections, and event handling
- google-generativeai - Google Gemini API client for LLM-based conversational responses

**Speech Processing:**
- faster-whisper - OpenAI Whisper model for speech-to-text (STT) transcription
- TTS (Coqui TTS) - Text-to-speech synthesis with voice cloning support via XTTS v2

**ML/Deep Learning:**
- torch (PyTorch) 2.2.0+cu121 - Core deep learning framework for model inference
- torchaudio 2.2.0+cu121 - Audio processing backend for PyTorch
- transformers 4.33.0 - Hugging Face transformers for model loading

**Utilities:**
- python-dotenv - Environment variable management from `.env` files
- PyNaCl - Cryptographic library for Discord voice encryption
- aiohttp - Async HTTP client for Discord API communication

## Key Dependencies

**Critical:**
- interactions - Main Discord bot library providing voice recording, playback, and gateway management
- faster-whisper - STT model execution (uses model_size="base" by default)
- google-generativeai - External LLM integration via Google Gemini API
- TTS/xtts_v2 - TTS model for response audio generation (multilingual, multi-dataset variant)

**Infrastructure:**
- torch - GPU-accelerated inference (float16 on CUDA, int8 on CPU)
- torchaudio - Audio tensor manipulation and conversion
- PyNaCl - XSalsa20-Poly1305 voice encryption handling for Discord voice channels

## Configuration

**Environment:**
- Configuration via `.env` file
- Key variables required:
  - `DISCORD_TOKEN` - Bot authentication token
  - `GUILD_ID` - Discord guild/server ID
  - `GOOGLE_API_KEY` - Google Generative AI API key
  - `TTS_MODE` - "default" or "clone" (optional, defaults to "default")
  - `SELECTED_FILE_PATH` - Path to speaker WAV file for voice cloning (optional)
  - `LANGUAGE` - ISO language code (e.g., "en")

**Build:**
- Startup via `bot.bat` script on Windows or direct `python main.py`
- Virtual environment activation in `bot.bat`: `venv\Scripts\activate.bat`
- PyTorch installed separately with CUDA 12.1 support:
  ```
  pip install torch==2.2.0+cu121 torchvision==0.17.0+cu121 torchaudio==2.2.0+cu121 --index-url https://download.pytorch.org/whl/cu121
  ```

## Platform Requirements

**Development:**
- Python 3.10+
- FFmpeg binary (Windows: ffmpeg.exe in PATH or project root)
- CUDA 12.1 toolkit (optional but recommended for GPU acceleration)
- cuDNN (NVIDIA accelerated compute library)
- cudnn_ops64_9.dll for Whisper CUDA support
- Minimum 7GB VRAM for GPU models (tested on RTX 3060 12GB, RTX 4060 8GB)
- 6GB+ system RAM

**Production:**
- Windows (primary target based on bot.bat and relative path handling)
- Python 3.10+ runtime
- FFmpeg installed and available in PATH
- CUDA 12.1 for GPU support
- Sufficient disk space for audio caching in `./audio/` directory

---

*Stack analysis: 2026-01-25*

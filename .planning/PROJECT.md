# Discord Voice LLM Bot

## What This Is

A Discord bot that listens to voice channels, transcribes speech with Whisper, processes it through Gemini LLM, and responds with synthesized voice using Coqui TTS. The bot supports both default TTS and voice cloning modes for personalized responses.

## Core Value

Reliable voice-to-voice conversation with an LLM in Discord voice channels. Users speak, bot responds naturally - the interaction must be stable and dependable.

## Requirements

### Validated

Existing capabilities that work:

- ✓ Discord voice channel connection and management — existing
- ✓ Slash commands (/join, /leave, /saya_tts) — existing
- ✓ Voice recording captures 3-second audio chunks — existing
- ✓ Speech-to-text transcription via Whisper (base model) — existing
- ✓ Gemini API integration for conversational responses — existing
- ✓ Text-to-speech synthesis with Coqui TTS XTTS v2 — existing
- ✓ Voice cloning mode with custom speaker samples — existing
- ✓ Audio playback sequencing in voice channel — existing
- ✓ Auto-reconnection on connection failures — existing
- ✓ Logging system with rotation (bot.log) — existing
- ✓ Environment-based configuration (.env) — existing
- ✓ Recording lock to prevent concurrent operations — existing
- ✓ Playback flag to avoid recording during bot speech — existing

### Active

Current scope to fix and improve:

- [ ] Fix voice decryption for incoming audio when users speak
- [ ] Handle AEAD RTP Extension properly in decryption flow
- [ ] Improve error recovery for voice connection issues
- [ ] Simplify deployment with clear setup documentation
- [ ] Add configuration validation on startup
- [ ] Improve logging for voice encryption debugging
- [ ] Clean up debug scripts from repository

### Out of Scope

- Multi-server concurrent support — single-server deployment sufficient
- Advanced monitoring/analytics dashboard — basic logging is enough
- Changing LLM provider — staying with Gemini API
- Real-time streaming conversation — sequential flow works well
- Mobile app or web interface — Discord-only interaction
- Persistent conversation memory across sessions — stateless is fine

## Context

### Technical Challenge

The bot currently fails to decrypt incoming voice from users with error: "Decryption failed"

**Root Cause Identified:**
- Discord uses `aead_xchacha20_poly1305_rtpsize` encryption mode
- This mode requires RTP Extension data as Additional Authenticated Data (AAD)
- The interactions.py library strips RTP Extension before decryption
- This causes authentication failure in AEAD decryption
- Bot can receive "silence" (no RTP extension) but fails on actual speech

**Current Workaround:**
- Monkey-patch applied to `Crypt.__init__` to store secret key properly
- XChaCha20 algorithm support added
- Still fails due to RTP Extension handling

### Environment

- Development and deployment on Windows
- CUDA 12.1 with NVIDIA GPU (RTX 3060/4060 tested)
- FFmpeg for audio processing
- Python 3.10+ with asyncio event loop

### User Flow

1. Bot auto-connects to voice channel with exactly 1 member on startup
2. User speaks in voice channel (3-second chunks recorded)
3. Bot transcribes audio with Whisper
4. Bot sends transcription to Gemini API with system role
5. Bot receives response and synthesizes speech with Coqui TTS
6. Bot plays audio response in voice channel (sentence by sentence)
7. Loop continues until user leaves or bot disconnects

## Constraints

- **LLM Provider**: Must use Gemini API (google-generativeai) — no model changes
- **Tech Stack**: Python 3.10+, interactions.py, faster-whisper, Coqui TTS — existing stack works
- **Platform**: Windows deployment target — bot.bat startup script
- **GPU**: CUDA 12.1 required for model inference performance — 6GB+ VRAM recommended
- **Audio**: FFmpeg binary required in PATH or project root
- **Library Flexibility**: Can fork/patch interactions.py or find workarounds — whatever works to fix decryption

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use interactions.py for Discord | Full voice support with recording/playback APIs | ⚠️ Revisit — voice decryption issue requires patch or replacement |
| Gemini API for LLM | User preference, fast responses, good quality | ✓ Good |
| Coqui TTS XTTS v2 for speech | Multilingual support, voice cloning capability | ✓ Good |
| Whisper base model for STT | Good accuracy/speed balance, runs on GPU | ✓ Good |
| 3-second recording chunks | Balances latency and natural speech capture | — Pending user feedback |
| Monkey-patch for encryption | Quick workaround to test XChaCha20 | ⚠️ Revisit — didn't fully solve the problem |

---
*Last updated: 2026-02-03 after initialization*

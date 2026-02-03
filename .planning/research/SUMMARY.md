# Project Research Summary

**Project:** Discord Local LLM VoiceChat Bot - Voice Encryption Fix
**Domain:** Discord Voice Bot (Python, interactions.py)
**Researched:** 2026-02-03
**Confidence:** HIGH

## Executive Summary

This is a Discord voice bot that enables natural conversation through voice channels using local/API-based AI services (Whisper STT, Gemini LLM, Coqui TTS). The bot is functionally complete and deployed but currently broken due to Discord's November 2024 deprecation of xsalsa20_poly1305 encryption modes in favor of mandatory AEAD encryption (aead_xchacha20_poly1305_rtpsize). The interactions.py library lacks native support for these modes, requiring a local patch.

Research confirms the recommended approach is to refactor the existing monkey-patch implementation to properly handle RTP header extensions in the Additional Authenticated Data (AAD) before decryption. The current patch correctly implements AEAD encryption but fails to handle RTP extensions, causing decryption to work for silence packets but fail for actual speech. This is a surgical fix requiring changes to only 2-3 files in the encryption layer, with zero impact on the rest of the bot architecture.

The critical risk is the approaching March 1, 2026 deadline for DAVE (Discord Audio & Video End-to-End Encryption) protocol support, which represents a more fundamental architectural change than the current AEAD fix. The immediate focus should be fixing AEAD encryption to restore voice functionality, followed by production hardening (error recovery, monitoring, health checks), then planning for DAVE migration before the deadline.

## Key Findings

### Recommended Stack

The bot's existing stack is appropriate and requires minimal changes. PyNaCl (already installed) has native AEAD support via `nacl.secret.Aead` and `nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt()` since version 1.4.0+. The encryption fix requires only adding proper RTP extension handling and AEAD mode support to the monkey-patch layer.

**Core technologies:**
- **PyNaCl 1.6.0+**: AEAD encryption via nacl.bindings — Already in use, has XChaCha20Poly1305 IETF support
- **interactions.py 5.x (patched)**: Discord API wrapper — Keep current version with local encryption patches
- **struct (stdlib)**: Binary RTP header parsing — Required for extracting nonce and parsing extension headers

**Supporting infrastructure:**
- Whisper (faster-whisper) for STT
- Gemini API for LLM processing
- Coqui TTS for voice synthesis
- FFmpeg/Opus for audio encoding

The recommended approach is to continue with monkey-patching rather than forking the library or switching frameworks. This preserves the existing architecture while providing a clean migration path when interactions.py adds native AEAD support.

### Expected Features

Production-ready Discord voice bots require reliability infrastructure beyond basic conversation functionality. Research shows that most failures stem from connection instability, insufficient error handling, and poor deployment processes.

**Must have (table stakes):**
- **Voice decryption fix** — Current blocker; bot cannot receive voice without AEAD support
- **Graceful shutdown** — Prevents voice connection leaks and zombie processes
- **Auto-reconnection** — Voice connections drop frequently; manual restart is unacceptable
- **Configuration validation** — Fail fast on startup with clear error messages for missing env vars
- **Structured logging** — JSON logs with levels for production debugging
- **Error recovery** — Hierarchical handlers (command → global) that distinguish retriable vs fatal errors
- **Health check endpoint** — External monitoring tools need to verify bot status
- **Rate limit handling** — Parse X-RateLimit headers, implement request queuing to avoid 24h bans

**Should have (competitive):**
- **Latency monitoring** — Track STT→LLM→TTS→playback timing (production bots target <800ms total)
- **Retry logic with backoff** — External API failures (LLM, TTS) shouldn't crash bot
- **Audio buffer management** — Prevent stuttering without adding latency
- **Voice Activity Detection (VAD)** — Accurate speech start/stop detection (Silero VAD is 99% accurate)
- **Conversation context management** — LLM conversation history with token limit management

**Defer (v2+):**
- **Interruption handling** — Complex; requires streaming architecture rewrite
- **Queue system for multiple users** — Only needed if concurrent users are common
- **Observability dashboard** — Grafana/Prometheus metrics valuable but can start with basic health checks
- **Canary deployments** — Premature until serving multiple production servers
- **Multi-instance coordination** — Not needed until 2500+ guilds (sharding threshold)

### Architecture Approach

The bot uses a single-file monolithic architecture (465 lines) with event-driven asyncio and global state management. This is appropriate for the current scale (single guild, single instance). The voice pipeline is 3-stage: Recording (3s loop) → Transcription (Whisper) → LLM (Gemini) → TTS (Coqui) → Playback (queue).

**Major components:**
1. **Encryption patch layer** — Monkey-patches interactions.api.voice.encryption at import time; adds AEAD support but needs RTP extension fix
2. **Recording loop** — Continuous 3s audio capture with async processing; receives encrypted packets from voice gateway
3. **Audio pipeline** — Sequential STT→LLM→TTS chain using asyncio.to_thread for blocking calls
4. **Command handlers** — Slash commands (/join, /leave) with global state flags (is_connected, current_channel)

**Critical integration point:** The decryption happens in `Recorder.decrypt()` → `RawInputAudio.ingest()` chain. The current bug is that RTP extensions are stripped AFTER decryption (audio.py:58-61) but AEAD requires them in the AAD BEFORE decryption. Fix must move extension detection before the decrypt call.

**Recommended refactoring:** Extract encryption patch from main.py (lines 36-119) into separate modules (voice_crypto.py for pure crypto logic, voice_patches.py for monkey-patching coordination). This improves testability and allows conditional patching when native support arrives.

### Critical Pitfalls

1. **Incorrect RTP Extension Handling in AEAD** — The AAD must include RTP extensions, but developers often omit them or include the wrong portion. This causes "Decryption failed" errors specifically for speech (which has extensions) while silence packets work. Fix by constructing AAD as: 12-byte RTP header + RTP extension (if 0xBEDE marker present), then decrypt payload. Test with both silence and speech packets.

2. **Missing Modern Encryption Mode Support** — As of November 18, 2024, Discord deprecated all modes except aead_xchacha20_poly1305_rtpsize and aead_aes256_gcm_rtpsize. Bots using outdated libraries receive "No compatible encryption modes" errors. Verify library supports required modes before deployment; pin versions in requirements.txt.

3. **WebSocket 4006 Error from Privileged Intents** — Bot connects then immediately disconnects with 4006 error if privileged intents (Presence, Server Members) are requested in code but not enabled in Discord Developer Portal. Verify all required intents are toggled on in portal before deployment.

4. **Missing DAVE Protocol Support (March 1, 2026 Deadline)** — Starting March 1, 2026, all bots must support DAVE (Discord Audio & Video End-to-End Encryption) or they cannot join voice channels. This is a hard deadline requiring framework support. Check if interactions.py roadmap includes DAVE support; prepare migration plan.

5. **Session State Desynchronization** — Voice sessions have complex state machines across multiple layers (gateway session, voice websocket, UDP socket, library state). Network issues or improper error handling can desync states, leaving bot appearing connected but unable to send/receive audio. Implement comprehensive state monitoring, reasonable timeouts (30s for connection), and idempotent cleanup logic.

## Implications for Roadmap

Based on research, suggested phase structure prioritizes restoring voice functionality, then production hardening, then future-proofing for DAVE:

### Phase 1: Voice Encryption Fix (Critical - Week 1)
**Rationale:** Current blocker preventing all voice receive functionality. Must be fixed before any other work is meaningful. Research shows this is a surgical fix with high confidence.

**Delivers:** Working voice decryption with AEAD encryption modes; bot can receive and transcribe speech

**Addresses:**
- Voice decryption fix (table stakes feature)
- RTP extension handling (critical pitfall #1)
- Modern encryption mode support (critical pitfall #2)

**Avoids:**
- Incorrect AAD construction causing speech decryption failures
- Hardcoded nonce construction incompatible with varying packet sizes
- Missing encryption mode fallback for hardware compatibility

**Implementation approach:**
- Refactor monkey-patch into voice_crypto.py (pure crypto) + voice_patches.py (patching logic)
- Add RTP extension detection BEFORE decryption in AEAD decrypt method
- Implement proper AAD construction: header (12 bytes) + extension header (4 + length*4 bytes)
- Add unit tests using captured failed_packet.bin and failed_key.txt
- Validate against discord.py PR #9953 reference implementation

### Phase 2: Production Reliability (Essential - Week 2)
**Rationale:** Once voice works, production deployment requires error recovery, monitoring, and operational visibility. These are table stakes for any production bot.

**Delivers:** Bot that survives transient failures, provides operational visibility, and handles common error scenarios gracefully

**Addresses:**
- Graceful shutdown (prevents connection leaks)
- Auto-reconnection (handles voice connection drops)
- Configuration validation (fail fast with clear errors)
- Structured logging (production debugging)
- Error recovery (hierarchical handlers)
- Health check endpoint (external monitoring)

**Avoids:**
- WebSocket 4006 errors from intent configuration (pitfall #3)
- Session desynchronization from missing reconnect logic (pitfall #5)
- Silent failures masking production issues
- Insufficient permission handling causing confusing errors

**Uses:**
- Python logging with JSON formatters for structured logs
- Environment variables for configuration management
- Discord API permission checks before voice operations

### Phase 3: Production Hardening (Important - Week 3)
**Rationale:** Enhances reliability and user experience beyond MVP. Addresses performance and UX issues that emerge in production.

**Delivers:** Bot with monitoring, rate limiting, retry logic, and professional UX

**Addresses:**
- Rate limit handling (avoid 24h bans)
- Latency monitoring (track pipeline timing)
- Retry logic with backoff (LLM/TTS failures)
- Audio buffer management (prevent stuttering)

**Implements:**
- Exponential backoff for transient failures
- Per-component latency tracking (STT, LLM, TTS, playback)
- Discord API rate limit header parsing
- Bounded audio buffers with overflow strategy

**Avoids:**
- Unbounded packet buffering causing memory growth
- Synchronous blocking degrading performance
- No retry logic causing permanent failures from transient issues

### Phase 4: DAVE Protocol Migration (Future - Before March 2026)
**Rationale:** March 1, 2026 hard deadline for DAVE support. This phase depends on interactions.py adding DAVE support or requires framework migration.

**Delivers:** Bot compatible with Discord's end-to-end encryption requirements

**Addresses:**
- Missing DAVE protocol support (critical pitfall #4)
- Future-proofing for Discord's encryption roadmap

**Research needed:**
- Check interactions.py roadmap for DAVE implementation timeline
- Evaluate alternative frameworks (discord.py, disnake, pycord) for DAVE support
- Test DAVE compatibility before deadline
- Plan key management strategy for persistent verification keys

**Risk:** HIGH complexity, framework-dependent. May require full bot migration if interactions.py doesn't add support.

### Phase Ordering Rationale

- **Phase 1 first** because nothing else matters if the bot can't receive voice. AEAD encryption is the current blocker with high-confidence fix.
- **Phase 2 before Phase 3** because basic reliability (reconnection, error recovery, health checks) must precede performance optimizations. Can't monitor what doesn't stay running.
- **Phase 3 before Phase 4** because production hardening provides stability for testing DAVE migration. DAVE is complex; need solid foundation.
- **Phase 4 timing flexible** but must complete before March 1, 2026 deadline. Start planning Q4 2025 to allow time for framework migration if needed.

**Dependency chain:**
1. Working encryption (Phase 1) → 2. Stable connections (Phase 2) → 3. Performance monitoring (Phase 3) → 4. Protocol migration (Phase 4)

### Research Flags

Phases likely needing deeper research during planning:

- **Phase 4 (DAVE Migration):** Complex protocol change, framework-dependent implementation. Need to research interactions.py support timeline, evaluate migration options if unsupported, understand DAVE key management requirements. May require spike to evaluate framework options.

Phases with standard patterns (skip research-phase):

- **Phase 1 (Encryption Fix):** Well-documented encryption implementation with multiple reference implementations (discord.py, disnake). RTP header parsing is standard per RFC 8285.
- **Phase 2 (Production Reliability):** Standard production bot patterns. Extensive documentation on error handling, logging, health checks from Discord bot community.
- **Phase 3 (Production Hardening):** Established monitoring, rate limiting, and retry patterns. Well-documented in Discord API docs and bot hosting guides.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | PyNaCl AEAD support verified in official docs; discord.py implementation validates approach; monkey-patch is proven tactical solution |
| Features | MEDIUM | Production features based on community consensus and hosting guides; some features (latency targets, VAD accuracy) from voice AI platforms may not directly translate to Discord context |
| Architecture | HIGH | Current codebase analysis reveals exact integration points; refactoring approach matches successful patterns from other libraries; RTP extension fix is well-specified in RFC 8285 |
| Pitfalls | HIGH | RTP extension bug confirmed by discord.js issue #7647; encryption deprecation timeline from official Discord changelog; DAVE deadline from official Discord blog; WebSocket error codes from official docs |

**Overall confidence:** HIGH

The encryption fix has very high confidence due to multiple reference implementations and clear specifications. Production reliability patterns are standard across Discord bot ecosystem. The main uncertainty is DAVE migration timeline, which depends on external factors (interactions.py development roadmap, Discord's rollout schedule).

### Gaps to Address

- **DAVE protocol support timeline:** interactions.py has no public roadmap for DAVE implementation. Need to monitor library development or plan framework migration. Address during Phase 4 planning (Q4 2025).

- **Actual latency profile of current bot:** Research cites 800ms as target for voice AI, but current bot's actual STT→LLM→TTS→playback timing is unknown. Measure during Phase 3 to determine if optimization needed.

- **interactions.py update compatibility:** Monkey-patch may break on library updates. Add conditional patching (check if native AEAD support exists) and pin library version until migration path clear. Document in Phase 1.

- **Hardware requirements for DAVE:** DAVE verification key storage and encryption may have hardware/performance implications. Research during Phase 4 planning.

- **Multi-guild scaling threshold:** Research suggests sharding at 2500+ guilds, but bot is currently single-guild. Defer scaling concerns; revisit if deployment expands.

## Sources

### Primary (HIGH confidence)
- [Discord Voice Connections - Discord Userdoccers](https://docs.discord.food/topics/voice-connections) — AEAD mode specifications, RTP structure
- [Discord.py PR #9953: Add support for AEAD XChaCha20 Poly1305](https://github.com/Rapptz/discord.py/pull/9953) — Reference implementation for AEAD encryption
- [Disnake PR #1228: Add aead_xchacha20_poly1305_rtpsize encryption mode](https://github.com/DisnakeDev/disnake/pull/1228) — Alternative reference implementation
- [PyNaCl Secret Key Encryption Documentation](https://pynacl.readthedocs.io/en/latest/secret/) — Aead class usage, bindings API
- [RFC 8285 - RTP Header Extensions](https://datatracker.ietf.org/doc/rfc8285/) — Extension length calculation (32-bit words)
- [Discord API Docs: Voice Change Log](https://discord.com/developers/docs/change-log?topic=Voice) — Encryption deprecation timeline (Nov 18, 2024)
- [Bringing DAVE to All Discord Platforms](https://discord.com/blog/bringing-dave-to-all-discord-platforms) — March 1, 2026 deadline announcement

### Secondary (MEDIUM confidence)
- [Discord.js Issue #7647: VoiceReceiver.parsePacket incorrectly strips RTP header extension](https://github.com/discordjs/discord.js/issues/7647) — Same bug in JavaScript, validates fix approach
- [Advanced Discord Bot Development Strategies](https://arnauld-alex.com/building-a-production-ready-discord-bot-architecture-beyond-discordjs) — Production architecture patterns
- [The Ultimate Guide to AI Voice Bots in 2026](https://www.lindy.ai/blog/ai-voice-bots) — Voice AI latency targets, conversation quality
- [What Latency Really Means in Voice AI](https://signalwire.com/blogs/industry/what-latency-means-voice-ai) — Sub-800ms latency recommendations
- [Choosing the Best Voice Activity Detection in 2026](https://picovoice.ai/blog/best-voice-activity-detection-vad/) — VAD options (Cobra vs Silero)
- [Simple Error Handling for Prefix and App commands - discord.py](https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612) — Error handling patterns
- [Discord Bot Logging and Monitoring Best Practices (2025)](https://friendify.net/blog/discord-bot-logging-monitoring-best-practices-2025.html) — Structured logging approaches

### Tertiary (LOW confidence)
- [The Voice AI Stack for Building Agents in 2026](https://www.assemblyai.com/blog/the-voice-ai-stack-for-building-agents) — Streaming architecture (may be overkill for Discord bot)
- [Building an AI-Powered Discord Bot - Modern Architecture](https://medium.com/@ayushsh762/building-an-ai-powered-discord-bot-a-deep-dive-into-modern-architecture-and-technologies-3a98b781637b) — Microservices patterns (not applicable to single-guild bot)

---
*Research completed: 2026-02-03*
*Ready for roadmap: yes*

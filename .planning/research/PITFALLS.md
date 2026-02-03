# Pitfalls Research

**Domain:** Discord Voice Bot Development
**Researched:** 2026-02-03
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Incorrect RTP Extension Handling in AEAD Encryption

**What goes wrong:**
When implementing `aead_xchacha20_poly1305_rtpsize` encryption, the Additional Authenticated Data (AAD) must include the RTP extension, but developers often omit it or include the wrong portion of the packet. This causes "Decryption failed" errors when processing incoming voice packets, even though the encryption mode is correctly negotiated. Silence packets may work while actual speech fails, creating confusing debugging scenarios.

**Why it happens:**
Discord's voice encryption specification requires that metadata needed by the WebRTC packetizer must remain unencrypted, but the RTP extension must be included as AAD in the authentication tag. Developers often misunderstand which parts of the packet go into AAD vs. the encrypted payload, especially when migrating from deprecated encryption modes (xsalsa20_poly1305) that had different AAD requirements.

**How to avoid:**
- Study the exact packet structure: RTP header (12 bytes) + RTP extension (if present) forms the AAD
- The encrypted portion is the OPUS payload only
- Verify AAD construction matches Discord's spec: once data leaves the encryptor, it cannot be modified before reaching the decryptor or decryption will fail
- Test with both silence and active speech packets, as they may have different RTP structures
- Review reference implementations from discord.py PR #9953 and disnake PR #1228

**Warning signs:**
- Decryption works for some packets but not others
- Silence packets decrypt successfully but speech packets fail
- Error message: "Decryption failed" in voice packet processing
- Bot can send audio but cannot receive/process incoming voice
- Inconsistent behavior between different users speaking

**Phase to address:**
Phase 1 (Encryption Fix) - This must be fixed before any other voice functionality works properly.

---

### Pitfall 2: Missing Library Support for Modern Encryption Modes

**What goes wrong:**
As of November 18, 2024, Discord deprecated all encryption modes except `aead_xchacha20_poly1305_rtpsize` (always available) and `aead_aes256_gcm_rtpsize` (hardware-dependent). Bots using outdated library versions receive "No compatible encryption modes" errors even when Discord offers the correct modes, because the client library doesn't implement support for the new modes.

**Why it happens:**
Discord deprecated xsalsa20_poly1305 variants without a long migration window. Many bot frameworks (discord.py, interactions.py, etc.) required updates to support the new encryption modes. Developers running stable/LTS versions may not realize their library is now incompatible with Discord's voice servers.

**How to avoid:**
- Verify library version supports aead_xchacha20_poly1305_rtpsize before deployment
- Check library changelog/issues for encryption mode support (e.g., discord.py issues show this was added in specific commits)
- Never assume voice functionality works without testing actual voice connections
- Add encryption mode compatibility check during bot initialization
- Pin library versions in requirements.txt and document minimum required versions

**Warning signs:**
- Error: "No compatible encryption modes"
- Bot connects to gateway but fails during voice channel join
- Voice websocket closes immediately after connection
- Library last updated before November 2024
- Documentation still references xsalsa20_poly1305 modes

**Phase to address:**
Phase 0 (Pre-deployment) - Verify library compatibility before beginning any voice work.

---

### Pitfall 3: WebSocket 4006 Error from Privileged Intents

**What goes wrong:**
Bot connects to voice channel, appears in the channel UI, then immediately disconnects with "WebSocket closed with 4006" error. The bot repeats connection attempts several times before giving up. This error indicates Discord's API rejected the connection because the bot is trying to access privileged gateway intents without proper configuration.

**Why it happens:**
Discord requires specific privileged intents (Presence Intent, Server Members Intent) to be explicitly enabled in the Discord Developer Portal. Even if the bot code requests these intents, they must be toggled on in the portal. For verified bots or bots in 100+ servers, these intents require justification and approval. Developers often enable intents in code but forget the portal configuration.

**How to avoid:**
- Before deployment, verify all required intents are enabled in Discord Developer Portal
- If bot subscribes to presence updates, enable Presence Intent
- If bot manages members or gets member updates, enable Server Members Intent
- Add intent verification during bot startup to fail fast with clear error messages
- Document which intents are required and why in deployment instructions
- For scaling beyond 100 servers, plan for intent verification process early

**Warning signs:**
- WebSocket 4006 close code in logs
- Bot appears in voice channel briefly then disconnects
- Connection works in development, fails in production (different bot tokens)
- Recent bot token regeneration or portal settings change
- Bot cannot see member presence or voice states

**Phase to address:**
Phase 1 (Deployment Configuration) - Critical for production deployment; can block all voice functionality.

---

### Pitfall 4: Missing DAVE Protocol Support (March 1, 2026 Deadline)

**What goes wrong:**
Starting March 1, 2026, all Discord clients and bots must support the DAVE (Discord Audio & Video End-to-End Encryption) protocol. Bots without DAVE support will no longer be able to participate in Discord voice calls. This is a hard deadline - non-compliant bots will be completely unable to join voice channels.

**Why it happens:**
Discord is transitioning to mandatory end-to-end encryption for all voice/video calls. The DAVE protocol represents a fundamental architecture change from the current voice encryption approach. Bot frameworks may not yet implement DAVE support, and developers may be unaware of the approaching deadline.

**How to avoid:**
- Check if your bot framework supports DAVE protocol (for discord.js, install @snazzah/davey)
- Monitor framework roadmaps for DAVE implementation timelines
- If framework doesn't support DAVE, prepare to migrate to one that does
- Test DAVE compatibility before March 2026 deadline
- Persistent verification keys are tied to devices, not user accounts - plan key management strategy
- Understand that E2EE won't apply to calls where an unsupported client is present

**Warning signs:**
- Framework documentation doesn't mention DAVE protocol
- No encryption library like @snazzah/davey in dependencies
- Framework last major update was before late 2024
- Voice connection warnings about encryption compatibility
- Unable to join voice channels after March 1, 2026

**Phase to address:**
Phase 2 (DAVE Migration) - Must be completed before March 1, 2026 deadline to maintain voice functionality.

---

### Pitfall 5: Session State Desynchronization

**What goes wrong:**
Voice connection enters a state where the bot thinks it's connected but Discord thinks the session is invalid, or vice versa. The bot may send audio that nobody hears, or appear connected but player switches to AutoPaused state. Connection gets stuck in "signalling" state indefinitely without transitioning to "connected" or "disconnected".

**Why it happens:**
Voice sessions have complex state machines across multiple layers: Discord gateway session, voice websocket connection, UDP socket for audio, and library state tracking. Network issues, Discord server hiccups, or improper error handling can desync these states. Sessions can expire while the websocket remains technically open, leading to "Session is no longer valid" errors.

**How to avoid:**
- Implement comprehensive state monitoring across all connection layers
- Add heartbeat/keepalive verification beyond Discord's built-in mechanisms
- Set reasonable timeouts for state transitions (connection should complete within ~30s)
- Implement cleanup on partial failures (don't leave half-connected states)
- Add connection state logging with timestamps to diagnose desyncs
- Use idempotent disconnect/reconnect logic (safe to call even if already disconnected)
- Never assume connection state - verify before operations

**Warning signs:**
- Bot appears in voice channel but doesn't play audio
- Player state shows AutoPaused without clear reason
- Connection state stuck in "signalling" for >60 seconds
- Voice websocket open but no audio transmission
- Logs show "Session is no longer valid"
- Bot requires restart to reconnect properly

**Phase to address:**
Phase 3 (Resilience & Recovery) - Essential for production reliability after basic voice functionality works.

---

### Pitfall 6: Insufficient Permission Handling

**What goes wrong:**
Bot receives "Voice Connection Failed" errors or silent failures when attempting to join or speak in voice channels. The bot may have been granted voice permissions initially, but permission changes during runtime (role modifications, channel overwrites) cause unexpected failures. Permission errors often manifest as generic connection failures without clear error messages.

**Why it happens:**
Discord bots require specific permissions to connect to and speak in voice channels: `CONNECT` to join, `SPEAK` to transmit audio, and potentially `USE_VAD` (Voice Activity Detection). These permissions can be configured at role level, channel level (overwrites), or category level. Runtime permission changes don't trigger bot notifications, so the bot attempts operations that are no longer permitted.

**How to avoid:**
- Check permissions before attempting voice connection (don't just try and fail)
- Implement permission verification as part of join logic
- Add error handling that distinguishes permission failures from connection failures
- Log specific permission requirements in error messages for user debugging
- Consider implementing permission change monitoring if critical for uptime
- Provide clear user-facing error messages when permission issues occur
- Document exact permissions needed in bot setup instructions

**Warning signs:**
- Bot joins successfully in some channels but not others in same server
- Voice connection worked previously but fails after server configuration changes
- Error logs show connection failures without clear network issues
- Bot can see channel but cannot join
- Inconsistent behavior across different servers

**Phase to address:**
Phase 1 (Core Functionality) - Handle during initial voice implementation to provide good UX.

---

### Pitfall 7: Hardcoded Nonce Construction for AEAD

**What goes wrong:**
When implementing AEAD encryption modes, developers may hardcode nonce construction based on old documentation (e.g., "12-byte header + 12 null bytes"). However, `aead_xchacha20_poly1305_rtpsize` uses the RTP packet size in nonce construction differently than previous modes. Hardcoded nonce logic causes authentication failures when packet sizes vary.

**Why it happens:**
Discord's encryption modes have evolved, and nonce construction varies between modes. Old documentation for xsalsa20_poly1305 described one approach, but aead_xchacha20_poly1305_rtpsize uses different nonce construction. Developers copying patterns from older implementations carry forward incompatible nonce logic.

**How to avoid:**
- Read current Discord voice documentation for exact nonce construction per mode
- Don't copy-paste encryption code from pre-2024 implementations without verification
- Test with varying packet sizes (silence vs active speech creates different packet sizes)
- Use reference implementations from official Discord documentation or well-maintained libraries
- Add test cases that verify encryption/decryption with different payload sizes
- Comment nonce construction logic with mode-specific requirements

**Warning signs:**
- Decryption fails inconsistently based on packet content
- Different behavior between short and long audio packets
- Working with one encryption mode but failing with another
- Authentication tag verification failures
- Reference to "12 null bytes" in nonce construction code

**Phase to address:**
Phase 1 (Encryption Fix) - Must be correct for AEAD modes to function.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skipping encryption unit tests | Faster development | Silent failures in production when Discord changes encryption; debugging encryption issues in prod is extremely difficult | Never - encryption must be tested |
| Using global try-catch around voice connection | Prevents crashes | Masks specific errors (permissions, encryption, network), makes debugging impossible | Never - voice failures need specific handling |
| Hardcoding encryption mode to aead_aes256_gcm_rtpsize | Works on your machine | Fails on hardware without AES-NI; aead_xchacha20_poly1305_rtpsize is always available | Never - must support xchacha20 fallback |
| Not logging raw packet data during development | Cleaner logs | When encryption breaks, impossible to debug without packet inspection | Only in production - dev should log packets |
| Assuming voice connection = audio working | Simpler state machine | Bot appears connected but users hear nothing; no automatic detection of failure | Never - verify audio transmission separately |
| Single retry on voice connection failure | Faster failure feedback | Transient network/Discord issues cause permanent failures | Only for dev - production needs exponential backoff |
| Storing encryption keys in memory only | No persistence complexity | Keys lost on restart; can't decrypt buffered packets across restarts | Acceptable for stateless bots |
| Skipping DAVE support until March 2026 | Defer complexity | Rushed migration when deadline approaches; potential incompatibility with updated servers earlier | Acceptable until Q1 2026, risky after |

## Integration Gotchas

Common mistakes when connecting to Discord services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Voice WebSocket | Assuming connection success after websocket open | Wait for ready event and session_description before considering connection established |
| Encryption negotiation | Using first offered encryption mode | Prefer aead_xchacha20_poly1305_rtpsize (always works) over aead_aes256_gcm_rtpsize (hardware-dependent) |
| Audio packet transmission | Sending packets before UDP connection confirmed | Wait for UDP hole-punching to complete; verify with IP discovery response |
| Gateway intents | Setting intents in code only | Must also enable privileged intents in Discord Developer Portal |
| Voice state tracking | Relying on local state | Discord is source of truth; poll/verify voice state from API, don't assume |
| Disconnect handling | Treating all disconnects the same | WebSocket 4006 (intents) vs 4014 (token) vs network errors require different recovery strategies |
| Encryption mode fallback | No fallback logic | If preferred mode fails, try alternative modes from server's offered list |
| RTP header parsing | Fixed offset parsing | RTP extensions are variable length; parse header flags to find payload start |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Synchronous audio processing | Audio stuttering, latency | Use async I/O for all audio operations; process in separate thread if CPU-intensive | >3 simultaneous voice connections |
| Unbounded packet buffering | Memory growth over time | Implement bounded buffer with overflow strategy (drop oldest or newest) | Long-running connections with unreliable network |
| Creating new encryption context per packet | High CPU usage, slow packet processing | Reuse encryption context; only nonce changes per packet | >1 voice connection or high bitrate |
| Logging every packet | Disk I/O becomes bottleneck | Log packet metadata only; full packet dumps only on error or in debug mode | >50 packets/sec (typical voice) |
| Blocking voice thread for LLM processing | Audio gaps, timeouts | Process audio async; use queue between voice receiver and LLM | Any real-time voice processing |
| No voice connection pooling | Slow connection times | Maintain persistent connections; reconnect on failure rather than create new | >5 servers requiring voice |
| Storing full audio history in memory | OOM crashes | Stream to disk or process in chunks; keep only recent buffer in memory | >5 minutes of recorded audio |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Logging encryption keys | Key exposure in log aggregation systems | Never log secret keys, session descriptions, or authentication data |
| Using predictable nonces | Nonce reuse breaks AEAD security completely | Use proper random nonce or counter-based nonce per spec; never reuse |
| Accepting any encryption mode | Downgrade attacks if old modes have vulnerabilities | Only accept aead_xchacha20_poly1305_rtpsize or aead_aes256_gcm_rtpsize |
| Skipping authentication tag verification | Attackers can inject modified audio | Always verify Poly1305 auth tag before processing decrypted audio |
| Exposing voice websocket URL in logs/errors | Token in URL allows voice session hijacking | Sanitize URLs before logging; voice tokens are sensitive |
| Processing untrusted audio without validation | Buffer overflows, DoS from malformed packets | Validate packet structure before decryption; limit payload sizes |
| Storing DAVE verification keys insecurely | E2EE compromise | DAVE keys must be stored encrypted; device-specific keys require secure storage |
| Not rate-limiting voice joins | Voice channel spam/abuse | Implement join rate limits per server and globally |

## UX Pitfalls

Common user experience mistakes in Discord voice bots.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No feedback when joining voice | Users unsure if bot is working | Send status message when bot joins/leaves voice |
| Silent failures on permission issues | Users think bot is broken | Send clear message: "I need CONNECT and SPEAK permissions in this channel" |
| Staying in empty voice channels | Wastes resources, seems broken | Auto-leave after N minutes with no other users |
| No indication of voice processing state | Users talk when bot isn't listening | Visual indicator (status, message) when actively listening |
| Audio cutoff without warning | Partial LLM responses, confused users | Send message before leaving or stopping recording |
| No retry indication | Users don't know if failure is temporary | "Connection failed, retrying in X seconds..." |
| Playing audio over active speakers | Interrupting users is rude | Implement turn-taking or wait for silence |
| No volume control | Bot too loud/quiet for different servers | Configurable volume per server with sensible defaults |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Voice Encryption:** Often missing proper AAD construction — verify with Wireshark packet capture showing successful decryption
- [ ] **Connection Resilience:** Often missing reconnect logic for transient failures — verify with network interruption tests
- [ ] **Error Handling:** Often missing specific permission error detection — verify by removing bot permissions mid-session
- [ ] **DAVE Support:** Often missing entirely or incomplete — verify bot can join voice after March 1, 2026
- [ ] **Audio Quality:** Often missing proper OPUS configuration — verify with human listening test at different network conditions
- [ ] **State Management:** Often missing cleanup on partial failures — verify no resource leaks after 100 failed connections
- [ ] **Session Recovery:** Often missing handling of Discord-side session expiry — verify behavior after 12+ hour connection
- [ ] **Multi-server Support:** Often missing per-server voice state tracking — verify with bot in voice on 2+ servers simultaneously
- [ ] **Encryption Mode Fallback:** Often missing alternative mode support — verify on hardware without AES-NI
- [ ] **Voice State Sync:** Often missing reconciliation between bot state and Discord state — verify after bot process restart while in voice

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Incorrect AAD in encryption | MEDIUM | 1. Capture failing packet with Wireshark 2. Compare with reference implementation 3. Fix AAD construction 4. Test with same packet |
| Missing library encryption support | LOW | 1. Update library to latest version 2. Check changelog for encryption mode support 3. Test voice connection 4. May require code changes for API differences |
| WebSocket 4006 (intents) | LOW | 1. Go to Discord Developer Portal 2. Enable required privileged intents 3. Restart bot 4. No code changes needed |
| DAVE protocol missing | HIGH | 1. Check if framework supports DAVE 2. If yes, update and configure 3. If no, migrate to different framework 4. Test thoroughly |
| Session desynchronization | MEDIUM | 1. Implement full disconnect/reconnect cycle 2. Clear all local state 3. Don't attempt to resume session 4. Log state transitions for future diagnosis |
| Permission issues | LOW | 1. Check bot's effective permissions in channel 2. Request admin to grant missing perms 3. Provide clear permission list in error message |
| Hardcoded nonce construction | MEDIUM | 1. Review Discord docs for current nonce spec 2. Implement mode-specific nonce construction 3. Test with multiple packet sizes 4. Add nonce construction unit tests |
| Session expired | LOW | 1. Detect expiry from WebSocket close code 2. Full disconnect and rejoin 3. Don't try to reuse session ID |
| State stuck in signalling | MEDIUM | 1. Add timeout (30s max) 2. Full disconnect on timeout 3. Exponential backoff retry 4. Log for pattern analysis |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Incorrect RTP Extension AAD | Phase 1: Encryption Fix | Decrypt live voice packets successfully; test with both silence and speech |
| Missing modern encryption support | Phase 0: Library Verification | Bot negotiates aead_xchacha20_poly1305_rtpsize successfully |
| WebSocket 4006 (intents) | Phase 1: Deployment Config | Bot connects to voice without 4006 errors across restarts |
| Missing DAVE support | Phase 2: DAVE Migration | Bot functions after March 1, 2026; test with DAVE-enabled servers |
| Session desynchronization | Phase 3: Resilience | Bot recovers from network interruptions without restart |
| Permission failures | Phase 1: Core Functionality | Bot provides clear permission error messages |
| Hardcoded nonce construction | Phase 1: Encryption Fix | Encryption works with varying packet sizes |
| No encryption fallback | Phase 1: Encryption Fix | Bot works on systems without AES-NI support |
| Unbounded packet buffering | Phase 3: Production Hardening | Memory usage stable over 24h runtime |
| No connection retry logic | Phase 3: Resilience | Bot survives transient Discord outages |
| Missing audio quality validation | Phase 2: Testing & Validation | Human QA confirms clear audio reproduction |
| No monitoring/health checks | Phase 4: Deployment & Monitoring | Uptime monitoring catches bot failures within 5 minutes |

## Sources

- [Discord Voice Connections Documentation](https://docs.discord.food/topics/voice-connections) - Official voice connection implementation guide
- [Discord.py PR #9953: AEAD XChaCha20 Poly1305 support](https://github.com/Rapptz/discord.py/pull/9953) - Reference implementation for modern encryption
- [Disnake PR #1228: aead_xchacha20_poly1305_rtpsize](https://github.com/DisnakeDev/disnake/pull/1228) - Another reference implementation
- [Discord API Docs - Voice Change Log](https://discord.com/developers/docs/change-log?topic=Voice) - Official encryption deprecation timeline
- [Discord.py Issue #10207: WebSocket 4006 errors](https://github.com/Rapptz/discord.py/issues/10207) - Community troubleshooting for intent issues
- [Discord DAVE Protocol Whitepaper](https://github.com/discord/dave-protocol) - End-to-end encryption specification
- [End-to-End Encryption for Audio and Video - Discord Support](https://support.discord.com/hc/en-us/articles/25968222946071-End-to-End-Encryption-for-Audio-and-Video) - DAVE rollout timeline and requirements
- [Bringing DAVE to All Discord Platforms](https://discord.com/blog/bringing-dave-to-all-discord-platforms) - March 1, 2026 deadline announcement
- [Code of Connor: Monitoring My Discord Bot](https://codeofconnor.com/monitoring-my-discord-bot/) - Production monitoring best practices
- [Discord Voice Connection Errors - Support Article](https://support.discord.com/hc/en-us/articles/115001310031-Voice-Connection-Errors) - Official troubleshooting guide

---
*Pitfalls research for: Discord Local LLM Voice Chat Bot*
*Researched: 2026-02-03*

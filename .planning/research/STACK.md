# Stack Research: Discord Voice Encryption Fix

**Domain:** Discord Voice Bot - Voice Encryption Layer
**Researched:** 2026-02-03
**Confidence:** HIGH

## Problem Statement

interactions.py uses deprecated xsalsa20_poly1305 encryption modes (discontinued November 18, 2024) and lacks support for the required `aead_xchacha20_poly1305_rtpsize` mode. Additionally, the library incorrectly strips RTP header extensions AFTER decryption (line 58-61 in audio.py), but Discord's AEAD protocol requires the RTP extension as part of the Additional Authenticated Data (AAD) BEFORE decryption. This causes decryption to fail for actual speech while working for silence packets.

## Recommended Solution

### Primary Approach: Patch interactions.py Locally

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| PyNaCl | 1.6.0+ | AEAD encryption via nacl.secret.Aead | Already in use, has native XChaCha20Poly1305 IETF support since 1.4.0+ |
| interactions.py (patched) | 5.x (local fork) | Discord API wrapper | Existing codebase, minimal changes needed, keeps current architecture |

**Rationale:** Patching interactions.py locally is the most pragmatic solution because:
1. **Minimal code changes**: Only two files need modification (encryption.py and audio.py)
2. **Preserves existing architecture**: No need to rewrite the entire voice system
3. **PyNaCl already supports AEAD**: The `nacl.secret.Aead` class has been available since PyNaCl 1.4.0
4. **Low risk**: Changes are isolated to the encryption/decryption layer

### Implementation Details

**Step 1: Add AEAD Encryption Mode Support**

File: `interactions/api/voice/encryption.py`

Required changes:
- Add `"aead_xchacha20_poly1305_rtpsize"` to `SUPPORTED` tuple (currently only has deprecated modes)
- Import `nacl.secret.Aead` instead of just `SecretBox`
- Implement `decrypt_aead_xchacha20_poly1305_rtpsize()` method that:
  - Extracts nonce from last 4 bytes of payload
  - Uses first 12 bytes of RTP header + 4-byte extension header length as AAD
  - Calls `nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(ciphertext, aad, nonce, key)`

**Step 2: Fix RTP Extension Handling**

File: `interactions/api/voice/audio.py` (line 47-63 in RawInputAudio.ingest())

Required changes:
- Move RTP extension detection BEFORE decryption (lines 58-61 currently strip AFTER)
- Calculate AAD as: `header + extension_header` (12-byte RTP header + 4 bytes + extension data)
- Pass AAD to decrypt function
- Remove extension stripping from post-decryption

**Technical specification** (per RFC 8285):
- Extension length field represents 32-bit words
- Total extension size = `4 + (header_extension_length * 4)` bytes
- Extension format: `0xBEDE` marker + 2-byte length + data padded to 4-byte boundary

**Step 3: Update Voice Gateway Negotiation**

File: `interactions/api/voice/voice_gateway.py`

Required changes:
- Add `"aead_xchacha20_poly1305_rtpsize"` to preferred encryption modes
- Remove deprecated xsalsa20_poly1305 variants from selection logic

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PyNaCl | 1.6.0+ | Cryptographic operations | Already required, ensure version supports Aead class |
| struct | stdlib | Binary data packing/unpacking | RTP header parsing, nonce handling |

## Alternative Solutions Considered

### Alternative 1: Switch to discord.py

| Aspect | discord.py | Why Not Used |
|--------|-----------|--------------|
| **AEAD Support** | Native support as of PR #9953 (Nov 2024) | Requires complete rewrite of bot |
| **Maintenance** | Active, official Discord support | Migration cost too high for single feature |
| **Voice Receive** | Mature implementation | Loses interactions.py slash command patterns |
| **When to Use** | New projects or complete rewrites | Not this incremental fix |

**Verdict:** discord.py has solved this problem correctly, but migrating the entire bot is overkill. Use discord.py's implementation as reference for the patch.

### Alternative 2: Pycord or Disnake

| Library | AEAD Status | Why Not Used |
|---------|-------------|--------------|
| **Pycord** | Status unclear from 2026 docs | No confirmed AEAD support, same migration cost |
| **Disnake** | Has PR #1228 for AEAD support | Fork of discord.py, still requires full migration |
| **Nextcord** | Open PR #1278 for AEAD | Implementation status uncertain |

**Verdict:** These are discord.py forks with similar architectures. Migration cost is just as high, and AEAD support status is less certain than discord.py upstream.

### Alternative 3: Custom Voice Client

| Approach | Pros | Cons |
|----------|------|------|
| Build from scratch | Complete control | Reinvents wheel, high maintenance |
| Use discord.js as reference | JavaScript implementation available | Cross-language complexity |
| Discord Voice Protocol docs | Authoritative source | Low-level, requires extensive UDP/RTP knowledge |

**Verdict:** Overkill for this problem. The voice client works fine except for this specific encryption issue.

## What NOT to Do

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Keep xsalsa20_poly1305 modes | Deprecated Nov 18, 2024, Discord will eventually stop supporting them | aead_xchacha20_poly1305_rtpsize (required mode) |
| Strip RTP extension after decryption | AEAD requires extension as AAD before decryption, causes auth tag validation to fail | Include extension in AAD, strip after successful decryption |
| Use chacha20poly1305 PyPI package | Separate dependency, not IETF variant, incompatible with Discord's implementation | PyNaCl's built-in nacl.secret.Aead (XChaCha20Poly1305 IETF) |
| Implement custom crypto | Security risk, likely incorrect | Use PyNaCl's audited implementation |
| Wait for upstream fix | interactions.py has no active PR for AEAD support (as of Feb 2026) | Patch locally and consider submitting upstream |

## Installation

```bash
# Ensure PyNaCl version supports Aead
pip install "PyNaCl>=1.6.0"

# Current requirements (no changes needed)
# - interactions.py already depends on PyNaCl
# - FFmpeg, opus, libffi already installed
```

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| PyNaCl 1.6.0+ | Python 3.8+ | Aead class available since 1.4.0, but 1.6.0+ recommended for stability |
| interactions.py 5.x | PyNaCl 1.6.0+ | Current version uses SecretBox; patched version will use Aead |
| Python 3.10+ | PyNaCl 1.6.0+ | Project constraint, fully compatible |

## Implementation Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Breaking existing voice playback | Medium | Implement AEAD mode alongside existing modes for testing |
| PyNaCl version incompatibility | Low | PyNaCl 1.6.0+ is stable, Aead support well-established |
| Discord protocol changes | Low | aead_xchacha20_poly1305_rtpsize is required mode, won't be deprecated |
| RTP extension calculation errors | Medium | Use RFC 8285 spec exactly, test with discord.js fix as reference |

## Code Confidence Levels

| Component | Confidence | Source |
|-----------|-----------|--------|
| PyNaCl Aead usage | **HIGH** | Official PyNaCl docs, discord.py PR #9953 implementation |
| RTP extension calculation | **HIGH** | RFC 8285 specification, discord.js issue #7647 fix |
| AEAD encryption mode requirement | **HIGH** | Discord API docs, multiple library implementations confirm |
| interactions.py patch approach | **MEDIUM** | Based on successful discord.py implementation, not yet tested in interactions.py |

## Testing Strategy

1. **Verify PyNaCl version**: `python -c "import nacl.secret; print(nacl.secret.Aead)"`
2. **Test with silence packets first**: Should continue working (no RTP extensions)
3. **Test with actual speech**: Should decrypt successfully (RTP extensions present)
4. **Monitor for crypto exceptions**: `nacl.exceptions.CryptoError` indicates AAD mismatch
5. **Validate with multiple speakers**: Ensure SSRC mapping and user tracking still work

## Sources

- [Voice Connections - Discord Userdoccers](https://docs.discord.food/topics/voice-connections) — AEAD mode specifications, HIGH confidence
- [Add support for AEAD XChaCha20 Poly1305 encryption mode - discord.py PR #9953](https://github.com/Rapptz/discord.py/pull/9953) — Reference implementation, HIGH confidence
- [PyNaCl Secret Key Encryption Documentation](https://pynacl.readthedocs.io/en/latest/secret/) — Aead class usage, HIGH confidence
- [RFC 8285 - RTP Header Extensions](https://datatracker.ietf.org/doc/rfc8285/) — Extension length calculation (32-bit words), HIGH confidence
- [VoiceReceiver.parsePacket incorrectly strips RTP header extension - discord.js #7647](https://github.com/discordjs/discord.js/issues/7647) — Same bug in JavaScript, fix pattern confirms solution, HIGH confidence
- [interactions.py Voice Support Guide](https://interactions-py.github.io/interactions.py/Guides/23%20Voice/) — Current library capabilities, MEDIUM confidence
- [PyNaCl Changelog](https://pynacl.readthedocs.io/en/latest/changelog/) — Version history and Aead availability, HIGH confidence

---
*Stack research for: Discord Voice Bot Voice Encryption Fix*
*Researched: 2026-02-03*
*Overall confidence: HIGH*

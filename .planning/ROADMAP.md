# Roadmap: Discord Voice LLM Bot

## Overview

This roadmap takes the bot from broken (voice decryption failures) to production-ready in 3 focused phases. Phase 1 fixes the critical AEAD encryption bug blocking all voice reception. Phase 2 adds production stability through error recovery and connection management. Phase 3 polishes the deployment experience with validation and documentation. The journey prioritizes getting voice working first, then making it reliable, then making it easy to deploy.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Voice Encryption Fix** - Restore voice reception with AEAD encryption support
- [ ] **Phase 2: Production Stability** - Add error recovery, reconnection, and monitoring
- [ ] **Phase 3: Deployment Polish** - Improve setup experience and validation

## Phase Details

### Phase 1: Voice Encryption Fix
**Goal**: Bot can decrypt and transcribe incoming voice from users who are speaking
**Depends on**: Nothing (first phase)
**Requirements**: ENC-01, ENC-02, ENC-03
**Success Criteria** (what must be TRUE):
  1. Bot receives and decrypts voice packets from users speaking in voice channel
  2. Bot correctly handles RTP extensions in AEAD Additional Authenticated Data (AAD)
  3. Bot transcribes actual speech (not just silence packets) and responds via LLM/TTS
  4. Encryption patch works for both aead_xchacha20_poly1305_rtpsize and aead_aes256_gcm_rtpsize modes
**Plans**: TBD

Plans:
- [ ] TBD (to be planned via /gsd:plan-phase 1)

### Phase 2: Production Stability
**Goal**: Bot survives transient failures and provides operational visibility
**Depends on**: Phase 1
**Requirements**: CONN-01, CONN-02, CONN-03, ERR-01, ERR-02, ERR-03
**Success Criteria** (what must be TRUE):
  1. Bot automatically reconnects when voice connection drops unexpectedly
  2. Bot shuts down cleanly without leaving zombie voice connections
  3. Bot logs clear error messages when failures occur (connection, API, permissions)
  4. Bot recovers from temporary Gemini API or TTS failures without crashing
  5. Bot validates all required environment variables on startup and fails with helpful messages
**Plans**: TBD

Plans:
- [ ] TBD (to be planned via /gsd:plan-phase 2)

### Phase 3: Deployment Polish
**Goal**: New users can set up the bot quickly with clear guidance
**Depends on**: Phase 2
**Requirements**: DEPLOY-01, DEPLOY-02, DEPLOY-03
**Success Criteria** (what must be TRUE):
  1. Setup documentation includes all steps from Discord bot creation to first voice conversation
  2. Bot checks for CUDA, FFmpeg, and Python dependencies on startup with actionable error messages
  3. Configuration uses .env file consistently for all settings (API keys, model paths, channels)
**Plans**: TBD

Plans:
- [ ] TBD (to be planned via /gsd:plan-phase 3)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Voice Encryption Fix | 0/TBD | Not started | - |
| 2. Production Stability | 0/TBD | Not started | - |
| 3. Deployment Polish | 0/TBD | Not started | - |

---
*Roadmap created: 2026-02-03*
*Last updated: 2026-02-03*

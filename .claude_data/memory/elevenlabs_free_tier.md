---
name: elevenlabs-free-tier-limits
description: "What the user's free ElevenLabs account can/can't do via API vs website (voices, SFX, music download)"
metadata:
  node_type: memory
  type: reference
  originSessionId: f2127c4b-9447-417e-9ee3-f385fd69e341
  modified: 2026-10-04T10:57:49.776Z
---

User's ElevenLabs account is **free tier** (10,000 credits/month; key in lr_demo/blender_owl/.env as ELEVEN_LABS_API_KEY).
- Library voices (Mark UgBBYS2sOqTuMpoF3BR0): API returns 402 → generate on the website via Claude-in-Chrome.
- Sound Effects API (`/v1/sound-generation`) works on free tier → `miles/scripts/08_sfx.py`.
- Music API: 402 paid_plan_required. Website generates music (1 min ≈ 900 credits) but **download requires paid plan** —
  don't spend credits generating music unless the user has upgraded (900 credits were wasted on 2026-10-04 learning this).
- Free-tier output is non-commercial: remind to regenerate on paid plan before publishing.

Related: [[project-lr-demo-videos]]

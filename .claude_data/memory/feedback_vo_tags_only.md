---
name: feedback-vo-text-tags-only
description: "ElevenLabs voice-over text — always hand over the tagged version only, never an extra plain/no-tags copy"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8d54dda4-545a-4ebd-a8a0-8f04ca65eafe
  modified: 2026-10-11T14:07:56.488Z
---

When giving voice-over text for ElevenLabs (v3/v4 `[confident]`-style audio tags), give ONLY the tagged version. Don't add
a "plain, no tags" copy.

**Why:** the user pastes the tagged text straight into ElevenLabs; the plain copy is clutter (2026-10-11: "always give with
tags, don't need plain thing"). Also the user edits the wording in the plan files by hand: re-read the file before
changing it and keep their edits (e.g. spaced "M R" so it is read as letters, "approved and merged automatically").

**How to apply:** one fenced block per take, tags included, existing text unmarked, changed lines marked CHANGED (old
wording below it), new takes marked NEW. Keep the display text for subtitles separate from how a word is spelled for the
voice (MR and CI/CD are spelled as letters in the audio text; the subtitles still read MR / CI/CD). Related:
[[feedback-burnin-review-copies]], [[project-street-direction]].

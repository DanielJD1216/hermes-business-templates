---
name: creator-video-script
description: "Use when the source sheet is done. Script playbook for the Video role."
version: 0.1.0
metadata:
  hermes:
    tags: [creator-template, video]
---

# Script

**Trigger:** the source sheet is done.

## Steps
1. Lock these decisions in writing first: audience, structure, the core point in 12 words or fewer, opening move, disclosure, and full script or outline only. Get the owner's approval on them.
2. Draft in the owner's voice (canon/voice.md).
3. Check runtime: spoken words divided by 150 gives minutes. Save the script as `script.md` in the episode folder, with the first line `Runtime: about <n> minutes`.
4. Finish with a voice pass and a pass that removes AI-sounding phrasing.

## Done when
`script.md` (runtime on its first line) and the locked decisions are in the episode folder, and `status.md` names the next action.

## Approval
Post the result in its own thread and move the card to review. Nothing leaves the business without the owner's `approve`.

The Kanban board is named in your AGENTS.md. Read canon/ before any public-facing work.

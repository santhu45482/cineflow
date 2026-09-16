---
name: directing-character-dialogue
description: |
  Directs dialogue audio synthesis, SSML prosody shaping, dramatic timing, and low-latency Gemini Live API real-time table reads.
  Enforces sample rate targets, character acoustic consistency, and emotional pacing.
  Use when synthesizing character voice stems, conducting interactive voice rehearsals with directors, or shaping SSML prosody.
  Do NOT use for composing background musical scores, parsing screenplay formatting, or executing container restarts.
version: 1.0.0
license: Apache-2.0
allowed-tools: [synthesize_dialogue, start_script_rehearsal_session, get_character_bible, get_production_overview]
metadata:
  author: cineflow-core
  category: audio
---

# Directing Character Dialogue

## When to use
- Synthesizing multi-track character dialogue stems aligned with character voice presets.
- Shaping SSML prosody, dramatic pauses, vocal inflection, and emotional cadence.
- Initiating interactive, bidirectional real-time table reads with the Director via Gemini Live API.
- Enforcing studio runtime audio configurations (e.g. 48kHz sample rate, 24-bit PCM).

## When NOT to use
- Composing background musical themes or synth pads (use `composing-cinematic-scores`).
- Rendering storyboard visual frames (use `rendering-storyboard-frames`).
- Stitching rough-cut animatics or final timeline export (use `orchestrating-production-lifecycle`).

## Workflow
1. **Voice Profile Retrieval:**
   - Retrieve character's registered `voice_preset` from the production bible.
2. **SSML & Prosody Shaping:**
   - Insert dramatic pauses (`[pause 0.5s]`) and pace adjustments matching scene tension.
3. **Dialogue Stem Synthesis:**
   - Call `synthesize_dialogue(shot_id, character_id, dialogue_text, voice_preset, emotion)`.
   - Bind output stem to `runtime_config.scene_config.audio_sample_rate_hz` (e.g. 48000 Hz).
4. **Live Table Read / Rehearsal Session:**
   - When Director requests live rehearsal, initiate Gemini Live API session over WebSocket `/ws/table-read/{session_id}`.
   - See `references/live_table_read_protocol.md` for bidirectional streaming protocol.

## Examples
- **Input:** "Synthesize Kade's line: 'She was here. The trail is still warm.' with weary gruff delivery."
  **Output:** Generates dialogue stem at 48kHz using `Detective_Male_Gruff` preset and weary inflection.
- **Input:** "Start live table read rehearsal for Kade Mercer in Scene 2."
  **Output:** Initiates WebSocket Live API session configured with Kade's persona and scene context.

## Output format
- Dialogue stem manifest conforming to `assets/dialogue_stem_schema.json`.
- Output records `stem_id`, `shot_id`, `character_id`, `audio_uri`, `duration_sec`, and `sample_rate_hz`.

## Anti-patterns to avoid
- Do NOT use unassigned voice presets that deviate from the character bible.
- Do NOT generate stems that exceed shot duration limits (+/- 0.5s tolerance).
- Do NOT downsample audio below `runtime_config.scene_config.audio_sample_rate_hz`.

---
name: locking-character-continuity
description: |
  Extracts character profiles, locks deterministic visual seeds, defines visual anchor tokens, and assigns acoustic voice profiles.
  Maintains cross-scene actor appearance and audio continuity across all studio assets.
  Use when extracting character rosters from scripts, locking persistent seed tokens, assigning voice presets, or enforcing appearance bibles.
  Do NOT use for rendering storyboard frames, directing screenplay beats, or triaging cluster telemetry.
version: 1.0.0
license: Apache-2.0
allowed-tools: [register_character_bible, get_character_bible, get_production_overview]
metadata:
  author: cineflow-core
  category: casting
---

# Locking Character Continuity

## When to use
- Extracting character descriptions and biographical traits from ingested screenplays.
- Defining immutable visual anchor tokens (clothing, facial scars, cybernetics, silhouettes).
- Locking seed tokens for deterministic or variance-controlled image generation.
- Mapping characters to acoustic voice presets for dialogue synthesis.
- Auditing production bible consistency before approving `GATE_1_PREPROD`.

## When NOT to use
- Rendering visual storyboard frames directly (use `rendering-storyboard-frames`).
- Synthesizing speech audio or shaping SSML prosody (use `directing-character-dialogue`).
- Ingesting or formatting raw Fountain screenplay text (use `formatting-screenplays`).

## Workflow
1. **Character Roster Extraction:**
   - Identify speaking roles and key background characters from screenplay breakdowns.
2. **Visual Anchor Definition:**
   - Synthesize a dense, photorealistic visual anchor prompt describing age, ethnicity, attire, and distinctive markers.
3. **Seed Token Allocation:**
   - Assign a persistent 6-digit integer seed token (e.g. `849201`).
   - Adhere to `runtime_config.scene_config.seed_locking_mode`:
     * If `deterministic`: maintain exact base seed across all scenes.
     * If `creative_variance`: calculate scene-offset seed `base_seed + (scene_number * 100)`.
4. **Voice Preset Mapping:**
   - Assign acoustic profile from `references/voice_preset_matrix.md` (e.g. `Detective_Male_Gruff`).
5. **Bible Registration:**
   - Register entry via `register_character_bible(character_id, name, seed_token, visual_anchor, voice_preset)`.

## Examples
- **Input:** "Lock character profile for Kade Mercer: 40s detective with weather-beaten trenchcoat and blue cybernetic eye."
  **Output:** Registers `char_kade` with seed `849201`, anchor prompt, and `Detective_Male_Gruff` voice preset.
- **Input:** "Check character bible for session `sess-102`."
  **Output:** Returns registered character roster with visual anchors and assigned voice presets.

## Output format
- JSON character bible conforming to `assets/character_bible_schema.json`.

## Anti-patterns to avoid
- Do NOT alter visual anchor tokens midway through a production without explicit Director variance approval.
- Do NOT register characters without assigning an acoustic voice preset.
- Do NOT use unseeded random number generation for character assets.

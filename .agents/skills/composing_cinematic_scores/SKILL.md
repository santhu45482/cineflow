---
name: composing-cinematic-scores
description: |
  Composes scene soundtracks, ambient Foley soundscapes, and multi-stem musical cues aligned with dramatic tension and scene tempo.
  Translates scene sentiment and pacing into musical prompts and technical audio briefs.
  Use when generating background music cues, atmospheric synthesizer pads, dramatic tempo markers, or scene Foley layers.
  Do NOT use for synthesizing character dialogue lines, rendering visual storyboard images, or managing production gates.
version: 1.0.0
license: Apache-2.0
allowed-tools: [compose_scene_score, get_production_overview]
metadata:
  author: cineflow-core
  category: music
---

# Composing Cinematic Scores

## When to use
- Composing original cinematic soundtrack cues, themes, and motifs for screenplay scenes.
- Designing atmospheric background soundscapes (drone pads, rain Foley, industrial hums).
- Mapping scene emotional sentiment and tension curves into musical tempos (BPM) and instrumentation.
- Generating multi-stem score briefs for parallel asset generation in Phase 2.

## When NOT to use
- Synthesizing spoken dialogue lines or voice rehearsals (use `directing-character-dialogue`).
- Inspecting visual frames for rendering continuity (use `auditing-visual-continuity`).
- Orchestrating milestone gate approvals or workflow execution (use `orchestrating-production-lifecycle`).

## Workflow
1. **Scene Context & Sentiment Ingestion:**
   - Ingest scene pacing, sentiment valence, and environmental setting.
   - Consult `references/tempo_mood_mapping.md` for BPM and instrumentation guidelines.
2. **Score Brief Construction:**
   - Construct descriptive musical prompt specifying genre, tempo, instruments, and mood:
     e.g., "Dark ambient synth drone, moody saxophone, 72 BPM, rainy dystopian atmosphere".
3. **Score Stem Generation:**
   - Call `compose_scene_score(prompt, duration_sec, shot_id)`.
   - Set duration to match total scene length and adhere to configured sample rate.
4. **Stem Registration:**
   - Register score stem in production state for final rough-cut assembly.

## Examples
- **Input:** "Compose 30-second tense ambient synth score for Scene 1 alleyway investigation at 72 BPM."
  **Output:** Invokes `compose_scene_score` with dark synth drone brief and returns score audio URI.
- **Input:** "Create moody saxophone motif for Kade's realization in Scene 4."
  **Output:** Generates melodic score cue with melancholic brass and slow tempo.

## Output format
- Score brief and audio stem metadata conforming to `assets/score_brief_template.json`.
- Output records `shot_id`, `score_uri`, `duration_sec`, `sample_rate_hz`, and `musical_key`.

## Anti-patterns to avoid
- Do NOT generate scores that overpower dialogue frequencies; leave dynamic headroom for voice stems.
- Do NOT ignore scene pacing; high-tension action scenes must not have lethargic tempos.
- Do NOT hardcode audio durations independently of the scene shot breakdown.

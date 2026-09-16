---
name: formatting-screenplays
description: |
  Parses Fountain screenplays, decomposes scenes into atomic camera shot breakdowns, and analyzes narrative pacing.
  Calculates emotional valence and shot durations aligned with studio runtime configuration.
  Use when ingesting screenplay documents, splitting scenes into shots, analyzing dramatic pacing, or tagging characters.
  Do NOT use for generating storyboard images, synthesizing voice tracks, or approving production gates.
version: 1.0.0
license: Apache-2.0
allowed-tools: [ingest_screenplay_document, analyze_script_pacing_and_sentiment, record_shot, get_production_overview]
metadata:
  author: cineflow-core
  category: preproduction
---

# Formatting Screenplays

## When to use
- Parsing raw screenplay text or Fountain files into structured scene entities.
- Analyzing narrative tension, pacing metrics, and emotional sentiment curves across scenes.
- Decomposing scene action blocks into discrete, atomic camera shot breakdowns.
- Tagging speaking characters and extracting dialogue blocks for downstream casting.

## When NOT to use
- Locking visual seed tokens or character bible bibles (use `locking-character-continuity`).
- Rendering camera visual frames with generative models (use `rendering-storyboard-frames`).
- Directing voice prosody or conducting live rehearsals (use `directing-character-dialogue`).

## Workflow
1. **Screenplay Ingestion:**
   - Ingest raw script: `ingest_screenplay_document(file_content, scene_number)`.
   - Validate scene slugline, action descriptions, character headings, and parentheticals.
2. **Pacing & Sentiment Analysis:**
   - Evaluate dramatic tension: `analyze_script_pacing_and_sentiment(scene_text)`.
   - Extract sentiment scores to guide downstream lighting and score mood.
3. **Atomic Shot Breakdown:**
   - Split scene into sequential shots according to `runtime_config.scene_config.default_shot_duration_sec`.
   - Specify shot type (Wide Establishing, Medium Close-Up, Extreme Close-Up) and camera movement.
   - Record each shot: `record_shot(shot_id, scene_number, camera_movement, visual_prompt, duration_sec)`.
   - See `references/shot_decomposition.md` for shot classification rules.

## Examples
- **Input:** "Parse Scene 1 from Fountain: EXT. SECTOR 4 - NIGHT. Kade Mercer watches rain slicked towers."
  **Output:** Decomposes scene into 2 atomic shots with visual prompts and records them in studio state.
- **Input:** "Analyze dramatic pacing for the rooftop confrontation in Scene 5."
  **Output:** Generates tension curve report showing climax at beat 4 with recommended shot duration of 2.5s.

## Output format
- Structured shot list adhering to `assets/fountain_template.fountain` conventions.
- Each shot breakdown contains `shot_id`, `camera_movement`, `visual_prompt`, `character_ids`, and `duration_sec`.

## Anti-patterns to avoid
- Do NOT combine multiple distinct camera angles into a single shot unit.
- Do NOT hardcode fixed shot durations; always derive baseline from `default_shot_duration_sec`.
- Do NOT omit character tags from dialogue shot blocks.

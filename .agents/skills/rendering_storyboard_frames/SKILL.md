---
name: rendering-storyboard-frames
description: |
  Generates cinematic storyboard frames using persistent character seeds, precise optical framing, and dynamic runtime configuration.
  Injects aspect ratios, focal lengths, lighting styles, and resolution targets into image generation models.
  Use when generating storyboard frames, rendering visual concept art, updating camera lenses, or applying volumetric lighting styles.
  Do NOT use for synthesizing audio dialogue, writing screenplay scenes, or conducting SRE log audits.
version: 1.0.0
license: Apache-2.0
allowed-tools: [render_storyboard_frame, record_shot, get_production_overview]
metadata:
  author: cineflow-core
  category: visual_arts
---

# Rendering Storyboard Frames

## When to use
- Generating visual storyboard frames from decomposed screenplay shot prompts.
- Translating camera movement and staging into cinematic optical prompts (anamorphic lenses, f-stops).
- Applying volumetric lighting, atmospheric fog, color grading palettes, and key-to-fill ratios.
- Enforcing persistent character seed tokens and visual anchors for visual continuity.
- Ingesting `StudioRuntimeConfig` aspect ratios (e.g. `2.39:1`, `16:9`) and resolution targets.

## When NOT to use
- Synthesizing dialogue speech or sound effects (use `directing-character-dialogue`).
- Auditing rendered frames for visual continuity defects or glitches (use `auditing-visual-continuity`).
- Ingesting or analyzing raw screenplay documents (use `formatting-screenplays`).

## Workflow
1. **Shot Specification Retrieval:**
   - Retrieve shot breakdown and character visual anchors from the production state.
2. **Optics & Composition Engineering:**
   - Consult `references/cinematography_lexicon.md` for lens choices (e.g. 35mm anamorphic, 85mm portrait).
   - Inject `runtime_config.scene_config.aspect_ratio` and `resolution` into prompt styling.
3. **Frame Rendering:**
   - Invoke `render_storyboard_frame(prompt, seed, shot_id)`.
   - Incorporate character visual anchor tokens and locked seed tokens.
4. **Frame Registration & Hand-off:**
   - Store resulting `image_uri` and seed metadata in shot record for downstream QA critic audit.

## Examples
- **Input:** "Render shot-01-01: Wide establishing shot of rainy cyberpunk alleyway in 2.39:1 Cinemascope."
  **Output:** Calls `render_storyboard_frame` with anamorphic lens prompts, seed `849201`, and returns frame URI.
- **Input:** "Render medium close-up of Kade under neon light with shallow depth of field."
  **Output:** Renders shot using 50mm prime f/1.8 optical framing and character visual anchor.

## Output format
- Storyboard asset metadata conforming to `assets/storyboard_prompt_template.json`.
- Output must record `shot_id`, `image_uri`, `seed`, `aspect_ratio`, and `resolution`.

## Anti-patterns to avoid
- Do NOT generate frames without including the character's locked visual anchor tokens.
- Do NOT ignore runtime configuration aspect ratio and resolution parameters.
- Do NOT render frames without passing a deterministic seed token.

---
name: auditing-visual-continuity
description: |
  Performs multimodal frame-vs-script inspection, visual defect detection, and character continuity auditing across rendered shots.
  Scores compliance, flags rendering glitches, and routes automated retry signals to storyboard generation.
  Use when verifying generated storyboard frames, detecting rendering artifacts, auditing costume/seed consistency, or scoring QA compliance.
  Do NOT use for approving milestone gates without human input, composing musical scores, or parsing screenplay files.
version: 1.0.0
license: Apache-2.0
allowed-tools: [inspect_and_verify_shot, get_character_bible, get_production_overview]
metadata:
  author: cineflow-core
  category: quality_assurance
---

# Auditing Visual Continuity

## When to use
- Verifying rendered storyboard frames against the corresponding screenplay shot visual prompt.
- Detecting visual artifacts, anatomical glitches, unnatural lighting, or missing props.
- Auditing character visual continuity against registered character bibles (clothing, hair, facial features).
- Scoring shots for QA compliance and determining whether an automated re-render is required.
- Enforcing generator-critic refinement loops bounded by `qa_critic_max_retries`.

## When NOT to use
- Rendering the initial visual storyboard frames (use `rendering-storyboard-frames`).
- Approving Human-in-the-Loop milestone gates (use `orchestrating-production-lifecycle`).
- Triaging infrastructure and SRE container crashes (use `triaging-studio-telemetry`).

## Workflow
1. **Frame & Shot Ingestion:**
   - Ingest rendered `image_uri`, target `visual_prompt`, and character IDs.
2. **Multimodal Visual Inspection:**
   - Call `inspect_and_verify_shot(shot_id, script, image_uri)`.
   - Consult `references/visual_defect_taxonomy.md` to classify defects:
     * SEVERITY_HIGH: Missing primary character, wrong aspect ratio, severe anatomical glitch.
     * SEVERITY_LOW: Minor lighting variance, slight background artifact.
3. **Compliance Scoring:**
   - Assign compliance score (0.0 to 1.0). Threshold for pass: >= 0.85.
4. **Conditional Routing:**
   - If all shots pass: route to `QA_PASSED`.
   - If defects detected and retry count < `qa_critic_max_retries`: route to `RETRY_RENDER` with revision guidance.
   - If retry limit exceeded: escalate with warning to `GATE_2_ASSETS` for Director discretion.

## Examples
- **Input:** "Audit frame `shot-01-01` against visual prompt for Kade's cybernetic eye and rain reflection."
  **Output:** Calls `inspect_and_verify_shot`, reports compliance 0.94, zero critical glitches, `qa_passed: True`.
- **Input:** "Inspect rendered frame where character coat appears red instead of charcoal trenchcoat."
  **Output:** Flags SEVERITY_HIGH continuity defect, marks `qa_passed: False`, and triggers `RETRY_RENDER`.

## Output format
- QA Audit report conforming to `assets/qa_audit_report_schema.json`.
- Output records `shot_id`, `compliance_score`, `qa_passed`, `defect_list`, and `recommended_action`.

## Anti-patterns to avoid
- Do NOT pass frames with missing core character visual anchors.
- Do NOT trigger infinite retry loops; always enforce `qa_critic_max_retries`.
- Do NOT evaluate frames in isolation; always compare against the registered `character_bible`.

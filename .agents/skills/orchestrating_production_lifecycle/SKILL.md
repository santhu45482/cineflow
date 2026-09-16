---
name: orchestrating-production-lifecycle
description: |
  Orchestrates autonomous multi-agent film production lifecycles across pre-production, parallel asset generation,
  and timeline assembly while governing Human-in-the-Loop (HITL) milestone gates. Use when initiating an end-to-end
  scene run, advancing or reviewing milestone gates (GATE_1_PREPROD, GATE_2_ASSETS, GATE_3_FINAL), resuming paused
  sessions with director feedback, or cancelling active production runs. Do NOT use for direct frame rendering,
  dialogue SSML shaping, music composition, or SRE telemetry diagnostics.
version: 1.0.0
license: Apache-2.0
allowed-tools: [trigger_production_workflow, resume_production_workflow, cancel_production_run, approve_production_gate, reject_production_gate, get_production_overview]
metadata:
  author: cineflow-core
  category: orchestration
---

# Orchestrating Production Lifecycle

## When to use
- Initiating end-to-end autonomous scene production runs from raw screenplay text.
- Submitting milestone deliverables to the Director at `GATE_1_PREPROD`, `GATE_2_ASSETS`, or `GATE_3_FINAL`.
- Resuming paused sessions with Director approval notes, creative feedback, or revision directives.
- Cancelling or aborting active production pipelines upon Director wrap orders.
- Processing ambient completion events arriving from Cloud Storage asset drops or Pub/Sub triggers.

## When NOT to use
- Synthesizing character dialogue voice stems directly (use `directing-character-dialogue`).
- Rendering camera shots and storyboard visual frames (use `rendering-storyboard-frames`).
- Composing orchestral scores, atmospheric pads, or Foley audio (use `composing-cinematic-scores`).
- Triaging infrastructure crashes, OOM errors, or Grafana telemetry (use `triaging-studio-telemetry`).

## Workflow
1. **Screenplay Ingestion & Casting Lock (Phase 1):**
   - Instruct screenplay agent to ingest script and break into atomic shot units.
   - Instruct casting agent to register character visual anchors and deterministic seeds.
   - Intercept at `GATE_1_PREPROD` using native ADK `RequestInput` checkpoint.
2. **Director Sign-off & Resumption:**
   - Present Phase 1 package to the Director.
   - On approval: invoke `resume_production_workflow(session_id, "gate_1_approval", "APPROVED", notes)`.
   - On rejection: invoke `resume_production_workflow(session_id, "gate_1_approval", "REJECTED", notes)` to route revisions.
3. **Parallel Multi-Track Asset Generation (Phase 2):**
   - Execute parallel track generation: Storyboard frames, Dialogue voice stems, and Score composition.
   - Route rendered frames through QA critic verification loop.
   - Advance to `GATE_2_ASSETS` checkpoint for Director asset package review.
4. **Assembly, Delivery & Final Gate (Phase 3):**
   - On Gate 2 approval, trigger rough-cut timeline stitch.
   - Present final animatic package at `GATE_3_FINAL`.
5. **Cancellation & Emergency Abort:**
   - If the Director orders a stop, call `cancel_production_run(session_id, reason)`.
   - See `references/production_phases.md` for phase transition details.

## Examples
- **Input:** "Start production on Scene 3 with 2.39:1 Cinemascope and 4K resolution."
  **Output:** Initiates workflow with custom `StudioRuntimeConfig` and pauses at `GATE_1_PREPROD` with shot breakdowns.
- **Input:** "Director approved Gate 1 for session `sess-882`, notes: 'Proceed with amber lighting'."
  **Output:** Invokes `resume_production_workflow("sess-882", "gate_1_approval", "APPROVED", "Proceed with amber lighting")`.
- **Input:** "Stop production on session `sess-882` immediately, director called wrap."
  **Output:** Invokes `cancel_production_run("sess-882", "Director called wrap")`.

## Output format
- Structured production status summary following `assets/gate_approval_schema.json`.
- State transitions must output `session_id`, `current_gate`, `gate_status`, and `director_notes`.

## Anti-patterns to avoid
- Do NOT bypass milestone gates without explicit human Director sign-off.
- Do NOT hardcode scene parameters; always propagate `StudioRuntimeConfig` across nodes.
- Do NOT retry failed gates in an infinite loop; respect `qa_critic_max_retries`.
- Do NOT ignore ambient trigger events; route telemetry alerts immediately to `triaging-studio-telemetry`.

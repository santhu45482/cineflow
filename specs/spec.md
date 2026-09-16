# CineFlow: Autonomous Multi-Agent Cinema Studio (`.agents-cli-spec.md`)

## 1. Overview & Problem Statement.

A human director steers production through deterministic **Human-in-the-Loop (HITL)** approval gates. The multi-agent studio runs on Google's **Agent Runtime** within the **Google Enterprise Agent Platform**, protected by **Google Model Armor** sanitization filters and actively monitored at runtime by an autonomous SRE agent querying the **Google Cloud Operations Suite** (Cloud Logging, Cloud Trace, and Cloud Monitoring).

---

## 2. Model Allocation & Departmental Mapping

| Department Role | Agent Name | Designated Model | Primary Responsibility |
| --- | --- | --- | --- |
| **Executive Direction** | `director_hitl` | *Human-in-the-Loop* | Creative input, gate approval, verbal feedback via WebSockets. |
| **Studio Showrunner** | `showrunner_agent` | `gemini-3.7-flash` | Master orchestrator, state transition control, task delegation, gate interrupts. |
| **Screenwriting & Lore** | `screenplay_agent` | `gemini-3.7-flash` | Fountain script formatting, beat-sheet generation, scene decomposition. |
| **Casting & Continuity** | `casting_agent` | `gemini-3.7-flash` | Character bible extraction, persistent seed assignment, visual token locking. |
| **Visual Production** | `storyboard_agent` | `gemini-3.1-flash-image` | High-fidelity storyboard frames, VFX concept art, lighting palettes. |
| **Audio Production** | `audio_director_agent` | `gemini-3.7-flash` + Cloud TTS | Expressive character dialogue synthesis and voice timing cues. |
| **Score & Atmosphere** | `score_composer_agent` | `Lyria-3.5` | Mood-aligned cinematic soundtrack composition, Foley stems, ambient beds. |
| **Visual QA & Continuity** | `qa_critic_agent` | `gemini-omni-1.1-flash` | Multimodal frame-vs-script inspection, visual glitch & artifact detection. |
| **Studio Operations & SRE** | `studio_ops_agent` | `gemini-3.7-flash` | Google Cloud Operations Suite integration, Cloud Logging/Trace/Monitoring queries, automated self-healing. |

---

## 3. Architecture & Data Flow

```
                              ┌─────────────────────────────┐
                              │    HUMAN DIRECTOR (HITL)    │
                              └──────────────┬──────────────┘
                                             │ WebSocket / CLI
                                             ▼
                              ┌─────────────────────────────┐
                              │  Studio Showrunner Agent    │
                              │     (gemini-3.7-flash)      │
                              └──────┬───────┬───────┬──────┘
                                     │       │       │
              ┌──────────────────────┘       │       └──────────────────────┐
              ▼                              ▼                              ▼
    ┌───────────────────┐          ┌───────────────────┐          ┌───────────────────┐
    │  Creative Studio  │          │  Virtual Set Dept │          │   Post-Prod Lab   │
    ├───────────────────┤          ├───────────────────┤          ├───────────────────┤
    │ Screenwriter      │          │ Storyboard Agent  │          │ Multimodal QA     │
    │ (gemini-3.7-flash)│          │ (gemini-3.1-image)│          │(gemini-omni-1.1-flash) │
    │ Casting & Lore    │          │ Score Composer    │          │ FFmpeg Assembly   │5
    │ (gemini-3.7-flash)│          │ (Lyria-3.5)       │          │ (Cloud Run Worker)│
    └─────────┬─────────┘          └─────────┬─────────┘          └─────────┬─────────┘
              │                              │                              │
              └──────────────────────┬───────┴──────────────────────────────┘
                                     ▼
                      ┌─────────────────────────────┐
                      │     Google Model Armor      │
                      │  (Sanitization & Filter)    │
                      └──────────────┬──────────────┘
                                     ▼
                      ┌─────────────────────────────┐
                      │     GCP Agent Runtime       │
                      │  (Enterprise Agent Platform)│
                      └──────────────┬──────────────┘
                                     │ Native OTel & Traces
                                     ▼
                      ┌─────────────────────────────┐
                      │ Google Cloud Operations     │
                      │  - Cloud Trace (OTel Spans) │
                      │  - Cloud Monitoring (PromQL)│
                      │  - Cloud Logging (Logs)     │
                      └──────────────▲──────────────┘
                                     │ Runtime Diagnostics
                      ┌──────────────┴──────────────┐
                      │      Studio Ops Agent       │
                      │     (gemini-3.7-flash)      │
                      └─────────────────────────────┘

```

---

## 4. State Management Schema (`app/state.py`)

```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CharacterSheet(BaseModel):
    character_id: str
    name: str
    seed_token: int
    visual_anchor: str
    voice_preset: str


class ShotUnit(BaseModel):
    shot_id: str
    scene_number: int
    camera_movement: str
    visual_prompt: str
    dialogue_script: Optional[str] = None
    character_id: Optional[str] = None
    duration_sec: float = 4.0
    image_uri: Optional[str] = None
    audio_uri: Optional[str] = None
    score_uri: Optional[str] = None
    qa_passed: bool = False
    qa_feedback: Optional[str] = None


class MovieProductionBible(BaseModel):
    project_id: str
    title: str
    logline: str
    genre: str
    characters: Dict[str, CharacterSheet] = Field(default_factory=dict)
    shots: List[ShotUnit] = Field(default_factory=list)
    hitl_gate: str = "GATE_1_PREPROD"  # GATE_1_PREPROD, GATE_2_ASSETS, GATE_3_FINAL
    gate_cleared: bool = False
    director_notes: List[str] = Field(default_factory=list)
```

---

## 5. External Tools & Integrations

### 5.1 Google Cloud In-House Operations Toolset (`app/tools/gcp_telemetry.py`)

Equips the `studio_ops_agent` with native Google Cloud Operations integrations:

```python
from app.tools.gcp_telemetry import (
    query_cloud_logs,
    query_cloud_traces,
    query_cloud_monitoring_metrics,
    trigger_automated_recovery,
    run_sre_diagnostics_suite,
)
```

### 5.2 Generative Media Toolsets (`app/tools/media_tools.py`)

* **`render_storyboard_frame(prompt: str, seed: int, shot_id: str) -> str`**: Calls Vertex AI image generation API with `gemini-3.1-flash-image`, saving generated frames to `gs://$GCS_BUCKET/storyboards/`.
* **`compose_scene_score(prompt: str, duration_sec: int, shot_id: str) -> str`**: Invokes `Lyria-3.5` for cinematic music generation, saving stem outputs to `gs://$GCS_BUCKET/scores/`.
* **`synthesize_dialogue(text: str, voice_preset: str, shot_id: str) -> str`**: Invokes Google Speech / Gemini TTS for multi-speaker vocal inflection, saving `.wav` files to `gs://$GCS_BUCKET/audio/`.
* **`stitch_rough_cut(shot_ids: list[str]) -> str`**: Invokes containerized FFmpeg on Cloud Run to mux visuals, speech stems, and Lyria score stems into an assembled `.mp4`.

---

## 6. Safety & Security: Google Model Armor

All incoming prompts from the Director and outbound generative calls across child agents pass through Model Armor inspection filters:

```yaml
# config/model-armor-config.yaml
filter_config:
  rai_settings:
    hate_speech: BLOCK_LOW_AND_ABOVE
    harassment: BLOCK_LOW_AND_ABOVE
    sexually_explicit: BLOCK_LOW_AND_ABOVE
    dangerous_content: BLOCK_LOW_AND_ABOVE
  prompt_injection_protection:
    enabled: true
    enforcement: REJECT
  pii_sanitization:
    enabled: true
    mask_character: "*"

```

---

## 7. `agents-cli` Workflow Execution Steps

Run these commands inside Google Cloud Shell to initialize, test, evaluate, and deploy the project to the Enterprise Agent Platform.

### Phase 1: Scaffold

Initialize the project structure with the ADK template configured for Agent Runtime:

```bash
# 1. Initialize ADK project targeting Agent Runtime
agents-cli create cineflow --agent adk --deployment-target agent_runtime --yes

# 2. Navigate to project root
cd cineflow

# 3. Add project dependencies
uv add "google-cloud-aiplatform[agent_engines,adk]>=1.101.0" \
       "google-genai>=0.1.1" \
       "opentelemetry-api" \
       "opentelemetry-sdk" \
       "pydantic>=2.7.0"

```

### Phase 2: Build & Iterate

Implement agent logic inside `app/agent.py` and run local testing:

```bash
# Launch ADK Web Playground with hot-reloading
agents-cli playground

# Run terminal smoke tests
agents-cli run "Showrunner: Draft scene 1 and character bibles for a cyberpunk neo-noir film."

# Run code formatters and lint checks
agents-cli lint

```

### Phase 3: Evaluate

Define benchmark datasets in `tests/eval/datasets/film_eval.json` to score character consistency, script layout, and tool invocation accuracy:

```bash
# Execute automated evaluation suite
agents-cli eval run

# Inspect evaluation summaries
agents-cli eval analyze

```

### Phase 4: Deploy & Secure

Deploy to Google Enterprise Agent Platform with Model Armor enabled:

```bash
# 1. Provision GCP infrastructure & telemetry buckets
agents-cli infra single-project

# 2. Deploy CineFlow to Enterprise Agent Runtime
agents-cli deploy

# 3. Verify deployed endpoints
agents-cli run "Run pipeline status check via studio_ops_agent." --remote

```

### Phase 5: Publish

Publish the agent directly into the Gemini Enterprise catalog:

```bash
agents-cli publish gemini-enterprise

```

---

## 8. Success Criteria & Demonstration Storyline

* **Prompt-to-Animatic Pipeline:** The Showrunner transforms a 2-sentence movie premise into a fully structured screenplay, character sheets with locked seeds, 4 storyboard frames (`gemini-3.1-flash-image`), synthesized vocal tracks, and a scored ambient theme (`Lyria-3.5`).
* **Active Director Sign-Off:** The terminal/web interface pauses at **Gate 1** and **Gate 2**. The system modifies outputs based on Director notes (`"Make lighting high-contrast neon purple"`) without restarting the pipeline.
* **Runtime Self-Healing (Google Cloud Operations):** An intentional video generation error is injected during the live demo. The `studio_ops_agent` uses its Google Cloud Operations toolset to inspect Cloud Logging error logs, detect the API timeout trace in Cloud Trace, and report root-cause diagnostics directly to the Showrunner.
* **Enterprise Security:** Inappropriate prompt injections or harmful directives are intercepted and blocked by Google Model Armor before reaching downstream media generators.
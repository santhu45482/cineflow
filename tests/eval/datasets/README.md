# Evaluation Datasets

This directory contains evaluation datasets for testing CineFlow multi-agent studio behavior across both hermetic pre-commit CI and live Agent Platform evaluation flywheel runs.

## Datasets

### 1. `golden_film_eval.json` (Canonical Production Golden Dataset)
The production-grade benchmark covering 20 curated multi-turn and single-turn scenarios across 5 core studio domains:
- **Pre-Production Breakdown**: Fountain screenplay ingestion, scene decomposition, character roster extraction, optical/resolution configuration (`aspect_ratio: 2.39:1`).
- **HITL Milestone Governance**: Strict adherence to `GATE_1_PREPROD`, `GATE_2_ASSETS`, and `GATE_3_FINAL` checkpoints; approval with creative notes, rejection/rework loops, and clean cancellation.
- **Asset Generation Quality**: Persistent character seed propagation (`seed: 849201`), audio dialogue stems with voice presets, Lyria-3.5 Foley soundscapes, cinematic scores, and rough-cut timeline assembly.
- **SRE Telemetry & Automated Self-Healing**: OOMKilled worker pool diagnosis, Cloud Logging & Cloud Trace inspection, automated recovery triggers, and 429 quota failovers.
- **Security & Model Armor Guardrails**: Prompt injection defense, system instruction exfiltration prevention, toxic screenplay sanitization, and enterprise gateway enforcement.

### 2. `film_eval.json`
Pre-production prompt suite used for rapid prototyping and synthetic trace generation.

### 3. `basic-dataset.json`
Minimal sanity-check dataset for local CLI smoke testing.

---

## Running Evaluations

### Running the Golden Dataset
```bash
# Run the agent over the Production Golden Dataset and grade traces
agents-cli eval run --dataset tests/eval/datasets/golden_film_eval.json
```

### Decoupled Runs (Recommended for CI/CD)
Split generation and grading for reproducibility and caching:

```bash
# 1. Generate agent traces
agents-cli eval generate \
  --dataset tests/eval/datasets/golden_film_eval.json \
  --output tests/eval/traces/cand/

# 2. Grade generated traces against custom deterministic metrics + LLM judges
agents-cli eval grade \
  --eval-config tests/eval/adk_eval_config.json \
  --traces tests/eval/traces/cand/ \
  --output tests/eval/results/cand_results.json

# 3. Compare with verified baseline to check for regressions
agents-cli eval compare \
  tests/eval/results/baseline_results.json \
  tests/eval/results/cand_results.json
```

### Deployed Agent
To evaluate against a live deployed Cloud Run instance:
```bash
agents-cli eval generate \
  --url https://cineflow-agent.run.app \
  --app-name app \
  --dataset tests/eval/datasets/golden_film_eval.json
```

---

## Quality Flywheel Iteration Commands

- `agents-cli eval compare BASE CAND` — Regression diff between baseline and candidate evaluation runs.
- `agents-cli eval analyze RESULTS` — Automatic failure clustering across traces.
- `agents-cli eval optimize` — GEPA prompt auto-tuning based on evaluation scores.

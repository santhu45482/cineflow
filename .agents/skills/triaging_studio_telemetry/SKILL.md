---
name: triaging-studio-telemetry
description: |
  Triages runtime failures, service latencies, and container errors across studio services using Google Cloud Operations Suite.
  Executes Cloud Monitoring metrics queries, inspects Cloud Logging logs and Cloud Trace distributed traces, and triggers automated self-healing recoveries.
  Use when receiving ambient Pub/Sub or Eventarc alerts, diagnosing render crashes, investigating latency spikes,
  or executing automated Cloud Run worker restarts. Do NOT use for modifying screenplay text, casting characters, or generating media assets.
version: 2.0.0
license: Apache-2.0
allowed-tools: [query_cloud_logs, query_cloud_traces, query_cloud_monitoring_metrics, query_loki_logs, query_tempo_traces, query_mimir_metrics, trigger_automated_recovery, run_sre_diagnostics_suite, get_production_overview]
metadata:
  author: cineflow-core
  category: operations
---

# Triaging Studio Telemetry

## When to use
- Receiving ambient alerts from Pub/Sub or Eventarc triggers (e.g. `RENDER_FAILURE_ALERT`, container OOMKilled).
- Diagnosing API latency spikes or timeout errors during asset generation.
- Inspecting distributed traces via Google Cloud Trace Explorer to isolate bottleneck microservices.
- Querying Google Cloud Logging for error stack traces or Cloud Run worker panics.
- Monitoring generation rates and quotas in Google Cloud Monitoring.
- Executing automated remediation (Cloud Run worker restarts, circuit breaking, buffer resizing).

## When NOT to use
- Ingesting, parsing, or decomposing screenplay text (use `formatting-screenplays`).
- Registering character seed tokens or voice presets (use `locking-character-continuity`).
- Reviewing or advancing Human-in-the-Loop production gates (use `orchestrating-production-lifecycle`).

## Workflow
1. **Ambient Alert Ingestion:**
   - Parse event payload from Pub/Sub push trigger `/apps/{app_name}/trigger/pubsub`.
   - Identify affected component, incident type, and trace ID.
2. **Google Cloud Logging Querying:**
   - Query log streams for error patterns: `query_cloud_logs(filter_or_query='resource.type="cloud_run_revision" severity>=ERROR', limit=20)`.
3. **Google Cloud Trace Inspection:**
   - Trace latency bottlenecks across OpenTelemetry spans: `query_cloud_traces(trace_id=trace_id)`.
4. **Google Cloud Monitoring Corroboration:**
   - Check error rates and worker queue depths via `query_cloud_monitoring_metrics(metric_query="sum(rate(cineflow_errors_total[5m]))")`.
5. **Automated Remediation:**
   - Trigger targeted recovery: `trigger_automated_recovery(incident_id=incident_id, component=component, incident_type=incident_type)`.
   - Or run full self-healing suite: `run_sre_diagnostics_suite()`.
   - See `references/promql_triage_playbook.md` for query templates.

## Examples
- **Input:** "Cloud Run FFmpeg worker crashed with OOMKilled in pod cineflow-worker-4. Investigate and recover."
  **Output:** Queries Google Cloud Logging, inspects trace `tr-9812`, and triggers worker pool restart via `trigger_automated_recovery`.
- **Input:** "P99 image generation latency jumped to 14 seconds. Run telemetry diagnostics."
  **Output:** Executes `run_sre_diagnostics_suite()` and provides root cause analysis linking upstream rate limiting.

## Output format
- Markdown SRE incident report summarizing Incident Type, Root Cause, Correlated Trace ID, Log Excerpt, and Remediation Status.

## Anti-patterns to avoid
- Do NOT trigger automated recovery without recording the correlated Trace ID and timestamp.
- Do NOT run PromQL or metrics queries without bounded lookback windows (e.g. always use `[5m]` or `[1m]`).
- Do NOT suppress alerts without notifying the Showrunner Orchestrator.

# PromQL Triage Playbook & Standard Queries

## Essential Prometheus/Mimir Queries

### 1. HTTP 5xx Error Rate (% of total traffic)
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
```

### 2. P99 Request Latency by Route
```promql
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, route))
```

### 3. Media Rendering Worker Concurrency
```promql
sum(cineflow_active_media_render_tasks) by (agent_type)
```

### 4. GCS Upload Failure Spike Detection
```promql
increase(gcs_upload_errors_total[10m]) > 3
```

### 5. Multi-Agent Invocations by Agent
```promql
sum(rate(cineflow_agent_invocations_total[5m])) by (agent_name)
```

### 6. Token Usage Rate by Agent & Token Type (Prompt vs Completion)
```promql
sum(rate(cineflow_tokens_total[5m])) by (agent_name, token_type)
```

### 7. Agent Execution Latency (P95)
```promql
histogram_quantile(0.95, sum(rate(cineflow_agent_latency_seconds_bucket[5m])) by (le, agent_name))
```


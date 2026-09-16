#!/usr/bin/env bash
# Quick smoke check for CineFlow SRE Google Cloud Operations Tools
set -euo pipefail

echo "==> Running CineFlow SRE smoke test with Google Cloud Operations..."
uv run python -c "
from app.tools.gcp_telemetry import run_sre_diagnostics_suite, query_cloud_logs, query_cloud_traces, query_cloud_monitoring_metrics
result = run_sre_diagnostics_suite()
print('Diagnostics result status:', result.get('status', 'OK'))
print('Cloud suite:', result.get('cloud_suite'))
"
echo "==> Smoke test completed successfully."

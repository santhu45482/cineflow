# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Backward-compatibility module for telemetry tools.

NOTE: Grafana Cloud integration has been replaced by Google Cloud In-House Operations
(Google Cloud Logging, Google Cloud Trace, and Google Cloud Monitoring).
This module re-exports the in-house GCP tools to preserve API compatibility.
"""

from typing import Any

from app.tools.gcp_telemetry import (
    query_cloud_logs,
    query_cloud_monitoring_metrics,
    query_cloud_traces,
    query_loki_logs,
    query_mimir_metrics,
    query_tempo_traces,
    run_sre_diagnostics_suite,
    trigger_automated_recovery,
)


def get_grafana_mcp() -> Any:
    """Deprecated: Grafana MCP has been removed in favor of Google Cloud In-House Services."""
    return None


__all__ = [
    "get_grafana_mcp",
    "query_cloud_logs",
    "query_cloud_monitoring_metrics",
    "query_cloud_traces",
    "query_loki_logs",
    "query_mimir_metrics",
    "query_tempo_traces",
    "run_sre_diagnostics_suite",
    "trigger_automated_recovery",
]

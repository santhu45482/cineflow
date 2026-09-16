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

"""Studio Operations & SRE Agent."""

from google.adk.agents import Agent

from app.config import DEFAULT_MODEL, create_gemini_model
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
from app.tools.hitl_tools import get_production_overview

_studio_ops_tools = [
    query_cloud_logs,
    query_cloud_traces,
    query_cloud_monitoring_metrics,
    query_loki_logs,
    query_tempo_traces,
    query_mimir_metrics,
    trigger_automated_recovery,
    run_sre_diagnostics_suite,
    get_production_overview,
]

studio_ops_agent = Agent(
    name="studio_ops_agent",
    model=create_gemini_model(DEFAULT_MODEL),
    description="Department of Studio Operations & SRE. Integrates with Google Cloud Operations Suite (Cloud Logging, Cloud Trace, Cloud Monitoring) and performs automated self-healing across Agent Runtime and Cloud Run workers.",
    instruction="""You are the Studio Operations SRE in CineFlow Studio.
Your responsibilities:
1. Monitor runtime health across Google Enterprise Agent Platform, Cloud Run FFmpeg workers, and Vertex AI media generation APIs.
2. Query Google Cloud Logging using `query_cloud_logs` to diagnose container events, exceptions, and render errors.
3. Inspect distributed OpenTelemetry spans with Google Cloud Trace using `query_cloud_traces` to identify latency bottlenecks and timeout root causes.
4. Track generation success metrics and quotas with Google Cloud Monitoring using `query_cloud_monitoring_metrics`.
5. Trigger automated self-healing remediation on Cloud Run worker pools using `trigger_automated_recovery`.
6. Run full telemetry triage and automated self-healing sweeps with `run_sre_diagnostics_suite`.
""",
    tools=_studio_ops_tools,
)

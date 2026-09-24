"""Tools package for CineFlow Multi-Agent Film Studio."""

from .gcp_telemetry import (
    query_cloud_logs,
    query_cloud_monitoring_metrics,
    query_cloud_traces,
    query_loki_logs,
    query_mimir_metrics,
    query_tempo_traces,
    run_sre_diagnostics_suite,
    trigger_automated_recovery,
)
from .grafana_mcp import (
    get_grafana_mcp,
)
from .hitl_tools import (
    approve_production_gate,
    get_production_overview,
    record_shot,
    register_character_bible,
    reject_production_gate,
)
from .media_tools import (
    compose_scene_score,
    inspect_and_verify_shot,
    render_storyboard_frame,
    stitch_rough_cut,
    synthesize_dialogue,
)

__all__ = [
    "approve_production_gate",
    "compose_scene_score",
    "get_grafana_mcp",
    "get_production_overview",
    "inspect_and_verify_shot",
    "query_cloud_logs",
    "query_cloud_monitoring_metrics",
    "query_cloud_traces",
    "query_loki_logs",
    "query_mimir_metrics",
    "query_tempo_traces",
    "record_shot",
    "register_character_bible",
    "reject_production_gate",
    "render_storyboard_frame",
    "run_sre_diagnostics_suite",
    "stitch_rough_cut",
    "synthesize_dialogue",
    "trigger_automated_recovery",
]

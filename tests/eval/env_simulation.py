"""Environment Simulation configurations for hermetic CineFlow evaluations.

Provides controlled, deterministic mocking and fault injection for external
dependencies (Cloud Run FFmpeg rendering, TTS voice synthesis, Grafana Loki/Tempo).
"""

import json

from google.adk.tools.environment_simulation import EnvironmentSimulationFactory
from google.adk.tools.environment_simulation.environment_simulation_config import (
    EnvironmentSimulationConfig,
    InjectedError,
    InjectionConfig,
    MockStrategy,
    ToolSimulationConfig,
)

# Simulated studio telemetry data snapshot
STUDIO_TELEMETRY_DATA = {
    "loki_logs": [
        {
            "stream": {
                "app": "cineflow",
                "component": "ffmpeg-worker-pool",
                "pod": "cineflow-worker-7",
            },
            "values": [
                [
                    "1725870000000000000",
                    "FATAL: OutOfMemory container killed (limit: 8GiB)",
                ],
                [
                    "1725870001000000000",
                    "Worker thread terminated with signal 9 (SIGKILL)",
                ],
            ],
        }
    ],
    "tempo_traces": {
        "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
        "root_service": "cineflow-render-worker",
        "error": True,
        "spans": [
            {"name": "ffmpeg_assembly_job", "duration_ms": 14200, "status": "ERROR"}
        ],
    },
}


def get_cineflow_env_simulation_config() -> EnvironmentSimulationConfig:
    """Returns the standard EnvironmentSimulationConfig for hermetic studio tests."""
    return EnvironmentSimulationConfig(
        tool_simulation_configs=[
            # 1. Fault injection for FFmpeg timeline rendering
            ToolSimulationConfig(
                tool_name="render_ffmpeg_timeline",
                injection_configs=[
                    InjectionConfig(
                        match_args={"scene_number": 99},
                        injected_error=InjectedError(
                            injected_http_error_code=500,
                            error_message="OOMKilled: worker pod cineflow-worker-7 exceeded memory limit (8GiB)",
                        ),
                    ),
                    InjectionConfig(
                        match_args={"scene_number": 1},
                        injected_response={
                            "status": "SUCCESS",
                            "timeline_uri": "gs://cineflow-renders/scenes/scene_1_final_cut.mp4",
                            "duration_seconds": 18.5,
                            "resolution": "3840x2160",
                            "codec": "hevc",
                        },
                    ),
                ],
                mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
            ),
            # 2. Audio dialogue synthesis with latency & high-fidelity payload
            ToolSimulationConfig(
                tool_name="synthesize_dialogue_stem",
                injection_configs=[
                    InjectionConfig(
                        injected_latency_seconds=0.1,
                        injected_response={
                            "status": "SUCCESS",
                            "stem_uri": "gs://cineflow-assets/audio/kade_line_01.wav",
                            "sample_rate_hz": 48000,
                            "character": "Kade Mercer",
                            "duration_seconds": 3.8,
                        },
                    )
                ],
                mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
            ),
            # 3. Google Cloud In-House Logging & Loki mock
            ToolSimulationConfig(
                tool_name="query_cloud_logs",
                injection_configs=[
                    InjectionConfig(
                        injected_response={
                            "status": "success",
                            "engine": "Google Cloud Logging",
                            "data": {
                                "resultType": "streams",
                                "result": STUDIO_TELEMETRY_DATA["loki_logs"],
                            },
                        }
                    )
                ],
            ),
            ToolSimulationConfig(
                tool_name="query_loki_logs",
                injection_configs=[
                    InjectionConfig(
                        injected_response={
                            "status": "success",
                            "data": {
                                "resultType": "streams",
                                "result": STUDIO_TELEMETRY_DATA["loki_logs"],
                            },
                        }
                    )
                ],
            ),
            # 4. Google Cloud In-House Trace & Tempo mock
            ToolSimulationConfig(
                tool_name="query_cloud_traces",
                injection_configs=[
                    InjectionConfig(
                        injected_response={
                            "status": "success",
                            "engine": "Google Cloud Trace",
                            "trace": STUDIO_TELEMETRY_DATA["tempo_traces"],
                        }
                    )
                ],
            ),
            ToolSimulationConfig(
                tool_name="query_tempo_traces",
                injection_configs=[
                    InjectionConfig(
                        injected_response={
                            "status": "success",
                            "trace": STUDIO_TELEMETRY_DATA["tempo_traces"],
                        }
                    )
                ],
            ),
            # 5. Automated recovery trigger mock
            ToolSimulationConfig(
                tool_name="trigger_automated_recovery",
                injection_configs=[
                    InjectionConfig(
                        injected_response={
                            "status": "SUCCESS",
                            "action": "POD_RESTART_AND_SCALE_UP",
                            "target_component": "ffmpeg_worker_pool",
                            "remediated": True,
                        }
                    )
                ],
            ),
        ],
        environment_data=json.dumps(STUDIO_TELEMETRY_DATA),
    )


def create_cineflow_env_simulation_callback():
    """Factory helper creating a before_tool_callback for ADK agents."""
    config = get_cineflow_env_simulation_config()
    return EnvironmentSimulationFactory.create_callback(config)


def create_cineflow_env_simulation_plugin():
    """Factory helper creating an ADK plugin for App level interception."""
    config = get_cineflow_env_simulation_config()
    return EnvironmentSimulationFactory.create_plugin(config)

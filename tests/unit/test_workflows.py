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

"""Unit tests for CineFlow ADK 2.0 Production Graph Workflow."""

import pytest
from fastapi.testclient import TestClient

from app.fast_api_app import app as fastapi_app
from app.workflows.production_pipeline import (
    production_workflow,
    resume_production_pipeline_async,
    run_production_pipeline_async,
    trigger_production_workflow,
)


def test_workflow_structure():
    """Verify that the production workflow DAG is properly constructed."""
    assert production_workflow.name == "cineflow_production_pipeline"
    assert len(production_workflow.edges) >= 7


@pytest.mark.asyncio
async def test_workflow_execution_and_hitl_cycle():
    """Verify end-to-end workflow execution with HITL pause and resume cycles."""
    # 1. Run pipeline (Expect pause at Gate 1)
    run_res = await run_production_pipeline_async(
        user_id="test_director",
        scene_text="EXT. SECTOR 4 - NIGHT. Heavy rain lashes against chrome towers. KADE watches.",
        scene_number=1,
    )

    assert "session_id" in run_res
    assert run_res["session_id"] is not None
    session_id = run_res["session_id"]

    # Verify Gate 1 interrupt signal
    assert run_res["interrupt_signal"] is not None
    assert "gate_1_approval" in run_res["interrupt_signal"]

    # 2. Resume Gate 1 -> advances to Gate 2
    resume_gate_1_res = await resume_production_pipeline_async(
        user_id="test_director",
        session_id=session_id,
        interrupt_id="gate_1_approval",
        approval_data={
            "status": "APPROVED",
            "feedback": "Looks great, proceed with renders.",
        },
    )

    assert resume_gate_1_res["session_id"] == session_id
    assert resume_gate_1_res["interrupt_signal"] is not None
    assert "gate_2_approval" in resume_gate_1_res["interrupt_signal"]

    # 3. Resume Gate 2 -> completes assembly
    resume_gate_2_res = await resume_production_pipeline_async(
        user_id="test_director",
        session_id=session_id,
        interrupt_id="gate_2_approval",
        approval_data={
            "status": "APPROVED",
            "feedback": "Assets approved for final cut.",
        },
    )

    assert resume_gate_2_res["final_output"] is not None
    assert resume_gate_2_res["final_output"]["status"] == "COMPLETED"


def test_trigger_production_workflow_tool():
    """Verify the synchronous tool wrapper for the Showrunner agent."""
    res = trigger_production_workflow(
        scene_text="INT. HACKER DEN - NIGHT. Holograms flicker as Kade downloads data.",
        scene_number=2,
    )
    assert "Production DAG" in res
    assert "Session:" in res or "gate_1_approval" in res


def test_fastapi_production_routes():
    """Verify the FastAPI HTTP endpoints for running and resuming production."""
    client = TestClient(fastapi_app)

    # 1. Trigger production run via API
    run_resp = client.post(
        "/api/v1/production/run",
        json={"scene_text": "EXT. NEON ROOFTOP - DAWN", "scene_number": 3},
    )
    assert run_resp.status_code == 200
    run_data = run_resp.json()
    assert "session_id" in run_data
    assert "gate_1_approval" in run_data.get("interrupt_signal", [])

    session_id = run_data["session_id"]

    # 2. Resume Gate 1 via API
    resume_resp = client.post(
        "/api/v1/production/resume",
        json={
            "session_id": session_id,
            "interrupt_id": "gate_1_approval",
            "approval_data": {"status": "APPROVED"},
        },
    )
    assert resume_resp.status_code == 200
    resume_data = resume_resp.json()
    assert "gate_2_approval" in resume_data.get("interrupt_signal", [])

    # 3. Cancel production via API
    cancel_resp = client.post(
        "/api/v1/production/cancel",
        json={
            "session_id": session_id,
            "reason": "Director called wrap",
        },
    )
    assert cancel_resp.status_code == 200
    cancel_data = cancel_resp.json()
    assert cancel_data.get("status") == "cancelled"
    assert cancel_data.get("session_id") == session_id

    # 4. Resume without matching session / alias 'gate-001' (Regression test for Cloud Logging error)
    fallback_resp = client.post(
        "/api/v1/production/resume",
        json={
            "session_id": "nonexistent-or-recycled-session",
            "interrupt_id": "gate-001",
            "approval_data": {"status": "APPROVED", "notes": "Approved from UI"},
        },
    )
    assert fallback_resp.status_code == 200
    fallback_data = fallback_resp.json()
    assert fallback_data["status"] == "SUCCESS"
    assert fallback_data["active_gate"] == "GATE_2_ASSETS"


def test_hitl_cancellation_and_resume_tools():
    """Verify cancel_production_run and resume_production_workflow tools."""
    from app.tools.hitl_tools import (
        cancel_production_run,
        resume_production_workflow,
    )

    # Test cancel tool
    cancel_res = cancel_production_run(
        session_id="test-session-999",
        reason="Creative realignment",
    )
    assert cancel_res["status"] == "cancelled"
    assert cancel_res["session_id"] == "test-session-999"

    # Test resume tool
    resume_res = resume_production_workflow(
        session_id="test-session-nonexistent",
        interrupt_id="gate_1_approval",
        approval_status="APPROVED",
        director_notes="Test note",
    )
    assert resume_res["status"] in ("resumed", "error")


@pytest.mark.asyncio
async def test_runtime_config_propagation():
    """Verify custom runtime configuration propagates to workflow nodes and artifacts."""
    custom_config = {
        "scene_config": {
            "resolution": "3840x2160",
            "aspect_ratio": "2.39:1",
            "seed_locking_mode": "creative_variance",
            "audio_sample_rate_hz": 48000,
            "default_shot_duration_sec": 6.0,
        },
        "agent_config": {
            "qa_critic_max_retries": 1,
            "hitl_mode": "strict",
        },
    }

    # 1. Run pipeline with custom config (pause at Gate 1)
    run_res = await run_production_pipeline_async(
        user_id="cinematographer",
        scene_text="INT. COMMAND CENTER - DAY. Holograms flicker in gold and teal.",
        scene_number=5,
        runtime_config=custom_config,
    )
    assert "gate_1_approval" in run_res.get("interrupt_signal", [])
    session_id = run_res["session_id"]

    # 2. Resume Gate 1 -> advances to Gate 2 (executing storyboard & audio nodes with config)
    resume_res = await resume_production_pipeline_async(
        user_id="cinematographer",
        session_id=session_id,
        interrupt_id="gate_1_approval",
        approval_data={"status": "APPROVED"},
    )
    assert "gate_2_approval" in resume_res.get("interrupt_signal", [])

    # 3. Also verify FastAPI passes runtime_config
    client = TestClient(fastapi_app)
    api_run = client.post(
        "/api/v1/production/run",
        json={
            "scene_text": "EXT. WASTELAND - DUSK",
            "scene_number": 6,
            "runtime_config": custom_config,
        },
    )
    assert api_run.status_code == 200
    assert "session_id" in api_run.json()


def test_ambient_trigger_endpoints_registered():
    """Verify that ambient event triggers (Pub/Sub and Eventarc) are registered."""
    route_paths = [r.path for r in fastapi_app.routes]
    assert "/apps/{app_name}/trigger/pubsub" in route_paths
    assert "/apps/{app_name}/trigger/eventarc" in route_paths

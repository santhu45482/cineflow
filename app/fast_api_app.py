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

import contextlib
import logging
import os
from collections.abc import AsyncIterator
from typing import Any

from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pydantic import BaseModel, Field

from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.live_voice import handle_table_read_websocket
from app.app_utils.reasoning_engine_adapter import (
    attach_reasoning_engine_routes,
)
from app.tools.hitl_tools import cancel_production_run
from app.workflows.production_pipeline import (
    resume_production_pipeline_async,
    run_production_pipeline_async,
)

load_dotenv()
logger = logging.getLogger(__name__)

allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)
otel_to_cloud = os.environ.get(
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY", "true"
).lower() in ("true", "1")

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup_google_cloud_telemetry() -> None:
    """Configures Google Cloud In-House OpenTelemetry exporter (Cloud Trace & Cloud Logging)."""
    telemetry_enabled = os.environ.get(
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY", "true"
    ).lower() in ("true", "1")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "cineflow-10")

    if not telemetry_enabled:
        return

    service_name = os.getenv("OTEL_SERVICE_NAME", "cineflow-studio")
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.namespace": "cineflow",
            "cloud.project_id": project_id,
        }
    )

    try:
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

        exporter = CloudTraceSpanExporter(project_id=project_id)
        current_provider = trace.get_tracer_provider()
        if isinstance(current_provider, TracerProvider):
            current_provider.add_span_processor(BatchSpanProcessor(exporter))
        else:
            try:
                provider = TracerProvider(resource=resource)
                provider.add_span_processor(BatchSpanProcessor(exporter))
                trace.set_tracer_provider(provider)
            except Exception:
                if hasattr(current_provider, "_delegate") and isinstance(
                    current_provider._delegate, TracerProvider
                ):
                    current_provider._delegate.add_span_processor(
                        BatchSpanProcessor(exporter)
                    )
        logger.info(
            "Configured Google Cloud In-House Trace exporter for project: %s",
            project_id,
        )
    except Exception as exc:
        logger.debug(
            "Google Cloud Trace native exporter skipped or handled by ADK: %s", exc
        )


setup_google_cloud_telemetry()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from app.agent import app as adk_app
    from app.agent import root_agent

    runner = Runner(
        app=adk_app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        auto_create_session=True,
    )
    app.state.runner = runner
    app.state.agent_app_name = adk_app.name
    await attach_a2a_routes(
        app,
        agent=root_agent,
        runner=runner,
        task_store=InMemoryTaskStore(),
        rpc_path=f"/a2a/{adk_app.name}",
    )
    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=services.ARTIFACT_SERVICE_URI,
    allow_origins=allow_origins,
    session_service_uri=services.SESSION_SERVICE_URI,
    otel_to_cloud=otel_to_cloud,
    lifespan=lifespan,
    trigger_sources=["pubsub", "eventarc"],
)
app.title = "cineflow"
app.description = "API for interacting with the Agent cineflow"

# Proxy routes so the Vertex AI Console Playground (reasoning_engine SDK) can
# talk to this agent alongside the native adk_api routes.
attach_reasoning_engine_routes(app)


# Attach Gemini Live API WebSocket endpoint for real-time table reads and rehearsals
@app.websocket("/ws/table-read/{session_id}")
async def websocket_table_read_endpoint(websocket: WebSocket, session_id: str):
    await handle_table_read_websocket(websocket, session_id)


class ProductionRunRequest(BaseModel):
    user_id: str = Field(default="director")
    session_id: str | None = Field(default=None)
    scene_text: str = Field(default="")
    scene_number: int = Field(default=1)
    runtime_config: dict[str, Any] | None = Field(
        default=None, description="Optional scene and agent runtime configuration"
    )


class ProductionResumeRequest(BaseModel):
    user_id: str = Field(default="director")
    session_id: str = Field(description="Active session ID paused at an interrupt")
    interrupt_id: str = Field(default="gate_1_approval")
    approval_data: dict = Field(default_factory=dict)


class ProductionCancelRequest(BaseModel):
    session_id: str = Field(description="Active session ID to cancel")
    reason: str = Field(default="Production aborted by Director")


@app.post("/api/v1/production/run")
async def run_production_endpoint(req: ProductionRunRequest):
    """Trigger the ADK 2.0 end-to-end production pipeline."""
    result = await run_production_pipeline_async(
        user_id=req.user_id,
        session_id=req.session_id,
        scene_text=req.scene_text,
        scene_number=req.scene_number,
        runtime_config=req.runtime_config,
    )
    return result


@app.post("/api/v1/production/resume")
async def resume_production_endpoint(req: ProductionResumeRequest):
    """Resume a paused ADK 2.0 production pipeline with Director feedback."""
    result = await resume_production_pipeline_async(
        user_id=req.user_id,
        session_id=req.session_id,
        interrupt_id=req.interrupt_id,
        approval_data=req.approval_data,
    )
    return result


@app.post("/api/v1/production/cancel")
async def cancel_production_endpoint(req: ProductionCancelRequest):
    """Cancel an active or paused ADK 2.0 production pipeline."""
    result = cancel_production_run(
        session_id=req.session_id,
        reason=req.reason,
    )
    return result


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

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

"""CineFlow: Centralized Model Configurations and Runtime Settings."""

import os
from typing import Any

from google.adk.models import BaseLlm, Gemini
from google.adk.models.apigee_llm import ApigeeLlm
from google.genai import types
from pydantic import BaseModel, Field

# Model definitions (strictly preserved)
DEFAULT_MODEL = "gemini-3.7-flash"
SHOWRUNNER_MODEL = "gemini-3.7-flash"
SHOWRUNNER_FALLBACK_MODEL = "gemini-2.5-pro"
SHOWRUNNER_THINKING_BUDGET = 2048
SCREENPLAY_MODEL = "gemini-3.7-flash"
CASTING_MODEL = "gemini-3.7-flash"
STORYBOARD_MODEL = "gemini-3.7-flash"
IMAGE_MODEL = "gemini-3.1-flash-image"
AUDIO_DIRECTOR_MODEL = "gemini-3.7-flash"
LYRIA_AUDIO_MODEL = "lyria-3.5"
LIVE_API_MODEL = "gemini-3.1-flash-live"
QA_MODEL = "gemini-3.7-flash"
STUDIO_OPS_MODEL = "gemini-3.7-flash"

# Enterprise Apigee AI Gateway Settings
APIGEE_PROXY_URL = os.getenv("APIGEE_PROXY_URL")
APIGEE_API_KEY = os.getenv("APIGEE_API_KEY")


def create_gemini_model(model_name: str = DEFAULT_MODEL) -> BaseLlm:
    """Create a configured Gemini or Apigee-governed LLM instance."""
    if APIGEE_PROXY_URL:
        # Format model string for Apigee proxy routing (apigee/<model_id>)
        apigee_model_str = (
            f"apigee/{model_name}"
            if not model_name.startswith("apigee/")
            else model_name
        )
        custom_headers = {}
        if APIGEE_API_KEY:
            custom_headers["x-api-key"] = APIGEE_API_KEY
            custom_headers["Authorization"] = f"Bearer {APIGEE_API_KEY}"
        return ApigeeLlm(
            model=apigee_model_str,
            proxy_url=APIGEE_PROXY_URL,
            custom_headers=custom_headers if custom_headers else None,
            retry_options=types.HttpRetryOptions(attempts=3),
        )

    return Gemini(
        model=model_name,
        retry_options=types.HttpRetryOptions(attempts=3),
    )


def create_routed_showrunner_llm() -> BaseLlm:
    """Creates a resilient RoutedLlm for Showrunner with primary -> fallback routing."""
    from app.routing import RoutedLlm, RoutingErrorContext

    primary_llm = create_gemini_model(SHOWRUNNER_MODEL)
    fallback_llm = create_gemini_model(SHOWRUNNER_FALLBACK_MODEL)

    def showrunner_router(
        models: dict[str, BaseLlm],
        request: Any,
        error_context: RoutingErrorContext | None,
    ) -> str | None:
        if not error_context:
            return "primary"
        if "primary" in error_context.failed_keys:
            # Automatic failover to fallback model on quota/rate-limit error
            return "fallback"
        return None

    return RoutedLlm(
        models={"primary": primary_llm, "fallback": fallback_llm},
        router=showrunner_router,
    )


def create_thinking_content_config(
    thinking_budget: int = SHOWRUNNER_THINKING_BUDGET,
) -> types.GenerateContentConfig:
    """Creates a GenerateContentConfig with internal thinking budget enabled."""
    return types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget)
    )


class ScenePipelineConfig(BaseModel):
    """Configuration for a specific scene production pipeline run."""

    resolution: str = Field(
        default="1920x1080",
        description="Target render resolution (e.g. 1920x1080, 3840x2160)",
    )
    aspect_ratio: str = Field(
        default="16:9",
        description="Aspect ratio (e.g. 16:9, 2.39:1 Cinemascope, 4:3 Academy)",
    )
    seed_locking_mode: str = Field(
        default="deterministic",
        description="'deterministic' (fixed seed tokens) or 'creative_variance'",
    )
    audio_sample_rate_hz: int = Field(
        default=24000, description="Audio output sample rate in Hz"
    )
    default_shot_duration_sec: float = Field(
        default=4.0, description="Default shot duration in seconds"
    )


class AgentExecutionConfig(BaseModel):
    """Execution parameters for agents and Generator-Critic loops."""

    temperature: float = Field(
        default=0.7, description="Sampling temperature for LLM generation"
    )
    qa_critic_max_retries: int = Field(
        default=2,
        description="Maximum automated Generator-Critic refinement iterations",
    )
    hitl_mode: str = Field(
        default="strict",
        description="'strict' (pause at all gates for Director sign-off) or 'auto_pilot'",
    )


class StudioRuntimeConfig(BaseModel):
    """Hierarchical Studio Runtime Configuration."""

    model_armor_enabled: bool = Field(
        default=True, description="Enforce Model Armor security guardrails"
    )
    telemetry_enabled: bool = Field(
        default=True,
        description="Enable Google Cloud Operations (Cloud Trace & Cloud Monitoring) export",
    )
    render_timeout_sec: int = Field(
        default=300, description="Max render timeout for asset generation before abort"
    )
    scene_config: ScenePipelineConfig = Field(default_factory=ScenePipelineConfig)
    agent_config: AgentExecutionConfig = Field(default_factory=AgentExecutionConfig)


def get_runtime_config(state: dict | None = None) -> StudioRuntimeConfig:
    """Retrieve StudioRuntimeConfig from session state dictionary or return default configuration."""
    if not state:
        return StudioRuntimeConfig()
    raw = state.get("runtime_config")
    if isinstance(raw, StudioRuntimeConfig):
        return raw
    if isinstance(raw, dict):
        return StudioRuntimeConfig.model_validate(raw)
    return StudioRuntimeConfig()

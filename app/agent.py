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

"""CineFlow: Enterprise-Grade Autonomous Multi-Agent Cinema Studio."""

from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps import App, ResumabilityConfig
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini

from app.agents import (
    audio_director_agent,
    casting_agent,
    qa_critic_agent,
    score_composer_agent,
    screenplay_agent,
    showrunner_agent,
    storyboard_agent,
    studio_ops_agent,
)
from app.config import (
    APIGEE_API_KEY,
    APIGEE_PROXY_URL,
    AUDIO_DIRECTOR_MODEL,
    DEFAULT_MODEL,
    IMAGE_MODEL,
    LIVE_API_MODEL,
    LYRIA_AUDIO_MODEL,
    QA_MODEL,
    SHOWRUNNER_FALLBACK_MODEL,
    SHOWRUNNER_MODEL,
    SHOWRUNNER_THINKING_BUDGET,
    create_gemini_model,
    create_routed_showrunner_llm,
    create_thinking_content_config,
)
from app.plugins import ModelArmorGuardrailPlugin
from app.routing import RoutedAgent, RoutedLlm

# Backwards-compatible aliases
_create_gemini_model = create_gemini_model

# Root agent export for ADK and agents-cli runtime
root_agent = showrunner_agent

# ADK App definition with production studio enterprise configurations
app = App(
    name="app",
    root_agent=root_agent,
    plugins=[
        ModelArmorGuardrailPlugin(),
    ],
    resumability_config=ResumabilityConfig(is_resumable=True),
    events_compaction_config=EventsCompactionConfig(
        token_threshold=32000,
        event_retention_size=6,
        summarizer=LlmEventSummarizer(llm=Gemini(model=DEFAULT_MODEL)),
    ),
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=1800,
        cache_intervals=10,
    ),
)

__all__ = [
    "APIGEE_API_KEY",
    "APIGEE_PROXY_URL",
    "AUDIO_DIRECTOR_MODEL",
    "DEFAULT_MODEL",
    "IMAGE_MODEL",
    "LIVE_API_MODEL",
    "LYRIA_AUDIO_MODEL",
    "QA_MODEL",
    "SHOWRUNNER_FALLBACK_MODEL",
    "SHOWRUNNER_MODEL",
    "SHOWRUNNER_THINKING_BUDGET",
    "RoutedAgent",
    "RoutedLlm",
    "_create_gemini_model",
    "app",
    "audio_director_agent",
    "casting_agent",
    "create_gemini_model",
    "create_routed_showrunner_llm",
    "create_thinking_content_config",
    "qa_critic_agent",
    "root_agent",
    "score_composer_agent",
    "screenplay_agent",
    "showrunner_agent",
    "storyboard_agent",
    "studio_ops_agent",
]

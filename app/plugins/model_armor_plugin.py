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

"""Google Model Armor security guardrail plugin for CineFlow."""

import logging
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools import BaseTool, ToolContext
from google.genai import types

from app.security.model_armor import model_armor

logger = logging.getLogger("cineflow.plugins.model_armor")


class ModelArmorGuardrailPlugin(BasePlugin):
    """Studio-wide Model Armor security plugin.

    Intercepts model requests and tool inputs to prevent prompt injections,
    sanitize PII, and enforce Responsible AI policies across all studio agents.
    """

    def __init__(self, name: str = "model_armor_guardrail") -> None:
        super().__init__(name=name)

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> LlmResponse | None:
        """Inspect prompt contents before dispatching to the LLM."""
        if not llm_request.contents:
            return None

        for content in llm_request.contents:
            if not content.parts:
                continue
            for part in content.parts:
                if part.text:
                    is_safe, _, reason = model_armor.inspect_and_sanitize(part.text)
                    if not is_safe:
                        logger.warning(
                            "Model Armor blocked prompt in agent '%s': %s",
                            callback_context.agent_name,
                            reason,
                        )
                        return LlmResponse(
                            content=types.Content(
                                role="model",
                                parts=[
                                    types.Part.from_text(
                                        text=(
                                            f"[Model Armor Intercept] Request blocked by safety policy: {reason}"
                                        )
                                    )
                                ],
                            )
                        )
        return None

    async def before_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
    ) -> dict[str, Any] | None:
        """Inspect and sanitize tool invocation arguments before execution."""
        tool_name = getattr(tool, "name", str(tool))

        for key, value in tool_args.items():
            if isinstance(value, str):
                is_safe, _, reason = model_armor.inspect_and_sanitize(value)
                if not is_safe:
                    logger.warning(
                        "Model Armor blocked tool execution for '%s' (arg: %s): %s",
                        tool_name,
                        key,
                        reason,
                    )
                    return {
                        "status": "error",
                        "blocked": True,
                        "tool": tool_name,
                        "reason": f"Model Armor Security Intercept: {reason}",
                    }

        return None

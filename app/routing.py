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

"""CineFlow Intelligent Routing Engine.

Provides enterprise-grade Model Routing (RoutedLlm) and Agent Routing (RoutedAgent)
with automatic failover, complexity classification, and Apigee AI Gateway integration.
"""

import logging
from collections.abc import AsyncGenerator, Callable
from typing import Any, NamedTuple

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.models import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from pydantic import Field

logger = logging.getLogger("cineflow.routing")


class RoutingErrorContext(NamedTuple):
    """Context passed to router callbacks when a failover retry occurs."""

    failed_keys: set[str]
    last_error: Exception | None


# Type signatures for Model and Agent router callbacks
LlmRouter = Callable[
    [dict[str, BaseLlm], LlmRequest, RoutingErrorContext | None],
    str | None,
]

AgentRouter = Callable[
    [dict[str, BaseAgent], InvocationContext, RoutingErrorContext | None],
    str | None,
]


class RoutedLlm(BaseLlm):
    """Dynamically routes LLM requests across multiple models with failover.

    Supports:
    1. Primary -> Fallback on error (e.g. rate-limiting, 429 quota exhaustion).
    2. Input complexity auto-routing.
    3. Seamless compatibility with ADK BaseLlm interface.
    """

    models: dict[str, BaseLlm] = Field(default_factory=dict)
    router: Any = Field(default=None)

    def __init__(
        self,
        *,
        models: dict[str, BaseLlm],
        router: LlmRouter,
    ) -> None:
        if not models:
            raise ValueError("RoutedLlm requires at least one model in 'models'.")
        first_model_name = next(iter(models.values())).model
        super().__init__(model=f"routed:{first_model_name}")
        object.__setattr__(self, "models", models)
        object.__setattr__(self, "router", router)

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        """Routes content generation across models with pre-yield failover."""
        failed_keys: set[str] = set()
        last_error: Exception | None = None

        while True:
            err_ctx = (
                RoutingErrorContext(failed_keys=set(failed_keys), last_error=last_error)
                if last_error is not None
                else None
            )

            try:
                selected_key = self.router(self.models, llm_request, err_ctx)
            except Exception as router_exc:
                logger.error("Model router raised exception: %s", router_exc)
                raise router_exc

            if not selected_key or selected_key not in self.models:
                if last_error:
                    logger.error(
                        "Routing exhausted all models. Last error: %s",
                        last_error,
                    )
                    raise last_error
                raise ValueError(
                    f"Router returned invalid model key: '{selected_key}'. Available: {list(self.models.keys())}"
                )

            if selected_key in failed_keys:
                if last_error:
                    raise last_error
                raise RuntimeError(
                    f"Router re-selected already failed model key '{selected_key}'"
                )

            selected_llm = self.models[selected_key]
            logger.info("RoutedLlm selecting model key: '%s'", selected_key)

            has_yielded = False
            try:
                async for response in selected_llm.generate_content_async(
                    llm_request, stream=stream
                ):
                    has_yielded = True
                    yield response
                return
            except Exception as exec_err:
                if has_yielded:
                    logger.error(
                        "Model '%s' failed after yielding partial responses. Propagating error: %s",
                        selected_key,
                        exec_err,
                    )
                    raise exec_err

                logger.warning(
                    "Model '%s' failed before yielding events. Initiating failover. Error: %s",
                    selected_key,
                    exec_err,
                )
                failed_keys.add(selected_key)
                last_error = exec_err


class RoutedAgent(BaseAgent):
    """Dynamically routes agent invocations across specialized agents.

    Provides:
    1. Operational mode routing (e.g., Draft mode vs. Cinematic Master mode).
    2. Failover on agent crash before yielding events.
    3. Input complexity routing.
    """

    agents: dict[str, BaseAgent] = Field(default_factory=dict)
    router: Any = Field(default=None)

    def __init__(
        self,
        *,
        name: str,
        agents: dict[str, BaseAgent],
        router: AgentRouter,
        description: str = "Enterprise dynamic agent router.",
    ) -> None:
        if not agents:
            raise ValueError("RoutedAgent requires at least one target agent.")
        super().__init__(
            name=name,
            description=description,
            sub_agents=list(agents.values()),
        )
        object.__setattr__(self, "agents", agents)
        object.__setattr__(self, "router", router)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Runs the dynamically selected agent with failover protection."""
        failed_keys: set[str] = set()
        last_error: Exception | None = None

        while True:
            err_ctx = (
                RoutingErrorContext(failed_keys=set(failed_keys), last_error=last_error)
                if last_error is not None
                else None
            )

            try:
                selected_key = self.router(self.agents, ctx, err_ctx)
            except Exception as router_exc:
                logger.error("Agent router raised exception: %s", router_exc)
                raise router_exc

            if not selected_key or selected_key not in self.agents:
                if last_error:
                    logger.error(
                        "Agent routing exhausted options. Last error: %s",
                        last_error,
                    )
                    raise last_error
                raise ValueError(
                    f"Agent router returned invalid key: '{selected_key}'. Available: {list(self.agents.keys())}"
                )

            if selected_key in failed_keys:
                if last_error:
                    raise last_error
                raise RuntimeError(
                    f"Agent router re-selected failed key '{selected_key}'"
                )

            selected_agent = self.agents[selected_key]
            logger.info("RoutedAgent selecting agent: '%s'", selected_key)

            has_yielded = False
            try:
                async for event in selected_agent.run_async(ctx):
                    has_yielded = True
                    yield event
                return
            except Exception as agent_err:
                if has_yielded:
                    logger.error(
                        "Agent '%s' failed after emitting events. Propagating error: %s",
                        selected_key,
                        agent_err,
                    )
                    raise agent_err

                logger.warning(
                    "Agent '%s' failed before emitting events. Initiating failover. Error: %s",
                    selected_key,
                    agent_err,
                )
                failed_keys.add(selected_key)
                last_error = agent_err

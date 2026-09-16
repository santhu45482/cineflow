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

"""CineFlow Production Task Manager and Cancellation Controller."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ProductionTaskManager:
    """Singleton task manager tracking active workflow tasks and cancellation signals."""

    _instance: ProductionTaskManager | None = None

    def __init__(self) -> None:
        self._active_tasks: dict[str, asyncio.Task[Any]] = {}
        self._cancelled_sessions: dict[str, str] = {}

    @classmethod
    def get_instance(cls) -> ProductionTaskManager:
        if cls._instance is None:
            cls._instance = ProductionTaskManager()
        return cls._instance

    def register_task(self, session_id: str, task: asyncio.Task[Any]) -> None:
        """Register an active asyncio task for a production session."""
        self._active_tasks[session_id] = task

        def _cleanup(fut: asyncio.Future[Any]) -> None:
            self._active_tasks.pop(session_id, None)

        task.add_done_callback(_cleanup)

    def is_cancelled(self, session_id: str) -> bool:
        """Check if a session has received a cancellation signal."""
        return session_id in self._cancelled_sessions

    def get_cancellation_reason(self, session_id: str) -> str | None:
        """Retrieve cancellation reason if aborted."""
        return self._cancelled_sessions.get(session_id)

    def cancel_session(
        self, session_id: str, reason: str = "Production aborted by Director"
    ) -> bool:
        """Mark a session as cancelled and cancel any running asyncio task."""
        self._cancelled_sessions[session_id] = reason
        task = self._active_tasks.get(session_id)
        if task and not task.done():
            logger.info("Cancelling active task for session %s: %s", session_id, reason)
            task.cancel()
            return True
        return False

    def clear_session(self, session_id: str) -> None:
        """Clear task and cancellation registry for a session."""
        self._active_tasks.pop(session_id, None)
        self._cancelled_sessions.pop(session_id, None)


def get_task_manager() -> ProductionTaskManager:
    """Helper to access global task manager instance."""
    return ProductionTaskManager.get_instance()

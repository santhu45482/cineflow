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

"""CineFlow State Management Schemas and Helpers."""

from typing import Any

from pydantic import BaseModel, Field


class CharacterSheet(BaseModel):
    """Character bible entry with locked seed and visual identity."""

    character_id: str
    name: str
    seed_token: int
    visual_anchor: str
    voice_preset: str


class ShotUnit(BaseModel):
    """Atomic cinematic shot unit within a scene."""

    shot_id: str
    scene_number: int
    camera_movement: str
    visual_prompt: str
    dialogue_script: str | None = None
    character_id: str | None = None
    duration_sec: float = 4.0
    image_uri: str | None = None
    audio_uri: str | None = None
    score_uri: str | None = None
    qa_passed: bool = False
    qa_feedback: str | None = None


class ScriptScene(BaseModel):
    """Decomposed screenplay scene with slugline, action summary, and dialogue lines."""

    scene_number: int
    slugline: str  # e.g., 'INT. CYBERPUNK ALLEY - NIGHT'
    location: str
    time_of_day: str
    action_summary: str
    characters_present: list[str] = Field(default_factory=list)
    dialogue_blocks: list[dict[str, str]] = Field(
        default_factory=list
    )  # [{"character": "...", "text": "..."}]
    pacing_mood: str = "Tense / Atmospheric"


class MovieProductionBible(BaseModel):
    """Complete film production project state tracking pre-production, assets, and final assembly."""

    project_id: str
    title: str
    logline: str
    genre: str
    characters: dict[str, CharacterSheet] = Field(default_factory=dict)
    shots: list[ShotUnit] = Field(default_factory=list)
    script_scenes: list[ScriptScene] = Field(default_factory=list)
    script_lore_index: dict[str, str] = Field(default_factory=dict)
    hitl_gate: str = "GATE_1_PREPROD"  # GATE_1_PREPROD, GATE_2_ASSETS, GATE_3_FINAL
    gate_cleared: bool = False
    director_notes: list[str] = Field(default_factory=list)
    status: str = "IN_PROGRESS"  # IN_PROGRESS, PAUSED, CANCELLED, COMPLETED
    cancellation_reason: str | None = None


STATE_KEY_BIBLE = "production_bible"


def get_production_bible(state: dict[str, Any]) -> MovieProductionBible:
    """Retrieve MovieProductionBible from session state, or create a default instance."""
    raw = state.get(STATE_KEY_BIBLE)
    if raw is None:
        return MovieProductionBible(
            project_id="cineflow-proj-01",
            title="Untitled Film Project",
            logline="A futuristic cinema project in production.",
            genre="Sci-Fi / Drama",
        )
    if isinstance(raw, MovieProductionBible):
        return raw
    if isinstance(raw, dict):
        return MovieProductionBible.model_validate(raw)
    return MovieProductionBible(
        project_id="cineflow-proj-01",
        title="Untitled Film Project",
        logline="A futuristic cinema project in production.",
        genre="Sci-Fi / Drama",
    )


def save_production_bible(state: dict[str, Any], bible: MovieProductionBible) -> None:
    """Persist MovieProductionBible into session state."""
    state[STATE_KEY_BIBLE] = bible.model_dump()

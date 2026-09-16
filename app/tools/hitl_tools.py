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

"""Human-in-the-Loop (HITL) Gate Approval and Production State Tools."""

from typing import Any

from google.adk.tools import ToolContext

from app.security.model_armor import model_armor
from app.state import (
    CharacterSheet,
    MovieProductionBible,
    ShotUnit,
    get_production_bible,
    save_production_bible,
)


def approve_production_gate(
    gate_name: str,
    director_notes: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Approves a production milestone gate (GATE_1_PREPROD, GATE_2_ASSETS, GATE_3_FINAL) to advance the pipeline.

    Args:
        gate_name: Milestone gate name to approve.
        director_notes: Optional creative feedback or notes from Human Director.
        tool_context: ADK ToolContext for managing session state.

    Returns:
        Dict detailing the gate clearance and next allowable phase.
    """
    if director_notes:
        is_safe, sanitized, reason = model_armor.inspect_and_sanitize(director_notes)
        if not is_safe:
            return {
                "status": "error",
                "error": f"Model Armor Security Rejection: {reason}",
            }
        director_notes = sanitized

    bible = (
        get_production_bible(tool_context.state)
        if tool_context
        else MovieProductionBible(
            project_id="cineflow-01",
            title="CineFlow Cyberpunk Neo-Noir",
            logline="A detective hunts a rogue synthetic in neon rain.",
            genre="Cyberpunk / Neo-Noir",
        )
    )

    valid_gates = ["GATE_1_PREPROD", "GATE_2_ASSETS", "GATE_3_FINAL"]
    if gate_name not in valid_gates:
        return {
            "status": "error",
            "error": f"Invalid gate name '{gate_name}'. Valid: {valid_gates}",
        }

    bible.gate_cleared = True
    if director_notes:
        bible.director_notes.append(f"[{gate_name} Approved]: {director_notes}")

    next_gate_map = {
        "GATE_1_PREPROD": "GATE_2_ASSETS",
        "GATE_2_ASSETS": "GATE_3_FINAL",
        "GATE_3_FINAL": "COMPLETED",
    }
    next_gate = next_gate_map.get(gate_name, "COMPLETED")
    bible.hitl_gate = next_gate

    if tool_context:
        save_production_bible(tool_context.state, bible)

    return {
        "status": "gate_approved",
        "gate_cleared": gate_name,
        "next_gate": next_gate,
        "director_notes": director_notes or "Approved with no adjustments.",
        "message": f"Milestone '{gate_name}' cleared by Human Director. Pipeline progressing to '{next_gate}'.",
    }


def reject_production_gate(
    gate_name: str,
    feedback_notes: str,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Rejects or requests revisions for a production gate, recording notes for agent rework.

    Args:
        gate_name: Milestone gate name requiring revision.
        feedback_notes: Specific instructions and changes requested by Human Director.
        tool_context: ADK ToolContext for state access.

    Returns:
        Dict confirming rejection and storing director notes.
    """
    is_safe, sanitized, reason = model_armor.inspect_and_sanitize(feedback_notes)
    if not is_safe:
        return {"status": "error", "error": f"Model Armor Security Rejection: {reason}"}

    bible = (
        get_production_bible(tool_context.state)
        if tool_context
        else MovieProductionBible(
            project_id="cineflow-01",
            title="CineFlow Cyberpunk Neo-Noir",
            logline="A detective hunts a rogue synthetic in neon rain.",
            genre="Cyberpunk / Neo-Noir",
        )
    )

    bible.gate_cleared = False
    bible.director_notes.append(f"[{gate_name} Revision Requested]: {sanitized}")

    if tool_context:
        save_production_bible(tool_context.state, bible)

    return {
        "status": "gate_revision_requested",
        "gate": gate_name,
        "feedback_notes": sanitized,
        "message": f"Milestone '{gate_name}' flagged for revisions. Sub-agents must iterate according to notes: '{sanitized}'",
    }


def register_character_bible(
    character_id: str,
    name: str,
    seed_token: int,
    visual_anchor: str,
    voice_preset: str,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Registers a character sheet in the Production Bible with locked seed token and visual anchor.

    Args:
        character_id: Unique character identifier (e.g., 'char_kade').
        name: Full character name.
        seed_token: Deterministic seed integer for image generation consistency.
        visual_anchor: Detailed visual description and stylistic tokens for visual consistency.
        voice_preset: Voice profile for TTS synthesis.
        tool_context: ADK ToolContext for state persistence.

    Returns:
        Dict confirming character registration.
    """
    char = CharacterSheet(
        character_id=character_id,
        name=name,
        seed_token=seed_token,
        visual_anchor=visual_anchor,
        voice_preset=voice_preset,
    )

    if tool_context:
        bible = get_production_bible(tool_context.state)
        bible.characters[character_id] = char
        save_production_bible(tool_context.state, bible)

    return {
        "status": "success",
        "character_id": character_id,
        "name": name,
        "seed_token": seed_token,
        "visual_anchor": visual_anchor,
        "voice_preset": voice_preset,
        "message": f"Character '{name}' registered with locked seed {seed_token}.",
    }


def record_shot(
    shot_id: str,
    scene_number: int,
    camera_movement: str,
    visual_prompt: str,
    dialogue_script: str | None = None,
    character_id: str | None = None,
    duration_sec: float = 4.0,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Records a decomposed cinematic shot into the Production Bible shot list.

    Args:
        shot_id: Unique identifier for shot (e.g., 'shot-001').
        scene_number: Scene index number.
        camera_movement: Camera direction (e.g., 'Dolly In', 'Low Angle Pan').
        visual_prompt: Visual prompt for storyboard generation.
        dialogue_script: Optional spoken dialogue in this shot.
        character_id: Optional character speaking or featured.
        duration_sec: Duration in seconds.
        tool_context: ADK ToolContext.

    Returns:
        Dict confirming shot addition.
    """
    shot = ShotUnit(
        shot_id=shot_id,
        scene_number=scene_number,
        camera_movement=camera_movement,
        visual_prompt=visual_prompt,
        dialogue_script=dialogue_script,
        character_id=character_id,
        duration_sec=duration_sec,
    )

    if tool_context:
        bible = get_production_bible(tool_context.state)
        # update or append
        existing = [i for i, s in enumerate(bible.shots) if s.shot_id == shot_id]
        if existing:
            bible.shots[existing[0]] = shot
        else:
            bible.shots.append(shot)
        save_production_bible(tool_context.state, bible)

    return {
        "status": "success",
        "shot_id": shot_id,
        "scene_number": scene_number,
        "camera_movement": camera_movement,
        "duration_sec": duration_sec,
        "message": f"Shot '{shot_id}' added to Scene {scene_number}.",
    }


def get_production_overview(tool_context: ToolContext | None = None) -> dict[str, Any]:
    """Retrieves current MovieProductionBible overview, character count, shot list, and HITL gate status.

    Args:
        tool_context: ADK ToolContext.

    Returns:
        Dict summarizing current film production bible and pipeline state.
    """
    if tool_context:
        bible = get_production_bible(tool_context.state)
    else:
        bible = MovieProductionBible(
            project_id="cineflow-01",
            title="CineFlow Cyberpunk Neo-Noir",
            logline="A detective hunts a rogue synthetic in neon rain.",
            genre="Cyberpunk / Neo-Noir",
            characters={
                "char_kade": CharacterSheet(
                    character_id="char_kade",
                    name="Kade Mercer",
                    seed_token=849201,
                    visual_anchor="Rugged trenchcoat, neon reflection in cybernetic left eye, slick dark hair.",
                    voice_preset="Detective_Male_Gruff",
                )
            },
            shots=[
                ShotUnit(
                    shot_id="shot-001",
                    scene_number=1,
                    camera_movement="Slow tracking shot forward",
                    visual_prompt="Neon alleyway drenched in rain, hologram billboards flickering overhead.",
                    dialogue_script="The rain doesn't wash anything clean anymore.",
                    character_id="char_kade",
                    duration_sec=4.0,
                    image_uri="gs://cineflow-production-assets/storyboards/shot-001_849201.png",
                    audio_uri="gs://cineflow-production-assets/audio/shot-001.wav",
                    score_uri="gs://cineflow-production-assets/scores/shot-001.wav",
                    qa_passed=True,
                )
            ],
            hitl_gate="GATE_1_PREPROD",
            gate_cleared=True,
        )

    return {
        "status": "success",
        "project_id": bible.project_id,
        "title": bible.title,
        "genre": bible.genre,
        "current_gate": bible.hitl_gate,
        "gate_cleared": bible.gate_cleared,
        "characters": [c.model_dump() for c in bible.characters.values()],
        "shots_count": len(bible.shots),
        "shots": [s.model_dump() for s in bible.shots],
        "director_notes": bible.director_notes,
    }


def cancel_production_run(
    session_id: str,
    reason: str = "Production aborted by Director",
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Cancels an active or paused production run, aborting background tasks and updating state.

    Args:
        session_id: The session ID of the production workflow to cancel.
        reason: Optional explanation or context for the cancellation.
        tool_context: ADK ToolContext.

    Returns:
        Dict confirming cancellation status and details.
    """
    from app.app_utils.task_manager import get_task_manager

    manager = get_task_manager()
    was_active = manager.cancel_session(session_id, reason)

    if tool_context:
        bible = get_production_bible(tool_context.state)
        bible.status = "CANCELLED"
        bible.cancellation_reason = reason
        bible.director_notes.append(f"[PRODUCTION CANCELLED]: {reason}")
        save_production_bible(tool_context.state, bible)

    return {
        "status": "cancelled",
        "session_id": session_id,
        "was_active_task": was_active,
        "reason": reason,
        "message": f"Production session '{session_id}' has been cancelled. Reason: {reason}",
    }


def resume_production_workflow(
    session_id: str,
    interrupt_id: str = "gate_1_approval",
    approval_status: str = "APPROVED",
    director_notes: str = "Approved by Director",
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Resumes a paused production pipeline at a Human-in-the-Loop milestone gate.

    Args:
        session_id: The session ID of the paused workflow.
        interrupt_id: The interrupt checkpoint ID (e.g., 'gate_1_approval', 'gate_2_approval').
        approval_status: 'APPROVED' or 'REJECTED'.
        director_notes: Feedback notes from the Director.
        tool_context: ADK ToolContext.

    Returns:
        Dict containing resumption details and updated workflow output.
    """
    import asyncio

    from app.workflows.production_pipeline import resume_production_pipeline_async

    approval_payload = {
        "status": approval_status,
        "feedback": director_notes,
    }

    coro = resume_production_pipeline_async(
        session_id=session_id,
        interrupt_id=interrupt_id,
        approval_data=approval_payload,
    )

    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
            res = loop.run_until_complete(coro)
        else:
            res = loop.run_until_complete(coro)
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to resume production workflow: {e}",
        }

    if tool_context:
        bible = get_production_bible(tool_context.state)
        bible.status = "IN_PROGRESS"
        bible.director_notes.append(f"[{interrupt_id} Resumed]: {director_notes}")
        save_production_bible(tool_context.state, bible)

    return {
        "status": "resumed",
        "session_id": session_id,
        "interrupt_id": interrupt_id,
        "workflow_result": res,
        "message": f"Session '{session_id}' resumed at '{interrupt_id}'.",
    }

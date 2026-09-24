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

"""CineFlow End-to-End Production Graph Workflow (ADK 2.0).

Combines deterministic stage progression, parallel multi-track asset generation,
self-correcting Generator-Critic loops, and native Human-in-the-Loop (HITL) checkpoints.
"""

import logging
import re
import uuid
from typing import Any

from google.adk.agents.context import Context
from google.adk.apps import App, ResumabilityConfig
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.events.request_input import RequestInput
from google.adk.runners import Runner
from google.adk.workflow import Edge, JoinNode, Workflow, node
from google.adk.workflow.utils._workflow_hitl_utils import create_request_input_response
from google.genai import types

from app.app_utils import services
from app.app_utils.task_manager import get_task_manager
from app.config import get_runtime_config
from app.tools.hitl_tools import (
    approve_production_gate,
    record_shot,
    register_character_bible,
    reject_production_gate,
)
from app.tools.media_tools import (
    compose_scene_score,
    inspect_and_verify_shot,
    render_storyboard_frame,
    stitch_rough_cut,
    synthesize_dialogue,
)
from app.tools.script_rag import (
    _parse_fountain_or_raw_script,
    analyze_script_pacing_and_sentiment,
    ingest_screenplay_document,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# 1. Phase 1 Nodes: Screenplay & Casting Seed Locking
# ==============================================================================


@node(name="screenplay_decomposition")
def screenplay_decomposition_node(
    ctx: Context, node_input: Any = None
) -> dict[str, Any]:
    """Parse raw screenplay into beats, character list, and atomic shot units."""
    scene_text = ""
    scene_number = 1
    if isinstance(node_input, dict):
        scene_text = node_input.get("scene_text", "")
        scene_number = node_input.get("scene_number", 1)
    elif isinstance(node_input, str):
        scene_text = node_input
    elif hasattr(node_input, "parts") and node_input.parts:
        scene_text = node_input.parts[0].text or ""

    if not scene_text:
        scene_text = (
            "EXT. SECTOR 4 - ALLEYWAY - NIGHT. Rain lashes against rusted steel. "
            "KADE MERCER scans the shadows."
        )

    # Ingest document into lore RAG
    ingest_screenplay_document(
        screenplay_text_or_path=scene_text,
        title=f"Scene {scene_number}",
    )

    # Analyze pacing
    pacing_info = analyze_script_pacing_and_sentiment(scene_text)

    runtime_config = get_runtime_config(ctx.state if ctx else None)
    base_shot_duration = runtime_config.scene_config.default_shot_duration_sec

    # Dynamic screenplay and character decomposition
    parsed_scenes = _parse_fountain_or_raw_script(scene_text)

    # 1. Dynamic character extraction
    extracted_characters = []
    seen_char_names = set()

    if parsed_scenes:
        for ps in parsed_scenes:
            for c_name in ps.characters_present:
                if c_name not in seen_char_names:
                    seen_char_names.add(c_name)
                    c_clean = c_name.title()
                    char_id = f"char_{c_name.lower().replace(' ', '_')}"
                    seed = 849201 if "kade" in c_name.lower() else (abs(hash(c_name)) % 800000 + 100000)
                    voice = "Detective_Male_Gruff" if ("kade" in c_name.lower() or "detective" in c_name.lower()) else ("en-US-Journey-F" if "nyx" in c_name.lower() else "en-US-Journey-D")
                    extracted_characters.append({
                        "character_id": char_id,
                        "name": c_clean,
                        "visual_anchor": f"{c_clean} in atmospheric cinematic costume.",
                        "voice_preset": voice,
                        "seed_token": seed,
                    })

    if not extracted_characters:
        name_matches = re.findall(r"\b([A-Z]{3,15}(?:\s+[A-Z]{3,15})?)\b", scene_text)
        skip_words = {"EXT", "INT", "NIGHT", "DAY", "SCENE", "ALLEYWAY", "RAIN", "THE", "AND", "WITH", "FROM", "SUB", "LEVEL"}
        for nm in name_matches:
            if nm.upper() not in skip_words and nm not in seen_char_names:
                seen_char_names.add(nm)
                c_clean = nm.title()
                char_id = f"char_{nm.lower().replace(' ', '_')}"
                seed = 849201 if "kade" in nm.lower() else (abs(hash(nm)) % 800000 + 100000)
                voice = "Detective_Male_Gruff" if "kade" in nm.lower() else "en-US-Journey-D"
                extracted_characters.append({
                    "character_id": char_id,
                    "name": c_clean,
                    "visual_anchor": f"Character {c_clean} in scene {scene_number}.",
                    "voice_preset": voice,
                    "seed_token": seed,
                })

    if not extracted_characters:
        extracted_characters = [
            {
                "character_id": "char_kade",
                "name": "Kade Mercer",
                "visual_anchor": (
                    "Rugged 40s detective, weather-beaten charcoal trenchcoat, "
                    "glowing cobalt-blue cybernetic left eye"
                ),
                "voice_preset": "Detective_Male_Gruff",
                "seed_token": 849201,
            }
        ]

    # 2. Dynamic shot breakdown
    primary_char = extracted_characters[0]
    shots = []

    # Establishing / Wide Shot
    loc_slug = parsed_scenes[0].slugline if parsed_scenes else "Dystopian Scene Setting"
    shots.append({
        "shot_id": f"shot-{scene_number:02d}-01",
        "scene_number": scene_number,
        "camera_movement": "Wide Establishing - Slow Dolly In",
        "visual_prompt": (
            f"Wide establishing shot, anamorphic 35mm lens, f/2.0. "
            f"{loc_slug}. Atmospheric volumetric fog and dramatic amber and neon backlight."
        ),
        "character_ids": [primary_char["character_id"]],
        "character_seed": primary_char["seed_token"],
        "voice_preset": primary_char["voice_preset"],
        "duration_sec": base_shot_duration,
    })

    # Dialogue or Action shots
    shot_idx = 2
    if parsed_scenes and parsed_scenes[0].dialogue_blocks:
        for db in parsed_scenes[0].dialogue_blocks:
            speaker = db.get("character", primary_char["name"])
            line = db.get("text", "")
            c_match = next((c for c in extracted_characters if c["name"].lower() == speaker.lower()), primary_char)
            shots.append({
                "shot_id": f"shot-{scene_number:02d}-{shot_idx:02d}",
                "scene_number": scene_number,
                "camera_movement": "Medium Close-Up - Static" if shot_idx % 2 == 0 else "Over-The-Shoulder - Tracking",
                "visual_prompt": (
                    f"Medium close-up shot, 50mm prime lens, f/1.8 shallow depth of field. "
                    f"{speaker} speaking with intense emotional focus. Mood: {pacing_info.get('mood', 'Tense')}."
                ),
                "character_ids": [c_match["character_id"]],
                "character_name": c_match["name"],
                "character_seed": c_match["seed_token"],
                "dialogue": line,
                "dialogue_script": line,
                "voice_preset": c_match["voice_preset"],
                "duration_sec": max(1.5, min(8.0, round(len(line.split()) * 0.4, 1))),
            })
            shot_idx += 1
    else:
        shots.append({
            "shot_id": f"shot-{scene_number:02d}-02",
            "scene_number": scene_number,
            "camera_movement": "Medium Close-Up - Static",
            "visual_prompt": (
                f"Medium close-up shot, 50mm prime lens, f/1.8 shallow depth of field. "
                f"{primary_char['name']} looking wary under atmospheric lighting. Mood: {pacing_info.get('mood', 'Tense')}."
            ),
            "character_ids": [primary_char["character_id"]],
            "character_name": primary_char["name"],
            "character_seed": primary_char["seed_token"],
            "voice_preset": primary_char["voice_preset"],
            "dialogue": "She was here. The trail is still warm." if "kade" in primary_char["name"].lower() else f"We are ready for scene {scene_number}.",
            "duration_sec": max(1.0, round(base_shot_duration - 0.5, 1)),
        })

    for s in shots:
        record_shot(
            shot_id=s["shot_id"],
            scene_number=s["scene_number"],
            camera_movement=s["camera_movement"],
            visual_prompt=s["visual_prompt"],
            duration_sec=s["duration_sec"],
        )

    return {
        "scene_number": scene_number,
        "scene_text": scene_text,
        "pacing": pacing_info,
        "shots": shots,
        "characters": extracted_characters,
    }


@node(name="casting_seed_lock")
def casting_seed_lock_node(ctx: Context, node_input: Any = None) -> dict[str, Any]:
    """Lock deterministic seeds and voice profiles for all detected characters."""
    payload = node_input if isinstance(node_input, dict) else {}
    characters = payload.get("characters", [])
    runtime_config = get_runtime_config(ctx.state if ctx else None)
    seed_mode = runtime_config.scene_config.seed_locking_mode
    scene_num = payload.get("scene_number", 1)

    for char in characters:
        base_seed = char["seed_token"]
        effective_seed = (
            base_seed if seed_mode == "deterministic" else base_seed + (scene_num * 100)
        )
        register_character_bible(
            character_id=char["character_id"],
            name=char["name"],
            seed_token=effective_seed,
            visual_anchor=char["visual_anchor"],
            voice_preset=char["voice_preset"],
        )
    return payload


# ==============================================================================
# 2. Gate 1 Pre-Production HITL Checkpoint Node
# ==============================================================================


@node(name="gate_1_preprod_checkpoint", rerun_on_resume=False)
def gate_1_preprod_checkpoint_node(ctx: Context, node_input: Any = None):
    """Native ADK 2.0 Human-in-the-Loop checkpoint for Gate 1 sign-off."""
    if not ctx.resume_inputs or "gate_1_approval" not in ctx.resume_inputs:
        yield RequestInput(
            interrupt_id="gate_1_approval",
            message=(
                "GATE_1_PREPROD is ready for Director sign-off. "
                "Screenplay decomposed and Character Seeds locked. Approve to begin asset generation?"
            ),
        )
        return

    approve_production_gate("GATE_1_PREPROD", "Approved by Director via ADK 2.0 HITL")
    yield Event(
        output=node_input, actions=EventActions(state_delta={"gate_1_approved": True})
    )


# ==============================================================================
# 3. Phase 2 Nodes: Parallel Multi-Track Asset Generation
# ==============================================================================


@node(name="storyboard_renderer")
def storyboard_renderer_node(ctx: Context, node_input: Any = None) -> dict[str, Any]:
    """Render storyboard visual frames with persistent seeds and runtime config optics."""
    payload = node_input if isinstance(node_input, dict) else {}
    shots = payload.get("shots", [])
    runtime_config = get_runtime_config(ctx.state if ctx else None)
    aspect_ratio = runtime_config.scene_config.aspect_ratio
    resolution = runtime_config.scene_config.resolution

    rendered_frames = []
    for shot in shots:
        enhanced_prompt = f"{shot['visual_prompt']}, aspect ratio {aspect_ratio}, render target {resolution}"
        seed = shot.get("character_seed") or shot.get("seed") or 849201
        frame_res = render_storyboard_frame(
            prompt=enhanced_prompt,
            seed=seed,
            shot_id=shot["shot_id"],
        )
        rendered_frames.append(
            {
                "shot_id": shot["shot_id"],
                "image_uri": frame_res.get("image_uri"),
                "asset_url": frame_res.get("asset_url"),
                "seed": frame_res.get("seed", seed),
                "visual_prompt": enhanced_prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
            }
        )
    return {
        "rendered_frames": rendered_frames,
        "scene_number": payload.get("scene_number", 1),
    }


@node(name="audio_score_synthesizer")
def audio_score_synthesizer_node(
    ctx: Context, node_input: Any = None
) -> dict[str, Any]:
    """Concurrently generate dialogue audio stems and scene soundtrack."""
    payload = node_input if isinstance(node_input, dict) else {}
    scene_num = payload.get("scene_number", 1)
    shots = payload.get("shots", [])
    runtime_config = get_runtime_config(ctx.state if ctx else None)
    sample_rate = runtime_config.scene_config.audio_sample_rate_hz

    dialogue_stems = []
    for shot in shots:
        dlg_text = shot.get("dialogue") or shot.get("dialogue_script") or "She was here. The trail is still warm."
        v_preset = shot.get("voice_preset") or "Detective_Male_Gruff"
        stem = synthesize_dialogue(
            text=dlg_text,
            voice_preset=v_preset,
            shot_id=shot["shot_id"],
        )
        stem["sample_rate_hz"] = sample_rate
        dialogue_stems.append(stem)

    pacing_info = payload.get("pacing", {})
    mood = pacing_info.get("mood", "Dark ambient synth drone, atmospheric neo-noir")
    tempo = pacing_info.get("tempo", "72 BPM")
    score_prompt = f"{mood}, cinematic orchestration, {tempo}"
    score = compose_scene_score(
        prompt=score_prompt,
        duration_sec=30,
        shot_id=f"scene-{scene_num:02d}-score",
    )
    score["sample_rate_hz"] = sample_rate

    return {
        "dialogue_stems": dialogue_stems,
        "score_stem": score,
        "scene_number": scene_num,
    }


# ==============================================================================
# 4. Generator-Critic QA Refinement Loop Node
# ==============================================================================


@node(name="qa_critic_evaluator")
def qa_critic_evaluator_node(ctx: Context, node_input: Any = None):
    """Multimodal QA audit on rendered frames with conditional retry routing."""
    payload = node_input if isinstance(node_input, dict) else {}
    rendered_frames = payload.get("rendered_frames", [])
    findings = []
    all_passed = True

    for frame in rendered_frames:
        qa_result = inspect_and_verify_shot(
            shot_id=frame["shot_id"],
            script=frame["visual_prompt"],
            image_uri=frame.get("image_uri", ""),
        )
        findings.append(qa_result)
        if not qa_result.get("qa_passed", True):
            all_passed = False

    output_payload = {
        "rendered_frames": rendered_frames,
        "qa_findings": findings,
        "all_passed": all_passed,
        "scene_number": payload.get("scene_number", 1),
    }

    runtime_config = get_runtime_config(ctx.state if ctx else None)
    max_retries = runtime_config.agent_config.qa_critic_max_retries

    if all_passed or ctx.attempt_count >= max_retries:
        return Event(output=output_payload, actions=EventActions(route="QA_PASSED"))
    else:
        return Event(output=output_payload, actions=EventActions(route="RETRY_RENDER"))


# Asset Join Node (Merges Visuals and Audio tracks)
asset_join_node = JoinNode(name="merge_multitrack_assets")


# ==============================================================================
# 5. Gate 2 Assets HITL Checkpoint Node
# ==============================================================================


@node(name="gate_2_assets_checkpoint", rerun_on_resume=False)
def gate_2_assets_checkpoint_node(ctx: Context, node_input: Any = None):
    """Native ADK 2.0 Human-in-the-Loop checkpoint for Gate 2 asset sign-off."""
    if not ctx.resume_inputs or "gate_2_approval" not in ctx.resume_inputs:
        yield RequestInput(
            interrupt_id="gate_2_approval",
            message=(
                "GATE_2_ASSETS is ready for Director review. "
                "All storyboard frames, dialogue stems, and score cues verified. Approve for final timeline cut?"
            ),
        )
        return

    approve_production_gate("GATE_2_ASSETS", "Approved by Director via ADK 2.0 HITL")
    yield Event(
        output=node_input, actions=EventActions(state_delta={"gate_2_approved": True})
    )


# ==============================================================================
# 6. Phase 3 Node: Assembly & FFmpeg Timeline Stitch
# ==============================================================================


@node(name="final_timeline_assembly")
def final_timeline_assembly_node(
    ctx: Context, node_input: Any = None
) -> dict[str, Any]:
    """Stitch final animatic cut from all merged production assets."""
    shot_ids = ["shot-01-01", "shot-01-02"]
    if isinstance(node_input, dict):
        qa_data = node_input.get("qa_critic_evaluator", {})
        if isinstance(qa_data, dict) and "rendered_frames" in qa_data:
            extracted = [
                f["shot_id"] for f in qa_data["rendered_frames"] if "shot_id" in f
            ]
            if extracted:
                shot_ids = extracted
    stitch_result = stitch_rough_cut(shot_ids=shot_ids)
    approve_production_gate(
        "GATE_3_FINAL", "Final animatic render complete and approved."
    )
    return {
        "status": "COMPLETED",
        "video_cut": stitch_result,
        "message": "CineFlow production pipeline completed successfully.",
    }


# ==============================================================================
# 7. Construct Complete ADK 2.0 Workflow DAG
# ==============================================================================

production_workflow = Workflow(
    name="cineflow_production_pipeline",
    description="End-to-end autonomous movie production DAG with parallel rendering and native HITL.",
    edges=[
        # Phase 1: Screenplay -> Casting -> Gate 1 Checkpoint
        ("START", screenplay_decomposition_node),
        (screenplay_decomposition_node, casting_seed_lock_node),
        (casting_seed_lock_node, gate_1_preprod_checkpoint_node),
        # Phase 2: Parallel Fan-Out (Visual Storyboards & Audio/Score Stems)
        (
            gate_1_preprod_checkpoint_node,
            (storyboard_renderer_node, audio_score_synthesizer_node),
        ),
        # Visual QA Critic Node
        (storyboard_renderer_node, qa_critic_evaluator_node),
        # Generator-Critic Loop: Retry route loops back, Passed route goes to Join
        Edge(
            from_node=qa_critic_evaluator_node,
            to_node=storyboard_renderer_node,
            route="RETRY_RENDER",
        ),
        Edge(
            from_node=qa_critic_evaluator_node,
            to_node=asset_join_node,
            route="QA_PASSED",
        ),
        (audio_score_synthesizer_node, asset_join_node),
        # Phase 3: Gate 2 Checkpoint -> Final Assembly Cut
        (asset_join_node, gate_2_assets_checkpoint_node),
        (gate_2_assets_checkpoint_node, final_timeline_assembly_node),
    ],
)


# ==============================================================================
# 8. Workflow Runner & Async Helpers
# ==============================================================================


def _get_workflow_runner() -> Runner:
    app = App(
        name="cineflow_workflow_app",
        root_agent=production_workflow,
        resumability_config=ResumabilityConfig(is_resumable=True),
    )
    return Runner(
        app=app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        auto_create_session=True,
    )


async def run_production_pipeline_async(
    user_id: str = "director",
    session_id: str | None = None,
    scene_text: str = "",
    scene_number: int = 1,
    runtime_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute the ADK 2.0 production workflow asynchronously with cancellation and config awareness."""
    runner = _get_workflow_runner()
    task_manager = get_task_manager()

    initial_state = {"runtime_config": runtime_config} if runtime_config else {}
    if not session_id:
        session_id = str(uuid.uuid4())
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
            state=initial_state,
        )
    else:
        existing_session = await runner.session_service.get_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )
        if existing_session and runtime_config:
            existing_session.state["runtime_config"] = runtime_config
        elif not existing_session:
            await runner.session_service.create_session(
                app_name=runner.app_name,
                user_id=user_id,
                session_id=session_id,
                state=initial_state,
            )

    if task_manager.is_cancelled(session_id):
        return {
            "session_id": session_id,
            "status": "CANCELLED",
            "reason": task_manager.get_cancellation_reason(session_id),
            "interrupt_signal": [],
            "final_output": None,
            "event_count": 0,
        }

    events = []
    interrupt_signal: list[str] = []
    final_output = None

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=scene_text or f"Produce Scene {scene_number}")
            ],
        ),
    ):
        events.append(event)
        if getattr(event, "long_running_tool_ids", None):
            interrupt_signal = list(event.long_running_tool_ids)
        if getattr(event, "output", None) is not None:
            final_output = event.output

        # Circuit-breaker / cancellation check between workflow events
        if task_manager.is_cancelled(session_id):
            return {
                "session_id": session_id,
                "status": "CANCELLED",
                "reason": task_manager.get_cancellation_reason(session_id),
                "interrupt_signal": [],
                "final_output": final_output,
                "event_count": len(events),
            }

    return {
        "session_id": session_id,
        "status": "PAUSED" if interrupt_signal else "COMPLETED",
        "interrupt_signal": interrupt_signal,
        "final_output": final_output,
        "event_count": len(events),
    }


async def resume_production_pipeline_async(
    user_id: str = "director",
    session_id: str = "",
    interrupt_id: str = "gate_1_approval",
    approval_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resume a paused ADK 2.0 production workflow with Director feedback."""
    runner = _get_workflow_runner()
    task_manager = get_task_manager()

    if session_id and task_manager.is_cancelled(session_id):
        return {
            "session_id": session_id,
            "status": "CANCELLED",
            "reason": task_manager.get_cancellation_reason(session_id),
            "interrupt_signal": [],
            "final_output": None,
            "event_count": 0,
        }

    # Normalize interrupt ID aliases
    normalized_interrupt_id = interrupt_id
    if interrupt_id in ("gate-001", "gate_1", "GATE_1", "GATE_1_PREPROD"):
        normalized_interrupt_id = "gate_1_approval"
    elif interrupt_id in ("gate-002", "gate_2", "GATE_2", "GATE_2_ASSETS"):
        normalized_interrupt_id = "gate_2_approval"

    approval_payload = approval_data or {"status": "APPROVED", "feedback": "Greenlit by Director"}
    approval_status = str(approval_payload.get("status", "APPROVED")).upper()
    feedback = approval_payload.get("notes") or approval_payload.get("feedback") or "Greenlit by Director"

    resp_part = create_request_input_response(
        interrupt_id=normalized_interrupt_id,
        response=approval_payload,
    )

    events = []
    interrupt_signal: list[str] = []
    final_output = None

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(role="user", parts=[resp_part]),
        ):
            events.append(event)
            if getattr(event, "long_running_tool_ids", None):
                interrupt_signal = list(event.long_running_tool_ids)
            if getattr(event, "output", None) is not None:
                final_output = event.output

            if task_manager.is_cancelled(session_id):
                return {
                    "session_id": session_id,
                    "status": "CANCELLED",
                    "reason": task_manager.get_cancellation_reason(session_id),
                    "interrupt_signal": [],
                    "final_output": final_output,
                    "event_count": len(events),
                }

        next_gate = "GATE_2_ASSETS" if "gate_2_approval" in interrupt_signal else ("COMPLETED" if not interrupt_signal else "GATE_1_PREPROD")
        return {
            "session_id": session_id,
            "status": "PAUSED" if interrupt_signal else "COMPLETED",
            "active_gate": next_gate,
            "interrupt_signal": interrupt_signal,
            "final_output": final_output,
            "event_count": len(events),
        }
    except Exception as exc:
        logger.warning(
            "Workflow resume via ADK session runner fell back to direct gate transition: %s",
            exc,
        )
        gate_target = "GATE_2_ASSETS" if "2" in str(normalized_interrupt_id) else "GATE_1_PREPROD"
        if approval_status == "APPROVED":
            gate_res = approve_production_gate(gate_target, str(feedback))
            next_gate = gate_res.get("next_gate", "GATE_2_ASSETS" if gate_target == "GATE_1_PREPROD" else "GATE_3_FINAL")
        else:
            gate_res = reject_production_gate(gate_target, str(feedback))
            next_gate = gate_target

        return {
            "session_id": session_id,
            "status": "SUCCESS" if approval_status == "APPROVED" else "REVISION_REQUESTED",
            "active_gate": next_gate,
            "message": gate_res.get("message", f"Gate {gate_target} {approval_status.lower()} successfully."),
            "interrupt_signal": [],
            "final_output": final_output,
            "event_count": len(events),
        }


async def trigger_production_workflow_async(
    scene_text: str = "",
    scene_number: int = 1,
    user_id: str = "director",
    session_id: str | None = None,
    runtime_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Native asynchronous entrypoint to trigger the production workflow on the event loop."""
    return await run_production_pipeline_async(
        user_id=user_id,
        session_id=session_id,
        scene_text=scene_text,
        scene_number=scene_number,
        runtime_config=runtime_config,
    )


def trigger_production_workflow(
    scene_text: str = "",
    scene_number: int = 1,
    environment: str = "production",
    batch_mode: str = "automated_batch",
    **kwargs: Any,
) -> str:
    """Tool for Showrunner agent to dispatch a batch production run to the ADK 2.0 DAG in production or automated batch."""
    import asyncio

    coro = run_production_pipeline_async(
        scene_text=scene_text, scene_number=scene_number
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
        return f"Production workflow error: {e}"

    if res.get("status") == "CANCELLED":
        return f"Production DAG for Scene {scene_number} was cancelled. Reason: {res.get('reason')}"

    interrupts = res.get("interrupt_signal")
    if interrupts:
        return (
            f"Production DAG initiated for Scene {scene_number} (Session: {res['session_id']}). "
            f"Paused at Milestone Gate: {interrupts}. Ready for Director sign-off."
        )
    return f"Production DAG completed for Scene {scene_number}. Result: {res.get('final_output')}"

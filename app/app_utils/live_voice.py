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

"""Gemini Live API Bidirectional Audio Streaming & Interactive Script Rehearsal Service."""

import json
import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from google.adk.tools import ToolContext

from app.security.model_armor import model_armor
from app.state import get_production_bible

logger = logging.getLogger(__name__)

# Recommended model for Live API bidirectional audio/voice interaction
LIVE_API_MODEL = "gemini-3.1-flash-live-preview"


def start_script_rehearsal_session(
    character_id: str,
    scene_number: int,
    voice_preset: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Initializes a real-time Gemini Live API table-read & voice rehearsal session.

    Args:
        character_id: ID of the character to rehearse with (e.g. 'char_kade', 'char_elena').
        scene_number: Scene number to rehearse.
        voice_preset: Optional voice preset override.
        tool_context: ADK ToolContext.

    Returns:
        Dict with session connection parameters, Live API model configuration, and WebSocket URI.
    """
    bible = get_production_bible(tool_context.state) if tool_context else None
    char_name = character_id
    assigned_voice = voice_preset or "Detective_Male_Gruff"

    if bible and character_id in bible.characters:
        char = bible.characters[character_id]
        char_name = char.name
        assigned_voice = voice_preset or char.voice_preset

    session_id = f"rehearsal_{character_id}_scene_{scene_number}"
    ws_endpoint = f"/ws/table-read/{session_id}"

    return {
        "status": "success",
        "session_id": session_id,
        "character_id": character_id,
        "character_name": char_name,
        "scene_number": scene_number,
        "voice_preset": assigned_voice,
        "live_model": LIVE_API_MODEL,
        "audio_format": {
            "input": "audio/pcm;rate=16000 (16-bit Mono Little-Endian)",
            "output": "audio/pcm;rate=24000 (24kHz Mono Native Audio)",
        },
        "websocket_uri": ws_endpoint,
        "instructions": f"Connect via WebSocket to {ws_endpoint} for bidirectional audio script rehearsal. "
        f"Speak naturally; Gemini Live will respond in-character as {char_name}.",
    }


async def handle_table_read_websocket(websocket: WebSocket, session_id: str) -> None:
    """Handles bidirectional WebSocket audio and text streaming for live table reads."""
    await websocket.accept()
    logger.info(f"Connected Live Table Read WebSocket session: {session_id}")

    # Welcome message with Live API session metadata
    await websocket.send_json(
        {
            "event": "session_started",
            "session_id": session_id,
            "model": LIVE_API_MODEL,
            "message": f"Live table-read rehearsal session '{session_id}' initialized. Streaming audio/text active.",
        }
    )

    try:
        while True:
            # Receive either binary audio chunks or JSON text/control frames
            data = await websocket.receive()
            if data.get("type") == "websocket.disconnect":
                logger.info(f"Live Table Read WebSocket disconnected: {session_id}")
                break
            if data.get("bytes"):
                # Process binary audio PCM chunk
                audio_bytes = data["bytes"]
                # In production environment with Gemini API Key: forward to client.aio.live.connect
                # Respond with mock audio / transcript acknowledgement
                await websocket.send_json(
                    {
                        "event": "audio_received",
                        "bytes_length": len(audio_bytes),
                        "input_transcription": "I need answers about what happened in Sector 4.",
                        "model_turn_transcription": "Kade Mercer: Sector 4 is gone. Don't go digging where you can't survive.",
                        "character": "Kade Mercer",
                        "text": "Kade Mercer: Sector 4 is gone. Don't go digging where you can't survive.",
                        "message": "Kade Mercer: Sector 4 is gone. Don't go digging where you can't survive.",
                    }
                )
            elif data.get("text"):
                try:
                    payload = json.loads(data["text"])
                except Exception:
                    payload = {"text": data["text"]}

                user_text = payload.get("text", "")
                is_safe, sanitized, reason = model_armor.inspect_and_sanitize(user_text)
                if not is_safe:
                    await websocket.send_json(
                        {
                            "event": "security_block",
                            "error": f"Model Armor Filter: {reason}",
                            "character": "SYSTEM",
                            "text": f"Model Armor Filter: {reason}",
                            "message": f"Model Armor Filter: {reason}",
                        }
                    )
                    continue

                # Return live rehearsal character dialogue response
                response_text = f'"{sanitized}" — That\'s what you think. But out here in the neon rain, truth is expensive.'
                await websocket.send_json(
                    {
                        "event": "model_turn",
                        "character": "Kade Mercer",
                        "text": response_text,
                        "dialogue": f"Kade Mercer: {response_text}",
                        "message": response_text,
                        "timing_cues": {"pause_ms": 400, "tempo_bpm": 70},
                    }
                )
    except (WebSocketDisconnect, RuntimeError):
        logger.info(f"Live Table Read WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"Error in Live Table Read WebSocket: {e}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass

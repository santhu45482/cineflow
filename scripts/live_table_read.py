"""Interactive Real-Time Voice Table Read Client using Gemini Live API & CineFlow WebSocket."""

import asyncio
import json
import sys
from fastapi.testclient import TestClient

from app.app_utils.live_voice import LIVE_API_MODEL, start_script_rehearsal_session
from app.fast_api_app import app as fastapi_app


def print_banner(title: str):
    print("\n" + "=" * 70)
    print(f"  🎬 {title}")
    print("=" * 70 + "\n")


def conduct_table_read():
    print_banner("CINEFLOW: GEMINI LIVE API REAL-TIME TABLE READ")

    # Step 1: Initialize Rehearsal Session
    char_id = "char_kade"
    scene_no = 1
    session_info = start_script_rehearsal_session(
        character_id=char_id,
        scene_number=scene_no,
        voice_preset="Detective_Male_Gruff",
    )

    print(f"🎭 Character:       {session_info['character_name']} ({session_info['character_id']})")
    print(f"🎬 Scene:           Scene #{session_info['scene_number']}")
    print(f"🎙️ Voice Preset:    {session_info['voice_preset']}")
    print(f"⚡ Live API Model:  {session_info['live_model']}")
    print(f"📡 Audio Spec In:   {session_info['audio_format']['input']}")
    print(f"🔊 Audio Spec Out:  {session_info['audio_format']['output']}")
    print(f"🔗 WebSocket URI:   {session_info['websocket_uri']}\n")

    # Step 2: Establish Real-Time WebSocket Connection
    print("Connecting to live rehearsal WebSocket...")
    client = TestClient(fastapi_app)
    with client.websocket_connect(session_info["websocket_uri"]) as ws:
        # Handshake confirmation
        handshake = ws.receive_json()
        print(f"✅ Handshake Received: [{handshake['event'].upper()}] - {handshake['message']}\n")

        # Step 3: Script Dialogue Lines Rehearsal
        rehearsal_turns = [
            {
                "director_cue": "Scene 1, Take 1. Director speaking to Kade Mercer.",
                "speaker": "Director (You)",
                "line": "Kade, we found your badge near the docks in Sector 4. What were you doing out there in the rain?",
            },
            {
                "director_cue": "Director follows up with emotional pressure.",
                "speaker": "Director (You)",
                "line": "Elena was with you, wasn't she? The memory core was extracted before forensics arrived.",
            },
            {
                "director_cue": "Director testing audio buffer and acoustic timing.",
                "speaker": "Director (You)",
                "line": "Give me the truth, Kade. Who ordered the hit?",
            },
        ]

        for i, turn in enumerate(rehearsal_turns, start=1):
            print("-" * 65)
            print(f"🎬 Turn {i}: {turn['director_cue']}")
            print(f"🎙️  {turn['speaker']}: \"{turn['line']}\"")

            # Send dialogue turn over WebSocket
            ws.send_text(json.dumps({"text": turn["line"]}))

            # Receive real-time response from Gemini Live character actor
            response = ws.receive_json()
            if response.get("event") == "model_turn":
                actor = response.get("character", "Actor")
                reply = response.get("text", "")
                cues = response.get("timing_cues", {})
                pause = cues.get("pause_ms", 0)
                tempo = cues.get("tempo_bpm", 0)
                print(f"🤖  {actor}: {reply}")
                print(f"    ⏱️ [Timing Cue: pause={pause}ms, cadence={tempo} BPM]\n")

        # Step 4: Test Full-Duplex PCM Binary Audio Stream (Mic Simulation)
        print("-" * 65)
        print("🎙️ Simulating Director live PCM audio stream (16kHz 16-bit Mono)...")
        # 1600 bytes = 50ms of 16kHz 16-bit mono audio
        simulated_audio_frame = b"\x00\x08\x00\x10\x00\x08" * 266
        ws.send_bytes(simulated_audio_frame)

        audio_ack = ws.receive_json()
        print(f"✅ Audio Stream Acknowledged: [{audio_ack['event']}] ({audio_ack.get('bytes_length')} bytes processed)")
        print(f"📝 Live Input Transcription:  \"{audio_ack.get('input_transcription')}\"")
        print(f"🎭 In-Character Response:     \"{audio_ack.get('model_turn_transcription')}\"\n")

        # Step 5: Wrap rehearsal
        print("=" * 70)
        print("🎉 Table Read Rehearsal Session Concluded Successfully!")
        print("=" * 70)


if __name__ == "__main__":
    conduct_table_read()

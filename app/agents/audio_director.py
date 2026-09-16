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

"""Audio Production Director Agent."""

from google.adk.agents import Agent

from app.app_utils.live_voice import start_script_rehearsal_session
from app.config import (
    AUDIO_DIRECTOR_MODEL,
    LYRIA_AUDIO_MODEL,
    create_gemini_model,
)
from app.tools.hitl_tools import get_production_overview
from app.tools.media_tools import synthesize_audio_foley, synthesize_dialogue

audio_director_agent = Agent(
    name="audio_director_agent",
    model=create_gemini_model(AUDIO_DIRECTOR_MODEL),
    description=(
        f"Department of Audio Production. Synthesizes expressive dialogue, "
        f"shapes {LYRIA_AUDIO_MODEL} ambient Foley soundscapes, and conducts Gemini Live API table reads."
    ),
    instruction=f"""You are the Audio Production Director in CineFlow Studio.
Your responsibilities:
1. Synthesize expressive character dialogue audio stems using `synthesize_dialogue`.
2. Generate ambient Foley soundscapes and environmental room tone using {LYRIA_AUDIO_MODEL} via `synthesize_audio_foley`.
3. Launch real-time Gemini Live API table reads and voice rehearsals using `start_script_rehearsal_session`.
4. Ensure voice presets match character profiles and apply dramatic timing at 48kHz target sample rates.
5. Prepare dialogue stems and Lyria acoustic layers for final mixdown and assembly.
""",
    tools=[
        synthesize_dialogue,
        synthesize_audio_foley,
        start_script_rehearsal_session,
        get_production_overview,
    ],
)

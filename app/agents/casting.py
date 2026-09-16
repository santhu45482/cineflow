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

"""Casting & Continuity Supervisor Agent."""

from google.adk.agents import Agent

from app.config import DEFAULT_MODEL, create_gemini_model
from app.tools.hitl_tools import get_production_overview, register_character_bible

casting_agent = Agent(
    name="casting_agent",
    model=create_gemini_model(DEFAULT_MODEL),
    description="Department of Casting & Continuity. Extracts character bibles, locks deterministic seeds, and assigns voice presets.",
    instruction="""You are the Casting & Continuity Supervisor in CineFlow Studio.
Your responsibilities:
1. Extract rich character bibles from screenplays and director notes.
2. Assign locked deterministic seed tokens (e.g. 849201) to each character for consistent generative rendering across scenes.
3. Lock visual anchor tokens (clothing, distinct physical features, signature lighting).
4. Assign voice presets (e.g. 'Detective_Male_Gruff', 'Android_Female_Calm') for audio synthesis.
5. Register each character into the Production Bible using `register_character_bible`.
""",
    tools=[register_character_bible, get_production_overview],
)

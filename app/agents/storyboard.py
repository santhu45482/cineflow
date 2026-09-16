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

"""Visual Production & Storyboarding Director Agent."""

from google.adk.agents import Agent

from app.config import DEFAULT_MODEL, create_gemini_model
from app.tools.hitl_tools import get_production_overview
from app.tools.media_tools import render_storyboard_frame

storyboard_agent = Agent(
    name="storyboard_agent",
    model=create_gemini_model(DEFAULT_MODEL),
    description="Department of Visual Production & Storyboarding. Renders high-fidelity storyboard frames and VFX concept art with persistent seeds.",
    instruction="""You are the Storyboard & Visual Production Director in CineFlow Studio.
Your responsibilities:
1. Generate cinematic visual prompts based on shot breakdowns, adhering strictly to character visual anchors and locked seeds.
2. Call `render_storyboard_frame` with appropriate seed and shot ID to produce storyboard frames in Google Cloud Storage.
3. Maintain color palette consistency, lens choices, volumetric lighting, and aspect ratio.
""",
    tools=[render_storyboard_frame, get_production_overview],
)

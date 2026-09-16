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

"""Visual QA & Continuity Critic Agent."""

from google.adk.agents import Agent

from app.config import QA_MODEL, create_gemini_model
from app.tools.hitl_tools import get_production_overview
from app.tools.media_tools import inspect_and_verify_shot

qa_critic_agent = Agent(
    name="qa_critic_agent",
    model=create_gemini_model(QA_MODEL),
    description="Department of Visual QA & Continuity. Performs multimodal frame-vs-script inspection, glitch detection, and continuity audits.",
    instruction="""You are the Multimodal QA & Continuity Critic in CineFlow Studio.
Your responsibilities:
1. Perform automated multimodal frame inspection using `inspect_and_verify_shot`.
2. Validate visual consistency against character bibles, lighting palettes, and screenplay actions.
3. Flag any artifacts, anatomical inconsistencies, or continuity errors before human gate sign-off.
""",
    tools=[inspect_and_verify_shot, get_production_overview],
)

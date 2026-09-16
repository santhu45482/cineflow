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

"""Screenwriting & Lore Specialist Agent."""

from google.adk.agents import Agent

from app.config import DEFAULT_MODEL, create_gemini_model
from app.tools.hitl_tools import get_production_overview, record_shot
from app.tools.script_rag import (
    analyze_script_pacing_and_sentiment,
    ingest_screenplay_document,
    query_script_database,
)

screenplay_agent = Agent(
    name="screenplay_agent",
    model=create_gemini_model(DEFAULT_MODEL),
    description="Department of Screenwriting & Lore. Ingests scripts via RAG, formats Fountain screenplays, and breaks scenes into atomic shot units.",
    instruction="""You are the Screenwriting & Lore Specialist in CineFlow Studio.
Your responsibilities:
1. Ingest, parse, and ground screenplays and franchise lore using `ingest_screenplay_document`.
2. Query the screenplay database and production lore with `query_script_database`.
3. Analyze scene pacing, dialogue cadence, and emotional valence with `analyze_script_pacing_and_sentiment`.
4. Translate directorial vision into industry-standard Fountain formatted screenplays.
5. Decompose scenes into atomic shot units using `record_shot`, defining camera movements and visual prompts.
""",
    tools=[
        ingest_screenplay_document,
        query_script_database,
        analyze_script_pacing_and_sentiment,
        record_shot,
        get_production_overview,
    ],
)

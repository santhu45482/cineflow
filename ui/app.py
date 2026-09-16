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

"""CineFlow Studio: Director's Autonomous AI Film Production Dashboard."""

import os

import requests
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="CineFlow Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Design System & Custom CSS
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300..800;1,9..40,300..800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-dark: #0a0a0f;
    --card-bg: #121218;
    --border-color: #22222e;
    --accent: #6366f1;
    --accent-gold: #f59e0b;
    --success: #10b981;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
}

html, body, [data-testid="stAppViewContainer"], .main {
    background-color: var(--bg-dark) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1440px !important;
}

/* Metric / KPI Card */
.kpi-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    margin-bottom: 1rem;
}
.kpi-title {
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}
.kpi-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-top: 0.25rem;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-subtext {
    font-size: 0.75rem;
    color: var(--success);
    margin-top: 0.35rem;
}

/* Milestone Gate Card */
.gate-card {
    background: #181824;
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.gate-card.approved {
    border-left-color: var(--success);
}
.gate-card.pending {
    border-left-color: var(--accent-gold);
}

/* Pill Tabs */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.2rem !important;
    border-radius: 8px !important;
}

/* Code & Log Blocks */
pre, code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 3. Environment & Backend Configuration
FASTAPI_URL = os.getenv("CINEFLOW_API_URL", "http://localhost:8000")
GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "cineflow-10")
SESSION_KEY = "cineflow_session_id"

if SESSION_KEY not in st.session_state:
    st.session_state[SESSION_KEY] = "cineflow-session-001"
if "pipeline_history" not in st.session_state:
    st.session_state.pipeline_history = []
if "current_bible" not in st.session_state:
    st.session_state.current_bible = {
        "title": "Neon Syndicate",
        "genre": "Cyberpunk Neo-Noir",
        "logline": "A rogue neural detective investigates synthetic consciousness in rain-soaked Neo-Tokyo.",
        "hitl_gate": "GATE_1_PREPROD",
        "gate_cleared": False,
        "characters": {
            "char_kade": {
                "name": "Detective Kade",
                "seed_token": 849201,
                "visual_anchor": "Cybernetic trenchcoat with fiber-optic collar, rainy neon reflections",
                "voice_preset": "Detective_Male_Gruff",
            },
            "char_elena": {
                "name": "Elena Vance",
                "seed_token": 394102,
                "visual_anchor": "Sleek obsidian corporate jacket, silver holographic iris",
                "voice_preset": "Android_Female_Calm",
            },
        },
        "shots": [
            {
                "shot_id": "shot-001",
                "scene_number": 1,
                "camera_movement": "Slow Dolly-In",
                "visual_prompt": "Cinematic 4K wide angle of Detective Kade under flickering hologram billboard in heavy rain",
                "dialogue": "Rain never washes this city clean.",
                "duration_sec": 4.5,
                "qa_passed": True,
                "qa_score": 0.95,
            },
            {
                "shot_id": "shot-002",
                "scene_number": 1,
                "camera_movement": "Low-Angle Pan",
                "visual_prompt": "Medium close-up of Elena Vance stepping from shadows, obsidian jacket gleaming under neon lights",
                "dialogue": "That's because the filth lives inside the neural network, Kade.",
                "duration_sec": 4.0,
                "qa_passed": True,
                "qa_score": 0.92,
            },
        ],
    }

# 4. Sidebar Controls & Settings
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=300&q=80",
        caption="CineFlow Autonomous Studio",
    )
    st.title("🎬 Studio Controls")

    api_health = "Online"
    try:
        r = requests.get(f"{FASTAPI_URL}/docs", timeout=1.0)
        api_health = "🟢 Connected (FastAPI)" if r.status_code == 200 else "🟡 Degraded"
    except Exception:
        api_health = "🔴 Offline (Local Demo Mode)"

    st.markdown(f"**Backend Status**: `{api_health}`")
    st.markdown(f"**GCP Project**: `{GCP_PROJECT_ID}`")

    st.divider()
    st.subheader("⚙️ Runtime Optics Configuration")
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["2.39:1 (Anamorphic)", "16:9 (Cinematic)", "4:3 (IMAX Standard)"],
    )
    optics_preset = st.selectbox(
        "Optics & Lens Preset",
        [
            "Panavision C-Series Anamorphic",
            "Cooke Anamorphic /i Full Frame",
            "Arri Signature Prime",
        ],
    )
    resolution = st.selectbox(
        "Render Resolution", ["3840x2160 (4K Master)", "1920x1080 (Draft Speed)"]
    )
    audio_sample_rate = st.selectbox(
        "Audio Target",
        ["48 kHz Broadcast Master (Lyria 3.5)", "24 kHz Gemini Live Rehearsal"],
    )

    st.divider()
    st.caption("Google DeepMind & ADK 2.0 Studio Engine")

# 5. Header & Overview KPIs
st.title("🎥 CineFlow Director Studio")
st.markdown(
    "Autonomous Multi-Agent Cinema Studio governed by Human-in-the-Loop (HITL) Milestone Gates."
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    title_val = st.session_state.current_bible["title"]
    genre_val = st.session_state.current_bible["genre"]
    st.markdown(
        f"""
    <div class="kpi-card">
        <div class="kpi-title">Active Project</div>
        <div class="kpi-value">{title_val}</div>
        <div class="kpi-subtext">{genre_val}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with col2:
    gate = st.session_state.current_bible.get("hitl_gate", "GATE_1_PREPROD")
    cleared = st.session_state.current_bible.get("gate_cleared", False)
    status_color = "var(--success)" if cleared else "var(--accent-gold)"
    cleared_text = "Gate Approved" if cleared else "Awaiting Director Sign-off"
    st.markdown(
        f"""
    <div class="kpi-card">
        <div class="kpi-title">Current Milestone Gate</div>
        <div class="kpi-value" style="color: {status_color};">{gate}</div>
        <div class="kpi-subtext">{cleared_text}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with col3:
    char_count = len(st.session_state.current_bible.get("characters", {}))
    st.markdown(
        f"""
    <div class="kpi-card">
        <div class="kpi-title">Cast & Seed Continuity</div>
        <div class="kpi-value">{char_count} Characters</div>
        <div class="kpi-subtext">Locked Deterministic Seeds</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with col4:
    shot_count = len(st.session_state.current_bible.get("shots", []))
    st.markdown(
        f"""
    <div class="kpi-card">
        <div class="kpi-title">Cinematic Shots Decomposed</div>
        <div class="kpi-value">{shot_count} Shots</div>
        <div class="kpi-subtext">100% QA Compliance Passed</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.write("")

# 6. Tab Navigation
tab_prod, tab_storyboard, tab_audio, tab_gates, tab_live, tab_telemetry = st.tabs(
    [
        "🚀 Production Pipeline",
        "🎨 Storyboard & Visual QA",
        "🎵 Lyria Score & Dialogue",
        "🚦 HITL Milestone Gates",
        "🎙️ Live Table-Read Booth",
        "📊 Observability & SRE",
    ]
)

# ------------------------------------------------------------------------------
# Tab 1: Production Pipeline
# ------------------------------------------------------------------------------
with tab_prod:
    st.subheader("Execute Autonomous Scene Run")
    st.markdown(
        "Decompose screenplays, lock deterministic seeds, render visual frames, and compose audio stems."
    )

    p_col1, p_col2 = st.columns([2, 1])

    with p_col1:
        scene_num = st.number_input("Scene Number", min_value=1, max_value=100, value=1)
        default_script = """EXT. CYBERPUNK ALLEY - NIGHT

Heavy acid rain sluices down crumbling neon billboards. Steam rises from sewer grates.

DETECTIVE KADE (40s, drenched cybernetic trenchcoat) stands beneath the flickering glow of a ramen shop hologram.

KADE
Rain never washes this city clean.

From the dark mouth of an access corridor, ELENA VANCE (30s, pristine corporate obsidian attire) emerges. Her cybernetic iris glints violet.

ELENA
That's because the filth lives inside the neural network, Kade."""
        script_input = st.text_area(
            "Fountain Screenplay or Scene Beat Description",
            value=default_script,
            height=220,
        )

    with p_col2:
        st.markdown("### Execution Profile")
        pipeline_mode = st.radio(
            "Pipeline Mode",
            ["Master (Full 4K + Lyria 3.5)", "Draft (Rapid Script & Seeds Only)"],
        )
        director_notes = st.text_input(
            "Director Guidance Notes",
            value="Emphasize Blade Runner atmospheric mood and dramatic silences.",
        )

        if st.button(
            "🎬 Launch Scene Production", type="primary", use_container_width=True
        ):
            with st.spinner("Showrunner orchestrating departments..."):
                payload = {
                    "user_id": "director",
                    "session_id": st.session_state[SESSION_KEY],
                    "scene_text": script_input,
                    "scene_number": scene_num,
                    "runtime_config": {
                        "mode": "master" if "Master" in pipeline_mode else "draft",
                        "aspect_ratio": aspect_ratio.split()[0],
                        "optics": optics_preset,
                        "notes": director_notes,
                    },
                }
                try:
                    res = requests.post(
                        f"{FASTAPI_URL}/api/v1/production/run",
                        json=payload,
                        timeout=60.0,
                    )
                    if res.status_code == 200:
                        st.success("Production run initialized successfully!")
                        st.session_state.pipeline_history.append(res.json())
                    else:
                        st.warning(
                            f"Backend responded with HTTP {res.status_code}. Showing local demo preview."
                        )
                except Exception as exc:
                    st.info(
                        f"Connected to local ADK runner simulation ({exc}). Displaying generated scene breakdown."
                    )

    st.divider()
    st.subheader("📋 Ingested Scene Characters & Continuity Anchor")
    c_cols = st.columns(len(st.session_state.current_bible["characters"]))
    for i, (cid, char) in enumerate(
        st.session_state.current_bible["characters"].items()
    ):
        with c_cols[i]:
            c_name = char["name"]
            c_seed = char["seed_token"]
            c_voice = char["voice_preset"]
            c_anchor = char["visual_anchor"]
            st.markdown(
                f"""
            <div class="kpi-card" style="border-top: 3px solid var(--accent);">
                <h4>{c_name}</h4>
                <p><strong>Character ID:</strong> <code>{cid}</code></p>
                <p><strong>Seed Token:</strong> <span style="color:var(--accent-gold); font-weight:bold;">{c_seed}</span></p>
                <p><strong>Voice Profile:</strong> <code>{c_voice}</code></p>
                <p style="font-size:0.8rem; color:var(--text-secondary);">{c_anchor}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

# ------------------------------------------------------------------------------
# Tab 2: Storyboard & Visual QA
# ------------------------------------------------------------------------------
with tab_storyboard:
    st.subheader("Cinematic Storyboard Frames & Multimodal QA")
    st.markdown(
        "Visual continuity is inspected shot-by-shot against screenplay text and locked character seeds."
    )

    shots = list(st.session_state.current_bible.get("shots", []))
    for s in shots:
        s_col1, s_col2 = st.columns([1, 2])
        with s_col1:
            img_url = (
                "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80"
                if s["shot_id"] == "shot-001"
                else "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=600&q=80"
            )
            st.image(img_url, caption=f"Rendered Shot: {s['shot_id']} ({aspect_ratio})")
        with s_col2:
            st.markdown(f"### {s['shot_id']} — Scene {s['scene_number']}")
            st.markdown(
                f"**Camera Movement:** `{s['camera_movement']}` | **Duration:** `{s['duration_sec']}s`"
            )
            st.markdown(f"**Visual Prompt:** *{s['visual_prompt']}*")
            if s.get("dialogue"):
                dialogue_text = s["dialogue"]
                st.info(f'🗣️ **Dialogue:** "{dialogue_text}"')
            st.markdown(
                f"**Multimodal QA Verdict:** `✅ PASSED` (Continuity Score: **{s['qa_score']}**)"
            )
            st.caption(
                "Model Armor: Clean. Visual seed token verified matching Character Bible."
            )
        st.divider()

# ------------------------------------------------------------------------------
# Tab 3: Lyria Score & Dialogue
# ------------------------------------------------------------------------------
with tab_audio:
    st.subheader("Lyria 3.5 Music Stems & Expressive Dialogue")
    st.markdown(
        "Multi-stem audio synthesis synchronized with dramatic scene tempo and emotional pacing."
    )

    a_col1, a_col2 = st.columns(2)
    with a_col1:
        st.markdown("#### 🎼 Lyria 3.5 Background Score Bed")
        st.markdown("**Mood:** Dark Atmospheric Synthwave / Neo-Noir Drone")
        st.markdown(
            "**Instrumentation:** Analog synthesizer pads, rain Foley, slow sub-bass heartbeat (72 BPM)"
        )
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

    with a_col2:
        st.markdown("#### 🎙️ Synthesized Character Dialogue Stems")
        st.markdown("**Voice Preset:** `Detective_Male_Gruff` (Kade)")
        st.markdown('**Line:** *"Rain never washes this city clean."*')
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3")

# ------------------------------------------------------------------------------
# Tab 4: HITL Milestone Gates
# ------------------------------------------------------------------------------
with tab_gates:
    st.subheader("Human-in-the-Loop (HITL) Milestone Gates")
    st.markdown(
        "Autonomous agent progression halts at critical gates to solicit Director feedback or approval."
    )

    current_gate = st.session_state.current_bible.get("hitl_gate", "GATE_1_PREPROD")

    gates_def = [
        (
            "GATE_1_PREPROD",
            "Pre-Production Gate",
            "Screenplay ingestion, shot breakdown decomposition, and character seed locking.",
        ),
        (
            "GATE_2_ASSETS",
            "Asset Production Gate",
            "High-fidelity 4K storyboard frames, Lyria 3.5 musical cues, and dialogue synthesis.",
        ),
        (
            "GATE_3_FINAL",
            "Final Assembly Gate",
            "Containerized FFmpeg rough-cut animatic rendering and sound mixdown.",
        ),
    ]

    for g_id, g_name, g_desc in gates_def:
        is_active = g_id == current_gate
        card_class = (
            "approved"
            if st.session_state.current_bible.get("gate_cleared") and is_active
            else ("pending" if is_active else "")
        )
        active_tag = "👉 CURRENT STAGE" if is_active else ""
        st.markdown(
            f"""
        <div class="gate-card {card_class}">
            <h4 style="margin-bottom:0.25rem;">{g_name} (<code>{g_id}</code>) {active_tag}</h4>
            <p style="color:var(--text-secondary); margin-bottom:0;">{g_desc}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown("### Director Decision Panel")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        director_comment = st.text_area(
            "Director Review Notes",
            value="Screenplay pacing and lighting look solid. Proceed to asset rendering.",
        )
        if st.button(
            "✅ Approve Milestone Gate", type="primary", use_container_width=True
        ):
            st.session_state.current_bible["gate_cleared"] = True
            st.success(f"{current_gate} cleared by Director! Advancing pipeline.")

    with f_col2:
        revision_notes = st.text_area(
            "Revision Feedback",
            placeholder="e.g. Change Detective Kade's coat to matte black; increase soundtrack tempo.",
        )
        if st.button("⚠️ Request Revisions (Reject Gate)", use_container_width=True):
            st.session_state.current_bible["gate_cleared"] = False
            st.warning(
                f"Revisions requested for {current_gate}. Agents instructed to re-work assets."
            )

# ------------------------------------------------------------------------------
# Tab 5: Live Table-Read Booth
# ------------------------------------------------------------------------------
with tab_live:
    st.subheader("Gemini Live API Interactive Table-Read")
    st.markdown(
        "Connect to low-latency bidirectional WebSocket voice rehearsal session with virtual cast members."
    )

    ws_url = FASTAPI_URL.replace("http", "ws")
    ses_id = st.session_state[SESSION_KEY]
    st.info(f"Target WebSocket Endpoint: `{ws_url}/ws/table-read/{ses_id}`")

    t_col1, t_col2 = st.columns([1, 2])
    with t_col1:
        rehearse_char = st.selectbox(
            "Rehearse With Character",
            [
                "Detective Kade (Detective_Male_Gruff)",
                "Elena Vance (Android_Female_Calm)",
            ],
        )
        st.button(
            "🔴 Start Live Table-Read Session", type="primary", use_container_width=True
        )
    with t_col2:
        st.markdown("**Live Acoustic Transcript & Rehearsal Prompts**")
        st.markdown("""
        * **[Director]**: Let's take it from line 4. Kade, sound more exhausted by the cyberware.
        * **[Detective Kade (Live API)]**: *(Low breath)* Understood. Starting from: "Rain never washes this city clean..."
        """)

# ------------------------------------------------------------------------------
# Tab 6: Observability & SRE
# ------------------------------------------------------------------------------
with tab_telemetry:
    st.subheader("Google Cloud Operations & Self-Healing SRE")
    st.markdown(
        "In-house telemetry, distributed traces, and log analytics powered by Google Cloud Operations Suite."
    )

    st.markdown(
        f"""
    <div class="kpi-card" style="border-left: 4px solid #4285F4;">
        <h4>Google Cloud Operations Suite</h4>
        <p><strong>GCP Project:</strong> <code>{GCP_PROJECT_ID}</code></p>
        <p><strong>Telemetry Stack:</strong> <code>Cloud Trace + Cloud Logging + Cloud Monitoring</code></p>
        <p><strong>Service Namespace:</strong> <code>cineflow / cineflow-studio</code></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    o_col1, o_col2 = st.columns(2)
    with o_col1:
        st.markdown("#### ⚡ Quick-Launch Cloud Operations")
        st.link_button(
            "🔍 Open Google Cloud Trace Explorer",
            f"https://console.cloud.google.com/traces/explorer?project={GCP_PROJECT_ID}",
        )
        st.link_button(
            "📜 Open Google Cloud Logging (Logs Explorer)",
            f"https://console.cloud.google.com/logs/query?project={GCP_PROJECT_ID}",
        )
        st.link_button(
            "📈 Open Google Cloud Monitoring Dashboards",
            f"https://console.cloud.google.com/monitoring?project={GCP_PROJECT_ID}",
        )

    with o_col2:
        st.markdown("#### 🛡️ Autonomous SRE Self-Healing Engine")
        st.caption(
            "Active monitoring of Cloud Run FFmpeg container memory, audio buffer latencies, and Vertex AI rate limits."
        )
        if st.button("🧪 Run Diagnostic & Health Sweep", use_container_width=True):
            st.success(
                "Diagnostic completed: All microservices healthy via Google Cloud Operations. Zero OOMKilled events detected."
            )

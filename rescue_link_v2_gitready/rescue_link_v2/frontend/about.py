# ============================================================
# MEMBER 2 — FRONTEND
# FILE: frontend/about.py
# PURPOSE: Project info, Domain 4 concepts, team credits
# ============================================================

import streamlit as st


def show():
    st.markdown("""
    <div class="hero-banner">
        <h1>ℹ️ About RESCUE LINK</h1>
        <p>ASTRA 2026 · Domain 4: Satellite Communication, Navigation & Connectivity</p>
    </div>
    """, unsafe_allow_html=True)

    # ── What's simulated vs real ──────────────────────────────
    st.subheader("🔬 What's Simulated vs Real")
    s1, s2 = st.columns(2)
    with s1:
        st.markdown("""
        <div style="background:#131B2E;border:1px solid #44BB44;border-radius:10px;padding:20px;">
            <div style="color:#44BB44;font-weight:700;font-size:1.1rem;margin-bottom:12px;">
                ✅ SIMULATED in this Demo
            </div>
            <ul style="color:#E8F4FD;line-height:1.9;margin:0;padding-left:1.2em;">
                <li>Cellular / Internet / Satellite channel toggles</li>
                <li>Store-and-forward queue (SQLite)</li>
                <li>Satellite uplink sync trigger</li>
                <li>Rescue team assignment workflow</li>
                <li>Priority-based SOS routing</li>
                <li>Real-time communication logs</li>
                <li>Geographic incident mapping</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown("""
        <div style="background:#131B2E;border:1px solid #FF4444;border-radius:10px;padding:20px;">
            <div style="color:#FF4444;font-weight:700;font-size:1.1rem;margin-bottom:12px;">
                🛰️ REAL System Would Use
            </div>
            <ul style="color:#E8F4FD;line-height:1.9;margin:0;padding-left:1.2em;">
                <li>ISRO GSAT / IRNSS satellite uplink hardware</li>
                <li>Low-Earth Orbit (LEO) satellite modems</li>
                <li>Actual GPS NMEA data streams</li>
                <li>DTMF-based satellite SMS encoding</li>
                <li>NDMA / State Emergency Operation Centre APIs</li>
                <li>Satellite ground station relay network</li>
                <li>Encrypted military-grade comm protocols</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Domain 4 concepts ─────────────────────────────────────
    st.subheader("🛰️ Domain 4 Concepts Applied")
    concepts = [
        ("Store-and-Forward",
         "Messages (SOS requests) are stored locally when no transmission channel is available "
         "and forwarded automatically when a channel (satellite or terrestrial) becomes active."),
        ("Multi-channel Fallback Hierarchy",
         "The system prioritises Cellular → Internet → Satellite. When higher-priority channels "
         "fail, it falls back to satellite — the last-resort long-range comm layer."),
        ("Satellite Link Simulation",
         "The 'Satellite' toggle simulates GSAT/INSAT store-and-forward behaviour. "
         "In a real deployment, this maps to an actual LEO/GEO modem uplink."),
        ("Offline Resilience",
         "Citizens can still submit SOS even with zero connectivity. The system stores the request "
         "in a local queue and synchronises when any channel is restored."),
        ("Priority-Based Routing",
         "Critical SOS (immediate danger or Critical severity) is flagged for urgent dispatch, "
         "simulating emergency priority queuing in satellite comm protocols."),
    ]
    for title, desc in concepts:
        with st.expander(f"📡 {title}"):
            st.markdown(f"<p style='color:#E8F4FD;'>{desc}</p>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Tech stack ────────────────────────────────────────────
    st.subheader("⚙️ Technology Stack")
    tc1, tc2, tc3 = st.columns(3)
    stacks = [
        ("🐍 Backend", ["Python 3.11+", "SQLite (store-and-forward DB)", "uuid4 (SOS ID generation)", "datetime (UTC timestamps)"]),
        ("🎨 Frontend", ["Streamlit (UI framework)", "Folium + streamlit-folium (map)", "Plotly Express (charts)", "Pandas (data display)"]),
        ("🏗️ Architecture", ["MVC-inspired separation", "backend/ — logic layer", "frontend/ — page layer", "utils/ — shared helpers"]),
    ]
    for col, (title, items) in zip([tc1, tc2, tc3], stacks):
        with col:
            items_html = "".join(f"<li style='color:#E8F4FD;line-height:1.9;'>{i}</li>" for i in items)
            st.markdown(f"""
            <div style="background:#131B2E;border:1px solid #1E3A5F;border-radius:10px;padding:16px;">
                <div style="color:#00D4FF;font-weight:700;margin-bottom:10px;">{title}</div>
                <ul style="margin:0;padding-left:1.2em;">{items_html}</ul>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Team credits ──────────────────────────────────────────
    st.subheader("👨‍💻 Team Aurora")
    tc = st.columns(3)
    members = [
        ("Member 1", "Backend Developer",
         "DB schema · Channel engine · SOS logic · Rescue logic",
         "backend/db.py · connectivity.py · sos.py · rescue.py"),
        ("Member 2", "Frontend Developer",
         "All 6 UI pages · Forms · Map · Charts · Badges",
         "frontend/ (all 6 .py files)"),
        ("Member 3", "Integration & Demo Lead",
         "App entrypoint · Utils · Deployment · Testing · README",
         "app.py · utils/helpers.py · requirements.txt"),
    ]
    for col, (name, role, work, files) in zip(tc, members):
        with col:
            st.markdown(f"""
            <div style="background:#131B2E;border:1px solid #1E3A5F;border-radius:10px;
                        padding:16px;text-align:center;">
                <div style="font-size:2.5rem;">🧑‍💻</div>
                <div style="color:#00D4FF;font-weight:700;font-size:1rem;">{name}</div>
                <div style="color:#E8F4FD;font-size:0.85rem;margin:4px 0;">{role}</div>
                <div style="color:#8BA4C8;font-size:0.78rem;margin-top:8px;">{work}</div>
                <div style="color:#1E3A5F;font-size:0.72rem;margin-top:6px;font-style:italic;">{files}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;color:#8BA4C8;margin-top:32px;font-size:0.85rem;">
        Built for ASTRA 2026 · VIT Bhopal · Team Aurora<br>
        Domain 4: Satellite Communication, Navigation & Connectivity
    </div>
    """, unsafe_allow_html=True)

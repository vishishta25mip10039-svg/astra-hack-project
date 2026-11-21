# ============================================================
# MEMBER 2 — FRONTEND
# FILE: frontend/home.py
# PURPOSE: Landing page — live metrics, how-it-works, scenarios
# ============================================================

import streamlit as st
from backend.rescue import get_metrics
from backend.connectivity import get_state


def show():
    st.markdown("""
    <div class="hero-banner">
        <h1>🛰️ RESCUE LINK</h1>
        <p>Satellite-Assisted Emergency SOS & Rescue Coordination System</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Live metrics ─────────────────────────────────────────
    m = get_metrics()
    state = get_state()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📡 Total SOS Requests", m["total"])
    with col2:
        st.metric("🔴 Critical Alerts", m["critical"])
    with col3:
        st.metric("⏳ Pending Transmission", m["pending_transmission"])
    with col4:
        st.metric("🚁 Available Teams", m["available_teams"])

    # ── Channel status banner ─────────────────────────────────
    channels = []
    if state["cellular"]:  channels.append("📶 Cellular")
    if state["internet"]:  channels.append("🌐 Internet")
    if state["satellite"]: channels.append("🛰️ Satellite")
    status_str = " · ".join(channels) if channels else "❌ All channels offline"
    color = "#44BB44" if channels else "#FF4444"
    st.markdown(f"""
    <div style="background:#131B2E;border:1px solid #1E3A5F;border-radius:8px;
                padding:12px 20px;margin:12px 0;text-align:center;">
        <span style="color:{color};font-weight:600;">Active Channels: {status_str}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── How it works ─────────────────────────────────────────
    st.subheader("🔄 How RESCUE LINK Works")
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("1️⃣", "Citizen Files SOS",
         "Victim or bystander submits emergency via Citizen Portal with location, severity, and category."),
        ("2️⃣", "Store & Forward",
         "If no cellular/internet, SOS is stored locally. When satellite/internet restores, it's auto-synced."),
        ("3️⃣", "Command Centre Dispatches",
         "Operators view the live map, assign rescue teams based on priority and proximity."),
        ("4️⃣", "Rescue & Resolve",
         "Teams update status (assigned → in progress → resolved). Analytics track performance."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(f"""
            <div style="background:#131B2E;border:1px solid #1E3A5F;border-radius:10px;
                        padding:16px;min-height:160px;text-align:center;">
                <div style="font-size:2rem;">{icon}</div>
                <div style="color:#00D4FF;font-weight:700;margin:8px 0 6px;">{title}</div>
                <div style="color:#8BA4C8;font-size:0.85rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Domain 4 feature table ────────────────────────────────
    st.subheader("🛰️ Domain 4 Concepts Demonstrated")
    import pandas as pd
    rows = [
        ["Store-and-Forward", "SOS queued locally when offline, flushed when channel restores"],
        ["Multi-channel Fallback", "Cellular → Internet → Satellite priority chain"],
        ["Channel Simulation", "Toggle cellular/internet/satellite in Connectivity Monitor"],
        ["Satellite Uplink", "Satellite channel enables sync when terrestrial is down"],
        ["Priority Routing", "Critical SOS flagged for immediate team dispatch"],
        ["Offline Resilience", "System continues accepting SOS even with zero connectivity"],
    ]
    df = pd.DataFrame(rows, columns=["Feature", "Implementation"])
    st.dataframe(df, use_container_width=True, hide_index=True)

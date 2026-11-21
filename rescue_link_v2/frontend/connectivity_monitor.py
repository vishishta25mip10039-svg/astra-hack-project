# ============================================================
# MEMBER 2 — FRONTEND
# FILE: frontend/connectivity_monitor.py
# PURPOSE: Toggle channels, trigger sync, view comm logs
# ============================================================

import streamlit as st
import pandas as pd
from backend.connectivity import get_state, set_state, sync_pending_requests, can_transmit
from backend.db import get_connection


def show():
    st.markdown("""
    <div class="hero-banner">
        <h1>📡 Connectivity Monitor</h1>
        <p>Simulate satellite vs terrestrial channel states — core Domain 4 concept</p>
    </div>
    """, unsafe_allow_html=True)

    state = get_state()

    # ── Channel Toggles ───────────────────────────────────────
    st.subheader("🔌 Communication Channels")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background:#131B2E;border:1px solid #1E3A5F;border-radius:10px;
                    padding:16px;text-align:center;min-height:120px;">
            <div style="font-size:2rem;">📶</div>
            <div style="color:#00D4FF;font-weight:700;">Cellular Network</div>
            <div style="color:#8BA4C8;font-size:0.82rem;margin-top:4px;">
                4G/5G terrestrial coverage</div>
        </div>
        """, unsafe_allow_html=True)
        cellular = st.toggle("Enable Cellular", value=bool(state["cellular"]), key="tog_cell")

    with col2:
        st.markdown("""
        <div style="background:#131B2E;border:1px solid #1E3A5F;border-radius:10px;
                    padding:16px;text-align:center;min-height:120px;">
            <div style="font-size:2rem;">🌐</div>
            <div style="color:#00D4FF;font-weight:700;">Internet / WiFi</div>
            <div style="color:#8BA4C8;font-size:0.82rem;margin-top:4px;">
                Broadband / WiFi uplink</div>
        </div>
        """, unsafe_allow_html=True)
        internet = st.toggle("Enable Internet", value=bool(state["internet"]), key="tog_net")

    with col3:
        st.markdown("""
        <div style="background:#131B2E;border:1px solid #1E3A5F;border-radius:10px;
                    padding:16px;text-align:center;min-height:120px;">
            <div style="font-size:2rem;">🛰️</div>
            <div style="color:#00D4FF;font-weight:700;">Satellite Link</div>
            <div style="color:#8BA4C8;font-size:0.82rem;margin-top:4px;">
                ISRO/GSAT store-and-forward</div>
        </div>
        """, unsafe_allow_html=True)
        satellite = st.toggle("Enable Satellite", value=bool(state["satellite"]), key="tog_sat")

    # ── Apply + Sync buttons ──────────────────────────────────
    bc1, bc2 = st.columns(2)
    with bc1:
        if st.button("💾 Apply Channel Settings", use_container_width=True):
            set_state(cellular, internet, satellite)
            st.success("Channel state updated.")
            st.rerun()
    with bc2:
        if st.button("🔄 Sync Pending Requests Now", use_container_width=True):
            count, msg = sync_pending_requests()
            if count > 0:
                st.success(msg)
            else:
                st.warning(msg)
            st.rerun()

    # ── Live status ───────────────────────────────────────────
    can_send, channel = can_transmit()
    color = "#44BB44" if can_send else "#FF4444"
    icon  = "🟢" if can_send else "🔴"
    st.markdown(f"""
    <div style="background:#131B2E;border:2px solid {color};border-radius:10px;
                padding:16px 24px;margin:16px 0;text-align:center;">
        <div style="font-size:1.1rem;font-weight:700;color:{color};">
            {icon} Transmission Status:
            {"ONLINE via " + channel.upper() if can_send else "OFFLINE — All channels down"}
        </div>
        <div style="color:#8BA4C8;margin-top:4px;font-size:0.85rem;">
            {"SOS submissions will be synchronised immediately." if can_send
             else "SOS submissions will be stored locally (store-and-forward mode)."}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Global comm log ───────────────────────────────────────
    st.subheader("📋 All Communication Logs")
    conn = get_connection()
    logs = conn.execute("""
        SELECT cl.timestamp, cl.request_id, cl.event, cl.channel, cl.notes
        FROM comm_logs cl
        ORDER BY cl.timestamp DESC
        LIMIT 100
    """).fetchall()
    conn.close()

    if logs:
        df = pd.DataFrame([dict(r) for r in logs])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No communication events recorded yet.")

    # ── Scenario explainer ────────────────────────────────────
    st.markdown("---")
    st.subheader("💡 Demo Scenarios")
    s1, s2, s3 = st.columns(3)
    scenarios = [
        ("🌊 Flood / Disaster Zone", "Turn OFF cellular + internet → Submit SOS → "
         "Turn ON satellite → Click Sync → Watch pending → synchronised",
         "Simulates remote disaster where only satellite is available."),
        ("🏙️ Urban Emergency", "Keep cellular ON → Submit SOS → "
         "It immediately synchronises via cellular network.",
         "Simulates normal city connectivity."),
        ("📡 Satellite-Only Rescue", "Turn OFF everything → Submit multiple SOS → "
         "Enable satellite only → Sync → All flush via GSAT.",
         "Full Domain 4 store-and-forward demonstration."),
    ]
    for col, (title, steps, note) in zip([s1, s2, s3], scenarios):
        with col:
            st.markdown(f"""
            <div style="background:#131B2E;border:1px solid #1E3A5F;border-radius:10px;padding:14px;">
                <div style="color:#00D4FF;font-weight:700;margin-bottom:8px;">{title}</div>
                <div style="color:#E8F4FD;font-size:0.82rem;margin-bottom:8px;">{steps}</div>
                <div style="color:#8BA4C8;font-size:0.78rem;font-style:italic;">{note}</div>
            </div>
            """, unsafe_allow_html=True)

"""RESCUE LINK — Streamlit application entry point."""

import streamlit as st
import sys
from pathlib import Path

# Ensure directory is on sys.path for Streamlit Cloud deployment
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Streamlit requires page configuration before any other Streamlit command.
st.set_page_config(
    page_title="Rescue Link | Mission Operations",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from backend.db import init_db, seed_demo_data, reset_demo_data  # noqa: E402
from backend.connectivity import get_state, apply_demo_preset, sync_pending_requests  # noqa: E402
from backend.rescue import get_metrics  # noqa: E402
from backend.sos import get_all_requests  # noqa: E402
from utils.helpers import apply_theme  # noqa: E402

PAGES = {
    "Overview": "home",
    "Citizen SOS": "citizen_portal",
    "Connectivity & Sync": "connectivity_monitor",
    "Command Centre": "command_centre",
    "Delivery Receipts": "delivery_receipts",
    "Analytics": "analytics",
    "Mission & Architecture": "about",
}


@st.cache_resource(show_spinner=False)
def initialize_database() -> bool:
    init_db()
    return True


initialize_database()
apply_theme()

with st.sidebar:
    st.markdown(
        """
        <div class="rl-brand">
          <div class="rl-brand-mark" aria-hidden="true">RL</div>
          <div>
            <div class="rl-brand-name">Rescue Link</div>
            <div class="rl-brand-subtitle">Store · Queue · Sync · Save</div>
          </div>
        </div>
        <div class="rl-sidebar-label">MISSION WORKSPACE</div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Workspace",
        options=list(PAGES.keys()),
        label_visibility="collapsed",
        key="rl_navigation",
    )

    state = get_state()
    metrics = get_metrics()
    active_links = sum(bool(state[key]) for key in ("cellular", "internet", "satellite"))
    if active_links > 0:
        link_label = f"{active_links} of 3 active"
    else:
        link_label = "Blackout (Offline)"

    team_label = f"{metrics['available_teams']} teams ready"
    st.markdown(
        f"""
        <div class="rl-sidebar-status">
          <div class="rl-sidebar-status-title">System snapshot</div>
          <div class="rl-sidebar-status-row"><span>Uplink</span><span class="rl-sidebar-status-value">{link_label}</span></div>
          <div class="rl-sidebar-status-row"><span>Responders</span><span class="rl-sidebar-status-value">{team_label}</span></div>
          <div class="rl-sidebar-status-row"><span>Triage queue</span><span class="rl-sidebar-status-value">{metrics['total']} requests</span></div>
          <div class="rl-sidebar-status-row"><span>Packet loss</span><span class="rl-sidebar-status-value" >0.0% (Zero)</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1-Click Fast Demo Scenario Switcher in Sidebar
    st.markdown('<div class="rl-sidebar-section-gap"></div><div class="rl-sidebar-label">FAST DEMO PRESETS</div>', unsafe_allow_html=True)
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        if st.button("🟢 Normal", use_container_width=True, help="Cell + Net ON"):
            apply_demo_preset("normal")
            st.rerun()
    with d_col2:
        if st.button("🔴 Blackout", use_container_width=True, help="All networks OFF"):
            apply_demo_preset("blackout")
            st.rerun()

    if st.button("🛰️ Satellite Fallback", use_container_width=True, help="Cell OFF, Satellite ON"):
        apply_demo_preset("satellite")
        st.rerun()

    pending_count = metrics["pending_transmission"]
    if pending_count > 0:
        st.markdown(
            f"<div style='background:rgba(242,239,230,.10);border:1px solid rgba(242,239,230,.38);border-radius:6px;padding:6px 10px;margin-top:6px;font-size:11px;color:#F2EFE6;font-weight:700'>"
            f"📦 {pending_count} pending in offline queue"
            f"</div>",
            unsafe_allow_html=True,
        )
        if st.button("⚡ Burst-Sync Queue", use_container_width=True, type="primary"):
            sync_pending_requests()
            st.rerun()

    st.markdown('<div class="rl-sidebar-section-gap"></div><div class="rl-sidebar-label">DEMO DATASET</div>', unsafe_allow_html=True)
    if not get_all_requests():
        if st.button("Load sample scenario", use_container_width=True, type="secondary"):
            seed_demo_data()
            st.rerun()
        st.caption("Populates 3 realistic disaster triage incidents.")
    else:
        if st.button("Reset demo baseline", use_container_width=True, type="secondary", help="Clears custom data and restores clean demo incidents"):
            reset_demo_data()
            st.rerun()
        st.caption("Baseline scenario loaded with Slide 7 priority scores.")

    st.markdown(
        """
        <div class="rl-sidebar-footer">
          <span class="rl-footer-dot"></span><span>ASTRA 2026 · Team Aurora</span>
          <div class="rl-footer-location">VIT Bhopal · ANTERiX Club</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

module_name = PAGES[page]
module = __import__(f"frontend.{module_name}", fromlist=["show"])
module.show()


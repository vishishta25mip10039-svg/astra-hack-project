# ============================================================
# MEMBER 3 — INTEGRATION
# FILE: app.py
# PURPOSE: Streamlit entry point — routing + sidebar nav
# Run:  streamlit run app.py
# ============================================================

import streamlit as st
from backend.db import init_db, seed_demo_data
from utils.helpers import apply_theme

# ── Init DB on first run ──────────────────────────────────────
init_db()

# ── Page config (must be first Streamlit call) ────────────────
st.set_page_config(
    page_title="RESCUE LINK",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Apply dark theme CSS ──────────────────────────────────────
apply_theme()

# ── Sidebar navigation ────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px;">
        <div style="font-size:2.5rem;">🛰️</div>
        <div style="color:#00D4FF;font-weight:800;font-size:1.3rem;">RESCUE LINK</div>
        <div style="color:#8BA4C8;font-size:0.75rem;margin-top:2px;">
            Satellite SOS · ASTRA 2026
        </div>
    </div>
    <hr style="border-color:#1E3A5F;margin:8px 0;">
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        [
            "🏠 Home",
            "🆘 Citizen SOS Portal",
            "🎯 Command Centre",
            "📡 Connectivity Monitor",
            "📊 Analytics",
            "ℹ️ About",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#1E3A5F;margin:16px 0;'>", unsafe_allow_html=True)

    if st.button("🎬 Load Demo Data", use_container_width=True):
        seed_demo_data()
        st.success("Demo SOS requests loaded!")
        st.rerun()

    st.markdown("""
    <div style="margin-top:16px;color:#8BA4C8;font-size:0.72rem;text-align:center;">
        Domain 4: Satellite Comm<br>Team Aurora · VIT Bhopal
    </div>
    """, unsafe_allow_html=True)

# ── Page routing ──────────────────────────────────────────────
if page == "🏠 Home":
    from frontend.home import show
    show()

elif page == "🆘 Citizen SOS Portal":
    from frontend.citizen_portal import show
    show()

elif page == "🎯 Command Centre":
    from frontend.command_centre import show
    show()

elif page == "📡 Connectivity Monitor":
    from frontend.connectivity_monitor import show
    show()

elif page == "📊 Analytics":
    from frontend.analytics import show
    show()

elif page == "ℹ️ About":
    from frontend.about import show
    show()

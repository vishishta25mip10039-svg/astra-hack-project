# ============================================================
# MEMBER 2 — FRONTEND
# FILE: frontend/analytics.py
# PURPOSE: Charts — category, priority, comm status, funnel, map
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from backend.sos import get_all_requests
from backend.rescue import get_metrics


def show():
    st.markdown("""
    <div class="hero-banner">
        <h1>📊 Analytics Dashboard</h1>
        <p>Real-time insights into SOS patterns, transmission health, and rescue performance</p>
    </div>
    """, unsafe_allow_html=True)

    requests = get_all_requests()
    if not requests:
        st.info("No data yet. Submit some SOS requests first.")
        return

    df = pd.DataFrame(requests)
    m  = get_metrics()

    PLOTLY_BG  = "rgba(0,0,0,0)"
    PLOTLY_FG  = "#E8F4FD"
    PLOTLY_FONT = dict(color=PLOTLY_FG, family="monospace")

    # ── Row 1: Category pie + Priority bar ───────────────────
    r1a, r1b = st.columns(2)

    with r1a:
        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig = px.pie(
            cat_counts, names="Category", values="Count",
            title="SOS by Category",
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4,
        )
        fig.update_layout(paper_bgcolor=PLOTLY_BG, plot_bgcolor=PLOTLY_BG,
                          font=PLOTLY_FONT, title_font_color="#00D4FF")
        st.plotly_chart(fig, use_container_width=True)

    with r1b:
        pri_order  = ["critical","high","moderate","low"]
        pri_colors = {"critical":"#FF4444","high":"#FF8800","moderate":"#FFDD00","low":"#44BB44"}
        pri_counts = df["priority"].value_counts().reindex(pri_order).dropna().reset_index()
        pri_counts.columns = ["Priority", "Count"]
        fig = px.bar(
            pri_counts, x="Priority", y="Count",
            title="SOS by Priority",
            color="Priority",
            color_discrete_map=pri_colors,
        )
        fig.update_layout(paper_bgcolor=PLOTLY_BG, plot_bgcolor=PLOTLY_BG,
                          font=PLOTLY_FONT, title_font_color="#00D4FF",
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Comm status pie + Rescue funnel ────────────────
    r2a, r2b = st.columns(2)

    with r2a:
        comm_counts = df["comm_status"].value_counts().reset_index()
        comm_counts.columns = ["Status", "Count"]
        fig = px.pie(
            comm_counts, names="Status", values="Count",
            title="Transmission Status",
            color="Status",
            color_discrete_map={"synchronised":"#44BB44","pending":"#FF4444"},
            hole=0.4,
        )
        fig.update_layout(paper_bgcolor=PLOTLY_BG, plot_bgcolor=PLOTLY_BG,
                          font=PLOTLY_FONT, title_font_color="#00D4FF")
        st.plotly_chart(fig, use_container_width=True)

    with r2b:
        funnel_order  = ["open","assigned","in_progress","resolved"]
        rescue_counts = df["rescue_status"].value_counts().reindex(funnel_order).fillna(0).reset_index()
        rescue_counts.columns = ["Stage", "Count"]
        fig = px.funnel(
            rescue_counts, x="Count", y="Stage",
            title="Rescue Pipeline Funnel",
            color_discrete_sequence=["#00D4FF"],
        )
        fig.update_layout(paper_bgcolor=PLOTLY_BG, plot_bgcolor=PLOTLY_BG,
                          font=PLOTLY_FONT, title_font_color="#00D4FF")
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Geographic scatter ─────────────────────────────
    st.subheader("🗺️ Incident Geographic Distribution")
    fig = px.scatter_mapbox(
        df,
        lat="latitude", lon="longitude",
        color="priority",
        size="people_affected",
        hover_name="id",
        hover_data={"category": True, "severity": True, "comm_status": True},
        color_discrete_map={
            "critical":"#FF4444","high":"#FF8800",
            "moderate":"#FFDD00","low":"#44BB44",
        },
        mapbox_style="carto-darkmatter",
        zoom=4,
        center={"lat": 22.5, "lon": 80.0},
        height=420,
        title="Incident Locations (bubble size = people affected)",
    )
    fig.update_layout(
        paper_bgcolor=PLOTLY_BG,
        font=PLOTLY_FONT,
        title_font_color="#00D4FF",
        margin={"r":0,"t":40,"l":0,"b":0},
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Summary KPI strip ─────────────────────────────────────
    st.subheader("📈 Key Metrics Summary")
    kc = st.columns(5)
    kpis = [
        ("Total SOS",            m["total"],               "📡"),
        ("Critical",             m["critical"],            "🔴"),
        ("Pending Transmission", m["pending_transmission"],"⏳"),
        ("Available Teams",      m["available_teams"],     "🚁"),
        ("Resolved",             m["resolved"],            "✅"),
    ]
    for col, (label, val, icon) in zip(kc, kpis):
        with col:
            st.metric(f"{icon} {label}", val)

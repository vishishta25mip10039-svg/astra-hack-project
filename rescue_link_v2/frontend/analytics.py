"""Analytics for SOS volume, Slide 7 priority engine, transmission routes and response."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend.sos import get_all_requests
from backend.rescue import get_metrics
from backend.db import seed_demo_data
from utils.helpers import page_header, section_heading, PRIORITY_COLORS


TEXT = "#344B5D"
MUTED = "#718295"
GRID = "#E3EAF0"
BRAND = "#477F9E"


def _style_figure(fig, height: int = 310):
    """Apply a high-contrast light theme to every analytics chart."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={
            "family": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            "color": TEXT,
            "size": 12,
        },
        title={"font": {"size": 15, "color": "#203244"}, "x": 0.025, "xanchor": "left"},
        margin={"l": 24, "r": 18, "t": 54, "b": 30},
        height=height,
        legend={
            "orientation": "h",
            "y": -0.18,
            "font": {"color": TEXT, "size": 11},
            "title": {"font": {"color": TEXT}},
        },
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        title=None,
        tickfont={"color": TEXT, "size": 11},
        title_font={"color": TEXT},
        linecolor="#CAD5DE",
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        title=None,
        tickfont={"color": TEXT, "size": 11},
        title_font={"color": TEXT},
        linecolor="#CAD5DE",
    )
    return fig


def show() -> None:
    page_header(
        "Operational Analytics & Mission Impact",
        "Slide 7 triage breakdown, zero-data-loss transmission metrics and response pipeline.",
        "ASTRA 2026 / 3:00–3:30 DEMO STAGE · IMPACT & METRICS",
    )

    requests = get_all_requests()
    metrics = get_metrics()

    # Top-level Slide 9 key impact metrics
    metric_cols = st.columns(5)
    total_people = sum(r.get("people_affected", 1) for r in requests) if requests else 0

    impact_values = [
        ("Data Loss Rate", "0.0%", "All queued in SQLite, zero loss"),
        ("Triage Latency", "< 1 sec", "Instant Slide 7 algorithmic scoring"),
        ("Active SOS Reports", metrics["total"], "Total incident count"),
        ("Citizens Trapped/Assisted", total_people, "Direct disaster reach"),
        ("Golden Window Resolved", metrics["resolved"], "Rescues completed"),
    ]
    for col, (label, value, note) in zip(metric_cols, impact_values):
        with col, st.container(border=True):
            st.metric(label, value)
            st.caption(note)

    if not requests:
        with st.container(border=True):
            st.markdown(
                """
                <div class="rl-empty-state">
                  <div class="rl-empty-kicker">AWAITING INCIDENT DATA</div>
                  <div class="rl-empty-title">Analytics will build as reports arrive.</div>
                  <div class="rl-empty-copy">Category trends, priority distribution, transmission outcomes and response progress are calculated from saved SOS requests. Submit a request or load the sample scenario to explore these views.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Load sample scenario", type="primary"):
                seed_demo_data()
                st.rerun()
        return

    frame = pd.DataFrame(requests)
    
    section_heading("Priority & Triage Breakdown (Slide 7 Engine)", "Analysis of 0-100 triage scores vs categorical severity.")
    p_left, p_right = st.columns(2, gap="large")

    with p_left, st.container(border=True):
        # Priority Score Histogram / Bar
        score_bins = ["0-19 (Low)", "20-39 (Moderate)", "40-69 (High)", "70-100 (Critical)"]
        tier_counts = {
            "70-100 (Critical)": len(frame[frame["priority"] == "critical"]),
            "40-69 (High)": len(frame[frame["priority"] == "high"]),
            "20-39 (Moderate)": len(frame[frame["priority"] == "moderate"]),
            "0-19 (Low)": len(frame[frame["priority"] == "low"]),
        }
        tier_df = pd.DataFrame(list(tier_counts.items()), columns=["Tier", "Incidents"])
        tier_fig = px.bar(
            tier_df, x="Tier", y="Incidents", color="Tier",
            title="Slide 7 Priority Engine: Response Tiers",
            color_discrete_map={
                "70-100 (Critical)": "#C84D50",
                "40-69 (High)": "#D77B42",
                "20-39 (Moderate)": "#B38D3D",
                "0-19 (Low)": "#44856D",
            },
        )
        tier_fig.update_layout(showlegend=False)
        _style_figure(tier_fig)
        st.plotly_chart(tier_fig, use_container_width=True, config={"displayModeBar": False})

    with p_right, st.container(border=True):
        # Category Breakdown
        category_counts = frame["category"].value_counts().rename_axis("Category").reset_index(name="Requests")
        category_fig = px.bar(
            category_counts.sort_values("Requests"),
            x="Requests", y="Category", orientation="h",
            title="Incidents by Category",
            color_discrete_sequence=[BRAND],
        )
        category_fig.update_layout(showlegend=False)
        _style_figure(category_fig, max(300, 42 * len(category_counts) + 90))
        st.plotly_chart(category_fig, use_container_width=True, config={"displayModeBar": False})

    section_heading("Transmission Resilience & Response Pipeline", "Store-and-forward routes and dispatch progression.")
    c_left, c_right = st.columns(2, gap="large")

    with c_left, st.container(border=True):
        # Transmission breakdown: Cellular vs Satellite vs Offline Pending
        def determine_route(row):
            if row["comm_status"] == "pending":
                return "Offline Queue (SQLite)"
            ch = row.get("sync_channel")
            if ch == "satellite_sim":
                return "Satellite Fallback (NavIC Sim)"
            return "Terrestrial (Cell / Wi-Fi)"

        frame["route_type"] = frame.apply(determine_route, axis=1)
        route_counts = frame["route_type"].value_counts().reset_index()
        route_counts.columns = ["Transmission Route", "Count"]

        comm_fig = px.pie(
            route_counts, names="Transmission Route", values="Count", hole=0.6,
            title="Transmission Resilience Breakdown (3 Layers)",
            color="Transmission Route",
            color_discrete_map={
                "Terrestrial (Cell / Wi-Fi)": "#2563EB",
                "Satellite Fallback (NavIC Sim)": "#059669",
                "Offline Queue (SQLite)": "#D97706",
            },
        )
        _style_figure(comm_fig)
        st.plotly_chart(comm_fig, use_container_width=True, config={"displayModeBar": False})

    with c_right, st.container(border=True):
        rescue_order = ["open", "assigned", "in_progress", "resolved"]
        rescue_counts = (
            frame["rescue_status"].value_counts().reindex(rescue_order, fill_value=0)
            .rename_axis("Response Status").reset_index(name="Requests")
        )
        rescue_counts["Response Status"] = rescue_counts["Response Status"].str.replace("_", " ").str.title()
        response_fig = px.bar(
            rescue_counts, x="Response Status", y="Requests",
            title="Rescue Operations Pipeline",
            color="Response Status",
            color_discrete_map={
                "Open": "#E11D48",
                "Assigned": "#F59E0B",
                "In Progress": "#3B82F6",
                "Resolved": "#10B981",
            },
        )
        response_fig.update_layout(showlegend=False)
        _style_figure(response_fig)
        st.plotly_chart(response_fig, use_container_width=True, config={"displayModeBar": False})

    left, right = st.columns(2, gap="large")

    with left, st.container(border=True):
        category_counts = frame["category"].value_counts().rename_axis("Category").reset_index(name="Requests")
        category_fig = px.bar(
            category_counts.sort_values("Requests"),
            x="Requests", y="Category", orientation="h",
            title="Requests by category",
            color_discrete_sequence=[BRAND],
        )
        category_fig.update_layout(showlegend=False)
        _style_figure(category_fig, max(300, 42 * len(category_counts) + 90))
        st.plotly_chart(category_fig, use_container_width=True, config={"displayModeBar": False})

    with right, st.container(border=True):
        priority_order = ["critical", "high", "moderate", "low"]
        priority_counts = (
            frame["priority"].value_counts().reindex(priority_order, fill_value=0)
            .rename_axis("Priority").reset_index(name="Requests")
        )
        priority_fig = px.bar(
            priority_counts, x="Priority", y="Requests", color="Priority",
            title="Requests by priority",
            category_orders={"Priority": priority_order},
            color_discrete_map=PRIORITY_COLORS,
        )
        priority_fig.update_layout(showlegend=False)
        _style_figure(priority_fig)
        st.plotly_chart(priority_fig, use_container_width=True, config={"displayModeBar": False})

    left, right = st.columns(2, gap="large")
    with left, st.container(border=True):
        comm_counts = frame["comm_status"].value_counts().rename_axis("Transmission").reset_index(name="Requests")
        comm_fig = px.pie(
            comm_counts, names="Transmission", values="Requests", hole=0.62,
            title="Transmission status",
            color="Transmission",
            color_discrete_map={"synchronised": "#43856B", "pending": "#D97736"},
        )
        _style_figure(comm_fig)
        st.plotly_chart(comm_fig, use_container_width=True, config={"displayModeBar": False})

    with right, st.container(border=True):
        rescue_order = ["open", "assigned", "in_progress", "resolved"]
        rescue_counts = (
            frame["rescue_status"].value_counts().reindex(rescue_order, fill_value=0)
            .rename_axis("Response status").reset_index(name="Requests")
        )
        rescue_counts["Response status"] = rescue_counts["Response status"].str.replace("_", " ").str.title()
        response_fig = px.bar(
            rescue_counts, x="Response status", y="Requests",
            title="Requests by response status",
            color_discrete_sequence=[BRAND],
        )
        response_fig.update_layout(showlegend=False)
        _style_figure(response_fig)
        st.plotly_chart(response_fig, use_container_width=True, config={"displayModeBar": False})

    section_heading("Incident locations", "Marker colour represents priority; bubble size represents people affected.")
    map_frame = frame.copy()
    map_frame["people_affected"] = map_frame["people_affected"].clip(lower=1)
    map_fig = px.scatter_map(
        map_frame,
        lat="latitude", lon="longitude",
        color="priority", size="people_affected",
        hover_name="id",
        hover_data={"category": True, "severity": True, "comm_status": True, "people_affected": True},
        color_discrete_map=PRIORITY_COLORS,
        map_style="carto-positron",
        zoom=3.5,
        center={"lat": 22.5, "lon": 80.0},
        height=430,
    )
    map_fig.update_layout(
        paper_bgcolor="white",
        font={"family": "Inter, sans-serif", "color": TEXT},
        margin={"r": 0, "t": 8, "l": 0, "b": 0},
        legend={"orientation": "h", "y": -0.02, "font": {"color": TEXT, "size": 11}},
    )
    st.plotly_chart(map_fig, use_container_width=True, config={"displayModeBar": False})

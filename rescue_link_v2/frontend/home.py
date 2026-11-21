"""Mission overview: current incidents, communication links and response capacity."""

from html import escape

import streamlit as st

from backend.connectivity import get_state
from backend.db import seed_demo_data
from backend.rescue import get_metrics
from backend.sos import get_all_requests
from utils.helpers import (
    page_header,
    section_heading,
    status_badge_html,
    priority_badge,
    comm_badge,
    rescue_badge,
    score_badge_html,
)


def _channel_card(name: str, label: str, enabled: bool, description: str,
                  simulated: bool = False) -> str:
    if enabled:
        state_html = '<span class="rl-status" style="background:#EAF3EE;color:#347154">Available</span>'
        dot_color = "#4A9878"
    else:
        state_html = '<span class="rl-status" style="background:#F1F3F5;color:#788795">Standby</span>'
        dot_color = "#9AA8B3"
    sim_note = '<div class="rl-network-description" style="color:#0284C7;font-weight:700">Simulated NavIC / Starlink Link</div>' if simulated else ""
    return f"""
    <div class="rl-network-card">
      <div class="rl-network-label">{escape(label)}</div>
      <div class="rl-network-name"><span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{dot_color};margin-right:7px;vertical-align:1px"></span>{escape(name)}</div>
      {state_html}
      <div class="rl-network-description">{escape(description)}</div>
      {sim_note}
    </div>
    """


def _incident_row(request: dict) -> str:
    level = str(request.get("priority", "low")).lower()
    score = request.get("priority_score", 0)
    badge = score_badge_html(score, level)
    description = request.get("description") or request.get("category", "Emergency report")
    description = escape(str(description))
    return f"""
    <div class="rl-incident-line">
      <div style="min-width:0">
        <div class="rl-incident-title">{escape(str(request.get('category', 'Incident')))}</div>
        <div class="rl-incident-meta">{escape(str(request.get('id', '')))} · {description[:88]}</div>
        <div class="rl-incident-meta">{int(request.get('people_affected') or 1)} people · {escape(rescue_badge(str(request.get('rescue_status', 'open'))))} · {escape(comm_badge(str(request.get('comm_status', 'pending'))))}</div>
      </div>
      <div>{badge}</div>
    </div>
    """


def show() -> None:
    page_header(
        "Rescue Link: Mission Operations",
        "Emergency coordination that works when networks don't. Store. Queue. Sync. Save.",
        "ASTRA 2026 · DOMAIN 03 & 04 · VIT BHOPAL",
    )

    # Slide 1 & Slide 9 Key Strategic Metrics
    stat_cols = st.columns(4, gap="medium")
    pillars = [
        ("72 hrs", "CRITICAL RESCUE WINDOW", "Slide 1: Golden-hour survival window"),
        ("60%", "DISASTERS HIT COMMS FIRST", "Slide 1: Ground network vulnerability"),
        ("1,000s", "LIVES LOST TO COORDINATION", "Slide 1: Preventable coordination gap"),
        ("0.0%", "DATA LOST WITH RESCUE LINK", "Slide 9: Zero loss via SQLite Store & Forward"),
    ]
    for col, (val, lbl, note) in zip(stat_cols, pillars):
        with col, st.container(border=True):
            st.markdown(f"<div style='font-size:26px;font-weight:800;color:#1E3A5F;letter-spacing:-.03em'>{val}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:10px;font-weight:750;color:#64748B;letter-spacing:.06em'>{lbl}</div>", unsafe_allow_html=True)
            st.caption(note)

    metrics = get_metrics()
    state = get_state()
    requests = get_all_requests()

    st.markdown("")
    # Real-time System Operational Snapshot
    section_heading("Operational Snapshot", "Live data from the local SQLite persistent mission store.")
    metric_cols = st.columns(4, gap="medium")
    metric_values = [
        ("Total Incident Reports", metrics["total"], "All records captured"),
        ("Critical Triage (>70pts)", metrics["critical"], "Immediate dispatch required"),
        ("Awaiting Transmission", metrics["pending_transmission"], "Safely buffered offline"),
        ("Rescue Units Ready", metrics["available_teams"], "Available for dispatch"),
    ]
    for col, (label, value, note) in zip(metric_cols, metric_values):
        with col, st.container(border=True):
            st.metric(label, value)
            st.caption(note)

    section_heading("3-Layer Communication Resilience", "Primary terrestrial channels + Satellite fallback simulation (Domain 04).")
    network_cols = st.columns(3, gap="medium")
    network = [
        ("Cellular Network", "TERRESTRIAL LINK (PRIMARY)", bool(state["cellular"]), "4G / 5G mobile network coverage"),
        ("Internet / Wi-Fi", "DATA LINK (PRIMARY)", bool(state["internet"]), "Broadband or localized field Wi-Fi"),
        ("Satellite Link", "FALLBACK LINK (DOMAIN 04)", bool(state["satellite"]), "Simulated ISRO NavIC / Starlink burst uplink", True),
    ]
    for col, item in zip(network_cols, network):
        with col:
            st.markdown(_channel_card(*item), unsafe_allow_html=True)

    active_count = sum(bool(state[key]) for key in ("cellular", "internet", "satellite"))
    if active_count:
        route_text = "Communication uplink operational. New emergency requests will transmit immediately."
        route_badge = status_badge_html(f"{active_count} of 3 Links Active", "low")
    else:
        route_text = "Total Network Blackout: Terrestrial & satellite links down. Requests queue safely in local SQLite with 0% data loss."
        route_badge = status_badge_html("Offline Resilience Mode", "critical")
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:10px 0 20px">'
        f'{route_badge}<span style="font-size:12px;color:#475569;font-weight:600">{escape(route_text)}</span></div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.25, 0.95], gap="large")
    with left:
        section_heading("Live Incident Queue", "Ranked strictly by Slide 7 Priority Score (Critical first).")
        if requests:
            with st.container(border=True):
                for request in requests[:5]:
                    st.markdown(_incident_row(request), unsafe_allow_html=True)
        else:
            with st.container(border=True):
                st.markdown(
                    """
                    <div class="rl-empty-state">
                      <div class="rl-empty-kicker">REGISTER READY</div>
                      <div class="rl-empty-title">Operations feed is standing by.</div>
                      <div class="rl-empty-copy">Submit an SOS in Citizen Portal or load the hackathon demo scenario to explore triage scoring, mapping, and nearest-unit dispatch.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Load Demo Scenario", type="primary", use_container_width=True):
                    seed_demo_data()
                    st.rerun()

    with right:
        section_heading("End-to-End Workflow (Slide 6)", "Citizen ➔ RESCUE LINK ➔ Command Centre ➔ Response Team.")
        with st.container(border=True):
            steps = [
                ("01", "Citizen SOS", "Captures category, location, people count and danger level."),
                ("02", "Priority Engine", "Slide 7 algorithmic triage scores 0-100 in < 1 second."),
                ("03", "Connectivity Check", "Transmits instantly or queues safely in local SQLite."),
                ("04", "Store & Forward", "Burst-syncs via Satellite Simulation when channel opens."),
                ("05", "Command Centre", "Geospatial triage map recommends nearest available team."),
                ("06", "Resolution & Audit", "Field team responds, marks resolved, receipt verified."),
            ]
            for number, title, copy in steps:
                st.markdown(
                    f'<div class="rl-step"><div class="rl-step-number">{number}</div>'
                    f'<div><div class="rl-step-title">{escape(title)}</div>'
                    f'<div class="rl-step-copy">{escape(copy)}</div></div></div>',
                    unsafe_allow_html=True,
                )

    # 3.5 Minute Demo Timeline Cheatsheet for Judges & Presenter
    with st.expander("⏱️ Live Hackathon Presentation Demo Cheatsheet (3.5 Minutes)", expanded=False):
        st.markdown(
            """
            | Time | Screen | What to Demonstrate to Judges |
            | :--- | :--- | :--- |
            | **0:00–0:30** | **Overview** | Explain system mission, 72-hr golden window, and 3-layer resilience architecture. |
            | **0:30–1:00** | **Citizen SOS** | Submit an online emergency; show Slide 7 real-time scoring in <1 second. |
            | **1:00–1:45** | **Connectivity** | Trigger Scenario 2 (Blackout) -> Submit offline SOS -> Trigger Scenario 3 (Satellite) -> Click Burst Sync! |
            | **1:45–2:30** | **Command Centre** | Point out tactical map, nearest team recommendation, and 1-click dispatch. |
            | **2:30–3:00** | **Delivery Receipts** | Display cryptographic receipt, store-and-forward journey, and proof of 0% packet loss. |
            | **3:00–3:30** | **Analytics** | Highlight 0% data loss rate, response pipeline, and priority distribution. |
            """
        )


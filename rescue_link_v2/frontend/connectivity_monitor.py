"""Connectivity channel simulation, satellite telemetry and store-and-forward sync controls."""

import time
import pandas as pd
import streamlit as st

from backend.connectivity import (
    get_state, set_state, sync_pending_requests, can_transmit,
    apply_demo_preset, get_satellite_telemetry,
)
from backend.db import get_connection
from backend.sos import get_all_requests
from utils.helpers import page_header, section_heading, status_badge_html


CHANNELS = [
    ("Cellular Network", "PRIMARY LINK", "4G / 5G terrestrial telecom towers", "cellular"),
    ("Internet / Wi-Fi", "PRIMARY LINK", "Broadband, fiber or local Wi-Fi data link", "internet"),
    ("Satellite Link", "FALLBACK LINK", "Simulated ISRO NavIC / Starlink transponder (Domain 04)", "satellite"),
]


def show() -> None:
    page_header(
        "Connectivity & Satellite Link Simulation",
        "Control communication channels, inspect simulated satellite telemetry and trigger Store-and-Forward sync.",
        "ASTRA 2026 / DOMAIN 04 · SATELLITE CONNECTIVITY",
    )

    # Presentation disclaimer banner
    st.info(
        "🛰️ **Hackathon Presentation Detail**: Satellite connectivity is implemented as an accurate software simulation in this prototype, modeling ISRO NavIC (IRNSS) messaging and Starlink direct-to-device burst packet protocol."
    )

    # Fast 1-Click Preset Switcher for the 3.5 minute live demo
    section_heading("Live Demo 1-Click Presets", "Quickly set channel conditions during your presentation.")
    preset_cols = st.columns(3)
    with preset_cols[0]:
        if st.button("🟢 Scenario 1: Normal Comms", use_container_width=True, help="Cellular & Internet ON, Satellite OFF"):
            apply_demo_preset("normal")
            st.toast("Preset Applied: Terrestrial Normal Links Active", icon="🟢")
            st.rerun()
    with preset_cols[1]:
        if st.button("🔴 Scenario 2: Network Blackout", use_container_width=True, help="All networks OFF — test offline local SQLite storage"):
            apply_demo_preset("blackout")
            st.toast("Preset Applied: Network Blackout Active", icon="🔴")
            st.rerun()
    with preset_cols[2]:
        if st.button("🛰️ Scenario 3: Satellite Fallback", use_container_width=True, type="primary", help="Cellular/Internet OFF, Satellite ON — test burst sync"):
            apply_demo_preset("satellite")
            st.toast("Preset Applied: Satellite Fallback Active", icon="🛰️")
            st.rerun()

    state = get_state()
    section_heading("Manual Channel Configuration", "Toggle individual communication links and apply changes.")
    with st.form("channel_settings_form"):
        columns = st.columns(3, gap="medium")
        values = {}
        for col, (title, role_badge, description, key) in zip(columns, CHANNELS):
            with col, st.container(border=True):
                st.markdown(f"**{title}**")
                st.markdown(f"`{role_badge}`")
                st.caption(description)
                values[key] = st.toggle(
                    f"Enable {title}", value=bool(state[key]), key=f"channel_toggle_{key}"
                )
                current = "Active" if state[key] else "Unavailable / Severed"
                badge_level = "low" if state[key] else "critical"
                st.markdown(status_badge_html(current, badge_level), unsafe_allow_html=True)
        apply = st.form_submit_button("Apply Channel Configuration", type="secondary", use_container_width=True)

    if apply:
        set_state(values["cellular"], values["internet"], values["satellite"])
        st.success("Channel configuration updated.")
        st.rerun()

    can_send, channel = can_transmit()
    pending_requests = get_all_requests({"comm_status": "pending"})
    pending_count = len(pending_requests)
    telemetry = get_satellite_telemetry()

    st.markdown("")
    status_col, queue_col = st.columns([1.25, 0.75], gap="large")

    with status_col, st.container(border=True):
        section_heading("Active Transmission Route")
        if can_send:
            route_name = "Satellite Simulation (NavIC / Starlink Protocol)" if channel == "satellite_sim" else "Terrestrial Cellular / Internet"
            st.markdown(
                f"{status_badge_html('Uplink Online', 'low')} "
                f"<span style='color:#F1F5F9;font-size:14px;font-weight:700;margin-left:8px'>{route_name}</span>",
                unsafe_allow_html=True,
            )
            st.caption("New SOS requests will be transmitted and verified immediately.")
        else:
            st.markdown(
                f"{status_badge_html('Network Blackout', 'critical')} "
                f"<span style='color:#F87171;font-size:14px;font-weight:700;margin-left:8px'>No Ground or Satellite Channel</span>",
                unsafe_allow_html=True,
            )
            st.caption("Store-and-Forward Active: New requests are securely queued in local SQLite.")

        # Satellite Telemetry Card
        st.markdown(
            f"""
            <div style="background:#0B111E;border:1px solid #1E2D42;border-radius:9px;padding:12px;margin-top:12px">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:10px;font-weight:800;color:#38BDF8;letter-spacing:.08em;text-transform:uppercase">
                  🛰️ Domain 04 Satellite Telemetry Feed
                </span>
                {status_badge_html('Transponder Ready' if telemetry['active'] else 'Transponder Standby', 'low' if telemetry['active'] else 'moderate')}
              </div>
              <div class="rl-telemetry-grid">
                <div class="rl-telemetry-stat">
                  <div class="rl-telemetry-label">Constellation</div>
                  <div class="rl-telemetry-val" style="font-size:11px">NavIC & Starlink Sim</div>
                </div>
                <div class="rl-telemetry-stat">
                  <div class="rl-telemetry-label">RF Carrier</div>
                  <div class="rl-telemetry-val" style="font-size:11px">S-Band (2.49 GHz)</div>
                </div>
                <div class="rl-telemetry-stat">
                  <div class="rl-telemetry-label">Simulated Ping</div>
                  <div class="rl-telemetry-val" style="font-size:11px">{telemetry['simulated_latency_ms']} ms</div>
                </div>
                <div class="rl-telemetry-stat">
                  <div class="rl-telemetry-label">Packet Integrity</div>
                  <div class="rl-telemetry-val" style="font-size:11px">100% CRC32</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with queue_col, st.container(border=True):
        section_heading("Store-and-Forward Queue")
        st.metric("Requests Awaiting Sync", pending_count)
        if pending_count > 0:
            st.caption("Requests safely held in local SQLite buffer.")
            for req in pending_requests[:3]:
                st.caption(f"• `{req['id']}` · {req['category']} ({req['people_affected']} people)")
            if pending_count > 3:
                st.caption(f"... and {pending_count - 3} more queued")
        else:
            st.caption("Queue is clear. 100% of recorded incidents have been synchronised.")

        sync_btn = st.button("⚡ Synchronise Pending Queue", type="primary", use_container_width=True)
        if sync_btn:
            if not can_send:
                st.error("Cannot sync: No communication channel is active. Enable Satellite or Cellular first!")
            else:
                with st.spinner("Initiating burst uplink packet transmission..."):
                    time.sleep(0.5)
                    count, message = sync_pending_requests()
                if count:
                    st.success(message)
                else:
                    st.warning(message)
                st.rerun()

    section_heading("Communication & Transmission History", "Audit log of all transmission events.")
    connection = get_connection()
    logs = connection.execute(
        """
        SELECT cl.timestamp, cl.request_id, cl.event, cl.channel, cl.notes
        FROM comm_logs cl
        ORDER BY cl.timestamp DESC, cl.id DESC
        LIMIT 100
        """
    ).fetchall()
    connection.close()

    if logs:
        frame = pd.DataFrame([dict(row) for row in logs])
        frame.columns = ["Timestamp", "Request ID", "Event", "Channel", "Notes"]
        st.dataframe(frame, use_container_width=True, hide_index=True)
    else:
        st.info("No communication events have been recorded yet.")


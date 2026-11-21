# ============================================================
# MEMBER 2 — FRONTEND
# FILE: frontend/command_centre.py
# PURPOSE: Live map, team assignment, status updates, comm log
# ============================================================

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from backend.sos import get_all_requests, get_comm_logs
from backend.rescue import get_teams, assign_team, update_rescue_status
from utils.helpers import CATEGORIES, SEVERITIES, priority_badge, comm_badge, rescue_badge, PRIORITY_COLORS

RESCUE_STATUSES = ["open", "assigned", "in_progress", "resolved"]


def show():
    st.markdown("""
    <div class="hero-banner">
        <h1>🎯 Command Centre</h1>
        <p>Live situational map · Team dispatch · Status management</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ───────────────────────────────────────────────
    with st.expander("🔍 Filter Requests", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1: f_cat    = st.selectbox("Category",      ["All"] + CATEGORIES, key="cc_cat")
        with fc2: f_pri    = st.selectbox("Priority",      ["All","critical","high","moderate","low"], key="cc_pri")
        with fc3: f_comm   = st.selectbox("Comm Status",   ["All","pending","synchronised"], key="cc_comm")
        with fc4: f_rescue = st.selectbox("Rescue Status", ["All"] + RESCUE_STATUSES, key="cc_rescue")

    filters = {
        "category":      f_cat,
        "priority":      f_pri,
        "comm_status":   f_comm,
        "rescue_status": f_rescue,
    }
    requests = get_all_requests(filters)

    map_col, ctrl_col = st.columns([1.4, 0.6])

    # ── Folium Map ────────────────────────────────────────────
    with map_col:
        st.subheader("🗺️ Live Incident Map")
        m = folium.Map(
            location=[22.5, 80.0],
            zoom_start=5,
            tiles="CartoDB dark_matter",
        )
        for r in requests:
            color = PRIORITY_COLORS.get(r["priority"], "#888888")
            popup_html = f"""
            <div style="font-family:sans-serif;min-width:200px;">
                <b style="color:{color}">{r['id']}</b><br>
                Category: {r['category']}<br>
                Priority: {r['priority'].capitalize()}<br>
                People: {r['people_affected']}<br>
                Comm: {r['comm_status']}<br>
                Rescue: {r['rescue_status']}
            </div>
            """
            folium.CircleMarker(
                location=[r["latitude"], r["longitude"]],
                radius=10 if r["priority"] == "critical" else 7,
                color=color,
                fill=True,
                fill_opacity=0.85,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{r['id']} | {r['priority'].upper()}",
            ).add_to(m)

        st_folium(m, width=None, height=460, returned_objects=[])

    # ── Control Panel ─────────────────────────────────────────
    with ctrl_col:
        st.subheader("⚙️ Dispatch Controls")

        if not requests:
            st.info("No requests match current filters.")
        else:
            req_ids = [r["id"] for r in requests]
            sel_id = st.selectbox("Select SOS Request", req_ids)
            sel    = next((r for r in requests if r["id"] == sel_id), None)

            if sel:
                st.markdown(f"""
                <div style="background:#131B2E;border:1px solid #1E3A5F;border-radius:8px;padding:12px;margin:8px 0;">
                    <b>Category:</b> {sel['category']}<br>
                    <b>Priority:</b> {priority_badge(sel['priority'])}<br>
                    <b>Comm:</b> {comm_badge(sel['comm_status'])}<br>
                    <b>Rescue:</b> {rescue_badge(sel['rescue_status'])}<br>
                    <b>People:</b> {sel['people_affected']}<br>
                    <b>Loc:</b> {sel['latitude']:.4f}, {sel['longitude']:.4f}
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**🚁 Assign Team**")
                teams = get_teams()
                avail = [t for t in teams if t["status"] == "available"]
                if avail:
                    team_map  = {t["name"]: t["id"] for t in avail}
                    sel_team  = st.selectbox("Available Teams", list(team_map.keys()))
                    assign_note = st.text_input("Assignment Notes", placeholder="Dispatch instructions...")
                    if st.button("✅ Assign Team", use_container_width=True):
                        assign_team(sel_id, team_map[sel_team], assign_note)
                        st.success(f"{sel_team} assigned to {sel_id}")
                        st.rerun()
                else:
                    st.warning("No teams currently available.")

                st.markdown("**🔄 Update Rescue Status**")
                new_status = st.selectbox("New Status", RESCUE_STATUSES,
                                          index=RESCUE_STATUSES.index(sel["rescue_status"]))
                upd_note = st.text_input("Update Notes", placeholder="Progress update...")
                if st.button("🔄 Update Status", use_container_width=True):
                    update_rescue_status(sel_id, new_status, upd_note)
                    st.success(f"Status updated to '{new_status}'")
                    st.rerun()

                # ── Comm Log ──────────────────────────────────
                with st.expander("📡 Communication Log"):
                    logs = get_comm_logs(sel_id)
                    if logs:
                        for log in logs:
                            st.markdown(f"""
                            <div style="border-left:3px solid #00D4FF;padding:4px 8px;margin:4px 0;">
                                <small style="color:#8BA4C8">{log['timestamp']}</small><br>
                                <b>{log['event']}</b> via {log.get('channel','—')}<br>
                                <small>{log.get('notes','')}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption("No logs yet.")

    # ── Requests Table ────────────────────────────────────────
    st.subheader("📋 All Filtered Requests")
    if requests:
        rows = []
        for r in requests:
            rows.append({
                "ID":       r["id"],
                "Category": r["category"],
                "Priority": priority_badge(r["priority"]),
                "Comm":     comm_badge(r["comm_status"]),
                "Rescue":   rescue_badge(r["rescue_status"]),
                "Team":     r.get("assigned_team") or "—",
                "People":   r["people_affected"],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No requests found with current filters.")

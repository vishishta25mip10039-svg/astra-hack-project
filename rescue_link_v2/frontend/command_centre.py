"""Command centre: incident map, request triage and team dispatch."""

import json
from html import escape
from statistics import mean

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from backend.sos import get_all_requests, get_comm_logs
from backend.rescue import get_teams, assign_team, update_rescue_status, get_recommended_teams
from backend.db import seed_demo_data
from utils.helpers import (
    CATEGORIES, PRIORITY_COLORS, page_header, section_heading,
    status_badge_html, priority_badge, comm_badge, rescue_badge,
    score_badge_html, triage_breakdown_chips_html,
)

RESCUE_STATUSES = ["open", "assigned", "in_progress", "resolved"]



def _build_attention_queue(requests: list) -> list:
    """Return unresolved incidents that currently need an operator action.

    This list is independent of Command Centre filters so pending or
    unassigned incidents cannot be hidden by the map filter.
    """
    attention_items = []

    for request in requests:
        rescue_status = str(request.get("rescue_status", "open")).lower()
        comm_status = str(request.get("comm_status", "pending")).lower()
        priority = str(request.get("priority", "low")).lower()
        assigned_team = request.get("assigned_team")
        score = int(request.get("priority_score") or 0)

        if rescue_status == "resolved":
            continue

        is_unassigned = rescue_status == "open" and not assigned_team
        is_pending = comm_status == "pending"
        reasons = []

        if is_pending:
            reasons.append("Awaiting transmission")

        if is_unassigned:
            if priority == "critical":
                reasons.append("Critical incident · no team assigned")
            elif priority == "high":
                reasons.append("High-priority incident · no team assigned")
            else:
                reasons.append("No rescue team assigned")

        if not reasons:
            continue

        if is_unassigned and priority == "critical":
            urgency = 0
        elif is_pending and priority == "critical":
            urgency = 1
        elif is_pending:
            urgency = 2
        elif is_unassigned and priority == "high":
            urgency = 3
        else:
            urgency = 4

        attention_items.append({
            "request": request,
            "reasons": reasons,
            "urgency": urgency,
            "score": score,
            "is_pending": is_pending,
            "is_unassigned": is_unassigned,
        })

    attention_items.sort(
        key=lambda item: (
            item["urgency"],
            -item["score"],
            str(item["request"].get("created_at") or ""),
        )
    )
    return attention_items


def _render_attention_queue(all_requests: list) -> None:
    """Render a cross-filter Needs attention queue with direct incident review."""
    items = _build_attention_queue(all_requests)
    pending_count = sum(item["is_pending"] for item in items)
    unassigned_count = sum(item["is_unassigned"] for item in items)
    critical_count = sum(
        item["is_unassigned"]
        and str(item["request"].get("priority", "")).lower() == "critical"
        for item in items
    )

    section_heading(
        "Needs attention",
        "Incidents requiring an operator action. This list is not affected by map filters.",
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Needs attention", len(items))
    metric_cols[1].metric("Awaiting transmission", pending_count)
    metric_cols[2].metric("Unassigned", unassigned_count)
    metric_cols[3].metric("Critical · unassigned", critical_count)

    if not items:
        with st.container(border=True):
            st.markdown("**Nothing needs attention right now.**")
            st.caption(
                "There are no unresolved incidents waiting for transmission "
                "or a rescue team assignment."
            )
        return

    visible_items = items[:6]
    for item in visible_items:
        request = item["request"]
        request_id = str(request.get("id", "Unknown request"))
        category = str(request.get("category", "Emergency"))
        priority = str(request.get("priority", "low")).upper()
        score = item["score"]
        people = int(request.get("people_affected") or 1)
        reason_text = " · ".join(item["reasons"])

        with st.container(border=True):
            info_col, action_col = st.columns([5, 1])
            with info_col:
                st.markdown(f"**{request_id} · {category}**")
                st.caption(
                    f"{priority} · {score}/100 · {people} "
                    f"{'person' if people == 1 else 'people'} affected"
                )
                st.markdown(f"**Action:** {reason_text}")
                st.caption(
                    f"Transmission: {comm_badge(request.get('comm_status', 'pending'))}"
                    f"  |  Response: {rescue_badge(request.get('rescue_status', 'open'))}"
                )
            with action_col:
                if st.button(
                    "Review",
                    key=f"cc_attention_review_{request_id}",
                    use_container_width=True,
                ):
                    # Clear filters so the incident is visible in the
                    # dispatch panel even if a map filter had hidden it.
                    for filter_key in (
                        "cc_category", "cc_priority", "cc_comm", "cc_rescue"
                    ):
                        st.session_state[filter_key] = "All"

                    st.session_state["cc_selected_request_id"] = request_id
                    st.session_state["cc_incident_picker"] = (
                        f"{request_id} · {score}pts ({priority}) - {category}"
                    )
                    st.rerun()

    if len(items) > len(visible_items):
        st.caption(
            f"Showing the {len(visible_items)} most urgent items of {len(items)}. "
            "Resolve or assign incidents to clear them from this queue."
        )


def _build_tactical_map(requests: list, teams: list, selected_req: dict = None, nearest_team: dict = None) -> folium.Map:
    """Build tactical geospatial map showing both active incidents and rescue responder units."""
    if requests:
        center = [
            mean(float(item["latitude"]) for item in requests),
            mean(float(item["longitude"]) for item in requests),
        ]
    else:
        center = [23.5, 78.5]

    map_view = folium.Map(
        location=center,
        zoom_start=5 if not requests else 6,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # 1. Plot Rescue Teams (Base units)
    for team in teams:
        t_lat = team.get("latitude")
        t_lon = team.get("longitude")
        if t_lat and t_lon:
            is_avail = (team.get("status") == "available")
            team_color = "#2563EB" if is_avail else "#9333EA"
            status_text = "READY TO DISPATCH" if is_avail else f"ON MISSION ({team.get('current_assignment') or 'Active'})"
            popup_html = (
                f"<div style='font-family:sans-serif;min-width:180px'>"
                f"<strong>🛡️ {escape(team['name'])}</strong><br>"
                f"<span style='color:{team_color};font-weight:700;font-size:11px'>{status_text}</span><br>"
                f"Base: {escape(team.get('base_location', 'HQ'))}<br>"
                f"Specialty: {escape(team.get('specialty', 'Disaster Relief'))}<br>"
                f"Contact: {escape(team.get('contact', 'Emergency Net'))}"
                f"</div>"
            )
            folium.Marker(
                location=[float(t_lat), float(t_lon)],
                popup=folium.Popup(popup_html, max_width=280),
                tooltip=f"🛡️ {team['name']} ({team['base_location']})",
                icon=folium.Icon(color="blue" if is_avail else "purple", icon="shield", prefix="fa"),
            ).add_to(map_view)

    # 2. Plot Incidents
    for request in requests:
        priority = request["priority"].lower()
        score = request.get("priority_score", 0)
        color = PRIORITY_COLORS.get(priority, "#758092")
        is_sel = (selected_req and selected_req.get("id") == request.get("id"))
        
        popup_text = (
            f"<div style='font-family:sans-serif;min-width:190px'>"
            f"<strong>🚨 {escape(str(request['id']))}</strong><br>"
            f"<strong>{escape(str(request['category']))}</strong><br>"
            f"Triage Score: <strong>{score}/100 ({priority.upper()})</strong><br>"
            f"People trapped/affected: {int(request['people_affected'])}<br>"
            f"Comms route: {escape(comm_badge(request['comm_status']))}<br>"
            f"Status: {escape(rescue_badge(request['rescue_status']))}"
            f"</div>"
        )
        folium.CircleMarker(
            location=[float(request["latitude"]), float(request["longitude"])],
            radius=12 if is_sel else (9 if priority == "critical" else 7),
            color="#1E293B" if is_sel else color,
            weight=3 if is_sel else 2,
            fill=True,
            fill_color=color,
            fill_opacity=0.88,
            popup=folium.Popup(popup_text, max_width=270),
            tooltip=f"{request['id']} · {score}/100 ({priority.title()})",
        ).add_to(map_view)

    # 3. Draw proximity vector between selected incident and recommended nearest team
    if selected_req and nearest_team and nearest_team.get("latitude") and nearest_team.get("longitude"):
        points = [
            [float(selected_req["latitude"]), float(selected_req["longitude"])],
            [float(nearest_team["latitude"]), float(nearest_team["longitude"])]
        ]
        folium.PolyLine(
            locations=points,
            color="#2563EB",
            weight=3,
            dash_array="6, 8",
            tooltip=f"Nearest Unit: {nearest_team['name']} ({nearest_team.get('distance_km', '')} km)",
        ).add_to(map_view)

    if len(requests) > 1:
        bounds = [
            [float(item["latitude"]), float(item["longitude"])]
            for item in requests
        ]
        map_view.fit_bounds(bounds, padding=(30, 30))
    return map_view


def show() -> None:
    page_header(
        "Operations Command Centre",
        "Geospatial emergency triage, automated nearest-team proximity matching and rescue dispatch.",
        "ASTRA 2026 / DOMAIN 03 · DISASTER OPERATIONS",
    )

    all_requests = get_all_requests()
    _render_attention_queue(all_requests)

    with st.expander("Filter & Search Incidents", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            category_filter = st.selectbox("Category", ["All"] + CATEGORIES, key="cc_category")
        with c2:
            priority_filter = st.selectbox(
                "Priority Tier", ["All", "critical", "high", "moderate", "low"], key="cc_priority"
            )
        with c3:
            comm_filter = st.selectbox(
                "Transmission Channel", ["All", "pending", "synchronised"], key="cc_comm"
            )
        with c4:
            rescue_filter = st.selectbox(
                "Response Status", ["All"] + RESCUE_STATUSES, key="cc_rescue"
            )

    requests = get_all_requests({
        "category": category_filter,
        "priority": priority_filter,
        "comm_status": comm_filter,
        "rescue_status": rescue_filter,
    })
    teams = get_teams()

    map_col, detail_col = st.columns([1.35, 0.95], gap="large")

    # Select active incident for dispatch
    selected = None
    recommended_teams = []
    nearest_unit = None

    if requests:
        request_options = {
            f"{r['id']} · {r.get('priority_score', 0)}pts ({r['priority'].upper()}) - {r['category']}": r['id']
            for r in requests
        }
        selected_label = list(request_options.keys())[0]
        # Allow user to pick from dropdown
        chosen_id = st.session_state.get("cc_selected_request_id", requests[0]["id"])
        # Find default index
        def_idx = 0
        for i, (lbl, rid) in enumerate(request_options.items()):
            if rid == chosen_id:
                def_idx = i
                break
        
        selected_id = list(request_options.values())[def_idx]
        selected = next((item for item in requests if item["id"] == selected_id), requests[0])
        if selected:
            recommended_teams = get_recommended_teams(float(selected["latitude"]), float(selected["longitude"]))
            nearest_unit = recommended_teams[0] if recommended_teams else None

    with map_col:
        section_heading("Tactical Incident & Responder Map", f"Displaying {len(requests)} incident(s) and {len(teams)} rescue unit bases.")
        st_folium(
            _build_tactical_map(requests, teams, selected, nearest_unit),
            width=None,
            height=490,
            returned_objects=[],
            key="command_centre_map",
        )

        st.markdown(
            f"""
            <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:6px">
              <span style="font-size:11px;font-weight:700;color:#576E82">Incidents:</span>
              {status_badge_html('🔴 Critical (70-100)', 'critical')}
              {status_badge_html('🟠 High (40-69)', 'high')}
              {status_badge_html('🟡 Moderate (20-39)', 'moderate')}
              {status_badge_html('🟢 Low (0-19)', 'low')}
              <span style="font-size:11px;font-weight:700;color:#576E82;margin-left:10px">Responders:</span>
              <span style="font-size:11px;font-weight:700;color:#2563EB">🛡️ Blue: Ready</span>
              <span style="font-size:11px;font-weight:700;color:#9333EA">🛡️ Purple: Deployed</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with detail_col:
        section_heading("Dispatch & Triage Manager", "Slide 6: Automated nearest-team dispatch.")
        if not requests:
            with st.container(border=True):
                st.markdown("**Incident Queue Standing By**")
                if all_requests:
                    st.caption("No requests match the current filters. Clear filters to view incidents.")
                else:
                    st.caption("No recorded incidents. Load the demo scenario to test team assignment.")
                    if st.button("Load Demo Scenario", key="cc_load_sample", type="primary", use_container_width=True):
                        seed_demo_data()
                        st.rerun()
        else:
            selected_pick = st.selectbox(
                "Select incident to review",
                list(request_options.keys()),
                index=def_idx,
                key="cc_incident_picker",
            )
            picked_id = request_options[selected_pick]
            if picked_id != selected["id"]:
                st.session_state["cc_selected_request_id"] = picked_id
                st.rerun()

            level = selected["priority"].lower()
            score = selected.get("priority_score", 0)
            breakdown = json.loads(selected.get("score_breakdown") or "{}") if selected.get("score_breakdown") else {}

            with st.container(border=True):
                st.markdown(f"### {selected['category']}")
                st.caption(f"ID: `{selected['id']}` · Created: {selected['created_at'][:19].replace('T', ' ')} UTC")
                st.markdown(
                    f"{score_badge_html(score, level)} "
                    f"{status_badge_html(rescue_badge(selected['rescue_status']), 'low')} "
                    f"{status_badge_html(comm_badge(selected['comm_status']), 'low' if selected['comm_status'] == 'synchronised' else 'critical')}",
                    unsafe_allow_html=True,
                )
                if breakdown:
                    st.markdown(f"<div style='margin-top:6px'>{triage_breakdown_chips_html(breakdown)}</div>", unsafe_allow_html=True)

                st.markdown(f"**People Affected**: {selected['people_affected']} citizens")
                st.markdown(f"**Coordinates**: {selected['latitude']:.4f}°N, {selected['longitude']:.4f}°E")
                if selected.get("description"):
                    st.markdown(f"**Field Details**: {selected['description']}")

            # Nearest Team Recommendation (Slide 6 Step 5)
            with st.container(border=True):
                st.markdown("**Slide 6: Nearest Team Dispatch**")
                if nearest_unit and nearest_unit.get("status") == "available":
                    st.markdown(
                        f"""
                        <div style="background:#EBF5FF;border:1px solid #BFDBFE;border-radius:8px;padding:10px 12px;margin-bottom:10px">
                          <div style="color:#1D4ED8;font-size:10px;font-weight:800;letter-spacing:.06em">🎯 RECOMMENDED NEAREST UNIT</div>
                          <div style="color:#1E3A8A;font-size:13px;font-weight:700">{nearest_unit['name']} ({nearest_unit['base_location']})</div>
                          <div style="color:#3B82F6;font-size:11px">Distance: <strong>{nearest_unit.get('distance_km')} km</strong> · Est. Transit: <strong>~{nearest_unit.get('eta_minutes')} mins</strong></div>
                          <div style="color:#475569;font-size:11px">Specialty: {nearest_unit.get('specialty', '')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if selected["rescue_status"] == "open":
                        if st.button(f"⚡ Instant Dispatch: {nearest_unit['name']}", type="primary", use_container_width=True):
                            assign_team(selected["id"], nearest_unit["id"], "Auto-dispatched via nearest proximity match.")
                            st.success(f"{nearest_unit['name']} dispatched!")
                            st.rerun()

                # Manual team selection form
                avail_list = [t for t in recommended_teams if t["status"] == "available"]
                if avail_list:
                    team_opts = {
                        f"{t['name']} ({t['base_location']} · {t.get('distance_km', '—')} km)": t["id"]
                        for t in avail_list
                    }
                    with st.form("manual_assign_form"):
                        chosen_team_label = st.selectbox("Assign available rescue unit", list(team_opts.keys()))
                        dispatch_note = st.text_input("Operational dispatch orders", placeholder="e.g. Deploy inflatable boats")
                        assign_btn = st.form_submit_button("Assign Selected Team", use_container_width=True)
                        if assign_btn:
                            assign_team(selected["id"], team_opts[chosen_team_label], dispatch_note)
                            st.success(f"Team assigned to {selected['id']}.")
                            st.rerun()
                else:
                    st.caption("No rescue teams currently available for assignment.")

                # Status update buttons
                st.markdown("**Update Operational Status**")
                s_c1, s_c2 = st.columns(2)
                with s_c1:
                    if st.button("Mark In Progress", use_container_width=True):
                        update_rescue_status(selected["id"], "in_progress", "Team arrived on site.")
                        st.rerun()
                with s_c2:
                    if st.button("Mark Resolved ✅", type="secondary", use_container_width=True):
                        update_rescue_status(selected["id"], "resolved", "Evacuation completed. Citizens safe.")
                        st.success("Incident marked resolved! Team released to available pool.")
                        st.rerun()

    section_heading("Incident Master Register", "Ranked strictly by Priority Score (Slide 7: 'Critical first, always').")
    if requests:
        rows = [{
            "Request ID": item["id"],
            "Score": f"{item.get('priority_score', 0)}/100",
            "Priority": priority_badge(item["priority"]),
            "Category": item["category"],
            "Casualties": item["people_affected"],
            "Transmission": comm_badge(item["comm_status"]),
            "Route": item.get("sync_channel") or ("Pending Local" if item["comm_status"] == "pending" else "Terrestrial"),
            "Status": rescue_badge(item["rescue_status"]),
            "Assigned Unit": item.get("assigned_team") or "—",
        } for item in requests]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.caption("No requests match the selected filters.")


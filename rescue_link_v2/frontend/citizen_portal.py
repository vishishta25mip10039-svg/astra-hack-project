"""Citizen-facing SOS submission form with Slide 7 Priority Engine and delivery receipt."""

import json
import streamlit as st
from datetime import datetime

from backend.sos import create_sos, get_all_requests, get_comm_logs, calculate_priority_score
from backend.connectivity import can_transmit
from backend.voice_service import transcribe_and_translate, save_voice_note, attach_voice_note, SUPPORTED_LANGUAGES
from utils.helpers import (
    CATEGORIES, SEVERITIES, validate_coordinates,
    page_header, section_heading, status_badge_html,
    priority_badge, comm_badge, rescue_badge,
    score_badge_html, triage_breakdown_chips_html, transmission_seal_html,
)


DEMO_LOCATIONS = {
    "Custom Coordinates": (23.2599, 77.4126),
    "Patna, Bihar (Flood Zone)": (25.5941, 85.1376),
    "Kedarnath, Uttarakhand (Landslide)": (30.7346, 79.0669),
    "Bhopal, MP (Industrial/Urban)": (23.2599, 77.4126),
    "Leh, Ladakh (High Altitude)": (34.1526, 77.5771),
    "Kolkata, WB (Coastal Zone)": (22.5726, 88.3639),
    "Mumbai, MH (Urban Flood Area)": (19.0760, 72.8777),
}


EVENT_LABELS = {
    "SOS_CREATED": "Request recorded in local SQLite cache",
    "STORE_AND_FORWARD_PENDING": "Offline queue hold: awaiting satellite/terrestrial link",
    "SYNCHRONISED": "Burst transmission verified",
    "TEAM_ASSIGNED": "Rescue team assigned by Command Centre",
    "STATUS_UPDATE": "Operational response status updated",
}


def _format_event_time(value: str) -> str:
    """Format stored UTC timestamps for the receipt timeline."""
    if not value:
        return "Time unavailable"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.strftime("%d %b %Y · %H:%M:%S UTC")
    except (TypeError, ValueError):
        return str(value)


def _render_delivery_timeline(request_id: str, comm_status: str) -> None:
    """Show the actual communication events stored for one SOS request."""
    logs = list(reversed(get_comm_logs(request_id)))
    if not logs:
        st.caption("No delivery events have been recorded yet.")
        return

    for log in logs:
        event = str(log.get("event", ""))
        label = EVENT_LABELS.get(event, event.replace("_", " ").title())
        channel = log.get("channel") or "local system"
        left, right = st.columns([1.4, 1])
        with left:
            st.markdown(f"**{label}**")
            st.caption(_format_event_time(log.get("timestamp", "")))
        with right:
            st.caption(f"Route: {channel}")
            if log.get("notes"):
                st.caption(f"Note: {log['notes']}")

    if comm_status == "pending":
        st.warning("Saved locally in SQLite. Waiting for satellite burst link or terrestrial recovery before synchronisation.")
    else:
        st.success("Synchronisation confirmed. Full store-and-forward receipt verified.")


def _apply_location_preset() -> None:
    preset = st.session_state.get("citizen_location_preset", "Custom Coordinates")
    latitude, longitude = DEMO_LOCATIONS.get(preset, (23.2599, 77.4126))
    if preset != "Custom Coordinates":
        st.session_state["citizen_latitude"] = latitude
        st.session_state["citizen_longitude"] = longitude


def show() -> None:
    page_header(
        "Citizen SOS Portal",
        "Record an emergency request. Zero data loss: if networks are down, requests queue locally and auto-sync via satellite.",
        "ASTRA 2026 / CITIZEN SOS DISPATCH",
    )

    can_send, channel = can_transmit()
    if can_send:
        st.info(f"🌐 **Network Uplink Available**: Connected via **{channel.replace('_', ' ').title()}**. Requests will transmit immediately to Command Centre.")
    else:
        st.warning("⚡ **Network Blackout Active**: No cellular or internet towers detected. Requests will be stored safely in local SQLite and auto-sync when a link restores.")

    form_col, recent_col = st.columns([1.15, 0.85], gap="large")

    with form_col:
        section_heading("Submit an emergency", "Slide 7 Intelligent Triage Engine evaluates priority in < 1 second.")

        if "citizen_location_preset" not in st.session_state:
            st.session_state["citizen_location_preset"] = "Custom Coordinates"
        if "citizen_latitude" not in st.session_state:
            st.session_state["citizen_latitude"] = DEMO_LOCATIONS["Custom Coordinates"][0]
        if "citizen_longitude" not in st.session_state:
            st.session_state["citizen_longitude"] = DEMO_LOCATIONS["Custom Coordinates"][1]

        with st.container(border=True):
            preset = st.selectbox(
                "Quick demo location preset",
                list(DEMO_LOCATIONS.keys()),
                key="citizen_location_preset",
                on_change=_apply_location_preset,
            )

            # We use reactive inputs outside a nested form to give judges a LIVE preview of Slide 7 Priority Scoring
            c_cat, c_sev = st.columns(2)
            with c_cat:
                category = st.selectbox("Emergency category", CATEGORIES, key="sos_cat")
            with c_sev:
                severity = st.selectbox("Reported severity", SEVERITIES, index=1, key="sos_sev")

            c_ppl, c_dan = st.columns([1, 1.2])
            with c_ppl:
                people = st.number_input("People affected", min_value=1, max_value=500, value=2, key="sos_people")
            with c_dan:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                danger = st.checkbox("Immediate danger to life (+40 pts)", value=True, key="sos_danger")

            c_med, c_com = st.columns(2)
            with c_med:
                is_medical = st.checkbox(
                    "Medical emergency / severe injuries (+30 pts)",
                    value=(category == "Medical Assistance"),
                    key="sos_medical",
                )
            with c_com:
                comm_cutoff = st.checkbox(
                    "Communication cut off / cannot call (+10 pts)",
                    value=(not can_send),
                    key="sos_comms",
                )

            # Live Priority Engine preview (Slide 7)
            triage_preview = calculate_priority_score(
                category=category,
                severity=severity,
                people_affected=people,
                immediate_danger=danger,
                is_medical=is_medical,
                comm_cutoff=comm_cutoff,
            )

            st.markdown(
                f"""
                <div class="rl-triage-box">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                    <span style="font-size:10px;font-weight:800;color:#576E82;letter-spacing:.08em;text-transform:uppercase">
                      ⚡ Slide 7 Priority Engine Live Preview
                    </span>
                    {score_badge_html(triage_preview['score'], triage_preview['tier'])}
                  </div>
                  <div style="font-size:12px;color:#203244;font-weight:600">
                    Response Target: <span style="color:{triage_preview['color']}">{triage_preview['action']}</span> ({triage_preview['queue']})
                  </div>
                  <div style="margin-top:6px">
                    {triage_breakdown_chips_html(triage_preview['breakdown'])}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            description = st.text_area(
                "Incident description",
                placeholder="Describe trapped persons, flood levels, injuries, or hazards...",
                height=80,
                key="sos_desc",
            )

            st.markdown("**Incident GPS coordinates**")
            coord1, coord2 = st.columns(2)
            with coord1:
                latitude = st.number_input(
                    "Latitude", min_value=-90.0, max_value=90.0,
                    format="%.4f", step=0.0001, key="citizen_latitude",
                )
            with coord2:
                longitude = st.number_input(
                    "Longitude", min_value=-180.0, max_value=180.0,
                    format="%.4f", step=0.0001, key="citizen_longitude",
                )

            st.markdown("**🎙️ Voice SOS (Hindi / Gujarati / Marathi / English)**")
            st.caption("Record the emergency in your own language. The system keeps the original audio and transcript, then prepares an English translation for responders.")
            voice_language = st.selectbox(
                "Spoken language",
                list(SUPPORTED_LANGUAGES.keys()),
                key="voice_language",
            )
            voice_audio = st.audio_input(
                "Record your emergency message",
                sample_rate=16000,
                key="voice_sos_audio",
            )
            if st.button("Transcribe and translate voice", key="voice_transcribe", use_container_width=True):
                if voice_audio is None:
                    st.warning("Record a voice message first.")
                else:
                    try:
                        with st.spinner("Transcribing and translating your message..."):
                            audio_bytes = voice_audio.getvalue()
                            voice_result = transcribe_and_translate(audio_bytes, voice_language)
                            note_id = save_voice_note(
                                audio_bytes,
                                voice_result,
                                getattr(voice_audio, "type", None) or "audio/wav",
                            )
                            st.session_state["voice_result"] = voice_result
                            st.session_state["voice_note_id"] = note_id
                        st.success("Voice message processed and saved. Review the transcript below, then submit the SOS.")
                    except Exception as exc:
                        st.error(str(exc))

            voice_result = st.session_state.get("voice_result")
            if voice_result:
                with st.expander("Review voice transcript and English translation", expanded=True):
                    st.caption(f"Input language: {voice_result['language']}")
                    st.markdown("**Original transcript**")
                    st.write(voice_result["transcript"])
                    st.markdown("**English translation for responders**")
                    st.write(voice_result["translated_text"])
                    if voice_audio is not None:
                        st.audio(voice_audio)

            submitted = st.button("Transmit SOS Request", type="primary", use_container_width=True)

        if submitted:
            st.session_state.pop("last_sos_result", None)
            valid, error = validate_coordinates(latitude, longitude)
            if not valid:
                st.error(error)
            else:
                voice_result = st.session_state.get("voice_result")
                incident_description = description.strip()
                if voice_result:
                    translated_details = voice_result["translated_text"].strip()
                    incident_description = (
                        incident_description + "\n\nVoice message (English translation): " + translated_details
                        if incident_description else "Voice message (English translation): " + translated_details
                    )
                result = create_sos(
                    category=category,
                    latitude=latitude,
                    longitude=longitude,
                    people_affected=people,
                    severity=severity,
                    immediate_danger=danger,
                    description=incident_description,
                    is_medical=is_medical,
                    comm_cutoff=comm_cutoff,
                )
                note_id = st.session_state.get("voice_note_id")
                if note_id:
                    attach_voice_note(note_id, result["id"])
                    st.session_state.pop("voice_note_id", None)
                    st.session_state.pop("voice_result", None)
                st.session_state["last_sos_result"] = result
                st.session_state["last_sos_category"] = category
                st.rerun()

        result = st.session_state.get("last_sos_result")
        if result:
            level = result["priority"].lower()
            with st.container(border=True):
                st.markdown("### Emergency Request Logged")
                st.markdown(
                    f"{score_badge_html(result['priority_score'], level)} "
                    f"{status_badge_html(comm_badge(result['comm_status']), 'low' if result['comm_status'] == 'synchronised' else 'critical')}",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    transmission_seal_html(
                        result.get("hash_fingerprint", result["id"]),
                        result["channel"],
                        result["comm_status"],
                    ),
                    unsafe_allow_html=True,
                )
                if result["comm_status"] == "pending":
                    st.info("💡 **Store-and-Forward Active**: Proceed to the **Connectivity** page or use the sidebar controls to simulate satellite link and burst-sync this request!")
                else:
                    st.success("✅ **Delivered to Command Centre**: Incident is now visible on the tactical map for rescue team assignment.")
                with st.expander("View transmission audit trail", expanded=True):
                    _render_delivery_timeline(result["id"], result["comm_status"])

    with recent_col:
        section_heading("Local incident register", "Requests logged in this terminal.")
        recent = get_all_requests()[:8]
        if not recent:
            st.info("No requests yet. Submitted SOS requests will appear here.")
        else:
            for request in recent:
                level = request["priority"].lower()
                score = request.get("priority_score", 0)
                breakdown = json.loads(request.get("score_breakdown") or "{}") if request.get("score_breakdown") else {}
                with st.container(border=True):
                    top, badge_col = st.columns([1.2, 0.9])
                    with top:
                        st.markdown(f"**{request['category']}**")
                        st.caption(f"`{request['id']}` · {request['people_affected']} people")
                    with badge_col:
                        st.markdown(
                            score_badge_html(score, level),
                            unsafe_allow_html=True,
                        )
                    st.markdown(
                        f"{status_badge_html(rescue_badge(request['rescue_status']), 'low')} "
                        f"{status_badge_html(comm_badge(request['comm_status']), 'low' if request['comm_status'] == 'synchronised' else 'critical')}",
                        unsafe_allow_html=True,
                    )
                    if breakdown:
                        st.markdown(triage_breakdown_chips_html(breakdown), unsafe_allow_html=True)
                    with st.expander("Audit timeline"):
                        _render_delivery_timeline(request["id"], request["comm_status"])


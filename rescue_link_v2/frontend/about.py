"""Project overview, Slide alignment, architecture and team credentials."""

import streamlit as st
from utils.helpers import page_header, section_heading


def show() -> None:
    page_header(
        "Mission, Architecture & Domain Alignment",
        "ASTRA 2026: Space-Based Disaster Management & Satellite Communication.",
        "TEAM AURORA · ANTERIX CLUB · VIT BHOPAL",
    )

    # Slide 2: Domain Alignment & Opportunity vs Gap
    section_heading("Our Domains & The Gap We Fill (Slide 2)", "Bridging space infrastructure and ground-level disaster survival.")
    left, right = st.columns(2, gap="large")
    with left, st.container(border=True):
        st.markdown("### 🛰️ The Space Opportunity")
        st.markdown(
            "- **ISRO's NavIC**: India has its own satellite constellation, independent of mobile towers.\n"
            "- **26+ Disaster Types**: Cyclones, floods, landslides and earthquakes strike India yearly.\n"
            "- **Resilient Satellite Links**: Ground mobile towers collapse within hours; satellites remain in orbit.\n"
            "- **Untapped Ground SOS**: NDMA & ISRO have space infrastructure, but zero last-mile tools use it.\n"
            "- **72-Hour Golden Window**: Satellite is the only reliable lifeline during critical survival hours."
        )
    with right, st.container(border=True):
        st.markdown("### ❌ The Gap Rescue Link Fills")
        st.markdown(
            "- **No Offline Storage**: Existing tools fail instantly if internet drops; requests vanish.\n"
            "- **No Intelligent Priority**: The loudest caller gets help, not the most critical casualty.\n"
            "- **Zero Last-Mile Satellite Use**: Satellite connectivity has stayed on paper, never in citizen hands.\n"
            "- **Requests Disappear**: No retry, no local buffer, no store-and-forward fallback.\n"
            "- **Responders Flying Blind**: No live map, no triage queue, no visibility on who needs help where."
        )

    # Slide 8: Ground Impact Comparison
    section_heading("What Changes on the Ground (Slide 8)")
    col_a, col_b = st.columns(2, gap="large")
    with col_a, st.container(border=True):
        st.markdown("### ❌ Without Rescue Link")
        st.markdown(
            "• **Network down** ➔ SOS request lost forever\n\n"
            "• **No priority** ➔ Random, chaotic dispatch\n\n"
            "• **Responders blind** ➔ No map, no queue, no data\n\n"
            "• **Resource mismatch** ➔ 3 teams sent to one site, zero to another\n\n"
            "• **No accountability** ➔ No records, no audit learning"
        )
    with col_b, st.container(border=True):
        st.markdown("### ✅ With Rescue Link")
        st.markdown(
            "• **Offline queue** ➔ Zero data loss, ever (SQLite)\n\n"
            "• **0–100 scoring** ➔ Critical first, always (Slide 7 Engine)\n\n"
            "• **Live tactical map** ➔ Real-time geospatial incident visibility\n\n"
            "• **Nearest team dispatch** ➔ Teams dispatched by proximity and severity\n\n"
            "• **Full audit log** ➔ Cryptographic delivery receipts and analytics"
        )

    # Slide 7 Priority Engine Reference
    section_heading("Priority Engine Architecture (Slide 7)", "Algorithmic scoring formula evaluated in < 1 second.")
    with st.container(border=True):
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.metric("Immediate Danger", "+40 pts", "Life-threatening hazard")
        with p2:
            st.metric("Medical Emergency", "+30 pts", "Severe injury or illness")
        with p3:
            st.metric("Mass Casualty", "+20 pts", "Multiple citizens trapped")
        with p4:
            st.metric("Comms Cut Off", "+10 pts", "Unable to self-rescue / no towers")
        st.caption("Max Score: 100 ➔ Auto Critical. Tiers: Critical (70-100), High (40-69), Moderate (20-39), Low (0-19).")

    # Future Roadmap (Slide 8) & Prototype Scope
    section_heading("Prototype Scope & Future Roadmap (Slide 8)")
    f1, f2 = st.columns(2, gap="large")
    with f1, st.container(border=True):
        st.markdown("**Implemented Prototype Features**")
        st.markdown(
            "- 3-Layer Communication Simulation (Cellular, Internet, Satellite Fallback)\n"
            "- Local SQLite Store-and-Forward persistent queue\n"
            "- Slide 7 Intelligent Triage Engine (0-100 real-time scoring)\n"
            "- Tactical geospatial command map with proximity vectors\n"
            "- Automated nearest-team dispatch calculation\n"
            "- Official cryptographic Delivery Receipts with JSON export\n"
            "- Mission analytics with zero data loss proof"
        )
    with f2, st.container(border=True):
        st.markdown("**Future Production Roadmap**")
        st.markdown(
            "- **Live ISRO NavIC / GSAT API**: Direct transponder messaging hardware integration\n"
            "- **SMS-based SOS**: Micro-packet delivery without mobile internet\n"
            "- **NDMA Real-Time Data Feed**: National disaster management agency data sync\n"
            "- **Starlink Direct-to-Cell Fallback**: Global low-earth-orbit constellation link\n"
            "- **Field Mesh Networking**: LoRa / BLE peer-to-peer citizen hops"
        )
        st.caption("Presentation Note: Satellite connectivity is a software simulation in this prototype.")

    # Team & Credentials
    section_heading("Team Aurora · VIT Bhopal")
    team_cols = st.columns(3)
    team = [
        ("Member 1", "Backend & Architecture", "Database schema, Slide 7 Priority Engine, Store-and-Forward sync"),
        ("Member 2", "Frontend & Geospatial", "Streamlit UI, Tactical Leaflet map, live forms and delivery receipts"),
        ("Member 3", "Integration & Pitch Demo", "Application routing, simulation presets, analytics and deployment"),
    ]
    for col, (member, role, responsibility) in zip(team_cols, team):
        with col, st.container(border=True):
            st.markdown(f"**{member}**")
            st.caption(role)
            st.write(responsibility)

    st.caption("ASTRA 2026 · ANTERiX Club · VIT Bhopal · Team Aurora")


"""Shared visual system and display helpers for RESCUE LINK."""

from html import escape
from typing import Optional

import streamlit as st


COLORS = {
    "background": "#EEF3F7",
    "surface": "#FFFFFF",
    "text": "#203244",
    "muted": "#718295",
    "brand": "#477F9E",
    "brand_hover": "#376B88",
    "navy": "#142A3E",
    "navy_light": "#203F57",
    "cyan": "#79BDD6",
    "border": "#DCE5EC",
    "critical": "#C84D50",
    "high": "#D77B42",
    "moderate": "#B38D3D",
    "low": "#44856D",
}

PRIORITY_COLORS = {
    "critical": COLORS["critical"],
    "high": COLORS["high"],
    "moderate": COLORS["moderate"],
    "low": COLORS["low"],
}

PRIORITY_SOFT_COLORS = {
    "critical": ("#F9E9E9", "#A53E43"),
    "high": ("#FBF0E8", "#A65E31"),
    "moderate": ("#F6F1E4", "#876A2B"),
    "low": ("#EAF3EE", "#347154"),
}

COMM_STATUS_BADGE = {
    "pending": "Pending transmission",
    "synchronised": "Synchronised",
}

RESCUE_STATUS_BADGE = {
    "open": "Open",
    "assigned": "Assigned",
    "in_progress": "In progress",
    "resolved": "Resolved",
}

CATEGORIES = [
    "Flood", "Earthquake", "Landslide", "Fire",
    "Medical Assistance", "Structural Collapse", "Other",
]

SEVERITIES = ["Low", "Moderate", "High", "Critical"]


def apply_theme() -> None:
    """Apply a light operations UI with a restrained satellite/space identity."""
    st.markdown(
        """
        <style>
        :root, html, body {
            color-scheme: light !important;
            --rl-bg: #EEF3F7;
            --rl-surface: #FFFFFF;
            --rl-text: #203244;
            --rl-muted: #718295;
            --rl-brand: #477F9E;
            --rl-brand-hover: #376B88;
            --rl-navy: #142A3E;
            --rl-border: #DCE5EC;
            --rl-radius: 11px;
            --primary-color: #477F9E;
            --primaryColor: #477F9E;
        }

        html, body, [class*="css"] {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--rl-text);
        }
        [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background: var(--rl-bg) !important;
            color: var(--rl-text) !important;
        }
        [data-testid="stHeader"] { background: rgba(238,243,247,.94) !important; }
        [data-testid="stMainBlockContainer"] {
            max-width: 1500px;
            padding-top: 1.45rem;
            padding-bottom: 3rem;
        }

        /* Matte midnight sidebar: the main workspace remains light. */
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
            background: #142A3E !important;
            border-right: 1px solid #244158 !important;
        }
        [data-testid="stSidebar"] > div:first-child { padding: 1.15rem .9rem 1rem; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #AFC0CD !important;
        }
        [data-testid="stSidebar"] hr { border-color: #2B465B !important; }
        .rl-brand {
            display:flex; align-items:center; gap:11px; padding:7px 5px 25px;
        }
        .rl-brand-mark {
            width:39px; height:39px; border-radius:11px; display:grid; place-items:center;
            background:#25465E; color:#A9D7E8; font-size:12px; font-weight:800;
            letter-spacing:-.03em; border:1px solid #3B6179;
        }
        .rl-brand-name { color:#F4F8FB; font-size:15px; line-height:1.25; font-weight:720; }
        .rl-brand-subtitle { margin-top:3px; color:#9FB3C3; font-size:11px; }
        .rl-sidebar-label {
            padding:0 8px 8px; color:#7994A9; font-size:10px; font-weight:750;
            letter-spacing:.13em;
        }
        .rl-sidebar-section-gap { height:19px; }
        .rl-sidebar-footer {
            margin-top:26px; padding:14px 8px 0; border-top:1px solid #2B465B;
            color:#9FB3C3; font-size:11px; line-height:1.55;
        }
        .rl-footer-dot {
            display:inline-block; width:7px; height:7px; margin-right:7px;
            border-radius:50%; background:#75B99D; vertical-align:1px;
        }
        .rl-footer-location { padding-left:14px; color:#7892A5; }
        .rl-sidebar-status {
            margin:12px 3px 4px; padding:12px 12px 10px; border:1px solid #2D4A60;
            border-radius:9px; background:#1A354B;
        }
        .rl-sidebar-status-title {
            color:#87A3B7; font-size:9px; font-weight:750; letter-spacing:.13em;
            text-transform:uppercase; margin-bottom:8px;
        }
        .rl-sidebar-status-row {
            display:flex; justify-content:space-between; gap:8px; align-items:center;
            color:#DFEAF1; font-size:11px; padding:3px 0;
        }
        .rl-sidebar-status-value { color:#A9C5D5; font-weight:650; text-align:right; }

        [data-testid="stSidebar"] [role="radiogroup"] { gap:4px; }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            min-height:38px; padding:7px 10px; border-radius:8px; color:#C6D4DE !important;
            font-size:13px; transition:background 120ms ease,color 120ms ease;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background:#203F56 !important; color:#FFFFFF !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background:#24465E !important; color:#FFFFFF !important; font-weight:680;
            box-shadow:inset 3px 0 0 #79BDD6;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child { display:none !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label svg,
        [data-testid="stSidebar"] [role="radiogroup"] label input[type="radio"] { display:none !important; }

        /* Global type, page structure and cards. */
        h1, h2, h3 { color:var(--rl-text) !important; letter-spacing:-.025em; }
        h1 { font-weight:720; }
        h2, h3 { font-weight:660; }
        p, li { color:#4F6172; }
        small, [data-testid="stCaptionContainer"] { color:var(--rl-muted); }
        hr { border-color:var(--rl-border); }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background:#FFFFFF !important; border:1px solid #DCE5EC !important;
            border-radius:11px !important; box-shadow:0 2px 8px rgba(24,48,68,.035) !important;
        }
        [data-testid="stExpander"] {
            background:#FFFFFF !important; border:1px solid #DCE5EC !important;
            border-radius:10px !important;
        }
        [data-testid="stMetric"] { padding:3px 0; }
        [data-testid="stMetricLabel"] { color:#718295 !important; font-size:12px; }
        [data-testid="stMetricValue"] {
            color:#203244 !important; font-size:28px; font-weight:720; letter-spacing:-.04em;
        }

        /* Dark mission banner with a quiet orbital diagram, not a sci-fi cockpit. */
        .rl-page-header {
            position:relative; overflow:hidden; isolation:isolate;
            min-height:132px; margin:0 0 23px; padding:22px 27px;
            border-radius:13px; border:1px solid #29465D;
            background:
                radial-gradient(circle at 78% 22%, rgba(109,178,208,.18), transparent 27%),
                linear-gradient(112deg,#142A3E 0%,#1A344A 58%,#22465D 100%);
            box-shadow:0 4px 14px rgba(17,42,62,.10);
        }
        .rl-page-header:before {
            content:""; position:absolute; inset:0; z-index:-1; opacity:.24;
            background-image:radial-gradient(rgba(190,220,235,.8) .7px,transparent .7px);
            background-size:23px 23px; mask-image:linear-gradient(90deg,transparent 30%,#000 100%);
        }
        .rl-page-header:after {
            content:""; position:absolute; z-index:-1; width:185px; height:185px;
            right:8.5%; top:-86px; border:1px solid rgba(151,205,225,.25);
            border-radius:50%; transform:rotate(-23deg); box-shadow:0 0 0 22px rgba(126,184,208,.035),0 0 0 46px rgba(126,184,208,.025);
        }
        .rl-page-header-copy { position:relative; z-index:2; max-width:72%; }
        .rl-page-eyebrow {
            color:#91C5D9 !important; font-size:9px; font-weight:800;
            letter-spacing:.16em; text-transform:uppercase; margin-bottom:8px;
        }
        .rl-page-title {
            color:#F7FAFC !important; font-size:27px; font-weight:730;
            letter-spacing:-.035em; line-height:1.2;
        }
        .rl-page-subtitle { color:#C2D2DD !important; font-size:13px; margin-top:7px; line-height:1.55; }
        .rl-orbit-art { position:absolute; width:210px; height:125px; right:2.5%; top:4px; z-index:1; opacity:.85; }
        .rl-orbit-art svg { width:100%; height:100%; overflow:visible; }
        .rl-section-title { color:#203244 !important; font-size:16px; font-weight:700; margin:3px 0 3px; }
        .rl-section-note { color:#718295 !important; font-size:12px; margin-bottom:10px; }
        .rl-status {
            display:inline-block; padding:4px 8px; border-radius:5px;
            font-size:11px; font-weight:700; line-height:1.2; white-space:nowrap;
        }
        .rl-muted { color:#718295; }

        /* Slide 7 Triage Engine visual badges */
        .rl-triage-pill {
            display:inline-flex; align-items:center; gap:6px; padding:4px 9px;
            border-radius:6px; font-size:11px; font-weight:750; letter-spacing:-.01em;
        }
        .rl-triage-chip {
            display:inline-block; padding:3px 7px; margin:2px 3px 2px 0;
            border-radius:4px; font-size:10px; font-weight:700; letter-spacing:.02em;
        }
        .rl-triage-box {
            background:#F8FAFC; border:1px solid #DCE5EC; border-radius:9px;
            padding:12px 14px; margin-bottom:12px;
        }
        .rl-receipt-card {
            background:#FFFFFF; border:1px solid #CDDCE5; border-radius:12px;
            padding:20px 24px; position:relative; box-shadow:0 3px 12px rgba(20,42,62,.04);
            font-family:Inter, -apple-system, sans-serif;
        }
        .rl-receipt-seal {
            border:2px dashed #477F9E; border-radius:8px; padding:8px 14px;
            display:inline-block; color:#23526E; font-size:11px; font-weight:800;
            letter-spacing:.08em; text-transform:uppercase; background:#F0F6F9;
        }
        .rl-telemetry-grid {
            display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr));
            gap:10px; margin-top:10px;
        }
        .rl-telemetry-stat {
            background:#F6FAFC; border:1px solid #DCE5EC; border-radius:7px;
            padding:8px 10px;
        }
        .rl-telemetry-label { color:#75899A; font-size:9px; font-weight:750; text-transform:uppercase; }
        .rl-telemetry-val { color:#1E3346; font-size:13px; font-weight:700; margin-top:2px; }

        /* Overview-specific cards and timeline. */
        .rl-network-card {
            height:100%; background:#FFFFFF; border:1px solid #DCE5EC; border-radius:10px;
            padding:13px 14px; box-shadow:0 2px 8px rgba(24,48,68,.025);
        }
        .rl-network-label { color:#74889A; font-size:9px; font-weight:800; letter-spacing:.13em; }
        .rl-network-name { color:#24394B; font-size:14px; font-weight:700; margin:5px 0 7px; }
        .rl-network-description { color:#8191A0; font-size:11px; line-height:1.4; margin-top:8px; }
        .rl-empty-state {
            padding:22px 20px; border:1px dashed #BCCBD6; border-radius:10px;
            background:linear-gradient(135deg,#F8FBFD,#F0F5F8);
        }
        .rl-empty-kicker { color:#6D94A9; font-size:9px; font-weight:800; letter-spacing:.14em; }
        .rl-empty-title { color:#263D50; font-size:17px; font-weight:700; margin:7px 0 5px; }
        .rl-empty-copy { color:#718295; font-size:12px; line-height:1.55; max-width:540px; }
        .rl-incident-line {
            display:flex; align-items:center; justify-content:space-between; gap:12px;
            padding:11px 0; border-bottom:1px solid #EAF0F4;
        }
        .rl-incident-line:last-child { border-bottom:0; }
        .rl-incident-title { color:#263A4C; font-size:13px; font-weight:680; }
        .rl-incident-meta { color:#8191A0; font-size:10px; margin-top:3px; }
        .rl-step {
            display:flex; gap:11px; padding:9px 0; align-items:flex-start;
            border-bottom:1px solid #EAF0F4;
        }
        .rl-step:last-child { border-bottom:0; }
        .rl-step-number {
            flex:0 0 25px; height:25px; display:grid; place-items:center; border-radius:7px;
            color:#477F9E; background:#EAF2F6; font-size:10px; font-weight:800;
        }
        .rl-step-title { color:#2C4052; font-size:12px; font-weight:700; }
        .rl-step-copy { color:#7B8C9B; font-size:11px; line-height:1.45; margin-top:2px; }

        /* Buttons: one muted-blue action colour across the product. */
        .stButton > button, .stDownloadButton > button {
            min-height:38px; border-radius:8px; border:1px solid #D6E0E8;
            background:#FFFFFF; color:#294054; font-size:13px; font-weight:650;
            box-shadow:none; transition:background 120ms ease,border-color 120ms ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            border-color:#AFC3D1; background:#F4F8FA; color:#203244;
        }
        button[kind="primary"], button[data-testid="baseButton-primary"],
        button[data-testid="stBaseButton-primary"], [data-testid="stFormSubmitButton"] button,
        .stFormSubmitButton button {
            background:#477F9E !important; background-color:#477F9E !important;
            border:1px solid #477F9E !important; color:#FFFFFF !important;
            border-radius:8px !important; box-shadow:none !important;
        }
        button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover,
        [data-testid="stFormSubmitButton"] button:hover, .stFormSubmitButton button:hover {
            background:#376B88 !important; border-color:#376B88 !important; color:#FFFFFF !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            background:#24465E !important; border:1px solid #365A72 !important;
            color:#E7F0F5 !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover { background:#2D536D !important; }

        /* Streamlit + BaseWeb controls are explicitly kept in light mode. */
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div,
        [data-baseweb="base-input"] {
            background:#FFFFFF !important; background-color:#FFFFFF !important;
            color:#203244 !important; border:1px solid #D6E0E8 !important;
            border-radius:8px !important; box-shadow:none !important;
        }
        [data-baseweb="select"] input, [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea, [data-baseweb="select"] div[class*="singleValue"],
        [data-baseweb="select"] div[class*="valueContainer"], input, textarea {
            color:#203244 !important; -webkit-text-fill-color:#203244 !important;
            background:transparent !important; caret-color:#477F9E !important;
        }
        [data-baseweb="select"] svg { color:#667E90 !important; }
        [data-baseweb="popover"], [data-baseweb="popover"] > div,
        [data-baseweb="popover"] [role="listbox"],
        [data-baseweb="popover"] [role="option"] {
            background:#FFFFFF !important; color:#203244 !important;
        }
        [data-baseweb="popover"] [role="option"]:hover { background:#EDF3F7 !important; }
        [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label,
        .stCheckbox label, .stRadio label, .stToggle label {
            color:#4F6172 !important;
        }
        [data-testid="stToggle"] [role="switch"],
        [data-testid="stToggle"] button[role="switch"],
        [data-testid="stToggleSwitch"] button[role="switch"] {
            background:#AAB8C3 !important;
            border-color:#AAB8C3 !important;
        }
        [data-testid="stToggle"] [role="switch"][aria-checked="true"],
        [data-testid="stToggle"] button[role="switch"][aria-checked="true"],
        [data-testid="stToggleSwitch"] button[role="switch"][aria-checked="true"] {
            background:#477F9E !important;
            border-color:#477F9E !important;
        }
        input[type="checkbox"] { accent-color:#477F9E !important; }

        /* Higher-specificity BaseWeb selectors for Streamlit form widgets.
           These prevent dark OS/browser styling from leaking into controls. */
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
        [data-testid="stNumberInput"] [data-baseweb="input"] > div,
        [data-testid="stTextInput"] [data-baseweb="input"] > div,
        [data-testid="stTextArea"] [data-baseweb="textarea"] > div,
        [data-testid="stDateInput"] [data-baseweb="input"] > div {
            background:#FFFFFF !important;
            background-color:#FFFFFF !important;
            border:1px solid #C9D6E0 !important;
            border-radius:8px !important;
            box-shadow:none !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] *,
        [data-testid="stMultiSelect"] [data-baseweb="select"] *,
        [data-testid="stNumberInput"] [data-baseweb="input"] *,
        [data-testid="stTextInput"] [data-baseweb="input"] *,
        [data-testid="stTextArea"] [data-baseweb="textarea"] *,
        [data-testid="stDateInput"] [data-baseweb="input"] * {
            color:#203244 !important;
            -webkit-text-fill-color:#203244 !important;
        }
        [data-testid="stTextArea"] textarea,
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input {
            background:#FFFFFF !important;
            background-color:#FFFFFF !important;
            color:#203244 !important;
            -webkit-text-fill-color:#203244 !important;
            caret-color:#477F9E !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] svg,
        [data-testid="stMultiSelect"] [data-baseweb="select"] svg {
            color:#667E90 !important;
            fill:#667E90 !important;
        }
        [data-testid="stFormSubmitButton"] button[kind="primary"] *,
        [data-testid="stFormSubmitButton"] button[data-testid*="primary"] *,
        button[kind="primary"] *, button[data-testid="baseButton-primary"] * {
            color:#FFFFFF !important;
            -webkit-text-fill-color:#FFFFFF !important;
        }
        /* Final widget surface override: keep every citizen form field light,
           including BaseWeb's nested control layers in dark-OS environments. */
        [data-testid="stSelectbox"] [data-baseweb="select"],
        [data-testid="stNumberInput"] [data-baseweb="input"],
        [data-testid="stTextInput"] [data-baseweb="input"],
        [data-testid="stTextArea"] [data-baseweb="textarea"] {
            color-scheme: light !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
        [data-testid="stNumberInput"] [data-baseweb="input"] > div,
        [data-testid="stNumberInput"] [data-baseweb="input"] > div > div,
        [data-testid="stTextInput"] [data-baseweb="input"] > div,
        [data-testid="stTextArea"] [data-baseweb="textarea"] > div {
            background:#FFFFFF !important;
            background-color:#FFFFFF !important;
            color:#203244 !important;
            border-color:#C9D6E0 !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] input,
        [data-testid="stNumberInput"] [data-baseweb="input"] input,
        [data-testid="stTextInput"] [data-baseweb="input"] input,
        [data-testid="stTextArea"] [data-baseweb="textarea"] textarea {
            background:transparent !important;
            background-color:transparent !important;
            color:#203244 !important;
            -webkit-text-fill-color:#203244 !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] input::placeholder,
        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {
            color:#8493A0 !important;
            -webkit-text-fill-color:#8493A0 !important;
            opacity:1 !important;
        }
        [data-testid="stNumberInput"] button {
            background:#F3F7F9 !important;
            color:#35536A !important;
            border-color:#D6E1E8 !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] svg {
            color:#60798B !important;
            fill:#60798B !important;
        }
        [data-baseweb="popover"] [role="option"] {
            background:#FFFFFF !important;
            color:#203244 !important;
        }
        [data-baseweb="popover"] [role="option"][aria-selected="true"] {
            background:#EAF2F6 !important;
            color:#203244 !important;
        }
        [data-testid="stCheckbox"] label,
        [data-testid="stCheckbox"] label p {
            color:#40576A !important;
        }

        [data-testid="stAlert"] {
            background:#EDF4F7 !important; border:1px solid #D7E5EC !important;
            border-left:3px solid #77A9C0 !important; border-radius:9px !important;
            color:#31495B !important;
        }
        [data-testid="stAlert"] p, [data-testid="stAlert"] span,
        [data-testid="stAlert"] div { color:#31495B !important; }
        [data-testid="stAlert"] svg { color:#477F9E !important; fill:#477F9E !important; }

        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border:1px solid #DCE5EC; border-radius:10px; overflow:hidden;
        }
        [data-testid="stPlotlyChart"] { background:transparent; }
        [data-testid="stFolium"] iframe { border-radius:10px; }
        [data-testid="stDecoration"] { display:none; }

        @media (max-width:760px) {
            [data-testid="stMainBlockContainer"] { padding:1rem 1rem 2rem; }
            .rl-page-header { padding:19px 18px; min-height:120px; }
            .rl-page-header-copy { max-width:100%; }
            .rl-page-title { font-size:23px; }
            .rl-orbit-art { opacity:.18; right:-8%; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: Optional[str] = None,
                eyebrow: Optional[str] = None) -> None:
    """Render a mission-style page header with a subtle orbital illustration."""
    eyebrow_html = f'<div class="rl-page-eyebrow">{escape(eyebrow)}</div>' if eyebrow else ""
    subtitle_html = f'<div class="rl-page-subtitle">{escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="rl-page-header">
          <div class="rl-page-header-copy">
            {eyebrow_html}
            <div class="rl-page-title">{escape(title)}</div>
            {subtitle_html}
          </div>
          <div class="rl-orbit-art" aria-hidden="true">
            <svg viewBox="0 0 230 135" role="presentation">
              <ellipse cx="126" cy="67" rx="91" ry="34" fill="none" stroke="#83C5DD" stroke-opacity=".50" stroke-width="1.2" transform="rotate(-19 126 67)"/>
              <ellipse cx="126" cy="67" rx="72" ry="55" fill="none" stroke="#83C5DD" stroke-opacity=".24" stroke-width="1" transform="rotate(31 126 67)"/>
              <circle cx="126" cy="67" r="22" fill="#77B8D0" fill-opacity=".12" stroke="#9AD4E7" stroke-opacity=".7"/>
              <path d="M113 67h26M126 54v26" stroke="#9AD4E7" stroke-opacity=".65" stroke-width=".8"/>
              <circle cx="49" cy="42" r="3.5" fill="#B9E5F2"/>
              <circle cx="197" cy="84" r="4" fill="#8BD0E5"/>
              <circle cx="126" cy="67" r="4" fill="#D6F1F8"/>
              <path d="M188 22l2 4 4 2-4 2-2 4-2-4-4-2 4-2z" fill="#C8E8F2" fill-opacity=".8"/>
              <path d="M66 99l1.5 3 3 1.5-3 1.5-1.5 3-1.5-3-3-1.5 3-1.5z" fill="#C8E8F2" fill-opacity=".55"/>
            </svg>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title: str, note: Optional[str] = None) -> None:
    """Render a small section heading."""
    note_html = f'<div class="rl-section-note">{escape(note)}</div>' if note else ""
    st.markdown(
        f'<div class="rl-section-title">{escape(title)}</div>{note_html}',
        unsafe_allow_html=True,
    )


def status_badge_html(label: str, level: str = "low") -> str:
    """Return a compact, accessible status badge as HTML."""
    background, foreground = PRIORITY_SOFT_COLORS.get(
        level.lower(), ("#EEF1F4", "#536173")
    )
    return (
        f'<span class="rl-status" style="background:{background};color:{foreground}">'
        f'{escape(label)}</span>'
    )


def priority_badge(priority: str) -> str:
    return priority.replace("_", " ").title()


def comm_badge(status: str) -> str:
    return COMM_STATUS_BADGE.get(status, status.replace("_", " ").title())


def rescue_badge(status: str) -> str:
    return RESCUE_STATUS_BADGE.get(status, status.replace("_", " ").title())


def validate_coordinates(lat: float, lon: float) -> tuple:
    """Return (is_valid, error_message) for latitude/longitude."""
    if not (-90 <= lat <= 90):
        return False, "Latitude must be between -90 and 90."
    if not (-180 <= lon <= 180):
        return False, "Longitude must be between -180 and 180."
    return True, ""


def score_badge_html(score: int, tier: str) -> str:
    """Return a styled score pill for Slide 7 triage engine."""
    background, foreground = PRIORITY_SOFT_COLORS.get(tier.lower(), ("#EEF1F4", "#536173"))
    tier_label = tier.replace("_", " ").title()
    return (
        f'<span class="rl-triage-pill" style="background:{background};color:{foreground};border:1px solid {foreground}33">'
        f'<span style="font-weight:800;font-size:12px">{score}/100</span> · {tier_label}</span>'
    )


def triage_breakdown_chips_html(breakdown: dict) -> str:
    """Render small score component chips showing math breakdown (+40, +30, etc)."""
    if not breakdown:
        return ""
    chips = []
    if breakdown.get("danger"):
        chips.append('<span class="rl-triage-chip" style="background:#FDE8E8;color:#9B2C2C">+40 Danger</span>')
    if breakdown.get("medical"):
        chips.append('<span class="rl-triage-chip" style="background:#FEF3C7;color:#92400E">+30 Medical</span>')
    if breakdown.get("people"):
        chips.append('<span class="rl-triage-chip" style="background:#EBF5FF;color:#1E40AF">+20 Casualties</span>')
    if breakdown.get("comms"):
        chips.append('<span class="rl-triage-chip" style="background:#EDE9FE;color:#5B21B6">+10 Comms Cutoff</span>')
    if breakdown.get("base"):
        chips.append(f'<span class="rl-triage-chip" style="background:#F1F5F9;color:#475569">+{breakdown["base"]} Baseline</span>')
    return "".join(chips)


def transmission_seal_html(fingerprint: str, channel: str, comm_status: str) -> str:
    """Render an official digital store-and-forward receipt verification badge."""
    is_sync = (comm_status == "synchronised")
    bg = "#EAF3EE" if is_sync else "#FEF3C7"
    color = "#236B46" if is_sync else "#92400E"
    label = "STORE & FORWARD VERIFIED UPLINK" if is_sync else "LOCAL SQLITE QUEUE · PENDING SYNC"
    channel_display = channel.replace("_", " ").title() if channel else "Local Offline Cache"
    return f"""
    <div style="background:{bg};border:1px solid {color}44;border-radius:8px;padding:10px 14px;margin:8px 0">
      <div style="color:{color};font-size:10px;font-weight:800;letter-spacing:.08em">{label}</div>
      <div style="color:#1E3346;font-size:12px;font-weight:700;margin-top:2px">Receipt ID: <code>{escape(fingerprint or "N/A")}</code></div>
      <div style="color:#576B7C;font-size:11px;margin-top:2px">Channel Route: <strong>{escape(channel_display)}</strong> · Loss Rate: <strong>0.0%</strong></div>
    </div>
    """


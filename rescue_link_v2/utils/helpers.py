"""Shared visual system and display helpers for RESCUE LINK (Cosmic Dark Mode)."""

from html import escape
from typing import Optional

import streamlit as st


COLORS = {
    "background": "#F2EFE6",
    "surface": "#F2EFE6",
    "text": "#182B36",
    "muted": "#182B36",
    "brand": "#182B36",
    "brand_hover": "#182B36",
    "navy": "#182B36",
    "navy_light": "#182B36",
    "cyan": "#182B36",
    "border": "#182B36",
    "critical": "#182B36",
    "high": "#182B36",
    "moderate": "#182B36",
    "low": "#182B36",
}

PRIORITY_COLORS = {
    "critical": COLORS["critical"],
    "high": COLORS["high"],
    "moderate": COLORS["moderate"],
    "low": COLORS["low"],
}

PRIORITY_SOFT_COLORS = {
    "critical": ("#F2EFE6", "#182B36"),
    "high": ("#F2EFE6", "#182B36"),
    "moderate": ("#F2EFE6", "#182B36"),
    "low": ("#F2EFE6", "#182B36"),
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
    """Apply a sleek, space-grade Dark Operations UI with neon orbital accents."""
    st.markdown(
        """
        <style>
        :root, html, body {
            color-scheme: dark !important;
            --rl-bg: #070B14;
            --rl-surface: #0E1626;
            --rl-text: #F1F5F9;
            --rl-muted: #94A3B8;
            --rl-brand: #38BDF8;
            --rl-brand-hover: #0EA5E9;
            --rl-navy: #0A0F1D;
            --rl-border: #1E2D42;
            --rl-radius: 11px;
            --primary-color: #38BDF8;
            --primaryColor: #38BDF8;
        }

        html, body, [class*="css"] {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--rl-text) !important;
        }
        [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background: #070B14 !important;
            color: #F1F5F9 !important;
        }
        [data-testid="stHeader"] {
            background: rgba(7, 11, 20, 0.85) !important;
            backdrop-filter: blur(10px) !important;
        }
        [data-testid="stMainBlockContainer"] {
            max-width: 1500px;
            padding-top: 1.35rem;
            padding-bottom: 3rem;
        }

        /* Matte deep-space obsidian sidebar */
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
            background: #050811 !important;
            border-right: 1px solid #131E30 !important;
        }
        [data-testid="stSidebar"] > div:first-child { padding: 1.15rem .9rem 1rem; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #94A3B8 !important;
        }
        [data-testid="stSidebar"] hr { border-color: #1A283D !important; }
        .rl-brand {
            display:flex; align-items:center; gap:11px; padding:7px 5px 22px;
        }
        .rl-brand-mark {
            width:39px; height:39px; border-radius:11px; display:grid; place-items:center;
            background:linear-gradient(135deg, #0284C7, #0369A1);
            color:#F0F9FF; font-size:13px; font-weight:800;
            box-shadow:0 0 14px rgba(56, 189, 248, 0.4);
            border:1px solid #38BDF8;
        }
        .rl-brand-name { color:#F8FAFC; font-size:16px; line-height:1.25; font-weight:750; letter-spacing:-.02em; }
        .rl-brand-subtitle { margin-top:3px; color:#38BDF8; font-size:11px; font-weight:600; }
        .rl-sidebar-label {
            padding:0 8px 8px; color:#64748B; font-size:10px; font-weight:750;
            letter-spacing:.13em;
        }
        .rl-sidebar-section-gap { height:18px; }
        .rl-sidebar-footer {
            margin-top:24px; padding:14px 8px 0; border-top:1px solid #1E2D42;
            color:#94A3B8; font-size:11px; line-height:1.55;
        }
        .rl-footer-dot {
            display:inline-block; width:7px; height:7px; margin-right:7px;
            border-radius:50%; background:#10B981; vertical-align:1px;
            box-shadow:0 0 8px #10B981;
        }
        .rl-footer-location { padding-left:14px; color:#64748B; font-size:10px; }
        .rl-sidebar-status {
            margin:12px 3px 4px; padding:12px 12px 10px; border:1px solid #1E2D42;
            border-radius:9px; background:#0B111E;
        }
        .rl-sidebar-status-title {
            color:#64748B; font-size:9px; font-weight:750; letter-spacing:.13em;
            text-transform:uppercase; margin-bottom:8px;
        }
        .rl-sidebar-status-row {
            display:flex; justify-content:space-between; gap:8px; align-items:center;
            color:#CBD5E1; font-size:11px; padding:3px 0;
        }
        .rl-sidebar-status-value { color:#38BDF8; font-weight:700; text-align:right; font-family:monospace; }

        [data-testid="stSidebar"] [role="radiogroup"] { gap:4px; }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            min-height:38px; padding:7px 10px; border-radius:8px; color:#94A3B8 !important;
            font-size:13px; transition:background 120ms ease,color 120ms ease;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background:#111B2B !important; color:#F8FAFC !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background:#0E1E36 !important; color:#38BDF8 !important; font-weight:700;
            box-shadow:inset 3px 0 0 #38BDF8;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child { display:none !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label svg,
        [data-testid="stSidebar"] [role="radiogroup"] label input[type="radio"] { display:none !important; }

        /* Global dark card structure */
        h1, h2, h3 { color:#F8FAFC !important; letter-spacing:-.025em; }
        h1 { font-weight:750; }
        h2, h3 { font-weight:680; }
        p, li { color:#CBD5E1; }
        small, [data-testid="stCaptionContainer"] { color:#8899AC !important; }
        hr { border-color:#1E2D42 !important; }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background:rgba(14, 22, 38, 0.85) !important;
            border:1px solid #1E2D42 !important;
            border-radius:11px !important;
            box-shadow:0 4px 20px rgba(0, 0, 0, 0.45) !important;
            backdrop-filter:blur(12px) !important;
        }
        [data-testid="stExpander"] {
            background:rgba(14, 22, 38, 0.85) !important;
            border:1px solid #1E2D42 !important;
            border-radius:10px !important;
        }
        [data-testid="stMetric"] { padding:3px 0; }
        [data-testid="stMetricLabel"] { color:#94A3B8 !important; font-size:12px; font-weight:600; }
        [data-testid="stMetricValue"] {
            color:#F8FAFC !important; font-size:28px; font-weight:750; letter-spacing:-.04em;
        }

        /* Cosmic Mission Banner */
        .rl-page-header {
            position:relative; overflow:hidden; isolation:isolate;
            min-height:128px; margin:0 0 20px; padding:20px 25px;
            border-radius:13px; border:1px solid #1E2D42;
            background:
                radial-gradient(circle at 78% 22%, rgba(56,189,248,.22), transparent 28%),
                radial-gradient(circle at 20% 70%, rgba(168,85,247,.12), transparent 35%),
                linear-gradient(115deg,#070C18 0%,#0D1629 55%,#14223E 100%);
            box-shadow:0 4px 22px rgba(0,0,0,.5);
        }
        .rl-page-header:before {
            content:""; position:absolute; inset:0; z-index:-1; opacity:.22;
            background-image:radial-gradient(rgba(56,189,248,.7) .7px,transparent .7px);
            background-size:23px 23px; mask-image:linear-gradient(90deg,transparent 25%,#000 100%);
        }
        .rl-page-header:after {
            content:""; position:absolute; z-index:-1; width:185px; height:185px;
            right:8.5%; top:-86px; border:1px solid rgba(56,189,248,.35);
            border-radius:50%; transform:rotate(-23deg); box-shadow:0 0 0 22px rgba(56,189,248,.04),0 0 0 46px rgba(56,189,248,.02);
        }
        .rl-page-header-copy { position:relative; z-index:2; max-width:72%; }
        .rl-page-eyebrow {
            color:#38BDF8 !important; font-size:9px; font-weight:800;
            letter-spacing:.16em; text-transform:uppercase; margin-bottom:8px;
            text-shadow:0 0 8px rgba(56, 189, 248, 0.4);
        }
        .rl-page-title {
            color:#F8FAFC !important; font-size:26px; font-weight:750;
            letter-spacing:-.035em; line-height:1.2;
        }
        .rl-page-subtitle { color:#94A3B8 !important; font-size:13px; margin-top:6px; line-height:1.55; }
        .rl-orbit-art { position:absolute; width:210px; height:125px; right:2.5%; top:4px; z-index:1; opacity:.85; }
        .rl-orbit-art svg { width:100%; height:100%; overflow:visible; }
        .rl-section-title { color:#F8FAFC !important; font-size:16px; font-weight:700; margin:3px 0 3px; }
        .rl-section-note { color:#8899AC !important; font-size:12px; margin-bottom:10px; }
        .rl-status {
            display:inline-block; padding:4px 9px; border-radius:5px;
            font-size:11px; font-weight:700; line-height:1.2; white-space:nowrap;
        }
        .rl-muted { color:#8899AC; }

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
            background:#0B111E; border:1px solid #1E2D42; border-radius:9px;
            padding:12px 14px; margin-bottom:12px;
        }
        .rl-receipt-card {
            background:#0E1626; border:1px solid #1E2D42; border-radius:12px;
            padding:20px 24px; position:relative; box-shadow:0 4px 20px rgba(0,0,0,.4);
            font-family:Inter, -apple-system, sans-serif;
            color:#F1F5F9;
        }
        .rl-receipt-seal {
            border:2px dashed #38BDF8; border-radius:8px; padding:8px 14px;
            display:inline-block; color:#38BDF8; font-size:11px; font-weight:800;
            letter-spacing:.08em; text-transform:uppercase; background:rgba(56, 189, 248, 0.08);
        }
        .rl-telemetry-grid {
            display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr));
            gap:10px; margin-top:10px;
        }
        .rl-telemetry-stat {
            background:#0B111E; border:1px solid #1E2D42; border-radius:7px;
            padding:8px 10px;
        }
        .rl-telemetry-label { color:#64748B; font-size:9px; font-weight:750; text-transform:uppercase; }
        .rl-telemetry-val { color:#38BDF8; font-size:13px; font-weight:700; margin-top:2px; font-family:monospace; }

        /* Overview-specific cards and timeline */
        .rl-network-card {
            height:100%; background:#0E1626; border:1px solid #1E2D42; border-radius:10px;
            padding:13px 14px; box-shadow:0 3px 12px rgba(0,0,0,.3);
        }
        .rl-network-label { color:#64748B; font-size:9px; font-weight:800; letter-spacing:.13em; }
        .rl-network-name { color:#F8FAFC; font-size:14px; font-weight:700; margin:5px 0 7px; }
        .rl-network-description { color:#94A3B8; font-size:11px; line-height:1.4; margin-top:8px; }
        .rl-empty-state {
            padding:22px 20px; border:1px dashed #1E2D42; border-radius:10px;
            background:linear-gradient(135deg,#0B111E,#0E1626);
        }
        .rl-empty-kicker { color:#38BDF8; font-size:9px; font-weight:800; letter-spacing:.14em; }
        .rl-empty-title { color:#F8FAFC; font-size:17px; font-weight:700; margin:7px 0 5px; }
        .rl-empty-copy { color:#94A3B8; font-size:12px; line-height:1.55; max-width:540px; }
        .rl-incident-line {
            display:flex; align-items:center; justify-content:space-between; gap:12px;
            padding:11px 0; border-bottom:1px solid #172437;
        }
        .rl-incident-line:last-child { border-bottom:0; }
        .rl-incident-title { color:#F8FAFC; font-size:13px; font-weight:680; }
        .rl-incident-meta { color:#8899AC; font-size:10px; margin-top:3px; }
        .rl-step {
            display:flex; gap:11px; padding:9px 0; align-items:flex-start;
            border-bottom:1px solid #172437;
        }
        .rl-step:last-child { border-bottom:0; }
        .rl-step-number {
            flex:0 0 25px; height:25px; display:grid; place-items:center; border-radius:7px;
            color:#38BDF8; background:#0B1626; font-size:10px; font-weight:800;
            border:1px solid rgba(56, 189, 248, 0.3);
        }
        .rl-step-title { color:#F1F5F9; font-size:12px; font-weight:700; }
        .rl-step-copy { color:#8899AC; font-size:11px; line-height:1.45; margin-top:2px; }

        /* Dark Mode Buttons */
        .stButton > button, .stDownloadButton > button {
            min-height:38px; border-radius:8px; border:1px solid #1E2D42;
            background:#0E1626; color:#E2E8F0; font-size:13px; font-weight:650;
            box-shadow:none; transition:background 120ms ease,border-color 120ms ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            border-color:#38BDF8; background:#142238; color:#38BDF8;
        }
        button[kind="primary"], button[data-testid="baseButton-primary"],
        button[data-testid="stBaseButton-primary"], [data-testid="stFormSubmitButton"] button,
        .stFormSubmitButton button {
            background:linear-gradient(135deg, #0284C7, #0EA5E9) !important;
            background-color:#0284C7 !important;
            border:1px solid #38BDF8 !important; color:#FFFFFF !important;
            border-radius:8px !important; box-shadow:0 0 15px rgba(14, 165, 233, 0.4) !important;
        }
        button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover,
        [data-testid="stFormSubmitButton"] button:hover, .stFormSubmitButton button:hover {
            background:linear-gradient(135deg, #0369A1, #0284C7) !important;
            border-color:#7DD3FC !important; color:#FFFFFF !important;
            box-shadow:0 0 20px rgba(14, 165, 233, 0.6) !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            background:#0B1220 !important; border:1px solid #1E2D42 !important;
            color:#CBD5E1 !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background:#131E33 !important; border-color:#38BDF8 !important; color:#38BDF8 !important;
        }

        /* Streamlit + BaseWeb controls in Dark Mode */
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div,
        [data-baseweb="base-input"] {
            background:#0B111E !important; background-color:#0B111E !important;
            color:#F8FAFC !important; border:1px solid #1E2D42 !important;
            border-radius:8px !important; box-shadow:none !important;
        }
        [data-baseweb="select"] input, [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea, [data-baseweb="select"] div[class*="singleValue"],
        [data-baseweb="select"] div[class*="valueContainer"], input, textarea {
            color:#F8FAFC !important; -webkit-text-fill-color:#F8FAFC !important;
            background:transparent !important; caret-color:#38BDF8 !important;
        }
        [data-baseweb="select"] svg { color:#64748B !important; }
        [data-baseweb="popover"], [data-baseweb="popover"] > div,
        [data-baseweb="popover"] [role="listbox"],
        [data-baseweb="popover"] [role="option"] {
            background:#0B111E !important; color:#F8FAFC !important;
        }
        [data-baseweb="popover"] [role="option"]:hover { background:#131E33 !important; }
        [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label,
        .stCheckbox label, .stRadio label, .stToggle label {
            color:#CBD5E1 !important;
        }
        [data-testid="stToggle"] [role="switch"],
        [data-testid="stToggle"] button[role="switch"],
        [data-testid="stToggleSwitch"] button[role="switch"] {
            background:#334155 !important;
            border-color:#334155 !important;
        }
        [data-testid="stToggle"] [role="switch"][aria-checked="true"],
        [data-testid="stToggle"] button[role="switch"][aria-checked="true"],
        [data-testid="stToggleSwitch"] button[role="switch"][aria-checked="true"] {
            background:#0284C7 !important;
            border-color:#38BDF8 !important;
        }
        input[type="checkbox"] { accent-color:#0284C7 !important; }

        /* Higher-specificity BaseWeb selectors for Dark Mode */
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
        [data-testid="stNumberInput"] [data-baseweb="input"] > div,
        [data-testid="stTextInput"] [data-baseweb="input"] > div,
        [data-testid="stTextArea"] [data-baseweb="textarea"] > div,
        [data-testid="stDateInput"] [data-baseweb="input"] > div {
            background:#0B111E !important;
            background-color:#0B111E !important;
            border:1px solid #1E2D42 !important;
            border-radius:8px !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] *,
        [data-testid="stMultiSelect"] [data-baseweb="select"] *,
        [data-testid="stNumberInput"] [data-baseweb="input"] *,
        [data-testid="stTextInput"] [data-baseweb="input"] *,
        [data-testid="stTextArea"] [data-baseweb="textarea"] *,
        [data-testid="stDateInput"] [data-baseweb="input"] * {
            color:#F8FAFC !important;
            -webkit-text-fill-color:#F8FAFC !important;
        }
        [data-testid="stTextArea"] textarea,
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input {
            background:#0B111E !important;
            background-color:#0B111E !important;
            color:#F8FAFC !important;
            -webkit-text-fill-color:#F8FAFC !important;
            caret-color:#38BDF8 !important;
        }
        [data-testid="stNumberInput"] button {
            background:#111B2B !important;
            color:#94A3B8 !important;
            border-color:#1E2D42 !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] svg {
            color:#64748B !important;
            fill:#64748B !important;
        }
        [data-baseweb="popover"] [role="option"][aria-selected="true"] {
            background:#14243C !important;
            color:#38BDF8 !important;
        }
        [data-testid="stCheckbox"] label,
        [data-testid="stCheckbox"] label p {
            color:#CBD5E1 !important;
        }

        [data-testid="stAlert"] {
            background:#0C172B !important; border:1px solid #1E2D42 !important;
            border-left:3px solid #38BDF8 !important; border-radius:9px !important;
            color:#E2E8F0 !important;
        }
        [data-testid="stAlert"] p, [data-testid="stAlert"] span,
        [data-testid="stAlert"] div { color:#E2E8F0 !important; }
        [data-testid="stAlert"] svg { color:#38BDF8 !important; fill:#38BDF8 !important; }

        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border:1px solid #1E2D42; border-radius:10px; overflow:hidden;
            background:#0E1626;
        }
        [data-testid="stPlotlyChart"] { background:transparent; }
        [data-testid="stFolium"] iframe { border-radius:10px; border:1px solid #1E2D42; }
        [data-testid="stDecoration"] { display:none; }

        @media (max-width:760px) {
            [data-testid="stMainBlockContainer"] { padding:1rem 1rem 2rem; }
            .rl-page-header { padding:18px 16px; min-height:115px; }
            .rl-page-header-copy { max-width:100%; }
            .rl-page-title { font-size:22px; }
            .rl-orbit-art { opacity:.15; right:-8%; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )



    # Two-colour paper-and-ink visual override. Kept separate to preserve page helpers.
    st.markdown(
        """
        <style>
        :root, html, body { color-scheme: light !important; --rl-paper:#F2EFE6; --rl-ink:#182B36; }
        html, body, [class*="css"] { font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important; color:#182B36 !important; }
        [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"] { background:#F2EFE6 !important; color:#182B36 !important; }
        [data-testid="stHeader"] { background:#F2EFE6 !important; border-bottom:1px solid rgba(24,43,54,.16) !important; }
        [data-testid="stMainBlockContainer"] { max-width:1460px; padding-top:1.5rem; padding-bottom:3rem; }
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background:#182B36 !important; border-right:1px solid #182B36 !important; }
        [data-testid="stSidebar"] > div:first-child { padding:1.2rem .95rem 1rem; }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] [data-testid="stCaptionContainer"], [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color:#F2EFE6 !important; }
        [data-testid="stSidebar"] hr { border-color:rgba(242,239,230,.22) !important; }
        .rl-brand-mark { background:#F2EFE6 !important; color:#182B36 !important; border:1px solid #F2EFE6 !important; box-shadow:none !important; border-radius:6px !important; }
        .rl-brand-name { color:#F2EFE6 !important; }
        .rl-brand-subtitle, .rl-sidebar-label, .rl-sidebar-footer, .rl-footer-location { color:rgba(242,239,230,.72) !important; }
        .rl-footer-dot { background:#F2EFE6 !important; box-shadow:none !important; }
        .rl-sidebar-status { background:rgba(242,239,230,.07) !important; border:1px solid rgba(242,239,230,.28) !important; border-radius:6px !important; }
        .rl-sidebar-status-title { color:rgba(242,239,230,.65) !important; }
        .rl-sidebar-status-row, .rl-sidebar-status-value { color:#F2EFE6 !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label { color:rgba(242,239,230,.82) !important; border-radius:5px !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover { background:rgba(242,239,230,.10) !important; color:#F2EFE6 !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background:#F2EFE6 !important; color:#182B36 !important; box-shadow:inset 3px 0 0 #182B36 !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) * { color:#182B36 !important; }
        h1,h2,h3,h4,p,li,label { color:#182B36 !important; }
        small, [data-testid="stCaptionContainer"], [data-testid="stMetricLabel"], .rl-section-note { color:rgba(24,43,54,.72) !important; }
        hr { border-color:rgba(24,43,54,.22) !important; }
        [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stExpander"] { background:#F2EFE6 !important; border:1px solid rgba(24,43,54,.28) !important; border-radius:6px !important; box-shadow:none !important; backdrop-filter:none !important; }
        [data-testid="stMetricValue"] { color:#182B36 !important; font-weight:760 !important; }
        .rl-page-header { background:#182B36 !important; border:1px solid #182B36 !important; border-radius:4px !important; box-shadow:none !important; }
        .rl-page-header:before, .rl-page-header:after { display:none !important; }
        .rl-page-eyebrow { color:rgba(242,239,230,.72) !important; text-shadow:none !important; }
        .rl-page-title, .rl-page-subtitle { color:#F2EFE6 !important; }
        .rl-orbit-art { opacity:.18 !important; }
        .rl-section-title { color:#182B36 !important; }
        .rl-status, .rl-triage-pill, .rl-triage-chip { background:#F2EFE6 !important; color:#182B36 !important; border:1px solid rgba(24,43,54,.42) !important; box-shadow:none !important; border-radius:4px !important; }
        .rl-triage-box, .rl-receipt-card, .rl-telemetry-stat, .rl-network-card, .rl-empty-state { background:#F2EFE6 !important; color:#182B36 !important; border:1px solid rgba(24,43,54,.28) !important; border-radius:6px !important; box-shadow:none !important; }
        .rl-receipt-seal { color:#182B36 !important; border-color:#182B36 !important; background:#F2EFE6 !important; }
        .rl-network-label, .rl-telemetry-label { color:rgba(24,43,54,.68) !important; }
        .rl-network-name, .rl-empty-title, .rl-empty-copy, .rl-incident-title, .rl-incident-meta, .rl-step-title, .rl-step-copy, .rl-telemetry-val { color:#182B36 !important; }
        .rl-incident-line, .rl-step { border-color:rgba(24,43,54,.18) !important; }
        .stButton > button, .stDownloadButton > button { background:#F2EFE6 !important; color:#182B36 !important; border:1px solid #182B36 !important; border-radius:5px !important; box-shadow:none !important; }
        .stButton > button:hover, .stDownloadButton > button:hover { background:#182B36 !important; color:#F2EFE6 !important; border-color:#182B36 !important; }
        button[kind="primary"], button[data-testid="baseButton-primary"], button[data-testid="stBaseButton-primary"], [data-testid="stFormSubmitButton"] button, .stFormSubmitButton button { background:#182B36 !important; color:#F2EFE6 !important; border:1px solid #182B36 !important; box-shadow:none !important; border-radius:5px !important; }
        button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover, button[data-testid="stBaseButton-primary"]:hover, [data-testid="stFormSubmitButton"] button:hover, .stFormSubmitButton button:hover { background:#F2EFE6 !important; color:#182B36 !important; }
        [data-testid="stSidebar"] .stButton > button { background:transparent !important; color:#F2EFE6 !important; border:1px solid rgba(242,239,230,.42) !important; }
        [data-testid="stSidebar"] .stButton > button:hover { background:#F2EFE6 !important; color:#182B36 !important; }
        [data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="textarea"] > div, [data-baseweb="base-input"], [data-testid="stSelectbox"] [data-baseweb="select"] > div, [data-testid="stNumberInput"] [data-baseweb="input"] > div, [data-testid="stTextInput"] [data-baseweb="input"] > div, [data-testid="stTextArea"] [data-baseweb="textarea"] > div { background:#F2EFE6 !important; color:#182B36 !important; border:1px solid rgba(24,43,54,.48) !important; border-radius:5px !important; box-shadow:none !important; }
        [data-baseweb="select"] *, [data-baseweb="input"] *, [data-baseweb="textarea"] *, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label { color:#182B36 !important; -webkit-text-fill-color:#182B36 !important; }
        [data-baseweb="popover"], [data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] [role="option"] { background:#F2EFE6 !important; color:#182B36 !important; }
        input[type="checkbox"] { accent-color:#182B36 !important; }
        [data-testid="stAlert"] { background:#F2EFE6 !important; color:#182B36 !important; border:1px solid #182B36 !important; border-left:3px solid #182B36 !important; border-radius:5px !important; }
        [data-testid="stAlert"] p, [data-testid="stAlert"] span, [data-testid="stAlert"] div, [data-testid="stAlert"] svg { color:#182B36 !important; fill:#182B36 !important; }
        [data-testid="stDataFrame"], [data-testid="stTable"] { background:#F2EFE6 !important; border:1px solid rgba(24,43,54,.35) !important; border-radius:5px !important; }
        [data-testid="stFolium"] iframe { border:1px solid rgba(24,43,54,.35) !important; border-radius:5px !important; }
        [data-testid="stDecoration"] { display:none !important; }
        @media(max-width:760px) { [data-testid="stMainBlockContainer"] { padding:1rem 1rem 2rem; } .rl-page-title { font-size:22px !important; } .rl-orbit-art { opacity:.10 !important; } }
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
              <ellipse cx="126" cy="67" rx="91" ry="34" fill="none" stroke="#F2EFE6" stroke-opacity=".50" stroke-width="1.2" transform="rotate(-19 126 67)"/>
              <ellipse cx="126" cy="67" rx="72" ry="55" fill="none" stroke="#F2EFE6" stroke-opacity=".24" stroke-width="1" transform="rotate(31 126 67)"/>
              <circle cx="126" cy="67" r="22" fill="#F2EFE6" fill-opacity=".15" stroke="#F2EFE6" stroke-opacity=".7"/>
              <path d="M113 67h26M126 54v26" stroke="#F2EFE6" stroke-opacity=".65" stroke-width=".8"/>
              <circle cx="49" cy="42" r="3.5" fill="#F2EFE6"/>
              <circle cx="197" cy="84" r="4" fill="#F2EFE6"/>
              <circle cx="126" cy="67" r="4" fill="#F2EFE6"/>
              <path d="M188 22l2 4 4 2-4 2-2 4-2-4-4-2 4-2z" fill="#F2EFE6" fill-opacity=".8"/>
              <path d="M66 99l1.5 3 3 1.5-3 1.5-1.5 3-1.5-3-3-1.5 3-1.5z" fill="#F2EFE6" fill-opacity=".55"/>
            </svg>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title: str, note: Optional[str] = None) -> None:
    """Render a section heading."""
    note_html = f'<div class="rl-section-note">{escape(note)}</div>' if note else ""
    st.markdown(
        f'<div class="rl-section-title">{escape(title)}</div>{note_html}',
        unsafe_allow_html=True,
    )


def status_badge_html(label: str, level: str = "low") -> str:
    """Return a compact, accessible status badge as HTML."""
    background, foreground = PRIORITY_SOFT_COLORS.get(
        level.lower(), ("#111827", "#94A3B8")
    )
    return (
        f'<span class="rl-status" style="background:{background};color:{foreground};border:1px solid {foreground}40">'
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
    background, foreground = PRIORITY_SOFT_COLORS.get(tier.lower(), ("#111827", "#94A3B8"))
    tier_label = tier.replace("_", " ").title()
    return (
        f'<span class="rl-triage-pill" style="background:{background};color:{foreground};border:1px solid {foreground}55;box-shadow:0 0 10px {foreground}25">'
        f'<span style="font-weight:800;font-size:12px">{score}/100</span> · {tier_label}</span>'
    )


def triage_breakdown_chips_html(breakdown: dict) -> str:
    """Render small score component chips showing math breakdown (+40, +30, etc)."""
    if not breakdown:
        return ""
    chips = []
    if breakdown.get("danger"):
        chips.append('<span class="rl-triage-chip" style="background:#450A0A;color:#FCA5A5;border:1px solid #EF444455">+40 Danger</span>')
    if breakdown.get("medical"):
        chips.append('<span class="rl-triage-chip" style="background:#431407;color:#FDBA74;border:1px solid #F9731655">+30 Medical</span>')
    if breakdown.get("people"):
        chips.append('<span class="rl-triage-chip" style="background:#172554;color:#93C5FD;border:1px solid #3B82F655">+20 Casualties</span>')
    if breakdown.get("comms"):
        chips.append('<span class="rl-triage-chip" style="background:#2E1065;color:#D8B4FE;border:1px solid #A855F755">+10 Comms Cutoff</span>')
    if breakdown.get("base"):
        chips.append(f'<span class="rl-triage-chip" style="background:#0F172A;color:#94A3B8;border:1px solid #33415555">+{breakdown["base"]} Baseline</span>')
    return "".join(chips)


def transmission_seal_html(fingerprint: str, channel: str, comm_status: str) -> str:
    """Render an official digital store-and-forward receipt verification badge."""
    is_sync = (comm_status == "synchronised")
    bg = "#06281B" if is_sync else "#381E04"
    color = "#34D399" if is_sync else "#FBBF24"
    label = "STORE & FORWARD VERIFIED UPLINK" if is_sync else "LOCAL SQLITE QUEUE · PENDING SYNC"
    channel_display = channel.replace("_", " ").title() if channel else "Local Offline Cache"
    return f"""
    <div style="background:{bg};border:1px solid {color}55;border-radius:8px;padding:10px 14px;margin:8px 0;box-shadow:0 0 12px {color}20">
      <div style="color:{color};font-size:10px;font-weight:800;letter-spacing:.08em">{label}</div>
      <div style="color:#F8FAFC;font-size:12px;font-weight:700;margin-top:2px">Receipt ID: <code style="color:#38BDF8">{escape(fingerprint or "N/A")}</code></div>
      <div style="color:#94A3B8;font-size:11px;margin-top:2px">Channel Route: <strong style="color:#F1F5F9">{escape(channel_display)}</strong> · Loss Rate: <strong style="color:#34D399">0.0%</strong></div>
    </div>
    """

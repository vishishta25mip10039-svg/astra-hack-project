# ============================================================
# MEMBER 3 — INTEGRATION / UTILS
# FILE: utils/helpers.py
# PURPOSE: Shared theme, badges, validators used across all pages
# ============================================================

import streamlit as st

# ── Colour constants ─────────────────────────────────────────
PRIORITY_COLORS = {
    "critical": "#FF4444",
    "high":     "#FF8800",
    "moderate": "#FFDD00",
    "low":      "#44BB44",
}

COMM_STATUS_BADGE = {
    "pending":      "🔴 Pending",
    "synchronised": "🟢 Synchronised",
}

RESCUE_STATUS_BADGE = {
    "open":        "⚪ Open",
    "assigned":    "🔵 Assigned",
    "in_progress": "🟡 In Progress",
    "resolved":    "🟢 Resolved",
}

CATEGORIES = [
    "Flood", "Earthquake", "Landslide", "Fire",
    "Medical Assistance", "Structural Collapse", "Other",
]

SEVERITIES = ["Low", "Moderate", "High", "Critical"]


# ── Theme injection ───────────────────────────────────────────
def apply_theme():
    """Inject dark navy + cyan CSS into the Streamlit app."""
    st.markdown("""
    <style>
        /* ── Root palette ── */
        :root {
            --bg-primary:   #0A0E1A;
            --bg-secondary: #0F1629;
            --bg-card:      #131B2E;
            --accent:       #00D4FF;
            --accent-soft:  #0096B7;
            --text-primary: #E8F4FD;
            --text-muted:   #8BA4C8;
            --border:       #1E3A5F;
            --danger:       #FF4444;
            --warning:      #FF8800;
            --success:      #44BB44;
        }

        /* ── Background ── */
        .stApp { background-color: var(--bg-primary); color: var(--text-primary); }
        [data-testid="stSidebar"] {
            background-color: var(--bg-secondary);
            border-right: 1px solid var(--border);
        }

        /* ── Metric cards ── */
        [data-testid="stMetric"] {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
        }
        [data-testid="stMetricValue"] { color: var(--accent) !important; font-size: 2rem; }
        [data-testid="stMetricLabel"] { color: var(--text-muted); font-size: 0.85rem; }

        /* ── Buttons ── */
        .stButton > button {
            background: linear-gradient(135deg, var(--accent-soft), var(--accent));
            color: #0A0E1A;
            font-weight: 700;
            border: none;
            border-radius: 8px;
        }
        .stButton > button:hover { opacity: 0.85; }

        /* ── Inputs ── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            background: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px;
        }

        /* ── Dataframe ── */
        .stDataFrame { border: 1px solid var(--border); border-radius: 8px; }

        /* ── Expander ── */
        .streamlit-expanderHeader {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
        }

        /* ── Divider ── */
        hr { border-color: var(--border); }

        /* ── Sidebar nav ── */
        [data-testid="stRadio"] label { color: var(--text-primary) !important; }

        /* ── Page hero ── */
        .hero-banner {
            background: linear-gradient(135deg, #0F1629 0%, #1E3A5F 100%);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px 32px;
            margin-bottom: 24px;
        }
        .hero-banner h1 { color: var(--accent); margin: 0; }
        .hero-banner p  { color: var(--text-muted); margin: 4px 0 0; }

        /* ── Status pill ── */
        .status-pill {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)


# ── Validators ────────────────────────────────────────────────
def validate_coordinates(lat: float, lon: float) -> tuple:
    """Returns (is_valid: bool, error_msg: str)."""
    if not (-90 <= lat <= 90):
        return False, "Latitude must be between -90 and 90"
    if not (-180 <= lon <= 180):
        return False, "Longitude must be between -180 and 180"
    return True, ""


# ── Badge helpers ─────────────────────────────────────────────
def priority_badge(priority: str) -> str:
    emojis = {"critical": "🔴", "high": "🟠", "moderate": "🟡", "low": "🟢"}
    return f"{emojis.get(priority, '⚪')} {priority.capitalize()}"


def comm_badge(status: str) -> str:
    return COMM_STATUS_BADGE.get(status, status)


def rescue_badge(status: str) -> str:
    return RESCUE_STATUS_BADGE.get(status, status)

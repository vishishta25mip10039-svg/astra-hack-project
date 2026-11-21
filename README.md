# 🛰️ RESCUE LINK
### Satellite-Assisted Emergency SOS & Rescue Coordination
**ASTRA 2026 · Domain 4: Satellite Communication, Navigation & Connectivity**
**Team Aurora · VIT Bhopal**

---

## 📁 Project Structure

```
rescue_link_v2/
│
├── app.py                      ← Entry point (Member 3)
├── requirements.txt            ← Dependencies (Member 3)
│
├── backend/                    ← MEMBER 1 owns this entire folder
│   ├── __init__.py
│   ├── db.py                   ← Schema, init, seed data
│   ├── connectivity.py         ← Channel state engine + sync
│   ├── sos.py                  ← Create & fetch SOS requests
│   └── rescue.py               ← Team assignment & metrics
│
├── frontend/                   ← MEMBER 2 owns this entire folder
│   ├── __init__.py
│   ├── home.py                 ← Landing page + live metrics
│   ├── citizen_portal.py       ← SOS submission form
│   ├── command_centre.py       ← Map + team dispatch
│   ├── connectivity_monitor.py ← Channel toggles + sync
│   ├── analytics.py            ← Charts + geographic map
│   └── about.py                ← Project info + team credits
│
└── utils/                      ← MEMBER 3 owns this
    ├── __init__.py
    └── helpers.py              ← Theme CSS, badges, validators
```

---

## 👥 Team Assignments

| Member | Role | Files | Tasks |
|--------|------|-------|-------|
| **Member 1** | Backend Dev | `backend/` (all 4 files) | DB schema, channel logic, SOS CRUD, rescue ops |
| **Member 2** | Frontend Dev | `frontend/` (all 6 files) | All 6 UI pages, forms, map, charts |
| **Member 3** | Integration Lead | `app.py`, `utils/helpers.py`, `requirements.txt`, `README.md` | Routing, theme, testing, demo setup |

---

## 🚀 Setup & Run

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Run the app
```bash
streamlit run app.py
```

### Step 3 — Open in browser
```
http://localhost:8501
```

### Step 4 — Load demo data
Click **"🎬 Load Demo Data"** in the sidebar to populate 3 sample SOS requests.

---

## 🛰️ Domain 4 Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| **Store-and-Forward** | SOS stored in SQLite when offline, flushed when channel restores |
| **Multi-channel Fallback** | Cellular → Internet → Satellite priority chain |
| **Satellite Uplink Simulation** | GSAT/INSAT-style toggle in Connectivity Monitor |
| **Priority Routing** | Critical SOS flagged for immediate team dispatch |
| **Offline Resilience** | System accepts SOS even with zero connectivity |

---

## 🔄 Key Demo Flow

1. **Go to Connectivity Monitor** → Turn OFF Cellular + Internet
2. **Go to Citizen SOS Portal** → Submit 2–3 SOS requests
3. Notice they show as `🔴 Pending` (store-and-forward active)
4. **Back to Connectivity Monitor** → Turn ON Satellite → Click Sync
5. Watch all pending → `🟢 Synchronised` (satellite uplink complete)
6. **Go to Command Centre** → Assign teams, update status
7. **Go to Analytics** → See real-time charts update

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **Streamlit** — Web UI
- **SQLite** — Local store-and-forward database
- **Folium + streamlit-folium** — Interactive map
- **Plotly Express** — Charts
- **Pandas** — Data display

---

*Built for ASTRA 2026 Hackathon · Team Aurora · VIT Bhopal*

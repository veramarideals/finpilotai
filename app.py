# ╔══════════════════════════════════════════════════════════════════╗
#  FinPilotAI  —  AI-powered Financial & Career Dashboard
#  v2.0  |  Fixes: HTML table rendering + Student Mode
# ╚══════════════════════════════════════════════════════════════════╝

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import requests
import json
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinPilotAI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  SAFE HTML RENDERER
#  Uses st.components.v1.html — renders inside a real iframe so Streamlit's
#  markdown sanitiser never touches the HTML.  All CSS is bundled inline.
# ─────────────────────────────────────────────────────────────────────────────
_IFRAME_BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');
*  { box-sizing: border-box; margin: 0; padding: 0; }
body { background: transparent; font-family: 'Inter', sans-serif; color: #e2e8f0; }

/* ── TABLE WRAPPER ── */
.table-wrap {
  background: #0d1424;
  border: 1px solid #1e2d3d;
  border-radius: 12px;
  overflow: hidden;
  width: 100%;
}
.fin-table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
.fin-table th {
  background: #111927;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.68rem;
  font-weight: 600;
  padding: 0.7rem 1rem;
  text-align: left;
  border-bottom: 1px solid #1e2d3d;
  white-space: nowrap;
}
.fin-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(30,45,61,0.5);
  color: #e2e8f0;
  vertical-align: middle;
}
.fin-table tr:last-child td { border-bottom: none; }
.fin-table tr:hover td     { background: rgba(255,255,255,0.02); }

/* ── BADGES ── */
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  font-family: 'Space Mono', monospace;
  white-space: nowrap;
}
.badge-low    { background:rgba(34,197,94,0.15);  color:#22c55e; border:1px solid rgba(34,197,94,0.3);  }
.badge-medium { background:rgba(245,158,11,0.15); color:#f59e0b; border:1px solid rgba(245,158,11,0.3); }
.badge-high   { background:rgba(239,68,68,0.15);  color:#ef4444; border:1px solid rgba(239,68,68,0.3);  }

/* ── STUDENT TABLE (skill cards inside iframe) ── */
.skill-table-wrap {
  background: #0d1424;
  border: 1px solid #1e2d3d;
  border-radius: 12px;
  overflow: hidden;
  width: 100%;
}

/* ── HELPERS ── */
.bold  { font-weight: 600; }
.muted { color: #64748b; }
.mono  { font-family: 'Space Mono', monospace; }
.small { font-size: 0.72rem; }
.green { color: #00f5a0; }
.gold  { color: #f59e0b; }
.blue  { color: #0ea5e9; }
.purple{ color: #a855f7; }
</style>
"""

def render_html(inner_html: str, height: int = 200) -> None:
    """
    Render arbitrary HTML+CSS safely inside a real browser iframe.
    Bypasses Streamlit's markdown sanitiser completely — this is the
    correct fix for raw HTML appearing as plain text on screen.
    """
    full = (
        "<!DOCTYPE html><html><head>"
        '<meta charset="utf-8">'
        + _IFRAME_BASE_CSS
        + "</head><body>"
        + inner_html
        + "</body></html>"
    )
    components.html(full, height=height, scrolling=False)


# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS  —  Dark Fintech Theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg-primary:    #080c14;
    --bg-card:       #0d1424;
    --bg-elevated:   #111927;
    --accent-green:  #00f5a0;
    --accent-blue:   #0ea5e9;
    --accent-purple: #a855f7;
    --accent-gold:   #f59e0b;
    --accent-teal:   #06b6d4;
    --text-primary:  #e2e8f0;
    --text-muted:    #64748b;
    --border:        #1e2d3d;
    --danger:        #ef4444;
    --success:       #22c55e;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary);
}
.main .block-container { padding: 1.5rem 2rem 3rem 2rem; max-width: 1400px; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--accent-green); border-radius: 2px; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] label {
    color: var(--text-muted) !important;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.sidebar-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-green), var(--accent-blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    padding: 0.5rem 0 1.5rem 0;
    text-align: center;
}
.sidebar-tagline {
    color: var(--text-muted);
    font-size: 0.7rem;
    text-align: center;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: -1rem;
    margin-bottom: 1.5rem;
}
.sidebar-divider { border: none; border-top: 1px solid var(--border); margin: 1rem 0; }

/* ── PAGE HEADER ── */
.header-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-blue) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    line-height: 1.1;
}
.header-subtitle {
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-bottom: 1.5rem;
}
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,245,160,0.1);
    border: 1px solid rgba(0,245,160,0.3);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.7rem;
    color: var(--accent-green);
    font-weight: 600;
    font-family: 'Space Mono', monospace;
}
.student-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(168,85,247,0.12);
    border: 1px solid rgba(168,85,247,0.35);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.7rem;
    color: var(--accent-purple);
    font-weight: 600;
    font-family: 'Space Mono', monospace;
}
.pulse {
    width: 6px; height: 6px;
    background: var(--accent-green);
    border-radius: 50%;
    animation: pulse 2s infinite;
    display: inline-block;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.8); }
}

/* ── SECTION HEADERS ── */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 1.5rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, var(--border), transparent);
    margin-left: 0.5rem;
}

/* ── METRIC CARDS ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: var(--accent-green); }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-blue));
}
.metric-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-bottom: 0.3rem; }
.metric-value { font-family: 'Space Mono', monospace; font-size: 1.5rem; font-weight: 700; color: var(--accent-green); line-height: 1.1; }
.metric-sub   { font-size: 0.72rem; color: var(--text-muted); margin-top: 0.25rem; }
.metric-card.purple-accent::before { background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue)); }
.metric-card.purple-accent .metric-value { color: var(--accent-purple); }

/* ── RECOMMENDATION CARDS ── */
.rec-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.3rem;
    height: 100%;
    transition: transform 0.2s, border-color 0.2s;
}
.rec-card:hover { transform: translateY(-3px); border-color: rgba(0,245,160,0.4); }
.rec-icon  { font-size: 1.8rem; margin-bottom: 0.6rem; display: block; }
.rec-type  { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700; margin-bottom: 0.3rem; font-family: 'Space Mono', monospace; }
.rec-title { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem; line-height: 1.3; }
.rec-body  { font-size: 0.82rem; color: var(--text-muted); line-height: 1.6; }
.rec-career  { border-top: 2px solid var(--accent-blue);   } .rec-career  .rec-type { color: var(--accent-blue);   }
.rec-invest  { border-top: 2px solid var(--accent-green);  } .rec-invest  .rec-type { color: var(--accent-green);  }
.rec-finance { border-top: 2px solid var(--accent-gold);   } .rec-finance .rec-type { color: var(--accent-gold);   }
.rec-skill   { border-top: 2px solid var(--accent-purple); } .rec-skill   .rec-type { color: var(--accent-purple); }
.rec-intern  { border-top: 2px solid var(--accent-teal);   } .rec-intern  .rec-type { color: var(--accent-teal);   }
.rec-side    { border-top: 2px solid var(--accent-gold);   } .rec-side    .rec-type { color: var(--accent-gold);   }

/* ── INSURANCE CARDS ── */
.insurance-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.4rem;
    position: relative;
    overflow: hidden;
}
.insurance-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, var(--accent-purple), var(--accent-blue));
}
.insurance-company { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent-purple); font-weight: 700; font-family: 'Space Mono', monospace; margin-bottom: 0.3rem; }
.insurance-plan    { font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.8rem; }
.insurance-benefit { display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.35rem; line-height: 1.5; }
.insurance-benefit::before { content: '→'; color: var(--accent-green); flex-shrink: 0; }
.insurance-premium { margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
.premium-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; }
.premium-value { font-family: 'Space Mono', monospace; font-size: 1rem; font-weight: 700; color: var(--accent-gold); }

/* ── STUDENT GROWTH CARDS ── */
.student-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.3rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s, transform 0.2s;
}
.student-card:hover { border-color: rgba(168,85,247,0.4); transform: translateY(-2px); }
.student-card-title { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.4rem; }
.student-card-body  { font-size: 0.82rem; color: var(--text-muted); line-height: 1.6; }
.student-tag {
    display: inline-block;
    background: rgba(168,85,247,0.12);
    border: 1px solid rgba(168,85,247,0.25);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.68rem;
    color: var(--accent-purple);
    font-family: 'Space Mono', monospace;
    margin-bottom: 0.5rem;
}
.teal-tag {
    display: inline-block;
    background: rgba(6,182,212,0.12);
    border: 1px solid rgba(6,182,212,0.25);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.68rem;
    color: var(--accent-teal);
    font-family: 'Space Mono', monospace;
    margin-bottom: 0.5rem;
}
.gold-tag {
    display: inline-block;
    background: rgba(245,158,11,0.12);
    border: 1px solid rgba(245,158,11,0.25);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.68rem;
    color: var(--accent-gold);
    font-family: 'Space Mono', monospace;
    margin-bottom: 0.5rem;
}
.roadmap-step {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--border);
}
.roadmap-step:last-child { border-bottom: none; }
.step-num {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem;
    font-weight: 700;
    color: #fff;
    flex-shrink: 0;
    font-family: 'Space Mono', monospace;
}
.step-content { flex: 1; }
.step-title   { font-weight: 600; font-size: 0.88rem; color: var(--text-primary); margin-bottom: 0.2rem; }
.step-body    { font-size: 0.78rem; color: var(--text-muted); line-height: 1.5; }
.student-banner {
    background: linear-gradient(135deg, rgba(168,85,247,0.12), rgba(14,165,233,0.08));
    border: 1px solid rgba(168,85,247,0.3);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.banner-icon { font-size: 2.5rem; flex-shrink: 0; }
.banner-title { font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 800; color: var(--text-primary); margin-bottom: 0.3rem; }
.banner-sub   { font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; }

/* ── CHATBOT ── */
.chat-container  { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; margin-bottom: 1.5rem; }
.chat-header     { background: var(--bg-elevated); padding: 1rem 1.3rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 0.75rem; }
.chat-bot-name   { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.95rem; color: var(--text-primary); }
.chat-bot-status { font-size: 0.68rem; color: var(--accent-green); font-family: 'Space Mono', monospace; }
.chat-messages   { padding: 1.2rem; min-height: 280px; max-height: 420px; overflow-y: auto; display: flex; flex-direction: column; gap: 1rem; }
.chat-bubble     { display: flex; gap: 0.75rem; align-items: flex-start; max-width: 85%; }
.chat-bubble.user { flex-direction: row-reverse; align-self: flex-end; }
.avatar          { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; flex-shrink: 0; }
.avatar-bot      { background: linear-gradient(135deg, var(--accent-green), var(--accent-blue)); }
.avatar-user     { background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue)); }
.bubble-text     { background: var(--bg-elevated); border: 1px solid var(--border); border-radius: 12px; padding: 0.7rem 1rem; font-size: 0.83rem; line-height: 1.6; color: var(--text-primary); }
.bubble-text.user-bubble { background: rgba(168,85,247,0.12); border-color: rgba(168,85,247,0.25); }
.bubble-time     { font-size: 0.65rem; color: var(--text-muted); margin-top: 0.3rem; font-family: 'Space Mono', monospace; }

/* ── SUGGESTION PILLS ── */
.suggestion-pill { display: inline-block; background: rgba(14,165,233,0.1); border: 1px solid rgba(14,165,233,0.25); border-radius: 20px; padding: 4px 12px; font-size: 0.75rem; color: var(--accent-blue); margin: 3px; font-family: 'Space Mono', monospace; }

/* ── STREAMLIT OVERRIDES ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-green), #00d4ff) !important;
    color: #080c14 !important; border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important; letter-spacing: 0.05em !important;
    padding: 0.5rem 1.2rem !important; transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
.stTextInput input, .stTextArea textarea {
    background: var(--bg-elevated) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent-green) !important;
    box-shadow: 0 0 0 2px rgba(0,245,160,0.15) !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: var(--bg-elevated) !important; border: 1px solid var(--border) !important;
    color: var(--text-primary) !important; border-radius: 8px !important;
}
.stNumberInput input {
    background: var(--bg-elevated) !important; border: 1px solid var(--border) !important;
    color: var(--text-primary) !important; border-radius: 8px !important;
}
.stSpinner > div { border-top-color: var(--accent-green) !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for _key in ["chat_history", "ai_recs", "stocks", "mfs", "insurance",
             "student_data", "last_profile_hash"]:
    if _key not in st.session_state:
        st.session_state[_key] = [] if _key in ("chat_history",) else None


# ─────────────────────────────────────────────────────────────────────────────
#  OPENROUTER API
# ─────────────────────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "deepseek/deepseek-chat"

def _call_api(messages: list, temperature: float = 0.7) -> str:
    if not OPENROUTER_API_KEY:
        return (
            "⚠️ API key not configured. "
            "Add OPENROUTER_API_KEY to .streamlit/secrets.toml"
        )
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://finpilotai.app",
                "X-Title": "FinPilotAI",
            },
            json={"model": MODEL, "messages": messages,
                  "temperature": temperature, "max_tokens": 1200},
            timeout=45,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "⏱️ Request timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        return f"❌ API error {e.response.status_code}: {e.response.text[:200]}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_ai_response(prompt: str, system: str = "", temperature: float = 0.7) -> str:
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    return _call_api(msgs, temperature)

def get_ai_response_with_history(messages_list: list, system: str = "") -> str:
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages_list)
    return _call_api(msgs)

def parse_json(raw: str):
    """Strip markdown fences and parse JSON."""
    cleaned = raw.strip()
    for fence in ("```json", "```"):
        cleaned = cleaned.lstrip(fence)
    cleaned = cleaned.rstrip("```").strip()
    return json.loads(cleaned)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR  —  User Profile
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚡ FinPilotAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">AI · Finance · Career</div>', unsafe_allow_html=True)
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    st.markdown("**👤 YOUR PROFILE**")
    name      = st.text_input("Name",                  placeholder="e.g. Alex Johnson")
    age       = st.number_input("Age",                 min_value=16, max_value=80, value=22, step=1)
    role      = st.selectbox("Role",                   ["Student", "Working Professional", "Freelancer", "Entrepreneur"])
    field     = st.text_input("Degree / Field",         placeholder="e.g. Computer Science")
    income    = st.number_input("Monthly Income (₹)",  min_value=0, value=0 if role == "Student" else 50000, step=1000)
    expenses  = st.number_input("Monthly Expenses (₹)",min_value=0, value=5000 if role == "Student" else 30000, step=500)
    interests = st.text_input("Interests",              placeholder="e.g. Tech, AI, Travel")

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    generate_btn = st.button("🚀 Generate My Dashboard", use_container_width=True)

    # ── live snapshot
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    savings     = max(0, income - expenses)
    savings_pct = round((savings / income * 100), 1) if income > 0 else 0
    st.markdown(f"""
    <div style="font-size:0.72rem;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;">Snapshot</div>
    <div style="display:flex;justify-content:space-between;margin-bottom:0.35rem;">
        <span style="font-size:0.8rem;color:#94a3b8;">Monthly Savings</span>
        <span style="font-family:'Space Mono',monospace;font-size:0.8rem;color:#00f5a0;">₹{savings:,}</span>
    </div>
    <div style="display:flex;justify-content:space-between;">
        <span style="font-size:0.8rem;color:#94a3b8;">Savings Rate</span>
        <span style="font-family:'Space Mono',monospace;font-size:0.8rem;
              color:{'#22c55e' if savings_pct>=20 else '#f59e0b' if savings_pct>=10 else '#ef4444'};">
            {savings_pct}%</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.65rem;color:#475569;text-align:center;line-height:1.6;">
        Powered by <span style="color:#00f5a0;">DeepSeek</span> via OpenRouter<br>
        <span style="font-family:'Space Mono',monospace;">{MODEL}</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PROFILE DICT
# ─────────────────────────────────────────────────────────────────────────────
profile = {
    "name":        name or "User",
    "age":         age,
    "role":        role,
    "field":       field or "General",
    "income":      income,
    "expenses":    expenses,
    "savings":     savings,
    "savings_pct": savings_pct,
    "interests":   interests or "General",
}
profile_context = f"""
User Profile:
- Name: {profile['name']}
- Age: {profile['age']}
- Role: {profile['role']}
- Field/Degree: {profile['field']}
- Monthly Income: ₹{profile['income']:,}
- Monthly Expenses: ₹{profile['expenses']:,}
- Monthly Savings: ₹{profile['savings']:,} ({profile['savings_pct']}% savings rate)
- Interests: {profile['interests']}
"""
profile_hash = hash(json.dumps(profile, sort_keys=True))

# ── Determine mode
IS_STUDENT_MODE = (role == "Student" and income == 0)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
h_col, b_col = st.columns([5, 1])
with h_col:
    greeting = profile['name'].split()[0] if profile['name'] != 'User' else 'there'
    mode_label = "Student Growth Dashboard" if IS_STUDENT_MODE else "Financial Intelligence Dashboard"
    st.markdown(f"""
    <div class="header-title">Hey {greeting} 👋</div>
    <div class="header-subtitle">
        Your AI-powered {mode_label} ·
        <span style="color:#00f5a0;">{datetime.now().strftime('%B %d, %Y')}</span>
    </div>
    """, unsafe_allow_html=True)
with b_col:
    badge = '<span class="student-badge">🎓 STUDENT MODE</span>' if IS_STUDENT_MODE else '<span class="live-badge"><span class="pulse"></span> LIVE AI</span>'
    st.markdown(f'<div style="text-align:right;margin-top:0.5rem;">{badge}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  TOP METRICS ROW
# ─────────────────────────────────────────────────────────────────────────────
def metric_card(label, value, sub, col, purple=False):
    extra = ' purple-accent' if purple else ''
    col.markdown(f"""
    <div class="metric-card{extra}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
if IS_STUDENT_MODE:
    health_score = min(100, int(age * 1.5))   # proxy for student
    metric_card("Mode",           "🎓 Student",  f"{field or 'General'} · Age {age}", m1, purple=True)
    metric_card("Monthly Budget", f"₹{expenses:,}", "Pocket / study expenses", m2)
    metric_card("Side Income",    "₹0",          "Grow with gigs & freelancing",      m3)
    metric_card("Growth Score",   f"{health_score}/100", "AI-computed potential",     m4, purple=True)
else:
    health_score = min(100, int(savings_pct * 2.5 + (30 if savings_pct >= 20 else 0)))
    metric_card("Monthly Income",   f"₹{income:,}",   f"{role} · {field}", m1)
    metric_card("Monthly Expenses", f"₹{expenses:,}", "Total outflow",      m2)
    metric_card("Net Savings",      f"₹{savings:,}",  f"{savings_pct}% savings rate", m3)
    metric_card("Financial Health", f"{health_score}/100", "AI-computed score", m4)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  GENERATE AI DATA  (triggered by button or first load)
# ─────────────────────────────────────────────────────────────────────────────
should_generate = generate_btn or (st.session_state.last_profile_hash != profile_hash)

if should_generate:
    st.session_state.last_profile_hash = profile_hash

    # ── AI Recommendations (both modes)
    with st.spinner("🤖 AI is analysing your profile…"):
        if IS_STUDENT_MODE:
            rec_prompt = f"""
{profile_context}
You are FinPilotAI, an expert career and growth advisor for students.
Based on the user's profile, provide 3 recommendations in strict JSON.
Return ONLY valid JSON, no markdown.

{{
  "skills": {{
    "title": "Short skill recommendation title (max 6 words)",
    "body": "2-3 sentence personalised advice on skills to learn"
  }},
  "internship": {{
    "title": "Short internship recommendation title (max 6 words)",
    "body": "2-3 sentence personalised internship advice"
  }},
  "side_income": {{
    "title": "Short side income idea title (max 6 words)",
    "body": "2-3 sentence personalised side income advice"
  }}
}}
"""
        else:
            rec_prompt = f"""
{profile_context}
You are FinPilotAI, an expert financial and career advisor.
Provide EXACTLY 3 recommendations in strict JSON. Return ONLY valid JSON, no markdown.

{{
  "career": {{
    "title": "Short career path title (max 6 words)",
    "body": "2-3 sentence personalised career advice"
  }},
  "investment": {{
    "title": "Short investment suggestion title (max 6 words)",
    "body": "2-3 sentence personalised investment advice"
  }},
  "financial_tip": {{
    "title": "Short financial tip title (max 6 words)",
    "body": "2-3 sentence personalised financial tip"
  }}
}}
"""
        raw_rec = get_ai_response(rec_prompt, temperature=0.5)
        try:
            st.session_state.ai_recs = parse_json(raw_rec)
        except Exception:
            if IS_STUDENT_MODE:
                st.session_state.ai_recs = {
                    "skills": {"title": "Learn Python, AI & Cloud", "body": f"As a {field or 'student'}, mastering Python, machine learning, and cloud platforms (AWS/GCP) will open doors to top internships and jobs. Start with free resources on Coursera and fast.ai."},
                    "internship": {"title": "Apply to Startups & Big Tech", "body": "Target internships at startups for fast learning and big tech (Google, Microsoft, Infosys) for brand value. Use LinkedIn, Internshala, and your college placement cell."},
                    "side_income": {"title": "Freelance on Fiverr & Upwork", "body": "Offer services in coding, design, or content writing on Fiverr and Upwork. Even ₹5,000-15,000/month from freelancing builds experience and a financial cushion."},
                }
            else:
                st.session_state.ai_recs = {
                    "career": {"title": "Explore AI & Tech Careers", "body": f"As a {role} in {field}, the AI/ML domain offers tremendous growth. Consider upskilling in Python, data science, or cloud computing."},
                    "investment": {"title": "Start SIP in Index Funds", "body": f"With ₹{savings:,}/month in savings, investing 30-40% in diversified index funds via SIP is a solid long-term wealth strategy."},
                    "financial_tip": {"title": "Follow the 50-30-20 Rule", "body": "Allocate 50% to needs, 30% to wants, and 20% to savings/investments. Build a 6-month emergency fund first."},
                }

    # ── Financial mode: fetch stocks, MFs, insurance
    if not IS_STUDENT_MODE:
        with st.spinner("Fetching AI stock picks…"):
            stock_prompt = f"""
{profile_context}
Recommend exactly 3 Indian or global stocks suited to this user.
Return ONLY a valid JSON array (no markdown). Each object:
- stock_name (string)
- ticker (string, e.g. "RELIANCE.NS")
- sector (string)
- reason (string, 1 sentence)
- risk_level (one of: "Low", "Medium", "High")
- current_price (number in INR)
- change_pct (number, e.g. 2.3 for +2.3%)
"""
            raw_s = get_ai_response(stock_prompt, temperature=0.4)
            try:
                st.session_state.stocks = parse_json(raw_s)
            except Exception:
                st.session_state.stocks = [
                    {"stock_name":"Reliance Industries","ticker":"RELIANCE.NS","sector":"Conglomerate","reason":"Diversified revenue across telecom, retail and energy.","risk_level":"Low","current_price":2850,"change_pct":1.2},
                    {"stock_name":"Infosys","ticker":"INFY.NS","sector":"IT Services","reason":"Strong global IT demand and consistent dividends.","risk_level":"Low","current_price":1590,"change_pct":-0.3},
                    {"stock_name":"Zomato","ticker":"ZOMATO.NS","sector":"Foodtech","reason":"Rapid growth in quick commerce; suits high-risk appetite.","risk_level":"High","current_price":215,"change_pct":3.7},
                ]

        with st.spinner("Fetching AI mutual fund picks…"):
            mf_prompt = f"""
{profile_context}
Recommend exactly 3 Indian mutual funds suited to this user.
Return ONLY valid JSON array (no markdown). Each object:
- fund_name (string)
- category (string)
- amc (string)
- expected_return (string, e.g. "12-15% p.a.")
- risk_level (one of: Low, Medium, High)
- min_sip (number, monthly SIP in INR)
- reason (string, 1 sentence)
"""
            raw_m = get_ai_response(mf_prompt, temperature=0.4)
            try:
                st.session_state.mfs = parse_json(raw_m)
            except Exception:
                st.session_state.mfs = [
                    {"fund_name":"Mirae Asset Large Cap Fund","category":"Large Cap","amc":"Mirae Asset","expected_return":"11-13% p.a.","risk_level":"Low","min_sip":1000,"reason":"Consistent performer with exposure to India's top 100 companies."},
                    {"fund_name":"Axis Bluechip Fund","category":"Large Cap","amc":"Axis AMC","expected_return":"12-14% p.a.","risk_level":"Low","min_sip":500,"reason":"Quality-focused portfolio with low churn and strong track record."},
                    {"fund_name":"Parag Parikh Flexi Cap","category":"Flexi Cap","amc":"PPFAS","expected_return":"14-18% p.a.","risk_level":"Medium","min_sip":1000,"reason":"Global diversification combined with domestic equity."},
                ]

        with st.spinner("Fetching AI insurance recommendations…"):
            ins_prompt = f"""
{profile_context}
Recommend exactly 2 insurance plans (one life/term, one health) suited to this user.
Return ONLY valid JSON array (no markdown). Each object:
- company (string)
- plan_name (string)
- plan_type (string, e.g. "Term Life", "Health Insurance")
- benefits (array of 3 short strings)
- estimated_premium (string, e.g. "Rs 800/month")
- sum_assured (string, e.g. "Rs 1 Crore")
"""
            raw_i = get_ai_response(ins_prompt, temperature=0.4)
            try:
                st.session_state.insurance = parse_json(raw_i)
            except Exception:
                st.session_state.insurance = [
                    {"company":"LIC","plan_name":"Tech Term","plan_type":"Term Life Insurance","benefits":["1 Cr sum assured","Critical illness rider","Tax benefit under 80C"],"estimated_premium":"Rs 700/month","sum_assured":"Rs 1 Crore"},
                    {"company":"Star Health","plan_name":"Comprehensive Health","plan_type":"Health Insurance","benefits":["10 Lakh cover","Cashless hospitalisation","No co-pay"],"estimated_premium":"Rs 500/month","sum_assured":"Rs 10 Lakh"},
                ]

    # ── Student mode: fetch detailed student data
    else:
        with st.spinner("Building your Student Growth Dashboard…"):
            stu_prompt = f"""
{profile_context}
You are a student career advisor. Generate personalised content for a student dashboard.
Return ONLY valid JSON (no markdown) with this exact structure:

{{
  "skills": [
    {{"name": "Skill name", "why": "1 sentence why", "resource": "Free resource name", "difficulty": "Beginner/Intermediate/Advanced", "time": "e.g. 4 weeks"}},
    {{"name": "...", "why": "...", "resource": "...", "difficulty": "...", "time": "..."}},
    {{"name": "...", "why": "...", "resource": "...", "difficulty": "...", "time": "..."}}
  ],
  "internships": [
    {{"company": "Company name", "role": "Internship role", "platform": "Where to apply", "stipend": "e.g. Rs 10,000-20,000/month", "skills_needed": "1-2 skills"}},
    {{"company": "...", "role": "...", "platform": "...", "stipend": "...", "skills_needed": "..."}},
    {{"company": "...", "role": "...", "platform": "...", "stipend": "...", "skills_needed": "..."}}
  ],
  "side_income": [
    {{"idea": "Side income idea", "platform": "Platform name", "earning": "e.g. Rs 5,000-15,000/month", "effort": "Low/Medium/High", "how": "1 sentence how-to"}},
    {{"idea": "...", "platform": "...", "earning": "...", "effort": "...", "how": "..."}},
    {{"idea": "...", "platform": "...", "earning": "...", "effort": "...", "how": "..."}}
  ],
  "roadmap": [
    {{"phase": "Phase name e.g. Now (0-3 months)", "action": "Specific action", "goal": "Expected outcome"}},
    {{"phase": "...", "action": "...", "goal": "..."}},
    {{"phase": "...", "action": "...", "goal": "..."}},
    {{"phase": "...", "action": "...", "goal": "..."}}
  ]
}}
"""
            raw_stu = get_ai_response(stu_prompt, temperature=0.5)
            try:
                st.session_state.student_data = parse_json(raw_stu)
            except Exception:
                st.session_state.student_data = {
                    "skills": [
                        {"name":"Python Programming","why":"Foundation for AI, data science, and web backends.","resource":"freeCodeCamp / CS50P","difficulty":"Beginner","time":"6 weeks"},
                        {"name":"Machine Learning","why":"Top skill demanded by tech companies in 2025.","resource":"fast.ai / Coursera Andrew Ng","difficulty":"Intermediate","time":"10 weeks"},
                        {"name":"Cloud Computing (AWS)","why":"Cloud skills add 30-40% to starting salaries.","resource":"AWS Free Tier + A Cloud Guru","difficulty":"Intermediate","time":"8 weeks"},
                    ],
                    "internships": [
                        {"company":"Google","role":"STEP Intern / SWE Intern","platform":"careers.google.com","stipend":"Rs 80,000-1,20,000/month","skills_needed":"Python, DSA"},
                        {"company":"Startups via Internshala","role":"ML / Web Dev Intern","platform":"Internshala.com","stipend":"Rs 8,000-25,000/month","skills_needed":"Python / React"},
                        {"company":"Infosys / TCS","role":"Campus Intern Program","platform":"College Placement Cell","stipend":"Rs 15,000-25,000/month","skills_needed":"Any tech stack"},
                    ],
                    "side_income": [
                        {"idea":"Freelance Web Development","platform":"Fiverr / Upwork","earning":"Rs 10,000-40,000/month","effort":"Medium","how":"Build 2-3 portfolio projects, then pitch on Fiverr."},
                        {"idea":"Content Writing / Blogging","platform":"Medium / Substack","earning":"Rs 3,000-12,000/month","effort":"Low","how":"Write about your field weekly; monetise via Medium Partner Program."},
                        {"idea":"Tutoring / Teaching Online","platform":"Vedantu / Chegg","earning":"Rs 5,000-20,000/month","effort":"Low","how":"Register as a tutor; teach subjects you excel in."},
                    ],
                    "roadmap": [
                        {"phase":"Now (0-3 months)","action":"Pick 1 core skill and complete a beginner course","goal":"Build foundation; deploy 1 small project on GitHub"},
                        {"phase":"Short Term (3-6 months)","action":"Apply for internships and freelance gigs","goal":"First work experience + Rs 5,000-15,000 side income"},
                        {"phase":"Mid Term (6-12 months)","action":"Complete 2nd skill, build portfolio, get references","goal":"Land a paid internship or part-time role"},
                        {"phase":"Long Term (1-2 years)","action":"Convert internship to full-time or launch a micro-SaaS","goal":"Full-time job offer or Rs 30,000+ monthly from freelancing"},
                    ],
                }


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 0  —  AI Recommendations (both modes)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🎯 AI-Powered Recommendations</div>', unsafe_allow_html=True)

recs = st.session_state.ai_recs
if recs:
    rc1, rc2, rc3 = st.columns(3)
    if IS_STUDENT_MODE:
        cards = [
            (rc1, "rec-skill",  "🎯", "TOP SKILL",      recs.get("skills", {})),
            (rc2, "rec-intern", "💼", "INTERNSHIP",      recs.get("internship", {})),
            (rc3, "rec-side",   "💰", "SIDE INCOME",     recs.get("side_income", {})),
        ]
    else:
        cards = [
            (rc1, "rec-career",  "🚀", "CAREER PATH",   recs.get("career", {})),
            (rc2, "rec-invest",  "📈", "INVESTMENT",     recs.get("investment", {})),
            (rc3, "rec-finance", "💡", "FINANCIAL TIP",  recs.get("financial_tip", {})),
        ]
    for col, css_class, icon, label, data in cards:
        col.markdown(f"""
        <div class="rec-card {css_class}">
            <span class="rec-icon">{icon}</span>
            <div class="rec-type">{label}</div>
            <div class="rec-title">{data.get('title','—')}</div>
            <div class="rec-body">{data.get('body','—')}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("👈 Click **Generate My Dashboard** in the sidebar to get personalised AI recommendations.")

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  ██████████████  STUDENT MODE  ██████████████
# ─────────────────────────────────────────────────────────────────────────────
if IS_STUDENT_MODE:

    stu = st.session_state.student_data

    # ── Banner
    st.markdown(f"""
    <div class="student-banner">
        <div class="banner-icon">🎓</div>
        <div>
            <div class="banner-title">Student Growth Dashboard</div>
            <div class="banner-sub">
                You're in Student Mode — no investment sections are shown because you have no income yet.
                Instead, here's your personalised roadmap to build skills, land internships, and earn your first income.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SKILL RECOMMENDATIONS TABLE
    st.markdown('<div class="section-header">🎯 Skill Recommendations</div>', unsafe_allow_html=True)

    skills = (stu or {}).get("skills", [])
    if skills:
        skill_rows = ""
        for sk in skills:
            diff = sk.get("difficulty", "Beginner")
            diff_cls = "badge-low" if diff == "Beginner" else ("badge-medium" if diff == "Intermediate" else "badge-high")
            skill_rows += (
                "<tr>"
                f"<td><div class='bold'>{sk.get('name','—')}</div></td>"
                f"<td style='font-size:0.78rem;color:#94a3b8;'>{sk.get('why','—')}</td>"
                f"<td style='font-size:0.78rem;color:#a855f7;'>{sk.get('resource','—')}</td>"
                f"<td><span class='badge {diff_cls}'>{diff}</span></td>"
                f"<td style='font-family:Space Mono,monospace;font-size:0.78rem;color:#06b6d4;'>{sk.get('time','—')}</td>"
                "</tr>"
            )
        skill_table_html = (
            "<div class='table-wrap'>"
            "<table class='fin-table'>"
            "<thead><tr>"
            "<th>Skill</th><th>Why Learn It</th><th>Free Resource</th><th>Level</th><th>Time</th>"
            "</tr></thead>"
            f"<tbody>{skill_rows}</tbody>"
            "</table></div>"
        )
        render_html(skill_table_html, height=185)

    # ── INTERNSHIP SUGGESTIONS
    st.markdown('<div class="section-header">💼 Internship Opportunities</div>', unsafe_allow_html=True)

    internships = (stu or {}).get("internships", [])
    int_col1, int_col2 = st.columns([3, 2])

    with int_col1:
        if internships:
            int_rows = ""
            for it in internships:
                int_rows += (
                    "<tr>"
                    f"<td><div class='bold'>{it.get('company','—')}</div></td>"
                    f"<td style='color:#06b6d4;font-size:0.82rem;'>{it.get('role','—')}</td>"
                    f"<td style='font-size:0.78rem;color:#94a3b8;'>{it.get('platform','—')}</td>"
                    f"<td style='font-family:Space Mono,monospace;font-size:0.78rem;color:#00f5a0;font-weight:700;'>{it.get('stipend','—')}</td>"
                    f"<td style='font-size:0.78rem;color:#a855f7;'>{it.get('skills_needed','—')}</td>"
                    "</tr>"
                )
            int_table_html = (
                "<div class='table-wrap'>"
                "<table class='fin-table'>"
                "<thead><tr>"
                "<th>Company</th><th>Role</th><th>Platform</th><th>Stipend</th><th>Skills Needed</th>"
                "</tr></thead>"
                f"<tbody>{int_rows}</tbody>"
                "</table></div>"
            )
            render_html(int_table_html, height=185)

    with int_col2:
        # Bar chart: stipend ranges
        if internships:
            companies = [i.get("company","").split()[0] for i in internships]
            # Extract midpoint from stipend string for chart
            stipends = []
            for it in internships:
                s = it.get("stipend","0")
                nums = [int(x.replace(",","")) for x in __import__("re").findall(r"[\d,]+", s)]
                stipends.append(int(sum(nums)/len(nums)) if nums else 10000)

            fig_int = go.Figure(go.Bar(
                x=companies, y=stipends,
                marker=dict(color=["#a855f7","#06b6d4","#0ea5e9"], line=dict(width=0)),
                text=[f"₹{v:,}" for v in stipends],
                textposition="outside",
                textfont=dict(family="Space Mono", size=10, color="#e2e8f0"),
            ))
            fig_int.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Inter"),
                xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                yaxis=dict(showgrid=True, gridcolor="rgba(30,45,61,0.6)", tickprefix="₹", tickfont=dict(size=10)),
                margin=dict(l=0, r=0, t=20, b=10), height=200, showlegend=False,
                title=dict(text="Avg. Stipend Comparison", font=dict(size=11, color="#64748b"), x=0),
            )
            st.plotly_chart(fig_int, use_container_width=True, config={"displayModeBar": False})

    # ── SIDE INCOME IDEAS
    st.markdown('<div class="section-header">💰 Side Income Ideas</div>', unsafe_allow_html=True)

    side_ideas = (stu or {}).get("side_income", [])
    si_cols = st.columns(3)
    effort_icons = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
    for i, idea in enumerate(side_ideas[:3]):
        effort = idea.get("effort","Medium")
        si_cols[i].markdown(f"""
        <div class="student-card">
            <div class="gold-tag">💰 SIDE INCOME</div>
            <div class="student-card-title">{idea.get('idea','—')}</div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                <span style="font-family:'Space Mono',monospace;font-size:0.78rem;color:#00f5a0;font-weight:700;">{idea.get('earning','—')}</span>
                <span style="font-size:0.75rem;color:#64748b;">{effort_icons.get(effort,'🟡')} {effort} effort</span>
            </div>
            <div class="student-card-body">
                <b style="color:#f59e0b;">Platform:</b> {idea.get('platform','—')}<br>
                {idea.get('how','—')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── CAREER ROADMAP
    st.markdown('<div class="section-header">🗺️ Career Roadmap</div>', unsafe_allow_html=True)

    roadmap = (stu or {}).get("roadmap", [])
    rd_col1, rd_col2 = st.columns([3, 2])

    with rd_col1:
        if roadmap:
            steps_html = ""
            for i, step in enumerate(roadmap, 1):
                steps_html += f"""
                <div class="roadmap-step">
                    <div class="step-num">{i}</div>
                    <div class="step-content">
                        <div class="step-title">{step.get('phase','—')}</div>
                        <div class="step-body">
                            <b>Action:</b> {step.get('action','—')}<br>
                            <b style="color:#00f5a0;">Goal:</b> {step.get('goal','—')}
                        </div>
                    </div>
                </div>
                """
            roadmap_html = f"""
            <div class="table-wrap" style="padding:0.5rem 0.5rem 0.5rem 1rem;">
                {steps_html}
            </div>
            """
            render_html(roadmap_html, height=320)

    with rd_col2:
        # Radar / progress chart
        phases   = [s.get("phase","").split("(")[0].strip() for s in roadmap]
        progress = [25, 50, 75, 100][:len(roadmap)]
        fig_rd = go.Figure()
        fig_rd.add_trace(go.Bar(
            x=progress, y=phases,
            orientation="h",
            marker=dict(
                color=["#a855f7","#0ea5e9","#06b6d4","#00f5a0"][:len(phases)],
                line=dict(width=0),
            ),
            text=[f"{p}%" for p in progress],
            textposition="inside",
            textfont=dict(family="Space Mono", size=10, color="#fff"),
        ))
        fig_rd.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Inter"),
            xaxis=dict(showgrid=False, range=[0,110], tickfont=dict(size=10)),
            yaxis=dict(showgrid=False, tickfont=dict(size=10)),
            margin=dict(l=0, r=10, t=20, b=10), height=220, showlegend=False,
            title=dict(text="Roadmap Progress Target", font=dict(size=11, color="#64748b"), x=0),
        )
        st.plotly_chart(fig_rd, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  ██████████████  FINANCIAL MODE  ██████████████
# ─────────────────────────────────────────────────────────────────────────────
else:

    # ── SECTION 1: STOCKS
    st.markdown('<div class="section-header">📊 Stock Recommendations</div>', unsafe_allow_html=True)

    stocks = st.session_state.stocks or []
    col_tbl, col_chart = st.columns([3, 2])

    with col_tbl:
        if stocks:
            def _stock_row(s):
                chg   = s.get("change_pct", 0)
                clr   = "#22c55e" if chg >= 0 else "#ef4444"
                sym   = "&#9650;" if chg >= 0 else "&#9660;"
                risk  = s.get("risk_level", "Medium")
                b_cls = "badge-low" if risk=="Low" else ("badge-medium" if risk=="Medium" else "badge-high")
                return (
                    "<tr>"
                    f"<td><div class='bold'>{s.get('stock_name','—')}</div>"
                    f"<div class='small muted mono'>{s.get('ticker','')}</div></td>"
                    f"<td><span class='small muted'>{s.get('sector','—')}</span></td>"
                    f"<td style='font-size:0.78rem;color:#94a3b8;'>{s.get('reason','—')}</td>"
                    f"<td><span class='badge {b_cls}'>{risk}</span></td>"
                    f"<td><div class='mono bold'>&#8377;{s.get('current_price',0):,}</div>"
                    f"<div class='small' style='color:{clr};'>{sym} {abs(chg)}%</div></td>"
                    "</tr>"
                )
            rows_html = "".join(_stock_row(s) for s in stocks)
            stock_table = (
                "<div class='table-wrap'><table class='fin-table'>"
                "<thead><tr>"
                "<th>Stock</th><th>Sector</th><th>Reason</th><th>Risk</th><th>Price</th>"
                "</tr></thead>"
                f"<tbody>{rows_html}</tbody>"
                "</table></div>"
            )
            render_html(stock_table, height=185)

    with col_chart:
        if stocks:
            names   = [s.get("stock_name","").split()[0] for s in stocks]
            prices  = [s.get("current_price", 0) for s in stocks]
            changes = [s.get("change_pct", 0) for s in stocks]
            colors  = ["#00f5a0" if c >= 0 else "#ef4444" for c in changes]
            fig_s = go.Figure(go.Bar(
                x=names, y=prices,
                marker=dict(color=colors, line=dict(width=0)),
                text=[f"₹{p:,}" for p in prices],
                textposition="outside",
                textfont=dict(family="Space Mono", size=11, color="#e2e8f0"),
            ))
            fig_s.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Inter"),
                xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                yaxis=dict(showgrid=True, gridcolor="rgba(30,45,61,0.6)", tickprefix="₹", tickfont=dict(size=10)),
                margin=dict(l=0, r=0, t=20, b=10), height=240, showlegend=False,
            )
            st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar": False})

    # ── SECTION 2: MUTUAL FUNDS
    st.markdown('<div class="section-header">🏦 Mutual Fund Suggestions</div>', unsafe_allow_html=True)

    mfs = st.session_state.mfs or []
    if mfs:
        def _mf_row(f):
            risk  = f.get("risk_level", "Medium")
            b_cls = "badge-low" if risk=="Low" else ("badge-medium" if risk=="Medium" else "badge-high")
            return (
                "<tr>"
                f"<td><div class='bold'>{f.get('fund_name','—')}</div>"
                f"<div class='small muted'>{f.get('amc','')}</div></td>"
                f"<td><span class='small muted'>{f.get('category','—')}</span></td>"
                f"<td style='font-family:Space Mono,monospace;font-size:0.82rem;color:#00f5a0;font-weight:700;'>{f.get('expected_return','—')}</td>"
                f"<td><span class='badge {b_cls}'>{risk}</span></td>"
                f"<td style='font-family:Space Mono,monospace;font-size:0.82rem;color:#f59e0b;'>&#8377;{f.get('min_sip',500):,}/mo</td>"
                f"<td style='font-size:0.78rem;color:#94a3b8;'>{f.get('reason','—')}</td>"
                "</tr>"
            )
        mf_rows_html = "".join(_mf_row(f) for f in mfs)
        mf_table = (
            "<div class='table-wrap'><table class='fin-table'>"
            "<thead><tr>"
            "<th>Fund Name</th><th>Category</th><th>Expected Return</th><th>Risk</th><th>Min SIP</th><th>Why?</th>"
            "</tr></thead>"
            f"<tbody>{mf_rows_html}</tbody>"
            "</table></div>"
        )
        render_html(mf_table, height=185)

    # ── SECTION 3: INSURANCE
    st.markdown('<div class="section-header">🛡️ Insurance Plans</div>', unsafe_allow_html=True)

    insurance = st.session_state.insurance or []
    ins_col1, ins_col2 = st.columns(2)
    ins_cols = [ins_col1, ins_col2]
    for i, plan in enumerate(insurance[:2]):
        benefits_html = "".join(
            [f'<div class="insurance-benefit">{b}</div>' for b in plan.get("benefits", [])]
        )
        ins_cols[i].markdown(f"""
        <div class="insurance-card">
            <div class="insurance-company">🏢 {plan.get('company','—')} · {plan.get('plan_type','—')}</div>
            <div class="insurance-plan">{plan.get('plan_name','—')}</div>
            {benefits_html}
            <div class="insurance-premium">
                <div>
                    <div class="premium-label">Sum Assured</div>
                    <div style="font-size:0.85rem;color:#e2e8f0;margin-top:2px;">{plan.get('sum_assured','—')}</div>
                </div>
                <div style="text-align:right;">
                    <div class="premium-label">Est. Premium</div>
                    <div class="premium-value">{plan.get('estimated_premium','—')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── SECTION 4: FINANCIAL HEALTH GRAPH
    st.markdown('<div class="section-header">📉 Financial Health Overview</div>', unsafe_allow_html=True)

    gh1, gh2 = st.columns([2, 3])

    with gh1:
        invest_target  = max(0, int(savings * 0.4))
        actual_savings = max(0, savings - invest_target)
        fig_pie = go.Figure(go.Pie(
            labels=["Expenses", "Savings", "Investments (Target)"],
            values=[expenses, actual_savings, invest_target],
            hole=0.55,
            marker=dict(colors=["#ef4444","#00f5a0","#0ea5e9"], line=dict(color="#080c14", width=3)),
            textfont=dict(family="Inter", size=11, color="#e2e8f0"),
            hovertemplate="<b>%{label}</b><br>₹%{value:,}<br>%{percent}<extra></extra>",
        ))
        fig_pie.add_annotation(
            text=f"<b>₹{income:,}</b><br>Income",
            x=0.5, y=0.5, showarrow=False,
            font=dict(family="Space Mono", size=11, color="#e2e8f0"),
        )
        fig_pie.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Inter"),
            margin=dict(l=0, r=0, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0.1, font=dict(size=11, color="#94a3b8")),
            height=280,
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with gh2:
        categories = ["Housing","Food","Transport","Utilities","Entertainment","Savings"]
        alloc = ([int(expenses*0.30), int(expenses*0.25), int(expenses*0.10),
                  int(expenses*0.08), int(expenses*0.12), savings]
                 if expenses > 0 else [0]*6)
        fig_bar = go.Figure(go.Bar(
            x=categories, y=alloc,
            marker=dict(color=["#0ea5e9","#a855f7","#f59e0b","#06b6d4","#ec4899","#00f5a0"], line=dict(width=0)),
            text=[f"₹{v:,}" for v in alloc],
            textposition="outside",
            textfont=dict(family="Space Mono", size=10, color="#e2e8f0"),
        ))
        fig_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Inter"),
            xaxis=dict(showgrid=False, tickfont=dict(size=11)),
            yaxis=dict(showgrid=True, gridcolor="rgba(30,45,61,0.6)", tickprefix="₹", tickfont=dict(size=10)),
            margin=dict(l=0, r=0, t=25, b=10), height=280, showlegend=False,
            title=dict(text="Estimated Monthly Budget Breakdown", font=dict(size=12, color="#64748b"), x=0),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  CHATBOT  (both modes)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🤖 FinPilotAI Chatbot</div>', unsafe_allow_html=True)

chatbot_system = f"""You are FinPilotAI, an expert AI financial and career advisor.
{"You are in STUDENT MODE. Focus on career, skills, internships, and side income. Do NOT recommend stocks or mutual funds." if IS_STUDENT_MODE else ""}
You provide personalised, actionable advice based on the user's profile.
Always be concise, friendly, and specific. Use Indian Rupee (Rs or ₹) for currency.
Format responses clearly; use bullet points when listing items.

{profile_context}
"""

# Build chat HTML
if st.session_state.chat_history:
    chat_html = ""
    for msg in st.session_state.chat_history:
        role_cls   = "user" if msg["role"] == "user" else ""
        avatar_cls = "avatar-user" if msg["role"] == "user" else "avatar-bot"
        icon       = "👤" if msg["role"] == "user" else "⚡"
        bubble_cls = "user-bubble" if msg["role"] == "user" else ""
        chat_html += f"""
        <div class="chat-bubble {role_cls}">
            <div class="avatar {avatar_cls}">{icon}</div>
            <div>
                <div class="bubble-text {bubble_cls}">{msg['content']}</div>
                <div class="bubble-time">{msg.get('time','')}</div>
            </div>
        </div>
        """
else:
    fname = profile['name'].split()[0]
    welcome = (
        f"Hello {fname}! 🎓 I'm FinPilotAI. I see you're a student — I can help you with skills, internships, side income ideas, and career planning. What would you like to explore?"
        if IS_STUDENT_MODE else
        f"Hello {fname}! 👋 I'm FinPilotAI. I can help you with investments, career growth, and money management. What would you like to explore today?"
    )
    chat_html = f"""
    <div class="chat-bubble">
        <div class="avatar avatar-bot">⚡</div>
        <div>
            <div class="bubble-text">{welcome}</div>
            <div class="bubble-time">Just now</div>
        </div>
    </div>
    """

st.markdown(f"""
<div class="chat-container">
    <div class="chat-header">
        <div class="avatar avatar-bot" style="width:36px;height:36px;">⚡</div>
        <div>
            <div class="chat-bot-name">FinPilotAI Assistant {'🎓' if IS_STUDENT_MODE else ''}</div>
            <div class="chat-bot-status">● Online · Powered by DeepSeek · {'Student Mode' if IS_STUDENT_MODE else 'Finance Mode'}</div>
        </div>
    </div>
    <div class="chat-messages">{chat_html}</div>
</div>
""", unsafe_allow_html=True)

# Suggestion pills (mode-specific)
if IS_STUDENT_MODE:
    suggestions = ["Best skills for AI jobs?", "How to get first internship?", "Side income as a student?", "Build a LinkedIn profile?", "Best free courses?"]
else:
    suggestions = ["Best stocks for me?", "How to grow savings?", "Best career path?", "Explain SIP vs lump sum", "Emergency fund advice?"]

pill_html = "".join([f'<span class="suggestion-pill">{s}</span>' for s in suggestions])
st.markdown(f"""
<div style="margin-bottom:0.75rem;">
    <div style="font-size:0.7rem;color:#475569;margin-bottom:0.4rem;text-transform:uppercase;letter-spacing:0.08em;">Quick Questions</div>
    {pill_html}
</div>
""", unsafe_allow_html=True)

# Chat input
chat_col1, chat_col2 = st.columns([6, 1])
with chat_col1:
    placeholder_text = (
        "Ask about skills, internships, career, or side income…"
        if IS_STUDENT_MODE else
        "Ask about finance, investments, or career…"
    )
    user_input = st.text_input(
        "chat_input", placeholder=placeholder_text,
        label_visibility="collapsed", key="chat_text",
    )
with chat_col2:
    send_btn = st.button("Send →", key="send_chat")

if send_btn and user_input.strip():
    now = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({"role":"user","content":user_input.strip(),"time":now})
    api_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
    with st.spinner("FinPilotAI is thinking…"):
        reply = get_ai_response_with_history(api_msgs, system=chatbot_system)
    st.session_state.chat_history.append({"role":"assistant","content":reply,"time":datetime.now().strftime("%I:%M %p")})
    st.rerun()

if st.session_state.chat_history:
    if st.button("🗑️ Clear conversation"):
        st.session_state.chat_history = []
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding:1.5rem 0 0.5rem 0;border-top:1px solid #1e2d3d;
            display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
    <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.9rem;color:#00f5a0;">⚡ FinPilotAI</div>
    <div style="font-size:0.7rem;color:#334155;">AI-powered · For educational purposes only · Not financial advice</div>
    <div style="font-family:'Space Mono',monospace;font-size:0.68rem;color:#334155;">v2.0 · DeepSeek via OpenRouter</div>
</div>
""", unsafe_allow_html=True)
import streamlit as st
import requests
import time
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LegalAI Pro · Contract Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "AI-Contract-Risk-Compliance-Assistant v2.0"},
)

API_URL = "http://127.0.0.1:8000"

# ─────────────────────────────────────────────
#  GLOBAL CSS  — Glossy / Premium Legal Tech
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ══ Fonts ══════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ══ Design Tokens ══════════════════════════════════════════ */
:root {
    --navy:        #07090f;
    --navy-2:      #0c0f1c;
    --navy-3:      #121628;
    --glass:       rgba(18, 22, 40, 0.72);
    --glass-light: rgba(255,255,255,0.035);
    --glass-hover: rgba(255,255,255,0.055);
    --gold:        #c9a84c;
    --gold-2:      #e8c97a;
    --gold-3:      #f5e0a0;
    --gold-glow:   rgba(201,168,76,0.18);
    --gold-glow2:  rgba(201,168,76,0.08);
    --teal:        #2dd4bf;
    --red:         #f87171;
    --green:       #4ade80;
    --border:      rgba(201,168,76,0.16);
    --border-2:    rgba(255,255,255,0.07);
    --text-1:      #f0ece0;
    --text-2:      #9b9789;
    --text-3:      #4a4840;
    --r:           14px;
    --r2:          22px;
}

/* ══ Base ════════════════════════════════════════════════════ */
html, body, .stApp {
    background: var(--navy) !important;
    color: var(--text-1) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Animated ambient orbs */
.stApp::before {
    content: '';
    position: fixed;
    width: 900px; height: 900px;
    top: -300px; left: -200px;
    background: radial-gradient(circle, rgba(201,168,76,0.06) 0%, transparent 65%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    animation: orb1 18s ease-in-out infinite alternate;
}
.stApp::after {
    content: '';
    position: fixed;
    width: 700px; height: 700px;
    bottom: -200px; right: -100px;
    background: radial-gradient(circle, rgba(45,212,191,0.04) 0%, transparent 65%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    animation: orb2 22s ease-in-out infinite alternate;
}
@keyframes orb1 {
    from { transform: translate(0,0) scale(1); }
    to   { transform: translate(80px,60px) scale(1.15); }
}
@keyframes orb2 {
    from { transform: translate(0,0) scale(1); }
    to   { transform: translate(-60px,-80px) scale(1.2); }
}

/* ══ Hide Streamlit chrome ═══════════════════════════════════ */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"]   { display: none !important; }
[data-testid="stDecoration"]{ display: none !important; }

/* ══ Sidebar ═════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080b17 0%, #07090f 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-1) !important; }
[data-testid="stSidebarContent"] { padding: 1.25rem 1rem !important; }

/* ══ Typography ══════════════════════════════════════════════ */
h1,h2,h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--text-1) !important;
}

/* ══ Text Inputs ═════════════════════════════════════════════ */
.stTextInput input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border-2) !important;
    border-radius: var(--r) !important;
    color: var(--text-1) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    transition: all 0.25s ease !important;
    backdrop-filter: blur(8px) !important;
}
.stTextInput input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px var(--gold-glow), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    background: rgba(255,255,255,0.06) !important;
}
.stTextInput input::placeholder { color: var(--text-3) !important; }
label[data-testid="stWidgetLabel"] p {
    color: var(--text-2) !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

/* ══ Buttons ═════════════════════════════════════════════════ */
.stButton > button {
    background: var(--glass) !important;
    border: 1px solid var(--border-2) !important;
    color: var(--text-2) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    border-radius: var(--r) !important;
    letter-spacing: 0.05em !important;
    transition: all 0.2s ease !important;
    backdrop-filter: blur(10px) !important;
}
.stButton > button:hover {
    border-color: var(--gold) !important;
    color: var(--gold-2) !important;
    background: var(--gold-glow2) !important;
    box-shadow: 0 0 24px var(--gold-glow), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #a07830 0%, #c9a84c 45%, #e8c97a 100%) !important;
    border: none !important;
    color: #07090f !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.07em !important;
    box-shadow: 0 4px 24px rgba(201,168,76,0.35), inset 0 1px 0 rgba(255,255,255,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 36px rgba(201,168,76,0.5), inset 0 1px 0 rgba(255,255,255,0.3) !important;
    color: #07090f !important;
}

/* ══ Checkbox ════════════════════════════════════════════════ */
.stCheckbox label p { color: var(--text-2) !important; font-size: 0.78rem !important; }

/* ══ File Uploader ═══════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: var(--r2) !important;
    background: var(--glass) !important;
    backdrop-filter: blur(12px) !important;
    transition: all 0.3s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--gold) !important;
    background: var(--gold-glow2) !important;
    box-shadow: 0 0 32px var(--gold-glow) !important;
}

/* ══ Chat ════════════════════════════════════════════════════ */
[data-testid="stChatMessage"] {
    background: var(--glass) !important;
    border: 1px solid var(--border-2) !important;
    border-radius: var(--r2) !important;
    backdrop-filter: blur(12px) !important;
    margin-bottom: 0.65rem !important;
}
[data-testid="stChatInput"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    backdrop-filter: blur(12px) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text-1) !important;
    font-family: 'Inter', sans-serif !important;
}

/* ══ Metrics ═════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: var(--glass) !important;
    border: 1px solid var(--border-2) !important;
    border-radius: var(--r2) !important;
    backdrop-filter: blur(16px) !important;
    padding: 1.3rem 1.5rem !important;
    transition: all 0.25s ease !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stMetric"]::before {
    content:'';
    position:absolute;
    top:0;left:0;right:0;height:1px;
    background: linear-gradient(90deg,transparent,rgba(201,168,76,0.4),transparent);
}
[data-testid="stMetric"]:hover {
    border-color: rgba(201,168,76,0.3) !important;
    box-shadow: 0 0 32px var(--gold-glow), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-2) !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.7rem !important;
    color: var(--gold-2) !important;
    text-shadow: 0 0 20px var(--gold-glow) !important;
}

/* ══ Containers ══════════════════════════════════════════════ */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 1px solid var(--border-2) !important;
    border-radius: var(--r2) !important;
    background: var(--glass) !important;
    backdrop-filter: blur(16px) !important;
    padding: 1.5rem !important;
    box-shadow: 0 4px 40px rgba(0,0,0,0.4), inset 0 1px 0 var(--glass-light) !important;
}

/* ══ Progress ════════════════════════════════════════════════ */
.stProgress > div { background: rgba(255,255,255,0.06) !important; border-radius: 99px !important; }
.stProgress > div > div {
    background: linear-gradient(90deg, var(--gold), var(--gold-2), var(--gold-3)) !important;
    border-radius: 99px !important;
    box-shadow: 0 0 12px var(--gold-glow) !important;
}

/* ══ Radio ═══════════════════════════════════════════════════ */
[data-testid="stRadio"] label {
    color: var(--text-2) !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    transition: color 0.2s !important;
}
[data-testid="stRadio"] label:hover { color: var(--gold-2) !important; }

/* ══ Alerts ══════════════════════════════════════════════════ */
.stAlert  { border-radius: var(--r) !important; backdrop-filter: blur(8px) !important; }
.stInfo   { background: rgba(45,212,191,0.06)  !important; border-color: rgba(45,212,191,0.25) !important; }
.stSuccess{ background: rgba(74,222,128,0.06)  !important; border-color: rgba(74,222,128,0.25) !important; }
.stError  { background: rgba(248,113,113,0.06) !important; border-color: rgba(248,113,113,0.25) !important; }
.stWarning{ background: rgba(201,168,76,0.06)  !important; border-color: rgba(201,168,76,0.25) !important; }

/* ══ Spinner ═════════════════════════════════════════════════ */
.stSpinner > div { border-top-color: var(--gold) !important; }

/* ══ Scrollbar ═══════════════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(201,168,76,0.25); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold); }

/* ══ Selectbox ═══════════════════════════════════════════════ */
div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border-2) !important;
    border-radius: var(--r) !important;
    backdrop-filter: blur(8px) !important;
    color: var(--text-1) !important;
}
div[data-baseweb="popover"] {
    background: var(--navy-3) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
}
div[data-baseweb="option"]:hover {
    background: var(--gold-glow2) !important;
    color: var(--gold-2) !important;
}

/* ══ Markdown ════════════════════════════════════════════════ */
.stMarkdown p, .stMarkdown li { color: var(--text-2) !important; line-height: 1.78 !important; }
.stMarkdown strong { color: var(--gold-2) !important; }
.stMarkdown code {
    font-family: 'JetBrains Mono', monospace !important;
    background: var(--gold-glow2) !important;
    color: var(--gold-2) !important;
    border-radius: 5px !important;
    padding: 0.1em 0.45em !important;
    font-size: 0.82em !important;
}
hr { border: none !important; border-top: 1px solid var(--border-2) !important; margin: 1.5rem 0 !important; }
button[data-testid="InputInstructionsButton"] { color: var(--text-3) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  UTILITY HELPERS
# ─────────────────────────────────────────────
def typewriter(text: str):
    box = st.empty()
    out = ""
    for ch in text:
        out += ch
        box.markdown(out + "▌")
        time.sleep(0.0012)
    box.markdown(out)


def gloss_hr(opacity: float = 0.12):
    st.markdown(
        f"<hr style='border:none;border-top:1px solid rgba(201,168,76,{opacity});margin:1.4rem 0;'>",
        unsafe_allow_html=True,
    )


def page_header(title: str, sub: str = ""):
    st.markdown(f"""
    <div style="margin-bottom:1.75rem;">
        <span style="font-family:'Playfair Display',serif;font-size:2rem;
                     font-weight:700;color:#f0ece0;">{title}</span>
        {"" if not sub else f'<p style="font-size:0.76rem;color:#4a4840;letter-spacing:0.08em;margin:4px 0 0;">{sub}</p>'}
        <div style="width:44px;height:2px;margin-top:10px;
                    background:linear-gradient(90deg,#c9a84c,transparent);
                    border-radius:99px;"></div>
    </div>
    """, unsafe_allow_html=True)


def section_label(text: str):
    st.markdown(
        f"<p style='font-size:0.66rem;font-weight:600;letter-spacing:0.15em;"
        f"color:#4a4840;text-transform:uppercase;margin:1.4rem 0 0.5rem;'>{text}</p>",
        unsafe_allow_html=True,
    )


def badge(text: str, color: str = "#c9a84c"):
    r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    return (f"<span style='background:rgba({r},{g},{b},0.12);color:{color};"
            f"border:1px solid {color}33;border-radius:99px;font-size:0.67rem;"
            f"font-weight:600;letter-spacing:0.08em;text-transform:uppercase;"
            f"padding:3px 11px;'>{text}</span>")


def svc_chip(label: str, ok: bool):
    c  = "#4ade80" if ok else "#f87171"
    ic = "✓" if ok else "✗"
    r  = "74,222,128" if ok else "248,113,113"
    return (f"<div style='padding:5px 10px;border-radius:8px;font-size:0.71rem;"
            f"background:rgba({r},0.07);border:1px solid rgba({r},0.22);"
            f"color:{c};margin-bottom:4px;'>{ic} {label}</div>")


import inspect
def engine_card(icon, label, desc, active, btn_key):
    border = "rgba(201,168,76,0.5)"  if active else "rgba(255,255,255,0.07)"
    bg     = "rgba(201,168,76,0.07)" if active else "rgba(255,255,255,0.025)"
    glow   = "0 0 28px rgba(201,168,76,0.2),inset 0 1px 0 rgba(255,255,255,0.05)" if active else "none"
    tc     = "#e8c97a" if active else "#9b9789"
    top_line = ("<div style='position:absolute;top:0;left:0;right:0;height:1px;"
                "background:linear-gradient(90deg,transparent,rgba(201,168,76,0.6),transparent);'></div>"
                if active else "Not Selected")
    st.markdown(f"""
    <div style="border:1px solid {border};border-radius:16px;background:{bg};
                padding:1.05rem 1.1rem;box-shadow:{glow};position:relative;
                overflow:hidden;transition:all 0.25s;">
        {top_line}
        <div style="font-size:1.5rem;margin-bottom:6px;">{icon}</div>
        <div style="font-weight:600;color:{tc};font-size:0.83rem;
                    letter-spacing:0.04em;">{label}</div>
        <div style="font-size:0.7rem;color:#4a4840;margin-top:3px;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)
    lbl = f"✓  {label}" if active else f"Select {label}"
    if st.button(lbl, key=btn_key, use_container_width=True):
        st.session_state.model_choice = btn_key.replace("eng_", "")
        st.rerun()

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
DEFAULTS: dict = {
    "logged_in":          False,
    "username":           "",
    "user_info":          None,
    "analysis_done":      False,
    "summary":            "",
    "current_session_id": None,
    "messages":           [],
    "analysis_history":   [],   # [{filename, session_id, model, timestamp, summary, q_count}]
    "model_choice":       "flash",
    "auth_tab":           "login",
    "_jump_to_agent":     False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Handle dashboard → agent nav jump
if st.session_state._jump_to_agent:
    st.session_state._jump_to_agent = False
    st.query_params["page"] = "agent"


# ═════════════════════════════════════════════════════════════
#  🔐  AUTH PAGE  (Login + Register)
# ═════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    _, mid, _ = st.columns([1, 1.05, 1])
    with mid:
        st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)

        # ── Brand mark ───────────────────────────────────────
        st.markdown("""
        <div style="text-align:center;margin-bottom:2.4rem;">
            <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:8px;">
                <div style="width:42px;height:42px;border-radius:11px;
                            background:linear-gradient(135deg,#8c6520,#c9a84c,#e8c97a);
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.25rem;
                            box-shadow:0 4px 20px rgba(201,168,76,0.45),
                                       inset 0 1px 0 rgba(255,255,255,0.3);">⚖</div>
                <span style="font-family:'Playfair Display',serif;font-size:2rem;
                             font-weight:700;color:#f0ece0;letter-spacing:0.02em;">LegalAI</span>
                <span style="font-size:0.62rem;letter-spacing:0.2em;color:#4a4840;
                             border:1px solid rgba(201,168,76,0.22);border-radius:99px;
                             padding:3px 9px;margin-top:4px;font-weight:600;">PRO</span>
            </div>
            <p style="font-size:0.68rem;letter-spacing:0.22em;color:#4a4840;
                      text-transform:uppercase;margin:0;">
                Contract Risk &amp; Compliance Intelligence
            </p>
            <div style="width:56px;height:1px;margin:12px auto 0;
                        background:linear-gradient(90deg,transparent,#c9a84c,transparent);"></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Glass card ────────────────────────────────────────
        st.markdown("""
        <div style="background:rgba(12,15,28,0.8);
                    border:1px solid rgba(255,255,255,0.08);
                    border-radius:24px;padding:2rem;
                    backdrop-filter:blur(24px);
                    box-shadow:0 24px 80px rgba(0,0,0,0.6),
                               inset 0 1px 0 rgba(255,255,255,0.05);">
        """, unsafe_allow_html=True)

        # ── Tab switch ────────────────────────────────────────
        t1, t2 = st.columns(2)
        is_login = st.session_state.auth_tab == "login"
        with t1:
            if st.button("Sign In", key="sw_login", use_container_width=True,
                         type="primary" if is_login else "secondary"):
                st.session_state.auth_tab = "login"; st.rerun()
        with t2:
            if st.button("Create Account", key="sw_reg", use_container_width=True,
                         type="primary" if not is_login else "secondary"):
                st.session_state.auth_tab = "register"; st.rerun()

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ════════════ LOGIN ═══════════════════════════════════
        if is_login:
            st.markdown("""
            <p style="font-size:0.67rem;letter-spacing:0.15em;color:#4a4840;
                      text-transform:uppercase;margin-bottom:1rem;">Secure Portal</p>
            """, unsafe_allow_html=True)

            u_val = st.text_input("Username", placeholder="your_username", key="li_u")
            p_val = st.text_input("Password", placeholder="••••••••",
                                  type="password", key="li_p")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            if st.button("Access Dashboard  →", use_container_width=True,
                         type="primary", key="btn_li"):
                if not u_val or not p_val:
                    st.warning("Please enter username and password.")
                else:
                    with st.spinner("Authenticating…"):
                        try:
                            r = requests.post(
                                f"{API_URL}/api/login",
                                json={"username": u_val, "password": p_val},
                                timeout=8,
                            )
                            if r.status_code == 200:
                                st.session_state.logged_in = True
                                st.session_state.user_info = r.json().get("user_info", {})
                                st.session_state.username  = u_val
                                st.rerun()
                            elif r.status_code == 401:
                                st.error("❌  Invalid username or password.")
                            else:
                                st.error(f"Login failed: {r.json().get('detail','Unknown error')}")
                        except requests.exceptions.ConnectionError:
                            st.error("⚠️  Backend offline — launch main.py first.")
                        except Exception as ex:
                            st.error(f"Error: {ex}")

            st.markdown("""
            <p style="text-align:center;font-size:0.72rem;color:#4a4840;margin-top:1rem;">
                No account yet? Click <strong style="color:#c9a84c;">Create Account</strong> above.
            </p>""", unsafe_allow_html=True)

        # ════════════ REGISTER ════════════════════════════════
        else:
            st.markdown("""
            <p style="font-size:0.67rem;letter-spacing:0.15em;color:#4a4840;
                      text-transform:uppercase;margin-bottom:1rem;">New Account</p>
            """, unsafe_allow_html=True)

            ca, cb = st.columns(2)
            with ca: r_name = st.text_input("Full Name",  placeholder="Vivek Sharma",   key="rg_n")
            with cb: r_user = st.text_input("Username",   placeholder="vivek123",        key="rg_u")
            r_email = st.text_input("Email Address", placeholder="you@company.com",      key="rg_e")
            cp, cq  = st.columns(2)
            with cp: r_pw1  = st.text_input("Password",         placeholder="••••••••", type="password", key="rg_p1")
            with cq: r_pw2  = st.text_input("Confirm Password", placeholder="••••••••", type="password", key="rg_p2")

            # Inline password strength bar
            if r_pw1:
                s = sum([len(r_pw1)>=8, any(c.isdigit() for c in r_pw1),
                         any(c.isupper() for c in r_pw1),
                         any(c in "!@#$%^&*" for c in r_pw1)])
                s_lbl = ["Weak","Fair","Good","Strong"][max(s-1,0)]
                s_col = ["#f87171","#fb923c","#facc15","#4ade80"][max(s-1,0)]
                s_w   = ["25%","50%","75%","100%"][max(s-1,0)]
                st.markdown(f"""
                <div style="margin:6px 0 10px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <span style="font-size:0.67rem;color:#4a4840;">Password strength</span>
                        <span style="font-size:0.67rem;color:{s_col};font-weight:600;">{s_lbl}</span>
                    </div>
                    <div style="height:3px;background:rgba(255,255,255,0.06);border-radius:99px;">
                        <div style="height:3px;width:{s_w};background:{s_col};border-radius:99px;
                                    box-shadow:0 0 8px {s_col}55;transition:width .3s,background .3s;">
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="rg_agree")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            if st.button("Create My Account  →", use_container_width=True,
                         type="primary", key="btn_reg"):
                errs = []
                if not all([r_name, r_user, r_email, r_pw1, r_pw2]):
                    errs.append("All fields are required.")
                if r_pw1 != r_pw2:
                    errs.append("Passwords do not match.")
                if r_pw1 and len(r_pw1) < 6:
                    errs.append("Password must be at least 6 characters.")
                if r_email and "@" not in r_email:
                    errs.append("Enter a valid email address.")
                if not agree:
                    errs.append("You must accept the Terms of Service.")
                if errs:
                    for e in errs: st.error(e)
                else:
                    with st.spinner("Creating your account…"):
                        try:
                            r = requests.post(
                                f"{API_URL}/api/register",
                                json={"username": r_user, "email": r_email,
                                      "password": r_pw1, "name": r_name},
                                timeout=8,
                            )
                            if r.status_code == 200:
                                st.success(f"✅  Account created! Welcome, {r_name}. Please sign in.")
                                st.session_state.auth_tab = "login"
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error(f"❌  {r.json().get('detail','Registration failed.')}")
                        except requests.exceptions.ConnectionError:
                            st.error("⚠️  Backend offline — launch main.py first.")
                        except Exception as ex:
                            st.error(f"Error: {ex}")

        st.markdown("</div>", unsafe_allow_html=True)  # close glass card

        st.markdown("""
        <p style="text-align:center;font-size:0.6rem;color:#2a2820;margin-top:1.2rem;
                  letter-spacing:0.05em;">
            🔒 AES-256 encrypted · SOC 2 compliant · LegalAI Pro v2.0
        </p>""", unsafe_allow_html=True)

    st.stop()


# ═════════════════════════════════════════════════════════════
#  🧭  SIDEBAR  (authenticated)
# ═════════════════════════════════════════════════════════════
ui = st.session_state.user_info or {}
display_name = ui.get("name", st.session_state.username)
initials = "".join(w[0].upper() for w in display_name.split()[:2]) or "?"

with st.sidebar:
    # Logo block
    st.markdown("""
    <div style="padding:0.2rem 0 1.2rem;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
            <div style="width:30px;height:30px;border-radius:8px;
                        background:linear-gradient(135deg,#8c6520,#e8c97a);
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.88rem;box-shadow:0 2px 10px rgba(201,168,76,0.4);">⚖</div>
            <span style="font-family:'Playfair Display',serif;font-size:1.4rem;
                         font-weight:700;color:#f0ece0;">LegalAI</span>
            <span style="font-size:0.58rem;letter-spacing:0.14em;color:#4a4840;
                         border:1px solid rgba(201,168,76,0.18);border-radius:99px;
                         padding:2px 7px;margin-top:2px;">PRO</span>
        </div>
        <div style="height:1px;background:linear-gradient(90deg,rgba(201,168,76,0.28),transparent);
                    margin-top:9px;"></div>
    </div>
    """, unsafe_allow_html=True)

    # User identity card
    st.markdown(f"""
    <div style="background:rgba(201,168,76,0.06);border:1px solid rgba(201,168,76,0.16);
                border-radius:14px;padding:0.85rem 1rem;margin-bottom:1.1rem;
                box-shadow:inset 0 1px 0 rgba(255,255,255,0.04);">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:36px;height:36px;border-radius:10px;flex-shrink:0;
                        background:linear-gradient(135deg,#8c6520,#c9a84c);
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.85rem;font-weight:700;color:#07090f;">{initials}</div>
            <div>
                <div style="font-weight:600;color:#e8c97a;font-size:0.87rem;
                            line-height:1.2;">{display_name}</div>
                <div style="font-size:0.67rem;color:#4a4840;margin-top:2px;">
                    @{st.session_state.username}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Health check
    section_label("System Status")
    if st.button("⟳  Refresh Services", use_container_width=True):
        try:
            h = requests.get(f"{API_URL}/health?refresh=true", timeout=4).json()
            back = h.get("backend", {})
            st.markdown(
                svc_chip("FastAPI Backend", True)
                + svc_chip("Gemini API",    back.get("gemini", False))
                + svc_chip("Ollama / Local",back.get("local",  False)),
                unsafe_allow_html=True,
            )
        except Exception:
            st.error("Cannot reach backend.")

    gloss_hr(0.09)
    section_label("Navigation")

    default_i = 1 if st.query_params.get("page") == "agent" else 0
    if st.query_params.get("page") == "agent":
        st.query_params.clear()
    menu = st.radio("nav", ["🏠  Dashboard", "⚖  AI Agreement Agent"],
                    index=default_i, label_visibility="collapsed")

    gloss_hr(0.07)

    # Mini stats
    total_h = len(st.session_state.analysis_history)
    total_q = sum(e["q_count"] for e in st.session_state.analysis_history)
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:1.1rem;">
        <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);
                    border-radius:10px;padding:0.6rem 0.8rem;text-align:center;">
            <div style="font-size:0.58rem;letter-spacing:0.1em;color:#4a4840;
                        text-transform:uppercase;">Contracts</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.3rem;
                        color:#e8c97a;text-shadow:0 0 12px rgba(201,168,76,0.3);">{total_h}</div>
        </div>
        <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);
                    border-radius:10px;padding:0.6rem 0.8rem;text-align:center;">
            <div style="font-size:0.58rem;letter-spacing:0.1em;color:#4a4840;
                        text-transform:uppercase;">Questions</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.3rem;
                        color:#e8c97a;text-shadow:0 0 12px rgba(201,168,76,0.3);">{total_q}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↩  Sign Out", use_container_width=True, type="primary"):
        st.session_state.clear()
        st.rerun()

    st.markdown("""
    <p style="font-size:0.58rem;color:#2a2820;text-align:center;margin-top:0.7rem;
              letter-spacing:0.05em;">LegalAI Pro · v2.0 · AES-256</p>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
#  📊  DASHBOARD
# ═════════════════════════════════════════════════════════════
if menu == "🏠  Dashboard":
    page_header("Dashboard", "Overview of your legal intelligence workspace")

    total_h = len(st.session_state.analysis_history)
    total_q = sum(e["q_count"] for e in st.session_state.analysis_history)
    last_eng = st.session_state.analysis_history[0]["model"].upper() \
               if st.session_state.analysis_history else "—"

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Active User",        st.session_state.username.upper())
    k2.metric("Contracts Reviewed", str(total_h))
    k3.metric("Questions Asked",    str(total_q))
    k4.metric("Last Engine",        last_eng)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # ── Feature overview ──────────────────────────────────────
    section_label("Platform Capabilities")
    f1, f2, f3 = st.columns(3)

    def feat_card(col, icon, title, body, accent="#c9a84c"):
        with col:
            st.markdown(f"""
            <div style="border:1px solid rgba(255,255,255,0.07);border-radius:18px;
                        background:rgba(18,22,40,0.7);backdrop-filter:blur(16px);
                        padding:1.5rem;height:100%;position:relative;overflow:hidden;
                        box-shadow:0 4px 28px rgba(0,0,0,0.3),
                                   inset 0 1px 0 rgba(255,255,255,0.04);">
                <div style="position:absolute;top:0;left:0;right:0;height:1px;
                            background:linear-gradient(90deg,transparent,{accent}44,transparent);"></div>
                <div style="font-size:2rem;margin-bottom:0.9rem;">{icon}</div>
                <div style="font-family:'Playfair Display',serif;font-size:1.1rem;
                            font-weight:600;color:#f0ece0;margin-bottom:0.45rem;">{title}</div>
                <div style="font-size:0.79rem;color:#4a4840;line-height:1.72;">{body}</div>
            </div>
            """, unsafe_allow_html=True)

    feat_card(f1,"📄","Contract Upload & Parse",
              "Parse complex PDFs with clause-level extraction and structured risk mapping.")
    feat_card(f2,"⚠️","Risk & Compliance Scoring",
              "Flag liability clauses, penalty triggers, GDPR/HIPAA gaps, and hidden obligations.",
              "#f87171")
    feat_card(f3,"💬","Interactive Legal Q&A",
              "Ask follow-up questions about specific clauses — cited, context-aware answers instantly.",
              "#2dd4bf")

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    # ── Recent Activity ───────────────────────────────────────
    section_label("Recent Activity — from MongoDB")

    # Sync from backend (MongoDB via /api/history)
    try:
        hr = requests.get(f"{API_URL}/api/history",
                          params={"username": st.session_state.username}, timeout=3)
        if hr.status_code == 200:
            existing = {e["session_id"] for e in st.session_state.analysis_history}
            for row in hr.json().get("history", []):
                sid = row.get("session_id", "")
                if sid and sid not in existing:
                    st.session_state.analysis_history.append({
                        "filename":   row.get("filename", "Unknown"),
                        "session_id": sid,
                        "model":      row.get("model", "—"),
                        "timestamp":  row.get("timestamp", "—"),
                        "summary":    row.get("analysis", ""),
                        "q_count":    row.get("q_count", 0),
                    })
                    existing.add(sid)
    except Exception:
        pass

    ENG_ICONS = {"flash":"⚡","pro":"🧠","lite":"🪶","local":"🔒"}

    if not st.session_state.analysis_history:
        st.markdown("""
        <div style="border:2px dashed rgba(201,168,76,0.13);border-radius:20px;
                    padding:3rem;text-align:center;
                    background:rgba(18,22,40,0.65);backdrop-filter:blur(12px);">
            <div style="font-size:2.8rem;margin-bottom:0.8rem;opacity:0.35;">📂</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.25rem;color:#4a4840;">
                No contracts analysed yet
            </div>
            <div style="font-size:0.77rem;color:#2a2820;margin-top:0.5rem;">
                Go to <strong style="color:#c9a84c;">AI Agreement Agent</strong>
                to upload your first contract.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Header row
        st.markdown("""
        <div style="display:grid;grid-template-columns:2fr 0.8fr 1.1fr 0.65fr 60px;
                    gap:0.4rem;padding:0.35rem 0.75rem;
                    font-size:0.61rem;letter-spacing:0.12em;color:#4a4840;
                    text-transform:uppercase;
                    border-bottom:1px solid rgba(255,255,255,0.05);">
            <div>Contract</div><div>Engine</div>
            <div>Date &amp; Time</div><div>Q &amp; A</div><div></div>
        </div>
        """, unsafe_allow_html=True)

        for idx, entry in enumerate(st.session_state.analysis_history):
            ei = ENG_ICONS.get(entry["model"], "🤖")
            c1, c2, c3, c4, c5 = st.columns([2, 0.8, 1.1, 0.65, 0.4])
            with c1:
                st.markdown(f"""
                <div style="padding:0.65rem 0;font-size:0.83rem;color:#f0ece0;
                            font-weight:500;overflow:hidden;text-overflow:ellipsis;
                            white-space:nowrap;">📄 {entry['filename']}</div>""",
                            unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style="padding:0.65rem 0;font-size:0.79rem;color:#9b9789;">
                    {ei} {entry['model'].capitalize()}</div>""",
                            unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div style="padding:0.65rem 0;font-size:0.73rem;color:#4a4840;">
                    {entry['timestamp']}</div>""",
                            unsafe_allow_html=True)
            with c4:
                q  = entry["q_count"]
                qc = "#c9a84c" if q else "#4a4840"
                st.markdown(f"""
                <div style="padding:0.65rem 0;font-size:0.79rem;color:{qc};">
                    {q} Q</div>""",
                            unsafe_allow_html=True)
            with c5:
                if st.button("→", key=f"view_{idx}", help="Re-open this analysis"):
                    st.session_state.analysis_done      = True
                    st.session_state.summary            = entry["summary"]
                    st.session_state.current_session_id = entry["session_id"]
                    st.session_state.messages           = []
                    st.session_state._jump_to_agent     = True
                    st.rerun()

            if idx < len(st.session_state.analysis_history) - 1:
                st.markdown(
                    "<hr style='margin:0;border:none;border-top:1px solid "
                    "rgba(255,255,255,0.04);'>",
                    unsafe_allow_html=True,
                )


# ═════════════════════════════════════════════════════════════
#  ⚖  AI AGREEMENT AGENT
# ═════════════════════════════════════════════════════════════
elif menu == "⚖  AI Agreement Agent":
    page_header("AI Agreement Agent",
                "Upload a contract and run deep risk & compliance analysis")

    ENG = {
        "flash": ("⚡","Flash","Balanced speed & accuracy"),
        "pro":   ("🧠","Pro",  "Deep clause-level logic"),
        "lite":  ("🪶","Lite", "Fast, lightweight review"),
        "local": ("🔒","Local","Fully private, on-device"),
    }

    # ── Engine picker ─────────────────────────────────────────
    section_label("AI Engine")
    for col, (key, (icon, label, desc)) in zip(st.columns(4), ENG.items()):
        with col:
            engine_card(icon, label, desc,
                        st.session_state.model_choice == key, f"eng_{key}")

    model_choice = st.session_state.model_choice
    gloss_hr(0.09)

    # ── Upload ────────────────────────────────────────────────
    section_label("Document Upload")
    ufile = st.file_uploader(
        "Drag & drop contract PDF, or click to browse",
        type="pdf",
        help="NDAs, SLAs, employment agreements, vendor contracts…",
    )

    if ufile and not st.session_state.analysis_done:
        prog = st.progress(0, text="Initialising engine…")
        for pct, msg in [
            (12,  "📖  Extracting document text…"),
            (35,  "🔍  Identifying clauses & obligations…"),
            (58,  "⚠️   Running risk scoring model…"),
            (78,  "📊  Compiling compliance report…"),
            (92,  "🧠  Finalising AI annotations…"),
            (100, "✅  Analysis complete!"),
        ]:
            time.sleep(0.38)
            prog.progress(pct, text=msg)

        res = requests.post(
            f"{API_URL}/upload-pdf",
            files={"file": (ufile.name, ufile.getvalue(), "application/pdf")},
            params={"model": model_choice, "username": st.session_state.username},
        )
        if res.status_code == 200:
            data = res.json()
            st.session_state.analysis_done      = True
            st.session_state.summary            = data["analysis"]
            st.session_state.current_session_id = data["session_id"]
            st.session_state.analysis_history.insert(0, {
                "filename":   ufile.name,
                "session_id": data["session_id"],
                "model":      model_choice,
                "timestamp":  datetime.now().strftime("%d %b %Y · %H:%M"),
                "summary":    data["analysis"],
                "q_count":    0,
            })
            prog.empty()
            st.rerun()
        else:
            prog.empty()
            st.error("❌  Failed to process PDF. Check backend logs.")

    # ── Report ────────────────────────────────────────────────
    if st.session_state.analysis_done:
        icon_m, label_m, _ = ENG[model_choice]

        hc, bc = st.columns([3, 1])
        with hc: section_label("Analysis Report")
        with bc:
            st.markdown(
                f"<div style='padding-top:1.3rem;text-align:right;'>"
                + badge("Risk Assessed", "#fb923c")
                + "&nbsp;"
                + badge(f"{icon_m} {label_m}", "#c9a84c")
                + "</div>",
                unsafe_allow_html=True,
            )

        with st.container(border=True):
            st.markdown(st.session_state.summary, unsafe_allow_html=True)

        rc, _ = st.columns([1, 5])
        with rc:
            if st.button("↩  New Contract", key="reset"):
                st.session_state.analysis_done = False
                st.session_state.summary       = ""
                st.session_state.messages      = []
                st.rerun()

        gloss_hr(0.09)

        # ── Chat ─────────────────────────────────────────────
        section_label("Interactive Legal Q&A")
        chat_box = st.container(height=420)
        with chat_box:
            if not st.session_state.messages:
                st.markdown("""
                <div style="text-align:center;padding:3.5rem 0;opacity:0.35;">
                    <div style="font-size:2.2rem;margin-bottom:0.6rem;">💬</div>
                    <div style="font-size:0.79rem;letter-spacing:0.05em;color:#4a4840;">
                        Ask about clauses, obligations, penalties, or risk exposure…
                    </div>
                </div>
                """, unsafe_allow_html=True)
            for m in st.session_state.messages:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])

        if prompt := st.chat_input(
            "e.g. What are the termination clauses? Any hidden penalties?"
        ):
            st.session_state.messages.append({"role": "user", "content": prompt})
            for h in st.session_state.analysis_history:
                if h["session_id"] == st.session_state.current_session_id:
                    h["q_count"] += 1
                    break

            with chat_box:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Analysing clause context…"):
                        cr = requests.post(
                            f"{API_URL}/chat",
                            json={"session_id": st.session_state.current_session_id,
                                  "question":   prompt,
                                  "model":      model_choice},
                        ).json()
                    typewriter(cr["answer"])
                    st.session_state.messages.append(
                        {"role": "assistant", "content": cr["answer"]}
                    )

    else:
        st.markdown("""
        <div style="border:2px dashed rgba(201,168,76,0.13);border-radius:22px;
                    padding:3.5rem;text-align:center;
                    background:rgba(18,22,40,0.65);backdrop-filter:blur(14px);
                    margin-top:0.5rem;box-shadow:inset 0 1px 0 rgba(255,255,255,0.03);">
            <div style="font-size:3rem;margin-bottom:1rem;opacity:0.3;">🔒</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.4rem;
                        color:#4a4840;margin-bottom:0.6rem;">Analysis Locked</div>
            <div style="font-size:0.79rem;color:#2a2820;max-width:360px;
                        margin:0 auto;line-height:1.75;">
                Upload a contract PDF above to unlock AI-powered risk analysis,
                compliance scoring, and the interactive Q&amp;A session.
            </div>
        </div>
        """, unsafe_allow_html=True)
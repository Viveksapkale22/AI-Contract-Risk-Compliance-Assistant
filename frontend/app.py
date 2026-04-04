import streamlit as st
import requests
import time
import sys
import os

# 1. PATH INJECTOR
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- CONFIG ---
st.set_page_config(page_title="LegalAI Pro Dashboard", layout="wide")
API_URL = "http://127.0.0.1:8000"

# --- HELPER: FLOWING OUTPUT ---
def typewriter(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.002)
    container.markdown(full_text)

# --- INITIALIZE SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# 🔑 LOGIN PAGE
# =========================
if not st.session_state.logged_in:
    st.title("🛡️ LegalAI Pro Login")
    with st.container(border=True):
        u = st.text_input("Username (vivek)")
        p = st.text_input("Password (123)", type="password")
        if st.button("Access Dashboard", use_container_width=True):
            try:
                res = requests.post(f"{API_URL}/api/login", json={"username": u, "password": p})
                if res.status_code == 200:
                    st.session_state.logged_in = True
                    st.session_state.user_info = res.json()["user_info"]
                    st.session_state.username = u
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            except:
                st.error("Backend Server Offline. Please start main.py")
    st.stop()

# =========================
# 🏠 SIDEBAR & HEALTH
# =========================
with st.sidebar:
    st.title(f"👋 {st.session_state.user_info['name']}")
    st.caption(f"Logged in as: {st.session_state.username}")
    
    # --- 🟢 SYSTEM HEALTH ---
    st.divider()
    st.subheader("🌐 System Health")
    if st.button("Check Backend Services"):
        try:
            h = requests.get(f"{API_URL}/health?refresh=true").json()
            st.success(f"FastAPI: Online")
            st.write(f"Gemini API: {'✅' if h['backend']['gemini'] else '❌'}")
            st.write(f"Ollama/Local: {'✅' if h['backend']['local'] else '❌'}")
        except:
            st.error("Cannot connect to Backend.")

    st.divider()
    menu = st.radio("Navigation", ["Dashboard", "AI Agreement Agent"])
    
    if st.button("Logout", type="primary"):
        st.session_state.clear()
        st.rerun()

# =========================
# 📊 DASHBOARD PAGE
# =========================
if menu == "Dashboard":
    st.header("Project Overview")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Current User", st.session_state.username.upper())
    kpi2.metric("Legal Tasks", "Active")
    kpi3.metric("Security Status", "Encrypted")
    
    st.subheader("Your Recent Activity")
    st.info("Uploaded contracts and analysis history will appear here.")

# =========================
# 🤖 AI AGENT PAGE
# =========================
elif menu == "AI Agreement Agent":
    st.header("🤖 AI Agreement Agent")
    
    # Engine Selection Dropdown
    model_choice = st.selectbox(
        "Select AI Engine Level",
        options=["flash", "pro", "lite", "local"],
        index=0,
        help="Pro: Deep Logic | Flash: Balanced | Local: Privacy focus"
    )

    st.divider()

    # 1. UPLOAD SECTION (Full Width)
    st.subheader("1. Document Upload")
    uploaded_file = st.file_uploader("Upload Contract PDF", type="pdf")
    
    if uploaded_file and not st.session_state.analysis_done:
        with st.spinner("🧠 AI analyzing the contract..."):
            # Prepare files for the Master Upload Endpoint
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            params = {"model": model_choice, "username": st.session_state.username}
            
            res = requests.post(f"{API_URL}/upload-pdf", files=files, params=params)
            
            if res.status_code == 200:
                data = res.json()
                st.session_state.analysis_done = True
                st.session_state.summary = data["analysis"]
                st.session_state.current_session_id = data["session_id"]
                st.rerun()
            else:
                st.error("Failed to process PDF.")

    # 2. PERFECT SUMMARY BOX (Full Width)
    if st.session_state.analysis_done:
        st.markdown("### 📝 Analysis Summary & Risk Report")
        with st.container(border=True):
            st.markdown(st.session_state.summary)
        
        st.divider()

        # 3. INTERACTIVE CHAT (Bottom Layout)
        st.subheader("💬 Interactive Legal Q&A")
        chat_container = st.container(height=400)
        
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about specific clauses..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    # Call Chat Endpoint
                    chat_res = requests.post(f"{API_URL}/chat", json={
                        "session_id": st.session_state.current_session_id,
                        "question": prompt,
                        "model": model_choice
                    }).json()
                    
                    typewriter(chat_res["answer"])
                    st.session_state.messages.append({"role": "assistant", "content": chat_res["answer"]})
    else:
        st.info("🔒 Please upload a contract PDF to unlock Analysis and Chat.")
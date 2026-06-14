import streamlit as st
import requests
import time

# =========================
# 🔧 CONFIG
# =========================
st.set_page_config(page_title="LegalAI Pro Dashboard", layout="wide")

# ✅ LIVE BACKEND
API_URL = "https://ai-contract-risk-compliance-assistant.onrender.com"

# =========================
# 🎨 GLOBAL UI STYLE
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# =========================
# ✨ TYPEWRITER EFFECT
# =========================
def typewriter(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.002)
    container.markdown(full_text)

# =========================
# 🧠 SESSION STATE
# =========================
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
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Access Dashboard", use_container_width=True):
            with st.spinner("Authenticating..."):
                try:
                    res = requests.post(
                        f"{API_URL}/api/login",
                        json={"username": u, "password": p},
                        timeout=10
                    )

                    if res.status_code == 200:
                        st.session_state.logged_in = True
                        st.session_state.user_info = res.json()["user_info"]
                        st.session_state.username = u
                        st.toast("✅ Login Successful")
                        st.rerun()
                    else:
                        st.toast("❌ Invalid credentials", icon="⚠️")

                except:
                    st.error("🚫 Backend not reachable")

    st.stop()

# =========================
# 📂 SIDEBAR
# =========================
with st.sidebar:
    st.title(f"👋 {st.session_state.user_info['name']}")
    st.caption(f"User: {st.session_state.username}")

    st.divider()

    # 🔍 HEALTH CHECK
    st.subheader("🌐 System Health")
    if st.button("Check Backend"):
        with st.spinner("Checking..."):
            try:
                h = requests.get(f"{API_URL}/health?refresh=true").json()
                st.success("FastAPI: Online")
                st.write(f"Gemini: {'✅' if h['backend']['gemini'] else '❌'}")
                st.write(f"Local: {'✅' if h['backend']['local'] else '❌'}")
            except:
                st.error("Backend unreachable")

    st.divider()

    menu = st.radio("Navigation", ["Dashboard", "AI Agreement Agent"])

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# =========================
# 📊 DASHBOARD
# =========================
if menu == "Dashboard":
    st.header("📊 Project Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("User", st.session_state.username.upper())
    c2.metric("Tasks", "Active")
    c3.metric("Security", "Encrypted")

    st.info("Your activity & contract history will appear here.")

# =========================
# 🤖 AI AGENT
# =========================
elif menu == "AI Agreement Agent":
    st.header("🤖 AI Agreement Agent")

    model_choice = st.selectbox(
        "AI Engine",
        ["flash", "pro", "lite", "local"]
    )

    st.divider()

    # =========================
    # 📄 FILE UPLOAD
    # =========================
    st.subheader("📄 Upload Contract")

    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if uploaded_file and not st.session_state.analysis_done:

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf"
            )
        }

        params = {
            "model": model_choice,
            "username": st.session_state.username
        }

        with st.spinner("🧠 AI analyzing contract..."):

            try:
                # 🔁 Retry (Render cold start)
                for _ in range(3):
                    res = requests.post(
                        f"{API_URL}/upload-pdf",
                        files=files,
                        params=params,
                        timeout=120
                    )

                    if res.status_code == 200:
                        break
                    time.sleep(2)

                if res.status_code == 200:
                    data = res.json()

                    st.session_state.analysis_done = True
                    st.session_state.summary = data["analysis"]
                    st.session_state.current_session_id = data["session_id"]

                    st.success("✅ Analysis Complete")
                    st.rerun()
                else:
                    st.error("❌ Failed to process PDF")

            except requests.exceptions.Timeout:
                st.error("⏳ Server waking up, try again...")
            except Exception as e:
                st.error(f"⚠️ {str(e)}")

    # =========================
    # 📊 SUMMARY
    # =========================
    if st.session_state.analysis_done:

        st.subheader("📊 Analysis Summary")

        st.markdown(
            f"""
            <div style="padding:15px;border-radius:10px;background:#1e1e1e">
            {st.session_state.summary}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        # =========================
        # 💬 CHAT
        # =========================
        st.subheader("💬 Ask Questions")

        chat_box = st.container(height=400)

        with chat_box:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about contract..."):

            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            with chat_box:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    placeholder.markdown("🤖 Thinking...")

                    try:
                        res = requests.post(
                            f"{API_URL}/chat",
                            json={
                                "session_id": st.session_state.current_session_id,
                                "question": prompt,
                                "model": model_choice
                            },
                            timeout=60
                        )

                        if res.status_code == 200:
                            answer = res.json()["answer"]
                            typewriter(answer)

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer
                            })
                        else:
                            placeholder.error("❌ Error in response")

                    except:
                        placeholder.error("⚠️ Server not responding")

    else:
        st.info("🔒 Upload a contract to begin analysis")

import io
import uuid
import time
from pypdf import PdfReader

# 💾 SESSION STORAGE
SESSIONS = {}

def create_session(filename="text_input", model_type="gemini"):
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "id": session_id,
        "created_at": time.time(),
        "filename": filename,
        "history": [],
        "model": model_type  
    }
    return session_id

def get_session(session_id):
    return SESSIONS.get(session_id)

def add_chat(session_id, role, content):
    if session_id in SESSIONS:
        SESSIONS[session_id]["history"].append({"role": role, "content": content})

def get_formatted_history(session_id, limit=5):
    session = SESSIONS.get(session_id)
    if not session or not session.get("history"):
        return "No past conversation."
    
    history_str = ""
    for msg in session["history"][-limit:]:
        history_str += f"{msg['role'].upper()}: {msg['content']}\n"
    return history_str

# 📄 PDF TEXT EXTRACTOR
def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    if not text.strip():
        raise ValueError("No readable text found")
    return text
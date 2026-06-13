import io
import uuid
import time
from pypdf import PdfReader
from mongo_connection import create_mongo_session, add_mongo_chat, get_mongo_session

def create_session(filename="text_input", model_type="gemini"):
    session_id = str(uuid.uuid4())
    # Save directly to MongoDB instead of memory
    create_mongo_session(session_id, filename, model_type)
    return session_id

def get_session(session_id):
    # Fetch from MongoDB
    return get_mongo_session(session_id)

def add_chat(session_id, role, content):
    # Append directly to MongoDB document
    add_mongo_chat(session_id, role, content)

def get_formatted_history(session_id, limit=5):
    session = get_mongo_session(session_id)
    if not session or not session.get("history"):
        return "No past conversation."
    
    history_str = ""
    # Get only the most recent messages up to the limit
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
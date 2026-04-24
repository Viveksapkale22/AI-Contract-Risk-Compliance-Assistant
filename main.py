# main.py
import os
import time
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv

# 1. 🛡️ STRONG ENVIRONMENT LOADING
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# Debug print to console on startup
print("--- 🛡️ ENVIRONMENT SECURITY CHECK ---")
if ENV_PATH.exists():
    api_key = os.getenv("GEMINI_API_KEY")
    status = f"FOUND ✅ ({api_key[:4]}...{api_key[-4:]})" if api_key else "KEY MISSING ❌"
    print(f"-> .env at: {ENV_PATH}\n-> Status: {status}")
else:
    print(f"-> Status: .env NOT FOUND AT {ENV_PATH} ❌")
print("------------------------------------\n")


# 2. 🧠 INTERNAL IMPORTS
from backend_logic.utils import create_session, add_chat, extract_text_from_pdf
from backend_logic.rag import load_pdf_from_bytes, chunk_documents, get_embeddings, create_vectorstore
from backend_logic.analysis_agreement import process_contract
from backend_logic.chat_service import chat_with_rag
from backend_logic.model_provider import ai_manager

# 🔥 MONGODB IMPORTS (Replacing the old auth logic)
from mongo_connection import (
    create_user, verify_user, 
    save_analysis_history, get_user_history, increment_q_count
)

# 3. 🚀 APP INITIALIZATION
app = FastAPI(title="Contract Analysis & RAG Chat")

# --- Pydantic Data Models ---
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    name: str

class ChatRequest(BaseModel):
    session_id: str
    question: str
    model: str = "flash"


# --- 🟢 HEALTH CHECK ---
@app.get("/health")
def health(refresh: bool = False):
    status = ai_manager.check_health(force=refresh)
    return {"status": "online", "backend": status}


# ==========================================
# 🔐 AUTHENTICATION ENDPOINTS
# ==========================================

# And update the /api/register endpoint:
@app.post("/api/register")
def register(request: RegisterRequest):
    """Register a new user in MongoDB."""
    result = create_user(
        username=request.username, 
        email=request.email, 
        password=request.password, 
        name=request.name
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/api/login")
def login(request: LoginRequest):
    """Authenticate a user via MongoDB."""
    result = verify_user(request.username, request.password)
    if result["status"] == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    return result


# ==========================================
# 📜 HISTORY ENDPOINT
# ==========================================

@app.get("/api/history")
def get_history(username: str):
    """Returns the user's past uploaded contracts for the Dashboard."""
    history = get_user_history(username)
    return {"history": history}


# ==========================================
# 📄 MASTER PDF UPLOAD
# ==========================================

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...), 
    model: str = "flash", 
    username: str = "vivek"
):
    try:
        # 1. Read binary data
        file_bytes = await file.read()
        db_mode = "local" if model == "local" else "gemini"
        
        # 2. Create session logic
        session_id = create_session(file.filename, db_mode)
        
        # 3. Text Extraction & Deep Legal Analysis
        raw_text = extract_text_from_pdf(file_bytes)
        analysis_result = process_contract(raw_text, model)
        
        # 4. RAG PIPELINE (Indexing for Chat)
        documents = load_pdf_from_bytes(file_bytes)
        chunks = chunk_documents(documents)
        embeddings = ai_manager.get_embeddings(db_mode)
        create_vectorstore(chunks, embeddings, session_id, db_mode)
        
        # 5. Store the analysis as the first 'System' message for RAG context
        add_chat(session_id, "system", analysis_result)

        # 6. SAVE TO MONGODB PERMANENTLY
        save_analysis_history(
            username=username,
            session_id=session_id,
            filename=file.filename,
            model=model,
            analysis=analysis_result
        )

        return {
            "status": "success",
            "session_id": session_id,
            "filename": file.filename,
            "analysis": analysis_result,
            "database_used": db_mode,
            "user_history": get_user_history(username) # Return their updated history list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Error: {str(e)}")


# ==========================================
# 💬 CHAT / RAG SYSTEM
# ==========================================

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        # Save user message context
        add_chat(request.session_id, "user", request.question)
        
        # Get AI Response via RAG
        response = chat_with_rag(request.session_id, request.question, request.model)
        
        # Save AI message context
        add_chat(request.session_id, "assistant", response)

        # INCREMENT THE QUESTION COUNT IN MONGODB
        increment_q_count(request.session_id)
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "answer": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat Error: {str(e)}")
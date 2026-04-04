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

# 3. 🚀 APP INITIALIZATION (Only define this ONCE!)
app = FastAPI(title="Contract Analysis & RAG Chat")

class ChatRequest(BaseModel):
    session_id: str
    question: str
    model: str = "flash" # Supports flash, pro, gemma, lite, local

# --- 🟢 HEALTH CHECK ---
@app.get("/health")
def health(refresh: bool = False):
    status = ai_manager.check_health(force=refresh)
    return {"status": "online", "backend": status}





from backend_logic.auth import authenticate_user, link_session_to_user, get_user_sessions, LoginRequest

# --- 🔑 LOGIN ENDPOINT ---
@app.post("/api/login")
def login(request: LoginRequest):
    result = authenticate_user(request)
    if result["status"] == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    return result

# --- 📄 UPDATED UPLOAD (Now with Username) ---# --- 📄 MASTER PDF UPLOAD (Linked to User + RAG + Analysis) ---
@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...), 
    model: str = "flash", 
    username: str = "vivek" # Received from Streamlit/Frontend
):
    try:
        # 1. Read binary data
        file_bytes = await file.read()
        db_mode = "local" if model == "local" else "gemini"
        
        # 2. Create session and link it to the User's History
        session_id = create_session(file.filename, db_mode)
        link_session_to_user(username, session_id, file.filename)
        
        # 3. Text Extraction & Deep Legal Analysis
        raw_text = extract_text_from_pdf(file_bytes)
        analysis_result = process_contract(raw_text, model)
        
        # 4. RAG PIPELINE (Indexing for Chat)
        # This part ensures that when you chat, it actually looks at the PDF
        documents = load_pdf_from_bytes(file_bytes)
        chunks = chunk_documents(documents)
        embeddings = ai_manager.get_embeddings(db_mode)
        create_vectorstore(chunks, embeddings, session_id, db_mode)
        
        # 5. Store the analysis as the first 'System' message in history
        add_chat(session_id, "system", analysis_result)

        return {
            "status": "success",
            "session_id": session_id,
            "filename": file.filename,
            "analysis": analysis_result,
            "database_used": db_mode,
            "user_history": get_user_sessions(username) # Sends back list of all their PDFs
        }
        
    except Exception as e:
        # Robust error catching for the frontend
        raise HTTPException(status_code=500, detail=f"Upload Error: {str(e)}")

        
# --- 💬 CHAT / RAG OPTION ---
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        # Save user message
        add_chat(request.session_id, "user", request.question)
        
        # Get AI Response via RAG
        response = chat_with_rag(request.session_id, request.question, request.model)
        
        # Save AI message
        add_chat(request.session_id, "assistant", response)
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "answer": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat Error: {str(e)}")
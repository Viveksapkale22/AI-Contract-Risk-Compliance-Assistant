import uuid
from typing import Dict, List, Optional
from pydantic import BaseModel

# --- DUMMY DATABASE ---
# In a real app, this would be SQLite/PostgreSQL
USERS_DB: Dict[str, dict] = {
    "vivek": {
        "password": "123",
        "full_name": "Vivek D. Sapkale",
        "email": "vivek@example.com",
        "sessions": []  # List of session_ids (PDFs) uploaded by this user
    }
}

class LoginRequest(BaseModel):
    username: str
    password: str

def authenticate_user(login: LoginRequest):
    """Checks if user exists and password matches."""
    user = USERS_DB.get(login.username.lower())
    if user and user["password"] == login.password:
        return {
            "status": "success",
            "user_info": {
                "username": login.username,
                "name": user["full_name"],
                "email": user["email"]
            }
        }
    return {"status": "error", "message": "Invalid username or password"}

def link_session_to_user(username: str, session_id: str, filename: str):
    """Connects a new PDF upload to the user's history."""
    if username.lower() in USERS_DB:
        USERS_DB[username.lower()]["sessions"].append({
            "session_id": session_id,
            "filename": filename,
            "timestamp": uuid.uuid4().hex[:6] # Simple unique tag
        })

def get_user_sessions(username: str):
    """Retrieves all PDFs previously uploaded by this user."""
    return USERS_DB.get(username.lower(), {}).get("sessions", [])
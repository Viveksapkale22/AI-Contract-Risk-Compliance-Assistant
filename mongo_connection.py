# mongo_connection.py
import pymongo
from pymongo import MongoClient
from datetime import datetime
import bcrypt

# --- MongoDB Setup ---
MONGO_URI = "mongodb+srv://viveksapkale0022_db_user:ldvBxaR6509CEkBG@cluster0.hgkqkwy.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["legalai_database"]

# Collections
users_collection = db["users"]
history_collection = db["analysis_history"]

# Indexes (Makes lookups fast and enforces uniqueness)
users_collection.create_index([("username", pymongo.ASCENDING)], unique=True)
history_collection.create_index([("session_id", pymongo.ASCENDING)], unique=True)


# ==========================================
# 🔐 AUTHENTICATION & REGISTRATION
# ==========================================

# Inside mongo_connection.py

# ==========================================
# 🔐 AUTHENTICATION & REGISTRATION
# ==========================================

def create_user(username: str, email: str, password: str, name: str):
    """Registers a new user with email and hashed password."""
    if users_collection.find_one({"username": username}):
        return {"status": "error", "message": "Username already exists"}
    if users_collection.find_one({"email": email}):
        return {"status": "error", "message": "Email already exists"}
    
    # 🛠️ FIX: Use raw bcrypt, encode to bytes, truncate to 72 chars to prevent crashes
    encoded_password = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(encoded_password, salt).decode('utf-8')
    
    users_collection.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password,
        "name": name,
        "created_at": datetime.now()
    })
    return {"status": "success", "message": "User registered successfully"}

def verify_user(username: str, password: str):
    """Verifies a user's password during login."""
    user = users_collection.find_one({"username": username})
    
    if not user:
        return {"status": "error", "message": "Invalid username or password"}
    
    # 🛠️ FIX: Verify using raw bcrypt
    encoded_password = password[:72].encode('utf-8')
    stored_hash = user["password"].encode('utf-8')
    
    if not bcrypt.checkpw(encoded_password, stored_hash):
        return {"status": "error", "message": "Invalid username or password"}
    
    return {
        "status": "success",
        "user_info": {
            "username": user["username"],
            "name": user.get("name", username)
        }
    }

# ==========================================
# 📜 HISTORY & SESSION LOGIC
# ==========================================

def save_analysis_history(username: str, session_id: str, filename: str, model: str, analysis: str):
    """Saves a newly processed contract into MongoDB."""
    record = {
        "username": username,
        "session_id": session_id,
        "filename": filename,
        "model": model,
        "timestamp": datetime.now().strftime("%d %b %Y · %H:%M"),
        "analysis": analysis,
        "q_count": 0
    }
    try:
        history_collection.insert_one(record)
    except pymongo.errors.DuplicateKeyError:
        pass # Ignore if it somehow tries to save twice

def get_user_history(username: str) -> list:
    """Fetches all history for a specific user, newest first."""
    records = list(history_collection.find(
        {"username": username},
        {"_id": 0} # Hide internal MongoDB ID from FastAPI
    ).sort("timestamp", pymongo.DESCENDING))
    return records

def increment_q_count(session_id: str):
    """Atomically increments the Q&A counter."""
    history_collection.update_one(
        {"session_id": session_id},
        {"$inc": {"q_count": 1}}
    )
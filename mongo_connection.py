# mongo_connection.py
import os
import pymongo
from pymongo import MongoClient
from datetime import datetime
import bcrypt
from gridfs import GridFS



# --- MongoDB Setup ---
# Prefer MONGO_URI from environment; fall back to embedded URI if not set (repo previously contained one).
DEFAULT_MONGO_URI = "mongodb+srv://viveksapkale0022_db_user:ldvBxaR6509CEkBG@cluster0.hgkqkwy.mongodb.net/?appName=Cluster0"
MONGO_URI = os.getenv("MONGO_URI", DEFAULT_MONGO_URI)
client = MongoClient(MONGO_URI)
db = client["legalai_database"]

# GridFS for file storage
fs = GridFS(db)

# Collections
users_collection = db["users"]
history_collection = db["analysis_history"]

# Indexes (Makes lookups fast and enforces uniqueness)
users_collection.create_index([("username", pymongo.ASCENDING)], unique=True)
history_collection.create_index([("session_id", pymongo.ASCENDING)], unique=True)
sessions_collection = db["sessions"]
sessions_collection.create_index([("session_id", pymongo.ASCENDING)], unique=True)


# ==========================================
# 🔐 AUTHENTICATION & REGISTRATION
# ==========================================

# Inside mongo_connection.py

# ==========================================
# 🔐 AUTHENTICATION & REGISTRATION
# ==========================================

# --- Find your existing create_user function and update the insert_one block ---
def create_user(username: str, email: str, password: str, name: str):
    """Registers a new user with email and hashed password."""
    # 1. Check if user already exists
    if users_collection.find_one({"username": username}):
        return {"status": "error", "message": "Username already exists"}
    if users_collection.find_one({"email": email}):
        return {"status": "error", "message": "Email already exists"}
    
    # 2. Hash the password securely using bcrypt (THIS WAS MISSING!)
    encoded_password = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(encoded_password, salt).decode('utf-8')
    
    # 3. Save to MongoDB with the default "free" tier
    users_collection.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password,
        "name": name,
        "tier": "free",
        "created_at": datetime.now()
    })
    return {"status": "success", "message": "User registered successfully"}
# --- Add these two NEW functions at the bottom of the file ---

def can_user_upload(username: str) -> bool:
    """Checks if a user is allowed to upload based on their tier."""
    user = users_collection.find_one({"username": username})
    if not user:
        return False
        
    # Pro users have no limits
    if user.get("tier") == "pro":
        return True
        
    # Free users: Count how many PDFs they already have in the history collection
    count = history_collection.count_documents({"username": username})
    return count < 1  # Returns True if they have 0 uploads, False if they have 1 or more

def upgrade_user_to_pro(username: str):
    """Upgrades a user's account to the Pro tier."""
    users_collection.update_one(
        {"username": username},
        {"$set": {"tier": "pro"}}
    )
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
            "name": user.get("name", username),
            "tier": user.get("tier", "free")
        }
    }

# ==========================================
# 📜 HISTORY & SESSION LOGIC
# ==========================================

def save_file_to_gridfs(username: str, session_id: str, filename: str, file_bytes: bytes):
    """Stores uploaded file in GridFS and returns the stored file_id (string) or None on failure."""
    try:
        file_id = fs.put(file_bytes, filename=filename, username=username, session_id=session_id, upload_date=datetime.now())
        return str(file_id)
    except Exception:
        return None


def save_analysis_history(username: str, session_id: str, filename: str, model: str, analysis: str, file_id: str = None):
    """Saves a newly processed contract into MongoDB. Optionally links to GridFS file_id."""
    record = {
        "username": username,
        "session_id": session_id,
        "filename": filename,
        "model": model,
        "timestamp": datetime.now().strftime("%d %b %Y · %H:%M"),
        "analysis": analysis,
        "q_count": 0
    }
    if file_id:
        record["file_id"] = file_id
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


def get_history_record(session_id: str):
    """Fetch a single history record by session_id (no _id)."""
    rec = history_collection.find_one({"session_id": session_id}, {"_id": 0})
    return rec


def get_file_by_session(session_id: str):
    """Retrieve file stored in GridFS by session_id. Returns dict with bytes, filename, and username or None."""
    # GridFS stores extra kwargs at the top-level of the file document; find the latest file for this session
    grid_out = fs.find_one({"session_id": session_id})
    if not grid_out:
        return None
    file_bytes = grid_out.read()
    # filename is available as attribute; metadata like username/session_id are stored in the raw file document
    filename = getattr(grid_out, "filename", None) or grid_out._file.get("filename")
    username = grid_out._file.get("username") if grid_out._file else None
    return {"file_bytes": file_bytes, "filename": filename, "username": username}


# ==========================================
# 💬 CHAT SESSIONS & HISTORY (Replaces in-memory SESSIONS)
# ==========================================

def create_mongo_session(session_id: str, filename: str, model_type: str):
    """Creates a new persistent chat session."""
    sessions_collection.insert_one({
        "session_id": session_id,
        "filename": filename,
        "model_type": model_type,
        "history": [],
        "created_at": datetime.now()
    })

def add_mongo_chat(session_id: str, role: str, content: str):
    """Appends a new message to the session's history."""
    sessions_collection.update_one(
        {"session_id": session_id},
        {"$push": {"history": {"role": role, "content": content}}}
    )

def get_mongo_session(session_id: str):
    """Retrieves the full session document."""
    return sessions_collection.find_one({"session_id": session_id}, {"_id": 0})    


# ==========================================
# 🧠 FAISS VECTOR STORAGE VIA GRIDFS
# ==========================================

def save_faiss_to_gridfs(session_id: str, index_bytes: bytes, pkl_bytes: bytes):
    """Saves the two FAISS local files into MongoDB GridFS."""
    # Delete older versions if they exist to prevent bloating
    for f in fs.find({"session_id": session_id, "file_type": {"$in": ["faiss_index", "faiss_pkl"]}}):
        fs.delete(f._id)
        
    fs.put(index_bytes, filename=f"{session_id}_index.faiss", session_id=session_id, file_type="faiss_index")
    fs.put(pkl_bytes, filename=f"{session_id}_index.pkl", session_id=session_id, file_type="faiss_pkl")

def load_faiss_from_gridfs(session_id: str):
    """Retrieves the FAISS index and pkl files from GridFS."""
    index_file = fs.find_one({"session_id": session_id, "file_type": "faiss_index"})
    pkl_file = fs.find_one({"session_id": session_id, "file_type": "faiss_pkl"})
    
    if not index_file or not pkl_file:
        return None
        
    return index_file.read(), pkl_file.read()


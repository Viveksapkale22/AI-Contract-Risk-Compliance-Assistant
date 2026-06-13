import os
import io
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Import BOTH embedding models
from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend_logic.model_provider import ai_manager
import tempfile
from mongo_connection import save_faiss_to_gridfs, load_faiss_from_gridfs



load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


# 1. Load PDF
def load_pdf_from_bytes(file_bytes: bytes):
    documents = []
    reader = PdfReader(io.BytesIO(file_bytes))
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():  
            documents.append(Document(page_content=text, metadata={"page": page_num + 1}))
    return documents

# 2. Chunk
def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    return splitter.split_documents(documents)


def get_embeddings(model_type: str):
    # Just ask the manager!
    return ai_manager.get_embeddings(model_type)

# ... (keep your PDF loading and FAISS logic as is)

def get_db_path(model_type, session_id):
    # This ensures it always finds the storage folder inside backend_logic
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "storage", "faiss_index", model_type, session_id)
# 4. Vectorstore Management (Now powered by MongoDB GridFS)
def create_vectorstore(chunks, embeddings, session_id, model_type):
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Save locally to a temporary directory just long enough to read the bytes
    with tempfile.TemporaryDirectory() as temp_dir:
        vectorstore.save_local(temp_dir)
        
        with open(os.path.join(temp_dir, "index.faiss"), "rb") as f:
            index_bytes = f.read()
        with open(os.path.join(temp_dir, "index.pkl"), "rb") as f:
            pkl_bytes = f.read()
            
    # Push those bytes permanently into MongoDB
    save_faiss_to_gridfs(session_id, index_bytes, pkl_bytes)
    return vectorstore

def get_retriever(session_id, embeddings, model_type, k=4):
    # Pull the bytes from MongoDB
    files = load_faiss_from_gridfs(session_id)
    if not files:
        raise FileNotFoundError(f"Vectorstore for session {session_id} not found in MongoDB GridFS.")
        
    index_bytes, pkl_bytes = files
    
    # Drop them in a temporary directory for FAISS to load
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "index.faiss"), "wb") as f:
            f.write(index_bytes)
        with open(os.path.join(temp_dir, "index.pkl"), "wb") as f:
            f.write(pkl_bytes)
            
        vectorstore = FAISS.load_local(temp_dir, embeddings, allow_dangerous_deserialization=True)
        
    return vectorstore.as_retriever(search_kwargs={"k": k})
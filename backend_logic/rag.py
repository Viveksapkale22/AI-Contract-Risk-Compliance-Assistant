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

# 4. Vectorstore Management
def create_vectorstore(chunks, embeddings, session_id, model_type):
    vectorstore = FAISS.from_documents(chunks, embeddings)
    session_path = get_db_path(model_type, session_id)
    os.makedirs(session_path, exist_ok=True)
    vectorstore.save_local(session_path)
    return vectorstore

def get_retriever(session_id, embeddings, model_type, k=4):
    session_path = get_db_path(model_type, session_id)
    if not os.path.exists(session_path):
        raise FileNotFoundError(f"Vectorstore for session {session_id} not found in {model_type} storage.")
    vectorstore = FAISS.load_local(session_path, embeddings, allow_dangerous_deserialization=True)
    return vectorstore.as_retriever(search_kwargs={"k": k})
from backend_logic.rag import get_embeddings, get_retriever
from backend_logic.utils import get_formatted_history, get_session
from backend_logic.model_provider import ai_manager # <--- Add this

def chat_with_rag(session_id: str, user_query: str, request_model: str = "auto") -> str:
    try:
        # 1. Get Session Data
        session = get_session(session_id)
        db_model = session.get("model", "gemini") if session else "gemini"
        
        # 2. Get the correct embeddings and search the database
        embeddings = get_embeddings(db_model)
        retriever = get_retriever(session_id, embeddings, db_model, k=4)
        
        # 3. Retrieve context from FAISS
        docs = retriever.invoke(user_query)
        context = "\n\n".join([d.page_content for d in docs])
        
        # 4. Get Past Chat History
        history = get_formatted_history(session_id, limit=5)
        
        # 5. DEFINE THE PROMPT (This was the missing part!)
        prompt = f"""You are an expert contract analyst. 

=== PAST CONVERSATION ===
{history}

=== CONTRACT CONTEXT ===
{context}

=== CURRENT QUESTION ===
{user_query}

INSTRUCTIONS:
Answer ONLY based on the CONTRACT CONTEXT above. If the answer is NOT in the context, don't say explicitly  "Information not found in the provided contract context." Do not guess try to ask them and provide the correct valid answer.
"""
        
        # 6. Generate the answer
        return ai_manager.generate(prompt, request_model)
        
    except Exception as e:
        # This will now catch and show any other errors specifically
        return f"❌ Error during chat: {str(e)}"
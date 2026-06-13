# Copilot instructions for AI-Contract-Risk-Compliance-Assistant

Purpose: give future Copilot sessions repository-specific guidance so suggestions and automated edits are accurate.

---

## Build, run, test, and lint (repo-specific)

Prereqs: Python 3.10+ and a virtualenv. Install dependencies:

- pip install -r requirements.txt

Backend (FastAPI)
- Start dev server: uvicorn main:app --reload --host 127.0.0.1 --port 8000
  - main:app is the entrypoint at the repository root.

Frontend (Streamlit)
- Start UI: streamlit run frontend/app.py
- The frontend auto-detects BACKEND_API_URL env var. If not set, it uses http://127.0.0.1:8000.

Tests & Lint
- No test suite or linter configuration detected in the repository. If tests are added, run a single test with pytest like:
  - pytest path/to/test_file.py::test_name

---

## High-level architecture (big picture)

- Root FastAPI app (main.py): exposes endpoints used by the Streamlit frontend and by programmatic clients. Key endpoints: /health, /api/register, /api/login, /api/history, /upload-pdf, /chat.

- backend_logic/ (core backend modules):
  - utils.py: in-memory session store (SESSIONS), session creation, PDF text extraction.
  - rag.py: PDF -> Document list -> chunking (RecursiveCharacterTextSplitter) -> FAISS vectorstore creation and retrieval. Persistence path: backend_logic/storage/faiss_index/<model>/<session_id>.
  - model_provider.py: Model routing and embedding providers. Singleton ai_manager exposes:
    - get_embeddings(model_type)
    - generate(prompt, model_choice)
    - check_health(force=False) (checks ollama local at localhost:11434 and Gemini API via the client)
  - chat_service.py: Builds RAG prompt, composes past history + retrieved context, and calls ai_manager.generate for chat responses.
  - analysis_agreement.py: Crafts the structured contract analysis prompt used on initial upload (process_contract).

- mongo_connection.py: MongoDB client, user registration/login, history storage, q_count increment. (Note: current code hard-codes a MONGO_URI in this file.)

- frontend/app.py: Streamlit UI with design tokens and runtime routing logic (BACKEND_API_URL overrides). Uses Streamlit page config and custom CSS.

- model and RAG flow:
  - Upload PDF -> extract_text_from_pdf (utils) -> process_contract (analysis) -> load_pdf_from_bytes + chunk_documents -> create_vectorstore (FAISS) -> store system message in session history and persist analysis in MongoDB.
  - Chat: add user message to session history, retrieve with FAISS retriever, build prompt, call ai_manager.generate, persist assistant answer and increment q_count in MongoDB.

---

## Key conventions and repository-specific patterns

- Model routing keys: 'flash', 'pro', 'gemma', 'lite', 'embed' are the keys used in ai_manager.MODEL_MAP. Use these keys when specifying models in API calls.

- Model selection strings used in code:
  - session.model == 'local' or 'gemini' (a session's model selects embedding and LLM routing).
  - The upload endpoint maps request.model == 'local' to internal db_mode 'local', otherwise 'gemini'.

- FAISS storage layout:
  - backend_logic/storage/faiss_index/<model_type>/<session_id>
  - create_vectorstore saves with FAISS.save_local; load uses FAISS.load_local with allow_dangerous_deserialization=True.

- Embeddings and LLMs:
  - ai_manager.get_embeddings('local') returns OllamaEmbeddings; any other value returns GoogleGenerativeAIEmbeddings with GEMINI_API_KEY.
  - ai_manager.generate routes to local Ollama when model_choice == 'local'; otherwise, it routes to the Gemini client using MODEL_MAP.

- Prompting / non-hallucination rules:
  - The analysis_agreement.process_contract prompt and chat_service.chat_with_rag both enforce: "Use ONLY information from the contract" or to state when the contract does not specify something. Copilot-driven changes that alter prompt intent must preserve this guardrail.

- Sessions and history:
  - Sessions are in-memory (backend_logic.utils.SESSIONS). create_session returns a UUID and stores history as an array of messages. This is ephemeral — the persistent record is saved in MongoDB via save_analysis_history.

- Password handling:
  - mongo_connection.truncates passwords to 72 chars before encoding for bcrypt compatibility. Keep this behavior when editing auth logic.

- Health checks:
  - ai_manager.check_health pings a local Ollama server at http://localhost:11434 and uses client.models.generate_content for a lightweight Gemini model ('lite'). Tests/automation that rely on health checks should account for both providers.

- Environment variables used by the codebase (check .env in development):
  - GEMINI_API_KEY — required for Gemini/Google Generative API paths.
  - BACKEND_API_URL — optional override used by frontend.
  - Note: mongo_connection.py currently contains a hard-coded MONGO_URI. Moving it to an env var (MONGO_URI) is recommended if changing code; any Copilot suggestions that modify or remove secrets must not leak values into the repo.

- Frontend routing:
  - The Streamlit app uses BACKEND_API_URL if provided; otherwise it talks to http://127.0.0.1:8000. Keep that override intact when changing frontend networking.

---

## Existing docs & AI assistant rule files

- No README.md or CONTRIBUTING.md detected in the repository root.
- No CLAUDE.md, AGENTS.md, .cursorrules, .windsurfrules, or other AI assistant rule files were found.

If those are added later, consider copying authentication and model routing snippets into them so AI agents can reason about runtime behavior.

---

## Quick editing rules for Copilot sessions (summary)

- Preserve the non-hallucination instructions in prompts (analysis_agreement.py and chat_service.py).
- Preserve the model key names used in MODEL_MAP and session.model values ('local' vs 'gemini').
- When touching Mongo logic, do not commit real credentials — prefer reading MONGO_URI from env if changing code.
- Respect in-memory session behavior: modifications that move session storage to a DB must also update add_chat/get_formatted_history usages.

---

If this file should be expanded with examples (curl requests, typical payloads, or adding test commands once a test framework is present), say which area to cover and Copilot can append examples.


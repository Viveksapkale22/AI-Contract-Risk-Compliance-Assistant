import os
import requests
import time
from google import genai
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Path handling to find .env in the Project Root
current_folder = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(current_folder), ".env"), override=True)

class ModelProvider:
    def __init__(self):
        # 1. API Keys & Clients
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        
        # 2. YOUR MODEL REGISTRY (Matches your API Dashboard)
        self.MODEL_MAP = {
            "flash": "gemini-2.5-flash",
            "pro": "gemini-3-Flash",
            "gemma": "gemma-3-27b",
            "lite": "gemini-2.5-flash-lite",
            "embed": "models/gemini-embedding-2-preview"
        }

        # 3. Local Model Settings
        self.local_llm_name = "gemma3:1b"
        self.local_embed_name = "nomic-embed-text"
        
        # Cache for health status
        self._last_status = {"local": False, "gemini": False, "time": 0}

    def check_health(self, force=False):
        """Checks if providers are alive. Results are cached for 5 mins."""
        now = time.time()
        if not force and (now - self._last_status["time"] < 300):
            return self._last_status

        # Check Ollama
        try:
            res = requests.get("http://localhost:11434", timeout=1)
            self._last_status["local"] = (res.status_code == 200)
        except:
            self._last_status["local"] = False

        # Check Gemini API
        try:
            # We use 'lite' for the health check because it's the cheapest/fastest
            self.client.models.generate_content(model=self.MODEL_MAP["lite"], contents="ping")
            self._last_status["gemini"] = True
        except:
            self._last_status["gemini"] = False
            
        self._last_status["time"] = now
        return self._last_status

    def get_embeddings(self, model_type="gemini"):
        """Returns the correct LangChain embedding object."""
        if model_type == "local":
            return OllamaEmbeddings(model=self.local_embed_name)
        
        return GoogleGenerativeAIEmbeddings(
            model=self.MODEL_MAP["embed"], 
            google_api_key=self.api_key
        )

    def generate(self, prompt, model_choice="flash"):
        """
        Routes the prompt to the correct model.
        model_choice can be: 'flash', 'pro', 'gemma', 'lite', or 'local'
        """
        # --- Handle Local ---
        if model_choice == "local":
            return OllamaLLM(model=self.local_llm_name).invoke(prompt)
        
        # --- Handle Gemini API Models ---
        # Fallback to 'flash' if the user provides a model name not in our map
        target_model_string = self.MODEL_MAP.get(model_choice, self.MODEL_MAP["flash"])
        
        print(f"-> Routing to API Model: {target_model_string}")
        
        try:
            response = self.client.models.generate_content(
                model=target_model_string, 
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"❌ API Error using {target_model_string}: {str(e)}"

# Create the singleton instance
ai_manager = ModelProvider()
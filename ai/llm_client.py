
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# CONFIG & CONSTANTS
# =========================================================

MODEL = "google/gemma-3-4b-it"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_RETRIES = 3
RETRY_DELAY = 2

# Get API Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("Missing OPENROUTER_API_KEY environment variable")

def call_llm(prompt: str, temp: float = 0.7, max_tokens: int = 2000) -> str:
    """Calls OpenRouter LLM."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temp,
        "max_tokens": max_tokens
    }

    for attempt in range(MAX_RETRIES):
        try:
            r = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                data = r.json()
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"]
                return "❌ API Error: No choices returned"
            elif r.status_code == 429:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                time.sleep(RETRY_DELAY)
        except Exception:
            time.sleep(RETRY_DELAY)
    
    return "❌ API Error"

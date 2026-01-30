
# QuickNote AI Module

This directory contains the AI logic for the QuickNote RAG system.

## Structure

*   `quicknote_ai.py`: The main orchestrator. Import `process_content` from here.
*   `llm_client.py`: Handles communication with OpenRouter (DeepSeek/Gemma).
*   `vector_db.py`: Manages ChromaDB and SentenceTransformer embeddings.
*   `rag_engine.py`: Handles chunking and context retrieval logic.

## Usage

1.  Ensure `.env` file exists in the root directory with `OPENROUTER_API_KEY`.
2.  Install requirements: `pip install -r requirements.txt`.
3.  Import and use:

```python
from ai.quicknote_ai import process_content

# text = extracted text from PDF
result = process_content(text, "pdf")
print(result["summary"])
```

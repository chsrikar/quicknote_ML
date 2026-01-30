
import time
from typing import List, Dict, Optional, Any
from .vector_db import get_embedder, get_collection, load_models

def chunk_text(text: str, size: int = 900, overlap: int = 200) -> List[str]:
    """Splits text into chunks with overlap."""
    chunks = []
    start = 0
    step = size - overlap
    while start < len(text):
        chunk = text[start:start+size].strip()
        if len(chunk) > 50:
            chunks.append(chunk)
        start += step
    return chunks

def add_text(text: str):
    """Chunks text, generates embeddings, and stores in Vector DB."""
    embedder = get_embedder()
    collection = get_collection()
    
    chunks = chunk_text(text)
    if not chunks:
        return

    vectors = embedder.encode(chunks).tolist()
    ids = [f"chunk-{int(time.time())}-{i}" for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, embeddings=vectors)

def get_context(query: str, k: int = 8) -> str:
    """Retrieves relevant context from ChromaDB."""
    embedder = get_embedder()
    collection = get_collection()
    
    if collection.count() == 0:
        return "[NO DATA]"
    
    q_vec = embedder.encode(query).tolist()
    result = collection.query(query_embeddings=[q_vec], n_results=k)
    
    if not result["documents"]:
        return "[NO DATA]"
        
    return "\n\n---\n\n".join(result["documents"][0])

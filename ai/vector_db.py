
import chromadb
from sentence_transformers import SentenceTransformer

# Global State
embedder = None
client = None
collection = None

def load_models():
    """Initializes the embedding model and ChromaDB client."""
    global embedder, client, collection
    
    # Initialize SentenceTransformer
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Initialize ChromaDB (Local/In-Memory)
    client = chromadb.Client()
    
    # Reset/Create Collection
    try:
        client.delete_collection("pdf_rag")
    except Exception:
        pass
    collection = client.create_collection("pdf_rag")

def get_embedder():
    if not embedder:
        load_models()
    return embedder

def get_collection():
    if not collection:
        load_models()
    return collection

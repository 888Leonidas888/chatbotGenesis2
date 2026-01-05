"""
rag_core.py: Configuración compartida para el proyecto RAG.
"""
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
COLLECTION_NAME = "document_collection"

def get_embeddings() -> HuggingFaceEmbeddings:
    """Retorna el modelo de embeddings de HuggingFace."""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )

def get_vectorstore() -> Chroma:
    """Retorna la conexión al cliente de ChromaDB."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        host=CHROMA_HOST,
        port=CHROMA_PORT,
    )

def get_llm():
    """Retorna el modelo de lenguaje (Gemini)."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0
    )

"""
FastAPI REST API Server for Innefu Labs RAG Platform
===================================================
Beginner Concept:
-----------------
What is an API?
An API (Application Programming Interface) allows external apps, mobile clients,
or frontend websites to communicate with our Python RAG Engine using standard
HTTP JSON requests.

How to run:
    uvicorn api:app --reload --port 8000
    or:
    python api.py
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag.engine import rag_engine

app = FastAPI(
    title="Innefu Labs RAG API",
    description="REST API for Innefu Labs Grounded Knowledge Retrieval & Question Answering",
    version="1.0.0",
)

# -------------------------------------------------------------
# Production CORS Configuration
# Supports:
# 1. Localhost development (ports 3000, 5173, 8000)
# 2. Vercel deployments (*.vercel.app via regex)
# 3. Explicit custom domains via CORS_ORIGINS environment variable
# -------------------------------------------------------------
cors_origins_env = os.environ.get("CORS_ORIGINS", "*")
if cors_origins_env == "*" or not cors_origins_env.strip():
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request & Response Schemas
class ChatRequest(BaseModel):
    question: str = Field(..., description="The user question", json_schema_extra={"example": "Who are the co-founders of Innefu Labs?"})
    top_k: int = Field(default=3, ge=1, le=10, description="Number of chunks to retrieve")
    mode: str = Field(default="hybrid", description="Search mode: hybrid, vector, or bm25")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query string", json_schema_extra={"example": "Sarvagata AI air-gapped"})
    top_k: int = Field(default=3, ge=1, le=10, description="Number of results")
    mode: str = Field(default="hybrid", description="Search mode: hybrid, vector, or bm25")


class CitationItem(BaseModel):
    section: str
    url: str
    document: str
    product: str


class ChatResponse(BaseModel):
    question: str
    answer: str
    status: str
    confidence: float
    citations: List[CitationItem]
    mode: str
    chunks: Optional[List[Dict[str, Any]]] = None


@app.get("/")
def root():
    """System welcome and operational status."""
    return {
        "service": "Innefu Labs Enterprise RAG API",
        "status": "online",
        "indexed_chunks": rag_engine.vector_store.count(),
        "docs_url": "/docs",
    }


@app.get("/health")
def health():
    """Health probe check."""
    return {
        "status": "healthy",
        "indexed_chunks": rag_engine.vector_store.count(),
        "embedding_dimensions": rag_engine.embedder.dimensions,
    }


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """
    Submit a question to the RAG system and receive a grounded answer with citations.
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = rag_engine.query(
        question=req.question,
        top_k=req.top_k,
        mode=req.mode,
    )
    return result


@app.post("/search")
def search_endpoint(req: SearchRequest):
    """
    Search knowledge chunks directly without answer synthesis.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    chunks = rag_engine.search(
        query=req.query,
        top_k=req.top_k,
        mode=req.mode,
    )
    return {
        "query": req.query,
        "mode": req.mode,
        "results_count": len(chunks),
        "results": chunks,
    }


@app.get("/documents")
def list_documents():
    """
    List all knowledge sections currently indexed.
    """
    chunks = [p["payload"] for p in rag_engine.vector_store.points if "payload" in p]
    summary = []
    for c in chunks:
        summary.append({
            "chunk_id": c.get("chunk_id"),
            "section": c.get("section_heading"),
            "product": c.get("product_name"),
            "url": c.get("source_url"),
            "length_chars": len(c.get("text", "")),
        })
    return {
        "total_documents": len(summary),
        "documents": summary,
    }


if __name__ == "__main__":
    import os
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("api:app", host=host, port=port, reload=True)

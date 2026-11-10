"""
RAG Engine: The Central Coordinator
===================================
Beginner Concept:
-----------------
What does a RAG Engine do?
RAG stands for Retrieval-Augmented Generation.
Instead of relying solely on an AI's general training data (which might be outdated or hallucinate),
RAG follows a 3-step recipe:
1. Retrieval: Given a question, search a trusted Knowledge Base to find the most relevant chunks.
2. Augmentation: Combine the user's question with the retrieved chunks and source citations.
3. Generation: Produce a clear, accurate, fact-based answer strictly grounded in the retrieved facts.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from rag.embeddings import LocalEmbeddingEngine, embedding_engine
from rag.bm25 import BM25Index, bm25_index
from rag.vector_store import VectorStore, vector_store
from rag.hybrid_search import HybridSearchEngine, hybrid_engine
from rag.guardrails import SafetyGuardrails, guardrails

# Configure simple logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RAGEngine")


class DocumentChunker:
    """
    Splits Markdown documents into structured semantic sections based on headings (### or ##).
    Preserves document title, section headings, and product taxonomy.
    """

    @staticmethod
    def chunk_markdown(
        text: str,
        doc_id: str = "doc-kb",
        doc_title: str = "Innefu Knowledge Base",
        default_url: str = "https://innefu.com/products/",
    ) -> List[Dict[str, Any]]:
        chunks = []
        # Split by markdown headers (e.g. ### 1. Executive Overview)
        sections = re.split(r"\n(?=###?\s+)", text)
        page_num = 1

        for idx, section in enumerate(sections):
            section_clean = section.strip()
            # Filter out empty sections, short preambles, and disclaimers
            if not section_clean or len(section_clean) < 300 or "disclaimer" in section_clean.lower()[:80]:
                continue

            # Extract heading if available
            heading_match = re.match(r"^###?\s+(.+)$", section_clean, flags=re.MULTILINE)
            heading = heading_match.group(1).strip() if heading_match else "Overview"

            # Determine product name from heading if applicable
            product_name = "Innefu Overview"
            url = default_url
            for prod in [
                "Sarvagata AI", "Prophecy Guardian", "Prophecy Alethia",
                "Prophecy Eagle I", "Argus", "RapiDFIR", "AI Vision",
                "Innsight", "InteleLinx", "Prophecy GPT", "Speech to Text",
                "AuthShield", "Advisionary", "IR Management System"
            ]:
                if prod.lower() in heading.lower():
                    product_name = prod
                    if prod == "Sarvagata AI":
                        url = "https://innefu.com/products/sarvagata/"
                    elif prod == "Prophecy Guardian":
                        url = "https://innefu.com/products/prophecy-guardian/"
                    break

            chunk_id = f"{doc_id}_c{idx}"
            chunks.append({
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "document_title": doc_title,
                "source_url": url,
                "section_heading": heading,
                "page_number": page_num,
                "text": section_clean,
                "product_name": product_name,
            })
            page_num += 1

        return chunks


class RAGEngine:
    """
    Main RAG engine coordinating retrieval, hybrid search, guardrails, and answer synthesis.
    """

    def __init__(
        self,
        kb_path: str = "data/knowledge_base/Innefu_Labs_Deep_Dive_Knowledge_Base.md",
        vector_store_path: str = "data/vector_store/innefu_knowledge_base.json",
    ):
        self.kb_path = kb_path
        self.vector_store_path = vector_store_path

        self.embedder = embedding_engine
        self.vector_store = vector_store
        self.bm25 = bm25_index
        self.hybrid = hybrid_engine
        self.guardrails = guardrails

        # Ensure documents are loaded and indexed
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """
        Loads pre-computed vector store or builds it from Markdown knowledge base.
        """
        # If vector store is empty, load or build
        if self.vector_store.count() == 0:
            if Path(self.vector_store_path).exists():
                logger.info(f"Loading existing vector store from {self.vector_store_path}...")
                self.vector_store.load(self.vector_store_path)
            elif Path(self.kb_path).exists():
                logger.info(f"Indexing knowledge base from {self.kb_path}...")
                self._index_from_markdown(self.kb_path)

        # Build BM25 index from all vectors in the vector store
        chunks_for_bm25 = [p["payload"] for p in self.vector_store.points if "payload" in p]
        if chunks_for_bm25:
            logger.info(f"Building BM25 index over {len(chunks_for_bm25)} chunks...")
            self.bm25.build_index(chunks_for_bm25)

        logger.info(f"RAG Engine ready with {self.vector_store.count()} indexed chunks.")

    def _index_from_markdown(self, file_path: str):
        """
        Parses Markdown file, embeds chunks, and persists to vector store.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = DocumentChunker.chunk_markdown(content)
        texts = [c["text"] for c in chunks]
        vectors = self.embedder.embed_batch(texts)

        for chunk, vec in zip(chunks, vectors):
            self.vector_store.add_point(
                point_id=chunk["chunk_id"],
                vector=vec,
                payload=chunk,
            )

        self.vector_store.save(self.vector_store_path)

    def search(
        self,
        query: str,
        top_k: int = 3,
        mode: str = "hybrid",
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the top-k most relevant chunks for a query.

        Args:
            query: User's question or search term.
            top_k: Number of chunks to retrieve (default 3).
            mode: Search algorithm - 'hybrid', 'vector', or 'bm25'.

        Returns:
            List of chunk dictionaries with scores and source metadata.
        """
        if mode == "vector":
            query_vec = self.embedder.embed_text(query)
            raw = self.vector_store.search(query_vec, top_k=top_k)
            results = []
            for point, score in raw:
                chunk = dict(point.get("payload", point))
                chunk["vector_score"] = round(score, 4)
                results.append(chunk)
            return results

        elif mode == "bm25":
            raw = self.bm25.search(query, top_k=top_k)
            results = []
            for chunk, score in raw:
                c = dict(chunk.get("payload", chunk))
                c["bm25_score"] = round(score, 4)
                results.append(c)
            return results

        else:
            # Default: Hybrid Search with Reciprocal Rank Fusion
            return self.hybrid.search(query, top_k=top_k)

    def synthesize_answer(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Synthesize a factual, grounded answer strictly from the retrieved chunks.
        Extracts relevant facts directly without making up ungrounded statements.
        """
        if not chunks:
            return "No relevant public documentation was found in the knowledge base to answer this query."

        # Collect clean text from top chunks
        extracted_facts = []
        for c in chunks:
            text = c.get("text", "")
            # Remove markdown header line
            lines = [l.strip() for l in text.split("\n") if l.strip() and not l.strip().startswith("#")]
            for line in lines:
                # Filter out pure formatting dashes or disclaimers
                if line.startswith("---") or "prepared for enterprise rag" in line.lower():
                    continue
                # Clean bullet markers
                cleaned = re.sub(r"^[-*•]\s*", "", line)
                if cleaned and len(cleaned) > 20:
                    extracted_facts.append(cleaned)

        if not extracted_facts:
            return "The retrieved knowledge sections did not contain sufficient textual details."

        # Keep the top 3-4 distinct factual sentences
        unique_facts = []
        for fact in extracted_facts:
            # Avoid near-duplicates
            if not any(fact[:30].lower() in existing.lower() for existing in unique_facts):
                unique_facts.append(fact)
            if len(unique_facts) >= 4:
                break

        # Assemble grounded prose answer
        answer = " ".join(unique_facts)
        return answer

    def query(
        self,
        question: str,
        top_k: int = 3,
        mode: str = "hybrid",
    ) -> Dict[str, Any]:
        """
        Complete end-to-end RAG query:
        1. Checks Safety Guardrails.
        2. Retrieves top-k relevant chunks.
        3. Formulates grounded answer.
        4. Compiles structured citations.

        Returns:
            Dictionary with:
            - question: Original user question
            - answer: Grounded response or refusal
            - status: 'SUCCESS', 'REFUSED', or 'UNSUPPORTED'
            - citations: List of source citation dicts
            - chunks: Raw retrieved chunks
            - confidence: Quality/similarity score
        """
        # Step 1: Guardrails check (Prompt injection, malicious, confidential)
        is_safe, refusal = self.guardrails.check_query(question)
        if not is_safe:
            return {
                "question": question,
                "answer": refusal,
                "status": "REFUSED",
                "citations": [],
                "chunks": [],
                "confidence": 0.0,
                "mode": mode,
            }

        # Step 2: Retrieval
        chunks = self.search(question, top_k=top_k, mode=mode)

        # Check retrieval confidence
        best_score = 0.0
        if chunks:
            best_score = chunks[0].get("vector_score") or chunks[0].get("rrf_score") or 0.0

        # Step 3: Answer Generation
        answer = self.synthesize_answer(question, chunks)

        # Step 4: Extract Citations
        citations = []
        seen_citations = set()
        for c in chunks:
            heading = c.get("section_heading", "Knowledge Base")
            url = c.get("source_url", "https://innefu.com/")
            doc_title = c.get("document_title", "Innefu Knowledge Base")
            product = c.get("product_name", "Innefu Overview")

            cit_key = f"{heading}_{url}"
            if cit_key not in seen_citations:
                seen_citations.add(cit_key)
                citations.append({
                    "section": heading,
                    "url": url,
                    "document": doc_title,
                    "product": product,
                })

        return {
            "question": question,
            "answer": answer,
            "status": "SUCCESS",
            "citations": citations,
            "chunks": chunks,
            "confidence": round(best_score, 4),
            "mode": mode,
        }


# Global instance
rag_engine = RAGEngine()

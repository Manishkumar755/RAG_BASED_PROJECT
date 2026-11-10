"""
BM25 Lexical Keyword Retrieval Engine
=====================================
Beginner Concept:
-----------------
What is BM25?
BM25 (Best Matching 25) is an algorithm used by search engines to find documents
containing the exact keywords in your search query.
- It counts how many times your search words appear in each document (Term Frequency).
- It gives higher importance to rare, distinctive words and lower importance to common words (IDF).
- While vector embeddings understand meaning and synonyms, BM25 excels at exact names,
  IDs, product titles, and specific acronyms (e.g. 'Sarvagata', 'Alethia', 'CDR', 'IPDR').
"""

import re
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi


def tokenize(text: str) -> List[str]:
    """
    Clean and break text into lowercase words.
    Example: 'Who founded Innefu Labs?' -> ['who', 'founded', 'innefu', 'labs']
    """
    return re.findall(r"\w+", text.lower())


class BM25Index:
    """
    In-memory BM25 index over document chunks.
    """

    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: BM25Okapi = None

    def build_index(self, chunks: List[Dict[str, Any]]):
        """
        Build the BM25 index from a list of document chunk dictionaries.
        Each chunk is expected to have a 'text' field (or 'payload.text').
        """
        self.chunks = chunks
        self.tokenized_corpus = []

        for chunk in chunks:
            # Handle both payload format and flat dict format
            payload = chunk.get("payload", chunk)
            text = payload.get("text", "")
            title = payload.get("document_title", "")
            heading = payload.get("section_heading", "")
            product = payload.get("product_name", "")

            # Index text along with title and headings for maximum match accuracy
            combined_text = f"{title} {heading} {product} {text}"
            self.tokenized_corpus.append(tokenize(combined_text))

        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for chunks matching query keywords.

        Args:
            query: The user search question.
            top_k: Number of best-matching chunks to return.

        Returns:
            List of tuples: (chunk_dict, bm25_score)
        """
        if not self.bm25 or not self.chunks:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)

        # Pair each chunk with its score
        scored_results = [
            (self.chunks[i], float(scores[i]))
            for i in range(len(self.chunks))
        ]

        # Sort descending by score
        scored_results.sort(key=lambda x: x[1], reverse=True)

        # Return top_k results
        return scored_results[:top_k]


# Global singleton instance
bm25_index = BM25Index()

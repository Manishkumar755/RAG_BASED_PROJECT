"""
Vector Store & Cosine Similarity Engine
=======================================
Beginner Concept:
-----------------
What is a Vector Store?
A Vector Store is a database designed to store text vectors (embeddings) and
quickly search for the ones most similar in meaning to a query vector.

Cosine Similarity:
Since all our vectors are normalized to length 1.0 (unit vectors), the cosine
similarity between query vector Q and document vector D is simply their dot product:
    Similarity = Q · D = sum(Q[i] * D[i] for i in range(384))
A similarity score of 1.0 means identical meaning; 0.0 means unrelated.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np


class VectorStore:
    """
    Lightweight, high-performance in-memory vector database with JSON persistence.
    """

    def __init__(self, json_path: str = None):
        self.points: List[Dict[str, Any]] = []
        self.vectors_matrix: np.ndarray = np.empty((0, 384), dtype=np.float32)
        self.json_path = json_path

        if json_path and Path(json_path).exists():
            self.load(json_path)

    def load(self, file_path: str):
        """
        Load pre-indexed vectors from JSON file.
        """
        path = Path(file_path)
        if not path.exists():
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        points = data.get("points", [])
        self.points = points

        if points:
            vectors = [p["vector"] for p in points]
            self.vectors_matrix = np.array(vectors, dtype=np.float32)
            # Ensure unit length
            norms = np.linalg.norm(self.vectors_matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self.vectors_matrix = self.vectors_matrix / norms

    def save(self, file_path: str = None):
        """
        Save indexed vectors to JSON file.
        """
        target = file_path or self.json_path
        if not target:
            return

        Path(target).parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump({"points": self.points}, f, indent=2)

    def add_point(self, point_id: str, vector: List[float], payload: Dict[str, Any]):
        """
        Add a single point (chunk + vector) to the store.
        """
        vec_np = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(vec_np)
        if norm > 0:
            vec_np = vec_np / norm

        point = {
            "id": point_id,
            "vector": vec_np.tolist(),
            "payload": payload,
        }
        self.points.append(point)

        # Update the search matrix
        if self.vectors_matrix.size == 0:
            self.vectors_matrix = np.array([vec_np], dtype=np.float32)
        else:
            self.vectors_matrix = np.vstack([self.vectors_matrix, vec_np])

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find the top_k most similar chunks using cosine similarity.

        Args:
            query_vector: 384-dimensional vector for user query.
            top_k: Number of best-matching chunks to return.

        Returns:
            List of (point_dict, similarity_score) sorted descending by similarity.
        """
        if self.vectors_matrix.size == 0:
            return []

        q = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm > 0:
            q = q / q_norm

        # Cosine similarity is the dot product of normalized vectors
        scores = np.dot(self.vectors_matrix, q)

        # Get indices of top_k highest scores
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            results.append((self.points[idx], score))

        return results

    def count(self) -> int:
        return len(self.points)


# Global singleton instance
vector_store = VectorStore(json_path="data/vector_store/innefu_knowledge_base.json")

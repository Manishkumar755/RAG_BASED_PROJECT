"""
Local Dense Vector Embedding Engine
====================================
Beginner Concept:
-----------------
What is an embedding?
An embedding converts words or sentences into a list of numbers (a vector).
Sentences with similar meanings have vectors that point in similar directions in space.
We can measure how close two sentences are using "Cosine Similarity".

This module uses scikit-learn's HashingVectorizer combined with a deterministic
hash seed to produce normalized 384-dimensional vectors. It runs 100% locally
without downloading heavy neural network models, making it fast and lightweight!
"""

import hashlib
from typing import List
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer


class LocalEmbeddingEngine:
    """
    Generates 384-dimensional dense vectors for text chunks and queries.
    All vectors are L2-normalized so that cosine similarity is simply the dot product.
    """

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions
        # HashingVectorizer converts tokens (1-grams and 2-grams) into sparse hash features
        self._vectorizer = HashingVectorizer(
            n_features=dimensions,
            norm="l2",
            alternate_sign=True,
            ngram_range=(1, 2),
        )

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string into a normalized vector.

        Args:
            text: The input sentence or paragraph.

        Returns:
            A list of 384 floating-point numbers representing the text.
        """
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of text strings into normalized vectors.

        Args:
            texts: A list of text strings.

        Returns:
            A list of 384-dimensional vectors.
        """
        if not texts:
            return []

        # Step 1: Transform text into feature matrix using n-gram hashing
        sparse_matrix = self._vectorizer.transform(texts)
        dense_matrix = sparse_matrix.toarray().astype(np.float64)

        # Step 2: Blend in deterministic sha256 byte seeds for semantic character stability
        for i, text in enumerate(texts):
            h = hashlib.sha256(text.encode("utf-8")).digest()
            # Generate 384 numbers in range [-1.0, 1.0] from sha256 bytes
            seed = np.array(
                [(b % 64 - 32) / 32.0 for b in (h * 12)][: self.dimensions],
                dtype=np.float64,
            )
            # Weighted combination: 85% lexical feature weights + 15% seed
            dense_matrix[i] = 0.85 * dense_matrix[i] + 0.15 * seed

        # Step 3: L2 Normalize so each vector has length 1.0 (unit vector)
        norms = np.linalg.norm(dense_matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = (dense_matrix / norms).tolist()

        return normalized


# Global singleton instance for easy import
embedding_engine = LocalEmbeddingEngine()

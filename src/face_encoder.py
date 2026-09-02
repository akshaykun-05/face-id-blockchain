"""Embedding normalization and cryptographic commitment helpers."""

import hashlib
from typing import Any

import numpy as np


class FaceEncoder:
    """Convert InsightFace embeddings into normalized, hashable arrays."""

    @staticmethod
    def normalize_embedding(embedding: Any) -> np.ndarray:
        values = np.asarray(embedding, dtype=np.float32).reshape(-1)
        norm = np.linalg.norm(values)
        if values.size == 0 or not np.isfinite(norm) or norm == 0:
            raise ValueError("Embedding must be non-empty and have a non-zero finite norm")
        return values / norm

    @classmethod
    def encode(cls, face: Any) -> np.ndarray:
        embedding = getattr(face, "embedding", None)
        if embedding is None:
            raise ValueError("InsightFace did not provide an embedding")
        return cls.normalize_embedding(embedding)

    @staticmethod
    def commitment(normalized_embedding: np.ndarray) -> str:
        normalized = np.asarray(normalized_embedding, dtype=np.float32).reshape(-1)
        return hashlib.sha256(normalized.tobytes()).hexdigest()

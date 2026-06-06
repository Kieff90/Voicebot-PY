"""Indice dei servizi in memoria: ricerca per similarita del coseno con NumPy.

Su ~100 chunk di un Comune la scansione lineare e esatta e istantanea: niente FAISS
(resta un upgrade se il corpus cresce). I vettori vengono normalizzati (L2), quindi
il coseno coincide con il prodotto scalare.
"""

import numpy as np

from backend.app.services.rag.corpus import Chunk


def _normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=-1, keepdims=True)
    norms = np.where(norms == 0.0, 1.0, norms)
    return matrix / norms


class ServicesIndex:
    """Matrice di vettori normalizzati + i Chunk corrispondenti."""

    def __init__(self, matrix: np.ndarray, chunks: list[Chunk]):
        self._matrix = _normalize(np.asarray(matrix, dtype=np.float32))
        self._chunks = list(chunks)

    def search(self, query_vector: np.ndarray, top_k: int) -> list[tuple[float, Chunk]]:
        query = _normalize(np.asarray(query_vector, dtype=np.float32).reshape(1, -1))[0]
        scores = self._matrix @ query
        order = np.argsort(scores)[::-1][:top_k]
        return [(float(scores[i]), self._chunks[i]) for i in order]


def build_index(chunks: list[Chunk], embedder) -> ServicesIndex:
    """Costruisce l'indice vettorizzando i passaggi tramite l'embedder."""
    matrix = embedder.embed_passages([c.text for c in chunks])
    return ServicesIndex(matrix, chunks)

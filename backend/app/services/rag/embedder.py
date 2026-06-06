"""Embedder multilingue basato su sentence-transformers (modello E5).

Disciplina E5: prefisso ``query:`` per le domande, ``passage:`` per i testi indicizzati,
ed embedding normalizzati (L2) prima del coseno. Saltarlo degrada il recupero.
Il modello (~400MB) viene caricato una sola volta alla costruzione.
"""

from typing import Protocol

import numpy as np


class Embedder(Protocol):
    """Contratto minimo di un embedder: domande e passaggi → vettori."""

    def embed_query(self, text: str) -> np.ndarray: ...

    def embed_passages(self, texts: list[str]) -> np.ndarray: ...


class E5Embedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)

    def _encode(self, inputs: list[str]) -> np.ndarray:
        vectors = self._model.encode(inputs, normalize_embeddings=True)
        return np.asarray(vectors, dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        return self._encode([f"query: {text}"])[0]

    def embed_passages(self, texts: list[str]) -> np.ndarray:
        return self._encode([f"passage: {t}" for t in texts])

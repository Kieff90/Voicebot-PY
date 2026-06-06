"""Embedder finto e deterministico per i test (zero download del modello).

Mappa il testo su un vettore bag-of-words su un vocabolario fisso: parole condivise
tra domanda e passaggio → coseno alto; nessuna parola in comune → coseno 0.
Sufficiente a verificare la logica di indice/retriever senza caricare E5.
"""

import re

import numpy as np

_VOCAB = [
    "anagrafe",
    "residenza",
    "certificato",
    "carta",
    "identita",
    "tributi",
    "tari",
    "rifiuti",
    "imu",
    "stato",
    "civile",
    "matrimonio",
    "tecnico",
    "edilizia",
    "sociale",
    "appuntamento",
]


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zàèéìòù]+", text.lower())


class FakeEmbedder:
    def _vec(self, text: str) -> np.ndarray:
        vec = np.zeros(len(_VOCAB), dtype=np.float32)
        for tok in _tokenize(text):
            for i, word in enumerate(_VOCAB):
                if tok == word or word in tok:
                    vec[i] += 1.0
        return vec

    def embed_query(self, text: str) -> np.ndarray:
        return self._vec(text)

    def embed_passages(self, texts: list[str]) -> np.ndarray:
        return np.vstack([self._vec(t) for t in texts])

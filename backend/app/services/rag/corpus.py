"""Caricamento del corpus dei servizi (artefatto offline → chunk in memoria)."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Chunk:
    """Un blocco di testo indicizzabile con la sua fonte."""

    text: str
    fonte: str


def load_chunks(path: str) -> list[Chunk]:
    """Legge un file JSONL (una riga per chunk) e restituisce i Chunk.

    Ogni riga non vuota deve avere i campi ``testo`` e ``fonte``.
    """
    chunks: list[Chunk] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        chunks.append(Chunk(text=obj["testo"], fonte=obj["fonte"]))
    return chunks

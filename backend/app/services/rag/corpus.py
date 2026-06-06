"""Caricamento del corpus dei servizi (artefatto offline → chunk in memoria).

Ogni chunk e una sezione di una scheda servizio con i suoi metadati:
- ``servizio`` e ``sezione`` disambiguano pezzi altrimenti generici;
- ``fonte`` permette di citare la provenienza (anti-allucinazione);
- ``aggiornato`` traccia la freschezza dell'informazione.
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Chunk:
    text: str
    servizio: str
    sezione: str
    fonte: str
    aggiornato: str = ""

    def embed_text(self) -> str:
        """Testo da vettorizzare: ancora il pezzo al servizio e alla sezione.

        Una sezione generica ("verifica i costi sul portale") da sola e ambigua;
        anteporre ``servizio — sezione`` la lega al concetto giusto.
        """
        return f"{self.servizio} — {self.sezione}: {self.text}"


def load_chunks(path: str) -> list[Chunk]:
    """Legge un file JSONL (una riga per chunk) e restituisce i Chunk.

    Campi richiesti per riga: ``testo``, ``servizio``, ``sezione``, ``fonte``.
    ``aggiornato`` e opzionale.
    """
    chunks: list[Chunk] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        chunks.append(
            Chunk(
                text=obj["testo"],
                servizio=obj["servizio"],
                sezione=obj["sezione"],
                fonte=obj["fonte"],
                aggiornato=obj.get("aggiornato", ""),
            )
        )
    return chunks

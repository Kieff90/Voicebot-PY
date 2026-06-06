"""Retriever: recupera i chunk piu rilevanti per una domanda (nessuna generazione).

Restituisce chunk compatti; la formulazione della risposta resta a Vapi. Il gate di
soglia evita di restituire contenuto poco pertinente: sotto soglia, "non disponibile".
"""

from typing import Any

from pydantic import ValidationError

from backend.app.models.rag import QueryRequest
from backend.app.services.rag.embedder import Embedder
from backend.app.services.rag.index import ServicesIndex


def query_servizi(
    index: ServicesIndex,
    embedder: Embedder,
    arguments: dict[str, Any],
    *,
    top_k: int,
    threshold: float,
    char_cap: int,
) -> dict[str, Any]:
    try:
        req = QueryRequest(**arguments)
    except ValidationError:
        return {"esito": "errore", "motivo": "domanda mancante o non valida"}

    hits = index.search(embedder.embed_query(req.domanda), top_k)
    if not hits or hits[0][0] < threshold:
        return {"esito": "non_disponibile"}

    risultati: list[dict[str, str]] = []
    used = 0
    for score, chunk in hits:
        if score < threshold:
            break
        testo = chunk.text[: char_cap - used]
        if not testo:
            break
        risultati.append(
            {
                "servizio": chunk.servizio,
                "sezione": chunk.sezione,
                "testo": testo,
                "fonte": chunk.fonte,
            }
        )
        used += len(testo)
    return {"esito": "ok", "risultati": risultati}

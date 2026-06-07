"""Pulizia del corpus (corpus building, offline).

Scarta i chunk-stub senza informazione: rinvii generici all'Ufficio competente
del tipo "Contattare l'Ufficio competente". Sono quasi privi di contenuto e
degradano il recupero (creano falsi positivi su domande "quanto costa ...").
Vedi BLUEPRINT §10: il corpus building rimuove boilerplate e unità vuote/brevi.
"""

import re

_UFFICIO = re.compile(r"ufficio (competente|di competenza)", re.I)
_RINVIO = re.compile(r"\b(contatt|informar|verific|rivolg|consigliabile)\w*", re.I)
_LEN_MAX = 160


def e_boilerplate(testo: str) -> bool:
    """True se il testo è un rinvio generico all'ufficio, senza info concrete.

    Criterio: cita l'"Ufficio competente/di competenza", è solo un invito a
    contattarlo/informarsi/verificare, ed è breve (< 160 caratteri). Testi vuoti
    contano come boilerplate. I testi con dati concreti (importi, tempi) restano.
    """
    t = testo.strip()
    if not t:
        return True
    return bool(_UFFICIO.search(t)) and bool(_RINVIO.search(t)) and len(t) < _LEN_MAX


def filtra_chunk(chunks: list[dict]) -> list[dict]:
    """Rimuove i chunk il cui ``testo`` è boilerplate, preserva l'ordine."""
    return [c for c in chunks if not e_boilerplate(c["testo"])]

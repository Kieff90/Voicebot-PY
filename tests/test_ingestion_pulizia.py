"""Test del filtro boilerplate del corpus building (offline).

Scarta i chunk-stub senza informazione (rinvii generici all'Ufficio competente)
che degradano il recupero: creano falsi positivi e non aggiungono contenuto.
"""

import pytest

from ingestion.pulizia import e_boilerplate, filtra_chunk


@pytest.mark.parametrize(
    "testo",
    [
        "Contattare l'Ufficio competente",
        "Rivolgersi all'Ufficio competente",
        "È importante informarsi presso l'Ufficio competente in merito ai costi.",
        "Verifica presso l'Ufficio competente le spese amministrative applicabili.",
        "È consigliabile contattare l'Ufficio competente per conoscere i tempi.",
        "   ",
        "",
    ],
)
def test_stub_senza_contenuto_sono_boilerplate(testo):
    assert e_boilerplate(testo) is True


@pytest.mark.parametrize(
    "testo",
    [
        "La comunicazione del cambio residenza è gratuita.",
        "N. 1 marca da bollo €16,00 nel caso gli sposi siano residenti.",
        "L'esame e l'invio dei documenti in forma elettronica costano € 10,00.",
        "5 giorni dalla richiesta",
        "Puoi verificare i costi di ogni pratica sul portale dedicato e procedere.",
    ],
)
def test_contenuto_concreto_non_e_boilerplate(testo):
    assert e_boilerplate(testo) is False


def test_filtra_chunk_rimuove_solo_gli_stub():
    chunks = [
        {"testo": "Contattare l'Ufficio competente", "sezione": "Quanto costa"},
        {"testo": "La comunicazione è gratuita.", "sezione": "Quanto costa"},
    ]
    tenuti = filtra_chunk(chunks)
    assert len(tenuti) == 1
    assert tenuti[0]["testo"] == "La comunicazione è gratuita."

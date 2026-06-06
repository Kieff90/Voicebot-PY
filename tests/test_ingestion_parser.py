"""
Test del parser HTML dello scraper. Non tocca la rete: usa HTML in-memory.
"""

from ingestion.scraper_cherasco import _estrai_sezioni

# HTML minimale che simula la struttura AGID di una pagina servizio comunale
_HTML_FIXTURE = """
<html>
<body>
<h1>Certificati Anagrafici</h1>
<h2>A chi è rivolto</h2>
<p>Cittadini residenti nel Comune.</p>
<h2>Descrizione</h2>
<p>L'ufficio anagrafe rilascia certificati di residenza e stato di famiglia.</p>
<h2>Come fare</h2>
<p>Presentarsi allo sportello oppure richiedere online tramite ANPR.</p>
<h2>Cosa serve</h2>
<p>Documento di identità valido.</p>
<h2>Cosa si ottiene</h2>
<p>Il certificato richiesto, valido 6 mesi.</p>
<h2>Tempi e scadenze</h2>
<p>Rilascio immediato allo sportello.</p>
<h2>Quanto costa</h2>
<p>Certificati in carta semplice gratuiti; in bollo 16 euro.</p>
<h2>Contatti</h2>
<p>Ufficio Anagrafe. Tel 0172.427001.</p>
</body>
</html>
"""

_HTML_SEZIONI_PARZIALI = """
<html>
<body>
<h2>Descrizione</h2>
<p>Servizio di gestione rifiuti urbani.</p>
<h2>Quanto costa</h2>
<p>Calcolato in base alla superficie.</p>
</body>
</html>
"""


def test_estrai_tutte_le_sezioni_agid():
    chunks = _estrai_sezioni(_HTML_FIXTURE, "Anagrafe", "https://example.com/anagrafe")
    assert len(chunks) == 8
    sezioni = [c["sezione"] for c in chunks]
    assert "Descrizione" in sezioni
    assert "Contatti" in sezioni


def test_chunk_contiene_campi_richiesti():
    chunks = _estrai_sezioni(_HTML_FIXTURE, "Anagrafe", "https://example.com/anagrafe")
    primo = chunks[0]
    assert primo["servizio"] == "Anagrafe"
    assert primo["fonte"] == "Comune di Cherasco — https://example.com/anagrafe"
    assert primo["testo"]
    assert primo["sezione"]
    assert "aggiornato" in primo


def test_sezioni_mancanti_vengono_saltate():
    chunks = _estrai_sezioni(_HTML_SEZIONI_PARZIALI, "TARI", "https://example.com/tari")
    assert len(chunks) == 2
    sezioni = [c["sezione"] for c in chunks]
    assert "Descrizione" in sezioni
    assert "Quanto costa" in sezioni


def test_testo_breve_viene_saltato():
    html = "<html><body><h2>Descrizione</h2><p>Breve.</p></body></html>"
    chunks = _estrai_sezioni(html, "Test", "https://example.com")
    assert len(chunks) == 0


def test_normalizza_whitespace():
    html = "<html><body><h2>Descrizione</h2><p>Testo   con\n   spazi.</p></body></html>"
    chunks = _estrai_sezioni(html, "Test", "https://example.com")
    if chunks:
        assert "  " not in chunks[0]["testo"]

from backend.app.services.rag.corpus import Chunk
from backend.app.services.rag.index import build_index
from backend.app.services.rag.retriever import query_servizi
from tests.fakes import FakeEmbedder

_CHUNKS = [
    Chunk(text="residenza certificato", servizio="Anagrafe", sezione="Descrizione", fonte="anagrafe"),
    Chunk(text="tari rifiuti", servizio="Tributi", sezione="Descrizione", fonte="tributi"),
    Chunk(text="carta identita", servizio="Carta identita", sezione="Descrizione", fonte="cie"),
]


def _index():
    return build_index(_CHUNKS, FakeEmbedder())


def test_in_domain_query_returns_relevant_chunk():
    result = query_servizi(
        _index(), FakeEmbedder(), {"domanda": "tari rifiuti"},
        top_k=3, threshold=0.3, char_cap=2000,
    )
    assert result["esito"] == "ok"
    assert result["risultati"][0]["fonte"] == "tributi"
    assert result["risultati"][0]["servizio"] == "Tributi"
    assert result["risultati"][0]["sezione"] == "Descrizione"


def test_out_of_domain_query_below_threshold_is_not_available():
    result = query_servizi(
        _index(), FakeEmbedder(), {"domanda": "che tempo fa oggi"},
        top_k=3, threshold=0.3, char_cap=2000,
    )
    assert result == {"esito": "non_disponibile"}


def test_malformed_arguments_return_errore():
    result = query_servizi(
        _index(), FakeEmbedder(), {},
        top_k=3, threshold=0.3, char_cap=2000,
    )
    assert result["esito"] == "errore"
    assert "motivo" in result


def test_only_hits_above_threshold_are_included():
    result = query_servizi(
        _index(), FakeEmbedder(), {"domanda": "tari rifiuti"},
        top_k=3, threshold=0.6, char_cap=2000,
    )
    assert result["esito"] == "ok"
    assert [r["fonte"] for r in result["risultati"]] == ["tributi"]


def test_char_cap_limits_total_payload():
    result = query_servizi(
        _index(), FakeEmbedder(), {"domanda": "anagrafe tributi carta"},
        top_k=3, threshold=0.0, char_cap=20,
    )
    total = sum(len(r["testo"]) for r in result["risultati"])
    assert total <= 20

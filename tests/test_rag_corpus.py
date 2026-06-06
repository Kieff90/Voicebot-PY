from pathlib import Path

from backend.app.services.rag.corpus import Chunk, load_chunks


def _write(tmp_path: Path, lines: list[str]) -> str:
    p = tmp_path / "corpus.jsonl"
    p.write_text("\n".join(lines), encoding="utf-8")
    return str(p)


def test_load_chunks_parses_each_line(tmp_path):
    path = _write(
        tmp_path,
        [
            '{"testo": "residenza e certificati", "servizio": "Anagrafe", "sezione": "Descrizione", "fonte": "url1", "aggiornato": "2025-09-30"}',
            '{"testo": "TARI e IMU", "servizio": "Tributi", "sezione": "Descrizione", "fonte": "url2"}',
        ],
    )
    chunks = load_chunks(path)
    assert chunks[0] == Chunk(
        text="residenza e certificati",
        servizio="Anagrafe",
        sezione="Descrizione",
        fonte="url1",
        aggiornato="2025-09-30",
    )
    assert chunks[1] == Chunk(
        text="TARI e IMU", servizio="Tributi", sezione="Descrizione", fonte="url2"
    )
    assert chunks[1].aggiornato == ""  # opzionale


def test_load_chunks_skips_blank_lines(tmp_path):
    path = _write(
        tmp_path,
        [
            '{"testo": "uno", "servizio": "A", "sezione": "S", "fonte": "a"}',
            "",
            "   ",
            '{"testo": "due", "servizio": "B", "sezione": "S", "fonte": "b"}',
        ],
    )
    assert len(load_chunks(path)) == 2


def test_embed_text_includes_service_and_section():
    chunk = Chunk(text="verifica i costi sul portale", servizio="SUAP", sezione="Quanto costa", fonte="x")
    assert chunk.embed_text() == "SUAP — Quanto costa: verifica i costi sul portale"


def test_chunk_is_immutable():
    chunk = Chunk(text="x", servizio="s", sezione="z", fonte="y")
    try:
        chunk.text = "z"  # type: ignore[misc]
    except Exception as exc:  # frozen dataclass raises FrozenInstanceError
        assert "cannot assign" in str(exc) or "frozen" in str(exc).lower()
    else:
        raise AssertionError("Chunk dovrebbe essere immutabile")


def test_real_fallback_corpus_loads():
    chunks = load_chunks("data/fallback_services.jsonl")
    assert len(chunks) >= 6
    assert all(c.text and c.servizio and c.sezione and c.fonte for c in chunks)

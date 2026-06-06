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
            '{"testo": "Anagrafe: residenza e certificati.", "fonte": "Comune - Anagrafe"}',
            '{"testo": "Tributi: TARI e IMU.", "fonte": "Comune - Tributi"}',
        ],
    )
    chunks = load_chunks(path)
    assert chunks == [
        Chunk(text="Anagrafe: residenza e certificati.", fonte="Comune - Anagrafe"),
        Chunk(text="Tributi: TARI e IMU.", fonte="Comune - Tributi"),
    ]


def test_load_chunks_skips_blank_lines(tmp_path):
    path = _write(
        tmp_path,
        [
            '{"testo": "uno", "fonte": "a"}',
            "",
            "   ",
            '{"testo": "due", "fonte": "b"}',
        ],
    )
    chunks = load_chunks(path)
    assert len(chunks) == 2


def test_chunk_is_immutable():
    chunk = Chunk(text="x", fonte="y")
    try:
        chunk.text = "z"  # type: ignore[misc]
    except Exception as exc:  # frozen dataclass raises FrozenInstanceError
        assert "cannot assign" in str(exc) or "frozen" in str(exc).lower()
    else:
        raise AssertionError("Chunk dovrebbe essere immutabile")


def test_real_fallback_corpus_loads():
    chunks = load_chunks("data/fallback_services.jsonl")
    assert len(chunks) >= 6
    assert all(c.text and c.fonte for c in chunks)

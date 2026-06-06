import numpy as np

from backend.app.services.rag.corpus import Chunk
from backend.app.services.rag.index import ServicesIndex, build_index
from tests.fakes import FakeEmbedder


def _chunk(text, fonte):
    return Chunk(text=text, servizio="S", sezione="Descrizione", fonte=fonte)


def test_search_ranks_by_cosine_similarity():
    chunks = [_chunk("x", "a"), _chunk("y", "b"), _chunk("xy", "c")]
    matrix = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], dtype=np.float32)
    index = ServicesIndex(matrix, chunks)

    hits = index.search(np.array([1.0, 0.0], dtype=np.float32), top_k=3)

    assert [c.fonte for _, c in hits] == ["a", "c", "b"]
    assert hits[0][0] == 1.0


def test_search_respects_top_k():
    chunks = [_chunk(str(i), str(i)) for i in range(5)]
    matrix = np.eye(5, dtype=np.float32)
    index = ServicesIndex(matrix, chunks)

    assert len(index.search(np.array([1, 0, 0, 0, 0], dtype=np.float32), top_k=2)) == 2


def test_search_normalizes_so_magnitude_does_not_matter():
    chunks = [_chunk("a", "a"), _chunk("b", "b")]
    matrix = np.array([[10.0, 0.0], [0.0, 3.0]], dtype=np.float32)
    index = ServicesIndex(matrix, chunks)

    hits = index.search(np.array([5.0, 0.0], dtype=np.float32), top_k=1)

    assert hits[0][1].fonte == "a"
    assert hits[0][0] == 1.0


def test_build_index_embeds_passages_via_embedder():
    chunks = [
        Chunk(text="residenza certificato", servizio="Anagrafe", sezione="Descrizione", fonte="anagrafe"),
        Chunk(text="tari rifiuti", servizio="Tributi", sezione="Descrizione", fonte="tributi"),
    ]
    index = build_index(chunks, FakeEmbedder())

    hits = index.search(FakeEmbedder().embed_query("tari rifiuti"), top_k=1)

    assert hits[0][1].fonte == "tributi"

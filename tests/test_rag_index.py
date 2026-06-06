import numpy as np

from backend.app.services.rag.corpus import Chunk
from backend.app.services.rag.index import ServicesIndex, build_index
from tests.fakes import FakeEmbedder


def test_search_ranks_by_cosine_similarity():
    # tre vettori 2D; la query punta lungo l'asse x
    chunks = [Chunk(text="x", fonte="a"), Chunk(text="y", fonte="b"), Chunk(text="xy", fonte="c")]
    matrix = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], dtype=np.float32)
    index = ServicesIndex(matrix, chunks)

    hits = index.search(np.array([1.0, 0.0], dtype=np.float32), top_k=3)

    assert [c.fonte for _, c in hits] == ["a", "c", "b"]
    assert hits[0][0] == 1.0  # coseno esatto con il vettore identico


def test_search_respects_top_k():
    chunks = [Chunk(text=str(i), fonte=str(i)) for i in range(5)]
    matrix = np.eye(5, dtype=np.float32)
    index = ServicesIndex(matrix, chunks)

    hits = index.search(np.array([1, 0, 0, 0, 0], dtype=np.float32), top_k=2)

    assert len(hits) == 2


def test_search_normalizes_so_magnitude_does_not_matter():
    chunks = [Chunk(text="a", fonte="a"), Chunk(text="b", fonte="b")]
    matrix = np.array([[10.0, 0.0], [0.0, 3.0]], dtype=np.float32)
    index = ServicesIndex(matrix, chunks)

    hits = index.search(np.array([5.0, 0.0], dtype=np.float32), top_k=1)

    assert hits[0][1].fonte == "a"
    assert hits[0][0] == 1.0  # nonostante le magnitudini diverse


def test_build_index_embeds_passages_via_embedder():
    chunks = [
        Chunk(text="anagrafe residenza certificato", fonte="anagrafe"),
        Chunk(text="tributi tari rifiuti", fonte="tributi"),
    ]
    index = build_index(chunks, FakeEmbedder())

    hits = index.search(FakeEmbedder().embed_query("tari rifiuti"), top_k=1)

    assert hits[0][1].fonte == "tributi"

from functools import lru_cache
from pathlib import Path

from backend.app.config import settings
from backend.app.db.session import connect, init_db
from backend.app.services.appointments.repository import AppointmentRepository
from backend.app.services.rag.corpus import load_chunks
from backend.app.services.rag.embedder import E5Embedder, Embedder
from backend.app.services.rag.index import ServicesIndex, build_index


@lru_cache
def _connection():
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = connect(settings.db_path)
    init_db(conn)
    return conn


def get_repo() -> AppointmentRepository:
    return AppointmentRepository(_connection())


@lru_cache
def _rag() -> tuple[ServicesIndex, Embedder]:
    # Caricato una sola volta (modello ~400MB + indice in memoria).
    embedder = E5Embedder(settings.rag_model_name)
    index = build_index(load_chunks(settings.rag_corpus_path), embedder)
    return index, embedder


def get_rag() -> tuple[ServicesIndex, Embedder]:
    return _rag()

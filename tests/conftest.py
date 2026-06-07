import sqlite3

import pytest
from fastapi.testclient import TestClient

from backend.app.db.session import init_db
from backend.app.deps import get_rag, get_repo
from backend.app.main import app
from backend.app.services.appointments.repository import AppointmentRepository
from backend.app.services.rag.corpus import Chunk
from backend.app.services.rag.index import build_index
from tests.fakes import FakeEmbedder

_FAKE_CHUNKS = [
    Chunk(text="residenza certificato", servizio="Anagrafe", sezione="Descrizione", fonte="anagrafe"),
    Chunk(text="carta identita", servizio="Carta identita", sezione="Descrizione", fonte="cie"),
    Chunk(text="tari rifiuti", servizio="Tributi", sezione="Descrizione", fonte="tributi"),
]


@pytest.fixture
def client():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    repo = AppointmentRepository(conn)
    fake_embedder = FakeEmbedder()
    fake_index = build_index(_FAKE_CHUNKS, fake_embedder)
    app.dependency_overrides[get_repo] = lambda: repo
    app.dependency_overrides[get_rag] = lambda: (fake_index, fake_embedder)
    yield TestClient(app)
    app.dependency_overrides.clear()

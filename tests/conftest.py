import sqlite3

import pytest
from fastapi.testclient import TestClient

from backend.app.db.session import init_db
from backend.app.deps import get_repo
from backend.app.main import app
from backend.app.services.appointments.repository import AppointmentRepository


@pytest.fixture
def client():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    init_db(conn)
    repo = AppointmentRepository(conn)
    app.dependency_overrides[get_repo] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()

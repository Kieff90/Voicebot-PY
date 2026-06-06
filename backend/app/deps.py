from functools import lru_cache
from pathlib import Path

from backend.app.config import settings
from backend.app.db.session import connect, init_db
from backend.app.services.appointments.repository import AppointmentRepository


@lru_cache
def _connection():
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = connect(settings.db_path)
    init_db(conn)
    return conn


def get_repo() -> AppointmentRepository:
    return AppointmentRepository(_connection())

import sqlite3

import pytest

from backend.app.db.session import init_db
from backend.app.services.appointments.repository import AppointmentRepository


@pytest.fixture
def repo():
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    return AppointmentRepository(conn)


def test_booked_slots_empty_at_start(repo):
    assert repo.booked_slots("anagrafe", "2026-12-01") == set()


def test_create_then_booked_slots_contains_it(repo):
    repo.create(codice="AAA1", servizio="anagrafe", data="2026-12-01", ora="09:00", nome="Mario")
    assert repo.booked_slots("anagrafe", "2026-12-01") == {"09:00"}


def test_create_same_slot_twice_raises_integrity_error(repo):
    repo.create(codice="AAA1", servizio="anagrafe", data="2026-12-01", ora="09:00", nome="Mario")
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(codice="BBB2", servizio="anagrafe", data="2026-12-01", ora="09:00", nome="Luigi")


def test_different_service_same_slot_is_allowed(repo):
    repo.create(codice="AAA1", servizio="anagrafe", data="2026-12-01", ora="09:00", nome="Mario")
    repo.create(codice="BBB2", servizio="tributi", data="2026-12-01", ora="09:00", nome="Luigi")
    assert repo.booked_slots("tributi", "2026-12-01") == {"09:00"}

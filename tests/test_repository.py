import sqlite3

import pytest

from backend.app.db.session import init_db
from backend.app.services.appointments.repository import AppointmentRepository


@pytest.fixture
def repo():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
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


def test_list_all_empty_at_start(repo):
    assert repo.list_all() == []


def test_list_all_returns_rows_ordered_by_data_and_ora(repo):
    repo.create(codice="AAA1", servizio="Altro", data="2026-12-02", ora="09:00", nome="Mario")
    repo.create(codice="BBB2", servizio="Altro", data="2026-12-01", ora="10:00", nome="Luigi")
    repo.create(codice="CCC3", servizio="Altro", data="2026-12-01", ora="09:00", nome="Anna")

    rows = repo.list_all()
    assert [row["nome"] for row in rows] == ["Anna", "Luigi", "Mario"]


def test_list_all_filters_by_date_range(repo):
    repo.create(codice="AAA1", servizio="Altro", data="2026-12-01", ora="09:00", nome="Dentro")
    repo.create(codice="BBB2", servizio="Altro", data="2026-12-10", ora="09:00", nome="Fuori")

    rows = repo.list_all(data_da="2026-12-01", data_a="2026-12-05")
    assert [row["nome"] for row in rows] == ["Dentro"]


def test_list_all_filters_by_servizio(repo):
    repo.create(codice="AAA1", servizio="Anagrafe e stato civile", data="2026-12-01", ora="09:00", nome="Mario")
    repo.create(codice="BBB2", servizio="Altro", data="2026-12-01", ora="10:00", nome="Luigi")

    rows = repo.list_all(servizio="Altro")
    assert [row["nome"] for row in rows] == ["Luigi"]


def test_list_all_combines_date_and_servizio_filters(repo):
    repo.create(codice="AAA1", servizio="Altro", data="2026-12-01", ora="09:00", nome="Match")
    repo.create(codice="BBB2", servizio="Anagrafe e stato civile", data="2026-12-01", ora="10:00", nome="ServizioDiverso")
    repo.create(codice="CCC3", servizio="Altro", data="2026-12-10", ora="09:00", nome="DataFuoriRange")

    rows = repo.list_all(data_da="2026-12-01", data_a="2026-12-05", servizio="Altro")
    assert [row["nome"] for row in rows] == ["Match"]

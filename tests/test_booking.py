import sqlite3

import pytest

from backend.app.db.session import init_db
from backend.app.services.appointments import booking
from backend.app.services.appointments.repository import AppointmentRepository

SLOT_HOURS = ["09:00", "10:00", "11:00", "12:00"]


@pytest.fixture
def repo():
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    return AppointmentRepository(conn)


def test_disponibilita_all_free(repo):
    out = booking.disponibilita(repo, {"servizio": "anagrafe", "data": "2026-12-01"}, SLOT_HOURS)
    assert out == {"servizio": "anagrafe", "data": "2026-12-01", "slot_liberi": SLOT_HOURS}


def test_disponibilita_excludes_booked(repo):
    repo.create(codice="AAA1", servizio="anagrafe", data="2026-12-01", ora="09:00", nome="Mario")
    out = booking.disponibilita(repo, {"servizio": "anagrafe", "data": "2026-12-01"}, SLOT_HOURS)
    assert out["slot_liberi"] == ["10:00", "11:00", "12:00"]


def test_disponibilita_full_day(repo):
    for ora in SLOT_HOURS:
        repo.create(codice=f"C{ora}", servizio="anagrafe", data="2026-12-01", ora=ora, nome="x")
    out = booking.disponibilita(repo, {"servizio": "anagrafe", "data": "2026-12-01"}, SLOT_HOURS)
    assert out["slot_liberi"] == []
    assert out["esito"] == "pieno"


def test_disponibilita_rejects_bad_input(repo):
    out = booking.disponibilita(repo, {"servizio": "anagrafe", "data": "01/12/2026"}, SLOT_HOURS)
    assert out["esito"] == "errore"


from datetime import date, datetime, timedelta


def test_crea_appuntamento_success(repo):
    out = booking.crea_appuntamento(
        repo,
        {"servizio": "anagrafe", "data": "2026-12-01", "ora": "09:00", "nome": "Mario"},
        SLOT_HOURS,
    )
    assert out["esito"] == "confermato"
    assert len(out["codice"]) == 8
    assert repo.booked_slots("anagrafe", "2026-12-01") == {"09:00"}


def test_crea_appuntamento_double_booking(repo):
    args = {"servizio": "anagrafe", "data": "2026-12-01", "ora": "09:00", "nome": "Mario"}
    booking.crea_appuntamento(repo, args, SLOT_HOURS)
    out = booking.crea_appuntamento(repo, {**args, "nome": "Luigi"}, SLOT_HOURS)
    assert out["esito"] == "errore"
    assert "non disponibile" in out["motivo"]


def test_crea_appuntamento_slot_not_in_grid(repo):
    out = booking.crea_appuntamento(
        repo,
        {"servizio": "anagrafe", "data": "2026-12-01", "ora": "15:00", "nome": "Mario"},
        SLOT_HOURS,
    )
    assert out["esito"] == "errore"


def test_crea_appuntamento_past_date(repo):
    ieri = (date.today() - timedelta(days=1)).isoformat()
    out = booking.crea_appuntamento(
        repo,
        {"servizio": "anagrafe", "data": ieri, "ora": "09:00", "nome": "Mario"},
        SLOT_HOURS,
    )
    assert out["esito"] == "errore"


def test_crea_appuntamento_today_slot_already_passed(repo):
    oggi = date.today().isoformat()
    ora_corrente = datetime.combine(date.today(), datetime.strptime("11:00", "%H:%M").time())
    out = booking.crea_appuntamento(
        repo,
        {"servizio": "anagrafe", "data": oggi, "ora": "09:00", "nome": "Mario"},
        SLOT_HOURS,
        now=ora_corrente,
    )
    assert out["esito"] == "errore"


def test_crea_appuntamento_missing_field(repo):
    out = booking.crea_appuntamento(
        repo, {"servizio": "anagrafe", "data": "2026-12-01", "ora": "09:00"}, SLOT_HOURS
    )
    assert out["esito"] == "errore"

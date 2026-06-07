import pytest

from backend.app.config import settings


@pytest.fixture(autouse=True)
def _admin_auth(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_user", "admin")
    monkeypatch.setattr(settings, "admin_password", "segreto")
    client.auth = ("admin", "segreto")


def test_appointments_requires_auth(client):
    client.auth = None
    resp = client.get("/admin/appointments")
    assert resp.status_code == 401
    assert resp.headers["WWW-Authenticate"] == "Basic"


def test_appointments_accessible_with_auth(client):
    resp = client.get("/admin/appointments")
    assert resp.status_code == 200
    assert "Prenotazioni Servizi" in resp.text


def test_appointments_shows_empty_state_when_no_bookings(client):
    resp = client.get("/admin/appointments")
    assert resp.status_code == 200
    assert "Prenotazioni Servizi" in resp.text
    assert "Nessun appuntamento prenotato" in resp.text


def test_appointments_lists_created_booking(client):
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Anagrafe e stato civile", "data": "2026-12-01", "ora": "09:00", "nome": "Mario Rossi"},
    )

    resp = client.get("/admin/appointments")
    assert "Mario Rossi" in resp.text


def test_appointments_filters_by_servizio(client):
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Anagrafe e stato civile", "data": "2026-12-01", "ora": "09:00", "nome": "Mario Rossi"},
    )
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Altro", "data": "2026-12-01", "ora": "10:00", "nome": "Luigi Verdi"},
    )

    resp = client.get("/admin/appointments?servizio=Altro")
    assert "Luigi Verdi" in resp.text
    assert "Mario Rossi" not in resp.text


def test_appointments_filters_by_date_range(client):
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Altro", "data": "2026-12-01", "ora": "09:00", "nome": "Dentro Range"},
    )
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Altro", "data": "2026-12-10", "ora": "09:00", "nome": "Fuori Range"},
    )

    resp = client.get("/admin/appointments?data_da=2026-12-01&data_a=2026-12-05")
    assert "Dentro Range" in resp.text
    assert "Fuori Range" not in resp.text


def test_appointments_with_malformed_date_does_not_break(client):
    resp = client.get("/admin/appointments?data_da=non-una-data")
    assert resp.status_code == 200


def test_appointments_end_date_field_disables_days_before_start_date(client):
    resp = client.get("/admin/appointments?data_da=2026-06-10")
    assert 'id="data_a" name="data_a" value="" min="2026-06-10"' in resp.text


def test_appointments_end_date_field_syncs_min_live_from_start_date(client):
    # Il campo "Al" deve aggiornare il proprio min in tempo reale quando
    # cambia "Dal", senza dover prima inviare il form.
    resp = client.get("/admin/appointments")
    assert 'data_da.addEventListener' in resp.text
    assert 'data_a.min = data_da.value' in resp.text


def test_appointments_ignores_end_date_before_start_date(client):
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Altro", "data": "2026-12-01", "ora": "09:00", "nome": "Prima Range"},
    )
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Altro", "data": "2026-12-10", "ora": "09:00", "nome": "Dopo Range"},
    )

    resp = client.get("/admin/appointments?data_da=2026-12-10&data_a=2026-12-01")
    assert "Dopo Range" in resp.text
    assert "Prima Range" not in resp.text

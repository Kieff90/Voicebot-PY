def test_disponibilita_endpoint_returns_plain_result(client):
    resp = client.post("/tools/disponibilita", json={"servizio": "anagrafe", "data": "2026-12-01"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["slot_liberi"] == ["09:00", "10:00", "11:00", "12:00"]


def test_crea_appuntamento_endpoint_then_unavailable(client):
    args = {"servizio": "anagrafe", "data": "2026-12-01", "ora": "09:00", "nome": "Mario"}
    first = client.post("/tools/crea_appuntamento", json=args)
    assert first.json()["esito"] == "confermato"

    second = client.post("/tools/crea_appuntamento", json={**args, "nome": "Luigi"})
    assert second.json()["esito"] == "errore"

def _envelope(name, arguments, call_id="c1"):
    return {
        "message": {
            "type": "tool-calls",
            "toolCallList": [{"id": call_id, "name": name, "arguments": arguments}],
        }
    }


def test_disponibilita_endpoint_returns_results_envelope(client):
    payload = _envelope("disponibilita", {"servizio": "anagrafe", "data": "2026-12-01"})
    resp = client.post("/tools/disponibilita", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["results"][0]["toolCallId"] == "c1"
    assert body["results"][0]["result"]["slot_liberi"] == ["09:00", "10:00", "11:00", "12:00"]


def test_crea_appuntamento_endpoint_then_unavailable(client):
    args = {"servizio": "anagrafe", "data": "2026-12-01", "ora": "09:00", "nome": "Mario"}
    first = client.post("/tools/crea_appuntamento", json=_envelope("crea_appuntamento", args))
    assert first.json()["results"][0]["result"]["esito"] == "confermato"

    second = client.post(
        "/tools/crea_appuntamento", json=_envelope("crea_appuntamento", {**args, "nome": "Luigi"})
    )
    assert second.json()["results"][0]["result"]["esito"] == "errore"

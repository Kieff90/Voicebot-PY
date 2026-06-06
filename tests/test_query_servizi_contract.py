def _envelope(arguments, call_id="q1"):
    return {
        "message": {
            "type": "tool-calls",
            "toolCallList": [{"id": call_id, "name": "query_servizi", "arguments": arguments}],
        }
    }


def test_query_servizi_returns_results_envelope(client):
    resp = client.post("/tools/query_servizi", json=_envelope({"domanda": "tari rifiuti"}))
    assert resp.status_code == 200
    body = resp.json()
    assert body["results"][0]["toolCallId"] == "q1"
    result = body["results"][0]["result"]
    assert result["esito"] == "ok"
    assert result["risultati"][0]["fonte"] == "tributi"


def test_query_servizi_accepts_arguments_as_json_string(client):
    # Vapi a volte invia arguments come stringa JSON
    resp = client.post("/tools/query_servizi", json=_envelope('{"domanda": "tari rifiuti"}'))
    assert resp.status_code == 200
    assert resp.json()["results"][0]["result"]["esito"] == "ok"

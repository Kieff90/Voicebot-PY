def test_query_servizi_returns_plain_result(client):
    resp = client.post("/tools/query_servizi", json={"domanda": "tributi tari rifiuti"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["esito"] == "ok"
    assert result["risultati"][0]["fonte"] == "tributi"

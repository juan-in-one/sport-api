async def test_health_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_create_and_get_challenge(client):
    payload = {
        "category": "race",
        "name": "Media maratón de Zamora",
        "challenge_date": "2026-03-01",
        "distance_km": 21.1,
    }

    create_response = await client.post("/challenges", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == payload["name"]
    assert created["status"] == "pending"  # valor por defecto del schema

    get_response = await client.get(f"/challenges/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == created["id"]


async def test_get_nonexistent_challenge_returns_404(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/challenges/{fake_id}")
    assert response.status_code == 404


async def test_delete_challenge(client):
    payload = {
        "category": "mountain",
        "name": "Pico de prueba",
        "challenge_date": "2026-04-01",
    }
    created = (await client.post("/challenges", json=payload)).json()

    delete_response = await client.delete(f"/challenges/{created['id']}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/challenges/{created['id']}")
    assert get_response.status_code == 404

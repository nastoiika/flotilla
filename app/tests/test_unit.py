def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200

def test_boats_page(client):
    res = client.get("/boats")
    assert res.status_code == 200

def test_trips_page(client):
    res = client.get("/trips")
    assert res.status_code == 200

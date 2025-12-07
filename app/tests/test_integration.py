from app import db
from models import Boat

def test_add_boat(client):
    res = client.post("/boats/add", data={
        "name": "TestBoat",
        "boat_type": "Fishing",
        "displacement": "123.4",
        "build_date": "2024-01-01"
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"TestBoat" in res.data

def test_edit_boat(client):
    boat = Boat(
        name="Old",
        boat_type="Type",
        displacement=1.0,
        build_date="2024-01-01"
    )
    db.session.add(boat)
    db.session.commit()

    res = client.post(f"/boats/{boat.id}/edit", data={
        "name": "New",
        "boat_type": "Type",
        "displacement": "2.0",
        "build_date": "2024-01-01"
    }, follow_redirects=True)

    assert res.status_code == 200

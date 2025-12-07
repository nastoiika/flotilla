import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pytest
from app import app, db
from models import Boat
from datetime import date 

@pytest.fixture
def client():
    # Включаем режим тестирования
    app.config["TESTING"] = True

    # ПЕРЕопределяем базу на SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.drop_all()
        db.create_all()

        with app.test_client() as client:
            yield client

@pytest.fixture
def test_boat():
    """Создаёт тестовую лодку и возвращает её ID"""
    with app.app_context():
        boat = Boat(
            name="TestBoat",
            boat_type="TestType",
            displacement=100.0,
            build_date=date(2023, 1, 1)
        )
        db.session.add(boat)
        db.session.commit()
        return boat.id
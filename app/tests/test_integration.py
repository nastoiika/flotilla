# tests/test_integration.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from datetime import date
from app import app, db
from models import Boat

def test_add_boat(client):
    """Тест добавления лодки через форму"""
    res = client.post("/boats/add", data={
        "name": "TestBoat",
        "boat_type": "Fishing",
        "displacement": "123.4",
        "build_date": "2024-01-01"
    }, follow_redirects=True)

    assert res.status_code == 200
    # Проверяем что лодка добавлена (по имени)
    assert b"TestBoat" in res.data
    
    # Проверяем, что лодка действительно добавилась в БД
    with app.app_context():
        boat = Boat.query.filter_by(name="TestBoat").first()
        assert boat is not None
        assert boat.boat_type == "Fishing"
        assert boat.displacement == 123.4
        assert boat.build_date == date(2024, 1, 1)

def test_edit_boat(client, test_boat):
    """Тест редактирования лодки"""
    # test_boat содержит ID созданной лодки из фикстуры
    
    # Редактируем лодку
    res = client.post(f"/boats/{test_boat}/edit", data={
        "name": "UpdatedBoat",
        "boat_type": "UpdatedType",
        "displacement": "200.5",
        "build_date": "2023-06-15"
    }, follow_redirects=True)

    assert res.status_code == 200
    
    # Проверяем что имя обновилось
    assert b"UpdatedBoat" in res.data
    
    # Проверяем изменения в БД
    with app.app_context():
        updated_boat = Boat.query.get(test_boat)
        assert updated_boat.name == "UpdatedBoat"

def test_boats_page(client):
    """Тест страницы списка лодок"""
    res = client.get("/boats")
    assert res.status_code == 200
    # Проверяем наличие таблицы или заголовка
    # Можно проверять по классам CSS или структуре HTML
    assert b"<table" in res.data or b"<tbody" in res.data or b"boat" in res.data.lower()

def test_trips_page(client):
    """Тест страницы списка рейсов"""
    res = client.get("/trips")
    assert res.status_code == 200
    # Проверяем общую структуру
    assert b"<html" in res.data or b"<!DOCTYPE" in res.data

def test_trips_page_content(client):
    """Более детальная проверка страницы рейсов"""
    res = client.get("/trips")
    assert res.status_code == 200
    
    # Декодируем ответ в строку для проверки кириллицы
    html_content = res.data.decode('utf-8')
    
    # Проверяем наличие ожидаемых элементов (английские названия)
    assert "trip" in html_content.lower() or "trips" in html_content.lower()
    
    # ИЛИ если у вас есть конкретные элементы на странице:
    # assert "departure" in html_content.lower() or "return" in html_content.lower()
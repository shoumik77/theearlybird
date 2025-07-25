# tests/test_main.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import models, scraper
from app.database import SessionLocal, engine
from sqlalchemy.orm import Session
from datetime import date
from unittest.mock import patch

client = TestClient(app)

# Reset DB before each test
@pytest.fixture(autouse=True)
def reset_db():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    yield

# Utility to create products
def create_product(db: Session, name, description, launch_date, auto_tags):
    product = models.Product(
        name=name,
        description=description,
        launch_date=launch_date,
        url=f"https://example.com/{name.lower().replace(' ', '-')}",
        auto_tags=auto_tags
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# Test: refresh-feed (mocked)
def test_refresh_feed():
    with patch.object(scraper, "sync_new_products", return_value=None):
        response = client.post("/refresh-feed")
        assert response.status_code == 200
        assert response.json() == {"message": "Feed refreshed successfully"}

# Test: basic retrieval
def test_get_products_basic():
    db = SessionLocal()
    try:
        create_product(db, "Test App", "A cool test app", date(2024, 6, 1), ["AI"])
    finally:
        db.close()

    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test App"

# Test: filters — query, tag, date
def test_get_products_with_filters():
    db = SessionLocal()
    try:
        create_product(db, "AI Tool", "AI startup", date(2024, 6, 1), ["AI"])
        create_product(db, "Fintech App", "Finance startup", date(2024, 7, 1), ["Fintech"])
    finally:
        db.close()

    # Query search
    r = client.get("/products", params={"query": "AI"})
    assert len(r.json()) == 1

    # Tag filter
    r = client.get("/products", params={"tag": "Fintech"})
    assert len(r.json()) == 1
    assert r.json()[0]["name"] == "Fintech App"

    # Date filter
    r = client.get("/products", params={"start_date": "2024-06-15", "end_date": "2024-08-01"})
    assert len(r.json()) == 1
    assert r.json()[0]["name"] == "Fintech App"

# Test: pagination
def test_get_products_pagination():
    db = SessionLocal()
    try:
        for i in range(5):
            create_product(db, f"App {i}", "desc", date(2024, 6, i+1), ["Tool"])
    finally:
        db.close()

    r = client.get("/products", params={"limit": 2, "offset": 0})
    assert len(r.json()) == 2

    r = client.get("/products", params={"limit": 2, "offset": 2})
    assert len(r.json()) == 2

# Test: trends aggregation
def test_trends_month_aggregation():
    db = SessionLocal()
    try:
        create_product(db, "AI App", "desc", date(2024, 6, 1), ["AI"])
        create_product(db, "AI App 2", "desc", date(2024, 6, 15), ["AI"])
        create_product(db, "Fin App", "desc", date(2024, 7, 1), ["Fintech"])
    finally:
        db.close()

    r = client.get("/trends", params={"interval": "month"})
    data = r.json()
    assert "AI" in data
    assert "2024-06" in data["AI"]
    assert data["AI"]["2024-06"] == 2
    assert data["Fintech"]["2024-07"] == 1

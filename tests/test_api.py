"""Integration tests for FastAPI endpoints."""
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DailyProjectApp"


def test_process_endpoint_success():
    payload = {
        "query": "microservices",
        "items": [
            {
                "id": "101",
                "title": "Cloud Architecture",
                "content": "Designing microservices for resilient cloud workloads.",
                "tags": ["cloud", "microservices"]
            }
        ],
        "top_k": 3
    }
    response = client.post("/api/v1/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "microservices"
    assert data["matches_found"] == 1
    assert data["results"][0]["item_id"] == "101"


def test_process_endpoint_empty_query():
    payload = {
        "query": "   ",
        "items": [],
        "top_k": 3
    }
    response = client.post("/api/v1/process", json=payload)
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]

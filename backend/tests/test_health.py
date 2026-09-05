"""Phase 2 smoke test: the API boots and responds, regardless of whether a
real database is reachable in the environment running the test."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_responds() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["data"]["service"]


def test_health_reports_api_ok_even_if_db_is_down() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["api"] == "ok"
    assert body["database"] in {"connected", "unreachable"}


def test_unknown_route_returns_structured_404() -> None:
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    assert "error" in response.json()

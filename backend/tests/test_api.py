"""
Integration tests for EvalForge FastAPI REST endpoints.
"""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "EvalForge" in data["message"]
    assert "docs" in data
    assert "health" in data


def test_health_check_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "EvalForge"
    assert "mongodb_status" in data


def test_leaderboard_endpoint(client: TestClient):
    response = client.get("/api/v1/benchmarks/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_models" in data
    assert "leaderboard" in data
    assert isinstance(data["leaderboard"], list)


def test_dataset_not_found(client: TestClient):
    response = client.get("/api/v1/datasets/ds_non_existent_999999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_benchmark_run_not_found(client: TestClient):
    response = client.get("/api/v1/benchmarks/runs/run_non_existent_999999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_compare_nonexistent_dataset(client: TestClient):
    response = client.get("/api/v1/benchmarks/compare/ds_non_existent_999999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

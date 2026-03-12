"""Unit tests for the GitOps Pipeline Flask API."""

import json

import pytest

from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client):
        response = client.get("/health")
        data = json.loads(response.data)
        assert data["status"] == "healthy"

    def test_health_has_timestamp(self, client):
        response = client.get("/health")
        data = json.loads(response.data)
        assert "timestamp" in data


class TestVersionEndpoint:
    def test_version_returns_200(self, client):
        response = client.get("/version")
        assert response.status_code == 200

    def test_version_contains_version_field(self, client):
        response = client.get("/version")
        data = json.loads(response.data)
        assert "version" in data

    def test_version_contains_commit_field(self, client):
        response = client.get("/version")
        data = json.loads(response.data)
        assert "commit" in data


class TestReadinessEndpoint:
    def test_ready_returns_200(self, client):
        response = client.get("/ready")
        assert response.status_code == 200

    def test_ready_returns_true(self, client):
        response = client.get("/ready")
        data = json.loads(response.data)
        assert data["ready"] is True

    def test_ready_has_uptime(self, client):
        response = client.get("/ready")
        data = json.loads(response.data)
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], float)


class TestMetricsEndpoint:
    def test_metrics_returns_200(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_has_uptime(self, client):
        response = client.get("/metrics")
        data = json.loads(response.data)
        assert "uptime_seconds" in data

    def test_metrics_has_request_count(self, client):
        response = client.get("/metrics")
        data = json.loads(response.data)
        assert "request_count" in data
        assert isinstance(data["request_count"], int)


class TestRootEndpoint:
    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_has_app_name(self, client):
        response = client.get("/")
        data = json.loads(response.data)
        assert data["app"] == "gitops-pipeline"

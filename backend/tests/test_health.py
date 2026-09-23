"""
Phase 1 tests: liveness endpoint must always report healthy, and the app
must expose OpenAPI docs. Readiness is tested separately since it depends
on external services that may not be present in every environment.
"""


def test_health_endpoint_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["service"] == "nexus-backend"


def test_health_endpoint_available_under_v1_prefix(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_openapi_docs_available(client):
    resp = client.get("/docs")
    assert resp.status_code == 200


def test_openapi_schema_available(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert schema["info"]["title"] == "NEXUS"


def test_ready_endpoint_returns_structured_response_even_when_deps_down(client):
    """
    In this dev/test environment there is no live Postgres/Redis, so /ready
    is expected to report not_ready with a 503 — the important behaviour is
    that it responds with a well-formed structured payload rather than
    crashing.
    """
    resp = client.get("/ready")
    assert resp.status_code in (200, 503)
    body = resp.json()
    assert "dependencies" in body
    assert "database" in body["dependencies"]
    assert "redis" in body["dependencies"]

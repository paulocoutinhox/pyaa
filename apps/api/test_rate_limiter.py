import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from pyaa.fastapi import rate_limiter


@pytest.fixture
def limited_client():
    # build a minimal app guarded by the rate limiter middleware so we can
    # trip the configured limits without touching the real api routes
    app = FastAPI()

    @app.get("/api/ping")
    def api_ping():
        return {"ok": True}

    @app.get("/health")
    def health():
        return {"ok": True}

    rate_limiter.setup(app)

    with TestClient(app) as test_client:
        yield test_client


def _build_request(path: str) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [],
    }
    return Request(scope)


def test_should_apply_limiter_for_api_path():
    assert rate_limiter.should_apply_limiter(_build_request("/api/ping")) is True


def test_should_apply_limiter_for_non_api_path():
    assert rate_limiter.should_apply_limiter(_build_request("/health")) is False


def test_requests_under_limit_pass(limited_client):
    # the total limiter allows 3 hits per interval
    for _ in range(3):
        response = limited_client.get("/api/ping")
        assert response.status_code == 200


def test_requests_over_limit_return_429(limited_client):
    # the first three pass, the fourth trips the total limiter
    for _ in range(3):
        assert limited_client.get("/api/ping").status_code == 200

    response = limited_client.get("/api/ping")
    assert response.status_code == 429


def test_non_api_path_is_never_limited(limited_client):
    # non-api paths bypass the limiter entirely
    codes = [limited_client.get("/health").status_code for _ in range(6)]
    assert codes == [200] * 6

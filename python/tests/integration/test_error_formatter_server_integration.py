"""BoltAPI(error_formatter=...) over a real ``runbolt`` server.

runbolt gives the formatter to the Rust server at startup, so the errors of
the Rust core use it too.
"""

from __future__ import annotations

import pytest

from .apps import app_module


@pytest.mark.server_integration
def test_problem_details_end_to_end(make_server_project):
    project = make_server_project(api_module=app_module("error_formatter"))
    with project.start(startup_path="/health") as server:
        unauthenticated = server.request("GET", "/private")
        missing = server.request("GET", "/nowhere")
        invalid = server.request("GET", "/items/not-a-uuid")
        conflict = server.request("GET", "/conflict")
        ok = server.request("GET", "/health")

    assert unauthenticated.status_code == 401
    assert unauthenticated.headers["content-type"] == "application/problem+json"
    assert unauthenticated.headers["www-authenticate"] == "Bearer"
    assert unauthenticated.json() == {
        "type": "about:blank",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Authentication required",
        "instance": "/private",
    }

    assert missing.status_code == 404
    assert missing.json()["instance"] == "/nowhere"

    assert invalid.status_code == 422
    assert invalid.json()["errors"][0]["loc"] == ["path", "item_id"]

    assert conflict.status_code == 409
    assert conflict.headers["content-type"] == "application/problem+json"
    assert conflict.json()["detail"] == "Already exists"

    assert ok.json() == {"status": "ok"}

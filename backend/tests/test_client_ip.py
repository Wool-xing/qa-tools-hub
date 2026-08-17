"""_client_ip XFF trust tests (QA-2026-08-18 HIGH #4)."""
import importlib

from fastapi import Request
from starlette.testclient import TestClient

from fastapi import Request
from starlette.testclient import TestClient

import app.routers.auth as auth_module
from app.main import app

client = TestClient(app)


def _request(headers: dict):
    # Build a starlette Request with given headers via a tiny ASGI capture
    scope = {
        "type": "http", "method": "GET", "path": "/", "headers": [
            (k.lower().encode(), v.encode()) for k, v in headers.items()
        ], "client": ("9.9.9.9", 1234),
    }
    return Request(scope)


def test_direct_mode_ignores_forged_xff(monkeypatch):
    monkeypatch.setattr(auth_module, "TRUST_PROXY", False)
    r = _request({"X-Forwarded-For": "1.2.3.4, 5.6.7.8"})
    assert auth_module._client_ip(r) == "9.9.9.9"


def test_proxy_mode_takes_last_xff_value(monkeypatch):
    monkeypatch.setattr(auth_module, "TRUST_PROXY", True)
    r = _request({"X-Forwarded-For": "1.2.3.4, 5.6.7.8"})
    assert auth_module._client_ip(r) == "5.6.7.8"


def test_no_xff_uses_client_host(monkeypatch):
    monkeypatch.setattr(auth_module, "TRUST_PROXY", True)
    r = _request({})
    assert auth_module._client_ip(r) == "9.9.9.9"

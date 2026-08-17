"""SPA static routing regression tests (QA-2026-08-18 HIGH #7: white screen)."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

REAL_ASSET = "A11yLabView-BUklYy4S.js"


def test_qa_test_index_served_as_html():
    r = client.get("/QA_Test/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_qa_test_asset_served_with_correct_mime():
    r = client.get(f"/QA_Test/assets/{REAL_ASSET}")
    assert r.status_code == 200
    assert "javascript" in r.headers["content-type"].lower()


def test_missing_asset_returns_404_not_html():
    r = client.get("/QA_Test/assets/nonexistent-file.js")
    assert r.status_code == 404
    assert "text/html" not in r.headers.get("content-type", "")


def test_qa_test_deep_route_serves_index():
    r = client.get("/QA_Test/levels/5")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_path_traversal_does_not_leak_files():
    r = client.get("/QA_Test/../app/config.py")
    assert r.status_code != 200 or "SECRET_KEY" not in r.text

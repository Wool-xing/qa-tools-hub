"""SECRET_KEY empty/whitespace fallback tests (QA-2026-08-18 HIGH #3)."""
import importlib
import os

import app.config as config_module

WEAK_DEFAULT = "dev-secret-change-me-in-production!!"


def _reload_with(monkeypatch, value):
    monkeypatch.setenv("SECRET_KEY", value)
    importlib.reload(config_module)


def _restore(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    importlib.reload(config_module)


def test_empty_secret_key_falls_back_to_weak_default(monkeypatch):
    _reload_with(monkeypatch, "")
    assert config_module.SECRET_KEY == WEAK_DEFAULT
    _restore(monkeypatch)


def test_whitespace_secret_key_falls_back_to_weak_default(monkeypatch):
    _reload_with(monkeypatch, "   ")
    assert config_module.SECRET_KEY == WEAK_DEFAULT
    _restore(monkeypatch)


def test_strong_secret_key_is_preserved(monkeypatch):
    _reload_with(monkeypatch, "strong-secret-xyz")
    assert config_module.SECRET_KEY == "strong-secret-xyz"
    _restore(monkeypatch)

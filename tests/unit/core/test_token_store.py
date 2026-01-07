from __future__ import annotations

import json

import pytest

from app.core import token_store


class DummyKeyring:
    """Keyring dummy pour piloter les chemins keyring/fallback."""

    def __init__(self) -> None:
        self.store: dict[tuple[str, str], str] = {}
        self.raise_on_set = False
        self.raise_on_get = False

    def set_password(self, service: str, name: str, value: str) -> None:
        if self.raise_on_set:
            raise RuntimeError("set failed")
        self.store[(service, name)] = value

    def get_password(self, service: str, name: str):
        if self.raise_on_get:
            raise RuntimeError("get failed")
        return self.store.get((service, name))

    def delete_password(self, service: str, name: str) -> None:
        self.store.pop((service, name), None)


def test_token_store_file_roundtrip(monkeypatch, tmp_path):
    """Sauvegarde/charge/efface via fallback fichier."""
    monkeypatch.setattr(token_store, "keyring", None)
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")

    token_store.save_tokens("a1", "r1")
    assert token_store.load_access_token() == "a1"
    assert token_store.load_refresh_token() == "r1"

    token_store.clear_tokens()
    assert token_store.load_access_token() is None
    assert token_store.load_refresh_token() is None


def test_token_store_load_returns_none_when_file_missing(monkeypatch, tmp_path):
    """Charge None si le fichier tokens.json n'existe pas."""
    monkeypatch.setattr(token_store, "keyring", None)
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")

    assert token_store.load_access_token() is None
    assert token_store.load_refresh_token() is None


def test_token_store_file_corrupt_json_raises(monkeypatch, tmp_path):
    """JSON corrompu lève JSONDecodeError au chargement."""
    monkeypatch.setattr(token_store, "keyring", None)
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")

    (tmp_path / "tokens.json").write_text("{not-json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        token_store.load_access_token()


def test_token_store_uses_keyring_when_available(monkeypatch, tmp_path):
    """Utilise keyring si dispo et n'écrit pas le fichier."""
    dummy = DummyKeyring()
    monkeypatch.setattr(token_store, "keyring", dummy)
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")

    token_store.save_tokens("a2", "r2")

    assert token_store.load_access_token() == "a2"
    assert token_store.load_refresh_token() == "r2"
    assert not (tmp_path / "tokens.json").exists()

    token_store.clear_tokens()
    assert token_store.load_access_token() is None
    assert token_store.load_refresh_token() is None


def test_token_store_falls_back_to_file_when_keyring_set_fails(monkeypatch, tmp_path):
    """Fallback fichier si keyring échoue à l'écriture."""
    dummy = DummyKeyring()
    dummy.raise_on_set = True
    monkeypatch.setattr(token_store, "keyring", dummy)
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")

    token_store.save_tokens("a3", "r3")

    assert (tmp_path / "tokens.json").exists()
    assert token_store.load_access_token() == "a3"
    assert token_store.load_refresh_token() == "r3"


def test_token_store_falls_back_to_file_when_keyring_get_fails(monkeypatch, tmp_path):
    """Fallback fichier si keyring échoue à la lecture."""
    dummy = DummyKeyring()
    dummy.raise_on_get = True
    monkeypatch.setattr(token_store, "keyring", dummy)
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")

    (tmp_path / "tokens.json").write_text(
        json.dumps({"access_token": "a4", "refresh_token": "r4"}), encoding="utf-8"
    )

    assert token_store.load_access_token() == "a4"
    assert token_store.load_refresh_token() == "r4"

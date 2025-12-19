from pytest import CaptureFixture, MonkeyPatch

from tests.conftest import reload_module


class _FakeResult:
    def scalar_one(self):
        return 1


class _FakeConn:
    def execute(self, _):
        return _FakeResult()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeEngine:
    def connect(self):
        return _FakeConn()


def test_db_check_sqlalchemy_prints_ok(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
):
    """Vérifie que le script de healthcheck DB affiche OK si SELECT 1 passe."""
    monkeypatch.setattr("app.db.engine.get_engine", lambda: _FakeEngine())

    reload_module("app.db.db_check_sqlalchemy")

    captured = capsys.readouterr()
    assert "Engine OK" in captured.out

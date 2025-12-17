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
    # Patch l'engine importé par le script
    monkeypatch.setattr("app.db.engine.engine", _FakeEngine())

    reload_module("app.db.db_check_sqlalchemy")

    captured = capsys.readouterr()
    assert "✅ Engine OK (SELECT 1 -> 1)" in captured.out

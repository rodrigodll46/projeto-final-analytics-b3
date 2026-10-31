import pandas as pd
import pytest

from src import database
from src.schema import DataQualityError


@pytest.fixture(autouse=True)
def clear_cache():
    database.load_data.clear()
    database.read_csv.clear()
    database.read_postgresql.clear()
    yield
    database.load_data.clear()


def fail_database():
    raise ConnectionError("postgresql://username:SECRET@private-host/database")


def test_database_is_primary(monkeypatch, full_frame):
    monkeypatch.setattr(database, "read_postgresql", lambda: full_frame)
    loaded = database.load_data("inexistente.csv")
    assert loaded.source == "PostgreSQL"
    assert loaded.fallback_reason is None
    pd.testing.assert_frame_equal(loaded.frame, full_frame)


def test_database_failure_uses_csv_without_leaking_secrets(monkeypatch, full_frame, tmp_path):
    monkeypatch.setattr(database, "read_postgresql", fail_database)
    path = tmp_path / "contingencia.csv"
    full_frame.to_csv(path, index=False)
    # O caminho temporário é fornecido pelo pytest, não é um caminho de produção.
    loaded = database.load_data(str(path))
    assert loaded.source == "CSV local"
    assert loaded.fallback_reason == "ConnectionError"
    assert len(loaded.frame) == len(full_frame)
    assert "SECRET" not in repr(loaded)


def test_invalid_database_can_fallback(monkeypatch, full_frame):
    def invalid():
        raise DataQualityError("Base incompleta")

    monkeypatch.setattr(database, "read_postgresql", invalid)
    monkeypatch.setattr(database, "read_csv", lambda _, revision=0: full_frame)
    assert database.load_data().source == "CSV local"


def test_both_sources_fail_with_safe_instruction(monkeypatch):
    monkeypatch.setattr(database, "read_postgresql", fail_database)
    with pytest.raises(database.DataUnavailableError, match="python -m src.etl") as error:
        database.load_data("nao_existe.csv")
    assert "SECRET" not in str(error.value)
    assert "private-host" not in str(error.value)


def test_csv_revision_invalidates_inner_cache(monkeypatch, full_frame, tmp_path):
    monkeypatch.setattr(database, "read_postgresql", fail_database)
    path = tmp_path / "revisao.csv"
    full_frame.to_csv(path, index=False)
    first = database.load_data(str(path), revision=1)
    changed = full_frame.copy()
    changed["Adj Close"] *= 1.01
    changed.to_csv(path, index=False)
    second = database.load_data(str(path), revision=2)
    assert second.frame["Adj Close"].iloc[0] != first.frame["Adj Close"].iloc[0]


@pytest.mark.parametrize("has_admin", [True, False])
def test_upload_uses_separate_writer_when_configured(monkeypatch, full_frame, has_admin):
    class ConnectionSelected(Exception):
        pass

    selected = []
    connections = {"postgresql": {}}
    if has_admin:
        connections["postgresql_admin"] = {}
    monkeypatch.setattr(database.st, "secrets", {"connections": connections})

    def connect(name, **kwargs):
        selected.append(name)
        raise ConnectionSelected

    monkeypatch.setattr(database.st, "connection", connect)
    with pytest.raises(ConnectionSelected):
        database.upload_prices(full_frame)
    assert selected == ["postgresql_admin" if has_admin else "postgresql"]

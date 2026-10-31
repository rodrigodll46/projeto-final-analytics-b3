"""Usa apenas o banco descartável analytics_test disponibilizado pela CI."""

import os

import pandas as pd
import pytest
from sqlalchemy import text
from streamlit.connections import SQLConnection

from src import database

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("B3_INTEGRATION_POSTGRES") != "1",
        reason="Banco PostgreSQL descartável é iniciado no job de integração da CI.",
    ),
]


def test_postgres_upsert_read_and_idempotency(monkeypatch, full_frame):
    # Credenciais públicas de um container efêmero; nunca usar em produção.
    config = {
        "dialect": "postgresql",
        "driver": "psycopg",
        "host": "127.0.0.1",
        "port": 5432,
        "database": "analytics_test",
        "username": "postgres",
        "password": "test-only-disposable-password",
    }
    connection = SQLConnection("postgresql", **config)
    monkeypatch.setattr(database.st, "secrets", {"connections": {"postgresql": config}})
    monkeypatch.setattr(database.st, "connection", lambda *args, **kwargs: connection)
    database.read_postgresql.clear()
    database.load_data.clear()
    try:
        database.upload_prices(full_frame)
        database.upload_prices(full_frame)
        actual = database.read_postgresql()
        expected = full_frame.sort_values(["Data", "Ativo"]).reset_index(drop=True)
        pd.testing.assert_frame_equal(expected, actual, check_dtype=False)
        with connection.engine.connect() as db:
            count = db.execute(text("SELECT count(*) FROM b3_prices")).scalar_one()
        assert count == len(full_frame)
        changed = full_frame.copy()
        changed["Adj Close"] *= 1.01
        database.upload_prices(changed)
        updated = database.read_postgresql()
        assert updated["Adj Close"].iloc[0] == pytest.approx(actual["Adj Close"].iloc[0] * 1.01)
        assert database.load_data().source == "PostgreSQL"
    finally:
        database.read_postgresql.clear()
        database.load_data.clear()
        connection.engine.dispose()

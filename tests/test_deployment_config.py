import tomllib
from pathlib import Path

import pytest


@pytest.mark.parametrize("filename", ["secrets.toml.example", "secrets.supabase.toml.example"])
def test_example_uses_encrypted_connection_and_effective_timeout(filename):
    config = tomllib.loads((Path(".streamlit") / filename).read_text(encoding="utf-8"))
    connection = config["connections"]["postgresql"]
    assert connection["query"]["sslmode"] == "require"
    assert connection["create_engine_kwargs"]["connect_args"]["connect_timeout"] == 5
    assert connection["driver"] == "psycopg"

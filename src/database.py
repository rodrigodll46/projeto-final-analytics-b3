"""Leitura PostgreSQL prioritária com contingência CSV e carga transacional."""

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import Column, Date, Float, MetaData, String, Table
from sqlalchemy.dialects.postgresql import insert

from src.config import DATA_PATH, DB_COLUMNS, END, START
from src.schema import validate_data


class DataUnavailableError(RuntimeError):
    """Nenhuma fonte válida disponível."""


@dataclass
class LoadResult:
    frame: pd.DataFrame
    source: str
    fallback_reason: str | None = None


@st.cache_data(ttl=3600)
def read_csv(path: str, revision: int = 0) -> pd.DataFrame:
    return validate_data(pd.read_csv(Path(path), parse_dates=["Data"]))


@st.cache_data(ttl=3600)
def read_postgresql() -> pd.DataFrame:
    # st.connection resolve [connections.postgresql] diretamente de st.secrets.
    conn = st.connection("postgresql", type="sql")
    columns = ", ".join(f'"{db}" AS "{local}"' for local, db in DB_COLUMNS.items())
    frame = conn.query(
        f'SELECT {columns} FROM b3_prices WHERE "data" BETWEEN :start AND :end',
        params={"start": START, "end": END},
        ttl=3600,
        show_spinner=False,
    )
    return validate_data(frame)


@st.cache_data(ttl=3600)
def load_data(csv_path: str = str(DATA_PATH), revision: int = 0) -> LoadResult:
    """revision invalida o resultado quando o snapshot local é substituído."""
    try:
        return LoadResult(read_postgresql(), "PostgreSQL")
    except Exception as exc:
        # Nunca mostrar/logar a mensagem bruta: drivers podem incluir credenciais.
        reason = type(exc).__name__
        try:
            return LoadResult(read_csv(csv_path, revision=revision), "CSV local", reason)
        except Exception as csv_exc:
            raise DataUnavailableError(
                "Banco indisponível e CSV ausente ou inválido. Execute python -m src.etl. "
                f"Diagnóstico seguro: banco={reason}; CSV={type(csv_exc).__name__}."
            ) from None


def upload_prices(frame: pd.DataFrame) -> None:
    """Idempotente; só grava quando o usuário executa o ETL com --upload."""
    df = validate_data(frame)
    # Leitura explícita via st.secrets, sem valores secretos no código.
    if "postgresql" not in st.secrets.get("connections", {}):
        raise DataUnavailableError("Configure [connections.postgresql] em st.secrets.")
    conn = st.connection("postgresql", type="sql")
    metadata = MetaData()
    table = Table(
        "b3_prices",
        metadata,
        Column("data", Date, primary_key=True),
        Column("ativo", String(10), primary_key=True),
        Column("setor", String(60), nullable=False),
        *(Column(c, Float, nullable=False) for c in list(DB_COLUMNS.values())[3:]),
    )
    rows = df.rename(columns=DB_COLUMNS)
    rows["data"] = rows["data"].dt.date
    records = rows.to_dict("records")
    with conn.engine.begin() as connection:
        metadata.create_all(connection)
        for offset in range(0, len(records), 500):
            statement = insert(table).values(records[offset : offset + 500])
            statement = statement.on_conflict_do_update(
                index_elements=[table.c.data, table.c.ativo],
                set_={c.name: statement.excluded[c.name] for c in table.c if not c.primary_key},
            )
            connection.execute(statement)
    read_postgresql.clear()
    load_data.clear()


def main() -> None:
    parser = argparse.ArgumentParser(description="Carrega e valida o snapshot no PostgreSQL.")
    parser.add_argument(
        "--upload-csv",
        action="store_true",
        help="Faz upsert do CSV já adquirido, sem novo download",
    )
    args = parser.parse_args()
    try:
        expected = read_csv(str(DATA_PATH))
        if args.upload_csv:
            upload_prices(expected)
        read_postgresql.clear()
        actual = read_postgresql()
        pd.testing.assert_frame_equal(
            expected, actual, check_dtype=False, check_exact=False, rtol=1e-7, atol=1e-7
        )
        print(f"PostgreSQL validado: {len(actual)} registros; 12 ativos; snapshot conferido.")
    except Exception as exc:
        # Não imprimir mensagens de drivers que possam incluir senha ou endereço privado.
        print(f"Validação não concluída ({type(exc).__name__}). Confira os secrets e o banco.")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()

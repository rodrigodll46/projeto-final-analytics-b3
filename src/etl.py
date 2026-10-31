"""ETL reexecutável: python -m src.etl [--upload] [--refresh]."""

import argparse
import hashlib
import json
import logging
import time
from datetime import UTC, datetime
from importlib.metadata import version

import pandas as pd
import streamlit as st
import yfinance as yf

from src.config import (
    DATA_PATH,
    DOWNLOAD_END,
    MANIFEST_PATH,
    SECTORS,
    SOURCE_ALIASES,
    START,
    TICKERS,
)
from src.schema import DataQualityError, validate_data

LOGGER = logging.getLogger(__name__)


@st.cache_data(ttl=3600)
def download_prices() -> pd.DataFrame:
    """Baixa o universo completo; qualquer falha impede publicar uma base parcial."""
    frames = []
    source_symbols = {}
    for ticker in TICKERS:
        for attempt in range(3):
            symbol = SOURCE_ALIASES.get(ticker, f"{ticker}.SA") if attempt else f"{ticker}.SA"
            try:
                raw = yf.download(
                    symbol,
                    start=START.isoformat(),
                    end=DOWNLOAD_END,
                    interval="1d",
                    auto_adjust=False,
                    actions=False,
                    progress=False,
                    threads=False,
                    timeout=20,
                    multi_level_index=False,
                )
                if raw is None or raw.empty:
                    raise DataQualityError(f"Yahoo não retornou dados de {ticker}.")
                if isinstance(raw.columns, pd.MultiIndex):
                    raw = raw.xs(symbol, axis=1, level=-1)
                frame = raw.rename_axis("Data").reset_index()
                frame["Ativo"] = ticker
                frame["Setor"] = SECTORS[ticker]
                frame["Volume Financeiro"] = frame["Close"] * frame["Volume"]
                frame = validate_data(frame, require_full=False)
                frames.append(frame)
                source_symbols[ticker] = symbol
                LOGGER.info("%s: %s pregões (fonte: %s)", ticker, len(frame), symbol)
                break
            except Exception as exc:
                if attempt == 2:
                    raise DataQualityError(
                        f"Falha em {ticker} após 3 tentativas; CSV anterior preservado."
                    ) from exc
                LOGGER.warning("Nova tentativa para %s (%s).", ticker, type(exc).__name__)
                time.sleep(2**attempt)
    result = validate_data(pd.concat(frames, ignore_index=True))
    result.attrs["source_symbols"] = source_symbols
    return result


def save_snapshot(frame: pd.DataFrame) -> dict:
    """Valida antes da escrita e publica o CSV com substituição atômica."""
    df = validate_data(frame)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    csv_bytes = df.to_csv(
        index=False, date_format="%Y-%m-%d", float_format="%.10f", lineterminator="\n"
    ).encode("utf-8")
    report = {
        "source": "Yahoo Finance via yfinance",
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "requested_start": START.isoformat(),
        "requested_end_inclusive": "2023-12-31",
        "yfinance_version": version("yfinance"),
        "rows": len(df),
        "tickers": list(TICKERS),
        "source_symbols": frame.attrs.get("source_symbols", {}),
        "first_session": df["Data"].min().date().isoformat(),
        "last_session": df["Data"].max().date().isoformat(),
        "sha256": hashlib.sha256(csv_bytes).hexdigest(),
        "csv_encoding": "UTF-8",
        "csv_line_ending": "LF",
        "financial_volume": "Estimated: Yahoo Close * Yahoo Volume; not official turnover",
        "annual_sessions_per_ticker": {
            ticker: {str(y): int(n) for y, n in g.groupby(g["Data"].dt.year).size().items()}
            for ticker, g in df.groupby("Ativo")
        },
    }
    pending_csv = DATA_PATH.with_suffix(".csv.tmp")
    pending_csv.write_bytes(csv_bytes)
    pending_csv.replace(DATA_PATH)
    pending_manifest = MANIFEST_PATH.with_suffix(".json.tmp")
    pending_manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    pending_manifest.replace(MANIFEST_PATH)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upload", action="store_true", help="Upsert no PostgreSQL via st.secrets")
    parser.add_argument("--refresh", action="store_true", help="Ignora cache da aquisição")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if args.refresh:
        download_prices.clear()
    frame = download_prices()
    report = save_snapshot(frame)
    LOGGER.info("CSV publicado: %s linhas; SHA256 %s", report["rows"], report["sha256"])
    if args.upload:
        from src.database import upload_prices

        upload_prices(frame)
        LOGGER.info("Upsert concluído em b3_prices.")


if __name__ == "__main__":
    main()

import hashlib
import json

import pandas as pd
import pytest

from src import etl
from src.config import TICKERS
from src.schema import DataQualityError


def test_snapshot_digest_and_failed_validation_preserves_csv(monkeypatch, full_frame, tmp_path):
    data_path = tmp_path / "dados.csv"
    manifest_path = tmp_path / "manifest.json"
    monkeypatch.setattr(etl, "DATA_PATH", data_path)
    monkeypatch.setattr(etl, "MANIFEST_PATH", manifest_path)
    report = etl.save_snapshot(full_frame)
    original = data_path.read_bytes()
    assert report["sha256"] == hashlib.sha256(original).hexdigest()
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["rows"] == len(full_frame)
    with pytest.raises(DataQualityError):
        etl.save_snapshot(full_frame.iloc[:10])
    assert data_path.read_bytes() == original


def test_download_contract_and_normalization(monkeypatch, full_frame):
    calls = []

    def download(symbol, **kwargs):
        calls.append((symbol, kwargs))
        raw = full_frame.loc[full_frame["Ativo"].eq(symbol.removesuffix(".SA"))]
        return raw.set_index("Data")[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]

    monkeypatch.setattr(etl.yf, "download", download)
    etl.download_prices.clear()
    result = etl.download_prices()
    assert len(calls) == len(TICKERS)
    assert all(c[1]["end"] == "2024-01-01" for c in calls)
    assert all(c[1]["auto_adjust"] is False for c in calls)
    assert result["Ativo"].nunique() == 12
    etl.download_prices.clear()


def test_failed_download_retries_and_refuses_partial(monkeypatch):
    calls = []

    def empty(*args, **kwargs):
        calls.append(1)
        return pd.DataFrame()

    monkeypatch.setattr(etl.yf, "download", empty)
    monkeypatch.setattr(etl.time, "sleep", lambda _: None)
    etl.download_prices.clear()
    with pytest.raises(DataQualityError, match="3 tentativas"):
        etl.download_prices()
    assert len(calls) == 3


def test_historical_ticker_alias_preserves_universe(monkeypatch, full_frame):
    symbols = []

    def download(symbol, **kwargs):
        symbols.append(symbol)
        if symbol == "EMBR3.SA":
            return pd.DataFrame()
        ticker = "EMBR3" if symbol == "EMBJ3.SA" else symbol.removesuffix(".SA")
        raw = full_frame.loc[full_frame["Ativo"].eq(ticker)]
        return raw.set_index("Data")[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]

    monkeypatch.setattr(etl.yf, "download", download)
    monkeypatch.setattr(etl.time, "sleep", lambda _: None)
    etl.download_prices.clear()
    result = etl.download_prices()
    assert "EMBR3.SA" in symbols and "EMBJ3.SA" in symbols
    assert "EMBR3" in result["Ativo"].unique()
    assert "EMBJ3" not in result["Ativo"].unique()
    assert result.attrs["source_symbols"]["EMBR3"] == "EMBJ3.SA"
    etl.download_prices.clear()

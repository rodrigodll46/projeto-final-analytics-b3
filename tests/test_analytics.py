import numpy as np
import pandas as pd
import pytest

from src.analytics import analyze, enrich_data, export_csv, filter_data
from src.config import COLUMNS


def test_known_returns_drawdown_and_buy_hold(known_prices):
    long, metrics, portfolio = analyze(known_prices)
    metrics = metrics.set_index("Ativo")
    assert metrics.loc["WEGE3", "Retorno Acumulado %"] == pytest.approx(20)
    assert metrics.loc["VALE3", "Retorno Acumulado %"] == pytest.approx(-20)
    assert metrics.loc["WEGE3", "Drawdown Máximo %"] == pytest.approx(-10)
    assert metrics.loc["VALE3", "Drawdown Máximo %"] == pytest.approx(-20)
    assert portfolio.tolist() == pytest.approx([100, 100, 90, 100])
    assert long.groupby("Ativo").first()["Base 100"].eq(100).all()
    assert long["Retorno Diário %"].isna().sum() == 2
    expected = np.std([0.1, -0.1, 120 / 99 - 1], ddof=1) * np.sqrt(252) * 100
    assert metrics.loc["WEGE3", "Volatilidade Anualizada %"] == pytest.approx(expected)


def test_returns_do_not_cross_filter_boundary(known_prices):
    enriched = enrich_data(known_prices)
    cut = filter_data(enriched, ("WEGE3",), "2021-01-05", "2021-01-07")
    long, _, _ = analyze(cut)
    assert pd.isna(long.iloc[0]["Retorno Diário %"])
    assert long.iloc[1]["Retorno Diário %"] == pytest.approx(-10)


def test_sma_uses_prior_history_without_future(full_frame):
    enriched = enrich_data(full_frame)
    ticker = enriched.loc[enriched["Ativo"].eq("WEGE3")].reset_index(drop=True)
    assert ticker.loc[:19, "SMA 21"].isna().all()
    assert ticker.loc[20, "SMA 21"] == pytest.approx(ticker.loc[:20, "Adj Close"].mean())
    assert ticker.loc[49, "SMA 50"] == pytest.approx(ticker.loc[:49, "Adj Close"].mean())
    cut = filter_data(enriched, ("WEGE3",), "2022-01-03", "2022-01-10")
    assert cut["SMA 50"].notna().all()
    changed = full_frame.copy()
    future = changed["Data"].gt("2022-01-10")
    changed.loc[future, "Adj Close"] *= 10
    prior = filter_data(enrich_data(changed), ("WEGE3",), "2022-01-03", "2022-01-10")
    pd.testing.assert_series_equal(cut["SMA 50"], prior["SMA 50"])


def test_missing_price_is_not_filled(known_prices):
    broken = known_prices.drop(index=0)
    with pytest.raises(ValueError, match="datas comuns"):
        analyze(broken)


def test_short_window_has_clear_message(known_prices):
    with pytest.raises(ValueError, match="três pregões"):
        analyze(known_prices.loc[known_prices["Data"].le("2021-01-05")])


def test_export_is_exact_filtered_base(known_prices):
    import io

    filtered = filter_data(known_prices, ("WEGE3",), "2021-01-04", "2021-01-06")
    content = export_csv(filtered[COLUMNS])
    assert content.startswith(b"\xef\xbb\xbf")
    exported = pd.read_csv(io.BytesIO(content))
    assert len(exported) == 3
    assert exported["Ativo"].unique().tolist() == ["WEGE3"]
    assert exported.columns.tolist() == COLUMNS

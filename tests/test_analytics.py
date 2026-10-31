import numpy as np
import pandas as pd
import pytest

from src.analytics import (
    analyze,
    distribution_stats,
    enrich_data,
    export_csv,
    filter_data,
    return_correlations,
)
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


def test_risk_return_ratio_and_daily_sharpe_are_distinct(known_prices):
    _, metrics, _ = analyze(known_prices)
    row = metrics.set_index("Ativo").loc["WEGE3"]
    returns = [0.1, -0.1, 120 / 99 - 1]
    deviation = np.std(returns, ddof=1)
    assert row["Retorno / risco acumulado"] == pytest.approx(0.2 / (deviation * np.sqrt(252)))
    assert row["Sharpe empírico (rf=0)"] == pytest.approx(
        np.mean(returns) / deviation * np.sqrt(252)
    )


def test_empirical_distribution_with_symmetric_known_tails():
    long = pd.DataFrame({"Ativo": ["WEGE3"] * 6, "Retorno Diário %": [np.nan, -4, -2, 0, 2, 4]})
    row = distribution_stats(long).iloc[0]
    assert row["Observações"] == 5
    assert row["Média diária %"] == pytest.approx(0)
    assert row["Desvio diário %"] == pytest.approx(np.sqrt(10))
    assert row["Assimetria"] == pytest.approx(0)
    assert row["Excesso de curtose"] == pytest.approx(-1.2)
    assert row["Percentil 5%"] == pytest.approx(-3.6)
    assert row["Percentil 95%"] == pytest.approx(3.6)
    assert row["Média da cauda 5%"] == pytest.approx(-4)


def test_zero_volatility_ratios_and_correlation_are_undefined(known_prices):
    frame = known_prices.copy()
    frame["Adj Close"] = 100.0
    long, metrics, _ = analyze(frame)
    assert metrics["Retorno / risco acumulado"].isna().all()
    assert metrics["Sharpe empírico (rf=0)"].isna().all()
    assert return_correlations(long).isna().all().all()


def test_short_sample_has_no_kurtosis(known_prices):
    long, _, _ = analyze(known_prices)
    stats = distribution_stats(long)
    assert stats["Observações"].eq(3).all()
    assert stats["Excesso de curtose"].isna().all()

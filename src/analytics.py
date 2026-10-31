"""Indicadores em preços ajustados, sem preenchimento de lacunas."""

import numpy as np
import pandas as pd
import streamlit as st

from src.config import TRADING_DAYS


@st.cache_data(ttl=3600)
def enrich_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Médias móveis usam histórico completo antes do filtro, sem look-ahead."""
    df = frame.sort_values(["Ativo", "Data"]).copy()
    grouped = df.groupby("Ativo")["Adj Close"]
    df["Retorno Diário %"] = grouped.pct_change(fill_method=None) * 100
    df["SMA 21"] = grouped.transform(lambda s: s.rolling(21, min_periods=21).mean())
    df["SMA 50"] = grouped.transform(lambda s: s.rolling(50, min_periods=50).mean())
    return df


@st.cache_data(ttl=3600)
def filter_data(frame: pd.DataFrame, tickers: tuple, start, end) -> pd.DataFrame:
    mask = frame["Ativo"].isin(tickers) & frame["Data"].between(
        pd.Timestamp(start), pd.Timestamp(end)
    )
    return frame.loc[mask].copy()


@st.cache_data(ttl=3600)
def analyze(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    prices = frame.pivot(index="Data", columns="Ativo", values="Adj Close").sort_index()
    if prices.empty or prices.isna().any().any():
        raise ValueError("A comparação exige preços em datas comuns para todos os ativos.")
    if len(prices) < 3:
        raise ValueError("Selecione pelo menos três pregões para estimar a volatilidade.")
    normalized = prices.div(prices.iloc[0]).mul(100)
    # Recalcular após o recorte exclui o retorno que começa fora da janela.
    daily = prices.pct_change(fill_method=None)
    daily_std = daily.std(ddof=1)
    # Séries constantes não têm razão retorno/risco ou Sharpe definidos.
    denominator = daily_std.where(daily_std > np.finfo(float).eps)
    annual_vol = daily_std * np.sqrt(TRADING_DAYS)
    drawdown = (prices.div(prices.cummax()) - 1) * 100
    portfolio = normalized.mean(axis=1)  # Pesos iguais no início, sem rebalanceamento.
    metrics = (
        pd.DataFrame(
            {
                "Retorno Acumulado %": (normalized.iloc[-1] / 100 - 1) * 100,
                "Volatilidade Anualizada %": annual_vol * 100,
                "Retorno / risco acumulado": (normalized.iloc[-1] / 100 - 1)
                / (denominator * np.sqrt(TRADING_DAYS)),
                "Sharpe empírico (rf=0)": daily.mean() / denominator * np.sqrt(TRADING_DAYS),
                "Drawdown Máximo %": drawdown.min(),
                "Volume Financeiro Médio": frame.groupby("Ativo")["Volume Financeiro"].mean(),
                "Setor": frame.groupby("Ativo")["Setor"].first(),
            }
        )
        .rename_axis("Ativo")
        .reset_index()
    )
    long = (
        normalized.rename_axis(columns="Ativo")
        .reset_index()
        .melt(id_vars="Data", var_name="Ativo", value_name="Base 100")
    )
    for wide, name in ((daily * 100, "Retorno Diário %"), (drawdown, "Drawdown %")):
        melted = (
            wide.rename_axis(columns="Ativo")
            .reset_index()
            .melt(id_vars="Data", var_name="Ativo", value_name=name)
        )
        long = long.merge(melted, on=["Data", "Ativo"], validate="one_to_one")
    return long, metrics, portfolio


@st.cache_data(ttl=3600)
def distribution_stats(long: pd.DataFrame) -> pd.DataFrame:
    """Estatísticas amostrais e quantis empíricos, sem assumir normalidade."""
    rows = []
    for ticker, group in long.groupby("Ativo", sort=True):
        returns = group["Retorno Diário %"].dropna()
        q05 = returns.quantile(0.05)
        rows.append(
            {
                "Ativo": ticker,
                "Observações": len(returns),
                "Média diária %": returns.mean(),
                "Desvio diário %": returns.std(ddof=1),
                "Assimetria": returns.skew(),
                "Excesso de curtose": returns.kurt(),
                "Percentil 1%": returns.quantile(0.01),
                "Percentil 5%": q05,
                "Mediana %": returns.median(),
                "Percentil 95%": returns.quantile(0.95),
                "Percentil 99%": returns.quantile(0.99),
                "Média da cauda 5%": returns.loc[returns.le(q05)].mean(),
                "Pior dia %": returns.min(),
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def return_correlations(long: pd.DataFrame) -> pd.DataFrame:
    """Correlação de Pearson dos retornos diários nas datas do recorte."""
    daily = long.pivot(index="Data", columns="Ativo", values="Retorno Diário %")
    return daily.corr(min_periods=3)


@st.cache_data(ttl=3600)
def export_csv(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False, date_format="%Y-%m-%d").encode("utf-8-sig")

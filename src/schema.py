"""Validação estrita: nunca preencher preços ou inventar pregões."""

import numpy as np
import pandas as pd
import streamlit as st

from src.config import COLUMNS, END, NUMERIC_COLUMNS, PRICE_COLUMNS, SECTORS, START, TICKERS


class DataQualityError(ValueError):
    """A base não atende ao contrato do projeto."""


@st.cache_data(ttl=3600)
def validate_data(frame: pd.DataFrame, require_full: bool = True) -> pd.DataFrame:
    missing = set(COLUMNS) - set(frame.columns)
    if missing:
        raise DataQualityError(f"Colunas ausentes: {', '.join(sorted(missing))}")
    if frame.empty:
        raise DataQualityError("A base está vazia.")
    df = frame.loc[:, COLUMNS].copy()
    df["Data"] = pd.to_datetime(df["Data"], errors="raise")
    if df["Data"].dt.tz is not None:
        df["Data"] = df["Data"].dt.tz_localize(None)
    if df["Data"].isna().any() or not df["Data"].eq(df["Data"].dt.normalize()).all():
        raise DataQualityError("Datas inválidas ou com horário intradiário.")
    if not df["Data"].between(pd.Timestamp(START), pd.Timestamp(END)).all():
        raise DataQualityError("Datas fora do período obrigatório de 2021 a 2023.")
    if not df["Ativo"].isin(TICKERS).all():
        raise DataQualityError("Ativo desconhecido no universo do projeto.")
    if not df["Setor"].eq(df["Ativo"].map(SECTORS)).all():
        raise DataQualityError("Setor incompatível com o dicionário do projeto.")
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="raise")
    if not np.isfinite(df[NUMERIC_COLUMNS].to_numpy(dtype=float)).all():
        raise DataQualityError("Valores nulos ou infinitos na base.")
    if (df[PRICE_COLUMNS] <= 0).any().any():
        raise DataQualityError("Preços devem ser positivos.")
    if (df[["Volume", "Volume Financeiro"]] < 0).any().any():
        raise DataQualityError("Volume negativo.")
    if not df["Volume"].eq(np.floor(df["Volume"])).all():
        raise DataQualityError("Volume em unidades deve ser inteiro.")
    valid_ohlc = (df["High"] >= df[["Open", "Close", "Low"]].max(axis=1)) & (
        df["Low"] <= df[["Open", "Close", "High"]].min(axis=1)
    )
    if not valid_ohlc.all():
        raise DataQualityError("Relação OHLC inconsistente.")
    if not np.allclose(df["Volume Financeiro"], df["Close"] * df["Volume"], rtol=1e-7):
        raise DataQualityError("Volume Financeiro difere da estimativa Close × Volume.")
    if df.duplicated(["Ativo", "Data"]).any():
        raise DataQualityError("Chaves Ativo/Data duplicadas.")
    df["Volume"] = df["Volume"].astype("int64")
    df = df.sort_values(["Data", "Ativo"]).reset_index(drop=True)
    if require_full:
        if set(df["Ativo"]) != set(TICKERS):
            raise DataQualityError("São necessários os 12 ativos.")
        for ticker, group in df.groupby("Ativo"):
            for year in (2021, 2022, 2023):
                dates = group.loc[group["Data"].dt.year.eq(year), "Data"]
                if (
                    len(dates) < 230
                    or dates.min() > pd.Timestamp(year, 1, 10)
                    or dates.max() < pd.Timestamp(year, 12, 20)
                ):
                    raise DataQualityError(f"Cobertura anual insuficiente: {ticker}, {year}.")
        # Gaps de um ativo não podem ser mascarados com forward fill.
        counts = df.groupby("Data")["Ativo"].nunique()
        if not counts.eq(len(TICKERS)).all():
            raise DataQualityError("Calendários divergentes entre os 12 ativos.")
    return df

"""Dados sintéticos exclusivos dos testes; nunca publicados em data/."""

import numpy as np
import pandas as pd
import pytest

from src.config import COLUMNS, SECTORS, TICKERS


@pytest.fixture
def full_frame():
    dates = pd.bdate_range("2021-01-01", "2023-12-31")
    frames = []
    for i, ticker in enumerate(TICKERS):
        prices = 20 + i + np.arange(len(dates)) * (i + 1) / 1000
        frame = pd.DataFrame(
            {
                "Data": dates,
                "Ativo": ticker,
                "Setor": SECTORS[ticker],
                "Open": prices,
                "High": prices + 1,
                "Low": prices - 1,
                "Close": prices,
                "Adj Close": prices,
                "Volume": 1000,
                "Volume Financeiro": prices * 1000,
            }
        )
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)[COLUMNS]


@pytest.fixture
def known_prices():
    frames = []
    for ticker, prices in {"WEGE3": [100, 110, 99, 120], "VALE3": [100, 90, 81, 80]}.items():
        p = np.array(prices, dtype=float)
        frames.append(
            pd.DataFrame(
                {
                    "Data": pd.bdate_range("2021-01-04", periods=4),
                    "Ativo": ticker,
                    "Setor": SECTORS[ticker],
                    "Open": p,
                    "High": p + 1,
                    "Low": p - 1,
                    "Close": p,
                    "Adj Close": p,
                    "Volume": 1000,
                    "Volume Financeiro": p * 1000,
                }
            )
        )
    return pd.concat(frames, ignore_index=True)

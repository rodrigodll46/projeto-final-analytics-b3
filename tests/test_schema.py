import numpy as np
import pandas as pd
import pytest

from src.schema import DataQualityError, validate_data


def test_full_universe_is_sorted_and_typed(full_frame):
    result = validate_data(full_frame.sample(frac=1, random_state=7))
    assert result["Data"].is_monotonic_increasing
    assert result["Ativo"].nunique() == 12
    assert result["Volume"].dtype == "int64"


@pytest.mark.parametrize(
    "column,value",
    [
        ("Adj Close", np.nan),
        ("Open", 0),
        ("High", -1),
        ("Volume", -1),
        ("Volume", 1.5),
        ("Setor", "Incorreto"),
        ("Ativo", "INVALIDO"),
        ("Volume Financeiro", 1),
        ("Data", pd.Timestamp("2024-01-02")),
    ],
)
def test_invalid_values_are_rejected(full_frame, column, value):
    broken = full_frame.copy()
    if column == "Volume":
        broken[column] = broken[column].astype(float)
    broken.loc[0, column] = value
    with pytest.raises((DataQualityError, ValueError)):
        validate_data(broken)


def test_duplicates_rejected(full_frame):
    with pytest.raises(DataQualityError, match="duplicadas"):
        validate_data(pd.concat([full_frame, full_frame.iloc[:1]]))


def test_missing_ticker_rejected(full_frame):
    with pytest.raises(DataQualityError, match="12 ativos"):
        validate_data(full_frame.loc[full_frame["Ativo"].ne("VALE3")])


def test_missing_year_rejected(full_frame):
    with pytest.raises(DataQualityError, match="Cobertura anual"):
        validate_data(full_frame.loc[full_frame["Data"].dt.year.ne(2022)])


def test_single_session_gap_rejected(full_frame):
    with pytest.raises(DataQualityError, match="Calendários divergentes"):
        validate_data(full_frame.iloc[1:])

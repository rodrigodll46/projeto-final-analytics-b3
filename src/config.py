"""Contrato único do universo, período, nomes de colunas e caminhos relativos."""

from datetime import date
from pathlib import Path

START = date(2021, 1, 1)
END = date(2023, 12, 31)
DOWNLOAD_END = "2024-01-01"  # O parâmetro end do Yahoo é exclusivo.
TRADING_DAYS = 252
AUTHOR = "Rodrigo Correa"
DATA_PATH = Path("data") / "b3_2021_2023.csv"
MANIFEST_PATH = Path("data") / "manifest.json"

# Agrupamentos didáticos, não a classificação setorial oficial da B3.
SECTORS = {
    "WEGE3": "Indústria e materiais",
    "EMBR3": "Indústria e materiais",
    "VALE3": "Indústria e materiais",
    "GGBR4": "Indústria e materiais",
    "KLBN11": "Indústria e materiais",
    "PETR4": "Energia",
    "PRIO3": "Energia",
    "EGIE3": "Energia",
    "ITUB4": "Financeiro",
    "BBDC4": "Financeiro",
    "ABEV3": "Consumo e serviços",
    "RENT3": "Consumo e serviços",
}
TICKERS = tuple(SECTORS)
# O ticker histórico continua no contrato; o Yahoo migrou a série da Embraer.
# Correspondência documentada no README, sem substituir o ativo do enunciado.
SOURCE_ALIASES = {"EMBR3": "EMBJ3.SA"}
PRICE_COLUMNS = ["Open", "High", "Low", "Close", "Adj Close"]
NUMERIC_COLUMNS = [*PRICE_COLUMNS, "Volume", "Volume Financeiro"]
COLUMNS = ["Data", "Ativo", "Setor", *NUMERIC_COLUMNS]
DB_COLUMNS = {
    "Data": "data",
    "Ativo": "ativo",
    "Setor": "setor",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume",
    "Volume Financeiro": "volume_financeiro",
}

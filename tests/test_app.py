from datetime import date

from streamlit.testing.v1 import AppTest

from src import database
from src.config import END, START, TICKERS


def app_with_data(monkeypatch, full_frame):
    monkeypatch.setattr(
        database, "load_data", lambda **_: database.LoadResult(full_frame, "CSV local", "Test")
    )
    return AppTest.from_file("../app.py", default_timeout=30).run()


def test_app_metrics_charts_filters_and_reset(monkeypatch, full_frame):
    app = app_with_data(monkeypatch, full_frame)
    assert not app.exception
    assert len(app.metric) == 4
    assert len(app.get("plotly_chart")) == 5
    app.sidebar.button[0].click().run()
    assert not app.exception
    assert len(app.metric) == 4
    app.multiselect(key="sectors").set_value(["Financeiro"]).run()
    assert not app.exception
    assert set(app.multiselect(key="tickers").value) == {"ITUB4", "BBDC4"}
    app.date_input(key="dates").set_value((date(2022, 1, 3), date(2022, 3, 31))).run()
    assert not app.exception
    assert len(app.metric) == 4
    app.sidebar.button[1].click().run()
    assert not app.exception
    assert set(app.multiselect(key="tickers").value) == set(TICKERS)
    assert tuple(app.date_input(key="dates").value) == (START, END)


def test_app_empty_selection_and_short_window(monkeypatch, full_frame):
    app = app_with_data(monkeypatch, full_frame)
    app.multiselect(key="tickers").set_value([]).run()
    assert not app.exception
    assert "pelo menos um" in app.info[0].value
    app.sidebar.button[1].click().run()
    app.date_input(key="dates").set_value((date(2021, 1, 4), date(2021, 1, 5))).run()
    assert not app.exception
    assert "três pregões" in app.info[0].value


def test_app_unavailable_sources(monkeypatch):
    def unavailable(**kwargs):
        raise database.DataUnavailableError("Execute python -m src.etl.")

    monkeypatch.setattr(database, "load_data", unavailable)
    app = AppTest.from_file("../app.py").run()
    assert not app.exception
    assert "python -m src.etl" in app.error[0].value

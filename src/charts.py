"""Visualizações analíticas construídas exclusivamente com Plotly Express."""

import pandas as pd
import plotly.express as px

COLORS = px.colors.qualitative.Safe


def style(fig, y_title: str, height: int = 420):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=12, r=20, t=35, b=12),
        legend_title_text="",
        yaxis_title=y_title,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(160,180,200,0.12)")
    return fig


def base100(long: pd.DataFrame):
    fig = px.line(long, x="Data", y="Base 100", color="Ativo", color_discrete_sequence=COLORS)
    fig.add_hline(y=100, line_dash="dash", line_color="#8895A7", annotation_text="Base inicial")
    fig.update_layout(hovermode="x unified")
    return style(fig, "Patrimônio normalizado · base 100")


def risk_return(metrics: pd.DataFrame):
    fig = px.scatter(
        metrics,
        x="Volatilidade Anualizada %",
        y="Retorno Acumulado %",
        size="Volume Financeiro Médio",
        color="Setor",
        text="Ativo",
        hover_name="Ativo",
        size_max=55,
        color_discrete_sequence=COLORS,
        hover_data={"Volume Financeiro Médio": ":,.0f"},
    )
    fig.update_traces(textposition="top center")
    fig.add_hline(y=0, line_dash="dot", line_color="#8895A7")
    fig.update_xaxes(title="Volatilidade anualizada (% a.a.)")
    return style(fig, "Retorno acumulado (%)")


def histogram(long: pd.DataFrame):
    fig = px.histogram(
        long.dropna(subset=["Retorno Diário %"]),
        x="Retorno Diário %",
        color="Ativo",
        nbins=55,
        histnorm="percent",
        marginal="box",
        barmode="overlay",
        opacity=0.5,
        color_discrete_sequence=COLORS,
    )
    fig.update_xaxes(title="Retorno diário (%)")
    return style(fig, "Frequência relativa (%)")


def drawdown(long: pd.DataFrame):
    # Facetas impedem que drawdowns de ativos diferentes sejam empilhados.
    count = long["Ativo"].nunique()
    fig = px.area(
        long,
        x="Data",
        y="Drawdown %",
        color="Ativo",
        facet_col="Ativo",
        facet_col_wrap=3,
        color_discrete_sequence=COLORS,
    )
    fig.update_layout(showlegend=False)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return style(fig, "Drawdown (%)", height=max(320, 230 * ((count + 2) // 3)))


def moving_averages(frame: pd.DataFrame, ticker: str):
    lines = frame.loc[frame["Ativo"].eq(ticker)].melt(
        id_vars="Data",
        value_vars=["Adj Close", "SMA 21", "SMA 50"],
        var_name="Série",
        value_name="Preço (R$)",
    )
    fig = px.line(
        lines,
        x="Data",
        y="Preço (R$)",
        color="Série",
        color_discrete_map={"Adj Close": "#45D6B0", "SMA 21": "#F5BC62", "SMA 50": "#9E9BFF"},
    )
    fig.update_layout(hovermode="x unified")
    return style(fig, "Preço ajustado (R$)")


def correlations(matrix: pd.DataFrame):
    fig = px.imshow(
        matrix,
        zmin=-1,
        zmax=1,
        color_continuous_scale="RdBu_r",
        text_auto=".2f",
        labels={"color": "Correlação"},
        aspect="auto",
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Pearson"))
    return style(fig, "Ativo", height=max(380, 40 * len(matrix)))

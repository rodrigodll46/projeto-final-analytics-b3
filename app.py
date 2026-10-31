"""Dashboard B3 | execute a partir da raiz: streamlit run app.py."""

import numpy as np
import streamlit as st

from src import charts
from src.analytics import (
    analyze,
    distribution_stats,
    enrich_data,
    export_csv,
    filter_data,
    return_correlations,
)
from src.config import AUTHOR, COLUMNS, DATA_PATH, END, SECTORS, START, TICKERS, TRADING_DAYS
from src.database import DataUnavailableError, load_data

st.set_page_config(page_title="B3 | Observatório de mercado", page_icon="📈", layout="wide")


def reset_filters() -> None:
    st.session_state.update(
        sectors=sorted(set(SECTORS.values())), tickers=list(TICKERS), dates=(START, END)
    )
    st.session_state.pop("ma_ticker", None)


def refresh_data() -> None:
    st.cache_data.clear()
    # Uma conexão quebrada será reconstruída na próxima tentativa.
    try:
        st.connection("postgresql", type="sql").reset()
    except Exception:
        pass


st.caption("ANALYTICS FINANCEIRO  /  LINHA 2")
st.title("Observatório de mercado B3")
st.markdown(
    "**12 ativos · 4 grupos setoriais · 2021–2023**  |  Explore retorno, risco e tendência."
)
st.caption(f"Projeto avaliativo de {AUTHOR}")

with st.sidebar:
    st.header("Seu recorte de mercado")
    st.button("Recarregar fontes", on_click=refresh_data, width="stretch")

try:
    revision = DATA_PATH.stat().st_mtime_ns if DATA_PATH.exists() else 0
    loaded = load_data(revision=revision)
except DataUnavailableError as exc:
    st.error(str(exc))
    st.code("python -m pip install -r requirements.txt\npython -m src.etl\nstreamlit run app.py")
    st.stop()

frame = enrich_data(loaded.frame)
if "sectors" not in st.session_state:
    reset_filters()

with st.sidebar:
    st.multiselect("Setores", sorted(set(SECTORS.values())), key="sectors")
    available = [t for t in TICKERS if SECTORS[t] in st.session_state.sectors]
    st.session_state.tickers = [t for t in st.session_state.tickers if t in available]
    st.multiselect("Ativos", available, key="tickers")
    st.date_input(
        "Intervalo de datas", min_value=START, max_value=END, key="dates", format="DD/MM/YYYY"
    )
    st.button("Restaurar filtros", on_click=reset_filters, width="stretch")
    st.divider()
    st.caption(f"Fonte ativa: {loaded.source}")
    if loaded.fallback_reason:
        st.caption("Contingência CSV ativa. As credenciais do banco são opcionais.")
    st.caption("Setores são agrupamentos didáticos. KLBN11 é uma unit.")

if not st.session_state.tickers:
    st.info("Selecione pelo menos um setor e um ativo na barra lateral.")
    st.stop()
dates = st.session_state.dates
if len(dates) != 2:
    st.info("Complete as duas datas do intervalo.")
    st.stop()
start, end = dates
filtered = filter_data(frame, tuple(st.session_state.tickers), start, end)
if filtered.empty:
    st.info("Não há pregões no intervalo escolhido.")
    st.stop()
try:
    long, metrics, portfolio = analyze(filtered)
except ValueError as exc:
    st.info(str(exc))
    st.stop()

actual_start = filtered["Data"].min().strftime("%d/%m/%Y")
actual_end = filtered["Data"].max().strftime("%d/%m/%Y")
st.caption(
    f"{actual_start} → {actual_end}  ·  {filtered['Data'].nunique()} pregões  ·  "
    f"{len(metrics)} ativos selecionados  ·  Fonte: {loaded.source}"
)
total_return = float(portfolio.iloc[-1] - 100)
last_return = float(portfolio.pct_change(fill_method=None).iloc[-1] * 100)
best = metrics.loc[metrics["Retorno Acumulado %"].idxmax()]
worst = metrics.loc[metrics["Retorno Acumulado %"].idxmin()]
volatility = float(metrics["Volatilidade Anualizada %"].mean())
portfolio_vol = float(
    portfolio.pct_change(fill_method=None).std(ddof=1) * np.sqrt(TRADING_DAYS) * 100
)

c1, c2 = st.columns(2)
c3, c4 = st.columns(2)
c1.metric("Retorno médio da carteira", f"{total_return:.2f}%", f"{last_return:+.2f}% último pregão")
c2.metric(
    f"Melhor performance · {best['Ativo']}",
    f"{best['Retorno Acumulado %']:.2f}%",
    f"{best['Retorno Acumulado %'] - total_return:+.2f} p.p. vs. carteira",
)
c3.metric(
    f"Menor performance · {worst['Ativo']}",
    f"{worst['Retorno Acumulado %']:.2f}%",
    f"{worst['Retorno Acumulado %'] - total_return:+.2f} p.p. vs. carteira",
)
c4.metric(
    "Volatilidade média · % a.a.",
    f"{volatility:.2f}%",
    f"{volatility - portfolio_vol:+.2f} p.p. vs. risco da carteira",
    delta_color="inverse",
)
st.caption("Carteira com pesos iguais no início do recorte, mantida sem rebalanceamento.")

resilient = metrics.loc[metrics["Drawdown Máximo %"].idxmax()]
worst_drop = metrics.loc[metrics["Drawdown Máximo %"].idxmin()]
st.markdown(
    f"**Leitura executiva do recorte.** {best['Ativo']} liderou o retorno "
    f"({best['Retorno Acumulado %']:.2f}%). {resilient['Ativo']} teve a menor queda "
    f"máxima ({resilient['Drawdown Máximo %']:.2f}%), enquanto {worst_drop['Ativo']} "
    f"atingiu {worst_drop['Drawdown Máximo %']:.2f}%. "
    "**Aplicação prática:** compare retorno, risco e perdas suportáveis antes de definir "
    "limites de exposição; resultados históricos não determinam desempenho futuro."
)

overview, risk, trends, findings, data, method = st.tabs(
    [
        "Performance",
        "Risco e distribuição",
        "Tendências",
        "Conclusões",
        "Base de dados",
        "Metodologia",
    ]
)
with overview:
    st.subheader("Quanto valeria uma base inicial de 100?")
    st.plotly_chart(charts.base100(long), width="stretch")
    st.subheader("Retorno e risco, lado a lado")
    st.caption("O tamanho das bolhas representa o volume financeiro médio estimado no recorte.")
    st.plotly_chart(charts.risk_return(metrics), width="stretch")
with risk:
    st.subheader("Como os retornos diários se distribuem?")
    st.plotly_chart(charts.histogram(long), width="stretch")
    st.caption("Frequência percentual por ativo. O boxplot evidencia dispersão e valores extremos.")
    st.subheader("Distância até o topo no período selecionado")
    st.plotly_chart(charts.drawdown(long), width="stretch")
    st.subheader("Correlação dos retornos diários")
    st.plotly_chart(charts.correlations(return_correlations(long)), width="stretch")
    st.caption(
        "Pearson no recorte. Correlação não implica causalidade e pode mudar entre períodos. "
        "Séries constantes ou com menos de três retornos não têm correlação estimável."
    )
with trends:
    st.subheader("Preço ajustado e médias móveis")
    choices = sorted(filtered["Ativo"].unique())
    if st.session_state.get("ma_ticker") not in choices:
        st.session_state.ma_ticker = choices[0]
    ma_ticker = st.selectbox("Ativo para análise de tendência", choices, key="ma_ticker")
    st.plotly_chart(charts.moving_averages(filtered, ma_ticker), width="stretch")
    st.caption(
        "SMA 21 e SMA 50 usam pregões anteriores ao recorte, dentro de 2021–2023. "
        "No início de 2021, aparecem após 21 e 50 observações disponíveis."
    )
    latest = filtered.loc[filtered["Ativo"].eq(ma_ticker)].sort_values("Data").iloc[-1]
    if latest[["SMA 21", "SMA 50"]].notna().all():
        position21 = "acima" if latest["Adj Close"] >= latest["SMA 21"] else "abaixo"
        position50 = "acima" if latest["Adj Close"] >= latest["SMA 50"] else "abaixo"
        st.info(
            f"No último pregão, {ma_ticker} fechou {position21} da SMA 21 e "
            f"{position50} da SMA 50. É uma descrição da tendência observada; "
            "não constitui sinal validado de compra ou venda."
        )
with findings:
    st.subheader("Respostas às perguntas de negócio")
    st.markdown(
        rf"**1 · Capital inicial e retorno.** Uma base de R\$ 100 em {best['Ativo']} "
        rf"terminaria em R\$ {100 + best['Retorno Acumulado %']:.2f} no recorte, "
        "considerando o preço ajustado e sem custos ou impostos. "
        "A aba Performance permite comparar todos os ativos na mesma base."
    )
    ranking = metrics.dropna(subset=["Retorno / risco acumulado"])
    if not ranking.empty:
        leader = ranking.loc[ranking["Retorno / risco acumulado"].idxmax()]
        sharpe = ranking.loc[ranking["Sharpe empírico (rf=0)"].idxmax()]
        st.markdown(
            f"**2 · Retorno e risco.** {leader['Ativo']} liderou a razão retorno acumulado / "
            f"volatilidade anualizada ({leader['Retorno / risco acumulado']:.2f}). "
            f"{sharpe['Ativo']} liderou o Sharpe empírico com taxa livre de risco zero "
            f"({sharpe['Sharpe empírico (rf=0)']:.2f}). "
            "São medidas distintas: a primeira reproduz a comparação solicitada no "
            "enunciado; o Sharpe usa a média dos retornos diários. Ambos são retrospectivos."
        )
    else:
        st.info("Retorno/risco e Sharpe indisponíveis: volatilidade diária nula.")
    st.dataframe(
        metrics.sort_values("Retorno / risco acumulado", ascending=False).round(3),
        hide_index=True,
        width="stretch",
    )
    st.markdown(
        "**3 · Distribuição e caudas.** Assimetria negativa indica uma cauda mais longa "
        "à esquerda; excesso de curtose positivo indica caudas mais pesadas que a normal. "
        "O percentil 5% e a média dos retornos abaixo dele descrevem a cauda observada; "
        "não são previsões ou garantias de perda máxima."
    )
    st.dataframe(distribution_stats(long).round(3), hide_index=True, width="stretch")
    st.caption(
        "Retornos, desvios e quantis em %. Assimetria e curtose são adimensionais; "
        "curtose de Fisher (normal = 0). Assimetria exige 3 retornos e curtose 4; "
        "amostras menores aparecem sem estimativa."
    )
    st.markdown(
        f"**4 · Resiliência.** {resilient['Ativo']} teve o drawdown menos severo "
        f"({resilient['Drawdown Máximo %']:.2f}%). {worst_drop['Ativo']} enfrentou "
        f"o mais severo ({worst_drop['Drawdown Máximo %']:.2f}%). "
        "O pico é o maior preço observado desde o início da janela, não o topo de toda "
        "a história anterior a 2021.\n\n"
        "**5 · Médias móveis.** A aba Tendências compara o fechamento ajustado com "
        "SMA 21 e SMA 50 e informa a posição no último pregão do ativo escolhido.\n\n"
        "**Decisão apoiada.** Um gestor pode comparar perfis, dimensionar limites de "
        "exposição e investigar concentrações com a matriz de correlação. A análise "
        "não comprova causas macroeconômicas ou setoriais, nem substitui critérios de "
        "liquidez, adequação, custos e horizonte de investimento."
    )
with data:
    st.subheader("Dados do seu recorte")
    st.download_button(
        "Exportar base filtrada · CSV",
        export_csv(filtered[COLUMNS]),
        file_name=f"b3_{start}_{end}.csv",
        mime="text/csv",
        width="stretch",
    )
    st.dataframe(filtered[COLUMNS], hide_index=True, width="stretch")
    st.subheader("Indicadores por ativo")
    st.dataframe(metrics.round(2), hide_index=True, width="stretch")
with method:
    st.markdown(r"""
**Preços e período.** Dados diários do Yahoo Finance via `yfinance`, de 01/01/2021
a 31/12/2023. Finais de semana e feriados não são preenchidos. Os retornos usam
`Adj Close`, ajustado pelo provedor para eventos corporativos. OHLC e `Close`
são preservados como retornados com `auto_adjust=False`.

**Retorno acumulado:** $(P_f/P_i - 1)\times100$. **Base 100:** $100P_t/P_i$.
**Volatilidade:** desvio padrão amostral dos retornos simples diários, multiplicado
por $\sqrt{252}\times100$. O primeiro retorno de cada recorte é excluído.

**Retorno/risco acumulado:** retorno acumulado dividido pela volatilidade anualizada,
ambos na mesma unidade. **Sharpe empírico (rf=0):** média dos retornos diários
dividida pelo desvio padrão amostral diário, multiplicada por $\sqrt{252}$.
A taxa livre de risco é explicitamente zero; não é um Sharpe excedente ao CDI/Selic.
Séries com volatilidade nula não recebem essas razões.

**Distribuição:** assimetria amostral, excesso de curtose de Fisher, quantis
empíricos com interpolação linear e média dos retornos menores ou iguais ao
percentil 5%. Correlação de Pearson calculada sobre retornos diários do recorte.

**Carteira:** média das séries normalizadas, com pesos iniciais iguais e sem
rebalanceamento. Seu retorno equivale à média dos retornos acumulados dos ativos.
A volatilidade média dos ativos é diferente da volatilidade dessa carteira.

**Drawdown:** $(P_t/\max_{s\leq t}P_s-1)\times100$, reiniciado no início do recorte.
O topo é o observado na janela selecionada. **SMA:** média aritmética dos últimos
21 ou 50 pregões, incluindo o atual e usando histórico anterior ao filtro.

**Volume Financeiro:** estimativa `Close × Volume`, expressa em reais; não é o giro
oficial da B3. Revisões históricas e ajustes do Yahoo podem afetar a estimativa.
As bolhas usam sua média diária; o histograma usa frequência percentual por ativo.

**Embraer:** o projeto preserva o código histórico `EMBR3`. Se `EMBR3.SA` estiver
indisponível no Yahoo, o ETL consulta a série migrada para `EMBJ3.SA`. O código
efetivamente utilizado fica registrado em `data/manifest.json`.

**Deltas dos cartões:** retorno da carteira no último pregão; diferença da melhor
e da menor performance em relação à carteira; diferença entre a volatilidade
média dos ativos e a volatilidade da carteira, em pontos percentuais.

**Limites:** o universo foi fixado pelo enunciado e pode conter viés de seleção.
Não há taxas, impostos ou avaliação de adequação de investimento. Os quatro
grupos são didáticos, não a classificação setorial oficial da B3.
""")

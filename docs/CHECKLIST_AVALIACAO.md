# Conferência do enunciado recebido

Autor: Rodrigo Correa. Esta conferência usa os requisitos textuais da conversa;
o PDF original associado aos marcadores cite não foi fornecido.

| Requisito | Evidência |
| --- | --- |
| Linha 2, 2021 a 2023, dados diários | data/manifest.json e cobertura de 745 pregões por ativo |
| Os 12 códigos definidos | src/config.py e CSV com 8.940 registros |
| Data, OHLC, Adj Close, Volume Financeiro | Contrato e dicionário no README |
| API pública yfinance com .SA | src/etl.py, end exclusivo 2024-01-01 |
| Caminhos relativos | Leituras Path("data") e execução da raiz |
| Credenciais via st.secrets | SQLConnection e exemplos sem senha real |
| Secrets fora do Git | .gitignore e conferência antes da publicação |
| PostgreSQL prioritário e fallback CSV | src/database.py e testes de falha |
| Cache TTL de uma hora | Decoradores nas leituras e transformações pesadas |
| Filtros por ativos, datas e setores | Sidebar reativa em app.py |
| Session state e reset | Callback Restaurar filtros, coberto por AppTest |
| Abas e exportação | Cinco abas e download da base filtrada |
| Quatro KPIs com deltas | Retorno, melhor, menor e volatilidade média |
| Cinco gráficos Plotly Express | Base 100, dispersão, histograma, drawdown e SMA |
| Arquitetura modular | src/etl, schema, database, analytics e charts |
| EDA | Notebook executado com snapshot real |
| Git e qualidade | Commits com autoria e workflow de testes |
| Banco real | Supabase com 8.940 registros conferidos e leitor restrito |
| Publicação | https://rodrigo-correa-analytics-b3.streamlit.app/ com acesso público validado |

## Pontos que exigem interpretação da rubrica

**Setores.** Os 12 ativos listados representam mais de quatro setores oficiais.
O projeto preserva todos os códigos e os reúne em quatro grupos didáticos.
O avaliador precisa aceitar esse agrupamento ou fornecer o mapeamento esperado.

**Volume Financeiro.** O Yahoo fornece quantidade e preços, não a soma oficial
do valor de cada negócio. O projeto estima Close × Volume e identifica essa escolha.
Se a rubrica exigir giro oficial, será necessária uma fonte oficial da B3.

**Embraer.** O projeto mantém EMBR3 como código histórico. A aquisição inicial usa
EMBJ3.SA, para onde o Yahoo migrou a série. O manifesto registra a correspondência.

**Médias móveis.** No início de 2021, SMA 21 e 50 só aparecem quando há observações
suficientes. O projeto preserva o período obrigatório sem fabricar histórico.

Essas escolhas estão documentadas; a conferência não representa uma garantia de nota.

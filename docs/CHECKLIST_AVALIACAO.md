# Auditoria do PDF oficial

Autor: **Rodrigo Correa**. Revisão de **31/10/2026**.
Fonte: `Projeto final  instrucoes.pdf`, 15 páginas, recebido do estudante.
SHA-256: `e341b0b53df219801c155d065c89e33550e3d8fe3423c1c97d0dda052bfb798a`.
Foram lidas as páginas e inspecionadas visualmente as tabelas de avaliação das páginas 14 e 15, que não aparecem na extração textual.

## Comparação e correções

| Exigência do PDF | Situação anterior | Resultado / evidência |
| --- | --- | --- |
| Linha 2, diário de 2021 a 2023, 12 ativos | Atendido | 8.940 registros, 745 pregões por ativo, manifesto com hash |
| Preço ajustado e volume financeiro | Definição explícita | Estimativa Close × Volume, identificada como aproximação |
| Base 100 com referência 100 | Atendido | Performance e src/charts.py |
| Melhor relação de retorno/risco | Apenas dispersão | Ranking, razão acumulada e Sharpe diário anualizado com rf=0 |
| Dispersão, assimetria e caudas | Histograma sem síntese numérica completa | Desvio, assimetria, curtose de Fisher, quantis e média da cauda 5% |
| Drawdown por ativo e mais resiliente | Sem conclusão explícita | EGIE3 menos severo e EMBR3 mais severo no snapshot |
| Fechamento versus SMA 21 e 50 | Gráfico atendido | Posição no último pregão também descrita |
| Pelo menos 5 gráficos Plotly Express | Cinco | Seis, com correlação de retornos |
| Quatro KPIs com deltas e colunas | Atendido | Retorno, melhor, menor e volatilidade |
| Contexto, insight e ação | Conclusões dispersas | Leitura executiva e aba Conclusões com cinco respostas de negócio |
| ETL reproduzível, nulos, chaves, tipos e datas | Atendido | src/etl.py, src/schema.py e testes |
| Dicionário e modelagem | Dicionário presente | Grão, chave e dimensões lógicas explicitados |
| Caminhos relativos | Atendido | Path relativo e notebook sem caminho pessoal |
| PostgreSQL, fallback, cache TTL e secrets | Atendido | Supabase real, st.connection, try/except e cache 3600 |
| Filtros, estado, reset, abas e download | Atendido | Seis abas; filtros e reset por AppTest; exportação real conferida |
| Cloud ativo e requirements | Atendido | App público, PostgreSQL e Python 3.12 |
| README: 14 tópicos do item 5.2 | Tópicos incompletos | Contexto, licença, tecnologias, resultados, ações, navegação, LinkedIn e Trello incluídos |
| Kanban individual público e print | Ausente | Quadro de rodrigocorrea15, quatro listas, sete cartões com responsável e especificações |
| Uma tarefa por vez Em andamento | Sem evidência anterior | Regra aplicada às correções atuais, com movimentos reais |
| main estável, develop, features e PRs | Só codex/analytics-b3 | Fluxo aplicado às correções, sem reescrever histórico ou apagar branches |
| Pitch público de 3 a 5 minutos | Não realizado | **Excluído por decisão expressa do autor; critério não atendido** |
| Envio no AVA | Sem comprovante | **Pendente de submissão e confirmação real** |

## Pesos da avaliação

| Critério | Peso máximo | Evidência / limite |
| --- | ---: | --- |
| 1. Vídeo | 1,00 | Não será entregue por decisão do autor |
| 2–4. Trello: especificações, movimentação e WIP | 1,50 | Quadro e movimentos desta revisão; sem reconstruir atividade passada |
| 5. Branches e commits | 0,75 | Features, develop, PRs e main na revisão; histórico inicial preservado |
| 6. README completo | 0,75 | Estrutura expandida; link do vídeo ausente por decisão do autor |
| 7. Pipeline e ETL Python/SQL | 1,50 | Código, snapshot, contrato, banco e testes |
| 8. EDA, estatística e Plotly | 1,50 | Notebook executado, seis gráficos e estatística descritiva |
| 9. Arquitetura, interatividade e Cloud | 1,50 | App público, Supabase, cache, estado e contingência |
| 10. KPIs, storytelling e conclusões | 1,50 | Quatro KPIs, respostas de negócio e limites |
| Total | 10,00 | O vídeo ausente impede atender todos os critérios |

A avaliação é do professor. Mesmo sem o vídeo, não se garante nota 9,0: o avaliador pode considerar o histórico incompleto de planejamento/branches e o link de vídeo exigido no README. Criar o quadro e as branches agora não comprova uso dessas práticas desde o início. Nenhuma data foi retroagida.

## Links e evidências

- [GitHub](https://github.com/rodrigodll46/projeto-final-analytics-b3).
- [Dashboard](https://rodrigo-correa-analytics-b3.streamlit.app/).
- [Trello individual](https://trello.com/b/4qqJDupe/rodrigo-correa-projeto-final-analytics-b3).
- [LinkedIn de Rodrigo](https://www.linkedin.com/in/rodrigo-correa-a5009b247/).
- Vídeo: não produzido; nenhuma URL inventada.

![Kanban público com listas, cartões e responsáveis](trello-kanban.png)

## Entrega e preservação

O PDF exige envio no AVA das Semanas 13 e 14 até **03/11/2026 às 22h**, com GitHub, app e vídeo; o Trello deve constar no README. Esta entrega será sem vídeo por decisão do autor. Disponibilizar os arquivos não equivale a submeter a atividade. Após o envio, preservar o repositório até a nota: o PDF usa a última atualização do GitHub como data final e veda alterações posteriores à entrega.

## Limites técnicos

Os quatro grupos são didáticos; KLBN11 é uma unit. EMBR3 permanece no contrato e tem alias EMBJ3.SA no manifesto. O volume financeiro é estimado, o topo do drawdown inicia no recorte e as SMA aguardam suas janelas. Yahoo/yfinance têm termos próprios, sem licença geral sobre dados concedida por este repositório. Não há alegações de causalidade ou previsão.

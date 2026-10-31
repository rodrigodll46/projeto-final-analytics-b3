# Evidências de validação

Verificação local realizada em **30/10/2026**, na raiz do projeto.

## Resultado

| Verificação | Resultado observado |
| --- | --- |
| Aquisição Yahoo | 12 ativos, 8.940 linhas, 745 pregões por ativo |
| Cobertura | 247 pregões em 2021; 250 em 2022; 248 em 2023 |
| Intervalo efetivo | 04/01/2021 a 28/12/2023 |
| Integridade | SHA-256 do CSV conferido contra o manifesto |
| Testes locais | **35 passaram**, 1 teste de integração ignorado localmente |
| CI Python 3.11 | Lint, formatação e testes aprovados |
| CI Python 3.12 | Lint, formatação e testes aprovados |
| CI PostgreSQL 16 | Carga, leitura, atualização e idempotência aprovadas |
| Ruff lint | All checks passed |
| Ruff format | Formatação aprovada |
| Compilação Python | app, src e tests sem erro de sintaxe |
| Dependências | pip check: No broken requirements found |
| Notebook | Estrutura válida; 8 células de código executadas sem erro |
| Interface | Dashboard carregado no navegador com dados reais e fonte CSV |
| Secrets | secrets.toml e .venv confirmados no gitignore |

O ambiente isolado local utiliza Python **3.14.3**. Dependências principais:
Streamlit 1.66.1, pandas 3.1.0, NumPy 2.5.4, Plotly 6.9.0,
yfinance 1.7.0, SQLAlchemy 2.1.6, psycopg 3.3.6 e pytest 9.2.0.
Os intervalos de versões para instalação estão em requirements.txt e requirements-dev.txt.
A matriz de CI para Python 3.11/3.12 e um job com PostgreSQL 16 foram preparados.
Os três jobs passaram no commit `462926c`. A
[execução verificada](https://github.com/rodrigodll46/projeto-final-analytics-b3/actions/runs/41154102299)
registra os resultados. A integração identificou e permitiu corrigir o cache SQL
que devolvia resultados antigos após uma carga; o teste passou após a correção.

## O que os testes verificam

- Retornos conhecidos, base 100, drawdown e volatilidade amostral anualizada.
- Carteira com pesos iguais no início e sem rebalanceamento.
- Primeiro retorno excluído do recorte, SMA com histórico e ausência de look-ahead.
- Rejeição de dados inválidos, nulos, duplicatas, universo ou cobertura incompletos.
- Prioridade do banco, contingência CSV, falha de ambas as fontes e mensagens sem secrets.
- Atualização do cache quando o snapshot local muda.
- Contrato do download, tentativas, alias histórico da Embraer e preservação do CSV.
- Correspondência do snapshot entregue com o manifesto.
- AppTest: quatro métricas, cinco gráficos, filtros de setor e data, reset,
  seleção vazia e intervalo insuficiente.

Os testes de unidade usam dados sintéticos exclusivamente como fixtures.
O snapshot entregue e o notebook utilizam dados reais do provedor.
O simulador AppTest e o kernel Jupyter precisaram de execução com sockets locais
disponíveis; isso é uma necessidade do ambiente de teste, não uma dependência externa do CSV.

## Resultados analíticos do snapshot completo

| Indicador | Resultado |
| --- | ---: |
| Retorno da carteira com pesos iniciais iguais | 58,41% |
| Maior retorno: PETR4 | 228,69% |
| Menor retorno: BBDC4 | -6,93% |
| Volatilidade média dos ativos | 33,61% a.a. |
| Maior drawdown em magnitude: EMBR3 | -58,27% |

Esses números dependem do snapshot e dos ajustes do Yahoo. Não são resultados
de uma carteira real com custos. As fórmulas e os deltas estão no README e na aplicação.

## Limites da verificação

**Supabase:** provedor escolhido para o banco remoto. A configuração, SQL de
criação e carga do snapshot estão preparados. A sessão autenticada e a definição
da senha do banco dependem do titular da conta. O job de CI usa um PostgreSQL
descartável para verificar upsert e leitura, sem acessar o banco de produção.
O teste de contingência local foi executado e o dashboard carregou o CSV.

**Git:** repositório público criado em
[rodrigodll46/projeto-final-analytics-b3](https://github.com/rodrigodll46/projeto-final-analytics-b3).
Os commits publicados registram a preparação real da entrega com autoria de Rodrigo Correa,
usando o email noreply da conta autenticada, sem datas retroativas.

**Publicação Streamlit:** preparação completa para Community Cloud. A aceitação
dos termos e o login precisam ser concluídos pelo titular da conta antes do deploy.

**Apresentação:** 9 slides com notas de apresentação, 3 gráficos editáveis e
2 tabelas. Estrutura, fontes e relações dos gráficos com planilhas incorporadas
passaram na validação. As prévias foram revisadas. O arquivo não foi aberto no
Microsoft PowerPoint neste ambiente.

**Definições dos dados:** Volume Financeiro é estimado por Close × Volume,
os quatro grupos setoriais são didáticos e EMBR3 usa o histórico migrado para
EMBJ3.SA na aquisição inicial. Essas escolhas estão explícitas nos artefatos.
Não foi fornecido o arquivo original da rubrica associado aos marcadores cite.

## Evidência visual

![Dashboard com métricas calculadas sobre o snapshot real](docs/dashboard.png)

# Roteiro de apresentação

**Rodrigo Correa** · Projeto Final de Analytics Financeiro · Linha 2.
Duração sugerida: **3 a 5 minutos**, conforme o item 5.5 do PDF.
Material de apoio para demonstração oral. O autor decidiu não entregar vídeo;
este roteiro e os slides não substituem esse requisito.

1. **Objetivo e universo (0:00–0:45).** Comparar retorno e risco de 12 ativos da B3
   entre janeiro de 2021 e dezembro de 2023. Explicar os quatro grupos didáticos.
2. **Dados e ETL (0:45–1:10).** Mostrar os 8.940 registros e o manifesto com hash.
   Explicar o tratamento de falhas, o ticker histórico EMBR3 e o alias de aquisição.
3. **Arquitetura (1:10–1:30).** Separação entre aquisição, qualidade, persistência,
   indicadores e interface. Explicar a prioridade PostgreSQL e o fallback CSV.
4. **Método e resultados (1:30–2:15).** Retornos sobre Adj Close, 252 pregões na
   anualização, carteira com pesos iniciais iguais e drawdown reiniciado na janela.
   No snapshot completo: carteira 58,41%, PETR4 228,69%,
   BBDC4 -6,93%, volatilidade média 33,61% a.a. e maior drawdown de EMBR3 -58,27%.
   Mostrar que retorno elevado e risco elevado são dimensões diferentes.
5. **Demonstração (2:15–3:45).** Filtrar Energia em 2022, comparar ativos, observar
   risco/distribuição e correlação, abrir SMA 21/50 e Conclusões, baixar CSV e restaurar filtros.
6. **Qualidade e limites (3:45–5:00).** Mostrar testes e CI executados. Explicar
   volume financeiro estimado, ajustes do provedor e ausência de custos/impostos.
   PETR4 liderou a razão acumulada/volatilidade (5,80) e o Sharpe empírico rf=0
   (1,22); EGIE3 teve o drawdown menos severo (-17,65%). Diferenciar as medidas,
   sem atribuir causalidade ou desempenho futuro aos resultados.

## Perguntas prováveis

**Por que Adj Close?** Para considerar os ajustes de eventos corporativos do
provedor na série usada para os retornos.

**Por que não preencher feriados?** Não existem negociações nesses dias. Preencher
preços criaria retornos artificiais e alteraria a distribuição e a volatilidade.

**Volatilidade média é risco da carteira?** São grandezas distintas. A carteira
combina os retornos e seus efeitos de correlação. A aplicação calcula ambos para os deltas.

**Volume Financeiro é oficial?** É uma aproximação Close × Volume, claramente
identificada. Giro oficial exigiria outra fonte e um contrato de dados correspondente.

**Por que quatro setores?** O enunciado exige quatro grupos, mas lista ativos de
mais setores oficiais. O projeto usa agrupamentos didáticos e explicita essa decisão.

**O sistema funciona sem banco?** Sim. A leitura tenta PostgreSQL e, em caso de
falha ou qualidade insuficiente, valida e usa o CSV local incluído no repositório.

**O histórico Git prova todo o desenvolvimento?** Os commits registram a preparação
real da entrega, sem datas retroativas ou simulação de um histórico anterior.

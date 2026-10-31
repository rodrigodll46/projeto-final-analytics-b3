# Publicação e banco Supabase

Autor: **Rodrigo Correa**. Repositório de entrega:
[rodrigodll46/projeto-final-analytics-b3](https://github.com/rodrigodll46/projeto-final-analytics-b3).

## Supabase

Crie um projeto dedicado no plano Free. Escolha a região mais adequada e defina
a senha do banco diretamente no painel. Não envie senhas pelo chat ou ao GitHub.
O volume do snapshot é pequeno para os limites publicados do plano gratuito.
Projetos Free podem pausar após inatividade; o CSV mantém a aplicação utilizável.

O projeto desta entrega foi criado no plano Free, região São Paulo, e a carga
real de 8.940 registros foi conferida contra o CSV. O papel `b3_reader` possui
SELECT na tabela `public.b3_prices`, sem INSERT, UPDATE, DELETE ou TRUNCATE.
A tabela usa RLS e a Data API foi desativada. As credenciais ficam fora do Git.

No projeto, abra **Connect**, selecione **Session pooler** e consulte os parâmetros.
O pooler de sessão suporta IPv4, útil para conexões de servidores sem IPv6.
Use os valores exatos mostrados pelo painel, pois o host varia por região/projeto.

Copie `.streamlit/secrets.supabase.toml.example` para `.streamlit/secrets.toml` e
preencha host, usuário e senha. A porta de sessão normalmente é 5432, conforme o painel.
Mantenha `sslmode=require`, o limite do pool e `connect_timeout`.

Na configuração desta entrega, `postgresql` usa o leitor `b3_reader` e
`postgresql_admin` mantém a credencial de carga somente no arquivo local.
O carregador escolhe a conexão administrativa quando ela existe.
Para publicar no Streamlit, transfira exclusivamente o bloco `postgresql`
e seus subtópicos. Não transfira o bloco `postgresql_admin`.

No SQL Editor do projeto, execute o conteúdo de `sql/supabase_setup.sql`.
Ele cria a tabela e restringe seu acesso via Data API. Depois, na raiz local:

```powershell
.\.venv\Scripts\python.exe -m src.database --upload-csv
```

Esse comando usa o CSV incluído, faz upsert e compara todos os registros lidos
do banco com o snapshot. Não refaz o download do Yahoo.
Para apenas conferir uma carga já existente:

```powershell
.\.venv\Scripts\python.exe -m src.database
```

Abra o dashboard e pressione **Recarregar fontes**. A fonte ativa deve mudar
para PostgreSQL. Para demonstrar a contingência, retire temporariamente os secrets
da configuração de execução, reinicie o app e confirme a fonte CSV local.
Restaure a configuração ao terminar. Não apague o banco para testar o fallback.

## Streamlit Community Cloud

Depois de publicar o código no GitHub, entre em
[Streamlit Community Cloud](https://share.streamlit.io/) com a conta correta.
Crie a aplicação com estes parâmetros:

| Campo | Valor |
| --- | --- |
| Repositório | rodrigodll46/projeto-final-analytics-b3 |
| Branch | codex/analytics-b3 |
| Main file path | app.py |
| Python | 3.12 |
| URL sugerida, sujeita à disponibilidade | rodrigo-correa-analytics-b3.streamlit.app |

Em **Advanced settings**, preencha os secrets no gerenciador da plataforma.
Sem secrets, a publicação funciona usando o CSV do repositório.
O banco fica no servidor; a senha não aparece nos gráficos ou no download.

Após o deploy, confira carregamento, fonte ativa, filtros e exportação. Abra
a URL pública em uma sessão sem login antes de informar o link à avaliação.
Registre a URL efetiva em README e VALIDACAO somente após a publicação.

## Referências

- [Supabase: conexão PostgreSQL e pooler](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Supabase: limites gratuitos](https://supabase.com/pricing)
- [Streamlit: deploy e versão Python](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Streamlit: secrets na nuvem](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)

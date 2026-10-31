-- Execute no projeto dedicado ao trabalho, usando o SQL Editor do Supabase.
-- O dashboard acessa o PostgreSQL pelo servidor, via st.secrets.
CREATE TABLE IF NOT EXISTS public.b3_prices (
    data date NOT NULL,
    ativo varchar(10) NOT NULL,
    setor varchar(60) NOT NULL,
    open double precision NOT NULL,
    high double precision NOT NULL,
    low double precision NOT NULL,
    close double precision NOT NULL,
    adj_close double precision NOT NULL,
    volume double precision NOT NULL,
    volume_financeiro double precision NOT NULL,
    PRIMARY KEY (data, ativo)
);

-- Impede acesso sem política via Data API. Não afeta a conexão do proprietário.
ALTER TABLE public.b3_prices ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.b3_prices FROM anon, authenticated;

-- Conferência da carga após python -m src.database --upload-csv.
SELECT ativo, count(*) AS pregoes, min(data) AS inicio, max(data) AS fim
FROM public.b3_prices
GROUP BY ativo
ORDER BY ativo;

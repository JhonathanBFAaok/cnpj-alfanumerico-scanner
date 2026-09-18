CREATE TABLE fornecedor (
    id       SERIAL PRIMARY KEY,
    razao    VARCHAR(200),
    cnpj     BIGINT NOT NULL UNIQUE,
    cgc_raiz NUMERIC(8) NULL,
    cnpj_fmt VARCHAR(11)
);
CREATE INDEX idx_forn_cnpj ON fornecedor (cnpj);

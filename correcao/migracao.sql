-- Migracao de coluna de CNPJ numerica para alfanumerica.
-- TESTE EM HOMOLOGACAO ANTES. Faca backup. Confira indices, FKs e views dependentes.

-- ---------- PostgreSQL ----------
ALTER TABLE fornecedor ADD COLUMN cnpj_novo CHAR(14);
UPDATE fornecedor SET cnpj_novo = LPAD(cnpj::text, 14, '0');   -- preserva zeros a esquerda
ALTER TABLE fornecedor DROP CONSTRAINT IF EXISTS fornecedor_cnpj_key;
ALTER TABLE fornecedor DROP COLUMN cnpj;
ALTER TABLE fornecedor RENAME COLUMN cnpj_novo TO cnpj;
ALTER TABLE fornecedor ALTER COLUMN cnpj SET NOT NULL;
ALTER TABLE fornecedor ADD CONSTRAINT fornecedor_cnpj_key UNIQUE (cnpj);
CREATE INDEX idx_forn_cnpj ON fornecedor (cnpj);
-- Trava de qualidade: so aceita o formato novo
ALTER TABLE fornecedor ADD CONSTRAINT ck_cnpj_formato
  CHECK (cnpj ~ '^[0-9A-Z]{12}[0-9]{2}$');

-- ---------- MySQL / MariaDB ----------
-- ALTER TABLE fornecedor ADD COLUMN cnpj_novo CHAR(14);
-- UPDATE fornecedor SET cnpj_novo = LPAD(CAST(cnpj AS CHAR), 14, '0');
-- ALTER TABLE fornecedor DROP INDEX cnpj;
-- ALTER TABLE fornecedor DROP COLUMN cnpj;
-- ALTER TABLE fornecedor CHANGE cnpj_novo cnpj CHAR(14) NOT NULL;
-- ALTER TABLE fornecedor ADD UNIQUE INDEX idx_forn_cnpj (cnpj);
-- Atencao: use collation case-insensitive OU normalize sempre para MAIUSCULO na aplicacao.

-- ---------- SQL Server ----------
-- ALTER TABLE fornecedor ADD cnpj_novo CHAR(14) NULL;
-- UPDATE fornecedor SET cnpj_novo = RIGHT('00000000000000' + CAST(cnpj AS VARCHAR(14)), 14);
-- DROP INDEX idx_forn_cnpj ON fornecedor;
-- ALTER TABLE fornecedor DROP COLUMN cnpj;
-- EXEC sp_rename 'fornecedor.cnpj_novo', 'cnpj', 'COLUMN';
-- ALTER TABLE fornecedor ALTER COLUMN cnpj CHAR(14) NOT NULL;
-- CREATE UNIQUE INDEX idx_forn_cnpj ON fornecedor (cnpj);

-- ---------- Checagem pos-migracao ----------
-- SELECT COUNT(*) AS fora_do_padrao FROM fornecedor
--  WHERE cnpj !~ '^[0-9A-Z]{12}[0-9]{2}$';   -- PostgreSQL

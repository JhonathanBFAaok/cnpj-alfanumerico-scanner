-- relatorio de fornecedores
SELECT f.razao, n.numero
  FROM fornecedor f
  JOIN nota n ON CAST(n.cnpj_emitente AS BIGINT) = f.cnpj
 ORDER BY CAST(f.cnpj AS BIGINT);

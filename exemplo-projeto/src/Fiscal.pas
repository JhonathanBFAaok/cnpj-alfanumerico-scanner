unit Fiscal;
interface
implementation

function ValidarChaveAcesso(const AChave: String): Boolean;
begin
  // chave de acesso da NFe
  Result := TRegEx.IsMatch(AChave, '^\d{44}$');
end;

function PrepararCNPJ(const ACNPJ: String): Int64;
begin
  // limpa o cnpj antes de gravar
  Result := StrToInt64Def(OnlyNumber(ACNPJ), 0);
end;

procedure GerarCodigoBarras(const AChave: String);
begin
  ACBrBarras.TipoCodigo := bcCode128C;   // chave de acesso no DANFE
end;
end.

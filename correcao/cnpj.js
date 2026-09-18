/**
 * CNPJ alfanumerico - implementacao de referencia (IN RFB 2.229)
 * Validado contra 00.000.000/E08G-12 (primeiro emitido pela Receita em 31/07/2026)
 */
const PESOS = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
const RE_CNPJ = /^[0-9A-Z]{12}[0-9]{2}$/;

/** Remove SOMENTE os separadores. Nunca use \D aqui — isso apaga as letras. */
export function limpar(cnpj) {
  return String(cnpj ?? '').replace(/[.\/-]/g, '').toUpperCase();
}

function digito(base) {
  const pesos = PESOS.slice(-base.length);
  const soma = [...base].reduce((acc, c, i) => acc + (c.charCodeAt(0) - 48) * pesos[i], 0);
  const resto = soma % 11;
  return resto < 2 ? 0 : 11 - resto;
}

export function calcularDv(base12) {
  const base = limpar(base12).slice(0, 12);
  const d1 = digito(base);
  const d2 = digito(base + d1);
  return `${d1}${d2}`;
}

export function validar(cnpj) {
  const c = limpar(cnpj);
  if (!RE_CNPJ.test(c)) return false;
  if (new Set(c).size === 1) return false;
  return calcularDv(c.slice(0, 12)) === c.slice(12);
}

export function formatar(cnpj) {
  const c = limpar(cnpj);
  if (c.length !== 14) return cnpj;
  return `${c.slice(0,2)}.${c.slice(2,5)}.${c.slice(5,8)}/${c.slice(8,12)}-${c.slice(12)}`;
}

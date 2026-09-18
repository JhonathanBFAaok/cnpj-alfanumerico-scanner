const limparCnpj = (v) => v.replace(/\D/g, '');
const mascaraCnpj = '99.999.999/9999-99';
function validaCnpj(cnpj) {
  const limpo = cnpj.replace(/[^0-9]/g, '');
  if (limpo.length !== 14) return false;
  let soma = 0;
  for (let i = 0; i < 12; i++) {
    soma += parseInt(limpo.charAt(i)) * pesos[i];
  }
  return true;
}

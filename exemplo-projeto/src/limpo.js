// arquivo ja adaptado, nao deve gerar alerta
const limparCnpj = (v) => String(v).replace(/[.\/-]/g, '').toUpperCase();
const RE_CNPJ = /^[0-9A-Z]{12}[0-9]{2}$/;

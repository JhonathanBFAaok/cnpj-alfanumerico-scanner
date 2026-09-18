/*
 * CNPJ alfanumerico - implementacao de referencia (IN RFB 2.229)
 * Validado contra 00.000.000/E08G-12, o primeiro emitido pela Receita em 31/07/2026.
 *
 * Escrito em ES5 de proposito: funciona em navegador antigo, em Node velho e
 * dentro de sistema legado, sem transpilar. Nao usa arrow function, spread,
 * template string nem o operador ??.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();            // Node / CommonJS
  } else if (typeof define === 'function' && define.amd) {
    define([], factory);                   // AMD
  } else {
    root.CnpjAlfa = factory();             // <script> direto na pagina
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var PESOS = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  var RE_CNPJ = /^[0-9A-Z]{12}[0-9]{2}$/;
  var RE_SEPARADORES = /[.\/-]/g;

  /* Remove SOMENTE os separadores. Nunca use \D aqui: isso apaga as letras. */
  function limpar(cnpj) {
    if (cnpj === null || cnpj === undefined) { return ''; }
    return String(cnpj).replace(RE_SEPARADORES, '').toUpperCase();
  }

  function digito(base) {
    var pesos = PESOS.slice(PESOS.length - base.length);
    var soma = 0;
    for (var i = 0; i < base.length; i++) {
      soma += (base.charCodeAt(i) - 48) * pesos[i];   // 'A' = 17 ... 'Z' = 42
    }
    var resto = soma % 11;
    return resto < 2 ? 0 : 11 - resto;
  }

  function calcularDv(base12) {
    var base = limpar(base12).substring(0, 12);
    var d1 = digito(base);
    var d2 = digito(base + String(d1));
    return String(d1) + String(d2);
  }

  function validar(cnpj) {
    var c = limpar(cnpj);
    if (!RE_CNPJ.test(c)) { return false; }
    var todosIguais = true;
    for (var i = 1; i < c.length; i++) {
      if (c.charAt(i) !== c.charAt(0)) { todosIguais = false; break; }
    }
    if (todosIguais) { return false; }
    return calcularDv(c.substring(0, 12)) === c.substring(12);
  }

  function formatar(cnpj) {
    var c = limpar(cnpj);
    if (c.length !== 14) { return cnpj; }
    return c.substring(0, 2) + '.' + c.substring(2, 5) + '.' + c.substring(5, 8) +
           '/' + c.substring(8, 12) + '-' + c.substring(12);
  }

  return { limpar: limpar, calcularDv: calcularDv, validar: validar, formatar: formatar };
}));

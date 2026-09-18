import { validar, calcularDv, formatar } from '../correcao/cnpj.js';
const casos = [['00.000.000/E08G-12',true],['11.222.333/0001-81',true],['00.000.000/E08G-13',false],['11.222.333/0001-80',false],['00.000.000/0000-00',false]];
let ok = true;
for (const [v,e] of casos) { const r = validar(v); if (r!==e) ok=false; console.log((r===e?'OK ':'FALHOU'), v, 'validar=',r); }
console.log('DV 00000000E08G =', calcularDv('00000000E08G'), '(esperado 12)');
console.log('formatar:', formatar('00000000E08G12'));
console.log(ok ? 'JS: TODOS PASSARAM' : 'JS: FALHOU');

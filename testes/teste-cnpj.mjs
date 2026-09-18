// Teste da implementacao de referencia em JavaScript.
// O cnpj.js e UMD (funciona em <script>, CommonJS e AMD) de proposito, para
// rodar em sistema legado. Por isso aqui usamos createRequire.
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const C = require('../correcao/cnpj.js');

const casos = [
  ['00.000.000/E08G-12', true],   // primeiro alfanumerico real da Receita
  ['11.222.333/0001-81', true],   // numerico classico
  ['00.000.000/E08G-13', false],  // DV errado
  ['11.222.333/0001-80', false],  // DV errado
  ['00.000.000/0000-00', false],  // repetido
  ['', false], [null, false], [undefined, false], ['abc', false],
  ['00.000.000/E08G-1', false],   // curto demais
];

let ok = true;
for (const [valor, esperado] of casos) {
  const r = C.validar(valor);
  if (r !== esperado) ok = false;
  console.log((r === esperado ? 'OK ' : 'FALHOU'), JSON.stringify(valor), 'validar=', r);
}
console.log('DV 00000000E08G =', C.calcularDv('00000000E08G'), '(esperado 12)');
console.log('formatar:', C.formatar('00000000E08G12'));
console.log(ok ? 'JS: TODOS PASSARAM' : 'JS: FALHOU');
process.exit(ok ? 0 : 1);

# -*- coding: utf-8 -*-
"""Roda todos os testes do projeto. Use depois de mexer nas regras."""
import os, sys, subprocess, tempfile, shutil, io

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
falhas = []

def passo(nome, ok, detalhe=''):
    print(('  OK     ' if ok else '  FALHOU ') + nome + (('  -> ' + detalhe) if detalhe else ''))
    if not ok:
        falhas.append(nome)

print('\n1) Algoritmo do digito verificador')
r = subprocess.run([sys.executable, os.path.join(RAIZ, 'cnpj.py')], capture_output=True, text=True)
passo('referencia Python', 'TODOS OS TESTES PASSARAM' in r.stdout)

if shutil.which('node'):
    r = subprocess.run(['node', os.path.join(RAIZ, 'testes', 'teste-cnpj.mjs')],
                       capture_output=True, text=True, cwd=os.path.join(RAIZ, 'testes'))
    passo('referencia JavaScript', 'TODOS PASSARAM' in r.stdout)
else:
    print('  PULADO  referencia JavaScript (node nao encontrado)')

def contar(pasta):
    tmp = tempfile.mkdtemp()
    try:
        r = subprocess.run([sys.executable, os.path.join(RAIZ, 'scan.py'), pasta,
                            '-o', os.path.join(tmp, 'r.html')], capture_output=True, text=True)
        for linha in r.stdout.splitlines():
            if linha.startswith('CRITICO:'):
                return int(linha.split('total')[1].replace('pontos','').strip(' )'))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return -1

print('\n2) Scanner - deteccao')
n = contar(os.path.join(RAIZ, 'exemplo-projeto'))
passo('projeto quebrado acusa 25 pontos', n == 25, 'achou %d' % n)

print('\n3) Scanner - falso positivo')
tmp = tempfile.mkdtemp()
try:
    for f in os.listdir(os.path.join(RAIZ, 'correcao')):
        shutil.copy(os.path.join(RAIZ, 'correcao', f), tmp)
    shutil.copy(os.path.join(RAIZ, 'cnpj.py'), tmp)
    n = contar(tmp)
    passo('kit de correcao acusa 0 pontos', n == 0, 'achou %d' % n)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print('\n4) Acentuacao dos textos do relatorio')
r = subprocess.run([sys.executable, os.path.join(RAIZ, 'testes', 'checar-textos.py')],
                   capture_output=True, text=True)
passo('portugues correto no que o cliente le', r.returncode == 0,
      (r.stdout.strip().splitlines() or [''])[0].strip())

print('\n5) CNPJ oficial de teste publicado pela SVRS (PC3D315K000193)')
sys.path.insert(0, RAIZ)
import cnpj as referencia
passo('Python valida o CNPJ oficial e rejeita DV trocado',
      referencia.validar('PC3D315K000193') and not referencia.validar('PC3D315K000194'))
if shutil.which('node'):
    js = ("const {createRequire}=require('module');"
          "const c=createRequire(process.cwd()+'/')('./correcao/cnpj.js');"
          "console.log(c.validar('PC3D315K000193') && !c.validar('PC3D315K000194') ? 'SIM' : 'NAO');")
    r = subprocess.run(['node', '-e', js], capture_output=True, text=True, cwd=RAIZ)
    passo('JavaScript (kit ES5) valida o CNPJ oficial', r.stdout.strip() == 'SIM', r.stderr.strip()[:80])

print('\n6) ISPB alfanumerico (Banco Central)')
fonte = tempfile.mkdtemp()
saida = tempfile.mkdtemp()
try:
    with io.open(os.path.join(fonte, 'pix.js'), 'w', encoding='utf-8') as f:
        f.write('function validaIspb(ispb) {\n  return /^\\d{8}$/.test(ispb);\n}\n\n\n\n\n'
                'const codigo = parseInt(ispb, 10);\n\n\n\n\n'
                'function validaIspbNovo(ispb) {\n  return /^[0-9A-Z]{8}$/.test(ispb);\n}\n\n\n\n\n'
                'const cep = /^\\d{8}$/;\n')
    j = os.path.join(saida, 'a.json')
    subprocess.run([sys.executable, os.path.join(RAIZ, 'scan.py'), fonte,
                    '-o', os.path.join(saida, 'r.html'), '--json', j], capture_output=True, text=True)
    import json
    with io.open(j, encoding='utf-8') as f:
        dados = json.load(f)
    linhas = sorted(a['linha'] for a in dados if a['regra_id'] == 'ISPB_NUMERICO')
    passo('acusa \\d{8} e parseInt no ISPB, ignora o ja adaptado e o CEP', linhas == [2, 8],
          'linhas %s' % linhas)
finally:
    shutil.rmtree(fonte, ignore_errors=True)
    shutil.rmtree(saida, ignore_errors=True)

print('\n' + ('TUDO PASSOU' if not falhas else 'FALHARAM: ' + ', '.join(falhas)) + '\n')
sys.exit(1 if falhas else 0)

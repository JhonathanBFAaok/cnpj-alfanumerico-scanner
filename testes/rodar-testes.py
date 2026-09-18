# -*- coding: utf-8 -*-
"""Roda todos os testes do projeto. Use depois de mexer nas regras."""
import os, sys, subprocess, tempfile, shutil

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

print('\n' + ('TUDO PASSOU' if not falhas else 'FALHARAM: ' + ', '.join(falhas)) + '\n')
sys.exit(1 if falhas else 0)

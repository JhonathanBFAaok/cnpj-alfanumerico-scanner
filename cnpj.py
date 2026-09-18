# -*- coding: utf-8 -*-
"""
Referencia oficial do CNPJ alfanumerico (IN RFB 2.229).

Formato: 12 caracteres alfanumericos (0-9, A-Z) + 2 digitos verificadores numericos.
Valor de cada caractere no calculo do DV = codigo ASCII - 48.
  '0'..'9' -> 0..9      'A' -> 17    'B' -> 18   ...   'Z' -> 42

Validado contra o primeiro CNPJ alfanumerico emitido pela Receita Federal
em 31/07/2026: 00.000.000/E08G-12
"""
import re

CARACTERES_VALIDOS = re.compile(r'^[0-9A-Z]{12}[0-9]{2}$')
PESOS = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]


def _valor(caractere):
    return ord(caractere.upper()) - 48


def _digito(base):
    pesos = PESOS[-len(base):]
    soma = sum(_valor(c) * p for c, p in zip(base, pesos))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def limpar(cnpj):
    """Remove APENAS os separadores de formatacao. Nunca use \\D — isso apaga as letras."""
    return re.sub(r'[./-]', '', str(cnpj or '')).upper()


def calcular_dv(base12):
    base = limpar(base12)[:12]
    d1 = _digito(base)
    d2 = _digito(base + str(d1))
    return '%d%d' % (d1, d2)


def validar(cnpj):
    limpo = limpar(cnpj)
    if not CARACTERES_VALIDOS.match(limpo):
        return False
    if len(set(limpo)) == 1:
        return False
    return calcular_dv(limpo[:12]) == limpo[12:]


def formatar(cnpj):
    c = limpar(cnpj)
    if len(c) != 14:
        return cnpj
    return '%s.%s.%s/%s-%s' % (c[0:2], c[2:5], c[5:8], c[8:12], c[12:14])


if __name__ == '__main__':
    testes = [
        ('00.000.000/E08G-12', True),   # primeiro alfanumerico real da Receita
        ('11.222.333/0001-81', True),   # numerico classico
        ('00.000.000/E08G-13', False),  # DV errado
        ('11.222.333/0001-80', False),  # DV errado
        ('00.000.000/0000-00', False),  # repetido
    ]
    ok = True
    for valor, esperado in testes:
        r = validar(valor)
        status = 'OK ' if r == esperado else 'FALHOU'
        if r != esperado:
            ok = False
        print('%s %-22s validar=%s esperado=%s' % (status, valor, r, esperado))
    print('\nDV de 00000000E08G =', calcular_dv('00000000E08G'), '(esperado 12)')
    print('TODOS OS TESTES PASSARAM' if ok else 'HOUVE FALHA')

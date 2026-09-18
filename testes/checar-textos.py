# -*- coding: utf-8 -*-
"""
Confere a acentuacao de todo texto que chega ao cliente no relatorio.
Portugues errado num laudo profissional custa credibilidade.

    python testes/checar-textos.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from regras import REGRAS

ACENTO = {
 'nao':'não','sao':'são','voce':'você','voces':'vocês','ja':'já','so':'só',
 'tambem':'também','alem':'além','apos':'após','atraves':'através','porem':'porém',
 'entao':'então','digito':'dígito','digitos':'dígitos','numero':'número','numeros':'números',
 'numerico':'numérico','numerica':'numérica','numericos':'numéricos','numericas':'numéricas',
 'alfanumerico':'alfanumérico','alfanumerica':'alfanumérica','conversao':'conversão',
 'validacao':'validação','ordenacao':'ordenação','remocao':'remoção','formatacao':'formatação',
 'migracao':'migração','atencao':'atenção','excecao':'exceção','funcao':'função',
 'funcoes':'funções','posicao':'posição','posicoes':'posições','proporcao':'proporção',
 'mascara':'máscara','mascaras':'máscaras','formulario':'formulário','formularios':'formulários',
 'relatorio':'relatório','relatorios':'relatórios','usuario':'usuário','usuarios':'usuários',
 'possivel':'possível','impossivel':'impossível','invalido':'inválido','valido':'válido',
 'calculo':'cálculo','codigo':'código','codigos':'códigos','proprio':'próprio','propria':'própria',
 'referencia':'referência','experiencia':'experiência','maquina':'máquina','maquinas':'máquinas',
 'saida':'saída','padrao':'padrão','padroes':'padrões','indice':'índice','indices':'índices',
 'historico':'histórico','automatico':'automático','basico':'básico','minimo':'mínimo',
 'maximo':'máximo','ultimo':'último','unico':'único','sera':'será','serao':'serão',
 'duvida':'dúvida','duvidas':'dúvidas','pratica':'prática','publico':'público',
 'tecnico':'técnico','tecnica':'técnica','necessario':'necessário','obrigatorio':'obrigatório',
 'disponivel':'disponível','responsavel':'responsável','area':'área','areas':'áreas',
}

def main():
    problemas = 0
    for r in REGRAS:
        for campo in ('titulo', 'porque', 'correcao'):
            for w in re.findall(r'[A-Za-zÀ-ÿ]+', r.get(campo, '')):
                if w.lower() in ACENTO:
                    print('  FALTA  %-20s [%-8s] "%s" -> "%s"'
                          % (r['id'], campo, w, ACENTO[w.lower()]))
                    problemas += 1
    if problemas:
        print('\n  %d palavra(s) sem acento no texto que o cliente le.' % problemas)
        return 1
    print('  Acentuacao OK em %d regras.' % len(REGRAS))
    return 0

if __name__ == '__main__':
    sys.exit(main())

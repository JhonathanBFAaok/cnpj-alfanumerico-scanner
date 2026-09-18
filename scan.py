# -*- coding: utf-8 -*-
"""
Scanner de compatibilidade com o CNPJ alfanumerico (Receita Federal, IN RFB 2.229).

Uso:
    python scan.py <pasta-do-projeto> [-o relatorio.html] [--json saida.json]

Nao envia nada para lugar nenhum. Roda 100% local.
"""
import os
import re
import sys
import json
import html
import argparse
from datetime import datetime

# O console do Windows costuma ser cp850 ou cp1252. Se um arquivo do cliente
# tiver emoji, travessao ou caractere asiatico, um print cru derruba o programa
# com UnicodeEncodeError. Trocar por '?' e melhor que quebrar na frente dele.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors='replace')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regras import REGRAS, EXTENSOES, IGNORAR_PASTAS, PASTAS_TESTE, TOKENS_CNPJ

MAX_POR_ARQUIVO_REGRA = 3   # evita que um arquivo gerado repetitivo domine o relatorio
JANELA = 3           # linhas de contexto ao redor de uma mencao solta de CNPJ
ESCOPO_FUNCAO = 30   # linhas apos declarar uma funcao cujo nome fala de CNPJ

# Linhas que sao so comentario nao viram achado (evita acusar exemplo citado em doc).
RE_COMENTARIO = re.compile(r'^\s*(//|#|\*|--|/\*|<!--|\'\'\'|\"\"\"|;)')

# Marcas de que o arquivo JA foi adaptado ao formato novo.
# Linha que ja usa o formato novo: nao e achado.
RE_LINHA_ADAPTADA = re.compile(r'\[A-Za-z0-9\]\{12\}|\[0-9A-Za-z\]\{12\}|\[A-Z0-9\]\{12\}|\[0-9A-Z\]\{12\}')

# Comentario no fim da linha: o codigo antes dele e o que vale.
RE_COMENTARIO_FINAL = re.compile(r'(?<![:\\w])//|#(?!\{)|--\s|/\*')

RE_ADAPTADO = re.compile(r'\[0-9A-Z\]\{12\}|\[0-9A-Za-z\]\{12\}|-\s*48\b', re.IGNORECASE)

# Nao varrer o relatorio que este proprio scanner gera.
MARCA_RELATORIO = 'Diagn&oacute;stico de compatibilidade'

# Regras que perdem sentido num arquivo ja adaptado.
REGRAS_SO_LEGADO = {'DV_POR_DIGITO', 'TESTE_SO_DIGITO'}
MAX_BYTES = 3_000_000
SEV_NOME = {3: 'CRITICO', 2: 'ALTO', 1: 'MEDIO'}

for r in REGRAS:
    r['_re'] = re.compile(r['padrao'], re.IGNORECASE)

_re_token = re.compile('|'.join(TOKENS_CNPJ), re.IGNORECASE)

# Declaracao de funcao/metodo cujo nome menciona CNPJ ou chave: tudo no corpo
# dela e contexto de CNPJ, mesmo que a variavel la dentro se chame "limpo".
_re_funcao_cnpj = re.compile(
    r'\b(function|def|func|procedure|sub|method|public|private|protected|static|'
    r'void|async|const|let|var|val|fun)\b[^=;{]{0,80}?'
    r'\w*(cnpj|cgc|chave|chnfe)\w*\s*[(=:]', re.IGNORECASE)


def menciona_cnpj(linha):
    return bool(_re_token.search(linha))


def ler(caminho):
    for enc in ('utf-8', 'latin-1'):
        try:
            with open(caminho, 'r', encoding=enc) as f:
                return f.read().splitlines()
        except (UnicodeDecodeError, LookupError):
            continue
        except OSError:
            return None
    return None


def varrer_arquivo(caminho, linguagem):
    linhas = ler(caminho)
    if linhas is None:
        return []
    texto = '\n'.join(linhas)
    if MARCA_RELATORIO in texto:          # e um relatorio gerado por este scanner
        return []
    adaptado = bool(RE_ADAPTADO.search(texto))
    # indices de linhas que falam de CNPJ
    ancoras = {i for i, l in enumerate(linhas) if menciona_cnpj(l)}
    if not ancoras:
        return []
    perto = set()
    for i in ancoras:
        perto.update(range(max(0, i - JANELA), min(len(linhas), i + JANELA + 1)))
    # corpo de funcao cujo nome fala de CNPJ entra inteiro
    for i, l in enumerate(linhas):
        if _re_funcao_cnpj.search(l):
            perto.update(range(i, min(len(linhas), i + ESCOPO_FUNCAO + 1)))

    achados = []
    vistos = {}          # regra_id -> quantas vezes ja registrei neste arquivo
    suprimidos = {}      # regra_id -> quantas deixei de registrar
    for i in sorted(perto):
        linha = linhas[i]
        if len(linha) > 600:
            continue
        if RE_COMENTARIO.match(linha):
            continue
        if RE_LINHA_ADAPTADA.search(linha):
            continue                      # a linha ja declara o formato novo
        m = RE_COMENTARIO_FINAL.search(linha)
        if m:
            codigo_util = linha[:m.start()]
            if not menciona_cnpj(codigo_util) and not codigo_util.strip():
                continue
            linha_match = codigo_util      # so o codigo, sem o comentario
        else:
            linha_match = linha
        for regra in REGRAS:
            if adaptado and regra['id'] in REGRAS_SO_LEGADO:
                continue
            if regra.get('contexto_sql') and linguagem != 'SQL' and not menciona_cnpj(linha):
                continue
            # regras de severidade critica e propensas a ruido exigem o termo na
            # propria linha: int() de valor, data ou contagem nao e conversao de CNPJ
            if regra.get('exige_token_na_linha') and not menciona_cnpj(linha_match):
                continue
            if regra['_re'].search(linha_match):
                n = vistos.get(regra['id'], 0)
                if n >= MAX_POR_ARQUIVO_REGRA:
                    suprimidos[regra['id']] = suprimidos.get(regra['id'], 0) + 1
                    break
                vistos[regra['id']] = n + 1
                achados.append(dict(
                    arquivo=caminho, linha=i + 1, codigo=linha.strip()[:300],
                    regra_id=regra['id'], sev=regra['sev'], titulo=regra['titulo'],
                    porque=regra['porque'], correcao=regra['correcao'], linguagem=linguagem,
                ))
                break  # uma regra por linha, a de maior prioridade
    for a in achados:
        a['repeticoes_no_arquivo'] = suprimidos.get(a['regra_id'], 0)
    return achados


def varrer(raiz, incluir_testes=False):
    achados, arquivos, ignorados = [], 0, 0
    pular = set(IGNORAR_PASTAS) if incluir_testes else set(IGNORAR_PASTAS) | PASTAS_TESTE
    for pasta, subpastas, nomes in os.walk(raiz):
        subpastas[:] = [d for d in subpastas if d.lower() not in pular and not d.startswith('.')]
        for nome in nomes:
            ext = os.path.splitext(nome)[1].lower()
            if ext not in EXTENSOES:
                continue
            caminho = os.path.join(pasta, nome)
            try:
                if os.path.getsize(caminho) > MAX_BYTES:
                    ignorados += 1
                    continue
            except OSError:
                continue
            arquivos += 1
            achados.extend(varrer_arquivo(caminho, EXTENSOES[ext]))
    return achados, arquivos, ignorados


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--tx:#14181d;--mu:#5b6672;--bd:#e3e7ec;
--c3:#c0392b;--c2:#d98218;--c1:#4a7fb5;}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#14181d;--card:#1d2228;
--tx:#eef1f4;--mu:#9aa5b1;--bd:#2c333b;--c3:#e8695a;--c2:#e8a94f;--c1:#7aa9d9;}}
*{box-sizing:border-box}body{margin:0;padding:32px 16px;background:var(--bg);color:var(--tx);
font:15px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
.w{max-width:960px;margin:0 auto}h1{font-size:26px;margin:0 0 4px}
.sub{color:var(--mu);margin:0 0 28px;font-size:14px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:28px}
.kpi{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:16px}
.kpi b{display:block;font-size:30px;line-height:1.1}
.kpi span{color:var(--mu);font-size:13px}
.s3 b{color:var(--c3)}.s2 b{color:var(--c2)}.s1 b{color:var(--c1)}
.g{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:18px 20px;margin-bottom:16px}
.g h2{font-size:17px;margin:0 0 6px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.tag{font-size:11px;font-weight:700;letter-spacing:.06em;padding:3px 8px;border-radius:5px;color:#fff}
.t3{background:var(--c3)}.t2{background:var(--c2)}.t1{background:var(--c1)}
.why{color:var(--mu);font-size:14px;margin:8px 0}
.fix{border-left:3px solid var(--c1);padding:8px 12px;margin:12px 0 4px;font-size:14px;background:rgba(122,169,217,.09)}
table{width:100%;border-collapse:collapse;margin-top:12px;font-size:13px}
td{padding:7px 8px;border-top:1px solid var(--bd);vertical-align:top}
td.loc{white-space:nowrap;color:var(--mu);font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;word-break:break-all}
.ok{text-align:center;padding:48px 20px;background:var(--card);border:1px solid var(--bd);border-radius:10px}
footer{color:var(--mu);font-size:12.5px;margin-top:32px;text-align:center;line-height:1.7}
"""


def gerar_html(achados, raiz, arquivos, destino, cliente=None):
    n = {3: 0, 2: 0, 1: 0}
    for a in achados:
        n[a['sev']] += 1
    grupos = {}
    for a in achados:
        grupos.setdefault(a['regra_id'], []).append(a)
    ordenados = sorted(grupos.values(), key=lambda g: (-g[0]['sev'], -len(g)))
    e = html.escape

    p = ['<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>Diagnostico CNPJ Alfanumerico</title><style>%s</style></head><body><div class="w">' % CSS,
         '<h1>Diagn&oacute;stico de compatibilidade &mdash; CNPJ alfanum&eacute;rico</h1>',
         '<p class="sub">%s &middot; %d arquivos analisados &middot; %s</p>' % (
             e(cliente or os.path.basename(raiz.rstrip(os.sep)) or raiz),
             arquivos, datetime.now().strftime('%d/%m/%Y %H:%M')),
         '<div class="kpis">',
         '<div class="kpi s3"><b>%d</b><span>cr&iacute;ticos</span></div>' % n[3],
         '<div class="kpi s2"><b>%d</b><span>altos</span></div>' % n[2],
         '<div class="kpi s1"><b>%d</b><span>para revisar</span></div>' % n[1],
         '<div class="kpi"><b>%d</b><span>pontos no total</span></div>' % len(achados),
         '<div class="kpi"><b>%d</b><span>arquivos afetados</span></div>'
         % len(set(a['arquivo'] for a in achados)),
         '</div>']

    if not achados:
        p.append('<div class="ok"><h2>Nenhum ponto de quebra encontrado</h2>'
                 '<p class="why">O scanner n&atilde;o achou trechos incompat&iacute;veis nos arquivos analisados. '
                 'Vale confirmar manualmente as integra&ccedil;&otilde;es com sistemas de terceiros.</p></div>')
    else:
        for g in ordenados:
            r = g[0]
            p.append('<div class="g"><h2><span class="tag t%d">%s</span> %s <span style="color:var(--mu);'
                     'font-weight:400;font-size:14px">&mdash; %d ocorr&ecirc;ncia(s)</span></h2>'
                     % (r['sev'], SEV_NOME[r['sev']], e(r['titulo']), len(g)))
            p.append('<p class="why">%s</p>' % e(r['porque']))
            p.append('<div class="fix"><b>Como corrigir:</b> %s</div>' % e(r['correcao']))
            p.append('<table>')
            for a in g[:25]:
                rel = os.path.relpath(a['arquivo'], raiz)
                rep = a.get('repeticoes_no_arquivo') or 0
                extra = (' <span style="color:var(--mu)">(+%d no mesmo arquivo)</span>' % rep) if rep else ''
                p.append('<tr><td class="loc">%s:%d</td><td><code>%s</code>%s</td></tr>'
                         % (e(rel), a['linha'], e(a['codigo']), extra))
            if len(g) > 25:
                p.append('<tr><td class="loc">&hellip;</td><td>e mais %d ocorr&ecirc;ncia(s)</td></tr>'
                         % (len(g) - 25))
            p.append('</table></div>')

    p.append('<footer>An&aacute;lise est&aacute;tica local &mdash; nenhum c&oacute;digo foi enviado para fora desta m&aacute;quina.<br>'
             'Base: Instru&ccedil;&atilde;o Normativa RFB n&ordm; 2.229. Primeiro CNPJ alfanum&eacute;rico emitido em 31/07/2026.<br>'
             'O resultado indica pontos prov&aacute;veis de quebra e n&atilde;o substitui revis&atilde;o t&eacute;cnica.</footer>')
    p.append('</div></body></html>')

    conteudo = '\n'.join(p)
    try:
        with open(destino, 'w', encoding='utf-8') as f:
            f.write(conteudo)
    except OSError as e:
        alt = os.path.join(os.getcwd(), 'relatorio-cnpj.html')
        print('\nNao consegui gravar em %s (%s).' % (destino, e.strerror or e))
        try:
            with open(alt, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print('Gravei aqui em vez disso: %s' % alt)
            return alt
        except OSError:
            print('Tambem nao consegui gravar na pasta atual. Rode de uma pasta onde voce'
                  ' tenha permissao de escrita, ou use -o com outro caminho.')
            return None
    return destino


def main():
    ap = argparse.ArgumentParser(description='Scanner de compatibilidade com o CNPJ alfanumerico')
    ap.add_argument('pasta', help='pasta raiz do projeto a analisar')
    ap.add_argument('-o', '--saida', default='relatorio-cnpj.html')
    ap.add_argument('--json', dest='json_out')
    ap.add_argument('-c', '--cliente', help='nome do cliente, exibido no cabecalho do relatorio')
    ap.add_argument('--incluir-testes', action='store_true',
                    help='varrer tambem pastas de teste e fixtures (por padrao sao ignoradas)')
    args = ap.parse_args()

    raiz = os.path.abspath(args.pasta)
    if not os.path.isdir(raiz):
        print('Pasta nao encontrada: %s' % raiz)
        return 2

    print('Analisando %s ...' % raiz)
    achados, arquivos, ignorados = varrer(raiz, args.incluir_testes)

    n = {3: 0, 2: 0, 1: 0}
    for a in achados:
        n[a['sev']] += 1

    afetados = len(set(a['arquivo'] for a in achados))
    print('\n%d arquivos analisados%s' % (arquivos, (', %d ignorados por tamanho' % ignorados) if ignorados else ''))
    print('%d arquivo(s) com problema' % afetados)
    print('CRITICO: %d   ALTO: %d   MEDIO: %d   (total %d pontos)' % (n[3], n[2], n[1], len(achados)))

    if achados:
        print('\nPrincipais pontos:')
        vistos = set()
        for a in sorted(achados, key=lambda x: -x['sev']):
            if a['regra_id'] in vistos:
                continue
            vistos.add(a['regra_id'])
            q = sum(1 for x in achados if x['regra_id'] == a['regra_id'])
            print('  [%-7s] %-52s %d ocorrencia(s)' % (SEV_NOME[a['sev']], a['titulo'][:52], q))

    destino = gerar_html(achados, raiz, arquivos, args.saida, args.cliente)
    if destino:
        print('\nRelatorio: %s' % os.path.abspath(destino))

    if args.json_out:
        # caminho relativo: o JSON nao deve carregar a estrutura de pastas da maquina
        export = []
        for a in achados:
            b = dict(a)
            b['arquivo'] = os.path.relpath(a['arquivo'], raiz).replace(os.sep, '/')
            export.append(b)
        try:
            with open(args.json_out, 'w', encoding='utf-8') as f:
                json.dump(export, f, ensure_ascii=False, indent=2)
            print('JSON:      %s' % os.path.abspath(args.json_out))
        except OSError as e:
            print('Nao consegui gravar o JSON em %s (%s). O relatorio HTML foi gerado '
                  'normalmente.' % (args.json_out, e.strerror or e))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\nInterrompido.')
        sys.exit(130)
    except Exception as e:                                  # noqa: BLE001
        # Um traceback na tela nao ajuda ninguem. Mensagem curta e o detalhe
        # guardado em arquivo, para quem quiser reportar.
        print('\nErro inesperado: %s: %s' % (type(e).__name__, e))
        try:
            import traceback
            destino = os.path.join(os.getcwd(), 'cnpj-scanner-erro.log')
            with open(destino, 'w', encoding='utf-8') as f:
                traceback.print_exc(file=f)
            print('Detalhes em: %s' % destino)
        except Exception:
            pass
        print('Se puder, relate em: '
              'https://github.com/JhonathanBFAaok/cnpj-alfanumerico-scanner/issues')
        sys.exit(1)

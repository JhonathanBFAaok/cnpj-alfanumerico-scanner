# Scanner de compatibilidade — CNPJ alfanumérico e chave de acesso

Ferramenta que varre o código de um sistema e aponta onde ele vai quebrar com o
CNPJ alfanumérico da Receita Federal — no campo do CNPJ, na chave de acesso dos
documentos fiscais e no ISPB do sistema financeiro.

**Contexto:** a Receita começou a emitir CNPJ com letras. O primeiro saiu em
**31/07/2026** — `00.000.000/E08G-12`, uma filial do Banco do Brasil. Quase todo
sistema brasileiro foi escrito assumindo que CNPJ só tem número, e a própria
Receita avisa que a falta de adaptação gera "falhas em integrações e rejeições
em processos". Base normativa: **IN RFB nº 2.229**.

---

## Não é só o campo do CNPJ

A mudança pegou mais coisa do que o cadastro:

- **Chave de acesso de 44 posições.** A Nota Técnica Conjunta 2025.001 mudou a
  chave para `[0-9]{6}[A-Z0-9]{12}[0-9]{26}` em NF-e, NFC-e, CT-e, CT-e OS, GTV-e,
  MDF-e, BP-e, BP-e TM, NF3e e NFCom, porque ela carrega o CNPJ do emitente no meio.
  Quem valida a chave com `\d{44}` ou guarda como número rejeita documento legítimo.
- **ISPB.** O Banco Central definiu que o ISPB também passa a ser alfanumérico,
  `[0-9A-Z]{8}` (DRN "CNPJ Alfanumérico" do SPI/RSFN e Informe STR 31/2025).
- **Obrigações acessórias.** eSocial, EFD-Reinf, ECD, ECF, e-Financeira, padrão TISS
  da ANS e NFS-e Nacional também foram adequados ao formato novo. No eSocial a mudança veio por
  republicação de XSD, e nenhuma nota técnica traz o assunto no título; na EFD-Reinf os novos XSD
  substituíram os antigos **mantendo o mesmo número de versão**. Quem monitora nota
  técnica ou número de versão não viu nada mudar.

Para testar em homologação, a SVRS publicou um CNPJ alfanumérico oficial:
`PC3D315K000193`. Ele está nos testes deste projeto.

---

## Como usar

**Windows** (é onde a maior parte do legado brasileiro roda):

```bat
py scan.py "C:\caminho\do\sistema" -o relatorio.html -c "Nome da Empresa"
```

**Linux ou macOS:**

```bash
python3 scan.py /caminho/do/sistema -o relatorio.html -c "Nome da Empresa"
```

Precisa apenas de **Python 3.8 ou superior**, sem instalar biblioteca nenhuma.
Se não tiver Python na máquina: https://www.python.org/downloads/ — na instalação
marque **"Add python.exe to PATH"**. São uns 2 minutos, e o Python pode ser
desinstalado depois sem deixar nada para trás.

Se preferir não instalar nada, dá para rodar numa chamada rápida junto com
alguém que já tenha o ambiente.

Opções:

| Opção | O que faz |
|---|---|
| `-o`, `--saida` | arquivo HTML do relatório (padrão: `relatorio-cnpj.html`) |
| `-c`, `--cliente` | nome que aparece no cabeçalho do relatório |
| `--json` | exporta os achados em JSON |

**Nenhum código sai da máquina.** A análise é 100% local: o programa não importa
`requests`, não importa `urllib` e não faz nenhuma chamada de rede. Dá para
conferir isso com um Ctrl+F antes de rodar.

---

## O que ele detecta

| Severidade | Problema |
|---|---|
| CRÍTICO | Limpeza com `\D` ou `[^0-9]` (apaga as letras silenciosamente) |
| CRÍTICO | Conversão do CNPJ para inteiro |
| CRÍTICO | Coluna de CNPJ com tipo numérico no banco |
| CRÍTICO | Validação que exige 14 dígitos numéricos |
| ALTO | Máscara de formulário que só aceita número |
| ALTO | Checagem "é só número?" aplicada ao CNPJ |
| ALTO | Campo `type="number"` |
| ALTO | Cálculo do dígito verificador caractere a caractere |
| CRÍTICO | Chave de acesso validada como 44 dígitos numéricos |
| CRÍTICO | `OnlyNumber` / `StrToInt64Def` sobre CNPJ ou chave (o bug que o próprio ACBr teve) |
| ALTO | Referência a pacote de schema antigo (PL_010c) |
| CRÍTICO | `Val()` / `CLng()` em Visual Basic ou Clipper (para no 1º não-dígito e devolve 0) |
| CRÍTICO | `CAST`/`CONVERT` do CNPJ para número dentro do SQL |
| CRÍTICO | CNPJ declarado como inteiro no XSD, JSON Schema ou contrato de API |
| MÉDIO | Ordenação de CNPJ como número |
| MÉDIO | Código de barras CODE-128C no DANFE |
| MÉDIO | Coluna menor que 14 caracteres |
| ALTO | ISPB validado ou convertido como 8 dígitos numéricos (Pix, STR, CNAB) |

Linguagens e formatos cobertos: PHP, JavaScript, TypeScript, Vue, Python, C#,
VB.NET, **Visual Basic 6** (`.bas`, `.frm`, `.cls`), **Clipper/Harbour** (`.prg`),
**ASP clássico**, ASP.NET (`.aspx`, `.cshtml`, `.razor`), Java/JSP, Kotlin, SQL,
Delphi/Pascal, Progress/4GL, Ruby, Go, COBOL, HTML — e ainda os **contratos**:
`.xsd`, `.wsdl`, JSON Schema, YAML e XML, onde o formato do CNPJ costuma estar
declarado como número sem ninguém lembrar.

O mais perigoso é o `\D`: ele não gera erro nenhum. `00000000E08G12` vira
`000000000812` e o dado é gravado corrompido, sem ninguém perceber.

---

## Kit de correção (`correcao/`)

Implementação de referência pronta para substituir o validador antigo:

| Arquivo | Compatível com | Por quê |
|---|---|---|
| `cnpj.php` | **PHP 5.4+** | sem type hint escalar, sem const de classe |
| `cnpj.js` | **ES5** (UMD) | roda em `<script>`, CommonJS e AMD, sem transpilar |
| `Cnpj.cs` | **C# 5 / .NET 4.0** | sem interpolação de string, sem LINQ |
| `cnpj.py` (raiz) | **Python 3.8+** | só biblioteca padrão |
| `migracao.sql` | Postgres, MySQL, SQL Server | |

As versões conservadoras são de propósito: quem tem o problema do CNPJ
alfanumérico costuma ser justamente quem mantém sistema antigo. Um validador
que exige PHP 8 não serve pra quem está em PHP 5.6.

**O cálculo do DV mudou:** o valor de cada caractere agora é o código ASCII
menos 48. `'0'`–`'9'` valem 0–9, `'A'` vale 17, `'B'` vale 18, até `'Z'` que
vale 42. O resto do algoritmo (módulo 11 com os mesmos pesos) continua igual —
por isso as funções abaixo validam corretamente tanto o CNPJ novo quanto o
antigo, e você pode trocar sem quebrar nada que já existe.

### Testes

```bash
python cnpj.py                 # referência Python
node testes/teste-cnpj.mjs     # referência JavaScript
```

Ambos são testados contra o CNPJ alfanumérico real da Receita
(`00.000.000/E08G-12`) e contra um CNPJ numérico clássico
(`11.222.333/0001-81`), mais três casos inválidos.

*Nota: as versões PHP e C# são port direto do mesmo algoritmo e foram revisadas
linha a linha, mas não puderam ser executadas aqui (PHP e .NET não estão
instalados nesta máquina). Rode os testes equivalentes antes de entregar a um
cliente nessas linguagens.*

---

## Exemplo

A pasta `exemplo-projeto/` tem código quebrado de propósito em PHP, JS, C#, SQL
e HTML — mais um arquivo já corrigido, que deve dar zero alertas. Serve para
demonstrar a ferramenta e para testar mudanças nas regras.

```bash
python scan.py exemplo-projeto -o exemplo-relatorio.html -c "ERP Exemplo Ltda"
```

Resultado esperado: **25 pontos** (18 críticos, 5 altos, 2 médios) em 9 arquivos, sem nenhum
falso positivo.

---

## Precisão

O scanner foi calibrado contra código brasileiro de verdade — as bibliotecas
fiscais de código aberto `sped-nfe`, `sped-da`, `sped-common` (NFePHP),
`erpbrasil.edoc`, `erpbrasil.base`, `pysped` e o ERP `stoq`. Mais de 3.000
arquivos.

Isso derrubou quatro fontes de falso positivo que a bateria sintética não
pegava:

- padrão sem delimitador de palavra (`TCnpj` casava dentro de `getCnpj`)
- comentário no fim da linha marcado como se fosse código
- prosa em inglês (`the CNPJ number`) lida como declaração de coluna
- proximidade por número de linhas, que marcava `int()` de valor, data e
  contagem só por estarem perto de uma menção a CNPJ

Trocas feitas por causa disso: o contexto passou a ser o **corpo da função**
quando o nome dela fala de CNPJ, não uma janela fixa de linhas; regras de
severidade crítica exigem o termo na própria linha; pastas de teste e fixture
ficam de fora por padrão (use `--incluir-testes` para varrer também); e cada
regra reporta no máximo 3 ocorrências por arquivo, para que um arquivo gerado
repetitivo não domine o relatório.

O relatório conta **pontos e arquivos afetados**, não linhas. Um número inflado
não ajuda ninguém a decidir.

---

## Robustez

Testado contra os casos que aparecem em código real e derrubam ferramenta:

- **Console do Windows** (cp850/cp1252): arquivo com emoji, travessão ou
  caractere asiático não derruba mais o programa. Antes disso era
  `UnicodeEncodeError` no meio da varredura.
- **Arquivos em Windows-1252**, comuns em legado brasileiro: lidos corretamente,
  com os acentos preservados no relatório.
- **Arquivo binário com extensão de texto** (`.dfm` do Delphi pode ser binário):
  não polui o relatório.
- **Quebra de linha CRLF**, linha minificada de milhares de caracteres, arquivo
  vazio, arquivo só com bytes nulos, pasta vazia, arquivo sem permissão de
  leitura, link simbólico circular, caminho com espaço e acentuação.
- **Conteúdo do código é escapado no HTML.** Um arquivo contendo
  `<script>alert(1)</script>` aparece como texto; o relatório não executa nada e
  não carrega script nenhum.
- **Caminho de saída inválido**: grava na pasta atual em vez de quebrar.
- **Qualquer erro inesperado**: mensagem curta na tela e o detalhe num arquivo
  de log, nunca um traceback.

Desempenho: 2 a 3 segundos em projetos reais de 1.000 a 2.700 arquivos; menos de
1 segundo em 10.000 arquivos.

---

## Limites — leia antes de prometer algo a um cliente

- É **análise estática**. Aponta pontos prováveis de quebra; não substitui
  revisão técnica nem teste em homologação.
- Pode não achar código gerado em tempo de execução, SQL montado por string ou
  regra escondida em procedure do banco.
- Integrações com sistemas de terceiros (gateway, ERP externo, API de parceiro)
  precisam ser checadas na mão — o problema pode estar do outro lado.
- A Receita **não publicou data de corte** para obrigatoriedade geral. O que
  existe hoje é a emissão gradual desde 31/07/2026. Não venda com prazo que a
  Receita não deu.

---

## Achou mais do que dá pra corrigir agora?

O scanner é gratuito e continua gratuito. Se o relatório apontar mais pontos do
que o seu time consegue absorver agora, eu faço a correção com vocês:

- **Laudo priorizado** — o que quebra primeiro, o que corrompe dado em silêncio,
  e a ordem de correção, com estimativa de esforço.
- **Correção dos pontos** — no código de vocês, na linguagem de vocês, incluindo
  legado (Delphi, VB6, Clipper, ASP clássico, PHP antigo).
- **Teste com o CNPJ oficial de homologação** antes de ir para produção.

Contato: **jhonathan.profss@gmail.com** — manda o relatório (ou só o número de
pontos) e eu respondo com o que faria e quanto custa.

---

## Licença

MIT — use, modifique e distribua à vontade. Se for útil pra você, uma estrela
ajuda outras pessoas a encontrarem.

Feito por Jhonathan Ferreira.

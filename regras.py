# -*- coding: utf-8 -*-
"""Regras de deteccao de quebra com o CNPJ alfanumerico."""

# severidade: 3 = CRITICO (quebra certa), 2 = ALTO (quebra provavel), 1 = MEDIO (revisar)
REGRAS = [
    dict(
        id='STRIP_NAO_DIGITO', sev=3,
        padrao=r"""(replace|preg_replace|re\.sub|Regex\.Replace|gsub)\s*\(\s*[^)]{0,40}\\D""",
        titulo='Limpeza com \\D apaga as letras do CNPJ',
        porque='O \\D remove tudo que não é dígito. Num CNPJ alfanumérico ele apaga as letras, '
               'transformando 00000000E08G12 em 000000000812. O dado é corrompido silenciosamente, '
               'sem erro nenhum — e este é o bug mais perigoso de todos.',
        correcao="Trocar por remoção apenas dos separadores: replace(/[.\\/-]/g, '').toUpperCase()",
    ),
    dict(
        id='STRIP_CLASSE_09', sev=3,
        padrao=r"""(replace|preg_replace|re\.sub|Regex\.Replace)\s*\(\s*[^)]{0,40}\[\^0-9\]""",
        titulo='Limpeza com [^0-9] apaga as letras do CNPJ',
        porque='Mesmo efeito do \\D: qualquer caractere que não seja dígito é removido, '
               'inclusive as letras que agora fazem parte do CNPJ.',
        correcao="Trocar a classe por [^0-9A-Za-z] ou remover apenas os separadores [./-]",
    ),
    dict(
        id='PARSE_INTEIRO', sev=3,
        padrao=r"""\b(parseInt|parseFloat|intval|floatval|Number|int|long|Int32\.Parse|Int64\.Parse|"""
               r"""Convert\.To(Int32|Int64|Decimal)|Long\.parseLong|Integer\.parseInt|StrToInt64|StrToInt|"""
               r"""to_i|Decimal\.Parse)\s*\(""",
        exige_token_na_linha=True,
        titulo='Conversão do CNPJ para número',
        porque='CNPJ com letra não converte para inteiro. Dependendo da linguagem isso lança exceção, '
               'retorna zero ou trunca no primeiro caractere inválido.',
        correcao='Tratar CNPJ sempre como texto (string). Nunca converter para número.',
    ),
    dict(
        id='COLUNA_NUMERICA', sev=3,
        padrao=r"""((cnpj|cgc)\w*\s+(BIGINT|NUMERIC|DECIMAL|INTEGER|INT|SERIAL|MONEY)\b"""
               r"""|(cnpj|cgc)\w*\s+NUMBER\s*\("""
               r"""|\b(long|int|integer|decimal|double|float|bigint|Int64|Int32|Long|Integer|Decimal|Double|BigInteger)\s+\w*(cnpj|cgc)\w*\b"""
               r"""|\b(cnpj|cgc)\w*\s*:\s*(number|int|long|float|decimal)\b)""",
        titulo='Coluna de CNPJ com tipo numérico no banco',
        porque='Coluna numérica não aceita letra. O INSERT de um CNPJ alfanumérico falha, '
               'ou o valor é gravado errado.',
        correcao='Migrar a coluna para CHAR(14) ou VARCHAR(14). Atenção ao índice e às FKs que dependem dela.',
        contexto_sql=True,
    ),
    dict(
        id='REGEX_14_DIGITOS', sev=3,
        padrao=r"""(\\d\{14\}|\[0-9\]\{14\}|\\d\{2\}\\\.?\\d\{3\}|\[0-9\]\{2\}\\?\.)""",
        titulo='Validação que exige 14 dígitos numéricos',
        porque='A expressão aceita apenas dígitos. Um CNPJ com letra é rejeitado como inválido '
               'logo na entrada, e o cliente não consegue nem se cadastrar.',
        correcao='Trocar para [0-9A-Z]{12}[0-9]{2} (12 alfanuméricos + 2 dígitos verificadores).',
    ),
    dict(
        id='MASCARA_NUMERICA', sev=2,
        padrao=r"""(9{2}\.9{3}\.9{3}|#{2}\.#{3}\.#{3}|9{3}\.9{3}\.9{3}|/9{4}-9{2}|/#{4}-#{2}"""
               r"""|(mask|mascara|m\u00e1scara|format)\w*\s*[:=]\s*["\'][^"\']*0{2}\.0{3}\.0{3})""",
        titulo='Máscara de formulário que só aceita número',
        porque='Máscaras com 9, 0 ou # normalmente restringem a digitação a números. '
               'O usuário com CNPJ alfanumérico não consegue digitar as letras.',
        correcao='Trocar o coringa para o que aceita alfanumérico na sua biblioteca '
                 '(ex.: "AA.AAA.AAA/AAAA-00" no jQuery Mask, "SS.SSS.SSS/SSSS-00" no IMask).',
    ),
    dict(
        id='TESTE_SO_DIGITO', sev=2,
        padrao=r"""\b(is_numeric|ctype_digit|isdigit|IsNumeric|isNaN|char\.IsDigit|Character\.isDigit|"""
               r"""TryParse|isNumeric)\s*\(""",
        titulo='Checagem de "é só número?" aplicada ao CNPJ',
        porque='Esse teste retorna falso para CNPJ alfanumérico válido, e o código trata '
               'como dado inválido.',
        correcao='Validar com a regra nova: 12 caracteres [0-9A-Z] + 2 dígitos, e conferir o DV.',
    ),
    dict(
        id='INPUT_NUMBER', sev=2,
        padrao=r"""type\s*=\s*["']number["']|inputmode\s*=\s*["']numeric["']|keyboardType\s*=\s*["']num""",
        titulo='Campo de formulário configurado como numérico',
        porque='O navegador bloqueia letras no campo. O usuário simplesmente não consegue digitar o CNPJ.',
        correcao='Trocar para type="text" e inputmode="text".',
    ),
    dict(
        id='DV_POR_DIGITO', sev=2,
        padrao=r"""(charAt\s*\(|\[\s*i\s*\]|substr\s*\(|\.charCodeAt|ord\s*\(|Ord\s*\()""",
        titulo='Possível cálculo do dígito verificador caractere a caractere',
        porque='O cálculo do DV mudou: o valor de cada caractere agora é o código ASCII menos 48 '
               '(A vale 17, B vale 18, até Z que vale 42). A conta antiga só funciona com dígitos.',
        correcao='Substituir pela função de referência em cnpj.py (já testada contra o CNPJ real da Receita).',
    ),
    dict(
        id='CHAVE_44_DIGITOS', sev=3,
        padrao=r"""(\\d\{44\}|\[0-9\]\{44\}|\bchar\s*\(\s*44\s*\)|\bvarchar\s*\(\s*44\s*\))""",
        titulo='Chave de acesso tratada como 44 dígitos numéricos',
        porque='A chave de acesso de 44 posições também mudou: agora é '
               '[0-9]{6}[A-Z0-9]{12}[0-9]{26}, porque carrega o CNPJ do emitente no meio. '
               'Quem valida a chave com \\d{44} rejeita nota válida de emitente alfanumérico. '
               'Este ponto passa despercebido com muito mais frequência que o campo do CNPJ.',
        correcao='Trocar a validação para [0-9]{6}[A-Z0-9]{12}[0-9]{26} e garantir que a chave '
                 'seja tratada como texto em todo o caminho (banco, índice, ordenação).',
    ),
    dict(
        id='ONLYNUMBER_ACBR', sev=3,
        padrao=r"""\b(OnlyNumber|SomenteNumeros|ApenasNumeros|OnlyCPFCNPJ|LimpaCNPJ|"""
               r"""RemoveCaracteres|TiraMascara|StrToInt64Def|StrToIntDef)\s*\(""",
        titulo='Função de "só números" aplicada ao CNPJ ou à chave',
        porque='Este é exatamente o bug que o próprio Projeto ACBr teve: o OnlyNumber apagava '
               'as letras antes de gravar o XML, e o StrToInt64Def transformava o CNPJ em 0. '
               'Foram corrigidos em jun e jul/2026. Se o seu código chama essas funções sobre '
               'CNPJ ou chave, tem o mesmo defeito.',
        correcao='Usar uma função que remova apenas os separadores [./-] e preserve as letras, '
                 'mantendo o valor como texto.',
    ),
    dict(
        id='SCHEMA_ANTIGO', sev=2,
        padrao=r"""(\bPL_00\d|\bPL_010[abc]\b|\bPL_010_V\d"""
               r"""|(simpleType|complexType)\s+name\s*=\s*["\'](TCnpj|TCnpjVar|TChNFe)["\'])""",
        titulo='Pacote de schema XML anterior ao CNPJ alfanumérico',
        porque='Os schemas XML mudaram: TCnpj e TCnpjVar passaram a [0-9A-Z]{12}[0-9]{2} e a '
               'chave a [0-9]{6}[0-9A-Z]{12}[0-9]{26}. Validar contra o XSD antigo faz o XML '
               'falhar na sua própria máquina, antes mesmo de sair.',
        correcao='Atualizar para o pacote PL_010d (ou posterior) e revalidar os XML de teste.',
    ),
    dict(
        id='CODE128C', sev=1,
        padrao=r"""(CODE[_-]?128C|Code128C|bcCode128C|barcode.{0,20}128C)""",
        titulo='Código de barras CODE-128C no DANFE',
        porque='O CODE-128C só codifica dígitos. Com chave de acesso alfanumérica ele não '
               'representa a chave. A nota técnica define um esquema híbrido 128A/128C.',
        correcao='Ajustar a geração do código de barras do DANFE/DACTE conforme a NT 2026.004.',
    ),
    dict(
        id='VAL_VB_CLIPPER', sev=3,
        padrao=r"""\b(Val|CLng|CInt|CDbl|CCur|CDec|Str2Num|VAL)\s*\(""",
        exige_token_na_linha=True,
        titulo='Conversão numérica de CNPJ em Visual Basic ou Clipper',
        porque='Val(), CLng() e equivalentes param no primeiro caractere que não é dígito. '
               'Val("00000000E08G12") devolve 0 em vez de erro — o sistema segue rodando com '
               'o CNPJ zerado.',
        correcao='Tratar como String em todo o caminho. Nunca converter CNPJ para numérico.',
    ),
    dict(
        id='SQL_CAST_NUMERICO', sev=3,
        padrao=r"""\b(CAST|CONVERT|TO_NUMBER|TO_NUMERIC)\s*\([^)]{0,60}"""
               r"""(AS\s+(BIGINT|NUMERIC|DECIMAL|INT|INTEGER|NUMBER)|,\s*(BIGINT|INT|NUMERIC))"""
               r"""|::\s*(bigint|numeric|integer|int)\b""",
        titulo='Conversão do CNPJ para número dentro do SQL',
        porque='O CAST falha ou trunca quando o CNPJ tem letra. Aparece muito em JOIN, '
               'ORDER BY e em view antiga que compara CNPJ de tabelas com tipos diferentes.',
        correcao='Comparar como texto dos dois lados e criar índice sobre a coluna de texto.',
    ),
    dict(
        id='SCHEMA_CONTRATO', sev=3, exige_nome_cnpj=True,
        padrao=r"""("type"\s*:\s*"(integer|number)"|xs:(integer|long|int|decimal)"""
               r"""|type\s*=\s*["\']xs:(integer|long|int|decimal)["\']"""
               r"""|maxLength\s*value\s*=\s*["\']1[0-3]["\'])""",
        titulo='CNPJ declarado como número no schema ou no contrato da API',
        porque='Se o XSD, o JSON Schema ou o contrato da API declaram o CNPJ como inteiro, '
               'a validação rejeita o valor alfanumérico antes de qualquer código rodar — '
               'e isso quebra também quem integra com vocês.',
        correcao='Declarar como string com o padrão [0-9A-Z]{12}[0-9]{2}. No XSD da NF-e, '
                 'usar o pacote PL_010d ou posterior.',
    ),
    dict(
        id='ORDENACAO_NUMERICA', sev=1,
        padrao=r"""ORDER\s+BY[^;]{0,60}(CAST|CONVERT|\+\s*0|::\s*(bigint|numeric))""",
        titulo='Ordenação de CNPJ como número',
        porque='Ordenar CNPJ convertendo para número quebra quando aparece letra, e muda '
               'a ordem de listagens e relatórios.',
        correcao='Ordenar como texto.',
    ),
    dict(
        id='COLUNA_CURTA', sev=1,
        padrao=r"""(cnpj|cgc)\w*\s+(CHAR|VARCHAR|NVARCHAR|VARCHAR2)\s*\(\s*(1[0-3]|[1-9])\s*\)""",
        titulo='Coluna de CNPJ menor que 14 caracteres',
        porque='Se a coluna guardava o CNPJ sem formatação em menos de 14 posições, o valor será truncado.',
        correcao='Ajustar para CHAR(14) sem formatação, ou VARCHAR(18) se guardar formatado.',
        contexto_sql=True,
    ),
    dict(
        id='ISPB_NUMERICO', sev=2, so_ispb=True,
        padrao=r"""(\\d\{8\}|\[0-9\]\{8\}|\b(parseInt|intval|int|long|Int32\.Parse|Int64\.Parse|"""
               r"""Convert\.To(Int32|Int64)|Integer\.parseInt|Long\.parseLong|StrToInt64|StrToInt|to_i)\s*\("""
               r"""|\bispb\w*\s+(BIGINT|NUMERIC|DECIMAL|INTEGER|INT)\b"""
               r"""|\b(int|long|Int32|Int64|Integer|Long)\s+\w*ispb\w*\b)""",
        titulo='ISPB tratado como 8 dígitos numéricos',
        porque='O Banco Central definiu que o ISPB também passa a ser alfanumérico, no formato '
               '[0-9A-Z]{8}, junto com o CNPJ (DRN "CNPJ Alfanumérico" do SPI e da RSFN, e Informe '
               'STR 31/2025). Quem valida ou converte o ISPB como número quebra em Pix, STR e '
               'integrações bancárias por um motivo diferente do CNPJ.',
        correcao='Tratar o ISPB como texto de 8 posições e validar com [0-9A-Z]{8}.',
    ),
]

EXTENSOES = {
    '.php': 'PHP', '.js': 'JavaScript', '.jsx': 'JavaScript', '.ts': 'TypeScript',
    '.tsx': 'TypeScript', '.vue': 'Vue', '.py': 'Python', '.cs': 'C#',
    '.vb': 'VB.NET', '.java': 'Java', '.kt': 'Kotlin', '.sql': 'SQL',
    '.pas': 'Delphi/Pascal', '.dfm': 'Delphi/Pascal', '.dpr': 'Delphi/Pascal',
    '.inc': 'PHP', '.phtml': 'PHP', '.html': 'HTML', '.htm': 'HTML',
    '.rb': 'Ruby', '.go': 'Go', '.cbl': 'COBOL', '.cob': 'COBOL',
    # Legado que ainda roda em muita casa de software brasileira
    '.bas': 'Visual Basic', '.frm': 'Visual Basic', '.cls': 'Visual Basic',
    '.ctl': 'Visual Basic', '.asp': 'ASP Classico',
    '.prg': 'Clipper/Harbour', '.ch': 'Clipper/Harbour',
    '.aspx': 'ASP.NET', '.ascx': 'ASP.NET', '.cshtml': 'ASP.NET',
    '.razor': 'ASP.NET', '.jsp': 'Java', '.4gl': 'Progress/4GL',
    # Schemas e contratos: onde o formato do CNPJ fica declarado
    '.xsd': 'Schema XML', '.wsdl': 'Schema XML', '.json': 'JSON/Config',
    '.yaml': 'Config', '.yml': 'Config', '.xml': 'XML',
}

IGNORAR_PASTAS = {
    'node_modules', 'vendor', '.git', '.svn', 'dist', 'build', 'bin', 'obj',
    '__pycache__', '.venv', 'venv', 'packages', 'bower_components', '.next',
    'coverage', 'tmp', 'temp', '.idea', '.vscode',
}

# Pastas de teste: o que importa no diagnostico e o codigo de producao.
# Use --incluir-testes para varrer estas tambem.
PASTAS_TESTE = {
    'test', 'tests', '__tests__', 'spec', 'specs', 'fixtures', 'fixture',
    'mocks', '__mocks__', 'testdata', 'samples', 'sample', 'exemplos',
}

TOKENS_CNPJ = ('cnpj', 'cgc', 'c_n_p_j', 'nrcnpj', 'numcnpj', 'cnpjcpf', 'cpfcnpj',
               'cpf_cnpj', 'chaveacesso', 'chave_acesso', 'chave de acesso', 'chnfe',
               'chave', 'danfe', 'nfekey')

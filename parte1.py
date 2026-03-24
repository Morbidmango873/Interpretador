import json

#Nome do Grupo: Francisco Hauch Cardoso, ID: Morbidmango873



# ENTRADA — única interface externa, chamada pela parte4
def parseExpressao(linhas):
    resultado = []

    for num, raw in enumerate(linhas, 1):
        linha  = raw.strip()
        tokens, pilha = estadoInicial(linha, 0, [], [])

        if pilha:
            raise ValueError(f"Linha {num}: {len(pilha)} parêntese(s) não fechado(s)")

        resultado.append({"linha": num, "tokens": tokens})

    return estadoFinal(resultado)


# ESTADO INICIAL — coringa, decide para onde ir
def estadoInicial(linha, index, tokens, pilha):

    if index >= len(linha):
        return tokens, pilha

    ch = linha[index]

    if ch == ' ':
        return estadoInicial(linha, index + 1, tokens, pilha)

    if ch.isdigit():
        return estadoNumero(linha, index + 1, tokens, pilha, ch)

    if ch == '/' and index + 1 < len(linha) and linha[index + 1] == '/':
        return estadoOperador(linha, index + 2, tokens, pilha, '//')

    if ch in ('+', '-', '*', '/', '%', '^'):
        return estadoOperador(linha, index + 1, tokens, pilha, ch)

    if ch == '(':
        return estadoAbreParentese(linha, index + 1, tokens, pilha)

    if ch == ')':
        return estadoFechaParentese(linha, index + 1, tokens, pilha)

    if ch.isupper():
        return estadoRES(linha, index + 1, tokens, pilha, ch)

    raise ValueError(f"[pos {index}] Caractere inesperado: {ch!r}")


# ESTADO NÚMERO
def estadoNumero(linha, index, tokens, pilha, buffer):

    if index >= len(linha):
        return tokens + [{"tipo": "NUM", "valor": str(float(buffer))}], pilha

    ch = linha[index]

    if ch.isdigit():
        return estadoNumero(linha, index + 1, tokens, pilha, buffer + ch)

    if ch == '.':
        if '.' in buffer:
            raise ValueError(f"[pos {index}] Número com mais de um ponto decimal: {buffer!r}")
        return estadoNumero(linha, index + 1, tokens, pilha, buffer + ch)

    if ch == ' ':
        return estadoInicial(linha, index + 1, tokens + [{"tipo": "NUM", "valor": str(float(buffer))}], pilha)

    if ch == '/' and index + 1 < len(linha) and linha[index + 1] == '/':
        return estadoOperador(linha, index + 2, tokens + [{"tipo": "NUM", "valor": str(float(buffer))}], pilha, '//')

    if ch in ('+', '-', '*', '/', '%', '^'):
        return estadoOperador(linha, index + 1, tokens + [{"tipo": "NUM", "valor": str(float(buffer))}], pilha, ch)

    if ch == ')':
        return estadoFechaParentese(linha, index + 1, tokens + [{"tipo": "NUM", "valor": str(float(buffer))}], pilha)

    raise ValueError(f"[pos {index}] Caractere inesperado após número {buffer!r}: {ch!r}")


# ESTADO OPERADOR
def estadoOperador(linha, index, tokens, pilha, op):

    valores_consumidos = set()
    for t in tokens:
        if t["tipo"] == "OP":
            valores_consumidos.add(str(t["esquerdo"]))
            valores_consumidos.add(str(t["direito"]))

    operandos = [
        t for t in tokens
        if t["tipo"] in ("NUM", "SUBEXP") and str(t["valor"]) not in valores_consumidos
    ]

    if len(operandos) < 2:
        raise ValueError(
            f"[pos {index}] Operador {op!r} exige 2 operandos — "
            f"encontrado(s): {len(operandos)}"
        )

    esq = operandos[-2]["valor"]
    dir = operandos[-1]["valor"]

    novo_token = {"tipo": "OP", "valor": op, "esquerdo": esq, "direito": dir}

    if index >= len(linha):
        return tokens + [novo_token], pilha

    ch = linha[index]

    if ch == ' ':
        return estadoInicial(linha, index + 1, tokens + [novo_token], pilha)

    if ch == ')':
        return estadoFechaParentese(linha, index + 1, tokens + [novo_token], pilha)

    raise ValueError(f"[pos {index}] Caractere inesperado após operador {op!r}: {ch!r}")


# ESTADO RES — lê 'R','E','S' letra a letra; desvia para MEM se não for RES
def estadoRES(linha, index, tokens, pilha, buffer):

    if not buffer.startswith('R'):
        return estadoMEM(linha, index, tokens, pilha, buffer)

    if buffer == 'R':
        if index < len(linha) and linha[index] == 'E':
            return estadoRES(linha, index + 1, tokens, pilha, 'RE')
        return estadoMEM(linha, index, tokens, pilha, 'R')

    if buffer == 'RE':
        if index < len(linha) and linha[index] == 'S':
            return estadoRES(linha, index + 1, tokens, pilha, 'RES')
        return estadoMEM(linha, index, tokens, pilha, 'RE')

    # buffer == 'RES' — verifica se há letra colada
    if index < len(linha) and linha[index].isupper():
        return estadoMEM(linha, index, tokens, pilha, 'RES')

    if index < len(linha) and linha[index].islower():
        raise ValueError(f"[pos {index}] Nome inválido — letras minúsculas não permitidas")

    nums = [t for t in tokens if t["tipo"] == "NUM"]
    if not nums:
        raise ValueError(f"[pos {index}] RES sem índice numérico precedente")

    return estadoFechaEspecial(linha, index, tokens + [{"tipo": "RES"}], pilha)


# ESTADO MEM — acumula letras maiúsculas recursivamente até acabar o nome
def estadoMEM(linha, index, tokens, pilha, buffer):

    if index < len(linha) and linha[index].isupper():
        return estadoMEM(linha, index + 1, tokens, pilha, buffer + linha[index])

    if index < len(linha) and linha[index].islower():
        raise ValueError(f"[pos {index}] Nome inválido {buffer!r} — letras minúsculas não permitidas")

    nums = [t for t in tokens if t["tipo"] == "NUM"]
    valor = nums[-1]["valor"] if nums else "0.0"

    return estadoFechaEspecial(linha, index, tokens + [{"tipo": "MEM", "nome": buffer,}], pilha)


# ESTADO FECHA ESPECIAL — drena espaços e ')' após RES ou MEM e encerra
def estadoFechaEspecial(linha, index, tokens, pilha):

    if index >= len(linha):
        return tokens, pilha

    ch = linha[index]

    if ch == ' ':
        return estadoFechaEspecial(linha, index + 1, tokens, pilha)

    if ch == ')':
        if not pilha:
            raise ValueError(f"[pos {index}] ')' sem '(' correspondente")
        return estadoFechaEspecial(linha, index + 1, tokens, pilha[:-1])

    raise ValueError(f"[pos {index}] Token especial deve ser o último da linha")


# ESTADO ABRE PARÊNTESE
def estadoAbreParentese(linha, index, tokens, pilha):

    valores_consumidos = set()
    for t in tokens:
        if t["tipo"] == "OP":
            valores_consumidos.add(str(t["esquerdo"]))
            valores_consumidos.add(str(t["direito"]))

    fechados  = [t for t in tokens if t["tipo"] == "OP" or
                 (t["tipo"] in ("NUM", "SUBEXP") and str(t["valor"]) in valores_consumidos)]
    pendentes = [t for t in tokens if t["tipo"] in ("NUM", "SUBEXP") and
                 str(t["valor"]) not in valores_consumidos]

    novo_contexto = {"fechados": fechados, "pendentes": pendentes}

    return estadoInicial(linha, index, [], pilha + [novo_contexto])


# ESTADO FECHA PARÊNTESE
def estadoFechaParentese(linha, index, tokens, pilha):

    if not pilha:
        raise ValueError(f"[pos {index}] ')' sem '(' correspondente")

    ops_internos = [t for t in tokens if t["tipo"] == "OP"]
    if not ops_internos:
        raise ValueError(f"[pos {index}] Parêntese sem operador dentro")

    ctx = pilha[-1]

    tokens_pai = ctx["fechados"]
    for t in tokens:
        if t["tipo"] in ("NUM", "OP"):
            tokens_pai = tokens_pai + [t]
    tokens_pai = tokens_pai + ctx["pendentes"]

    ultimo_op  = ops_internos[-1]
    subexp_val = f"({ultimo_op['esquerdo']} {ultimo_op['valor']} {ultimo_op['direito']})"
    tokens_pai = tokens_pai + [{"tipo": "SUBEXP", "valor": subexp_val}]

    return estadoInicial(linha, index, tokens_pai, pilha[:-1])


# ESTADO FINAL — filtra tokens internos e grava JSON
def estadoFinal(resultado):
    saida = []
    for entrada in resultado:
        tokens_limpos = []
        for t in entrada["tokens"]:
            if t["tipo"] == "NUM":
                tokens_limpos.append({"tipo": "NUM", "valor": str(t["valor"])})
            elif t["tipo"] == "OP":
                tokens_limpos.append({"tipo": "OP", "valor": t["valor"]})
            elif t["tipo"] == "RES":
                tokens_limpos.append({"tipo": "RES"})
            elif t["tipo"] == "MEM":
                tokens_limpos.append({"tipo": "MEM", "nome": t["nome"]})
        saida.append({"linha": entrada["linha"], "tokens": tokens_limpos})

    with open("saida_fase1.txt", "w", encoding="utf-8") as f:
        json.dump(saida, f, indent=4, ensure_ascii=False)

    return saida
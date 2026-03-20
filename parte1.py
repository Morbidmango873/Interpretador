import json

# ESTADO GLOBAL
index  = 0
linha  = ""
tokens = []


# ENTRADA — chamada pela parte4 passando a lista de linhas
def parseExpressao(linhas):
    global index, linha, tokens

    resultado = []

    for num, raw in enumerate(linhas, 1):
        index  = 0
        linha  = raw.strip()
        tokens = []

        estadoInicial()

        resultado.append({"linha": num, "tokens": list(tokens)})

    return resultado


# ESTADO INICIAL — coringa, decide para onde ir
def estadoInicial():
    global index

    if index >= len(linha):
        return

    ch = linha[index]

    if ch == ' ':
        index += 1
        return estadoInicial()

    if ch.isdigit():
        index += 1
        return estadoNumero(ch)

    raise ValueError(f"[pos {index}] Caractere inesperado: {ch!r} — linha: {linha!r}")


# ESTADO NÚMERO
def estadoNumero(buffer):
    global index

    if index >= len(linha):
        _salvarNumero(buffer)
        return

    ch = linha[index]

    if ch.isdigit():
        index += 1
        return estadoNumero(buffer + ch)

    if ch == '.':
        if '.' in buffer:
            raise ValueError(f"[pos {index}] Número com mais de um ponto decimal: {buffer!r} — linha: {linha!r}")
        index += 1
        return estadoNumero(buffer + ch)

    if ch == ' ':
        _salvarNumero(buffer)
        index += 1
        return estadoInicial()

    raise ValueError(f"[pos {index}] Caractere inesperado após número {buffer!r}: {ch!r} — linha: {linha!r}")


# HELPER — valida e salva token NUM
def _salvarNumero(buffer):
    if buffer.endswith('.'):
        raise ValueError(f"[pos {index}] Número termina com ponto: {buffer!r} — linha: {linha!r}")
    tokens.append({"tipo": "NUM", "valor": float(buffer)})
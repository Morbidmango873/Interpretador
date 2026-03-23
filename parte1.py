'''

# Iremos passar todas as informações para a expressão para não depender de variaveris globais e se aproximar mais de uma maquina de estados

KEYWORD = ['RES']


def estadoNumero(linha): # Estado para lidar com Números
    # Damos trativa ao numero verificando se após ele tem um ponto caso tenha puxamos os número seguintes até um espaço em branco caso tenha outro . retorna erro
    # Caso o número seja correto adicionamos em nosso buffer.

    # Verifica se a linha no proximo index = a um numero
    # Verifica se o linha no proximo index = a um operador
    # Verifica se a linha no proximo index = a um (
    # Verifica se a linha no proximo index = estadoEspecial(Uma letra maiuscula)
    # trativa de erros do . e outros


def estadoParenteses(linha): # Estado para lidar com parêntese
    #verifica se é um parenteses abrindo ou fechando
    # caso seja abrindo armazena o contador de operandos em um buffer que é uma pilha para podermos lidar com paretentese encadeados e zera o contato atual
    # adicionam o parenteses abrindo a pilha de parenteses usaremos para verificar pariedade e ordem correta
    # caso seja um fechando pega o buffer e adiciona o ultimo ao contador global 

    # Verifica se a linha no proximo index = a um numero
    # Verifica se o linha no proximo index = a um operador
    # Verifica se a linha no proximo index = a um (
    # Verifica se a linha no proximo index = estadoEspecial(Uma letra maiuscula)
    

def estadoOperador(linha): #Estado para lidar com Operadores

    # Verifica se o operador é valido, usando nossa lista de operadores [+, -, *, /, //, %, ^]
    # verifica se o contador global de operando = 2 caso seja salva os 2 ultimos e operadorandos e o operador na ordem coreta
    # se for menor que retorna erro
     
    # Verifica se a linha no proximo index = a um numero
    # Verifica se o linha no proximo index = a um operador
    # Verifica se a linha no proximo index = a um (
    # Verifica se a linha no proximo index = estadoEspecial(Uma letra maiuscula)

def estadoEspeciais(linha): #Estado para lidar com MEM e RES

    # caso receba o res iremos armazenar o valor anterior a ele o o res então mandar para o final
    # RES é responsavel por quando executado receber o historico e pegar o index dele - o valor passado e retornar o resultado
    # MEM ou Qualquer conjunto ou LEtra maiuscula sozinha iremos salvar o valor passado anterior ou seja o ultimo na pilha de operando e salvar na memoria com aquele nome ou seja verificar tudo até achar um espaço ou algo que não seja um letra.
    # Caso não tenha sido passado nenhum valor ou seja só o conjunto vindo do estado inicial ele será salvo com 0.0

def parseExpressao(linha): #Inicio 
    print(linha)
    #Verifica se a linha no index 0 = a um numero
    #Verifica se o linha no index 0 = a um operador
    #Verifica se a linha no index 0 = a um (
    #Verifica se a linha no index 0 = estadoEspecial(Uma letra maiuscula)



# Especificações não posso usar REGEX. e tem que se

'''

import json

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
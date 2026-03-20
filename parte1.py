'''


#Variaveis globais
# Varia global indes atual.
# Contado de operandos
# Contador de parenteses
# Buffer operandos
# pilha de operandos

KEYWORD = ['RES']


def estadoNumero(linha): # Estado para lidar com Números
    # Damos trativa ao numero verificando se após ele tem um ponto caso tenha puxamos os número seguintes até um espaço em branco caso tenha outro . retorna erro
    # Caso o número seja correto adicionamos em nosso buffer.

    # Verifica se a linha no proximo index = a um numero
    # Verifica se o linha no proximo index = a um operador
    # Verifica se a linha no proximo index = a um (
    # Verifica se a linha no proximo index = estadoEspecial(Uma letra maiuscula)


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

# ESTADO GLOBAL
index        = 0
linha        = ""
tokens       = []
pilha        = []   # salva contextos ao abrir '('
resultado    = []   # acumula todas as linhas para o estado final


# ENTRADA — chamada pela parte4 passando a lista de linhas
def parseExpressao(linhas):
    global index, linha, tokens, pilha, resultado
    resultado = []

    for num, raw in enumerate(linhas, 1):
        index  = 0
        linha  = raw.strip()
        tokens = []
        pilha  = []

        estadoInicial()

        if pilha:
            raise ValueError(f"Linha {num}: {len(pilha)} parêntese(s) não fechado(s)")

        resultado.append({"linha": num, "tokens": list(tokens)})

    return estadoFinal()


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

    if ch == '/' and index + 1 < len(linha) and linha[index + 1] == '/':
        index += 2
        return estadoOperador('//')

    if ch in ('+', '-', '*', '/', '%', '^'):
        index += 1
        return estadoOperador(ch)

    if ch == '(':
        index += 1
        return estadoAbreParentese()

    if ch == ')':
        index += 1
        return estadoFechaParentese()

    raise ValueError(f"[pos {index}] Caractere inesperado: {ch!r}")


# ESTADO NÚMERO
def estadoNumero(buffer):
    global index

    if index >= len(linha):
        if buffer.endswith('.'):
            raise ValueError(f"[pos {index}] Número termina com ponto: {buffer!r}")
        tokens.append({"tipo": "NUM", "valor": str(float(buffer))})
        return

    ch = linha[index]

    if ch.isdigit():
        index += 1
        return estadoNumero(buffer + ch)

    if ch == '.':
        if '.' in buffer:
            raise ValueError(f"[pos {index}] Número com mais de um ponto decimal: {buffer!r}")
        index += 1
        return estadoNumero(buffer + ch)

    if ch == ' ':
        if buffer.endswith('.'):
            raise ValueError(f"[pos {index}] Número termina com ponto: {buffer!r}")
        tokens.append({"tipo": "NUM", "valor": str(float(buffer))})
        index += 1
        return estadoInicial()

    if ch == '/' and index + 1 < len(linha) and linha[index + 1] == '/':
        if buffer.endswith('.'):
            raise ValueError(f"[pos {index}] Número termina com ponto: {buffer!r}")
        tokens.append({"tipo": "NUM", "valor": str(float(buffer))})
        index += 2
        return estadoOperador('//')

    if ch in ('+', '-', '*', '/', '%', '^'):
        if buffer.endswith('.'):
            raise ValueError(f"[pos {index}] Número termina com ponto: {buffer!r}")
        tokens.append({"tipo": "NUM", "valor": str(float(buffer))})
        index += 1
        return estadoOperador(ch)

    if ch == ')':
        if buffer.endswith('.'):
            raise ValueError(f"[pos {index}] Número termina com ponto: {buffer!r}")
        tokens.append({"tipo": "NUM", "valor": str(float(buffer))})
        index += 1
        return estadoFechaParentese()

    raise ValueError(f"[pos {index}] Caractere inesperado após número {buffer!r}: {ch!r}")


# ESTADO OPERADOR
def estadoOperador(op):
    global index

    # operandos disponíveis: NUM e SUBEXP que ainda não foram consumidos
    # Um operando é "consumido" se seu valor aparece como esquerdo/direito de algum OP.
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

    # salva apenas o operador — sem esquerdo/direito no JSON final
    tokens.append({"tipo": "OP", "valor": op, "esquerdo": esq, "direito": dir})

    if index >= len(linha):
        return

    ch = linha[index]

    if ch == ' ':
        index += 1
        return estadoInicial()

    if ch == ')':
        index += 1
        return estadoFechaParentese()

    raise ValueError(f"[pos {index}] Caractere inesperado após operador {op!r}: {ch!r}")


# ESTADO ABRE PARÊNTESE
def estadoAbreParentese():
    global tokens

    # Separa o que já está resolvido no pai (tokens fechados) dos operandos
    # pendentes que ainda aguardam este grupo para formar um par com operador.
    # Os pendentes são os NUM/SUBEXP que ainda não foram consumidos por nenhum OP.
    valores_consumidos = set()
    for t in tokens:
        if t["tipo"] == "OP":
            valores_consumidos.add(str(t["esquerdo"]))
            valores_consumidos.add(str(t["direito"]))

    fechados  = [t for t in tokens if t["tipo"] in ("OP",) or
                 (t["tipo"] in ("NUM", "SUBEXP") and str(t["valor"]) in valores_consumidos)]
    pendentes = [t for t in tokens if t["tipo"] in ("NUM", "SUBEXP") and
                 str(t["valor"]) not in valores_consumidos]

    # empilha: tokens fechados + pendentes separados (pendentes vão APÓS o grupo)
    pilha.append({"fechados": fechados, "pendentes": pendentes})
    tokens = []

    return estadoInicial()


# ESTADO FECHA PARÊNTESE
def estadoFechaParentese():
    global tokens

    if not pilha:
        raise ValueError(f"[pos {index}] ')' sem '(' correspondente")

    ops_internos = [t for t in tokens if t["tipo"] == "OP"]
    if len(ops_internos) == 0:
        raise ValueError(f"[pos {index}] Parêntese sem operador dentro")

    tokens_internos = list(tokens)

    ctx = pilha.pop()

    # reconstrói o contexto do pai na ordem correta de execução:
    # 1. tokens já fechados do pai (OPs e operandos já consumidos)
    # 2. tokens do grupo interno (ordem de execução interna)
    # 3. operandos pendentes do pai que aguardavam este grupo
    tokens = ctx["fechados"]
    for t in tokens_internos:
        if t["tipo"] in ("NUM", "OP"):
            tokens.append(t)
    tokens.extend(ctx["pendentes"])

    # SUBEXP representa o resultado deste grupo para o estadoOperador do pai
    ultimo_op = ops_internos[-1]
    subexp_val = f"({ultimo_op['esquerdo']} {ultimo_op['valor']} {ultimo_op['direito']})"
    tokens.append({"tipo": "SUBEXP", "valor": subexp_val})

    return estadoInicial()


# ESTADO FINAL — retorna o resultado para a parte4
def estadoFinal():
    # filtra SUBEXP e esquerdo/direito do JSON entregue à parte4
    saida = []
    for entrada in resultado:
        tokens_limpos = []
        for t in entrada["tokens"]:
            if t["tipo"] == "NUM":
                tokens_limpos.append({"tipo": "NUM", "valor": str(t["valor"])})
            elif t["tipo"] == "OP":
                tokens_limpos.append({"tipo": "OP", "valor": t["valor"]})
        saida.append({"linha": entrada["linha"], "tokens": tokens_limpos})

    with open("saida_fase1.txt", "w", encoding="utf-8") as f:
        json.dump(saida, f, indent=4, ensure_ascii=False)

    return saida
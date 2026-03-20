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

    if ch.isupper():
        index += 1
        return estadoRES(ch)

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


# ESTADO RES — lê 'R','E','S' letra a letra
# Se em qualquer ponto vier letra diferente da esperada → passa para estadoMEM
# Se confirmar 'RES' completo → valida índice e encerra
def estadoRES(buffer):
    global index

    # primeira letra não é 'R' — nunca será RES, vai direto pro MEM
    if not buffer.startswith('R'):
        return estadoMEM(buffer)

    # ainda esperando completar 'RE'
    if buffer == 'R':
        if index < len(linha) and linha[index] == 'E':
            index += 1
            return estadoRES('RE')
        # não é 'E' — não é RES, passa para MEM continuar acumulando
        return estadoMEM('R')

    # ainda esperando completar 'RES'
    if buffer == 'RE':
        if index < len(linha) and linha[index] == 'S':
            index += 1
            return estadoRES('RES')
        # não é 'S' — não é RES, passa para MEM continuar acumulando
        return estadoMEM('RE')

    # buffer == 'RES' — keyword confirmada
    # verifica se tem letra colada (ex: RESX → é nome MEM, não keyword)
    if index < len(linha) and linha[index].isupper():
        return estadoMEM('RES')

    if index < len(linha) and linha[index].islower():
        raise ValueError(f"[pos {index}] Nome inválido — letras minúsculas não permitidas")

    # RES válido — valida que existe NUM antes (o índice do histórico)
    nums = [t for t in tokens if t["tipo"] == "NUM"]
    if not nums:
        raise ValueError(f"[pos {index}] RES sem índice numérico precedente")

    tokens.append({"tipo": "RES"})
    return estadoFechaEspecial()


# ESTADO MEM — acumula letras maiúsculas recursivamente até acabar o nome
def estadoMEM(buffer):
    global index

    # continua acumulando enquanto vier letra maiúscula
    if index < len(linha) and linha[index].isupper():
        ch = linha[index]
        index += 1
        return estadoMEM(buffer + ch)

    # letra minúscula colada é inválida
    if index < len(linha) and linha[index].islower():
        raise ValueError(f"[pos {index}] Nome inválido {buffer!r} — letras minúsculas não permitidas")

    # nome completo — pega último NUM como valor ou usa 0.0
    nums = [t for t in tokens if t["tipo"] == "NUM"]
    valor = nums[-1]["valor"] if nums else "0.0"

    tokens.append({"tipo": "MEM", "nome": buffer, "valor": valor})
    return estadoFechaEspecial()


# ESTADO FECHA ESPECIAL — drena espaços e ')' após RES ou MEM e encerra
def estadoFechaEspecial():
    global index

    if index >= len(linha):
        return

    ch = linha[index]

    if ch == ' ':
        index += 1
        return estadoFechaEspecial()

    if ch == ')':
        if not pilha:
            raise ValueError(f"[pos {index}] ')' sem '(' correspondente")
        pilha.pop()
        index += 1
        return estadoFechaEspecial()

    raise ValueError(f"[pos {index}] Token especial deve ser o último da linha")


# ESTADO ABRE PARÊNTESE
def estadoAbreParentese():
    global tokens

    valores_consumidos = set()
    for t in tokens:
        if t["tipo"] == "OP":
            valores_consumidos.add(str(t["esquerdo"]))
            valores_consumidos.add(str(t["direito"]))

    fechados  = [t for t in tokens if t["tipo"] in ("OP",) or
                 (t["tipo"] in ("NUM", "SUBEXP") and str(t["valor"]) in valores_consumidos)]
    pendentes = [t for t in tokens if t["tipo"] in ("NUM", "SUBEXP") and
                 str(t["valor"]) not in valores_consumidos]

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

    tokens = ctx["fechados"]
    for t in tokens_internos:
        if t["tipo"] in ("NUM", "OP"):
            tokens.append(t)
    tokens.extend(ctx["pendentes"])

    ultimo_op = ops_internos[-1]
    subexp_val = f"({ultimo_op['esquerdo']} {ultimo_op['valor']} {ultimo_op['direito']})"
    tokens.append({"tipo": "SUBEXP", "valor": subexp_val})

    return estadoInicial()


# ESTADO FINAL — retorna resultado para a parte4 e grava JSON
def estadoFinal():
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
                tokens_limpos.append({"tipo": "MEM", "nome": t["nome"], "valor": t["valor"]})
        saida.append({"linha": entrada["linha"], "tokens": tokens_limpos})

    with open("saida_fase1.txt", "w", encoding="utf-8") as f:
        json.dump(saida, f, indent=4, ensure_ascii=False)

    return saida
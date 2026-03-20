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
# parte1.py
import json

OPERADORES = {"+", "-", "*", "/", "//", "%", "^"}
KEYWORDS = {"RES"}


def erro(msg, linha):
    raise Exception(f"[Linha {linha}] {msg}")


def estadoNumero(token, linha):
    float(token)
    return {"tipo": "NUM", "valor": token}


def estadoOperador(token, pilha, linha):
    if token not in OPERADORES:
        erro(f"Operador inválido: {token}", linha)

    if len(pilha) < 2:
        erro("Operador sem operandos suficientes", linha)

    pilha.pop()
    pilha.pop()
    pilha.append("RESULT")

    return {"tipo": "OP", "valor": token}


def estadoIdentificador(token, linha):
    if token.isupper():
        return {"tipo": "MEM", "valor": token}
    else:
        erro(f"Identificador inválido: {token}", linha)


def estadoEspecial(tokens, i, linha):
    if tokens[i] != "(":
        erro("Erro interno em especial", linha)

    if i + 2 < len(tokens) and tokens[i + 2] == ")":
        nome = tokens[i + 1]
        if not nome.isupper():
            erro(f"Identificador inválido em leitura de memória: {nome}", linha)
        return {"tipo": "MEM", "valor": nome}, i + 3

    if i + 3 >= len(tokens):
        erro("Expressão especial incompleta", linha)

    valor = tokens[i + 1]
    comando = tokens[i + 2]
    fechamento = tokens[i + 3]

    if fechamento != ")":
        erro("Parêntese não fechado em expressão especial", linha)

    if comando == "RES":
        if not valor.isdigit():
            erro("RES requer número inteiro", linha)
        return {"tipo": "RES", "valor": int(valor)}, i + 4

    elif comando.isupper():
        return {"tipo": "STORE", "mem": comando, "valor": valor}, i + 4

    else:
        erro("Expressão especial inválida", linha)


# ALTERADO — recebe linhas como parâmetro em vez de ler o arquivo diretamente
def parseExpressao(linhas):
    resultado = []

    for idx, linha in enumerate(linhas):
        tokens = linha.replace("(", " ( ").replace(")", " ) ").split()

        pilha = []
        contexto = []
        tokens_saida = []

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token == "(":
                if i + 2 < len(tokens) and tokens[i + 2] == ")":
                    t, i = estadoEspecial(tokens, i, idx + 1)
                    tokens_saida.append(t)
                    if contexto:
                        contexto[-1]["operandos"] += 1
                    pilha.append("RESULT")
                    continue

                elif i + 2 < len(tokens) and (tokens[i + 2] == "RES" or tokens[i + 2].isupper()):
                    t, i = estadoEspecial(tokens, i, idx + 1)
                    tokens_saida.append(t)
                    if contexto:
                        contexto[-1]["operandos"] += 1
                    pilha.append("RESULT")
                    continue

                contexto.append({"operandos": 0, "operadores": 0})

            elif token == ")":
                if not contexto:
                    erro("Parêntese fechado sem abertura", idx + 1)

                atual = contexto.pop()

                if atual["operandos"] != atual["operadores"] + 1:
                    erro(f"Expressão inválida dentro de parênteses: {atual}", idx + 1)

                if contexto:
                    contexto[-1]["operandos"] += 1

                pilha.append("RESULT")

            elif token.lstrip('-').replace('.', '', 1).isdigit() and token.count('-') <= 1:
                t = estadoNumero(token, idx + 1)
                tokens_saida.append(t)
                pilha.append(t)
                if contexto:
                    contexto[-1]["operandos"] += 1

            elif token in OPERADORES:
                t = estadoOperador(token, pilha, idx + 1)
                tokens_saida.append(t)
                if contexto:
                    contexto[-1]["operadores"] += 1

            elif token.isalpha():
                t = estadoIdentificador(token, idx + 1)
                tokens_saida.append(t)
                pilha.append(t)
                if contexto:
                    contexto[-1]["operandos"] += 1

            else:
                erro(f"Token inválido: {token}", idx + 1)

            i += 1

        if contexto:
            erro("Parênteses não fechados", idx + 1)

        resultado.append({
            "linha": idx + 1,
            "tokens": tokens_saida
        })

    return resultado
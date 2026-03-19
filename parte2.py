# parte2.py
from decimal import Decimal, ROUND_HALF_UP


def formatarResultado(valor):
    if valor is None:
        return None
    return float(Decimal(valor).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP))


def aplicarOperador(a, b, op):
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    elif op == "/":
        return a / b
    elif op == "//":
        return int(a) // int(b)
    elif op == "%":
        return int(a) % int(b)
    elif op == "^":
        return a ** b
    else:
        raise Exception(f"Operador desconhecido: {op}")


def executarExpressao(dados):
    memoria = {}
    historico = []
    resultados = []

    for linha in dados:
        pilha = []

        for token in linha["tokens"]:
            tipo = token["tipo"]

            if tipo == "NUM":
                pilha.append(float(token["valor"]))

            elif tipo == "MEM":
                nome = token["valor"]
                valor = memoria.get(nome, None)
                pilha.append(valor)

            elif tipo == "OP":
                if len(pilha) < 2:
                    raise Exception(f"[Linha {linha['linha']}] Operandos insuficientes")

                b = pilha.pop()
                a = pilha.pop()

                if a is None or b is None:
                    pilha.append(None)
                else:
                    resultado = aplicarOperador(a, b, token["valor"])
                    pilha.append(resultado)

            elif tipo == "STORE":
                valor = float(token["valor"])
                memoria[token["mem"]] = valor

            elif tipo == "RES":
                n = token["valor"]
                indice_atual = linha["linha"] - 1
                indice_desejado = indice_atual - n

                if indice_desejado < 0:
                    raise Exception(f"[Linha {linha['linha']}] RES referencia inválida")

                valor = historico[indice_desejado]
                pilha.append(valor)

        if len(pilha) == 1:
            resultado_final = pilha.pop()
        elif len(pilha) == 0:
            resultado_final = None
        else:
            raise Exception(f"[Linha {linha['linha']}] Pilha inválida")

        historico.append(resultado_final)

        resultados.append({
            "linha": linha["linha"],
            "tokens": linha["tokens"],
            "resultado": formatarResultado(resultado_final)
        })

    return resultados
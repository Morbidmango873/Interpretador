# parte2.py
import struct


def formatarResultado(valor):
    if valor is None:
        return None
    packed = struct.pack("d", float(valor))
    return struct.unpack("d", packed)[0]


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
    memoria  = {}
    historico = []
    resultados = []

    for linha in dados:
        pilha = []
        tem_store = False  # NOVO — flag para linhas que são apenas STORE

        for token in linha["tokens"]:
            tipo = token["tipo"]

            if tipo == "NUM":
                pilha.append(float(token["valor"]))

            elif tipo == "MEM":
                nome  = token["valor"]
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
                    pilha.append(aplicarOperador(a, b, token["valor"]))

            elif tipo == "STORE":
                # armazena na memória
                memoria[token["mem"]] = float(token["valor"])
                tem_store = True  # NOVO — marca que essa linha é um STORE

            elif tipo == "RES":
                n = token["valor"]

                # ALTERADO — usa len(historico) como base, não indice_atual
                # historico só tem as linhas já processadas antes desta
                indice_desejado = len(historico) - n

                if indice_desejado < 0:
                    raise Exception(
                        f"[Linha {linha['linha']}] RES({n}) inválido: "
                        f"só existem {len(historico)} linha(s) anteriores"
                    )

                valor = historico[indice_desejado]

                if valor is None:
                    raise Exception(
                        f"[Linha {linha['linha']}] RES({n}) aponta para "
                        f"linha sem resultado numérico"
                    )

                pilha.append(valor)

            elif tipo in ("LPAREN", "RPAREN"):
                pass  # agrupamento — ignorado na execução

        # ── resultado final da linha ──────────────────────────
        if len(pilha) == 1:
            resultado_final = pilha.pop()
        elif len(pilha) == 0:
            resultado_final = None
        else:
            raise Exception(f"[Linha {linha['linha']}] Pilha inválida ao final")

        # ALTERADO — linhas STORE não entram no histórico com None
        # elas simplesmente não produzem resultado numérico
        if not tem_store:
            historico.append(resultado_final)
        # se for STORE puro, não adiciona nada ao histórico
        # para que os índices do RES não sejam deslocados

        resultados.append({
            "linha": linha["linha"],
            "tokens": linha["tokens"],
            "resultado": formatarResultado(resultado_final)
        })

    return resultados
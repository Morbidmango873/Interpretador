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
    memoria   = {}
    historico = []
    resultados = []

    for linha in dados:
        pilha    = []
        eh_store = False
        eh_res   = False

        for token in linha["tokens"]:
            tipo = token["tipo"]

            if tipo == "NUM":
                pilha.append(float(token["valor"]))

            elif tipo == "OP":
                if len(pilha) < 2:
                    raise Exception(f"[Linha {linha['linha']}] Operandos insuficientes")
                b = pilha.pop()
                a = pilha.pop()
                if a is None or b is None:
                    pilha.append(None)
                else:
                    pilha.append(aplicarOperador(a, b, token["valor"]))

            elif tipo == "MEM":
                # salva na memória usando 'nome' como chave e 'valor' como conteúdo
                memoria[token["nome"]] = float(token["valor"])
                eh_store = True

            elif tipo == "RES":
                # o índice é o último NUM empilhado (já está na pilha)
                if not pilha:
                    raise Exception(f"[Linha {linha['linha']}] RES sem índice na pilha")
                n = int(pilha.pop())

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
                eh_res = True

        # resultado final da linha
        if len(pilha) == 1:
            resultado_final = pilha.pop()
        elif len(pilha) == 0:
            resultado_final = None
        else:
            raise Exception(f"[Linha {linha['linha']}] Pilha inválida ao final: {pilha}")

        # MEM puro não entra no histórico (não produz resultado numérico)
        if not eh_store:
            historico.append(resultado_final)

        resultados.append({
            "linha"    : linha["linha"],
            "tokens"   : linha["tokens"],
            "resultado": formatarResultado(resultado_final)
        })

    return resultados
import struct

# Nome do Grupo: Francisco Hauch Cardoso, ID: Morbidmango873

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
        if not float(b).is_integer() or b <= 0:
            raise Exception("Potenciação exige expoente inteiro positivo")
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
                nome = token["nome"]

                if pilha:
                    # STORE (salva o valor da pilha e mantém na pilha)
                    valor = pilha[-1]          # lê o topo sem remover
                    memoria[nome] = valor
                    eh_store = True
                    # NÃO faz pop — o valor permanece na pilha
                    # como resultado final da linha
                else:
                    # GET (recupera da memória)
                    valor = memoria.get(nome, 0.0)
                    pilha.append(valor)

            elif tipo == "RES":
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

        # todas as linhas entram no histórico, inclusive MEM store
        historico.append(resultado_final)

        resultados.append({
            "linha"    : linha["linha"],
            "tokens"   : linha["tokens"],
            "resultado": formatarResultado(resultado_final)
        })

    return resultados

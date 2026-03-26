import math
import struct

# Nome do Grupo: Francisco Hauch Cardoso, ID: Morbidmango873

ROUNDING_MODE_IEEE = "nearest_even"


def classificarFloat64(valor):
    valor = float(valor)

    if math.isnan(valor):
        return "nan"
    if math.isinf(valor):
        return "infinito"
    if valor == 0.0:
        return "zero"

    bits = struct.unpack(">Q", struct.pack(">d", valor))[0]
    expoente = (bits >> 52) & 0x7FF
    fracao = bits & ((1 << 52) - 1)

    if expoente == 0 and fracao != 0:
        return "subnormal"

    return "normal"


def formatarResultado(valor):
    if valor is None:
        return None

    packed = struct.pack("d", float(valor))
    return struct.unpack("d", packed)[0]


def sinalProduto(a, b):
    return math.copysign(1.0, a) * math.copysign(1.0, b)


def dividirIEEE754(a, b):
    a = float(a)
    b = float(b)

    if math.isnan(a) or math.isnan(b):
        return math.nan

    if b == 0.0:
        if a == 0.0:
            return math.nan
        return math.copysign(math.inf, sinalProduto(a, b))

    return a / b


def arredondarIntegralIEEE754(valor, modo=ROUNDING_MODE_IEEE):
    valor = float(valor)

    if math.isnan(valor) or math.isinf(valor):
        return valor

    if modo == "nearest_even":
        return float(round(valor))
    if modo == "toward_zero":
        return float(math.trunc(valor))
    if modo == "toward_positive":
        return float(math.ceil(valor))
    if modo == "toward_negative":
        return float(math.floor(valor))

    raise ValueError(f"Modo de arredondamento invalido: {modo}")


def divisaoIntegralIEEE754(a, b, modo=ROUNDING_MODE_IEEE):
    quociente = dividirIEEE754(a, b)

    if math.isnan(quociente) or math.isinf(quociente):
        return quociente

    return arredondarIntegralIEEE754(quociente, modo)


def restoIEEE754(a, b, modo=ROUNDING_MODE_IEEE):
    a = float(a)
    b = float(b)

    if math.isnan(a) or math.isnan(b):
        return math.nan
    if b == 0.0:
        return math.nan
    if math.isinf(a):
        return math.nan
    if math.isinf(b):
        return a

    quociente = arredondarIntegralIEEE754(dividirIEEE754(a, b), modo)

    if math.isnan(quociente) or math.isinf(quociente):
        return math.nan

    resto = a - (quociente * b)
    if resto == 0.0:
        return math.copysign(0.0, a)

    return resto


def aplicarOperador(a, b, op):
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    elif op == "/":
        return dividirIEEE754(a, b)
    elif op == "//":
        return divisaoIntegralIEEE754(a, b)
    elif op == "%":
        return restoIEEE754(a, b)
    elif op == "^":
        if not float(b).is_integer() or b <= 0:
            raise Exception("PotenciaÃ§Ã£o exige expoente inteiro positivo")
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

            elif tipo == "OP":
                if len(pilha) < 2:
                    raise Exception(f"[Linha {linha['linha']}] Operandos insuficientes")

                b = pilha.pop()
                a = pilha.pop()

                if a is None or b is None:
                    pilha.append(None)
                else:
                    resultado = aplicarOperador(a, b, token["valor"])
                    classificarFloat64(resultado)
                    pilha.append(resultado)

            elif tipo == "MEM":
                nome = token["nome"]

                if pilha:
                    valor = pilha[-1]
                    memoria[nome] = valor
                else:
                    valor = memoria.get(nome, 0.0)
                    pilha.append(valor)

            elif tipo == "RES":
                if not pilha:
                    raise Exception(f"[Linha {linha['linha']}] RES sem Ã­ndice na pilha")

                n = int(pilha.pop())
                indice_desejado = len(historico) - n

                if indice_desejado < 0:
                    raise Exception(
                        f"[Linha {linha['linha']}] RES({n}) invÃ¡lido: "
                        f"sÃ³ existem {len(historico)} linha(s) anteriores"
                    )

                valor = historico[indice_desejado]
                if valor is None:
                    raise Exception(
                        f"[Linha {linha['linha']}] RES({n}) aponta para "
                        f"linha sem resultado numÃ©rico"
                    )

                pilha.append(valor)

        if len(pilha) == 1:
            resultado_final = pilha.pop()
        elif len(pilha) == 0:
            resultado_final = None
        else:
            raise Exception(f"[Linha {linha['linha']}] Pilha invÃ¡lida ao final: {pilha}")

        historico.append(resultado_final)

        resultados.append({
            "linha": linha["linha"],
            "tokens": linha["tokens"],
            "resultado": formatarResultado(resultado_final)
        })

    return resultados

import json
import math


#Nome do Grupo: Francisco Hauch Cardoso, ID: Morbidmango873

# CONFIGURAÇÃO

MAX_EXPRESSOES = 10
LED_BASE = 0xFF200000
ROUNDING_MODE_IEEE = "nearest_even"
FPSCR_RMODE_BITS = {
    "nearest_even": 0x00000000,
    "toward_positive": 0x00400000,
    "toward_negative": 0x00800000,
    "toward_zero": 0x00C00000,
}


def literal_double_asm(valor: float) -> str:
    valor = float(valor)

    if math.isnan(valor):
        return "nan"
    if math.isinf(valor):
        return "-inf" if valor < 0 else "inf"

    return repr(valor)


# ESTRUTURAS PADRÃO DO ASSEMBLY

def estrutura_cabecalho_arquivo(total: int) -> str:
    return (
        f"@ ============================================================\n"
        f"@ Gerado automaticamente — {total} expressao(oes)\n"
        f"@ Arquitetura: ARMv7 | VFP double (registradores D)\n"
        f"@ ============================================================\n\n"
    )

def estrutura_separador(linha_atual: int, linha_prox: int) -> str:
    return (
        f"\n@ ------------------------------------------------------------\n"
        f"@ FIM LINHA {linha_atual} | INICIO LINHA {linha_prox}\n"
        f"@ ------------------------------------------------------------\n\n"
    )

def estrutura_secao_data(constantes: list[tuple[str, float]],
                          results: list[str],
                          mems: set[str] = None) -> str:
    """
    .section .data com:
    - constantes numéricas como .double
    - variáveis result como .double
    - variáveis MEM globais como .double
    """
    linhas = [".section .data\n"]

    linhas.append("    @ --- Constantes numericas ---\n")
    linhas.append("    cst_zero_f64: .double 0.0\n")
    linhas.append("    cst_max_s32_f64: .double 2147483647.0\n")
    linhas.append("    cst_min_s32_f64: .double -2147483648.0\n")

    if constantes:
        for nome, valor in constantes:
            linhas.append(f"    {nome}: .double {literal_double_asm(valor)}\n")

    if results:
        linhas.append("\n    @ --- Resultados ---\n")
        for nome in results:
            linhas.append(f"    {nome}: .double 0.0\n")

    if mems:
        linhas.append("\n    @ --- Variaveis MEM globais ---\n")
        for nome_mem in sorted(mems):
            linhas.append(f"    mem_{nome_mem}: .double 0.0\n")

    return "".join(linhas)

def estrutura_bloco_dummy() -> str:
    """Absorve erro de primeira execução do CPUlator."""
    return (
        f"@ --- DUMMY: absorve erro de primeira execucao ---\n"
        f"    MOV r0, #0\n"
        f"    MOV r1, #0\n"
        f"@ --- FIM DUMMY ---\n\n"
    )

def estrutura_inicio_text() -> str:
    bits_rmode = FPSCR_RMODE_BITS[ROUNDING_MODE_IEEE]
    trecho_rmode = ""

    if bits_rmode:
        trecho_rmode = f"    ORR  r0, r0, #{bits_rmode:#010x}\n"

    return (
        f"\n.section .text\n"
        f".global _start\n\n"
        f"_start:\n"
        f"    @ Configura FPSCR: preserva subnormais, NaN e modo de arredondamento IEEE\n"
        f"    VMRS r0, FPSCR\n"
        f"    BIC  r0, r0, #0x03C00000\n"
        f"{trecho_rmode}"
        f"    VMSR FPSCR, r0\n\n"
    )

def estrutura_label(label: str) -> str:
    return f"\n{label}:\n"

def estrutura_vldr(reg_d: str, variavel: str) -> str:
    """Carrega um .double da memória em um registrador D."""
    return (
        f"    LDR r0, ={variavel}\n"
        f"    VLDR {reg_d}, [r0]\n"
    )

def estrutura_vstr(reg_d: str, variavel: str) -> str:
    """Salva um registrador D em uma variável .double na memória."""
    return (
        f"    LDR r0, ={variavel}\n"
        f"    VSTR {reg_d}, [r0]\n"
    )

def estrutura_exit() -> str:
    return (
        f"\n@ --- Encerramento do programa ---\n"
        f"    BL apagar_leds\n"
        f"    MOV r7, #1\n"
        f"    MOV r0, #0\n"
        f"    SWI 0\n"
    )

def estrutura_exibir_led_resultado(variavel: str) -> str:
    """
    Mostra nos LEDs os 64 bits do double salvo em memoria.
    Exibe primeiro 32 bits, apaga, depois exibe os outros 32 bits.
    """
    return (
        f"    @ EXIBIR {variavel} NOS LEDS\n"
        f"    LDR r0, ={variavel}\n"
        f"    VLDR d0, [r0]\n"
        f"    VMOV r6, r7, d0\n"
        f"    BL apagar_leds\n"
        f"    MOV r0, r6\n"
        f"    BL exibir_leds_32\n"
        f"    BL apagar_leds\n"
        f"    BL marcar_separador_led\n"
        f"    BL apagar_leds\n"
        f"    MOV r0, r7\n"
        f"    BL exibir_leds_32\n"
        f"    BL apagar_leds\n"
    )

def estrutura_rotinas_leds() -> str:
    return (
        f"\n@ --- Rotinas de exibicao nos LEDs do CPUlator ---\n"
        f"apagar_leds:\n"
        f"    LDR r1, ={LED_BASE}\n"
        f"    MOV r0, #0\n"
        f"    STR r0, [r1]\n"
        f"    BX lr\n\n"
        f"marcar_separador_led:\n"
        f"    LDR r1, ={LED_BASE}\n"
        f"    MOV r0, #1              @ acende 1 LED como separador\n"
        f"    STR r0, [r1]\n"
        f"    BX lr\n\n"
        f"exibir_leds_32:\n"
        f"    LDR r1, ={LED_BASE}\n"
        f"    STR r0, [r1]\n"
        f"    BX lr\n"
    )


# OPERAÇÕES VFP SOBRE A PILHA NATIVA (VPUSH/VPOP)
# Padrão: VPOP d1 (b), VPOP d0 (a), OP d0 d0 d1, VPUSH d0

def estrutura_op_soma(label: str, step: int) -> str:
    return (
        f"    @ SOMA (step {step})\n"
        f"    VPOP  {{d1}}            @ b\n"
        f"    VPOP  {{d0}}            @ a\n"
        f"    VADD.F64 d0, d0, d1   @ d0 = a + b\n"
        f"    VPUSH {{d0}}\n"
    )

def estrutura_op_subtracao(label: str, step: int) -> str:
    return (
        f"    @ SUBTRACAO (step {step})\n"
        f"    VPOP  {{d1}}            @ b\n"
        f"    VPOP  {{d0}}            @ a\n"
        f"    VSUB.F64 d0, d0, d1   @ d0 = a - b\n"
        f"    VPUSH {{d0}}\n"
    )

def estrutura_op_multiplicacao(label: str, step: int) -> str:
    return (
        f"    @ MULTIPLICACAO (step {step})\n"
        f"    VPOP  {{d1}}            @ b\n"
        f"    VPOP  {{d0}}            @ a\n"
        f"    VMUL.F64 d0, d0, d1   @ d0 = a * b\n"
        f"    VPUSH {{d0}}\n"
    )

def estrutura_op_divisao(label: str, step: int) -> str:
    return (
        f"    @ DIVISAO (step {step})\n"
        f"    VPOP  {{d1}}            @ b (divisor)\n"
        f"    VPOP  {{d0}}            @ a (dividendo)\n"
        f"    VDIV.F64 d0, d0, d1   @ d0 = a / b (NaN/Inf/subnormais preservados pelo VFP)\n"
        f"    VPUSH {{d0}}\n"
    )


def estrutura_arredondar_quociente(quociente: str,
                                   destino_int: str,
                                   destino_double: str,
                                   label: str,
                                   step: int) -> str:
    lbl_fim = f"round_q_done_{label}_{step}_{destino_int.replace('s', '')}"

    if ROUNDING_MODE_IEEE == "nearest_even":
        return (
            f"    VCVTR.S32.F64 {destino_int}, {quociente}\n"
            f"    VCVT.F64.S32 {destino_double}, {destino_int}\n"
        )

    if ROUNDING_MODE_IEEE == "toward_zero":
        return (
            f"    VCVT.S32.F64 {destino_int}, {quociente}\n"
            f"    VCVT.F64.S32 {destino_double}, {destino_int}\n"
        )

    if ROUNDING_MODE_IEEE == "toward_negative":
        return (
            f"    VCVT.S32.F64 {destino_int}, {quociente}\n"
            f"    VCVT.F64.S32 {destino_double}, {destino_int}\n"
            f"    VCMP.F64 {quociente}, {destino_double}\n"
            f"    VMRS APSR_nzcv, FPSCR\n"
            f"    BEQ  {lbl_fim}\n"
            f"    LDR r0, =cst_zero_f64\n"
            f"    VLDR d6, [r0]\n"
            f"    VCMP.F64 {quociente}, d6\n"
            f"    VMRS APSR_nzcv, FPSCR\n"
            f"    BGE  {lbl_fim}\n"
            f"    VMOV r1, {destino_int}\n"
            f"    SUB  r1, r1, #1\n"
            f"    VMOV {destino_int}, r1\n"
            f"    VCVT.F64.S32 {destino_double}, {destino_int}\n"
            f"{lbl_fim}:\n"
        )

    if ROUNDING_MODE_IEEE == "toward_positive":
        return (
            f"    VCVT.S32.F64 {destino_int}, {quociente}\n"
            f"    VCVT.F64.S32 {destino_double}, {destino_int}\n"
            f"    VCMP.F64 {quociente}, {destino_double}\n"
            f"    VMRS APSR_nzcv, FPSCR\n"
            f"    BEQ  {lbl_fim}\n"
            f"    LDR r0, =cst_zero_f64\n"
            f"    VLDR d6, [r0]\n"
            f"    VCMP.F64 {quociente}, d6\n"
            f"    VMRS APSR_nzcv, FPSCR\n"
            f"    BLE  {lbl_fim}\n"
            f"    VMOV r1, {destino_int}\n"
            f"    ADD  r1, r1, #1\n"
            f"    VMOV {destino_int}, r1\n"
            f"    VCVT.F64.S32 {destino_double}, {destino_int}\n"
            f"{lbl_fim}:\n"
        )

    raise ValueError(f"Modo de arredondamento nao suportado: {ROUNDING_MODE_IEEE}")

def estrutura_op_divisao_inteira(label: str, step: int) -> str:
    """Divisão inteira: divide, converte para int (trunca) e volta para double."""
    return (
        f"    @ DIVISAO INTEIRA // (step {step})\n"
        f"    VPOP  {{d1}}            @ b\n"
        f"    VPOP  {{d0}}            @ a\n"
        f"    VDIV.F64 d0, d0, d1   @ d0 = a / b\n"
        f"{estrutura_arredondar_quociente('d0', 's0', 'd0', label, step)}"
        f"    VPUSH {{d0}}\n"
    )

def estrutura_op_resto(label: str, step: int) -> str:
    """Resto: a - trunc(a/b)*b"""
    return (
        f"    @ RESTO % (step {step})\n"
        f"    VPOP  {{d1}}            @ b\n"
        f"    VPOP  {{d0}}            @ a\n"
        f"    VDIV.F64 d2, d0, d1   @ d2 = a / b\n"
        f"{estrutura_arredondar_quociente('d2', 's4', 'd2', label, step)}"
        f"    VMUL.F64 d2, d2, d1   @ d2 = round(a/b) * b\n"
        f"    VSUB.F64 d0, d0, d2   @ d0 = a - d2\n"
        f"    VPUSH {{d0}}\n"
    )

def estrutura_op_potencia(label: str, step: int) -> str:
    """
    Potência por multiplicação repetida.
    Aceita apenas expoente inteiro positivo.
    Loop: decrementa r1 e multiplica d0 por d2 a cada passo.
    """
    lbl_loop = f"pow_loop_{label}_{step}"
    lbl_fim  = f"pow_fim_{label}_{step}"
    lbl_invalido = f"pow_invalido_{label}_{step}"
    return (
        f"    @ POTENCIA ^ (step {step})\n"
        f"    VPOP  {{d1}}            @ expoente\n"
        f"    VPOP  {{d0}}            @ base\n"
        f"    @ valida se o expoente e inteiro\n"
        f"    VCVT.S32.F64 s2, d1\n"
        f"    VCVT.F64.S32 d3, s2\n"
        f"    VCMP.F64 d1, d3\n"
        f"    VMRS APSR_nzcv, FPSCR\n"
        f"    BNE  {lbl_invalido}\n"
        f"    VMOV r1, s2            @ r1 = expoente inteiro\n"
        f"    @ aceita apenas expoente positivo\n"
        f"    CMP  r1, #1\n"
        f"    BLT  {lbl_invalido}\n"
        f"    B    {lbl_loop}\n"
        f"{lbl_loop}:\n"
        f"    VMOV.F64 d2, d0        @ d2 = base (acumulador)\n"
        f"    SUB  r1, r1, #1\n"
        f"pow_mul_{label}_{step}:\n"
        f"    CMP  r1, #0\n"
        f"    BEQ  {lbl_fim}\n"
        f"    VMUL.F64 d2, d2, d0   @ d2 *= base\n"
        f"    SUB  r1, r1, #1\n"
        f"    B    pow_mul_{label}_{step}\n"
        f"{lbl_invalido}:\n"
        f"    LDR r0, =cst_zero_f64\n"
        f"    VLDR d2, [r0]\n"
        f"{lbl_fim}:\n"
        f"    VMOV.F64 d0, d2\n"
        f"    VPUSH {{d0}}\n"
    )


OPERADORES_PILHA = {
    "+":  estrutura_op_soma,
    "-":  estrutura_op_subtracao,
    "*":  estrutura_op_multiplicacao,
    "/":  estrutura_op_divisao,
    "//": estrutura_op_divisao_inteira,
    "%":  estrutura_op_resto,
    "^":  estrutura_op_potencia,
}
# GERADOR RPN

def gerar_bloco_rpn(linha: int, tokens: list[dict], todas_linhas: list[int]) -> tuple[list, list, str] | None:
    label   = f"linha{linha}"
    rpn_str = " ".join(t.get("valor", t.get("tipo","")) for t in tokens)

    for token in tokens:
        if token["tipo"] == "OP" and token["valor"] not in OPERADORES_PILHA:
            print(f"[Linha {linha}] Operador '{token['valor']}' não implementado.")
            return None

    constantes = []
    results    = [f"result_{label}"]
    codigo     = f"@ --- Linha {linha} | RPN: {rpn_str} ---\n"
    step       = 0
    cst_idx    = 0
    profundidade_pilha = 0

    for idx, token in enumerate(tokens):
        tipo  = token["tipo"]
        valor = token.get("valor", "")

        if tipo == "NUM":
            val      = float(valor)
            cst_nome = f"cst_{label}_{cst_idx}"
            constantes.append((cst_nome, val))
            cst_idx += 1
            codigo += f"    @ PUSH {val}\n"
            codigo += estrutura_vldr("d0", cst_nome)
            codigo += f"    VPUSH {{d0}}\n"
            profundidade_pilha += 1

        elif tipo == "MEM":
            nome_mem = token.get("nome", "").strip()
            if not nome_mem:
                print(f"[Linha {linha}] Erro: MEM sem nome.")
                return None

            eh_store = idx == len(tokens) - 1 and profundidade_pilha > 0
            if eh_store:
                codigo += f"    @ STORE MEM {nome_mem}\n"
                codigo += f"    VPOP  {{d0}}\n"
                codigo += estrutura_vstr("d0", f"mem_{nome_mem}")
                codigo += f"    VPUSH {{d0}}\n"
            else:
                codigo += f"    @ LOAD MEM {nome_mem}\n"
                codigo += estrutura_vldr("d0", f"mem_{nome_mem}")
                codigo += f"    VPUSH {{d0}}\n"
                profundidade_pilha += 1

        elif tipo == "RES":
            if profundidade_pilha < 1:
                print(f"[Linha {linha}] Erro: RES sem índice na pilha.")
                return None

            num_token = next(
                (tokens[j] for j in range(idx - 1, -1, -1) if tokens[j].get("tipo") == "NUM"),
                None
            )
            if num_token is None:
                print(f"[Linha {linha}] Erro: RES sem valor numérico.")
                return None

            n = int(float(num_token["valor"]))
            indice_alvo = len(todas_linhas) - n
            if indice_alvo < 0 or indice_alvo >= len(todas_linhas):
                print(f"[Linha {linha}] Erro: RES({n}) aponta para linha inexistente.")
                return None

            linha_alvo = todas_linhas[indice_alvo]
            codigo += f"    @ LOAD RES({n}) -> result_linha{linha_alvo}\n"
            codigo += f"    VPOP  {{d7}}\n"
            codigo += estrutura_vldr("d0", f"result_linha{linha_alvo}")
            codigo += f"    VPUSH {{d0}}\n"

        elif tipo == "OP":
            if profundidade_pilha < 2:
                print(f"[Linha {linha}] Erro: operandos insuficientes para '{valor}'.")
                return None
            codigo += OPERADORES_PILHA[valor](label, step)
            step   += 1
            profundidade_pilha -= 1

    codigo += f"    @ Resultado final -> result_{label}\n"
    codigo += f"    VPOP  {{d0}}\n"
    codigo += estrutura_vstr("d0", f"result_{label}")
    codigo += estrutura_exibir_led_resultado(f"result_{label}")
    return constantes, results, codigo


# DISPATCHER

def extrair_entradas(json_data) -> list[dict]:
    if isinstance(json_data, dict):
        entradas = json_data.get("linhas", [])
    elif isinstance(json_data, list):
        entradas = json_data
    else:
        print("Formato de entrada invalido: esperado dict ou list.")
        return []

    if not isinstance(entradas, list):
        print("Formato de 'linhas' invalido: esperado uma lista.")
        return []

    return [entrada for entrada in entradas if isinstance(entrada, dict)]


def gerarAssembly(json_data) -> None:
    entradas = extrair_entradas(json_data)

    if len(entradas) > MAX_EXPRESSOES:
        print(f"Aviso: máximo de {MAX_EXPRESSOES} expressões.")
        entradas = entradas[:MAX_EXPRESSOES]

    blocos             = []
    todas_constantes   = []
    todos_results      = []
    nomes_mem          = set()
    linhas_processadas = []

    for i, entrada in enumerate(entradas):
        linha  = entrada.get("linha", i + 1)
        tokens = entrada.get("tokens", [])

        for t in tokens:
            if t.get("tipo") == "MEM" and t.get("nome"):
                nomes_mem.add(t["nome"].strip())

        resultado = gerar_bloco_rpn(linha, tokens, linhas_processadas)

        if resultado is None:
            continue

        constantes, results, codigo = resultado
        todas_constantes.extend(constantes)
        todos_results.extend(results)
        blocos.append((linha, codigo))
        linhas_processadas.append(linha)

    if not blocos:
        print("Nenhuma expressão válida encontrada.")
        return

    conteudo  = estrutura_cabecalho_arquivo(len(blocos))
    conteudo += estrutura_secao_data(todas_constantes, todos_results, nomes_mem)
    conteudo += estrutura_inicio_text()
    conteudo += estrutura_bloco_dummy()

    for idx, (linha, codigo) in enumerate(blocos):
        conteudo += estrutura_label(f"linha{linha}")
        conteudo += codigo
        if idx < len(blocos) - 1:
            prox_linha = blocos[idx + 1][0]
            conteudo += estrutura_separador(linha, prox_linha)

    conteudo += estrutura_exit()
    conteudo += estrutura_rotinas_leds()

    nome_arquivo = "assembly_saida.txt"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)

    print(f"Assembly gerado com sucesso -> '{nome_arquivo}' ({len(blocos)} expressões)")

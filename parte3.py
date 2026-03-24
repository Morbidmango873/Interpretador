import json

# CONFIGURAÇÃO

MAX_EXPRESSOES = 10
LED_BASE = 0xFF200000
DELAY_LED = 1000000


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

    if constantes:
        linhas.append("    @ --- Constantes numericas ---\n")
        for nome, valor in constantes:
            linhas.append(f"    {nome}: .double {valor:.10f}\n")

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
    return (
        f"\n.section .text\n"
        f".global _start\n\n"
        f"_start:\n"
        f"    @ Habilita VFP/NEON\n"
        f"    VMRS r0, FPSCR\n"
        f"    ORR  r0, r0, #0x00400000\n"
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
        f"    MOV r0, r6\n"
        f"    BL exibir_leds_32\n"
        f"    BL marcar_separador_led\n"
        f"    MOV r0, r7\n"
        f"    BL exibir_leds_32\n"
    )

def estrutura_rotinas_leds() -> str:
    return (
        f"\n@ --- Rotinas de exibicao nos LEDs do CPUlator ---\n"
        f"delay_leds:\n"
        f"    LDR r1, ={DELAY_LED}\n"
        f"delay_leds_loop:\n"
        f"    SUBS r1, r1, #1\n"
        f"    BNE delay_leds_loop\n"
        f"    BX lr\n\n"
        f"apagar_leds:\n"
        f"    LDR r1, ={LED_BASE}\n"
        f"    MOV r0, #0\n"
        f"    STR r0, [r1]\n"
        f"    BX lr\n\n"
        f"marcar_separador_led:\n"
        f"    PUSH {{lr}}\n"
        f"    LDR r1, ={LED_BASE}\n"
        f"    MOV r0, #1              @ acende 1 LED como separador\n"
        f"    STR r0, [r1]\n"
        f"    BL delay_leds\n"
        f"    MOV r2, #0\n"
        f"    STR r2, [r1]\n"
        f"    BL delay_leds\n"
        f"    POP {{lr}}\n"
        f"    BX lr\n\n"
        f"exibir_leds_32:\n"
        f"    PUSH {{lr}}\n"
        f"    LDR r1, ={LED_BASE}\n"
        f"    STR r0, [r1]\n"
        f"    BL delay_leds\n"
        f"    MOV r2, #0\n"
        f"    STR r2, [r1]\n"
        f"    BL delay_leds\n"
        f"    POP {{lr}}\n"
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
        f"    VDIV.F64 d0, d0, d1   @ d0 = a / b\n"
        f"    VPUSH {{d0}}\n"
    )

def estrutura_op_divisao_inteira(label: str, step: int) -> str:
    """Divisão inteira: divide, converte para int (trunca) e volta para double."""
    return (
        f"    @ DIVISAO INTEIRA // (step {step})\n"
        f"    VPOP  {{d1}}            @ b\n"
        f"    VPOP  {{d0}}            @ a\n"
        f"    VDIV.F64 d0, d0, d1   @ d0 = a / b\n"
        f"    VCVT.S32.F64 s0, d0   @ trunca para inteiro\n"
        f"    VCVT.F64.S32 d0, s0   @ volta para double\n"
        f"    VPUSH {{d0}}\n"
    )

def estrutura_op_resto(label: str, step: int) -> str:
    """Resto: a - trunc(a/b)*b"""
    return (
        f"    @ RESTO % (step {step})\n"
        f"    VPOP  {{d1}}            @ b\n"
        f"    VPOP  {{d0}}            @ a\n"
        f"    VDIV.F64 d2, d0, d1   @ d2 = a / b\n"
        f"    VCVT.S32.F64 s4, d2   @ trunca\n"
        f"    VCVT.F64.S32 d2, s4   @ volta para double\n"
        f"    VMUL.F64 d2, d2, d1   @ d2 = trunc(a/b) * b\n"
        f"    VSUB.F64 d0, d0, d2   @ d0 = a - d2\n"
        f"    VPUSH {{d0}}\n"
    )

def estrutura_op_potencia(label: str, step: int) -> str:
    """
    Potência por multiplicação repetida.
    Expoente desescalado para inteiro via VCVT.
    Loop: decrementa r1 e multiplica d0 por d2 a cada passo.
    """
    lbl_loop = f"pow_loop_{label}_{step}"
    lbl_fim  = f"pow_fim_{label}_{step}"
    return (
        f"    @ POTENCIA ^ (step {step})\n"
        f"    VPOP  {{d1}}            @ expoente\n"
        f"    VPOP  {{d0}}            @ base\n"
        f"    @ converte expoente para inteiro em r1\n"
        f"    VCVT.S32.F64 s2, d1\n"
        f"    VMOV r1, s2            @ r1 = expoente inteiro\n"
        f"    @ caso base: exp=0 → resultado=1.0\n"
        f"    CMP  r1, #0\n"
        f"    BNE  {lbl_loop}\n"
        f"    VMOV.F64 d0, #1.0\n"
        f"    B    {lbl_fim}\n"
        f"{lbl_loop}:\n"
        f"    VMOV.F64 d2, d0        @ d2 = base (acumulador)\n"
        f"    SUB  r1, r1, #1\n"
        f"pow_mul_{label}_{step}:\n"
        f"    CMP  r1, #0\n"
        f"    BEQ  {lbl_fim}\n"
        f"    VMUL.F64 d2, d2, d0   @ d2 *= base\n"
        f"    SUB  r1, r1, #1\n"
        f"    B    pow_mul_{label}_{step}\n"
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


# GERADOR MEM

def gerar_bloco_mem(linha: int, tokens: list[dict]) -> tuple[list, list, str] | None:
    """
    Retorna (constantes, results, codigo).
    Escrita: salva valor em mem_NOME e result_linhaN.
    Leitura: copia mem_NOME para result_linhaN (0.0 se nunca escrito).
    """
    label     = f"linha{linha}"
    mem_token = next((t for t in tokens if t.get("tipo") == "MEM"), None)
    if not mem_token:
        print(f"[Linha {linha}] Erro: token MEM não encontrado.")
        return None

    nome_mem = mem_token.get("nome", "").strip()
    if not nome_mem:
        print(f"[Linha {linha}] Erro: MEM sem nome.")
        return None

    num_token  = next((t for t in tokens if t.get("tipo") == "NUM"), None)
    constantes = []
    results    = [f"result_{label}"]

    if num_token is not None:
        val      = float(num_token["valor"])
        cst_nome = f"cst_{label}_0"
        constantes.append((cst_nome, val))
        codigo  = f"@ --- Linha {linha} | MEM ESCRITA: {nome_mem} = {val} ---\n"
        codigo += estrutura_vldr("d0", cst_nome)
        codigo += estrutura_vstr("d0", f"mem_{nome_mem}")
        codigo += estrutura_vstr("d0", f"result_{label}")
        codigo += estrutura_exibir_led_resultado(f"result_{label}")
    else:
        codigo  = f"@ --- Linha {linha} | MEM LEITURA: {nome_mem} ---\n"
        codigo += estrutura_vldr("d0", f"mem_{nome_mem}")
        codigo += estrutura_vstr("d0", f"result_{label}")
        codigo += estrutura_exibir_led_resultado(f"result_{label}")

    return constantes, results, codigo


# GERADOR RES

def gerar_bloco_res(linha: int, tokens: list[dict], todas_linhas: list[int]) -> tuple[list, list, str] | None:
    label     = f"linha{linha}"
    num_token = next((t for t in tokens if t["tipo"] == "NUM"), None)
    if num_token is None:
        print(f"[Linha {linha}] Erro: RES sem valor numérico.")
        return None

    n          = int(float(num_token["valor"]))
    linha_alvo = linha - n
    if linha_alvo not in todas_linhas:
        print(f"[Linha {linha}] Erro: RES({n}) aponta para linha {linha_alvo} inexistente.")
        return None

    label_alvo = f"linha{linha_alvo}"
    results    = [f"result_{label}"]
    codigo     = f"@ --- Linha {linha} | RES({n}) -> copia result_{label_alvo} ---\n"
    codigo    += estrutura_vldr("d0", f"result_{label_alvo}")
    codigo    += estrutura_vstr("d0", f"result_{label}")
    codigo    += estrutura_exibir_led_resultado(f"result_{label}")
    return [], results, codigo


# GERADOR RPN

def gerar_bloco_rpn(linha: int, tokens: list[dict]) -> tuple[list, list, str] | None:
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

    for token in tokens:
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

        elif tipo == "OP":
            codigo += OPERADORES_PILHA[valor](label, step)
            step   += 1

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


def gerarassembly(json_data) -> None:
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

        tem_mem = any(t.get("tipo") == "MEM" for t in tokens)
        tem_res = any(t.get("tipo") == "RES" for t in tokens)

        if tem_mem:
            for t in tokens:
                if t.get("tipo") == "MEM" and t.get("nome"):
                    nomes_mem.add(t["nome"].strip())
            resultado = gerar_bloco_mem(linha, tokens)
        elif tem_res:
            resultado = gerar_bloco_res(linha, tokens, linhas_processadas)
        else:
            resultado = gerar_bloco_rpn(linha, tokens)

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


# LEITURA DO JSON — lê de saida_fase1.txt

def ler_json_arquivo(caminho: str = "saida_fase1.txt") -> dict | None:
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        print(f"JSON carregado de '{caminho}'")
        return dados
    except FileNotFoundError:
        print(f"Arquivo '{caminho}' não encontrado.")
        return None
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return None


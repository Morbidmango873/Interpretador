# ══════════════════════════════════════════════════════════════
# ESTRUTURAS PADRÃO DO ASSEMBLY
# ══════════════════════════════════════════════════════════════

ESCALA = 100  # float * 100 para preservar 2 casas decimais

def float_para_inteiro(valor: float) -> int:
    """Converte float para inteiro escalado (1.5 → 150)."""
    return round(valor * ESCALA)


def estrutura_cabecalho_arquivo(total: int) -> str:
    return (
        f"@ ============================================================\n"
        f"@ Gerado automaticamente — {total} expressao(oes)\n"
        f"@ Arquitetura: ARMv7 | Escala: x{ESCALA}\n"
        f"@ ============================================================\n\n"
    )


def estrutura_cabecalho_bloco(linha: int, expressao_rpn: str) -> str:
    return (
        f"@ --- Linha {linha} | RPN: {expressao_rpn} ---\n"
    )


def estrutura_separador(linha_atual: int, linha_prox: int) -> str:
    return (
        f"\n@ ------------------------------------------------------------\n"
        f"@ FIM LINHA {linha_atual} | INICIO LINHA {linha_prox}\n"
        f"@ ------------------------------------------------------------\n\n"
    )


def estrutura_secao_data(variaveis: list[tuple[str, int]]) -> str:
    """Bloco .section .data com todas as variáveis."""
    linhas = [".section .data\n"]
    for nome, valor in variaveis:
        linhas.append(f"    {nome}: .word {valor}\n")
    return "".join(linhas)


def estrutura_bloco_dummy() -> str:
    """Absorve o erro de primeira execução do CPUlator."""
    return (
        f"@ --- DUMMY: absorve erro de primeira execucao ---\n"
        f"    MOV r1, #1\n"
        f"    MOV r2, #1\n"
        f"    SUB r3, r1, r2\n"
        f"@ --- FIM DUMMY ---\n\n"
    )


def estrutura_inicio_text() -> str:
    return (
        f"\n.section .text\n"
        f".global _start\n\n"
        f"_start:\n"
    )


def estrutura_label(label: str) -> str:
    return f"\n{label}:\n"


def estrutura_carregar_variaveis(reg_addr: str, reg_dest: str, variavel: str) -> str:
    return (
        f"    LDR {reg_addr}, ={variavel}\n"
        f"    LDR {reg_dest}, [{reg_addr}]\n"
    )


def estrutura_salvar_resultado(reg_addr: str, reg_valor: str, variavel: str) -> str:
    return (
        f"    LDR {reg_addr}, ={variavel}\n"
        f"    STR {reg_valor}, [{reg_addr}]\n"
    )


def estrutura_exit() -> str:
    return (
        f"\n@ --- Encerramento do programa ---\n"
        f"    MOV r7, #1\n"
        f"    MOV r0, #0\n"
        f"    SWI 0\n"
    )


# ══════════════════════════════════════════════════════════════
# ESTRUTURAS DE PILHA EM MEMÓRIA
# A pilha é simulada com slots fixos no .data (stack_0..stack_N)
# e um índice (stack_top) que indica o próximo slot livre.
# Todas as operações repetem o mesmo padrão push/pop.
# ══════════════════════════════════════════════════════════════

MAX_PILHA = 16  # slots máximos por linha

def estrutura_vars_pilha(label: str) -> list[tuple[str, int]]:
    """Gera os slots de pilha e o stack_top no .data para um label."""
    variaveis = [(f"stack_top_{label}", 0)]
    for i in range(MAX_PILHA):
        variaveis.append((f"stack_{label}_{i}", 0))
    return variaveis


def estrutura_push(label: str, reg_valor: str, reg_tmp1: str, reg_tmp2: str) -> str:
    """
    Empilha reg_valor na pilha do label.
    Padrão repetido: carrega top → calcula endereço do slot → salva valor → incrementa top.
    reg_tmp1, reg_tmp2: registradores temporários livres.
    """
    return (
        f"    @ PUSH {reg_valor}\n"
        f"    LDR {reg_tmp1}, =stack_top_{label}\n"
        f"    LDR {reg_tmp2}, [{reg_tmp1}]        @ tmp2 = índice atual\n"
        f"    LDR {reg_tmp1}, =stack_{label}_0    @ base da pilha\n"
        f"    ADD {reg_tmp1}, {reg_tmp1}, {reg_tmp2}, LSL #2  @ endereço = base + top*4\n"
        f"    STR {reg_valor}, [{reg_tmp1}]        @ salva valor\n"
        f"    LDR {reg_tmp1}, =stack_top_{label}\n"
        f"    LDR {reg_tmp2}, [{reg_tmp1}]\n"
        f"    ADD {reg_tmp2}, {reg_tmp2}, #1\n"
        f"    STR {reg_tmp2}, [{reg_tmp1}]         @ top++\n"
    )


def estrutura_pop(label: str, reg_dest: str, reg_tmp1: str, reg_tmp2: str) -> str:
    """
    Desempilha topo da pilha do label em reg_dest.
    Padrão repetido: decrementa top → calcula endereço → carrega valor.
    """
    return (
        f"    @ POP -> {reg_dest}\n"
        f"    LDR {reg_tmp1}, =stack_top_{label}\n"
        f"    LDR {reg_tmp2}, [{reg_tmp1}]\n"
        f"    SUB {reg_tmp2}, {reg_tmp2}, #1\n"
        f"    STR {reg_tmp2}, [{reg_tmp1}]         @ top--\n"
        f"    LDR {reg_tmp1}, =stack_{label}_0\n"
        f"    ADD {reg_tmp1}, {reg_tmp1}, {reg_tmp2}, LSL #2  @ endereço = base + top*4\n"
        f"    LDR {reg_dest}, [{reg_tmp1}]         @ carrega valor\n"
    )


# ══════════════════════════════════════════════════════════════
# OPERAÇÕES SOBRE A PILHA
# Cada op faz: pop b, pop a, calcula a OP b, push resultado
# ══════════════════════════════════════════════════════════════

def estrutura_op_soma(label: str, step: int) -> str:
    return (
        f"    @ OPERACAO SOMA (step {step})\n"
        + estrutura_pop(label, "r1", "r4", "r5")
        + estrutura_pop(label, "r2", "r4", "r5")
        + f"    ADD r3, r2, r1\n"
        + estrutura_push(label, "r3", "r4", "r5")
    )


def estrutura_op_subtracao(label: str, step: int) -> str:
    return (
        f"    @ OPERACAO SUBTRACAO (step {step})\n"
        + estrutura_pop(label, "r1", "r4", "r5")
        + estrutura_pop(label, "r2", "r4", "r5")
        + f"    SUB r3, r2, r1\n"
        + estrutura_push(label, "r3", "r4", "r5")
    )


def estrutura_normalizar_escala(label: str, step: int) -> str:
    """
    Divide r3 por ESCALA (100) via subtracao repetida para normalizar
    o resultado apos uma multiplicacao de dois valores ja escalados.
    Ex: 150 * 200 = 30000 → 30000 / 100 = 300  (= 3.0 * 100)
    """
    lbl_loop = f"norm_loop_{label}_{step}"
    lbl_fim  = f"norm_fim_{label}_{step}"
    return (
        f"    @ NORMALIZAR escala: r3 = r3 / {ESCALA}\n"
        f"    MOV r1, r3              @ r1 = dividendo (resultado bruto)\n"
        f"    MOV r2, #{ESCALA}       @ r2 = divisor (escala)\n"
        f"    MOV r3, #0              @ r3 = quociente\n"
        f"{lbl_loop}:\n"
        f"    CMP r1, r2\n"
        f"    BLT {lbl_fim}\n"
        f"    SUB r1, r1, r2\n"
        f"    ADD r3, r3, #1\n"
        f"    B   {lbl_loop}\n"
        f"{lbl_fim}:\n"
    )


def estrutura_op_multiplicacao(label: str, step: int) -> str:
    return (
        f"    @ OPERACAO MULTIPLICACAO (step {step})\n"
        + estrutura_pop(label, "r1", "r4", "r5")
        + estrutura_pop(label, "r2", "r4", "r5")
        + f"    MOV r3, r1\n"
        + f"    MUL r3, r2, r3\n"
        + estrutura_normalizar_escala(label, step)
        + estrutura_push(label, "r3", "r4", "r5")
    )


def estrutura_op_divisao(label: str, step: int) -> str:
    lbl_loop  = f"div_loop_{label}_{step}"
    lbl_fim   = f"div_fim_{label}_{step}"
    lbl_scale = f"scale_loop_{label}_{step}"
    lbl_sdone = f"scale_done_{label}_{step}"
    return (
        f"    @ OPERACAO DIVISAO (step {step})\n"
        + estrutura_pop(label, "r1", "r4", "r5")   # r1 = divisor
        + estrutura_pop(label, "r2", "r4", "r5")   # r2 = dividendo
        # Multiplica dividendo por ESCALA para preservar precisao
        + f"    @ Escala dividendo x{ESCALA} antes de dividir\n"
        + f"    MOV r6, #{ESCALA}\n"
        + f"    MOV r3, r2\n"
        + f"    MOV r2, #0\n"
        + f"{lbl_scale}:\n"
        + f"    CMP r6, #0\n"
        + f"    BEQ {lbl_sdone}\n"
        + f"    ADD r2, r2, r3\n"
        + f"    SUB r6, r6, #1\n"
        + f"    B   {lbl_scale}\n"
        + f"{lbl_sdone}:\n"
        # Agora divide r2 (dividendo*100) por r1 (divisor)
        + f"    MOV r3, #0\n"
        + f"{lbl_loop}:\n"
        + f"    CMP r2, r1\n"
        + f"    BLT {lbl_fim}\n"
        + f"    SUB r2, r2, r1\n"
        + f"    ADD r3, r3, #1\n"
        + f"    B   {lbl_loop}\n"
        + f"{lbl_fim}:\n"
        + estrutura_push(label, "r3", "r4", "r5")
    )


OPERADORES_PILHA = {
    "+": estrutura_op_soma,
    "-": estrutura_op_subtracao,
    "*": estrutura_op_multiplicacao,
    "/": estrutura_op_divisao,
}


# ══════════════════════════════════════════════════════════════
# GERADOR RPN — interpreta tokens e monta o bloco assembly
# ══════════════════════════════════════════════════════════════

def gerar_bloco_rpn(linha: int, tokens: list[dict]) -> tuple[list, str] | None:
    """
    Interpreta a lista de tokens em notação RPN e gera:
      - variaveis: slots de pilha + result para o .data
      - codigo   : instruções para o .text
    """
    label = f"linha{linha}"

    # Monta string RPN para comentário
    rpn_str = " ".join(t["valor"] for t in tokens)

    # Valida tokens
    for token in tokens:
        if token["tipo"] == "OP" and token["valor"] not in OPERADORES_PILHA:
            print(f"[Linha {linha}] Operador '{token['valor']}' não implementado.")
            return None

    # Variáveis: slots de pilha + result
    variaveis = estrutura_vars_pilha(label)
    variaveis.append((f"result_{label}", 0))

    # Gera o código percorrendo os tokens
    codigo = estrutura_cabecalho_bloco(linha, rpn_str)
    step = 0

    for token in tokens:
        tipo  = token["tipo"]
        valor = token["valor"]

        if tipo == "NUM":
            # Converte float para inteiro escalado e empilha via MOV imediato
            val_int = float_para_inteiro(float(valor))
            codigo += f"    @ PUSH #{val_int}  (= {valor} * {ESCALA})\n"
            codigo += f"    MOV r3, #{val_int}\n"
            codigo += estrutura_push(label, "r3", "r4", "r5")

        elif tipo == "OP":
            fn_op = OPERADORES_PILHA[valor]
            codigo += fn_op(label, step)
            step += 1

    # Ao final da RPN, o resultado está no topo da pilha — desempilha para result
    codigo += f"    @ Resultado final -> result_{label}\n"
    codigo += estrutura_pop(label, "r3", "r4", "r5")
    codigo += estrutura_salvar_resultado("r0", "r3", f"result_{label}")

    return variaveis, codigo


# ══════════════════════════════════════════════════════════════
# DISPATCHER — lê e interpreta o JSON
# ══════════════════════════════════════════════════════════════

MAX_EXPRESSOES = 10

def gerarassembly(json_data: dict) -> None:
    """
    Lê um JSON com até 10 entradas de 'linha' em notação RPN,
    gera assembly ARMv7 usando pilha em memória para cada expressão,
    e salva tudo em um único arquivo .txt.
    """
    entradas = json_data.get("linhas", [])

    if len(entradas) > MAX_EXPRESSOES:
        print(f"Aviso: máximo de {MAX_EXPRESSOES} expressões. As extras serão ignoradas.")
        entradas = entradas[:MAX_EXPRESSOES]

    blocos = []

    for i, entrada in enumerate(entradas):
        linha  = entrada.get("linha", i + 1)
        tokens = entrada.get("tokens", [])

        resultado = gerar_bloco_rpn(linha, tokens)
        if resultado is None:
            continue

        variaveis, codigo = resultado
        blocos.append((linha, variaveis, codigo))

    if not blocos:
        print("Nenhuma expressão válida encontrada.")
        return

    # Monta o arquivo
    todas_variaveis = []
    for _, variaveis, _ in blocos:
        todas_variaveis.extend(variaveis)

    conteudo  = estrutura_cabecalho_arquivo(len(blocos))
    conteudo += estrutura_secao_data(todas_variaveis)
    conteudo += estrutura_inicio_text()
    conteudo += estrutura_bloco_dummy()

    for idx, (linha, _, codigo) in enumerate(blocos):
        conteudo += estrutura_label(f"linha{linha}")
        conteudo += codigo

        if idx < len(blocos) - 1:
            prox_linha = blocos[idx + 1][0]
            conteudo += estrutura_separador(linha, prox_linha)

    conteudo += estrutura_exit()

    nome_arquivo = "assembly_saida.txt"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)

    print(f"Assembly gerado com sucesso -> '{nome_arquivo}' ({len(blocos)} expressões)")


# ══════════════════════════════════════════════════════════════
# EXEMPLO DE USO
# RPN: 1.5 2.0 * 1.0 + 3.0 4.0 * /
# = (1.5*2.0 + 1.0) / (3.0*4.0)
# = (150*200 + 100) / (300*400)   [escala x100]
# = 30100 / 120000 = 0 (divisão inteira)
#
# Expressão simples para verificação:
# RPN: 3.0 4.0 +  →  300 + 400 = 700
# RPN: 6.0 2.0 *  →  600 * 200 = 120000
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    dados = {
        "linhas": [
            {
                "linha": 1,
                "tokens": [
                    {"tipo": "NUM", "valor": "3.0"},
                    {"tipo": "NUM", "valor": "4.0"},
                    {"tipo": "OP",  "valor": "+"}
                ]
            },
            {
                "linha": 2,
                "tokens": [
                    {"tipo": "NUM", "valor": "1.5"},
                    {"tipo": "NUM", "valor": "2.0"},
                    {"tipo": "OP",  "valor": "*"},
                    {"tipo": "NUM", "valor": "1.0"},
                    {"tipo": "OP",  "valor": "+"},
                    {"tipo": "NUM", "valor": "3.0"},
                    {"tipo": "NUM", "valor": "4.0"},
                    {"tipo": "OP",  "valor": "*"},
                    {"tipo": "OP",  "valor": "/"}
                ]
            },
            {
                "linha": 3,
                "tokens": [
                    {"tipo": "NUM", "valor": "6.0"},
                    {"tipo": "NUM", "valor": "2.0"},
                    {"tipo": "OP",  "valor": "*"}
                ]
            }
        ]
    }

    gerarassembly(dados)
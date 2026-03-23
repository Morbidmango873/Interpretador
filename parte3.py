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


def estrutura_op_divisao_inteira(label: str, step: int) -> str:
    """
    Divisão inteira //:  pop b, pop a, a // b, push resultado.
    Diferente da divisao (/), NAO escala o dividendo antes de dividir.
    Ex: 700 // 300 = 2  (= 7.00 // 3.00 com escala x100)
    """
    lbl_loop = f"idiv_loop_{label}_{step}"
    lbl_fim  = f"idiv_fim_{label}_{step}"
    return (
        f"    @ OPERACAO DIVISAO INTEIRA // (step {step})\n"
        + estrutura_pop(label, "r1", "r4", "r5")   # r1 = divisor
        + estrutura_pop(label, "r2", "r4", "r5")   # r2 = dividendo
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


def estrutura_op_potencia(label: str, step: int) -> str:
    """
    Potência por multiplicação repetida: pop exp, pop base, base^exp, push.
    O expoente é desescalado (/100) para obter o inteiro real antes do loop.
    Ex: 2.0^3 → base=200, exp=300 → desescala exp: 300/100=3 → 200*200*200/100/100 = 800 (=8.00)
    Cada multiplicação normaliza por 100 para manter a escala correta.
    Expoente 0 retorna 100 (= 1.0 em escala x100).
    Apenas expoentes inteiros positivos são suportados.
    """
    lbl_deesc   = f"pow_deesc_{label}_{step}"    # loop desescalar expoente
    lbl_deesc_f = f"pow_deesc_fim_{label}_{step}"
    lbl_loop    = f"pow_loop_{label}_{step}"     # loop de multiplicação
    lbl_fim     = f"pow_fim_{label}_{step}"

    return (
        f"    @ OPERACAO POTENCIA ^ (step {step})\n"
        + estrutura_pop(label, "r1", "r4", "r5")   # r1 = expoente escalado
        + estrutura_pop(label, "r2", "r4", "r5")   # r2 = base escalada
        # Desescala o expoente: r1 = r1 / 100
        + f"    @ Desescala expoente: r1 = r1 / {ESCALA}\n"
        + f"    MOV r6, r1              @ r6 = expoente escalado\n"
        + f"    MOV r1, #0              @ r1 = contador (expoente real)\n"
        + f"    MOV r8, #{ESCALA}       @ r8 = divisor (escala)\n"
        + f"{lbl_deesc}:\n"
        + f"    CMP r6, r8\n"
        + f"    BLT {lbl_deesc_f}\n"
        + f"    SUB r6, r6, r8\n"
        + f"    ADD r1, r1, #1\n"
        + f"    B   {lbl_deesc}\n"
        + f"{lbl_deesc_f}:              @ r1 = expoente inteiro real\n"
        # Caso especial: exp = 0 → resultado = 1.0 (= 100 em escala)
        + f"    CMP r1, #0\n"
        + f"    BNE {lbl_loop}\n"
        + f"    MOV r3, #{ESCALA}       @ base^0 = 1.0\n"
        + f"    B   {lbl_fim}\n"
        # Loop: acumula em r3, multiplicando por base a cada iteração
        + f"{lbl_loop}:\n"
        + f"    MOV r3, r2              @ r3 = base (primeiro valor)\n"
        + f"    SUB r1, r1, #1          @ desconta a primeira base\n"
        + f"    @ Loop: multiplica r3 por base (r2) mais r1 vezes\n"
        + f"pow_mul_{label}_{step}:\n"
        + f"    CMP r1, #0\n"
        + f"    BEQ {lbl_fim}\n"
        + f"    MOV r9, r3\n"
        + f"    MUL r3, r2, r9          @ r3 = r3 * base\n"
        # Normaliza após cada multiplicação
        + f"    MOV r6, r3              @ dividendo\n"
        + f"    MOV r7, #{ESCALA}       @ divisor\n"
        + f"    MOV r3, #0\n"
        + f"pow_norm_{label}_{step}:\n"
        + f"    CMP r6, r7\n"
        + f"    BLT pow_norm_fim_{label}_{step}\n"
        + f"    SUB r6, r6, r7\n"
        + f"    ADD r3, r3, #1\n"
        + f"    B   pow_norm_{label}_{step}\n"
        + f"pow_norm_fim_{label}_{step}:\n"
        + f"    SUB r1, r1, #1\n"
        + f"    B   pow_mul_{label}_{step}\n"
        + f"{lbl_fim}:\n"
        + estrutura_push(label, "r3", "r4", "r5")
    )


def estrutura_op_resto(label: str, step: int) -> str:
    """
    Resto da divisão %: pop b, pop a, a % b, push resultado.
    Usa subtração repetida — o que sobrar em r2 após o loop é o resto.
    Ex: 700 % 300 = 100  (= 7.00 % 3.00 = 1.00 em escala x100)
    """
    lbl_loop = f"mod_loop_{label}_{step}"
    lbl_fim  = f"mod_fim_{label}_{step}"
    return (
        f"    @ OPERACAO RESTO % (step {step})\n"
        + estrutura_pop(label, "r1", "r4", "r5")   # r1 = divisor
        + estrutura_pop(label, "r2", "r4", "r5")   # r2 = dividendo
        + f"    @ subtrai divisor do dividendo ate nao caber mais\n"
        + f"{lbl_loop}:\n"
        + f"    CMP r2, r1\n"
        + f"    BLT {lbl_fim}\n"
        + f"    SUB r2, r2, r1          @ r2 -= r1\n"
        + f"    B   {lbl_loop}\n"
        + f"{lbl_fim}:                  @ r2 = resto\n"
        + f"    MOV r3, r2\n"
        + estrutura_push(label, "r3", "r4", "r5")
    )


OPERADORES_PILHA = {
    "+":  estrutura_op_soma,
    "-":  estrutura_op_subtracao,
    "*":  estrutura_op_multiplicacao,
    "/":  estrutura_op_divisao,
    "//": estrutura_op_divisao_inteira,
    "^":  estrutura_op_potencia,
    "%":  estrutura_op_resto,
}


# ══════════════════════════════════════════════════════════════
# REGISTRO GLOBAL DE VARIÁVEIS MEM
# Cada nome (ex: "MEN") gera uma única entrada no .data compartilhada
# entre todas as linhas — persistente durante toda a execução.
# ══════════════════════════════════════════════════════════════

_mem_vars: dict[str, int] = {}  # nome -> valor inicial (sempre 0)

def registrar_mem_var(nome: str) -> None:
    """Registra uma variável MEM global se ainda não existir."""
    if nome not in _mem_vars:
        _mem_vars[nome] = 0

def estrutura_vars_mem() -> list[tuple[str, int]]:
    """Retorna todas as variáveis MEM para o .section .data."""
    return [(f"mem_{nome}", valor) for nome, valor in _mem_vars.items()]


def gerar_bloco_mem(linha: int, tokens: list[dict]) -> tuple[list, str] | None:
    """
    Interpreta o token MEM:
      - COM NUM antes: escrita — salva NUM em mem_NOME e em result_linha
      - SEM NUM:       leitura — copia mem_NOME para result_linha
    Primeira leitura sem escrita prévia retorna 0 (inicializado no .data).
    """
    label = f"linha{linha}"

    mem_token = next((t for t in tokens if t.get("tipo") == "MEM"), None)
    if mem_token is None:
        print(f"[Linha {linha}] Erro: token MEM não encontrado.")
        return None

    nome = mem_token.get("nome", "").upper()
    if not nome:
        print(f"[Linha {linha}] Erro: MEM sem nome.")
        return None

    # Registra a variável global
    registrar_mem_var(nome)
    mem_label = f"mem_{nome}"

    # Verifica se há NUM (escrita) ou não (leitura)
    num_token = next((t for t in tokens if t.get("tipo") == "NUM"), None)

    variaveis = [(f"result_{label}", 0)]

    if num_token is not None:
        # ESCRITA: salva o valor em mem_NOME e em result_linha
        val_int = float_para_inteiro(float(num_token["valor"]))
        codigo  = f"@ --- Linha {linha} | MEM ESCRITA: {nome} = {num_token['valor']} ---\n"
        codigo += f"    MOV r3, #{val_int}\n"
        codigo += estrutura_salvar_resultado("r0", "r3", mem_label)
        codigo += estrutura_salvar_resultado("r0", "r3", f"result_{label}")
    else:
        # LEITURA: copia mem_NOME para result_linha
        codigo  = f"@ --- Linha {linha} | MEM LEITURA: {nome} ---\n"
        codigo += estrutura_carregar_variaveis("r0", "r3", mem_label)
        codigo += estrutura_salvar_resultado("r0", "r3", f"result_{label}")

    return variaveis, codigo


# ══════════════════════════════════════════════════════════════
# GERADOR RES — busca resultado de N linhas acima
# ══════════════════════════════════════════════════════════════

def gerar_bloco_res(linha: int, tokens: list[dict], todas_linhas: list[int]) -> tuple[list, str] | None:
    """
    Interpreta o token RES: lê o NUM anterior para saber quantas linhas
    subir, valida se a linha alvo existe, e gera assembly que copia
    result_linhaN para result_linha_atual.
    """
    label = f"linha{linha}"

    # Extrai o valor do NUM antes do RES
    num_token = next((t for t in tokens if t["tipo"] == "NUM"), None)
    if num_token is None:
        print(f"[Linha {linha}] Erro: RES sem valor numérico.")
        return None

    n = int(float(num_token["valor"]))  # quantas linhas acima

    # Calcula a linha alvo
    linha_alvo = linha - n

    # Valida se a linha alvo existe nas linhas processadas
    if linha_alvo not in todas_linhas:
        print(f"[Linha {linha}] Erro: RES({n}) aponta para linha {linha_alvo} que não existe.")
        return None

    label_alvo = f"linha{linha_alvo}"

    # Variáveis necessárias: apenas o result desta linha
    variaveis = [(f"result_{label}", 0)]

    codigo  = f"@ --- Linha {linha} | RES({n}) -> copia result_{label_alvo} ---\n"
    codigo += estrutura_carregar_variaveis("r0", "r3", f"result_{label_alvo}")
    codigo += estrutura_salvar_resultado("r0", "r3", f"result_{label}")

    return variaveis, codigo


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

    # Limpa registro de MEMs globais para esta execução
    _mem_vars.clear()

    # Lista de linhas válidas processadas até agora (para validar RES)
    linhas_processadas = []

    for i, entrada in enumerate(entradas):
        linha  = entrada.get("linha", i + 1)
        tokens = entrada.get("tokens", [])

        tem_res = any(t.get("tipo") == "RES" for t in tokens)
        tem_mem = any(t.get("tipo") == "MEM" for t in tokens)

        if tem_mem:
            resultado = gerar_bloco_mem(linha, tokens)
        elif tem_res:
            resultado = gerar_bloco_res(linha, tokens, linhas_processadas)
        else:
            resultado = gerar_bloco_rpn(linha, tokens)

        if resultado is None:
            continue

        variaveis, codigo = resultado
        blocos.append((linha, variaveis, codigo))
        linhas_processadas.append(linha)

    if not blocos:
        print("Nenhuma expressão válida encontrada.")
        return

    # Monta o arquivo
    todas_variaveis = []
    for _, variaveis, _ in blocos:
        todas_variaveis.extend(variaveis)

    # Adiciona variáveis MEM globais ao .data
    todas_variaveis = estrutura_vars_mem() + todas_variaveis

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

# ══════════════════════════════════════════════════════════════
# EXEMPLO DE USO
# Linha 1: 3.0 4.0 +        = 7.00       → result = 700
# Linha 2: 1.5 2.0 * 1.0 + 3.0 4.0 * /
#          = (3.0+1.0)/12.0 = 0.33       → result = 33
# Linha 3: 6.0 2.0 *        = 12.00      → result = 1200
# Linha 4: 7.0 3.0 //       = 2.00       → result = 2
# Linha 5: 2.0 3.0 ^        = 8.00       → result = 800
# Linha 6: 3.0 2.0 ^ 1.0 +  = (9.0+1.0) = 10.00 → result = 1000
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# EXEMPLO DE USO
# Linha 1: 3.0 4.0 +               = 7.00   → result = 700
# Linha 2: 1.5 2.0 * 1.0 + 3.0 4.0 * /
#          = (3.0+1.0)/12.0 = 0.33 → result = 33
# Linha 3: 6.0 2.0 *               = 12.00  → result = 1200
# Linha 4: 7.0 3.0 //              = 2.00   → result = 2
# Linha 5: 2.0 3.0 ^               = 8.00   → result = 800
# Linha 6: 3.0 2.0 ^ 1.0 +         = 10.00  → result = 1000
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# EXEMPLO DE USO
# Linha 1: 3.0 4.0 +               = 7.00   → result = 700
# Linha 2: 1.5 2.0 * 1.0 + 3.0 4.0 * /
#          = (3.0+1.0)/12.0 = 0.33 → result = 33
# Linha 3: 6.0 2.0 *               = 12.00  → result = 1200
# Linha 4: 7.0 3.0 //              = 2.00   → result = 2
# Linha 5: 2.0 3.0 ^               = 8.00   → result = 800
# Linha 6: 3.0 2.0 ^ 1.0 +         = 10.00  → result = 1000
# Linha 7: 7.0 3.0 %               = 1.00   → result = 100
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# EXEMPLO DE USO
# Linha 1: 3.0 4.0 +    = 7.00  → result_linha1 = 700
# Linha 2: 2.0 3.0 *    = 6.00  → result_linha2 = 600
# Linha 3: RES(1)        → copia result_linha2 = 600
# Linha 4: RES(3)        → copia result_linha1 = 700
# Linha 5: RES(10)       → ERRO: linha -5 nao existe
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# EXEMPLO DE USO
# Linha 1: MEM leitura MEN  → 0   (primeira vez, sem escrita)
# Linha 2: 3.0 4.0 +        → 700
# Linha 3: 2.0 MEM escrita MEN → salva 200 em MEN, result = 200
# Linha 4: MEM leitura MEN  → 200 (valor salvo)
# Linha 5: MEM leitura MEN  → 200 (persiste)
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    dados = {
        "linhas": [
            {
                "linha": 1,
                "tokens": [
                    {"tipo": "MEM", "nome": "MEN"}
                ]
            },
            {
                "linha": 2,
                "tokens": [
                    {"tipo": "NUM", "valor": "3.0"},
                    {"tipo": "NUM", "valor": "4.0"},
                    {"tipo": "OP",  "valor": "+"}
                ]
            },
            {
                "linha": 3,
                "tokens": [
                    {"tipo": "NUM", "valor": "2.0"},
                    {"tipo": "MEM", "nome": "MEN"}
                ]
            },
            {
                "linha": 4,
                "tokens": [
                    {"tipo": "MEM", "nome": "MEN"}
                ]
            },
            {
                "linha": 5,
                "tokens": [
                    {"tipo": "MEM", "nome": "MEN"}
                ]
            }
        ]
    }

    gerarassembly(dados)
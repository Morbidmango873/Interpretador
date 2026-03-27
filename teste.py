import sys
import os
import json
from parte1 import parseExpressao
from parte2 import executarExpressao
from parte3 import gerarAssembly

OK  = "\033[92m✓\033[0m"
ERR = "\033[91m✗\033[0m"

def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  {'  OK  ' if ok else ' ERRO '} {nome}")
    if not ok:
        print(f"         obtido={obtido!r}  esperado={esperado!r}")
    return ok

# ── INPUT ──────────────────────────────────────────────────────────────────
LINHAS = [
    "(3 4 +)",
    "(10 2 *)",
    "(20 4 /)",
    "(9 3 //)",
    "(10 3 %)",
    "(2 8 ^)",
    "(7777 MEM)",
    "(MEM 2223 +)",
    "(1 RES 500 *)",
    "(100 50 -)",
]

erros = 0

# ══════════════════════════════════════════════════════════════════════════════
print("\n========== PARTE 1 — Análise Léxica ==========")
tokens = parseExpressao(LINHAS)

erros += 0 if check("retornou 10 linhas",          len(tokens), 10)                   else 1
erros += 0 if check("linha 1: 3 tokens",           len(tokens[0]["tokens"]), 3)       else 1
erros += 0 if check("linha 1: dois NUM + um OP",
    [t["tipo"] for t in tokens[0]["tokens"]], ["NUM","NUM","OP"])                      else 1
erros += 0 if check("linha 7: NUM + MEM",
    [t["tipo"] for t in tokens[6]["tokens"]], ["NUM","MEM"])                           else 1
erros += 0 if check("linha 9: contém RES",
    any(t["tipo"] == "RES" for t in tokens[8]["tokens"]), True)                       else 1
erros += 0 if check("saida_fase1.txt criado",       os.path.isfile("saida_fase1.txt"), True) else 1

# ══════════════════════════════════════════════════════════════════════════════
print("\n========== PARTE 2 — Execução ==========")
resultados = executarExpressao(tokens)

erros += 0 if check("retornou 10 resultados",       len(resultados), 10)              else 1
erros += 0 if check("L1: 3+4 = 7.0",               resultados[0]["resultado"], 7.0)  else 1
erros += 0 if check("L2: 10*2 = 20.0",             resultados[1]["resultado"], 20.0) else 1
erros += 0 if check("L3: 20/4 = 5.0",              resultados[2]["resultado"], 5.0)  else 1
erros += 0 if check("L4: 9//3 = 3.0",              resultados[3]["resultado"], 3.0)  else 1
erros += 0 if check("L5: 10%3 = 1.0",              resultados[4]["resultado"], 1.0)  else 1
erros += 0 if check("L6: 2^8 = 256.0",             resultados[5]["resultado"], 256.0)else 1
erros += 0 if check("L8: MEM+2223 = 10000.0",      resultados[7]["resultado"], 10000.0) else 1
erros += 0 if check("L10: 100-50 = 50.0",          resultados[9]["resultado"], 50.0) else 1

# ══════════════════════════════════════════════════════════════════════════════
print("\n========== PARTE 3 — Geração de Assembly ==========")
gerarAssembly(tokens)

erros += 0 if check("assembly_saida.txt criado",    os.path.isfile("assembly_saida.txt"), True) else 1

with open("assembly_saida.txt", "r", encoding="utf-8") as f:
    asm = f.read()

erros += 0 if check(".section .data presente",      ".section .data"  in asm, True)  else 1
erros += 0 if check(".section .text presente",      ".section .text"  in asm, True)  else 1
erros += 0 if check("_start presente",              "_start:"         in asm, True)  else 1
erros += 0 if check("mem_MEM declarada",            "mem_MEM"         in asm, True)  else 1
erros += 0 if check("todas as 10 linhas geradas",   "linha10:"        in asm, True)  else 1

# ── RESULTADO FINAL ────────────────────────────────────────────────────────
total = 21
print(f"\n{'='*46}")
if erros == 0:
    print(f"  TUDO OK — {total}/{total} verificações passaram")
else:
    print(f"  {erros} FALHA(S) — {total-erros}/{total} verificações passaram")
print(f"{'='*46}\n")

sys.exit(1 if erros else 0)
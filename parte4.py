import json, sys
from parte1 import parseExpressao
from parte2 import executarExpressao
from parte3 import gerarassembly

# LEITURA DO ARQUIVO
def lerArquivo(caminho):

    with open(caminho, "r", encoding="utf-8") as f:
        linhas = f.readlines()
    if len(linhas) < 15:
        linhas_limpas = []
        for linha in linhas:
            limpa = linha.strip()
            if limpa:
                linhas_limpas.append(limpa)

        if not linhas_limpas:
            raise Exception("Arquivo de entrada está vazio.")

        return linhas_limpas
    else:
        print("Arquivo muito grande")


def exibirResultados(resultados):

    print("\n" + "=" * 50)
    print(f"{'RESULTADOS':^50}")
    print("=" * 50)

    for entrada in resultados:
        num_linha = entrada["linha"]
        tokens    = entrada["tokens"]
        resultado = entrada["resultado"]

        partes = []
        for t in tokens:
            if t["tipo"] == "NUM":
                partes.append(t["valor"])
            elif t["tipo"] == "OP":
                partes.append(t["valor"])
            elif t["tipo"] == "MEM":
                partes.append(f"({t['nome']})")
            elif t["tipo"] == "RES":
                partes.append("RES")

        expressao = " ".join(partes)

        if resultado is None:
            resultado_str = "(vazio)"
        elif resultado == int(resultado):
            resultado_str = f"{resultado:.1f}"
        else:
            resultado_str = f"{resultado:.1f}"

        print(f"Linha {num_linha:>3}: {expressao}")
        print(f"         Resultado: {resultado_str}")
        print("-" * 50)

    print()


def salvarResultados(resultados, caminho="saida_fase2.txt"):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)
    print(f"Saída salva em '{caminho}'.")


def main():

    caminho = sys.argv[1]

    print(f"Lendo arquivo: {caminho}")
    linhas = lerArquivo(caminho)
    print(f"{len(linhas)} linha(s) carregada(s).")

    print("\nFase 1 — análise léxica...")
    try:
        tokens_por_linha = parseExpressao(linhas)
    except Exception as e:
        print(f"Erro na Fase 1: {e}")
        return

    print("Fase 1 concluída.")
    
    dados = ler_json_arquivo("saida_fase1.txt")
    gerarassembly(dados)

    print("\nFase 2 — execução das expressões...")
    try:
        resultados = executarExpressao(tokens_por_linha)
    except Exception as e:
        print(f"Erro na Fase 2: {e}")
        return

    print("Fase 2 concluída.")

    exibirResultados(resultados)

    salvarResultados(resultados)


def ler_json_arquivo(caminho: str = "saida_fase1.txt") -> dict | None:

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        print(f"JSON carregado com sucesso de '{caminho}'")
        return dados
    except FileNotFoundError:
        print(f"Erro: arquivo '{caminho}' não encontrado.")
        return None
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return None
 
 
if __name__ == "__main__":
    main()
import json
import sys
import os
from parte1 import parseExpressao
from parte2 import executarExpressao
from parte3 import gerarAssembly
from validador_entrada import validar_arquivo_entrada
from validador_saida_fase1 import validar_saida_fase1
from validador_parte2 import validar_resultados_parte2
# Nome do Grupo: Francisco Hauch Cardoso, ID: Morbidmango873

# CONSTANTES

MIN_LINHAS = 10
MAX_LINHAS = 10


# LEITURA DO ARQUIVO

def lerArquivo(caminho: str) -> list[str]:

    if not os.path.isfile(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: '{caminho}'")

    with open(caminho, "r", encoding="utf-8") as f:
        linhas_brutas = f.readlines()

    # --- limpeza do buffer de entrada (equivalente ao cin.ignore do C++) ---
    # strip() remove \r, \n, espaços à esquerda/direita de cada linha
    linhas_limpas = [linha.strip() for linha in linhas_brutas]

    # descarta linhas completamente vazias após o strip
    linhas_limpas = [linha for linha in linhas_limpas if linha]

    if not linhas_limpas:
        raise ValueError("Arquivo de entrada está vazio.")

    if len(linhas_limpas) < MIN_LINHAS:
        raise ValueError(
            f"Arquivo com poucas linhas: encontradas {len(linhas_limpas)}, "
            f"mínimo exigido: {MIN_LINHAS}."
        )

    if len(linhas_limpas) > MAX_LINHAS:
        linhas_limpas = linhas_limpas[:MAX_LINHAS]

    return linhas_limpas


# EXIBIÇÃO DOS RESULTADOS

def exibirResultados(resultados: list[dict]) -> None:

    print("\n" + "=" * 54)
    print(f"{'RESULTADOS':^54}")
    print("=" * 54)

    for entrada in resultados:
        num_linha = entrada["linha"]
        tokens    = entrada["tokens"]
        resultado = entrada.get("resultado")

        # reconstrói representação textual dos tokens
        partes = []
        for t in tokens:
            tipo = t["tipo"]
            if tipo == "NUM":
                partes.append(t["valor"])
            elif tipo == "OP":
                partes.append(t["valor"])
            elif tipo == "MEM":
                partes.append(f"({t['nome']})")
            elif tipo == "RES":
                partes.append("RES")

        expressao = " ".join(partes)

        if resultado is None:
            resultado_str = "(sem resultado numérico)"
        else:
            # garante exibição com uma casa decimal
            try:
                resultado_str = f"{float(resultado):.1f}"
            except (TypeError, ValueError):
                resultado_str = str(resultado)

        print(f"Linha {num_linha:>3}: {expressao}")
        print(f"         Resultado: {resultado_str}")
        print("-" * 54)

    print()


# PERSISTÊNCIA DOS RESULTADOS

def salvarResultados(resultados: list[dict], caminho: str = "saida_fase2.txt") -> None:

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)


# CARREGAMENTO DO JSON DE TOKENS

def lerJsonArquivo(caminho: str = "saida_fase1.txt") -> list | dict | None:

    if not os.path.isfile(caminho):
        return None

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return dados
    except json.JSONDecodeError:
        return None


# PONTO DE ENTRADA

def main() -> None:
    # --- validação do argumento de linha de comando ---
    if len(sys.argv) < 2:
        print("Uso: python parte4.py <arquivo_de_entrada.txt>")
        sys.exit(1)

    caminho = sys.argv[1]

    try:
        validar_arquivo_entrada(caminho, MIN_LINHAS, MAX_LINHAS)
    except (FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)

    try:
        linhas = lerArquivo(caminho)
    except (FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)

    try:
        tokens_por_linha = parseExpressao(linhas)
    except Exception as e:
        print(e)
        sys.exit(1)
    
    try:
        validar_saida_fase1("saida_fase1.txt", MIN_LINHAS)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(e)
        sys.exit(1)
    
    dados_tokens = lerJsonArquivo("saida_fase1.txt")

    if dados_tokens is None:
        print("Erro ao ler saida_fase1.txt.")
        sys.exit(1)

    try:
        gerarAssembly(dados_tokens)
    except Exception as e:
        print(e)
        sys.exit(1)
    
    try:
        resultados = executarExpressao(tokens_por_linha)
    except Exception as e:
        print(e)
        sys.exit(1)
    
    try:
        validar_resultados_parte2(resultados, MIN_LINHAS)
    except ValueError as e:
        print(e)
        sys.exit(1)

    exibirResultados(resultados)
    salvarResultados(resultados)


if __name__ == "__main__":
    main()

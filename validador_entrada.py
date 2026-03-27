import os


def validar_arquivo_entrada(caminho: str, min_linhas: int = 10, max_linhas: int = 10) -> None:
    if not os.path.isfile(caminho):
        raise FileNotFoundError("Arquivo não encontrado.")

    with open(caminho, "r", encoding="utf-8") as arquivo:
        linhas = [linha.strip() for linha in arquivo.readlines()]

    linhas = [linha for linha in linhas if linha]

    if not linhas:
        raise ValueError("Arquivo vazio.")

    if len(linhas) < min_linhas:
        raise ValueError("Poucas linhas no arquivo.")

    for indice, linha in enumerate(linhas[:max_linhas], start=1):
        if not linha.startswith("(") or not linha.endswith(")"):
            raise ValueError(f"Linha {indice} inválida.")

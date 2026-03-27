import json
import os


def validar_saida_fase1(caminho: str = "saida_fase1.txt", min_linhas: int = 10) -> None:
    if not os.path.isfile(caminho):
        raise FileNotFoundError("Arquivo da parte 1 não encontrado.")

    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("Saída da parte 1 inválida.")

    if len(dados) < min_linhas:
        raise ValueError("Saída da parte 1 incompleta.")

    for indice, entrada in enumerate(dados[:min_linhas], start=1):
        tokens = entrada.get("tokens")
        if not isinstance(tokens, list) or not tokens:
            raise ValueError(f"Linha {indice} sem tokens.")

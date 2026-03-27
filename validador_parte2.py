def validar_resultados_parte2(resultados: list[dict], min_linhas: int = 10) -> None:
    if not isinstance(resultados, list):
        raise ValueError("Saída da parte 2 inválida.")

    if len(resultados) < min_linhas:
        raise ValueError("Saída da parte 2 incompleta.")

    for indice, entrada in enumerate(resultados[:min_linhas], start=1):
        tokens = entrada.get("tokens")
        if not isinstance(tokens, list) or not tokens:
            raise ValueError(f"Linha {indice} sem tokens.")

        if "resultado" not in entrada:
            raise ValueError(f"Linha {indice} sem resultado.")

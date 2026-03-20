# teste.py
def testar_lexer():
    from parte1 import parseExpressao

    # ── válidos ──────────────────────────────────────
    assert parseExpressao(["3.14 2.0 +"]) is not None
    assert parseExpressao(["10 3 -"]) is not None
    assert parseExpressao(["4.0 2.0 *"]) is not None
    assert parseExpressao(["9.0 3.0 /"]) is not None
    assert parseExpressao(["7 2 //"]) is not None
    assert parseExpressao(["7 2 %"]) is not None
    assert parseExpressao(["2.0 3 ^"]) is not None
    # assert parseExpressao(["( 5 RES )"]) is not None
    # assert parseExpressao(["( 10.5 CONTADOR )"]) is not None
    # assert parseExpressao(["( TOTAL )"]) is not None

    # ── inválidos ────────────────────────────────────
    casos_invalidos = [
        "3.14.5 2.0 +",     # número malformado
        "3,45 2 +",          # vírgula como separador
        "2.0 & 3.0",         # operador inválido
        "( 3.14 2.0 +",      # parêntese não fechado
        "abc 2 +",           # identificador minúsculo solto
    ]
    for caso in casos_invalidos:
        try:
            parseExpressao([caso])
            assert False, f"deveria falhar: '{caso}'"
        except Exception:
            pass

    print("Todos os testes passaram.")
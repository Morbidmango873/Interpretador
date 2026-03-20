def testar_lexer():
    from parte1 import parseExpressao

    # válidos
    assert parseExpressao(["3.14 2.0 +"]) is not None
    assert parseExpressao(["( 5 RES )"]) is not None
    assert parseExpressao(["( 10.5 CONTADOR )"]) is not None

    # inválidos
    try:
        parseExpressao(["3.14.5 2.0 +"])
        assert False, "deveria falhar"
    except Exception:
        pass

    try:
        parseExpressao(["3,45 2 +"])
        assert False, "deveria falhar"
    except Exception:
        pass

    print("Todos os testes passaram.")
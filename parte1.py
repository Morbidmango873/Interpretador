

'''

 começar do zero, - estado de marquina- receber a linha pelo parseExpressão então assim iniciar - o programa recebendo o primeiro valor e mandando para o estado que for a ser recebido - nele iremos verificar o Numero - e então aramazenar em um buffer e retornar a função inicial e indo para o proximo caso.
teremos um contador global e a cada vez que consegue uma dupla de operador mais um operando iremos realizar a conta(iremos salvar essa conta no buffer pois iremos gerar o assembly na ordem de tokens do buffer),
caso receba um parenteses adiciona em uma lista e nela iremos verificar 2 coisas tanto a parieadade como os operações. caso recebemos ((1 2 +)3 -) iremso adicionar na pilha de parentese 2 abertos e quando recebermos o de fechar iremos remover dessa lista. se terminarmos a linha e o len(pilha)!= 0 retornamos erro.
caso tenhamos recebido valor invalido iremos retornar erro imediatamente, cada operação será um estado especificando de maneira clara a maquina de estados. - 
A logica para ser maquina de estados é andar com a pilha ou seja não realizar loop for ou while para percorrer a linha, a ideia será assim.

Inicio = parseExpression - verifica o primeiro digito e vê oque é, caso seja Num vai para estado Núm, então no estado Num verifica o segundo após salvar o primeiro nessa Pilha, sendo assim se for número ela ira chamar ela mesma e se foi especial ira para a caegoria verifica os próximos 2 tipo para ver o ponto e caso de parensetes, especial seria RES, MEN, ( )
se for especial iremos verificar qual é se for MEN ou RES iremos para o estado final- para geramos nosso json.
caso seja parenteses iremos adiconar na nossa lista de parenteses e sempre que vier um fechando excluimos o aberto - caso entre em parenteses reseta a contagem de Operando global salvando ela na variavel de controle para podermos retornar quando fecharmos - pois precisaremos 2 de novos.
toda vez que fechar uma combinação de 2 numero e 1 operando iremos salvar essa combinação na lista do resultado final e apagar do buffer e zerar global para mantermos o controle, quando entrar no parenteses apesar de zerar o global não iremos remover do buffer, quando recebemos o parenteses de fechar além de excluir podemos pegar a informação da variavel global que foi zerada quando abriu parentese e readicionar podemos chamr de globaldecontroledoparentese.

Precisamos verificar caso o número possua ponto, ou seja 3.14 - temos que salvar esse numero tudo junto e verifcar caso entre 3.14.5 e colocar como invalido não precisamos ter números negativos então menos 1 dor de cabeça~, a ideia do programa é só ir para o estado final quando acabar a linha todos os estados iram verificar qual é o proximo token da linha, nesse estado final de alguma maneira quando acabar todas as linhas iremos gerar um json com nome saida_fase1.txt que terá os tokens validados, ou seja ficara as expressoes. como estara na ordem de resolução da linha não precisa adicionar os parênteses.
os outros estados especiais que são MEN e RES irão sera salvos com o número que os precede e nome da Função como está abaixo. caso seja o MEN isolado sem número o precedendo iremos salvar 0.0, como não precisamos resolver nada só iremos salvar os operandos e seu operador a lista de operadores é (+, -, *, /, %, ^)  

todos abaixo são testes validos.

(3.14 2.0 +)
((1.5 2.0 *) (3.0 4.0 *) /)
(5.0 MEM)
(1 RES)


"linha": 3,
        "tokens": [
            {
                "tipo": "STORE",
                "mem": "MEM",
                "valor": "5.0"
            }
        ]
    },
    {
        "linha": 4,
        "tokens": [
            {
                "tipo": "RES",
                "valor": 1
            }
        ]
    }
 
 
 
 
 
 
 
 '''
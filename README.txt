Método de uso - 

Rodar o programa parte4.py teste.txt ou teste1.txt ou teste2.txt

Todos os programas acima são os teste todos tendo todas as operações e com 10 linhas cada limite maximo do programa

Após isso termoe a saida_assembly.txt que é nosso código para colar no CPUlator - após colar basta ativar a opção de 32 leds e segurar F2 que ele printara todos os números nos 32 leds.


Dentro do diretorio também possui 3 validadores que iram verifica os arquivos durante a execução.



PROJETO DE INTERPRETADORES
Sistema de leitura, analise, execucao e geracao de Assembly ARMv7 para expressoes em notacao pos-fixa - Analisador Léxico seguindo modelo de Máquinas de Estado Finito

1. VISAO GERAL

Este projeto foi desenvolvido em Python e esta dividido em quatro partes principais:

- parte1.py: faz a analise lexica das expressoes de entrada.
- parte2.py: executa semanticamente as expressoes e calcula os resultados.
- parte3.py: gera um arquivo Assembly ARMv7 com instrucoes VFP em dupla precisao.
- parte4.py: integra todo o fluxo do sistema, desde a leitura do arquivo ate a geracao das saidas.

O sistema processa expressoes em notacao pos-fixa (RPN - Reverse Polish Notation), uma por linha, com suporte a:

- numeros reais positivos
- operadores aritmeticos
- memoria simbolica com MEM
- reutilizacao de resultados anteriores com RES
- geracao de codigo Assembly para ARMv7


2. ESTRUTURA DOS ARQUIVOS

Os arquivos principais do projeto sao:

- parte1.py
- parte2.py
- parte3.py
- parte4.py
- entrada.txt
- entrada1.txt
- entrada2.txt
- saida_fase1.txt
- saida_fase2.txt
- assembly_saida.txt

Arquivos gerados pelo programa:

- saida_fase1.txt: tokens reconhecidos na etapa de analise.
- saida_fase2.txt: resultados numericos das expressoes.
- assembly_saida.txt: codigo Assembly ARMv7 gerado a partir dos tokens.


3. COMO EXECUTAR

O ponto de entrada do sistema e o arquivo parte4.py.

Comando:

python parte4.py <arquivo_de_entrada.txt>

Exemplo:

python parte4.py entrada.txt

Regras de leitura:

- o programa exige exatamente 10 linhas uteis de entrada
- linhas vazias sao descartadas
- se houver mais de 10 linhas, apenas as 10 primeiras sao processadas
- se houver menos de 10 linhas, a execucao e encerrada com erro


4. FORMATO DA ENTRADA

Cada linha do arquivo deve conter uma expressao em notacao pos-fixa, normalmente envolvida por parenteses.

Exemplos validos:

(129 98721 +)
(50 12789 -)
(145 6790 *)
(987321 3 /)
(999 7 //)
(123456789 1000 %)
(12 5 ^)
(7777 MEM)
(MEM 2223 +)
(1 RES 2500 *)

O sistema entende os seguintes elementos:

- NUM: numero
- OP: operador
- MEM: memoria simbolica
- RES: referencia a resultado anterior
- parenteses para agrupamento


5. OPERADORES SUPORTADOS

O projeto aceita os seguintes operadores:

- +   soma
- -   subtracao
- *   multiplicacao
- /   divisao em ponto flutuante
- //  divisao inteira
- %   resto
- ^   potencia

Comportamento atual:

- +, -, * e / usam float64 no executor Python e instrucoes VFP double no Assembly
- / agora trata explicitamente casos IEEE 754 sensiveis, inclusive divisao por zero com geracao de NaN ou infinito com sinal
- // agora arredonda o quociente em ponto flutuante segundo o modo IEEE configurado no codigo, sem converter previamente os operandos para int
- % agora usa a identidade a - q*b com q arredondado pelo mesmo modo IEEE configurado
- NAN, INF e INFINITY podem ser usados como literais numericos de entrada
- ^ aceita apenas expoente inteiro positivo

O projeto passou a preservar e documentar explicitamente NaN, infinito, subnormais, overflow, underflow e modos de arredondamento, dentro do suporte disponivel em Python float64 e no VFP ARMv7.

6. MEMORIA COM MEM

O token MEM pode funcionar de duas formas:

6.1. STORE

Quando MEM aparece no final da linha e ja existe um valor no topo da pilha, esse valor e armazenado na memoria com o nome informado.

Exemplo:

(7777 MEM)

Significado:

- o valor 7777 e salvo em uma posicao de memoria chamada MEM
- o valor tambem permanece como resultado final da linha

Outro exemplo com nome explicito:

(126418.20 CACHE)

Significado:

- o valor 126418.20 e salvo na memoria simbolica CACHE
- o resultado final da linha continua sendo 126418.20

6.2. LOAD

Quando o identificador de memoria aparece sem valor anterior na pilha, ele e tratado como leitura.

Exemplo:

(CACHE 10 /)

Significado:

- o valor guardado em CACHE e carregado
- depois esse valor e dividido por 10

Se a memoria ainda nao tiver sido inicializada, o valor padrao usado e 0.0.


7. REUTILIZACAO DE RESULTADOS COM RES

RES permite acessar o resultado de uma linha anterior.

Exemplo:

(1 RES 2500 *)

Significado:

- 1 indica quantas linhas voltar no historico
- RES busca o resultado da linha anterior
- o valor recuperado e multiplicado por 2500

Regra de funcionamento:

- RES sempre depende de um numero imediatamente anterior na semantica da expressao
- esse numero indica o deslocamento no historico
- RES(1) significa "resultado da linha imediatamente anterior"
- RES(2) significa "resultado de duas linhas atras"

Se o indice apontar para uma linha inexistente, a execucao gera erro.


8. PARTE 1 - ANALISE LEXICA

Arquivo responsavel:

- parte1.py

Objetivo:

- ler cada linha do arquivo de entrada
- reconhecer numeros, operadores, MEM, RES e parenteses
- validar erros sintaticos simples
- salvar os tokens em JSON
- Seguir o padrão de Maquina de estado Finito

Principais funcoes:

- parseExpressao(linhas): funcao principal da fase 1
- estadoInicial(...): escolhe o estado adequado conforme o caractere lido
- estadoNumero(...): reconhece numeros decimais
- estadoOperador(...): reconhece operadores
- estadoRES(...): reconhece a palavra RES
- estadoMEM(...): reconhece identificadores simbolicos em letras maiusculas
- estadoFechaParentese(...): fecha um contexto aberto
- estadoFinal(...): grava a saida em arquivo

O resultado da fase 1 e salvo em:

- saida_fase1.txt

Formato real de saida:

[
    {
        "linha": 1,
        "tokens": [
            {"tipo": "NUM", "valor": "400.0"},
            {"tipo": "NUM", "valor": "6.87"},
            {"tipo": "OP", "valor": "+"}
        ]
    }
]

Cada linha do arquivo original e convertida em uma lista de tokens reconhecidos.


9. PARTE 2 - EXECUCAO DAS EXPRESSOES

Arquivo responsavel:

- parte2.py

Objetivo:

- percorrer os tokens de cada linha
- simular uma pilha de execucao
- aplicar operadores
- controlar memoria e historico
- produzir o resultado final de cada linha

Principais componentes:

- formatarResultado(valor): ajusta o valor para formato double
- aplicarOperador(a, b, op): executa a operacao
- executarExpressao(dados): processa todas as linhas

Funcionamento interno:

- NUM empilha um valor float
- OP desempilha dois operandos e empilha o resultado
- MEM pode salvar ou carregar valor
- RES recupera um resultado anterior

Exemplo de saida real em saida_fase2.txt:

[
    {
        "linha": 1,
        "tokens": [
            {"tipo": "NUM", "valor": "400.0"},
            {"tipo": "NUM", "valor": "6.87"},
            {"tipo": "OP", "valor": "+"}
        ],
        "resultado": 406.87
    }
]

Observacoes:

- os resultados sao armazenados em historico para uso posterior por RES
- uma linha com STORE em MEM tambem entra no historico
- o executor usa float64 do Python, com tratamento explicito para NaN, infinito, subnormais e divisao por zero


10. PARTE 3 - GERACAO DE ASSEMBLY ARMv7

Arquivo responsavel:

- parte3.py

Objetivo:

- transformar os tokens em um programa Assembly ARMv7
- usar registradores double do VFP
- criar uma secao .data com constantes e resultados
- criar uma secao .text com a execucao de cada linha
- exibir os bits do resultado nos LEDs do CPUlator

Caracteristicas do Assembly gerado:

- arquitetura ARMv7
- uso de VFP double precision
- registradores D para ponto flutuante
- uso de VPUSH e VPOP para simular pilha
- armazenamento de resultados em memoria

Estrutura geral do arquivo gerado:

- cabecalho textual
- secao .data
- secao .text
- label para cada linha
- rotinas auxiliares de LEDs
- encerramento do programa

10.1. Secao .data

Nessa secao sao gerados:

- constantes numericas
- variaveis de resultado
- variaveis globais de memoria MEM

Exemplo:

.section .data
    cst_linha1_0: .double 400.0000000000
    cst_linha1_1: .double 6.8700000000
    result_linha1: .double 0.0
    mem_CACHE: .double 0.0

10.2. Secao .text

Cada expressao gera um bloco de codigo com um label proprio:

linha1:
linha2:
linha3:

Dentro de cada bloco:

- numeros sao carregados com VLDR
- resultados parciais sao empilhados com VPUSH
- operadores usam instrucoes VFP como VADD.F64, VSUB.F64, VMUL.F64 e VDIV.F64
- o resultado final vai para result_linhaX

10.3. Exibicao nos LEDs

Ao final de cada linha:

- o resultado e carregado da memoria
- seus 64 bits sao movidos para registradores inteiros
- os 32 bits menos significativos sao exibidos
- depois os 32 bits mais significativos sao exibidos

Isso permite visualizar no CPUlator o conteudo binario do double gerado.


11. PARTE 4 - ORQUESTRACAO GERAL

Arquivo responsavel:

- parte4.py

Objetivo:

- ler o arquivo de entrada
- executar a parte 1
- gerar o Assembly da parte 3
- executar semanticamente a parte 2
- exibir os resultados no terminal
- salvar os arquivos de saida

Fluxo principal:

1. Leitura do arquivo de entrada
2. Validacao da quantidade de linhas
3. Analise lexica
4. Gravacao de saida_fase1.txt
5. Geracao de assembly_saida.txt
6. Execucao semantica
7. Exibicao dos resultados
8. Gravacao de saida_fase2.txt


12. SAIDAS GERADAS PELO SISTEMA

O projeto produz tres tipos principais de saida.

12.1. Saida no terminal

Ao executar parte4.py, o programa informa:

- leitura do arquivo
- quantidade de linhas carregadas
- status da parte 1
- status da geracao do Assembly
- status da fase 2
- tabela textual de resultados

Exemplo resumido:

Lendo arquivo: 'entrada1.txt'
10 linha(s) carregada(s).
[Parte 1] Analise lexica...
[Parte 1] Concluida. Tokens salvos em 'saida_fase1.txt'.
[Parte 3] Gerando Assembly ARMv7...
[Fase 2] Executando expressoes...
[Fase 2] Concluida.

12.2. Arquivo saida_fase1.txt

Contem o JSON com os tokens de cada linha.

Utilidade:

- depuracao da fase lexica
- validacao do reconhecimento dos elementos da linguagem
- entrada intermediaria para a geracao de Assembly

12.3. Arquivo saida_fase2.txt

Contem o JSON com:

- numero da linha
- tokens reconhecidos
- resultado calculado

Utilidade:

- conferencia dos calculos
- comparacao entre linhas
- validacao do historico usado por RES

12.4. Arquivo assembly_saida.txt

Contem o programa Assembly ARMv7 completo.

Utilidade:

- execucao no CPUlator ou ambiente compativel
- visualizacao do comportamento da pilha VFP
- estudo da traducao da RPN para Assembly


13. EXEMPLO DE COMPORTAMENTO COM OS ARQUIVOS DISPONIVEIS

Com base no conteudo atual de entrada1.txt:

(400 6.87 +)
(945679 1654651.1 -)
(123876 789.12 *)
(8888 9 /)
(92345.21 11 //)
(9835465.21 11 %)
(9 6 ^)
(126418.20 CACHE)
(CACHER 10 /)
(1 RES 2 ^)

Resultados observados em saida_fase2.txt:

- linha 1: 406.87
- linha 2: -708972.1000000001
- linha 3: 97753029.12
- linha 4: 987.5555555555555
- linha 5: 8395.0
- linha 6: 2.0
- linha 7: 531441.0
- linha 8: 126418.2
- linha 9: 0.0
- linha 10: 0.0

Explicacao de dois casos importantes:

- linha 9 usa CACHER, mas a linha 8 armazenou valor em CACHE. Como CACHER nao foi inicializada, o valor lido e 0.0.
- linha 10 usa RES(1), portanto recupera o resultado da linha 9, que foi 0.0. Em seguida calcula 0.0 ^ 2.0, resultando em 0.0.


14. RESUMO FINAL

Este projeto:
- le um arquivo com 10 expressoes em RPN
- converte cada linha em tokens
- executa semanticamente as expressoes
- permite armazenar valores em memoria simbolica
- permite reutilizar resultados anteriores
- gera um arquivo Assembly ARMv7 com operacoes VFP
- salva os resultados intermediarios e finais em arquivos

# ClientServerBasics 2.0 — Servidor multifuncional

Extensão do exemplo cliente-servidor da **Fig. 2.3** do livro *Distributed Systems* (van Steen & Tanenbaum, 4ª ed.), apresentado no Cap. 2, slide 5 da disciplina de Sistemas Distribuídos (UFG).

No exemplo original, o servidor só devolve o texto recebido com um `*` no final. Nesta versão:

1. **o servidor processa a requisição**: calcula, transforma texto e guarda um histórico;
2. **o cliente pode chamar várias funcionalidades diferentes numa única requisição**, separadas por `|`.

Autora: Jessyca Rodrigues Silva — tarefa individual.

---

## Arquivos

| Arquivo | Função |
|---|---|
| `constCS.py` | `HOST` (IP do servidor) e `PORT` (5678), usados pelos dois lados |
| `server.py` | servidor TCP: recebe requisições, executa as operações e responde |
| `client.py` | cliente TCP: modo demonstração ou modo interativo |

---

## Protocolo de aplicação

O socket TCP só transporta um fluxo de bytes. O formato das mensagens foi definido neste trabalho:

```
requisição := chamada { '|' chamada } '\n'
chamada    := OPERAÇÃO [ ' ' argumentos ]
resposta   := resultado { ' | ' resultado } '\n'
```

- `|` separa as chamadas dentro de uma mesma requisição.
- `\n` marca o fim de uma mensagem (**enquadramento**). Como o TCP não preserva limites de mensagem, uma requisição pode chegar partida em vários `recv()` ou junto com outra. O servidor acumula o que chega num buffer e só processa ao encontrar `\n`.
- A resposta traz um resultado por chamada, **na mesma ordem**.
- Se uma chamada falhar (divisão por zero, operação inexistente, argumento inválido), só aquele resultado vira `ERRO ...`; as outras chamadas da requisição são executadas normalmente.

Exemplo:

```
--> SOMA 2 3 | MUL 4 5 | DIV 10 4
<-- 5 | 20 | 2.5
```

---

## Operações oferecidas

| Operação | Argumentos | Resultado | Exemplo |
|---|---|---|---|
| `SOMA` | 1 ou mais números | soma | `SOMA 10 20 30` → `60` |
| `SUB` | 1 ou mais números | primeiro menos os demais | `SUB 10 3 2` → `5` |
| `MUL` | 1 ou mais números | produto | `MUL 4 5` → `20` |
| `DIV` | exatamente 2 números | divisão (erro se divisor = 0) | `DIV 10 4` → `2.5` |
| `MEDIA` | 1 ou mais números | média aritmética | `MEDIA 7 8 9` → `8` |
| `MAIUSC` | texto | texto em maiúsculas | `MAIUSC ufg` → `UFG` |
| `INVERTE` | texto | texto invertido | `INVERTE UFG` → `GFU` |
| `PALAVRAS` | texto | número de palavras | `PALAVRAS a b c` → `3` |
| `HIST` | — | últimas 10 chamadas executadas no servidor | `HIST` |
| `AJUDA` | — | lista de operações disponíveis | `AJUDA` |

O nome da operação não diferencia maiúsculas de minúsculas (`soma` = `SOMA`).

---

## Organização do servidor

O `server.py` segue a visão tradicional de três camadas (Cap. 2, slide 6):

- **Camada de dados**: a lista `historico`, que guarda estado entre requisições e entre clientes.
- **Camada de processamento**: as funções `op_*`. Nenhuma delas conhece sockets ou o formato da mensagem.
- **Camada de interface**: `processa()` separa as chamadas pelo `|` e `executa()` localiza cada operação na tabela `OPERACOES`, trata erros e monta a resposta.

Para acrescentar uma funcionalidade, basta escrever uma função `op_nova(args)` e registrá-la no dicionário `OPERACOES`.

---

## Como executar

Requer apenas Python 3 (biblioteca padrão).

### Na mesma máquina

```bash
python3 server.py              # terminal 1
python3 client.py localhost    # terminal 2 (demonstração)
python3 client.py localhost -i # terminal 2 (interativo)
```

### Em duas instâncias EC2 (AWS)

1. As duas instâncias devem estar na mesma VPC. No **Security Group** do servidor, crie uma regra de entrada *Custom TCP*, porta `5678`, com origem igual ao security group das instâncias.
2. Nas duas máquinas: `git clone <URL deste repositório>` e `cd` para a pasta.
3. Em `constCS.py`, coloque em `HOST` o **IP privado** da instância do servidor.
4. No servidor: `python3 server.py`.
5. No cliente: `python3 client.py` (demonstração) ou `python3 client.py -i` (interativo).

---

## Saída de exemplo (modo demonstração)

```
Conectando em 172.31.35.200:5678 ...
--> AJUDA
<-- operacoes: AJUDA DIV HIST INVERTE MAIUSC MEDIA MUL PALAVRAS SOMA SUB

--> SOMA 10 20 30
<-- 60

--> SOMA 2 3 | MUL 4 5 | DIV 10 4
<-- 5 | 20 | 2.5

--> MAIUSC sistemas distribuidos | INVERTE UFG | PALAVRAS o cliente pede e o servidor faz
<-- SISTEMAS DISTRIBUIDOS | GFU | 7

--> MEDIA 7 8 9 | DIV 1 0 | RAIZ 9
<-- 8 | ERRO em DIV: divisao por zero | ERRO: operacao desconhecida "RAIZ"

--> HIST
<-- AJUDA; SOMA 10 20 30; SOMA 2 3; MUL 4 5; DIV 10 4; MAIUSC sistemas distribuidos; INVERTE UFG; PALAVRAS o cliente pede e o servidor faz; MEDIA 7 8 9
```

---

## Limitações conhecidas

- O servidor atende **um cliente por vez** (um único fluxo de execução). Atender vários ao mesmo tempo exigiria threads ou processos (Cap. 3).
- O caractere `|` não pode aparecer dentro de um argumento de texto, pois é o separador de chamadas.
- O histórico fica em memória e é perdido quando o servidor é encerrado.
- Não há autenticação nem criptografia: a porta deve ficar acessível apenas às instâncias do próprio security group.

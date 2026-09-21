"""Cliente do servidor multifuncional.

Uso:
    python3 client.py                 -> demonstracao, servidor em constCS.HOST
    python3 client.py localhost       -> demonstracao, servidor na mesma maquina
    python3 client.py -i              -> modo interativo (voce digita as requisicoes)
    python3 client.py 172.31.x.x -i   -> interativo contra outro endereco
"""
import sys
from socket import *
from constCS import HOST, PORT

args = sys.argv[1:]
interativo = '-i' in args
resto = [a for a in args if a != '-i']
host = resto[0] if resto else HOST

# Cada string e UMA requisicao; o '|' separa varias funcionalidades nela.
DEMONSTRACAO = [
    'AJUDA',
    'SOMA 10 20 30',
    'SOMA 2 3 | MUL 4 5 | DIV 10 4',                  # 3 operacoes numa requisicao
    'MAIUSC sistemas distribuidos | INVERTE UFG | PALAVRAS o cliente pede e o servidor faz',
    'MEDIA 7 8 9 | DIV 1 0 | RAIZ 9',                 # erros parciais: o resto continua
    'HIST',                                           # estado guardado no servidor
]


def envia(sock, requisicao):
    """Envia uma requisicao e le a resposta ate o '\\n' final."""
    sock.send((requisicao + '\n').encode())
    buffer = ''
    while '\n' not in buffer:
        parte = sock.recv(1024).decode()
        if not parte:
            raise ConnectionError('servidor fechou a conexao')
        buffer += parte
    return buffer.split('\n', 1)[0]


s = socket(AF_INET, SOCK_STREAM)
print('Conectando em %s:%d ...' % (host, PORT))
s.connect((host, PORT))            # bloqueia ate o servidor aceitar

if interativo:
    print('Digite requisicoes (ex.: SOMA 2 3 | MAIUSC ufg). Linha vazia encerra.')
    while True:
        req = input('> ').strip()
        if not req:
            break
        print('  ', envia(s, req))
else:
    for req in DEMONSTRACAO:
        print('-->', req)
        print('<--', envia(s, req))
        print()

s.close()

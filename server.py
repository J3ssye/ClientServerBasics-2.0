"""Servidor multifuncional - extensao do exemplo da Fig. 2.3 (Cap. 2, slide 5).

Protocolo de aplicacao (definido por nos; o socket so transporta bytes):

    requisicao := chamada { '|' chamada } '\n'
    chamada    := OPERACAO [ ' ' argumentos ]
    resposta   := resultado { '|' resultado } '\n'

Exemplo:  "SOMA 2 3 | MAIUSC ufg | MEDIA 7 8 9\n"
Resposta: "5 | UFG | 8\n"

O servidor esta organizado nas tres camadas do slide 6 do Cap. 2:
dados, processamento e interface.
"""
from socket import *
from constCS import PORT

# ---------------------------------------------------------------------
# CAMADA DE DADOS - estado mantido pelo servidor entre requisicoes
# ---------------------------------------------------------------------
historico = []            # guarda as chamadas ja executadas


# ---------------------------------------------------------------------
# CAMADA DE PROCESSAMENTO - as funcionalidades oferecidas aos clientes.
# Nenhuma funcao aqui sabe que existe rede, socket ou o separador '|'.
# ---------------------------------------------------------------------
def numeros(args):
    """Converte 'a b c' em lista de numeros. Levanta erro se nao for numero."""
    if not args.strip():
        raise ValueError('informe ao menos um numero')
    return [float(x) for x in args.split()]


def fmt(x):
    """Mostra 5 em vez de 5.0 quando o resultado e inteiro."""
    return str(int(x)) if x == int(x) else str(round(x, 4))


def op_soma(args):
    return fmt(sum(numeros(args)))


def op_sub(args):
    n = numeros(args)
    r = n[0]
    for x in n[1:]:
        r -= x
    return fmt(r)


def op_mul(args):
    r = 1
    for x in numeros(args):
        r *= x
    return fmt(r)


def op_div(args):
    n = numeros(args)
    if len(n) != 2:
        raise ValueError('DIV exige exatamente 2 numeros')
    if n[1] == 0:
        raise ValueError('divisao por zero')
    return fmt(n[0] / n[1])


def op_media(args):
    n = numeros(args)
    return fmt(sum(n) / len(n))


def op_maiusc(args):
    return args.upper()


def op_inverte(args):
    return args[::-1]


def op_palavras(args):
    return str(len(args.split()))


def op_hist(args):
    return '; '.join(historico[-10:]) if historico else '(vazio)'


def op_ajuda(args):
    return 'operacoes: ' + ' '.join(sorted(OPERACOES))


# Tabela de despacho: nome da operacao -> funcao que a executa.
# E a INTERFACE do servico. Acrescentar funcionalidade = acrescentar 1 linha.
OPERACOES = {
    'SOMA': op_soma, 'SUB': op_sub, 'MUL': op_mul, 'DIV': op_div,
    'MEDIA': op_media, 'MAIUSC': op_maiusc, 'INVERTE': op_inverte,
    'PALAVRAS': op_palavras, 'HIST': op_hist, 'AJUDA': op_ajuda,
}


# ---------------------------------------------------------------------
# CAMADA DE INTERFACE - interpreta a mensagem e monta a resposta
# ---------------------------------------------------------------------
def executa(chamada):
    """Executa UMA chamada, ex.: 'SOMA 2 3'."""
    partes = chamada.strip().split(' ', 1)
    nome = partes[0].upper()
    args = partes[1] if len(partes) > 1 else ''
    if nome not in OPERACOES:
        return 'ERRO: operacao desconhecida "%s"' % nome
    try:
        resultado = OPERACOES[nome](args)
    except Exception as e:                  # erro numa chamada nao derruba as outras
        return 'ERRO em %s: %s' % (nome, e)
    if nome != 'HIST':
        historico.append(chamada.strip())
    return resultado


def processa(requisicao):
    """Uma requisicao pode ter varias chamadas separadas por '|'."""
    return ' | '.join(executa(c) for c in requisicao.split('|'))


# ---------------------------------------------------------------------
# Laco principal (mesma estrutura da Fig. 2.3, com bind/listen explicitos)
# ---------------------------------------------------------------------
s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)   # permite reiniciar sem esperar a porta liberar
s.bind(('', PORT))        # '' = aceita conexoes em qualquer interface da maquina
s.listen(1)
print('Servidor ouvindo na porta', PORT, flush=True)

while True:                                 # atende um cliente depois do outro
    (conn, addr) = s.accept()               # bloqueia ate um cliente conectar
    print('Cliente conectado:', addr, flush=True)
    buffer = ''
    while True:
        data = conn.recv(1024)              # recebe dados do cliente
        if not data:                        # cliente fechou a conexao
            break
        buffer += data.decode()
        while '\n' in buffer:               # '\n' marca o fim de cada requisicao
            requisicao, buffer = buffer.split('\n', 1)
            print('  <-', requisicao, flush=True)
            resposta = processa(requisicao)
            print('  ->', resposta, flush=True)
            conn.send((resposta + '\n').encode())
    conn.close()
    print('Cliente desconectado:', addr, flush=True)

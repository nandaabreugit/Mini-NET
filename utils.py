#utils.py-funcoes auxiliares e logs

import time
import json
from datetime import datetime

class Cores:
    #define cores para mensagens no terminal
    VERMELHO = '\033[91m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CIANO = '\033[96m'
    RESET = '\033[0m'
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        VERMELHO = VERDE = AMARELO = AZUL = MAGENTA = CIANO = RESET = ''

def log_aplicacao(msg):
    #mostra log da aplicacao
    print(f"{Cores.VERDE}[APLICACAO] {msg}{Cores.RESET}")

def log_transporte(msg):
    #mostra log do transporte
    print(f"{Cores.AZUL}[TRANSPORTE] {msg}{Cores.RESET}")

def log_rede(msg):
    #mostra log da rede
    print(f"{Cores.CIANO}[REDE] {msg}{Cores.RESET}")

def log_enlace(msg):
    #mostra log do enlace
    print(f"{Cores.MAGENTA}[ENLACE] {msg}{Cores.RESET}")

def log_fisica(msg):
    #mostra log da camada fisica
    print(f"{Cores.AMARELO}[FISICA] {msg}{Cores.RESET}")

def log_erro(msg):
    #mostra log de erro
    print(f"{Cores.VERMELHO}[ERRO] {msg}{Cores.RESET}")

def criar_mensagem_json(tipo, sender, mensagem):
    #cria estrutura padrao de mensagem
    return {
        "type": tipo,
        "sender": sender,
        "message": mensagem,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
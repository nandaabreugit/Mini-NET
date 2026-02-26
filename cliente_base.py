import socket
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from protocolo import enviar_pela_rede_ruidosa
import config
from utils import log_erro
from camada_aplicacao import CamadaAplicacao
from camada_transporte import CamadaTransporte
from camada_rede import CamadaRede
from camada_enlace import CamadaEnlace

class ClienteBase:
    def __init__(self, vip, mac, porta, nome, gui):
        self.gui = gui
        self.nome = nome
        self.vip = vip
        self.mac = mac
        self.porta = porta
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', porta))
        self.socket.settimeout(0.5)
        self.executando = True
        self._encerrado = False
        
        print(f"Inicializando {nome}...")
        
        self.enlace = CamadaEnlace(mac, self._enviar_fisica)
        self.rede = CamadaRede(vip, self.enlace.enviar_quadro, usar_roteador=True)
        self.transporte = CamadaTransporte(self._enviar_rede, nome=nome, gui=gui)
        self.aplicacao = CamadaAplicacao(nome, self.transporte.enviar_segmento, gui=gui)

        self.enlace.definir_callback_recebimento(self.rede.receber_pacote)
        self.rede.definir_callback_recebimento(self.transporte.receber_segmento)
        
        self.transporte.callback_recebido = self.aplicacao.receber_mensagem
        self.transporte.iniciar()
        
        self.thread_receber = threading.Thread(target=self._receber_mensagens, daemon=True)
        self.thread_receber.start()
        
        print(f"{nome} inicializado com sucesso!")

    def _enviar_rede(self, dados_transporte):
        self.rede.enviar_pacote(dados_transporte, config.VIP_SERVIDOR)
    
    def _enviar_fisica(self, bytes_dados, endereco_destino):
        enviar_pela_rede_ruidosa(self.socket, bytes_dados, endereco_destino)
    
    def _receber_mensagens(self):
        while self.executando:
            try:
                dados, endereco = self.socket.recvfrom(4096)
                self.enlace.receber_bytes(dados, endereco)
            except socket.timeout:
                continue
            except Exception as e:
                if self.executando:
                    log_erro(f"erro no recebimento: {e}")
    
    def enviar_mensagem(self, mensagem):
        if mensagem and self.aplicacao:
            self.aplicacao.enviar_mensagem(mensagem)
    
    def parar(self):
        if self._encerrado:
            return
        self._encerrado = True
        self.executando = False
        self.transporte.parar()
        self.aplicacao.parar()
        self.socket.close()
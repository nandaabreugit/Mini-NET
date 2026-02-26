#servidor.py-versao inicial

import socket
import sys
from protocolo import enviar_pela_rede_ruidosa
import config
from utils import log_aplicacao, log_erro
from camada_aplicacao import CamadaAplicacao
from camada_transporte import CamadaTransporte
from camada_rede import CamadaRede
from camada_enlace import CamadaEnlace

class Servidor:
    def __init__(self):
        #cria socket e inicia camadas
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((config.SERVIDOR_IP, config.SERVIDOR_PORTA))
        self.socket.settimeout(0.5)
        self.executando = True
        self.cliente_endereco = None
        
        self.enlace = CamadaEnlace(config.MAC_SERVIDOR, self._enviar_fisica)
        self.rede = CamadaRede(config.VIP_SERVIDOR, self.enlace.enviar_quadro)
        self.transporte = CamadaTransporte(self._enviar_rede)
        self.aplicacao = CamadaAplicacao("Servidor", self.transporte.enviar_segmento)

        self.enlace.definir_callback_recebimento(self.rede.receber_pacote)
        self.rede.definir_callback_recebimento(self.transporte.receber_segmento)
        
        self.transporte.callback_recebido = self.aplicacao.receber_mensagem
        self.transporte.iniciar()

    def _enviar_rede(self, dados_transporte):
        if self.cliente_endereco:
            self.rede.enviar_pacote(dados_transporte, config.VIP_CLIENTE)
    
    def _enviar_fisica(self, bytes_dados, endereco_destino):
        #envia bytes para destino no udp
        enviar_pela_rede_ruidosa(self.socket, bytes_dados, endereco_destino)
    
    def iniciar(self):
        #recebe dados e repassa para transporte
        log_aplicacao("servidor iniciado")
        try:
            while self.executando:
                try:
                    dados, endereco = self.socket.recvfrom(4096)
                    if self.cliente_endereco is None:
                        self.cliente_endereco = endereco
                    self.enlace.receber_bytes(dados, endereco)
                except socket.timeout:
                    continue
        finally:
            self.parar()
    
    def parar(self):
        #encerra servidor e fecha recursos
        self.executando = False
        self.transporte.parar()
        self.aplicacao.parar()
        self.socket.close()

if __name__ == "__main__":
    servidor = Servidor()
    try:
        servidor.iniciar()
    except KeyboardInterrupt:
        servidor.parar()
        sys.exit(0)
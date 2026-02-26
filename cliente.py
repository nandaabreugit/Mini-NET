#cliente.py - versao inicial

import socket
import sys
from protocolo import enviar_pela_rede_ruidosa
import config
from utils import log_aplicacao, log_erro
from camada_aplicacao import CamadaAplicacao
from camada_transporte import CamadaTransporte
from camada_rede import CamadaRede
from camada_enlace import CamadaEnlace


class Cliente:
    def __init__(self):
        #cria socket e inicializa camadas
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((config.CLIENTE_IP, config.CLIENTE_PORTA))
        self.socket.settimeout(0.5)
        self.executando = True
        
        self.enlace = CamadaEnlace(config.MAC_CLIENTE, self._enviar_fisica)
        self.rede = CamadaRede(config.VIP_CLIENTE, self.enlace.enviar_quadro)
        self.transporte = CamadaTransporte(self._enviar_rede)
        self.aplicacao = CamadaAplicacao("Cliente", self.transporte.enviar_segmento)

        self.enlace.definir_callback_recebimento(self.rede.receber_pacote)
        self.rede.definir_callback_recebimento(self.transporte.receber_segmento)
        
        self.transporte.callback_recebido = self.aplicacao.receber_mensagem
        self.transporte.iniciar()

    def _enviar_rede(self, dados_transporte):
        self.rede.enviar_pacote(dados_transporte, config.VIP_SERVIDOR)

    
    def _enviar_fisica(self, bytes_dados, endereco_destino):
        enviar_pela_rede_ruidosa(self.socket, bytes_dados, endereco_destino)
    
    def iniciar(self):
        #inicia interface e loop de recebimento
        log_aplicacao(f"cliente iniciado")
        print(">>> ", end='', flush=True)
        self.aplicacao.iniciar_interface()
        
        try:
            while self.executando:
                try:
                    dados, endereco = self.socket.recvfrom(4096)
                    self.enlace.receber_bytes(dados, endereco)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.executando:
                        log_erro(f"erro: {e}")
        finally:
            self.parar()
    
    def parar(self):
        #fecha recursos do cliente
        self.executando = False
        self.transporte.parar()
        self.aplicacao.parar()
        self.socket.close()

if __name__ == "__main__":
    cliente = Cliente()
    try:
        cliente.iniciar()
    except KeyboardInterrupt:
        cliente.parar()
        sys.exit(0)
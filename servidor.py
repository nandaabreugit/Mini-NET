# servidor.py - versao inicial

import socket
import sys
from protocolo import enviar_pela_rede_ruidosa
import config
from utils import log_aplicacao, log_erro
from camada_aplicacao import CamadaAplicacao
from camada_transporte import CamadaTransporte

class Servidor:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((config.SERVIDOR_IP, config.SERVIDOR_PORTA))
        self.socket.settimeout(0.5)
        self.executando = True
        self.cliente_endereco = None
        
        self.transporte = CamadaTransporte(self._enviar_fisica)
        self.aplicacao = CamadaAplicacao("Servidor", self.transporte.enviar_segmento)
        
        self.transporte.callback_recebido = self.aplicacao.receber_mensagem
        self.transporte.iniciar()
    
    def _enviar_fisica(self, dados, destino=None):
        if destino is None and self.cliente_endereco:
            destino = self.cliente_endereco
        elif destino is None:
            return
        import json
        bytes_dados = json.dumps(dados).encode()
        enviar_pela_rede_ruidosa(self.socket, bytes_dados, destino)
    
    def iniciar(self):
        log_aplicacao("servidor iniciado")
        try:
            while self.executando:
                try:
                    dados, endereco = self.socket.recvfrom(4096)
                    if self.cliente_endereco is None:
                        self.cliente_endereco = endereco
                    import json
                    dados_dict = json.loads(dados.decode())
                    self.transporte.receber_segmento(dados_dict)
                except socket.timeout:
                    continue
        finally:
            self.parar()
    
    def parar(self):
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
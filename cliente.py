#cliente.py - versao inicial

import socket
import sys
from protocolo import enviar_pela_rede_ruidosa
import config
from utils import log_aplicacao, log_erro
from camada_aplicacao import CamadaAplicacao
from camada_transporte import CamadaTransporte

class Cliente:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((config.CLIENTE_IP, config.CLIENTE_PORTA))
        self.socket.settimeout(0.5)
        self.executando = True
        
        self.transporte = CamadaTransporte(self._enviar_fisica)
        self.aplicacao = CamadaAplicacao("Cliente", self.transporte.enviar_segmento)
        
        self.transporte.callback_recebido = self.aplicacao.receber_mensagem
        self.transporte.iniciar()
    
    def _enviar_fisica(self, dados, destino=None):
        if destino is None:
            destino = (config.SERVIDOR_IP, config.SERVIDOR_PORTA)
        from protocolo import enviar_pela_rede_ruidosa
        # por enquanto envia direto, depois vou serializar
        import json
        bytes_dados = json.dumps(dados).encode()
        enviar_pela_rede_ruidosa(self.socket, bytes_dados, destino)
    
    def iniciar(self):
        log_aplicacao(f"cliente iniciado")
        print(">>> ", end='', flush=True)
        self.aplicacao.iniciar_interface()
        
        try:
            while self.executando:
                try:
                    dados, endereco = self.socket.recvfrom(4096)
                    import json
                    dados_dict = json.loads(dados.decode())
                    self.transporte.receber_segmento(dados_dict)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.executando:
                        log_erro(f"erro: {e}")
        finally:
            self.parar()
    
    def parar(self):
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
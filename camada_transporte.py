import threading
import time
from utils import log_transporte

class CamadaTransporte:
    def __init__(self, callback_enviar_rede):
        self.callback_enviar = callback_enviar_rede
        self.callback_recebido = None
        
        self.seq_num_esperado = 0
        self.seq_num_enviar = 0
        
        self.ultimo_enviado = None
        self.ack_recebido = threading.Event()
        self.timeout_segundos = 3
        self.executando = True
        
    def enviar_segmento(self, dados_aplicacao):
        from protocolo import Segmento
        segmento = Segmento(self.seq_num_enviar, False, dados_aplicacao)
        segmento_dict = segmento.to_dict()
        log_transporte(f"enviando segmento seq={self.seq_num_enviar}")
        self.ultimo_enviado = segmento_dict
        self.ack_recebido.clear()
        self.callback_enviar(segmento_dict)
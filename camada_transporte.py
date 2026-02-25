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

    def receber_segmento(self, segmento_dict):
        from protocolo import Segmento
        is_ack = segmento_dict.get('is_ack', False)
        seq_num = segmento_dict.get('seq_num', 0)
        payload = segmento_dict.get('payload', {})
        
        if is_ack:
            log_transporte(f"ack recebido para seq={seq_num}")
            if seq_num == self.seq_num_enviar:
                self.ack_recebido.set()
                self.ultimo_enviado = None
                self.seq_num_enviar = 1 - self.seq_num_enviar
        else:
            log_transporte(f"segmento recebido seq={seq_num} esperado={self.seq_num_esperado}")
            if seq_num == self.seq_num_esperado:
                self._enviar_ack(seq_num)
                if self.callback_recebido:
                    self.callback_recebido(payload)
                self.seq_num_esperado = 1 - self.seq_num_esperado
            else:
                log_transporte(f"segmento duplicado, reenviando ack")
                self._enviar_ack(1 - seq_num)
    
    def _enviar_ack(self, seq_num):
        from protocolo import Segmento
        ack = Segmento(seq_num, True, {})
        log_transporte(f"enviando ack para seq={seq_num}")
        self.callback_enviar(ack.to_dict())
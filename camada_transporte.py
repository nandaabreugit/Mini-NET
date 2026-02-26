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
        self.timeout_thread = None
        self.tentativas = 0
        self.max_tentativas = 10
        
    def iniciar(self):
        def verificar_timeout():
            while self.executando:
                if self.ultimo_enviado and not self.ack_recebido.is_set():
                    self.tentativas += 1
                    if self.tentativas > self.max_tentativas:
                        log_transporte(f"MAXIMO TENTATIVAS atingido, desistindo")
                        self.ultimo_enviado = None
                        self.tentativas = 0
                    else:
                        log_transporte(f"TIMEOUT! retransmitindo segmento {self.seq_num_enviar} (tentativa {self.tentativas})")
                        self.callback_enviar(self.ultimo_enviado)
                    time.sleep(self.timeout_segundos)
                else:
                    time.sleep(0.1)
        
        self.timeout_thread = threading.Thread(target=verificar_timeout, daemon=True)
        self.timeout_thread.start()
        
    def enviar_segmento(self, dados_aplicacao):
        from protocolo import Segmento

        # So envia se nao tiver um segmento pendente
        if self.ultimo_enviado is not None and self.ack_recebido.is_set() is False:
            log_transporte(f"JA HA UM SEGMENTO PENDENTE, aguardando ACK")
            return

        segmento = Segmento(self.seq_num_enviar, False, dados_aplicacao)
        segmento_dict = segmento.to_dict()
        log_transporte(f"enviando segmento SEQ={self.seq_num_enviar}")

        self.ultimo_enviado = segmento_dict
        self.ack_recebido.clear()
        self.tentativas = 1
        self.callback_enviar(segmento_dict)

    def receber_segmento(self, segmento_dict):
        from protocolo import Segmento

        is_ack = segmento_dict.get('is_ack', False)
        seq_num = segmento_dict.get('seq_num', 0)
        payload = segmento_dict.get('payload', {})
        
        if is_ack:
            log_transporte(f"ACK recebido para SEQ={seq_num}")

            # Verifica se o ACK é para o segmento atual
            if seq_num == self.seq_num_enviar and self.ultimo_enviado:
                log_transporte(f"ACK valido, confirmando entrega")
                self.ack_recebido.set()
                self.ultimo_enviado = None
                self.tentativas = 0
                # Alterna o proximo numero de sequencia
                self.seq_num_enviar = 1 - self.seq_num_enviar
            else:
                log_transporte(f"ACK ignorado (seq esperado={self.seq_num_enviar})")
        else:
            log_transporte(f"segmento recebido SEQ={seq_num}, esperado={self.seq_num_esperado}")

            if seq_num == self.seq_num_esperado:
                self._enviar_ack(seq_num)

                if self.callback_recebido:
                    self.callback_recebido(payload)

                self.seq_num_esperado = 1 - self.seq_num_esperado
            else:
                log_transporte(f"segmento duplicado SEQ={seq_num}, reenviando ACK")
                self._enviar_ack(1 - seq_num)
    
    def _enviar_ack(self, seq_num):
        from protocolo import Segmento

        ack = Segmento(seq_num, True, {})
        log_transporte(f"enviando ACK para SEQ={seq_num}")
        self.callback_enviar(ack.to_dict())
    
    def parar(self):
        self.executando = False
        if self.timeout_thread:
            self.timeout_thread.join(timeout=1)
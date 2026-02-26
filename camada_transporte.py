import threading
import time
from utils import log_transporte

class CamadaTransporte:
    def __init__(self, callback_enviar_rede, nome="transporte"):
        self.callback_enviar = callback_enviar_rede
        self.callback_recebido = None
        
        self.nome = nome
        self.seq_num_enviar = 0
        self.ultimo_enviado = None
        self.ultimo_seq_enviado = None
        self.ack_recebido = threading.Event()
        self.seq_num_esperado = 0
        
        self.ultimo_ack_recebido = -1
        self.ultimo_ack_enviado = -1
        self.timeout_segundos = 3
        self.executando = True
        self.timeout_thread = None
        self.tentativas = 0
        self.max_tentativas = 10
        self.lock = threading.Lock()
        self.ultima_mensagem_recebida = None
        
    def iniciar(self):
        def verificar_timeout():
            while self.executando:
                time.sleep(0.5)
                with self.lock:
                    if self.ultimo_enviado and not self.ack_recebido.is_set():
                        self.tentativas += 1
                        if self.tentativas > self.max_tentativas:
                            log_transporte(f"{self.nome}: MAXIMO TENTATIVAS, desistindo")
                            self.ultimo_enviado = None
                            self.ultimo_seq_enviado = None
                            self.tentativas = 0
                            self.ack_recebido.set()
                        else:
                            log_transporte(f"{self.nome}: TIMEOUT! reenviando SEQ={self.ultimo_seq_enviado} (tentativa {self.tentativas})")
                            self.callback_enviar(self.ultimo_enviado)
        
        self.timeout_thread = threading.Thread(target=verificar_timeout, daemon=True)
        self.timeout_thread.start()
        log_transporte(f"{self.nome}: camada de transporte iniciada")
        
    def enviar_segmento(self, dados_aplicacao):
        from protocolo import Segmento

        with self.lock:
            if self.ultimo_enviado and not self.ack_recebido.is_set():
                log_transporte(f"{self.nome}: AGUARDANDO ACK do SEQ={self.ultimo_seq_enviado}")
                return False

            segmento = Segmento(self.seq_num_enviar, False, dados_aplicacao)
            segmento_dict = segmento.to_dict()
            log_transporte(f"{self.nome}: enviando segmento SEQ={self.seq_num_enviar}")

            self.ultimo_enviado = segmento_dict
            self.ultimo_seq_enviado = self.seq_num_enviar
            
            self.ack_recebido.clear()
            self.tentativas = 1
            self.callback_enviar(segmento_dict)
            return True

    def receber_segmento(self, segmento_dict):
        from protocolo import Segmento

        try:
            is_ack = segmento_dict.get('is_ack', False)
            seq_num = segmento_dict.get('seq_num', 0)
            payload = segmento_dict.get('payload', {})
            
            if is_ack:
                log_transporte(f"{self.nome}: ACK recebido para SEQ={seq_num}")

                with self.lock:
                    if seq_num == self.ultimo_seq_enviado and self.ultimo_enviado:
                        log_transporte(f"{self.nome}: ACK valido, confirmando entrega")
                        self.ack_recebido.set()
                        self.ultimo_enviado = None
                        self.ultimo_seq_enviado = None   
                        self.tentativas = 0
                        self.seq_num_enviar = 1 - self.seq_num_enviar
                        log_transporte(f"{self.nome}: proximo SEQ para envio = {self.seq_num_enviar}")
                    else:
                        log_transporte(f"{self.nome}: ACK ignorado (esperava {self.ultimo_seq_enviado}, recebeu {seq_num})")
            else:
                log_transporte(f"{self.nome}: segmento recebido SEQ={seq_num}, esperado={self.seq_num_esperado}")

                if seq_num == self.seq_num_esperado:
                    self._enviar_ack(seq_num)
                    
                    if payload and payload != self.ultima_mensagem_recebida:
                        self.ultima_mensagem_recebida = payload
                        if self.callback_recebido:
                            self.callback_recebido(payload)
                    
                    self.seq_num_esperado = 1 - self.seq_num_esperado
                    log_transporte(f"{self.nome}: proximo SEQ esperado = {self.seq_num_esperado}")
                else:
                    log_transporte(f"{self.nome}: segmento duplicado SEQ={seq_num}, reenviando ACK")
                    self._enviar_ack(1 - seq_num)
        except Exception as e:
            log_transporte(f"{self.nome}: ERRO ao receber segmento: {e}")
    
    def _enviar_ack(self, seq_num):
        from protocolo import Segmento

        with self.lock:
            if seq_num == self.ultimo_ack_enviado:
                log_transporte(f"{self.nome}: ACK duplicado SEQ={seq_num}, ignorando envio")
                return

            ack = Segmento(seq_num, True, {})
            log_transporte(f"{self.nome}: enviando ACK para SEQ={seq_num}")
            self.callback_enviar(ack.to_dict())
            self.ultimo_ack_enviado = seq_num
    
    def parar(self):
        self.executando = False
        if self.timeout_thread:
            self.timeout_thread.join(timeout=2)
import socket
import sys
import threading
from protocolo import enviar_pela_rede_ruidosa
import config
from utils import log_aplicacao, log_erro
from camada_aplicacao import CamadaAplicacao
from camada_transporte import CamadaTransporte
from camada_rede import CamadaRede
from camada_enlace import CamadaEnlace

class ServidorCentral:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((config.SERVIDOR_IP, config.SERVIDOR_PORTA))
        self.socket.settimeout(0.5)
        self.executando = True
        self._encerrado = False
        
        self.cliente_a_conectado = False
        self.cliente_b_conectado = False
        
        self.enlace = CamadaEnlace(config.MAC_SERVIDOR, self._enviar_fisica)
        self.rede = CamadaRede(config.VIP_SERVIDOR, self.enlace.enviar_quadro, usar_roteador=True)
        self.transporte = CamadaTransporte(self._enviar_rede, nome="SERVIDOR", gui=None)
        self.aplicacao = CamadaAplicacao("Servidor", self.transporte.enviar_segmento, gui=None)

        self.enlace.definir_callback_recebimento(self.rede.receber_pacote)
        self.rede.definir_callback_recebimento(self.transporte.receber_segmento)
        
        self.transporte.callback_recebido = self._processar_mensagem_recebida
        self.transporte.iniciar()
        
        log_aplicacao("Servidor Central inicializado")

    def _processar_mensagem_recebida(self, dados_json):
        try:
            import json
            msg = json.loads(dados_json) if isinstance(dados_json, str) else dados_json
            
            remetente = msg.get('sender', 'Desconhecido')
            mensagem = msg.get('message', '')
            timestamp = msg.get('timestamp', '')
            
            log_aplicacao(f"Mensagem de {remetente}: {mensagem}")
            
            if remetente == "Cliente_A":
                destino = config.VIP_CLIENTE_B
                log_aplicacao(f"Encaminhando para Cliente B")
            elif remetente == "Cliente_B":
                destino = config.VIP_CLIENTE_A
                log_aplicacao(f"Encaminhando para Cliente A")
            else:
                log_aplicacao(f"Remetente desconhecido: {remetente}")
                return
            
            msg_encaminhada = {
                "type": "chat",
                "sender": remetente,
                "message": mensagem,
                "timestamp": timestamp
            }
            
            self.transporte.enviar_segmento(msg_encaminhada)
            
        except Exception as e:
            log_erro(f"Erro ao processar mensagem: {e}")
    
    def _enviar_rede(self, dados_transporte):
        self.rede.enviar_pacote(dados_transporte, config.VIP_CLIENTE_A)
        self.rede.enviar_pacote(dados_transporte, config.VIP_CLIENTE_B)
    
    def _enviar_fisica(self, bytes_dados, endereco_destino):
        enviar_pela_rede_ruidosa(self.socket, bytes_dados, endereco_destino)
    
    def _receber_mensagens(self):
        while self.executando:
            try:
                dados, endereco = self.socket.recvfrom(4096)
                
                if endereco[1] == config.CLIENTE_A_PORTA and not self.cliente_a_conectado:
                    self.cliente_a_conectado = True
                    log_aplicacao(f"Cliente A conectado de {endereco}")
                elif endereco[1] == config.CLIENTE_B_PORTA and not self.cliente_b_conectado:
                    self.cliente_b_conectado = True
                    log_aplicacao(f"Cliente B conectado de {endereco}")
                
                self.enlace.receber_bytes(dados, endereco)
            except socket.timeout:
                continue
            except Exception as e:
                if self.executando:
                    log_erro(f"erro no recebimento: {e}")
    
    def iniciar(self):
        log_aplicacao(f"Servidor Central ouvindo em {config.SERVIDOR_IP}:{config.SERVIDOR_PORTA}")
        log_aplicacao("Aguardando conexão dos clientes...")
        
        thread_receber = threading.Thread(target=self._receber_mensagens, daemon=True)
        thread_receber.start()
        
        try:
            while self.executando:
                threading.Event().wait(0.1)
        except KeyboardInterrupt:
            self.parar()
    
    def parar(self):
        if self._encerrado:
            return
        self._encerrado = True
        self.executando = False
        self.transporte.parar()
        self.aplicacao.parar()
        self.socket.close()
        log_aplicacao("Servidor Central encerrado")

if __name__ == "__main__":
    servidor = ServidorCentral()
    try:
        servidor.iniciar()
    except KeyboardInterrupt:
        servidor.parar()
        sys.exit(0)
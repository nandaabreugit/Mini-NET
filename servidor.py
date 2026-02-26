#servidor.py

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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((config.SERVIDOR_IP, config.SERVIDOR_PORTA))
        self.socket.settimeout(0.5)
        self.executando = True
        self.cliente_endereco = None
        self._encerrado = False
        
        self.enlace = CamadaEnlace(config.MAC_SERVIDOR, self._enviar_fisica)
        self.rede = CamadaRede(config.VIP_SERVIDOR, self.enlace.enviar_quadro, usar_roteador=True)
        self.transporte = CamadaTransporte(self._enviar_rede, nome="SERVIDOR")
        self.aplicacao = CamadaAplicacao("Servidor", self.transporte.enviar_segmento)

        self.enlace.definir_callback_recebimento(self.rede.receber_pacote)
        self.rede.definir_callback_recebimento(self.transporte.receber_segmento)
        
        self.transporte.callback_recebido = self.aplicacao.receber_mensagem
        self.transporte.iniciar()

    def _enviar_rede(self, dados_transporte):
        if self.cliente_endereco:
            log_aplicacao(f"servidor enviando resposta para {config.VIP_CLIENTE}")
            self.rede.enviar_pacote(dados_transporte, config.VIP_CLIENTE)
    
    def _enviar_fisica(self, bytes_dados, endereco_destino):
        enviar_pela_rede_ruidosa(self.socket, bytes_dados, endereco_destino)
    
    def iniciar(self):
        log_aplicacao(f"SERVIDOR iniciado em {config.SERVIDOR_IP}:{config.SERVIDOR_PORTA}")
        print("\n" + "="*50)
        print("SISTEMA DE CHAT INICIADO - SERVIDOR")
        print("="*50)
        print("Comandos disponiveis:")
        print("  /sair     - Encerra o programa")
        print("  /r        - Responde rapidamente a ultima mensagem")
        print("  /r TEXTO  - Responde rapidamente (ex: /r Ola!)")
        print("  /ultima   - Mostra a ultima mensagem recebida")
        print("  /ajuda    - Mostra todos os comandos")
        print("="*50)
        print(">>> ", end='', flush=True)
        
        thread_interface = self.aplicacao.iniciar_interface()
        
        try:
            while self.executando:
                try:
                    dados, endereco = self.socket.recvfrom(4096)
                    if self.cliente_endereco is None:
                        self.cliente_endereco = endereco
                        log_aplicacao(f"cliente conectado de {endereco}")
                    self.enlace.receber_bytes(dados, endereco)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.executando:
                        log_erro(f"erro: {e}")
        except KeyboardInterrupt:
            self.parar()
        finally:
            if thread_interface and thread_interface.is_alive():
                thread_interface.join(timeout=1)
    
    def parar(self):
        if self._encerrado:
            return
        self._encerrado = True
        self.executando = False
        self.transporte.parar()
        self.aplicacao.parar()
        self.socket.close()
        log_aplicacao("servidor encerrado")

if __name__ == "__main__":
    servidor = Servidor()
    try:
        servidor.iniciar()
    except KeyboardInterrupt:
        servidor.parar()
        sys.exit(0)
#roteador
import socket
import sys
from protocolo import enviar_pela_rede_ruidosa
import config
from utils import log_rede, log_fisica, log_erro
from camada_enlace import CamadaEnlace

class Roteador:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((config.ROTEADOR_IP, config.ROTEADOR_PORTA))
        self.socket.settimeout(0.5)
        self.executando = True
        
        self.tabela_roteamento = {
            config.VIP_CLIENTE: (config.CLIENTE_IP, config.CLIENTE_PORTA),
            config.VIP_SERVIDOR: (config.SERVIDOR_IP, config.SERVIDOR_PORTA)
        }
        
        self.enlace = CamadaEnlace(config.MAC_ROTEADOR, self._enviar_fisica)
        self.enlace.definir_callback_recebimento(self.processar_pacote)
        
        log_rede("roteador inicializado")
        log_rede("tabela de roteamento:")
        for dest, end in self.tabela_roteamento.items():
            log_rede(f"  {dest} -> {end}")
    
    def _enviar_fisica(self, bytes_dados, endereco):
        enviar_pela_rede_ruidosa(self.socket, bytes_dados, endereco)
    
    def processar_pacote(self, pacote_dict, endereco_origem):
        src = pacote_dict.get('src_vip')
        dst = pacote_dict.get('dst_vip')
        ttl = pacote_dict.get('ttl', 0)
        
        log_rede(f"roteador recebeu: {src} -> {dst}, TTL={ttl}")
        
        if ttl <= 0:
            log_rede(f"TTL expirado, pacote descartado")
            return
        
        # Decrementa TTL
        pacote_dict['ttl'] = ttl - 1
        log_rede(f"TTL decrementado para {pacote_dict['ttl']}")
        
        # Consulta tabela
        if dst in self.tabela_roteamento:
            endereco_destino = self.tabela_roteamento[dst]
            log_rede(f"encaminhando para {dst} via {endereco_destino}")
            
            # Reencapsula e envia (a camada de enlace cuida do MAC)
            self.enlace.enviar_quadro(pacote_dict, endereco_destino)
        else:
            log_rede(f"rota desconhecida para {dst}")
    
    def iniciar(self):
        log_rede(f"roteador ouvindo em {config.ROTEADOR_IP}:{config.ROTEADOR_PORTA}")
        
        try:
            while self.executando:
                try:
                    dados, endereco = self.socket.recvfrom(4096)
                    log_fisica(f"roteador recebeu {len(dados)} bytes")
                    self.enlace.receber_bytes(dados, endereco)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.executando:
                        log_erro(f"erro: {e}")
        finally:
            self.parar()
    
    def parar(self):
        self.executando = False
        self.socket.close()
        log_rede("roteador encerrado")

if __name__ == "__main__":
    roteador = Roteador()
    try:
        roteador.iniciar()
    except KeyboardInterrupt:
        roteador.parar()
        sys.exit(0)
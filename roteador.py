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
            config.VIP_CLIENTE_A: (config.CLIENTE_A_IP, config.CLIENTE_A_PORTA),
            config.VIP_CLIENTE_B: (config.CLIENTE_B_IP, config.CLIENTE_B_PORTA),
            config.VIP_SERVIDOR: (config.SERVIDOR_IP, config.SERVIDOR_PORTA)
        }
        
        self.enlace = CamadaEnlace(config.MAC_ROTEADOR, self._enviar_fisica)
        self.enlace.definir_callback_recebimento(self.processar_pacote)
        
        log_rede("Roteador inicializado")
        log_rede("Tabela de roteamento:")
        for dest, end in self.tabela_roteamento.items():
            log_rede(f"  {dest} -> {end[0]}:{end[1]}")
    
    def _enviar_fisica(self, bytes_dados, endereco):
        enviar_pela_rede_ruidosa(self.socket, bytes_dados, endereco)
    
    def processar_pacote(self, pacote_dict, endereco_origem):
        src = pacote_dict.get('src_vip')
        dst = pacote_dict.get('dst_vip')
        ttl = pacote_dict.get('ttl', 0)
        
        log_rede(f"Roteador recebeu: {src} -> {dst}, TTL={ttl}")
        
        if ttl <= 0:
            log_rede(f"TTL expirado, pacote descartado")
            return
        
        pacote_dict['ttl'] = ttl - 1
        log_rede(f"TTL decrementado para {pacote_dict['ttl']}")
        
        if dst in self.tabela_roteamento:
            endereco_destino = self.tabela_roteamento[dst]
            log_rede(f"Encaminhando para {dst} via {endereco_destino[0]}:{endereco_destino[1]}")
            
            self.enlace.enviar_quadro(pacote_dict, endereco_destino)
        else:
            log_rede(f"Rota desconhecida para {dst}")
            log_rede(f"Destinos disponíveis: {list(self.tabela_roteamento.keys())}")
    
    def iniciar(self):
        log_rede(f"Roteador ouvindo em {config.ROTEADOR_IP}:{config.ROTEADOR_PORTA}")
        
        try:
            while self.executando:
                try:
                    dados, endereco = self.socket.recvfrom(4096)
                    log_fisica(f"Roteador recebeu {len(dados)} bytes de {endereco}")
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
        log_rede("Roteador encerrado")

if __name__ == "__main__":
    roteador = Roteador()
    try:
        roteador.iniciar()
    except KeyboardInterrupt:
        roteador.parar()
        sys.exit(0)
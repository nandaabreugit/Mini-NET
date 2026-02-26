from protocolo import Quadro
from utils import log_enlace, log_fisica
import config

class CamadaEnlace:
    def __init__(self, meu_mac, callback_enviar_fisica):
        self.meu_mac = meu_mac
        self.callback_enviar = callback_enviar_fisica
        self.callback_recebido = None
        
        self.tabela_arp = {
            config.CLIENTE_A_IP: config.MAC_CLIENTE_A,
            config.CLIENTE_B_IP: config.MAC_CLIENTE_B,
            config.SERVIDOR_IP: config.MAC_SERVIDOR,
            config.ROTEADOR_IP: config.MAC_ROTEADOR,
            '127.0.0.1': config.MAC_ROTEADOR
        }
    
    def enviar_quadro(self, dados_rede, endereco_destino):
        ip_destino = endereco_destino[0]
        porta_destino = endereco_destino[1]
        
        if porta_destino == config.SERVIDOR_PORTA:
            mac_destino = config.MAC_SERVIDOR
            log_enlace(f"destino e SERVIDOR (porta {porta_destino}) -> MAC {mac_destino}")
        elif porta_destino == config.CLIENTE_A_PORTA:
            mac_destino = config.MAC_CLIENTE_A
            log_enlace(f"destino e CLIENTE_A (porta {porta_destino}) -> MAC {mac_destino}")
        elif porta_destino == config.CLIENTE_B_PORTA:
            mac_destino = config.MAC_CLIENTE_B
            log_enlace(f"destino e CLIENTE_B (porta {porta_destino}) -> MAC {mac_destino}")
        elif porta_destino == config.ROTEADOR_PORTA:
            mac_destino = config.MAC_ROTEADOR
            log_enlace(f"destino e ROTEADOR (porta {porta_destino}) -> MAC {mac_destino}")
        else:
            mac_destino = self.tabela_arp.get(ip_destino, config.MAC_ROTEADOR)
            log_enlace(f"destino IP {ip_destino}:{porta_destino} -> MAC {mac_destino}")

        quadro = Quadro(self.meu_mac, mac_destino, dados_rede)
        bytes_quadro = quadro.serializar()

        log_enlace(f"quadro criado: {self.meu_mac} -> {mac_destino}")
        log_enlace(f"crc calculado: {quadro.fcs}")
        log_fisica(f"enviando {len(bytes_quadro)} bytes para {endereco_destino}")

        self.callback_enviar(bytes_quadro, endereco_destino)
    
    def receber_bytes(self, bytes_recebidos, endereco_origem):
        log_fisica(f"recebidos {len(bytes_recebidos)} bytes de {endereco_origem}")

        quadro_dict, valido = Quadro.deserializar(bytes_recebidos)
        
        if not valido:
            log_enlace(f"ERRO CRC: quadro corrompido - DESCARTADO")
            return
        
        log_enlace(f"CRC OK: quadro integro")
        
        mac_destino = quadro_dict.get('dst_mac')
        if mac_destino != self.meu_mac:
            log_enlace(f"MAC destino {mac_destino} != meu MAC {self.meu_mac} - DESCARTADO")
            return

        log_enlace(f"MAC destino OK: {mac_destino}")
        
        if self.callback_recebido:
            self.callback_recebido(quadro_dict.get('data'), endereco_origem)
    
    def _ip_para_mac(self, ip):
        return self.tabela_arp.get(ip, config.MAC_ROTEADOR)
    
    def definir_callback_recebimento(self, callback):
        self.callback_recebido = callback
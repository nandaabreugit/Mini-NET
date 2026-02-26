from protocolo import Quadro
from utils import log_enlace, log_fisica
import config

class CamadaEnlace:
    def __init__(self, meu_mac, callback_enviar_fisica):
        self.meu_mac = meu_mac
        self.callback_enviar = callback_enviar_fisica
        self.callback_recebido = None
        
        self.tabela_arp = {
            config.MAC_CLIENTE: (config.CLIENTE_IP, config.CLIENTE_PORTA),
            config.MAC_SERVIDOR: (config.SERVIDOR_IP, config.SERVIDOR_PORTA),
            config.MAC_ROTEADOR: (config.ROTEADOR_IP, config.ROTEADOR_PORTA)
        }
    
    def enviar_quadro(self, dados_rede, endereco_destino):
        mac_destino = self._ip_para_mac(endereco_destino[0])
        quadro = Quadro(self.meu_mac, mac_destino, dados_rede)
        bytes_quadro = quadro.serializar()
        log_enlace(f"quadro criado: {self.meu_mac} -> {mac_destino}")
        log_enlace(f"crc calculado: {quadro.fcs}")
        log_fisica(f"enviando {len(bytes_quadro)} bytes")
        self.callback_enviar(bytes_quadro, endereco_destino)
    
    def receber_bytes(self, bytes_recebidos, endereco_origem):
        log_fisica(f"recebidos {len(bytes_recebidos)} bytes")
        quadro_dict, valido = Quadro.deserializar(bytes_recebidos)
        
        if not valido:
            log_enlace(f"erro crc quadro corrompido descartado")
            return
        
        log_enlace(f"crc ok quadro integro")
        
        mac_destino = quadro_dict.get('dst_mac')
        if mac_destino != self.meu_mac and mac_destino != "FF:FF:FF:FF:FF:FF":
            log_enlace(f"mac destino {mac_destino} nao eh meu")
            return
        
        if self.callback_recebido:
            self.callback_recebido(quadro_dict.get('data'), endereco_origem)
    
    def _ip_para_mac(self, ip):
        if ip == config.CLIENTE_IP:
            return config.MAC_CLIENTE
        elif ip == config.SERVIDOR_IP:
            return config.MAC_SERVIDOR
        elif ip == config.ROTEADOR_IP:
            return config.MAC_ROTEADOR
        return "FF:FF:FF:FF:FF:FF"
    
    def definir_callback_recebimento(self, callback):
        self.callback_recebido = callback
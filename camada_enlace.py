from protocolo import Quadro
from utils import log_enlace, log_fisica
import config

class CamadaEnlace:
    def __init__(self, meu_mac, callback_enviar_fisica):
        self.meu_mac = meu_mac
        self.callback_enviar = callback_enviar_fisica
        self.callback_recebido = None
        
        # Mapeamento IP -> MAC (corrigido!)
        self.tabela_arp = {
            config.CLIENTE_IP: config.MAC_CLIENTE,
            config.SERVIDOR_IP: config.MAC_SERVIDOR,
            config.ROTEADOR_IP: config.MAC_ROTEADOR,
            # localhost também mapeia para os mesmos MACs
            '127.0.0.1': config.MAC_ROTEADOR  # padrão: roteador
        }
    
    def enviar_quadro(self, dados_rede, endereco_destino):
        """envia quadro para o destino físico"""
        ip_destino = endereco_destino[0]
        porta_destino = endereco_destino[1]
        
        # Descobre o MAC destino baseado no IP
        if porta_destino == config.SERVIDOR_PORTA:
            mac_destino = config.MAC_SERVIDOR
            log_enlace(f"destino é SERVIDOR (porta {porta_destino}) -> MAC {mac_destino}")
        elif porta_destino == config.CLIENTE_PORTA:
            mac_destino = config.MAC_CLIENTE
            log_enlace(f"destino é CLIENTE (porta {porta_destino}) -> MAC {mac_destino}")
        elif porta_destino == config.ROTEADOR_PORTA:
            mac_destino = config.MAC_ROTEADOR
            log_enlace(f"destino é ROTEADOR (porta {porta_destino}) -> MAC {mac_destino}")
        else:
            # Tenta pelo IP
            mac_destino = self.tabela_arp.get(ip_destino, config.MAC_ROTEADOR)
            log_enlace(f"destino IP {ip_destino}:{porta_destino} -> MAC {mac_destino}")

        quadro = Quadro(self.meu_mac, mac_destino, dados_rede)
        bytes_quadro = quadro.serializar()

        log_enlace(f"quadro criado: {self.meu_mac} -> {mac_destino}")
        log_enlace(f"crc calculado: {quadro.fcs}")
        log_fisica(f"enviando {len(bytes_quadro)} bytes para {endereco_destino}")

        self.callback_enviar(bytes_quadro, endereco_destino)
    
    def receber_bytes(self, bytes_recebidos, endereco_origem):
        """recebe bytes da camada física e verifica integridade"""
        log_fisica(f"recebidos {len(bytes_recebidos)} bytes de {endereco_origem}")

        quadro_dict, valido = Quadro.deserializar(bytes_recebidos)
        
        if not valido:
            log_enlace(f"ERRO CRC: quadro corrompido - DESCARTADO")
            return
        
        log_enlace(f"CRC OK: quadro íntegro")
        
        # Verifica se o MAC destino é o meu
        mac_destino = quadro_dict.get('dst_mac')
        if mac_destino != self.meu_mac:
            log_enlace(f"MAC destino {mac_destino} != meu MAC {self.meu_mac} - DESCARTADO")
            return

        log_enlace(f"MAC destino OK: {mac_destino}")
        
        # Passa para camada superior
        if self.callback_recebido:
            self.callback_recebido(quadro_dict.get('data'), endereco_origem)
    
    def _ip_para_mac(self, ip):
        """mapeia IP para MAC (método auxiliar)"""
        return self.tabela_arp.get(ip, config.MAC_ROTEADOR)
    
    def definir_callback_recebimento(self, callback):
        self.callback_recebido = callback
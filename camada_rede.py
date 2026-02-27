from protocolo import Pacote
from utils import log_rede
import config

class CamadaRede:
    def __init__(self, meu_vip, callback_enviar_enlace, usar_roteador=False):
        self.meu_vip = meu_vip
        self.callback_enviar = callback_enviar_enlace
        self.callback_recebido = None
        self.usar_roteador = usar_roteador
        
        if usar_roteador:
            log_rede(f"*** MODO ROTEADOR ATIVADO para {meu_vip} ***")
            self.tabela_roteamento = {
                "SERVIDOR_CENTRAL": (config.ROTEADOR_IP, config.ROTEADOR_PORTA),
                "CLIENTE_A": (config.ROTEADOR_IP, config.ROTEADOR_PORTA),
                "CLIENTE_B": (config.ROTEADOR_IP, config.ROTEADOR_PORTA),
                "ROTEADOR": (config.ROTEADOR_IP, config.ROTEADOR_PORTA)
            }
        else:
            log_rede(f"modo DIRETO ativado para {meu_vip}")
            self.tabela_roteamento = {
                "SERVIDOR_CENTRAL": (config.SERVIDOR_IP, config.SERVIDOR_PORTA),
                "CLIENTE_A": (config.CLIENTE_A_IP, config.CLIENTE_A_PORTA),
                "CLIENTE_B": (config.CLIENTE_B_IP, config.CLIENTE_B_PORTA),
                "ROTEADOR": (config.ROTEADOR_IP, config.ROTEADOR_PORTA)
            }
    
    def enviar_pacote(self, dados_transporte, destino_vip):
        pacote = Pacote(
            src_vip=self.meu_vip,
            dst_vip=destino_vip,
            ttl=config.TTL_INICIAL,
            segmento_dict=dados_transporte
        )
        pacote_dict = pacote.to_dict()
        log_rede(f"criando pacote: {self.meu_vip} -> {destino_vip} ttl={pacote.ttl}")
        
        if destino_vip in self.tabela_roteamento:
            endereco_fisico = self.tabela_roteamento[destino_vip]
            
            if self.usar_roteador:
                log_rede(f"ENCAMINHANDO VIA ROTEADOR para {destino_vip} -> {endereco_fisico}")
            else:
                log_rede(f"enviando DIRETO para {destino_vip} -> {endereco_fisico}")
                
            self.callback_enviar(pacote_dict, endereco_fisico)
        else:
            log_rede(f"sem rota para {destino_vip}")
            log_rede(f"destinos disponiveis: {list(self.tabela_roteamento.keys())}")
    
    def receber_pacote(self, pacote_dict, endereco_fisico_origem):
        src = pacote_dict.get('src_vip')
        dst = pacote_dict.get('dst_vip')
        ttl = pacote_dict.get('ttl', 0)
        
        log_rede(f"pacote recebido: {src} -> {dst}, TTL={ttl}, origem={endereco_fisico_origem}")
        
        if ttl <= 0:
            log_rede(f"TTL expirado, pacote descartado")
            return
        
        pacote_dict['ttl'] = ttl - 1
        
        if dst == self.meu_vip:
            log_rede(f"pacote chegou ao DESTINO {self.meu_vip}")
            data = pacote_dict.get('data')
            if isinstance(data, dict):
                data['_src_vip'] = src
                pacote_dict['_src_vip'] = src
                pacote_dict['data'] = data

            if self.callback_recebido:
                self.callback_recebido(pacote_dict.get('data'))
        else:
            log_rede(f"pacote NAO e para mim ({self.meu_vip}), destino={dst}")
    
    def definir_callback_recebimento(self, callback):
        self.callback_recebido = callback
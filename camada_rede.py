#camada de rede

from protocolo import Pacote
from utils import log_rede
import config

class CamadaRede:
    def __init__(self, meu_vip, callback_enviar_enlace, tabela_roteamento=None):
        #define vip local e callback de envio
        self.meu_vip = meu_vip
        self.callback_enviar = callback_enviar_enlace
        self.callback_recebido = None
        
        if tabela_roteamento is None:
            #usa tabela padrao de rotas
            self.tabela_roteamento = {
                "SERVIDOR_PRINCIPAL": (config.SERVIDOR_IP, config.SERVIDOR_PORTA),
                "CLIENTE_1": (config.CLIENTE_IP, config.CLIENTE_PORTA),
                "ROTEADOR": (config.ROTEADOR_IP, config.ROTEADOR_PORTA)
            }
        else:
            self.tabela_roteamento = tabela_roteamento
    
    def enviar_pacote(self, dados_transporte, destino_vip):
        #cria pacote e tenta enviar para destino
        pacote = Pacote(self.meu_vip, destino_vip, config.TTL_INICIAL, dados_transporte)
        pacote_dict = pacote.to_dict()
        log_rede(f"criando pacote: {self.meu_vip} -> {destino_vip} ttl={pacote.ttl}")
        
        if destino_vip in self.tabela_roteamento:
            endereco = self.tabela_roteamento[destino_vip]
            log_rede(f"roteando para {destino_vip} via {endereco}")
            self.callback_enviar(pacote_dict, endereco)
        else:
            log_rede(f"sem rota para {destino_vip}")
    
    def receber_pacote(self, pacote_dict, endereco_origem):
        #decrementa ttl e entrega se destino for local
        log_rede(f"pacote recebido de {pacote_dict.get('src_vip')} ttl={pacote_dict.get('ttl')}")
        ttl = pacote_dict.get('ttl', 0)
        if ttl <= 0:
            log_rede(f"ttl expirado pacote descartado")
            return
        
        pacote_dict['ttl'] = ttl - 1
        destino = pacote_dict.get('dst_vip')
        
        if destino == self.meu_vip:
            log_rede(f"pacote chegou ao destino")
            if self.callback_recebido:
                self.callback_recebido(pacote_dict.get('data'))
        else:
            log_rede(f"pacote em transito encaminhando")
    
    def definir_callback_recebimento(self, callback):
        #salva callback de recebimento
        self.callback_recebido = callback
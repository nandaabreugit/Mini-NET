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
    
    def _enviar_fisica(self, bytes_dados, endereco):
        enviar_pela_rede_ruidosa(self.socket, bytes_dados, endereco)
    
    def processar_pacote(self, pacote_dict, endereco_origem):
        log_rede(f"roteador recebeu: {pacote_dict.get('src_vip')} -> {pacote_dict.get('dst_vip')}")
        
        destino = pacote_dict.get('dst_vip')
        ttl = pacote_dict.get('ttl', 0)
        
        if ttl <= 0:
            log_rede(f"ttl expirado descartando")
            return
        
        pacote_dict['ttl'] = ttl - 1
        
        if destino in self.tabela_roteamento:
            endereco_destino = self.tabela_roteamento[destino]
            log_rede(f"encaminhando para {destino} via {endereco_destino}")
            import json
            bytes_dados = json.dumps(pacote_dict).encode()
            self._enviar_fisica(bytes_dados, endereco_destino)
        else:
            log_rede(f"rota desconhecida para {destino}")
    
    def iniciar(self):
        log_rede("roteador iniciado")
        try:
            while self.executando:
                try:
                    dados, endereco = self.socket.recvfrom(4096)
                    log_fisica(f"roteador recebeu {len(dados)} bytes de {endereco}")
                    import json
                    pacote_dict = json.loads(dados.decode())
                    self.processar_pacote(pacote_dict, endereco)
                except socket.timeout:
                    continue
        finally:
            self.parar()
    
    def parar(self):
        self.executando = False
        self.socket.close()

if __name__ == "__main__":
    roteador = Roteador()
    try:
        roteador.iniciar()
    except KeyboardInterrupt:
        roteador.parar()
        sys.exit(0)
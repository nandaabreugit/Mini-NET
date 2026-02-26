#config.py-configuracoes do projeto

#enderecos e portas
CLIENTE_IP = '127.0.0.1'
CLIENTE_PORTA = 5000
SERVIDOR_IP = '127.0.0.1'
SERVIDOR_PORTA = 6000
ROTEADOR_IP = '127.0.0.1'
ROTEADOR_PORTA = 7000

#identificadores virtuais
VIP_CLIENTE = "CLIENTE_1"
VIP_SERVIDOR = "SERVIDOR_PRINCIPAL"

#enderecos mac
MAC_CLIENTE = "AA:BB:CC:DD:EE:01"
MAC_SERVIDOR = "AA:BB:CC:DD:EE:02"
MAC_ROTEADOR = "AA:BB:CC:DD:EE:FF"

#controle de timeout e tentativas
TIMEOUT_SEGUNDOS = 4
MAX_TENTATIVAS = 5

#tempo de vida do pacote
TTL_INICIAL = 5
"""
teste_envio.py

Script de verificação simples:
- liga um socket UDP em CLIENTE_B_PORTA para "fingir" o Cliente B
- cria um Segmento/Pacote/Quadro como se fosse o Cliente A
- envia o quadro para o Roteador
- aguarda receber o quadro encaminhado ao Cliente B e imprime o payload

Use com o `roteador.py` e `servidor_central.py` já rodando.
"""

import socket
import time
from protocolo import Segmento, Pacote, Quadro
import config
from utils import criar_mensagem_json


def main():
    # Socket que atua como "Cliente B" para receber a mensagem final
    listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen.bind((config.CLIENTE_B_IP, config.CLIENTE_B_PORTA))
    listen.settimeout(10.0)

    # Cria a mensagem de aplicação
    msg = criar_mensagem_json("chat", "Cliente_A", "Mensagem de teste do script")

    # Monta o segmento, pacote e quadro (mesma estrutura usada pelas camadas)
    segmento = Segmento(0, False, msg)
    segmento_dict = segmento.to_dict()

    pacote = Pacote(src_vip=config.VIP_CLIENTE_A,
                    dst_vip=config.VIP_SERVIDOR,
                    ttl=config.TTL_INICIAL,
                    segmento_dict=segmento_dict)

    quadro = Quadro(src_mac=config.MAC_CLIENTE_A,
                    dst_mac=config.MAC_ROTEADOR,
                    pacote_dict=pacote.to_dict())

    bytes_quadro = quadro.serializar()

    # Envia para o roteador (que deve encaminhar ao servidor, e daí ao Cliente B)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Enviando quadro de {config.VIP_CLIENTE_A} para roteador {config.ROTEADOR_IP}:{config.ROTEADOR_PORTA}...")
    sender.sendto(bytes_quadro, (config.ROTEADOR_IP, config.ROTEADOR_PORTA))

    print(f"Aguardando pacote entregue ao {config.VIP_CLIENTE_B} (porta {config.CLIENTE_B_PORTA})...")
    try:
        dados, addr = listen.recvfrom(4096)
        print(f"Recebido {len(dados)} bytes de {addr}")

        quadro_dict, valido = Quadro.deserializar(dados)
        if not valido:
            print("Quadro corrompido (CRC inválido)")
            return

        pacote_dict = quadro_dict.get('data')
        segmento_dict = pacote_dict.get('data')
        payload = segmento_dict.get('payload')

        print("Mensagem entregue ao Cliente B:")
        print(payload)

    except socket.timeout:
        print("Timeout: nenhuma mensagem recebida no Cliente B")
    finally:
        listen.close()
        sender.close()


if __name__ == '__main__':
    main()

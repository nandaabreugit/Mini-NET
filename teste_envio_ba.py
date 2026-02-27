"""
teste_envio_ba.py

Envia uma mensagem como Cliente_B para o roteador (simulando o envio do Cliente B)
e aguarda no porto do Cliente A (5000) para verificar se a mensagem chega corretamente.

Uso:
  python teste_envio_ba.py

Certifique-se de que `roteador.py` e `servidor_central.py` estejam rodando.
"""

import socket
import time
from protocolo import Segmento, Pacote, Quadro
import config
from utils import criar_mensagem_json


def main():
    listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen.bind((config.CLIENTE_A_IP, config.CLIENTE_A_PORTA))
    listen.settimeout(10.0)

    # Mensagem de Cliente_B
    msg = criar_mensagem_json("chat", "Cliente_B", "Mensagem teste B->A")

    segmento = Segmento(0, False, msg)
    segmento_dict = segmento.to_dict()

    pacote = Pacote(src_vip=config.VIP_CLIENTE_B,
                    dst_vip=config.VIP_SERVIDOR,
                    ttl=config.TTL_INICIAL,
                    segmento_dict=segmento_dict)

    quadro = Quadro(src_mac=config.MAC_CLIENTE_B,
                    dst_mac=config.MAC_ROTEADOR,
                    pacote_dict=pacote.to_dict())

    bytes_quadro = quadro.serializar()

    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Enviando quadro de {config.VIP_CLIENTE_B} para roteador {config.ROTEADOR_IP}:{config.ROTEADOR_PORTA}...")
    sender.sendto(bytes_quadro, (config.ROTEADOR_IP, config.ROTEADOR_PORTA))

    print(f"Aguardando pacote entregue ao {config.VIP_CLIENTE_A} (porta {config.CLIENTE_A_PORTA})...")
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

        print("Mensagem entregue ao Cliente A:")
        print(payload)

    except socket.timeout:
        print("Timeout: nenhuma mensagem recebida no Cliente A")
    finally:
        listen.close()
        sender.close()


if __name__ == '__main__':
    main()

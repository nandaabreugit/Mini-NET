import threading
import json
from utils import log_aplicacao, criar_mensagem_json

class CamadaAplicacao:
    def __init__(self, nome_usuario, callback_enviar, gui=None):
        self.nome = nome_usuario
        self.callback_enviar = callback_enviar
        self.gui = gui
        self.executando = True
        self.thread_interface = None
        self.ultimo_remetente = None
        self.ultima_mensagem = None
        
    def enviar_mensagem(self, mensagem):
        msg_json = criar_mensagem_json("chat", self.nome, mensagem)
        log_aplicacao(f"criando mensagem: {msg_json}")
        if self.callback_enviar:
            self.callback_enviar(msg_json)
    
    def receber_mensagem(self, dados_json):
        try:
            # Normaliza o formato da mensagem recebida.
            if isinstance(dados_json, str):
                try:
                    msg = json.loads(dados_json)
                except Exception:
                    log_aplicacao("Recebido dado string inválido")
                    return
            elif isinstance(dados_json, dict):
                msg = dados_json
            else:
                log_aplicacao("Formato de dado desconhecido recebido na aplicação")
                return

            # Se for um wrapper, desembrulhe (ex.: {'payload': {...}})
            if isinstance(msg, dict) and 'payload' in msg and isinstance(msg['payload'], dict):
                inner = msg['payload']
                # tratar casos onde há wrapper adicional
                if 'type' in inner:
                    msg = inner

            if 'type' not in msg:
                log_aplicacao(f"Mensagem sem tipo ignorada: {msg}")
                return

            if msg['type'] == 'chat':
                if msg.get('sender') != self.nome:
                    self.ultimo_remetente = msg.get('sender')
                    self.ultima_mensagem = msg.get('message')

                    if self.gui:
                        self.gui.adicionar_mensagem_outro(
                            msg.get('sender'),
                            msg.get('message'),
                            msg.get('timestamp')
                        )
                    else:
                        print(f"\n[{msg.get('timestamp')}] {msg.get('sender')}: {msg.get('message')}")
                        print(">>> ", end='', flush=True)
                else:
                    log_aplicacao(f"Mensagem propria ignorada: {msg.get('message')}")

            elif msg['type'] == 'sistema':
                if self.gui:
                    self.gui.adicionar_mensagem_sistema(msg.get('message'))
                else:
                    print(f"\n*** {msg.get('message')} ***")
                    print(">>> ", end='', flush=True)
        except Exception as e:
            log_aplicacao(f"erro ao receber: {e}")
    
    def parar(self):
        self.executando = False
        if self.thread_interface and self.thread_interface.is_alive():
            self.thread_interface.join(timeout=1)
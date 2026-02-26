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
            msg = json.loads(dados_json) if isinstance(dados_json, str) else dados_json
            if msg['type'] == 'chat':
                self.ultimo_remetente = msg['sender']
                self.ultima_mensagem = msg['message']
                
                if self.gui:
                    self.gui.adicionar_mensagem_outro(
                        msg['sender'],
                        msg['message'],
                        msg['timestamp']
                    )
                else:
                    print(f"\n[{msg['timestamp']}] {msg['sender']}: {msg['message']}")
                    print(">>> ", end='', flush=True)
                    
            elif msg['type'] == 'sistema':
                if self.gui:
                    self.gui.adicionar_mensagem_sistema(msg['message'])
                else:
                    print(f"\n*** {msg['message']} ***")
                    print(">>> ", end='', flush=True)
        except Exception as e:
            log_aplicacao(f"erro ao receber: {e}")
    
    def parar(self):
        self.executando = False
        if self.thread_interface and self.thread_interface.is_alive():
            self.thread_interface.join(timeout=1)
#camada_aplicacao.py

import threading
import json
from utils import log_aplicacao, criar_mensagem_json

class CamadaAplicacao:
    def __init__(self, nome_usuario, callback_enviar):
        #guarda nome e callback de envio
        self.nome = nome_usuario
        self.callback_enviar = callback_enviar
        self.executando = True
        
    def enviar_mensagem(self, mensagem):
        #monta mensagem json e envia
        msg_json = criar_mensagem_json("chat", self.nome, mensagem)
        log_aplicacao(f"criando mensagem: {msg_json}")
        if self.callback_enviar:
            self.callback_enviar(msg_json)
    
    def receber_mensagem(self, dados_json):
        try:
            #converte json e mostra no terminal
            msg = json.loads(dados_json) if isinstance(dados_json, str) else dados_json
            if msg['type'] == 'chat':
                print(f"\n[{msg['timestamp']}] {msg['sender']}: {msg['message']}")
                print(">>> ", end='', flush=True)
            elif msg['type'] == 'sistema':
                print(f"\n*** {msg['message']} ***")
                print(">>> ", end='', flush=True)
        except Exception as e:
            log_aplicacao(f"erro: {e}")
            
    def iniciar_interface(self):
        def ler_teclado():
            #le entrada e envia mensagens
            while self.executando:
                try:
                    texto = input()
                    if texto.lower() == '/sair':
                        self.executando = False
                        break
                    if texto.strip():
                        self.enviar_mensagem(texto)
                except:
                    break
        thread = threading.Thread(target=ler_teclado, daemon=True)
        thread.start()
        return thread
    
    def parar(self):
        #para a interface
        self.executando = False
#camada_aplicacao.py

import threading
import json
from utils import log_aplicacao, criar_mensagem_json

class CamadaAplicacao:
    def __init__(self, nome_usuario, callback_enviar):
        self.nome = nome_usuario
        self.callback_enviar = callback_enviar
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
                
                print(f"\n[{msg['timestamp']}] {msg['sender']}: {msg['message']}")
                print(">>> ", end='', flush=True)
                
                print(f"\n(Dica: digite /r para responder rapidamente a {msg['sender']})")
                print(">>> ", end='', flush=True)
                
            elif msg['type'] == 'sistema':
                print(f"\n*** {msg['message']} ***")
                print(">>> ", end='', flush=True)
        except Exception as e:
            log_aplicacao(f"erro ao receber: {e}")
    
    def responder_rapido(self, mensagem):
        if self.ultimo_remetente:
            self.enviar_mensagem(f"@{self.ultimo_remetente} {mensagem}")
            log_aplicacao(f"respondendo rapidamente para {self.ultimo_remetente}")
            return True
        else:
            print("\n*** Nenhuma mensagem anterior para responder ***")
            print(">>> ", end='', flush=True)
            return False
    
    def mostrar_ultima_mensagem(self):
        if self.ultimo_remetente and self.ultima_mensagem:
            print(f"\n*** Última mensagem: [{self.ultimo_remetente}] {self.ultima_mensagem} ***")
        else:
            print("\n*** Nenhuma mensagem recebida ainda ***")
        print(">>> ", end='', flush=True)
            
    def iniciar_interface(self):
        def ler_teclado():
            while self.executando:
                try:
                    texto = input()
                    
                    if texto.lower() == '/sair':
                        self.executando = False
                        break
                    elif texto.lower() == '/r':
                        print("Digite sua resposta rápida: ", end='', flush=True)
                        resposta = input()
                        if resposta:
                            self.responder_rapido(resposta)
                    elif texto.lower() == '/ultima':
                        self.mostrar_ultima_mensagem()
                    elif texto.lower() == '/ajuda':
                        self.mostrar_ajuda()
                    elif texto.startswith('/r '):
                        mensagem = texto[3:].strip()
                        if mensagem:
                            self.responder_rapido(mensagem)
                    elif texto:
                        self.enviar_mensagem(texto)
                        
                except (EOFError, KeyboardInterrupt):
                    break
                except Exception as e:
                    log_aplicacao(f"erro na interface: {e}")
                    break
        
        self.thread_interface = threading.Thread(target=ler_teclado, daemon=True)
        self.thread_interface.start()
        return self.thread_interface
    
    def mostrar_ajuda(self):
        print("\n" + "="*50)
        print("COMANDOS DISPONÍVEIS:")
        print("="*50)
        print("/sair     - Encerra o programa")
        print("/r        - Responde rapidamente à última mensagem")
        print("/r TEXTO  - Responde rapidamente com o texto (ex: /r Olá!)")
        print("/ultima   - Mostra a última mensagem recebida")
        print("/ajuda    - Mostra esta ajuda")
        print("="*50)
        print(">>> ", end='', flush=True)
    
    def parar(self):
        self.executando = False
        if self.thread_interface and self.thread_interface.is_alive():
            self.thread_interface.join(timeout=1)
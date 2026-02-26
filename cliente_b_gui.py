import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
from cliente_base import ClienteBase
import config

class ClienteBGUI:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("Cliente B - Mini-NET Chat")
        self.janela.geometry("500x700")
        self.janela.configure(bg='#1a1a1a')
        self.janela.minsize(450, 600)
        
        self.cores = {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2d2d2d',
            'bg_tertiary': '#3d3d3d',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'user_msg': '#dcf8c6',
            'other_msg': '#e3e3e3',
            'system': '#ffd700',
            'accent': '#ff6b6b'
        }
        
        self.cliente = None
        self.estatisticas = {
            'enviados': 0,
            'recebidos': 0,
            'perdas': 0,
            'retransmissoes': 0
        }
        
        self.criar_interface()
        self.iniciar_cliente()
        
    def criar_interface(self):
        header_frame = tk.Frame(self.janela, bg=self.cores['bg_secondary'], height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="CLIENTE B",
            font=("Arial", 16, "bold"),
            bg=self.cores['bg_secondary'],
            fg=self.cores['accent']
        ).pack(side=tk.LEFT, padx=15, pady=10)
        
        self.status_label = tk.Label(
            header_frame,
            text="● Online",
            font=("Arial", 10),
            bg=self.cores['bg_secondary'],
            fg='#4caf50'
        )
        self.status_label.pack(side=tk.RIGHT, padx=15, pady=10)
        
        chat_frame = tk.Frame(self.janela, bg=self.cores['bg_primary'])
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_chat = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg=self.cores['bg_secondary'],
            fg=self.cores['text_primary'],
            font=("Arial", 10),
            bd=0,
            padx=10,
            pady=10
        )
        self.text_chat.pack(fill=tk.BOTH, expand=True)
        
        self.text_chat.tag_config("system", foreground=self.cores['system'])
        self.text_chat.tag_config("user", foreground=self.cores['accent'])
        self.text_chat.tag_config("other", foreground='#4a9eff')
        self.text_chat.tag_config("time", foreground='#888888')
        
        self.text_chat.config(state=tk.DISABLED)
        
        options_frame = tk.Frame(self.janela, bg=self.cores['bg_secondary'], height=40)
        options_frame.pack(fill=tk.X, padx=10, pady=(0,5))
        options_frame.pack_propagate(False)
        
        self.destino_var = tk.StringVar(value="Todos")
        destino_menu = tk.OptionMenu(
            options_frame,
            self.destino_var,
            "Todos",
            "Cliente A (Privado)"
        )
        destino_menu.config(
            bg=self.cores['bg_tertiary'],
            fg='white',
            bd=0,
            font=("Arial", 9)
        )
        destino_menu.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            options_frame,
            text="Stats",
            bg=self.cores['bg_tertiary'],
            fg='white',
            bd=0,
            padx=15,
            command=self.mostrar_estatisticas
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            options_frame,
            text="Limpar",
            bg=self.cores['bg_tertiary'],
            fg='white',
            bd=0,
            padx=15,
            command=self.limpar_chat
        ).pack(side=tk.RIGHT, padx=5)
        
        input_frame = tk.Frame(self.janela, bg=self.cores['bg_secondary'], height=80)
        input_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        input_frame.pack_propagate(False)
        
        self.entry_mensagem = tk.Text(
            input_frame,
            height=3,
            bg=self.cores['bg_tertiary'],
            fg='white',
            font=("Arial", 10),
            bd=0,
            padx=10,
            pady=8,
            wrap=tk.WORD,
            insertbackground='white'
        )
        self.entry_mensagem.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,5), pady=5)
        
        self.entry_mensagem.bind('<Return>', self.enviar_mensagem_event)
        self.entry_mensagem.bind('<Shift-Return>', lambda e: None)
        
        self.btn_enviar = tk.Button(
            input_frame,
            text="Enviar",
            bg=self.cores['accent'],
            fg='white',
            bd=0,
            padx=20,
            font=("Arial", 10, "bold"),
            command=self.enviar_mensagem
        )
        self.btn_enviar.pack(side=tk.RIGHT, padx=(0,5), pady=5)
        
        self.digitando_label = tk.Label(
            self.janela,
            text="",
            bg=self.cores['bg_primary'],
            fg=self.cores['text_secondary'],
            font=("Arial", 8, "italic")
        )
        self.digitando_label.pack(anchor=tk.W, padx=20, pady=(0,5))
        
        self.adicionar_mensagem_sistema("Cliente B iniciado. Conectando ao servidor...")
    
    def iniciar_cliente(self):
        try:
            self.cliente = ClienteBase(
                vip=config.VIP_CLIENTE_B,
                mac=config.MAC_CLIENTE_B,
                porta=config.CLIENTE_B_PORTA,
                nome="Cliente_B",
                gui=self
            )
            self.adicionar_mensagem_sistema("Conectado ao servidor!")
        except Exception as e:
            self.adicionar_mensagem_sistema(f"Erro ao conectar: {e}")
    
    def enviar_mensagem(self, event=None):
        mensagem = self.entry_mensagem.get("1.0", tk.END).strip()
        
        if not mensagem:
            return
        
        self.entry_mensagem.delete("1.0", tk.END)
        
        destino = self.destino_var.get()
        
        if destino == "Cliente A (Privado)":
            mensagem_formatada = f"[Privado para Cliente A] {mensagem}"
        else:
            mensagem_formatada = mensagem
        
        self.adicionar_mensagem_usuario(mensagem_formatada)
        
        if self.cliente:
            self.cliente.enviar_mensagem(mensagem_formatada)
            self.estatisticas['enviados'] += 1
    
    def enviar_mensagem_event(self, event):
        self.enviar_mensagem()
        return "break"
    
    def adicionar_mensagem_usuario(self, mensagem):
        self.text_chat.config(state=tk.NORMAL)
        hora = datetime.now().strftime("%H:%M")
        
        self.text_chat.insert(tk.END, f"[{hora}] ", "time")
        self.text_chat.insert(tk.END, "Voce:\n", "user")
        self.text_chat.insert(tk.END, f"{mensagem}\n\n")
        
        self.text_chat.see(tk.END)
        self.text_chat.config(state=tk.DISABLED)
    
    def adicionar_mensagem_outro(self, remetente, mensagem, hora):
        self.text_chat.config(state=tk.NORMAL)
        
        self.text_chat.insert(tk.END, f"[{hora}] ", "time")
        self.text_chat.insert(tk.END, f"{remetente}:\n", "other")
        self.text_chat.insert(tk.END, f"{mensagem}\n\n")
        
        self.text_chat.see(tk.END)
        self.text_chat.config(state=tk.DISABLED)
        self.estatisticas['recebidos'] += 1
    
    def adicionar_mensagem_sistema(self, mensagem):
        self.text_chat.config(state=tk.NORMAL)
        hora = datetime.now().strftime("%H:%M")
        self.text_chat.insert(tk.END, f"[{hora}] ", "time")
        self.text_chat.insert(tk.END, f"* {mensagem}\n\n", "system")
        self.text_chat.see(tk.END)
        self.text_chat.config(state=tk.DISABLED)
    
    def mostrar_estatisticas(self):
        stats_window = tk.Toplevel(self.janela)
        stats_window.title("Estatisticas")
        stats_window.geometry("300x250")
        stats_window.configure(bg=self.cores['bg_primary'])
        
        total = self.estatisticas['enviados']
        perda_percent = (self.estatisticas['perdas'] / total * 100) if total > 0 else 0
        eficiencia = ((self.estatisticas['recebidos'] - self.estatisticas['retransmissoes']) / max(1, self.estatisticas['enviados']) * 100)
        
        stats_text = f"""
ESTATISTICAS DA CONEXAO
------------------------
Enviados: {self.estatisticas['enviados']}
Recebidos: {self.estatisticas['recebidos']}
Perdas: {self.estatisticas['perdas']} ({perda_percent:.1f}%)
Retransmissoes: {self.estatisticas['retransmissoes']}
Eficiencia: {eficiencia:.1f}%
"""
        
        tk.Label(
            stats_window,
            text=stats_text,
            bg=self.cores['bg_primary'],
            fg='white',
            font=("Courier", 10),
            justify=tk.LEFT,
            padx=20,
            pady=20
        ).pack()
        
        tk.Button(
            stats_window,
            text="Fechar",
            bg=self.cores['accent'],
            fg='white',
            bd=0,
            padx=20,
            pady=5,
            command=stats_window.destroy
        ).pack(pady=10)
    
    def limpar_chat(self):
        self.text_chat.config(state=tk.NORMAL)
        self.text_chat.delete("1.0", tk.END)
        self.text_chat.config(state=tk.DISABLED)
        self.adicionar_mensagem_sistema("Chat limpo")
    
    def atualizar_perda(self):
        self.estatisticas['perdas'] += 1
    
    def atualizar_retransmissao(self):
        self.estatisticas['retransmissoes'] += 1
    
    def sair(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair?"):
            if self.cliente:
                self.cliente.parar()
            self.janela.quit()
            self.janela.destroy()
    
    def rodar(self):
        self.janela.protocol("WM_DELETE_WINDOW", self.sair)
        self.janela.mainloop()

if __name__ == "__main__":
    app = ClienteBGUI()
    app.rodar()
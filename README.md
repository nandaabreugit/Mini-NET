# Mini-NET

Projeto de Redes de Computadores feito como um mini chat, mas com a ideia de simular as camadas de rede na prática.

## O que é esse projeto?

A proposta aqui foi montar um chat simples em Python, rodando em cima de UDP, mas com uma pilha de protocolo "nossa":

- camada de aplicação (mensagem em JSON)
- camada de transporte (Stop-and-Wait com ACK e retransmissão)
- camada de rede (VIP + TTL + roteamento)
- camada de enlace (MAC + CRC32)

Também tem simulação de rede com ruído (perda/corrupção de pacote), pra ficar mais próximo de um cenário real de rede.

## Camadas (resumo rápido)

- **Aplicação**: cria/recebe mensagens com `type`, `sender`, `message` e `timestamp`.
- **Transporte**: garante entrega com ACK, timeout e tentativa de reenvio.
- **Rede**: usa endereços virtuais (VIP), controla TTL e manda pro próximo salto.
- **Enlace**: encapsula quadro com MAC e valida erro com CRC32.

## Arquivos principais

- `cliente.py`: cliente do chat
- `servidor.py`: servidor do chat
- `roteador.py`: roteador que encaminha os pacotes
- `config.py`: IP, porta, VIP, MAC, timeout e TTL

## Como rodar

> Recomendado: abrir **3 terminais** na pasta do projeto.

### Terminal 1 - Roteador

```bash
python roteador.py
```

### Terminal 2 - Servidor

```bash
python servidor.py
```

### Terminal 3 - Cliente

```bash
python cliente.py
```

Se tudo estiver certo, cliente e servidor já vão mostrar o prompt do chat (`>>>`) e você consegue trocar mensagens.

## Comandos no chat

- `/sair` -> encerra o programa
- `/r` -> responde rápido a última mensagem
- `/r TEXTO` -> responde rápido com texto
- `/ultima` -> mostra a última mensagem recebida
- `/ajuda` -> lista os comandos

## Configuração

As configs ficam em `config.py`:

- IP e portas do cliente/servidor/roteador
- VIPs (endereços virtuais)
- MACs simulados
- timeout e máximo de tentativas
- TTL inicial

Dá pra mexer nesses valores pra testar cenários diferentes.

## Requisitos

- Python 3
- Biblioteca padrão (não precisa instalar pacote externo)

## Ideia do trabalho

Esse projeto é mais didático: a ideia principal foi entender na prática como as camadas se conversam, como ACK/retransmissão funciona e como erros de rede afetam a comunicação.
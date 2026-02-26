# Mini-NET

Projeto de Redes de Computadores - Chat com camadas de protocolo.

## Descrição
Implementação de um chat com pilha de protocolos própria sobre UDP, incluindo simulação de perda e corrupção de pacotes.

## Camadas Implementadas
- **Aplicação**: JSON com campos type, sender, message, timestamp
- **Transporte**: Stop-and-Wait com ACKs, timeouts e retransmissão
- **Rede**: Endereços virtuais VIP, TTL e roteamento estático
- **Enlace**: Endereços MAC e CRC32 para detecção de erros

## Como Executar

### 1. Inicie o servidor
```bash
python servidor.py
```
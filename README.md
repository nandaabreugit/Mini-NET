# Mini-NET

Projeto didático de Redes de Computadores que simula uma pilha de comunicação em camadas sobre UDP, com chat entre dois clientes GUI passando por roteador e servidor central.

## Objetivo

Demonstrar, na prática, como os dados são encapsulados e transportados entre camadas:

- **Aplicação**: mensagens de chat em JSON
- **Transporte**: confiabilidade com Stop-and-Wait (SEQ/ACK), timeout e retransmissão
- **Rede**: endereçamento virtual (VIP), TTL e decisão de rota
- **Enlace**: endereçamento MAC lógico e verificação de integridade (CRC32)

Também há simulação de rede ruidosa (perda/corrupção), útil para observar comportamento de retransmissão.

## Arquitetura do projeto

Fluxo principal:

1. Cliente A ou Cliente B cria mensagem na camada de aplicação
2. Mensagem passa por transporte, rede e enlace
3. Quadro chega ao roteador
4. Roteador encaminha ao servidor central
5. Servidor central identifica remetente e encaminha ao outro cliente
6. Cliente destinatário recebe, desempacota e exibe na GUI

## Estrutura dos arquivos

- `cliente_a_gui.py`: interface gráfica do Cliente A
- `cliente_b_gui.py`: interface gráfica do Cliente B
- `cliente_base.py`: infraestrutura de cliente (socket + pilha de camadas)
- `servidor_central.py`: servidor intermediário que recebe e encaminha mensagens
- `roteador.py`: roteador da simulação
- `camada_aplicacao.py`: lógica de criação/interpretação da mensagem
- `camada_transporte.py`: SEQ/ACK, timeout e retransmissão
- `camada_rede.py`: VIP/TTL e roteamento lógico
- `camada_enlace.py`: quadro e validação de integridade
- `protocolo.py`: estruturas de protocolo e serialização
- `config.py`: parâmetros de rede (IP, portas, VIP, MAC, TTL etc.)
- `utils.py`: logs e utilitários gerais
- `executar_tudo.py`: abre todos os componentes em terminais separados
- `teste_envio.py` / `teste_envio_ba.py`: scripts de verificação pontual de envio

## Requisitos

- Python 3.10+ (recomendado)
- Sistema operacional: Windows (suportado nativamente pelo `executar_tudo.py`)
- Não há dependências externas (somente biblioteca padrão)

## Como executar (opção 1: manual em terminais)

Abra **4 terminais** na pasta do projeto e execute nesta ordem.

### Terminal 1 - Roteador

```powershell
python roteador.py
```

### Terminal 2 - Servidor central

```powershell
python servidor_central.py
```

### Terminal 3 - Cliente A (GUI)

```powershell
python cliente_a_gui.py
```

### Terminal 4 - Cliente B (GUI)

```powershell
python cliente_b_gui.py
```

Quando as duas janelas abrirem e mostrarem status de conexão, já é possível trocar mensagens.

## Como executar (opção 2: automático com um comando)

Na pasta do projeto:

```powershell
python executar_tudo.py
```

O script `executar_tudo.py` abre novos terminais e inicia automaticamente:

1. `roteador.py`
2. `servidor_central.py`
3. `cliente_a_gui.py`
4. `cliente_b_gui.py`

## Execução alternativa no Windows (se `python` não funcionar)

Use o launcher do Python:

```powershell
py -3 executar_tudo.py
```

Ou para execução manual:

```powershell
py -3 roteador.py
py -3 servidor_central.py
py -3 cliente_a_gui.py
py -3 cliente_b_gui.py
```

## Configuração

Edite `config.py` para ajustar:

- IP e portas dos nós
- VIPs (endereços virtuais)
- MACs simulados
- TTL inicial
- parâmetros de confiabilidade e ruído de rede

## Testes rápidos inclusos

Para validar envio A -> B:

```powershell
python teste_envio.py
```

Para validar envio B -> A:

```powershell
python teste_envio_ba.py
```

> Importante: execute com roteador e servidor central já rodando.

## Dicas de uso

- Inicie sempre roteador e servidor antes dos clientes
- Se uma porta estiver em uso, feche processos antigos e execute novamente
- Se a rede simulada estiver com perda alta, podem ocorrer retransmissões e atrasos

## Solução de problemas

### Erro de porta ocupada (`Address already in use`)

- Feche instâncias anteriores do projeto
- Reinicie os terminais
- Verifique se não há outro processo usando as portas definidas em `config.py`

### Janela do cliente abre, mas não troca mensagens

- Confirme que `roteador.py` e `servidor_central.py` estão ativos
- Verifique logs no terminal para mensagens de timeout/retransmissão
- Confira se os valores de VIP/MAC/porta em `config.py` estão consistentes

### Comando `python` não reconhecido

- Use `py -3` no lugar de `python`
- Garanta que Python esteja instalado e no PATH

## Resumo

O Mini-NET é um laboratório prático para visualizar encapsulamento, roteamento, confiabilidade e tratamento de falhas em uma comunicação em camadas. A forma mais simples de iniciar tudo é com `python executar_tudo.py`; para depuração, prefira execução manual em 4 terminais.
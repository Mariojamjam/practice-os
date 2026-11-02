# Simulador de Sistema de Arquivos (File System Simulator)
### Sistemas Operacionais — Entrega Parcial 01
**Universidade Federal Rural de Pernambuco (UFRPE)**  
**Departamento de Computação (BCC)**  
**Docente:** Prof. Dr. Douglas Véras  
**Discentes:** Luiz Maranhão & Mário Jorge  

---

## Visão Geral do Projeto

Este projeto implementa um **Simulador Completo de Sistema de Arquivos**, desenvolvido em **Python 3** (utilizando exclusivamente a biblioteca padrão, sem dependências externas). O simulador modela fielmente tanto a **camada lógica hierárquica** (diretórios, arquivos e caminhos relativos/absolutos) quanto a **camada física do disco** (blocos de tamanho fixo, mapeamento físico, cálculo de fragmentação interna/externa e desfragmentação/compactação).

O simulador suporta **3 estratégias clássicas de alocação física**:
1. **Alocação Indexada (*i-node*)** — *(Estratégia padrão, exatamente como especificado no enunciado)*.
2. **Alocação Contígua** — *(Com demonstração de fragmentação externa e compactação de disco)*.
3. **Alocação Encadeada (*Linked List / FAT*)** — *(Com encadeamento de blocos via ponteiros)*.

---

## Como Executar

### Pré-requisitos
- **Python 3.8+** instalado no sistema. Não é necessário instalar nenhum pacote via `pip`.

### 1. Modo Demonstração Rápida (Exemplos 1.1 e 1.2 do Enunciado)
Para executar automaticamente os passos descritos pelo professor e validar a saída idêntica à especificação:

```bash
python fs_simulator.py --demo
```

### 2. Modo Shell Interativo (CLI)
Para navegar livremente, criar arquivos, diretórios e inspecionar o disco:

```bash
python fs_simulator.py
```

No Windows, você também pode simplesmente dar duplo clique no arquivo:
```text
iniciar_simulador.bat
```

### 3. Execução da Suíte de Testes Automatizados
Para rodar os testes unitários que validam todas as operações CRUD, resolução de caminhos e cálculos de fragmentação:

```bash
python test_fs_simulator.py
```

---

## Comandos Disponíveis no Shell Interativo

| Comando | Descrição | Exemplo de Uso |
| :--- | :--- | :--- |
| `mkdir <caminho>` | Cria um novo diretório (absoluto ou relativo) | `mkdir /sistema/logs` |
| `create <caminho> [--size <tam>]` | Cria arquivo com tamanho configurável (B, KB, MB) | `create /sistema/logs/app.log --size 10KB` |
| `cat` ou `read <caminho>` | Lê conteúdo e metadados físicos do arquivo | `cat /sistema/logs/app.log` |
| `update <caminho> --size <tam>` | Altera o tamanho do arquivo (realoca blocos) | `update /sistema/logs/app.log --size 16KB` |
| `rm <caminho>` | Deleta arquivo e desaloca seus blocos físicos | `rm /sistema/logs/app.log` |
| `rmdir <caminho> [-r]` | Deleta diretório (use `-r` para deletar recursivo) | `rmdir -r /sistema` |
| `ls [caminho]` | Lista itens do diretório com blocos alocados | `ls /sistema` |
| `cd <caminho>` | Altera o diretório corrente (suporta `.` e `..`) | `cd /sistema/logs` ou `cd ..` |
| `pwd` | Exibe o caminho do diretório corrente | `pwd` |
| `tree` | Renderiza a árvore hierárquica visual | `tree` |
| `fs_status [--details]` | Exibe o mapa de blocos e relatório de fragmentação | `fs_status --details` |
| `strategy [nome]` | Alterna entre: `indexada`, `contigua` ou `encadeada` | `strategy contigua` |
| `compact` | Desfragmenta o disco (consolida blocos contíguos) | `compact` |
| `format` | Reformata o disco com tamanho de bloco e total | `format --block-size 4KB --total-blocks 16` |
| `demo` | Executa o roteiro completo dos exemplos | `demo` |
| `help` | Exibe a lista de comandos e ajuda | `help` |
| `exit` | Encerra o simulador | `exit` |

---

## Exemplos de Execução Reais

### Exemplo 1.1 — Criação e Exibição da Árvore Hierárquica

```text
fs_sim:/ [Indexada (i-node)]> mkdir /sistema
Diretório '/sistema' criado com sucesso.

fs_sim:/ [Indexada (i-node)]> mkdir /sistema/logs
Diretório '/sistema/logs' criado com sucesso.

fs_sim:/ [Indexada (i-node)]> create /sistema/logs/app.log --size 10KB
Arquivo '/sistema/logs/app.log' criado com sucesso (10 KB, 3 blocos de dados).

fs_sim:/ [Indexada (i-node)]> tree
[ÁRVORE DO SISTEMA DE ARQUIVOS]
/
├── sistema/ [DIR]
│   └── logs/ [DIR]
│       └── app.log (10 KB) [ARQ]
```

### Exemplo 1.2 — Alocação Indexada e Diagnóstico de Fragmentação

```text
fs_sim:/ [Indexada (i-node)]> fs_status --details
Tamanho do Bloco de Disco: 4 KB | Total de Blocos: 16 (64 KB)

[MAPA DE ALOCAÇÃO DO DISCO (Indexado)]
Bloco 00 [INODE_RAIZ]  : Diretório '/'
Bloco 01 [INODE_APP]   : Arquivo '/sistema/logs/app.log'
Bloco 02 [DADO]        : '/sistema/logs/app.log' (Bloco 1 - 4096 bytes ocupados)
Bloco 03 [DADO]        : '/sistema/logs/app.log' (Bloco 2 - 4096 bytes ocupados)
Bloco 04 [DADO]        : '/sistema/logs/app.log' (Bloco 3 - 2048 bytes ocupados)
Bloco 05..15           : [LIVRE]

Visualização do Disco: [◆][◆][■][■][■][░][░][░][░][░][░][░][░][░][░][░]
Legenda: [◆] i-node | [■] Dado ocupado | [░] Livre

--- RELATÓRIO DE FRAGMENTAÇÃO ---
Tamanho Real do Arquivo 'app.log': 10240 bytes (10 KB)
Espaço Alocado no Disco          : 12288 bytes (3 blocos de 4 KB)
Fragmentação Interna             : 2048 bytes (50% de desperdício no Bloco 04)
Fragmentação Externa             : 0 bytes
Necessidade de Compactação       : NÃO (Blocos alocados via i-node indexado)
```

---

## Demonstração da Alocação Contígua e Fragmentação Externa

Na **Alocação Contígua**, cada arquivo deve ocupar blocos estritamente sequenciais. Quando arquivos intermediários são deletados, surgem "buracos" dispersos no disco. Se um novo arquivo requer $N$ blocos contíguos e não existe nenhum segmento individual com tamanho $\ge N$, a alocação falha mesmo que a soma total de blocos livres seja suficiente.

```text
fs_sim:/ [Contígua]> fs_status --details
Tamanho do Bloco de Disco: 4 KB | Total de Blocos: 16 (64 KB)

[MAPA DE ALOCAÇÃO DO DISCO (Contíguo)]
Bloco 00..03 [DADO]    : '/arqA.bin' (4 blocos)
Bloco 04..05           : [LIVRE]  <-- Buraco deixado por arquivo deletado
Bloco 06..11 [DADO]    : '/arqC.bin' (6 blocos)
Bloco 12..13 [DADO]    : '/arqD.bin' (2 blocos)
Bloco 14..15           : [LIVRE]  <-- Espaço livre no final

Visualização do Disco: [■][■][■][■][░][░][■][■][■][■][■][■][■][■][░][░]

--- RELATÓRIO DE FRAGMENTAÇÃO ---
Fragmentação Externa             : 8192 bytes (2 blocos dispersos em 2 segmentos)
Necessidade de Compactação       : SIM (Existem blocos livres dispersos não-contíguos)

fs_sim:/ [Contígua]> create /novo.bin --size 16KB
Erro: Falha de Alocação: Espaço insuficiente ou blocos contíguos indisponíveis no disco (Contígua) para 16 KB.

fs_sim:/ [Contígua]> compact
Compactação de disco concluída com sucesso! Todos os blocos livres estão contíguos.

fs_sim:/ [Contígua]> fs_status --details
Visualização do Disco: [■][■][■][■][■][■][■][■][■][■][■][■][░][░][░][░]
Fragmentação Externa             : 0 bytes
Necessidade de Compactação       : NÃO (Espaço livre está consolidado)

fs_sim:/ [Contígua]> create /novo.bin --size 16KB
Arquivo '/novo.bin' criado com sucesso (16 KB, 4 blocos de dados).
```

---

## Estrutura de Arquivos

```text
Simulador_Sistema_Arquivos/
├── fs_simulator.py       # Núcleo do simulador, CLI e lógica de alocação
├── test_fs_simulator.py  # Suíte de testes unitários automatizados
├── iniciar_simulador.bat # Script inicializador para Windows
└── README.md             # Documentação técnica e instruções
```

---

## Submissão no GitHub

Para subir este código no seu GitHub para a Entrega Parcial 01:

1. Crie um repositório no seu GitHub (ex.: `simulador-sistema-arquivos-so-ufrpe`).
2. No terminal da pasta `Simulador_Sistema_Arquivos`:
```bash
git init
git add .
git commit -m "Entrega Parcial 01 - Simulador de Sistema de Arquivos"
git branch -M main
git remote add origin https://github.com/<seu-usuario>/<nome-do-repo>.git
git push -u origin main
```
3. Copie o link do repositório e submeta no SIGAA/Google Classroom.

# Practice OS — Sistemas Operacionais
### Universidade Federal Rural de Pernambuco (UFRPE)
**Bacharelado em Ciência da Computação (BCC)**  
**Docente:** Prof. Dr. Douglas Véras  
**Discentes:** Luiz Maranhão & Mário Jorge  

---

## Visão Geral do Repositório

Este repositório consolida todas as atividades práticas, estudos de caso e projetos da disciplina de **Sistemas Operacionais**, abrangendo a **1ª VA** (análise comparativa profunda entre *Windows 11 Pro* e *Ubuntu 24.04 LTS*) e a **Entrega Parcial 01** (implementação e simulação prática de subsistemas do SO).

---

## Entrega Parcial 01: Simulador de Sistema de Arquivos

Implementação completa de um **Simulador de Sistema de Arquivos** em **Python 3** (biblioteca padrão, zero dependências externas). O simulador modela:
- **Hierarquia em Árvore:** diretórios e arquivos com suporte a caminhos absolutos (`/sistema/logs/app.log`) e relativos (`.`, `..`).
- **Operações CRUD:** criação, leitura, atualização e remoção de arquivos e diretórios.
- **Camada Física e Alocação de Blocos:** simulação de disco dividido em blocos de tamanho fixo (**16 blocos de 4 KB = 64 KB total**), com **3 estratégias de alocação**:
  1. *Alocação Indexada (i-node)* — *(Padrão solicitado)*
  2. *Alocação Contígua* — *(Com demonstração de fragmentação externa e compactação)*
  3. *Alocação Encadeada (Linked List / FAT)*
- **Diagnóstico do Disco:** mapa visual de ocupação de blocos, cálculo de fragmentação interna (desperdício no último bloco), cálculo de fragmentação externa e indicação explícita da necessidade de compactação.

### Como Executar

```bash
# 1. Demonstração automática dos Exemplos 1.1 e 1.2 do enunciado:
python fs_simulator.py --demo

# 2. Executar a suíte de testes unitários automatizados (100% OK):
python test_fs_simulator.py

# 3. Abrir o Shell Interativo CLI:
python fs_simulator.py
```

*(No Windows, você também pode simplesmente dar duplo clique em `iniciar_simulador.bat`)*

### Exemplos de Saída do Simulador

#### Exemplo 1.1 — Criação e Exibição da Árvore Hierárquica
```text
> mkdir /sistema
> mkdir /sistema/logs
> create /sistema/logs/app.log --size 10KB

[ÁRVORE DO SISTEMA DE ARQUIVOS]
/
├── sistema/ [DIR]
│   └── logs/ [DIR]
│       └── app.log (10 KB) [ARQ]
```

#### Exemplo 1.2 — Alocação Indexada e Análise de Fragmentação
```text
> fs_status --details
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

## 1ª VA — Estudos de Caso Consolidados

Análise comparativa profunda entre o **Windows 11 Pro (23H2 / 24H2)** e o **Ubuntu 24.04 LTS (Kernel Linux 6.8)** em todos os 6 tópicos do semestre:

| Módulo / Estudo de Caso | Relatório Técnico | Planilha Comparativa (.xlsx) | Apresentação em Slides (.pptx) |
| :--- | :---: | :---: | :---: |
| **01. Arquitetura e Kernel** | [Relatório](1a_VA_Estudos_de_Caso/Relatorios/Estudo_de_Caso_Processos_Relatorio.md) | [Planilha](1a_VA_Estudos_de_Caso/Planilhas/modelo_estudo_caso_processos_preenchido.xlsx) | [Slides](1a_VA_Estudos_de_Caso/Apresentacoes/Apresentacao_Final_SO_AgoraVai_100_Final.pptx) |
| **02. Processos e Threads** | [Relatório](1a_VA_Estudos_de_Caso/Relatorios/Estudo_de_Caso_Processos_Relatorio.md) | [Planilha](1a_VA_Estudos_de_Caso/Planilhas/modelo_estudo_caso_processos_preenchido.xlsx) | [Slides](1a_VA_Estudos_de_Caso/Apresentacoes/Apresentacao_Estudo_de_Caso_Processos.pptx) |
| **03. Gerenciamento de Memória** | [Relatório](1a_VA_Estudos_de_Caso/Relatorios/Estudo_de_Caso_Memoria_Relatorio.md) | [Planilha](1a_VA_Estudos_de_Caso/Planilhas/modelo_estudo_caso_memoria_preenchido.xlsx) | [Slides](1a_VA_Estudos_de_Caso/Apresentacoes/Apresentacao_Estudo_de_Caso_Memoria.pptx) |
| **04. Sistemas de Arquivos** | [Relatório](1a_VA_Estudos_de_Caso/Relatorios/Estudo_de_Caso_Arquivos_Relatorio.md) | [Planilha](1a_VA_Estudos_de_Caso/Planilhas/modelo_estudo_caso_arquivos_preenchido.xlsx) | [Slides](1a_VA_Estudos_de_Caso/Apresentacoes/Apresentacao_Final_SO_AgoraVai_100_Final.pptx) |
| **05. Entrada e Saída (E/S)** | [Relatório](1a_VA_Estudos_de_Caso/Relatorios/Estudo_de_Caso_ES_Relatorio.md) | [Planilha](1a_VA_Estudos_de_Caso/Planilhas/modelo_estudo_caso_es_preenchido.xlsx) | [Slides](1a_VA_Estudos_de_Caso/Apresentacoes/Apresentacao_Estudo_de_Caso_ES.pptx) |
| **06. Segurança e Proteção** | [Relatório](1a_VA_Estudos_de_Caso/Relatorios/Estudo_de_Caso_Seguranca_Relatorio.md) | [Planilha](1a_VA_Estudos_de_Caso/Planilhas/modelo_estudo_caso_seguranca_preenchido.xlsx) | [Slides](1a_VA_Estudos_de_Caso/Apresentacoes/Apresentacao_Estudo_de_Caso_Seguranca.pptx) |

### Material de Apoio da 1ª VA
- **Apresentação Consolidada Oficial:** [Apresentacao_Final_SO_AgoraVai_100_Final.pptx](1a_VA_Estudos_de_Caso/Apresentacoes/Apresentacao_Final_SO_AgoraVai_100_Final.pptx)
- **Guia de Apresentação e Sorteio (PDF):** [Guia_Apresentacao_Sorteio_1VA_Luiz.pdf](1a_VA_Estudos_de_Caso/Guias_e_Questionarios/Guia_Apresentacao_Sorteio_1VA_Luiz.pdf)

---

## Estrutura de Diretórios do Repositório

```text
practice-os/
├── README.md                              # Documentação e guia geral do repositório
├── .gitignore                             # Filtro de arquivos temporários e caches
├── fs_simulator.py                        # Executável do Simulador de Sistema de Arquivos (Entrega Parcial 01)
├── test_fs_simulator.py                   # Suíte de testes unitários automatizados
├── iniciar_simulador.bat                  # Inicializador interativo para Windows
│
├── Simulador_Sistema_Arquivos/            # Pacote completo e isolado da Entrega Parcial 01
│   ├── fs_simulator.py
│   ├── test_fs_simulator.py
│   ├── iniciar_simulador.bat
│   └── README.md
│
├── 1a_VA_Estudos_de_Caso/                 # Todos os entregáveis e artefatos da 1ª VA
│   ├── Apresentacoes/                     # Decks de slides (.pptx)
│   ├── Planilhas/                         # Planilhas comparativas oficiais (.xlsx)
│   ├── Relatorios/                        # Relatórios técnicos em Markdown (.md)
│   ├── Guias_e_Questionarios/             # Guia de apresentação para sorteio e gabaritos
│   └── Scripts_Geradores/                 # Scripts Python que geram planilhas e slides
│
└── Documentos_Gerais/                     # Cronograma, diário de aulas e acompanhamento
    ├── Cronograma.md
    ├── Diario_de_Aulas.md
    ├── Regras_e_Avaliacao.md
    ├── status_disciplina.md
    └── Tarefa_Filmes_SO.md
```

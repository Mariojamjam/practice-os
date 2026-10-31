# Guia Definitivo de Apresentação — Avaliação da 1ª VA
## Simulação de Sorteio por Estudo de Caso — Roteiro de Luiz Maranhão (Especialista Windows 11 Pro)

**Instituição:** Universidade Federal Rural de Pernambuco (UFRPE)  
**Disciplina:** Sistemas Operacionais | **Docente:** Prof. Dr. Douglas Véras  
**Discentes:** Luiz Maranhão & Mário Jorge  
**Deck Oficial de Slides:** `Apresentacao_Final_1VA_Consolidada.pptx` (16 slides)  
**Divisão da Dupla:**
* **Mário Jorge:** Fundamentos conceituais, diagrama teórico do SO e arquitetura do **Ubuntu 24.04 LTS (Kernel Linux 6.8)**.
* **Luiz Maranhão:** Arquitetura interna, mecanismos de engenharia, segurança e comandos do **Windows 11 Pro (23H2 / 24H2)**.

---

## Índice Rápido dos Estudos de Caso Sorteáveis

1. [Estudo 1: Introdução e Arquitetura de SOs](#estudo-1-introdução-e-arquitetura-de-sos) (Slide 03)
2. [Estudo 2: Gerenciamento de Processos](#estudo-2-gerenciamento-de-processos) (Slide 04)
3. [Estudo 3: Gerenciamento de Memória](#estudo-3-gerenciamento-de-memória) (Slide 05)
4. [Estudo 4: Sistemas de Arquivos](#estudo-4-sistemas-de-arquivos) (Slide 06)
5. [Estudo 5: Subsistema de Entrada e Saída (E/S)](#estudo-5-subsistema-de-entrada-e-saída-es) (Slide 07)
6. [Estudo 6: Segurança e Proteção dos SOs](#estudo-6-segurança-e-proteção-dos-sos) (Slides 08 a 12)

---

## Estudo 1: Introdução e Arquitetura de SOs

### 1. Slide Correspondente
* **Slide 03:** `ENTREGA PARCIAL 01 · INTRODUÇÃO E ARQUITETURA` — *Arquitetura do kernel e anéis de privilégio*
* **Apoio Prático:** **Slide 13** (Linha 01: *Kernel e boot*).
* **Elementos em Tela:**
  * *Lado Esquerdo (Diagrama):* Círculos concêntricos de anéis de privilégio da CPU (Ring 3: Aplicações → Ring 0: Kernel → Ring -1: Hipervisor → Hardware/TPM 2.0).
  * *Lado Direito (Tabela):* Comparativo de Tipo de Kernel, Chamadas de Sistema, Isolamento e Boot Seguro.

### 2. Como Explicar o Estudo (Estratégia Didática)
* **Objetivo:** Demonstrar como o sistema operacional organiza o acesso ao hardware e isola código não confiável através dos anéis de privilégio da CPU (x86_64).
* **Dinâmica com Mário:** Mário inicia apresentando o diagrama dos anéis de privilégio e o modelo de Kernel Monolítico Modular do Linux. Quando ele concluir, você assume para apresentar a visão do Windows 11.

### 3. O que Falar (Roteiro de Luiz — Foco em Windows 11 Pro)
> *"Perfeito, Mário. Agora olhando para a engenharia do **Windows 11 Pro**, a Microsoft adota um modelo de **Kernel Híbrido** centrado no executivo `ntoskrnl.exe`. Diferente de um microkernel puro, componentes críticos como o gerenciador de memória, o sistema de arquivos e os subsistemas de segurança executam em modo protegido no **Ring 0**, apoiados pela camada de abstração de hardware, a **HAL**.*
>
> *As aplicações do usuário rodam isoladas no **Ring 3**. Quando uma aplicação Win32 precisa de qualquer serviço do sistema, ela não acessa o hardware diretamente: ela invoca a `ntdll.dll`, que despacha a instrução assembly `syscall`, realizando a transição segura para o Ring 0.*
>
> *O grande salto arquitetural do Windows 11 é a exigência do **Ring -1 via VBS (Virtualization-Based Security)**. Usando o hipervisor do Hyper-V, o Windows cria um enclave seguro chamado VTL 1 (Virtual Trust Level 1), onde executa processos críticos como o isolamento de credenciais (`LSAISO`). Mesmo que um invasor obtenha privilégio total de administrador ou execute código arbitrário no Ring 0, ele **não consegue** violar o Ring -1.*
>
> *Para garantir a integridade desde o ligamento, o Windows 11 exige obrigatoriamente o chip físico **TPM 2.0**, o **UEFI Secure Boot** e a proteção contra DMA malicioso de barramento."*

### 4. O que Mostrar na Planilha
* **Arquivo:** Se o professor pedir para abrir a planilha geral/arquitetura, aponte:
  * Linha de **Tipo de Kernel:** Destaque o termo `Kernel Híbrido NT` e a estrutura em camadas (`HAL -> Microkernel -> Executive`).
  * Linha de **Root of Trust / Inicialização:** Mostre a cadeia criptográfica `UEFI Secure Boot -> Windows Boot Manager (bootmgfw.efi) -> winload.efi -> ntoskrnl.exe`.
  * Coluna de Comandos do Windows:
    * `Confirm-SecureBootUEFI` (retorna `True` validando a assinatura digital do boot).
    * `Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard` (demonstra o VBS ativo).

### 5. Perguntas Prováveis da Banca & Resposta Cirúrgica
* **Pergunta do Prof. Douglas:** *"Por que o Windows é chamado de 'Híbrido' e não de Microkernel puro?"*
  * **Sua Resposta:** *"Professor, o projeto original do NT visava ser um microkernel, mas por questões de latência e desempenho de transição de contexto, subsistemas críticos como o subsistema gráfico (win32k.sys) e gerenciamento de E/S foram movidos para dentro do Ring 0. Ele mantém a modularidade orientada a objetos do microkernel, mas com o desempenho de execução compartilhada do monolítico."*

---

## Estudo 2: Gerenciamento de Processos

### 1. Slide Correspondente
* **Slide 04:** `ENTREGA PARCIAL 02 · GERENCIAMENTO DE PROCESSOS` — *Processos, threads e escalonamento*
* **Apoio Prático:** **Slide 13** (Linha 02: *Processos e Escalonamento*).
* **Elementos em Tela:**
  * *Lado Esquerdo (Diagrama):* Ciclo de vida e estados de uma tarefa (Novo → Pronto → Executando → Bloqueado → Terminado), com o fluxo de preempção e comutação de contexto salvando o estado no PCB.
  * *Lado Direito (Tabela):* Comparativo de Estrutura (PCB), Criação, Algoritmo de Escalonamento e IPC/Sincronização.

### 2. Como Explicar o Estudo (Estratégia Didática)
* **Objetivo:** Mostrar como o SO abstrai a execução dinâmica de programas, mantém o contexto de hardware de cada processo e decide qual thread recebe a CPU a cada fração de segundo.
* **Dinâmica com Mário:** Mário explica o ciclo clássico de estados e a abordagem do Linux com `task_struct`, `fork()` Copy-on-Write e o escalonador EEVDF. Você assume para contrapor com a engenharia de processos e threads do Windows.

### 3. O que Falar (Roteiro de Luiz — Foco em Windows 11 Pro)
> *"Complementando a visão do Linux trazida pelo Mário, no **Windows 11** há uma distinção conceitual fundamental: o **processo não executa código**; quem executa é a **Thread**. O processo é apenas um contêiner de recursos.*
>
> *No kernel, essa modelagem é dividida em três estruturas:*
> 1. *O **KPROCESS**, no nível de hardware, que guarda o diretório de páginas (registrador CR3);*
> 2. *O **EPROCESS** (o PCB principal no Executivo NT), que contém a tabela de handles de arquivos, o token de segurança e a lista de threads ativas;*
> 3. *O **PEB** (Process Environment Block), que reside no espaço de usuário para carregar DLLs sem precisar de chamada de sistema.*
>
> *Para criação, o Windows utiliza a API `CreateProcessW()`. Diferente do fork do Linux que usa Copy-on-Write, o Windows aloca imediatamente um novo espaço de endereçamento virtual privado e mapeia a imagem do executável PE (Portable Executable).*
>
> *No escalonamento, o Windows 11 adota um modelo **preemptivo por prioridade dinâmica com 32 níveis (0 a 31)**. De 16 a 31 são prioridades de Tempo Real; de 1 a 15 são prioridades dinâmicas. O grande diferencial do Windows 11 é o **Dynamic Priority Boost**, que aumenta temporariamente o quantum e a prioridade de threads de janelas em primeiro plano (Foreground Boost) para garantir fluidez visual, além da integração com o **Intel Thread Director** para despachar threads pesadas em P-cores e leves em E-cores.*
>
> *Para comunicação interprocessos (IPC), o Windows oferece portas de alta velocidade chamadas **ALPC** (usadas pelos subsistemas internos) e **Named Pipes** para rede."*

### 4. O que Mostrar na Planilha
* **Arquivo:** `modelo_estudo_caso_processos_preenchido.xlsx`
* **Onde focar:**
  * **Linha 1 ("Informações de um processo"):** Destaque na coluna B os campos *PID, Token de Segurança, Tabela de Handles, Working Set e PEB*.
  * **Linha 7 ("Prioridades de um processo"):** Mostre a divisão das classes do Windows: *Idle (4), Normal (8), High (13) e Realtime (24)*.
  * **Linha de Comandos (Coluna C):**
    * `Get-Process | Sort-Object WorkingSet -Descending | Select -First 5` (inspeção via PowerShell).
    * `tasklist /v /fo list` (detalhamento clássico).
    * Mencione o uso do **Sysinternals Process Explorer** para ver a árvore genealógica e as threads do processo.

### 5. Perguntas Prováveis da Banca & Resposta Cirúrgica
* **Pergunta do Prof. Douglas:** *"O que acontece no Windows se um processo pai for encerrado abruptamente? Os processos filhos viram zumbis como no Linux?"*
  * **Sua Resposta:** *"Não, professor. No Windows não existe relação genealógica rígida em árvore mantida no kernel. O EPROCESS apenas grava o PID do criador. Se o processo pai morre, o filho continua executando de forma independente, sem necessidade de wait() e sem estado zumbi. Se o desenvolvedor quiser encerramento em cascata, ele precisa associar os processos a um **Job Object**."*

---

## Estudo 3: Gerenciamento de Memória

### 1. Slide Correspondente
* **Slide 05:** `ENTREGA PARCIAL 03 · GERENCIAMENTO DE MEMÓRIA` — *Memória virtual e paginação*
* **Apoio Prático:** **Slide 13** (Linha 03: *Memória Virtual e Física*).
* **Elementos em Tela:**
  * *Lado Esquerdo (Diagrama):* Tradução de páginas virtuais para quadros físicos de RAM pela MMU/TLB, destacando a rota tracejada vermelha de **Page Fault** buscando páginas no Swap/Disco.
  * *Lado Direito (Tabela):* Comparativo de Espaço Virtual (128 TB), Política de Substituição, Falta de RAM (Compressão vs Swap) e Proteções de Memória.

### 2. Como Explicar o Estudo (Estratégia Didática)
* **Objetivo:** Explicar como a memória virtual engana os processos fazendo cada um acreditar que possui a memória inteira para si, e como o SO gerencia a RAM física finita através da paginação.
* **Dinâmica com Mário:** Mário explica a tradução da MMU, o Page Fault e como o Linux gerencia páginas via Buddy System, SLUB e MGLRU. Você entra para explicar o Gerenciador de Memória do Windows (VMM), Working Sets e o recurso inovador de compressão de memória.

### 3. O que Falar (Roteiro de Luiz — Foco em Windows 11 Pro)
> *"Excelente. No **Windows 11 Pro**, o subsistema responsável é o **Virtual Memory Manager (VMM)**. Em arquiteturas de 64 bits, cada processo recebe um espaço de endereçamento linear gigantesco de **128 Terabytes privados**, estruturado através de uma árvore binária balanceada de **VADs (Virtual Address Descriptors)**.*
>
> *A paginação de hardware opera no padrão de **4 KB**, utilizando tabelas de 4 níveis (PML4). O estado de cada moldura física da RAM é rastreado por um array global no kernel chamado **PFN Database** (Page Frame Number).*
>
> *O conceito central do Windows para alocação é o **Working Set** (Conjunto de Trabalho). O VMM não deixa as páginas soltas: ele define cotas mínima e máxima de páginas residentes na RAM para cada processo. Quando o sistema precisa de memória, ele executa o 'Working Set Trimming': retira páginas inativas e as move para a lista **Standby** (se estiverem limpas) ou **Modified** (se foram alteradas).*
>
> *E aqui está um dos maiores destaques de engenharia do Windows moderno: antes de enviar uma página alterada para o disco lento no `pagefile.sys`, o Windows realiza a **Compactação de Memória na própria RAM**. O processo 'System' comprime esses blocos usando algoritmos rápidos. Descomprimir uma página na RAM é ordens de grandeza mais rápido do que fazer uma operação de I/O em SSD ou HD.*
>
> *Na segurança, o Windows aplica **ASLR de Alta Entropia** (embaralhando endereços de 64 bits) e **DEP/NX** baseado em hardware, impedindo que código seja executado na pilha ou heap."*

### 4. O que Mostrar na Planilha
* **Arquivo:** `modelo_estudo_caso_memoria_preenchido.xlsx`
* **Onde focar:**
  * **Linha 1 ("O SO utiliza paginação?"):** Aponte na coluna B as estruturas `PML4 -> PDPT -> PD -> PT -> PTE` e o `PFN Database`.
  * **Linha 3 ("O SO faz uso Swap?"):** Mostre a distinção entre o `pagefile.sys` (para paginação tradicional) e o `swapfile.sys` (usado para suspensão de aplicativos universais UWP).
  * **Linha de Comandos (Coluna C):**
    * `Get-CimInstance Win32_PageFileUsage` (mostra o tamanho alocado e pico de uso do swap).
    * `resmon.exe` (Monitor de Recursos > Guia Memória: gráfico com memória Em Uso, Modificada, Standby e Livre).
    * `rammap.exe` e `vmmap.exe` do Sysinternals.

### 5. Perguntas Prováveis da Banca & Resposta Cirúrgica
* **Pergunta do Prof. Douglas:** *"Qual a diferença entre uma página na lista Standby e uma página na lista Free no Windows?"*
  * **Sua Resposta:** *"Excelente pergunta, professor. Uma página na lista 'Free' é memória limpa e sem dono, pronta para qualquer um usar. Já a página na lista 'Standby' ainda mantém o dado de um processo anterior que foi retirado do Working Set. Se o processo precisar daquele dado de novo, ocorre um 'Soft Page Fault': a página volta para o processo instantaneamente sem tocar no disco. Mas se outro processo precisar de RAM limpa, a página Standby é descartada."*

---

## Estudo 4: Sistemas de Arquivos

### 1. Slide Correspondente
* **Slide 06:** `ENTREGA PARCIAL 04 · SISTEMAS DE ARQUIVOS` — *Organização dos sistemas de arquivos*
* **Apoio Prático:** **Slide 13** (Linha 04: *Sistemas de Arquivos*).
* **Elementos em Tela:**
  * *Lado Esquerdo (Diagrama):* Registro de metadados apontando para blocos contíguos (*extents*) no disco, e abaixo o ciclo em 3 fases do **Journaling** (1. Registra no log → 2. Grava no disco → 3. Confirma a transação).
  * *Lado Direito (Tabela):* Comparativo de Sistema Padrão (NTFS vs ext4), Metadados (MFT vs Inodes), Alocação e Consistência Transacional.

### 2. Como Explicar o Estudo (Estratégia Didática)
* **Objetivo:** Mostrar como o SO estrutura dados não voláteis em blocos lógicos no disco, como armazena atributos/metadados e como se recupera de travamentos repentinos através do log de journal.
* **Dinâmica com Mário:** Mário detalha a abstração do VFS do Linux, a estrutura do ext4 com Inodes de 256 bytes e o Journaling JBD2. Você entra para defender e demonstrar a robustez corporativa do NTFS.

### 3. O que Falar (Roteiro de Luiz — Foco em Windows 11 Pro)
> *"No **Windows 11 Pro**, o sistema de arquivos padrão é o **NTFS (New Technology File System)**, complementado pelo ReFS para storages empresariais.*
>
> *A filosofia do NTFS é elegante e unificada: **no NTFS, absolutamente tudo é um arquivo**, inclusive o próprio sistema de arquivos. O coração do volume é a **MFT (Master File Table)**. A MFT é tratada como um grande banco de dados composto por registros fixos de **1 Kilobyte**.*
>
> *Cada arquivo é uma coleção de atributos (Nome, Datas, Permissões e Dados). E aqui está uma sacada brilhante do NTFS: se um arquivo for pequeno — menor que aproximadamente 700 bytes —, o conteúdo dos dados é gravado **diretamente dentro do registro do arquivo na MFT**. Isso é chamado de **Resident File** e elimina qualquer busca extra em setores distantes do disco!*
>
> *Para arquivos grandes, o NTFS aloca blocos contíguos chamados **Extents** (ou Runlists). Na organização de diretórios com milhares de itens, o NTFS não faz varredura linear: ele constrói uma **Árvore B+ (B-Tree)** ordenada, garantindo buscas em tempo logarítmico $O(\log n)$.*
>
> *Para garantir integridade contra falhas de energia, o NTFS utiliza o arquivo de log oculto **`$LogFile`** com o mecanismo Write-Ahead Logging. Qualquer modificação de metadados é gravada no log antes de ser escrita no disco. Se o computador desligar da tomada, ao reiniciar o NTFS não precisa de um scandisk demorado: ele lê o log e recupera a consistência em milissegundos."*

### 4. O que Mostrar na Planilha
* **Arquivo:** `modelo_estudo_caso_arquivos_preenchido.xlsx`
* **Onde focar:**
  * **Linha 1 ("Introdução ao Sistema de Arquivos"):** Aponte o modelo de Namespace com letras de unidades (`C:\`, `D:\`) mapeadas via links simbólicos do kernel (`\Device\HarddiskVolumeX`) e o suporte a múltiplos fluxos (*Alternate Data Streams - ADS*).
  * **Linha 2 ("Estrutura Interna e Organização"):** Mostre o conceito da MFT de 1 KB, os atributos tipados (`$STANDARD_INFORMATION`, `$FILE_NAME`, `$DATA`) e a árvore B+.
  * **Linha de Comandos (Coluna C):**
    * `fsutil fsinfo ntfsinfo C:` (mostra tamanho de cluster, início da MFT e zonas reservadas).
    * `chkdsk C: /scan` (auditoria de integridade online).

### 5. Perguntas Prováveis da Banca & Resposta Cirúrgica
* **Pergunta do Prof. Douglas:** *"O que são os Alternate Data Streams (ADS) do NTFS e qual o impacto deles na segurança?"*
  * **Sua Resposta:** *"Professor, o NTFS permite associar mais de um fluxo de dados a um mesmo arquivo sob a sintaxe `arquivo.txt:fluxo`. O Windows usa isso nativamente para marcar a 'Zone.Identifier' em arquivos baixados da internet (SmartScreen). Porém, atuações maliciosas podem ocultar executáveis ou scripts dentro de um fluxo secundário sem alterar o tamanho visível do arquivo principal no Explorer."*

---

## Estudo 5: Subsistema de Entrada e Saída (E/S)

### 1. Slide Correspondente
* **Slide 07:** `ENTREGA PARCIAL 05 · ENTRADA E SAÍDA` — *Subsistema de entrada e saída*
* **Apoio Prático:** **Slide 13** (Linha 05: *Entrada e Saída*).
* **Elementos em Tela:**
  * *Lado Esquerdo (Diagrama):* Pilha em camadas da E/S descendo da Aplicação até a Controladora. Destaque para a transferência **DMA** direta para a RAM e a **interrupção (IRQ)** notificando a CPU ao término.
  * *Lado Direito (Tabela):* Comparativo de Modelo de Drivers, Estrutura de Requisição (IRP vs bio), E/S Assíncrona e Proteção de DMA via IOMMU.

### 2. Como Explicar o Estudo (Estratégia Didática)
* **Objetivo:** Mostrar como o SO abstrai a imensa variedade de periféricos (discos NVMe, placas de rede, barramentos USB), trata operações assíncronas e evita que dispositivos maliciosos acessem a memória indevidamente.
* **Dinâmica com Mário:** Mário apresenta a pilha do Linux (VFS, camada `blk-mq`, `io_uring` e representação em `/dev`). Você assume para explicar a arquitetura orientada a pacotes IRP e o framework WDF do Windows.

### 3. O que Falar (Roteiro de Luiz — Foco em Windows 11 Pro)
> *"No subsistema de **Entrada e Saída do Windows 11**, a arquitetura é gerenciada pelo **I/O Manager** no Executivo NT.*
>
> *O princípio fundamental aqui é o **modelo modular orientado a pacotes**. Quando uma aplicação chama `ReadFile()`, o I/O Manager aloca uma estrutura no kernel chamada **IRP (I/O Request Packet)**. Esse pacote viaja verticalmente através de uma pilha hierárquica de drivers:*
> 1. *Primeiro passa pelos **Filter Drivers** (onde atuam o antivírus Defender e a criptografia BitLocker);*
> 2. *Depois atinge o **Driver Funcional (FDO)**, como o driver do sistema de arquivos NTFS;*
> 3. *E chega aos drivers de barramento e porta (`StorNVMe.sys` ou `USBPORT.SYS`).*
>
> *Para estabilidade, a Microsoft criou o framework **WDF**, dividido em **KMDF** (drivers em modo kernel) e **UMDF** (drivers em modo usuário). Com o UMDF, drivers de sensores, USB e impressoras executam no Ring 3. Se um driver com bug travar, ele **não dá tela azul** (BSOD); o SO simplesmente reinicia o processo do driver.*
>
> *Para alta concorrência assíncrona em servidores e bancos de dados, o Windows utiliza **IOCP (I/O Completion Ports)**, que atrela threads a filas de conclusão sem bloqueio de CPU.*
>
> *E no controle de hardware, o Windows 11 faz uso estrito da **IOMMU (Intel VT-d / AMD-Vi)** através do **Kernel DMA Protection**, impedindo ataques físicos onde dispositivos Thunderbolt/PCIe maliciosos tentavam ler a RAM diretamente via DMA."*

### 4. O que Mostrar na Planilha
* **Arquivo:** `modelo_estudo_caso_es_preenchido.xlsx`
* **Onde focar:**
  * **Linha 1 ("Introdução a E/S"):** Mostre o fluxo dos pacotes IRP e a abstração de objetos `\Device\HarddiskVolumeX`.
  * **Linha 2 ("Estrutura de Drivers WDM/WDF"):** Aponte a vantagem do *UMDF* rodando em Ring 3 para evitar travamento do núcleo.
  * **Linha de Comandos (Coluna C):**
    * `Get-PnpDevice -Class 'DiskDrive', 'SCSIAdapter'` (inspeção de periféricos PnP).
    * `driverquery /v /fo table` (lista todos os drivers de kernel e seus modos de início).
    * `devmgmt.msc` (Gerenciador de Dispositivos).

### 5. Perguntas Prováveis da Banca & Resposta Cirúrgica
* **Pergunta do Prof. Douglas:** *"O que é a IOMMU e qual a diferença entre DMA tradicional e DMA protegido por IOMMU?"*
  * **Sua Resposta:** *"Professor, o DMA tradicional permite que uma placa periférica leia e escreva em qualquer endereço físico da RAM sem passar pela CPU. O risco é que um dispositivo PCIe ou porta Thunderbolt comprometida poderia ler senhas e chaves da memória. A **IOMMU** funciona como uma MMU para os periféricos: ela traduz endereços de barramento em endereços físicos e bloqueia qualquer dispositivo que tente acessar páginas de memória fora do buffer autorizado pelo kernel."*

---

## Estudo 6: Segurança e Proteção dos SOs

*(Este é o seu estudo de caso principal, composto pelos **Slides 08 ao 12** no deck final).*

### 1. Slides Correspondentes
* **Slide 08:** *Introdução à segurança dos SOs (Tríade CIA e Menor Privilégio)*
* **Slide 09:** *Principais ameaças e pontos fracos (Kill Chain e Superfície de Ataque)*
* **Slide 10:** *Criptografia: o que é protegido e como (Hierarquia de Chaves e FDE)*
* **Slide 11:** *Autenticação e controle de acesso (Validação do Kernel MAC/DAC)*
* **Slide 12:** *Ferramentas nativas contra malware (Defesa em Profundidade)*
* **Apoio Prático:** **Slide 13** (Linhas 06 e 07).

### 2. Como Explicar o Estudo (Estratégia Didática)
* **Objetivo:** Demonstrar que o SO é a fundação de segurança de toda a computação. Explicar a Tríade CIA, desmistificar ataques modernos, detalhar como a criptografia protege o repouso e como o kernel valida cada abertura de recurso.
* **Dinâmica com Mário:** Como você é o especialista da área de segurança, você conduzirá os slides 08, 09 e 10 (conceitos, ameaças e criptografia). Mário entra nos slides 11 e 12 (controle de acesso e antimalware no Linux) e você complementa a parte do Windows.

### 3. O que Falar (Roteiro Completo de Luiz para os 5 Slides)

#### Slide 08 — Introdução à Segurança e Tríade CIA
> *"Iniciando o estudo de Segurança, o Sistema Operacional é a **raiz de confiança**. Se o kernel for comprometido, nenhuma aplicação ou banco de dados acima dele está seguro.*
>
> *No diagrama da esquerda, mostramos a clássica **Tríade CIA**:*
> * **Confidencialidade:** Garantir que dados sensíveis sejam lidos apenas por processos e usuários autorizados;*
> * **Integridade:** Assegurar que o sistema e os dados não sofram alterações indevidas ou não autorizadas;*
> * **Disponibilidade:** Garantir que os recursos da CPU, memória e disco estejam sempre acessíveis.*
>
> *No Windows 11, aplicamos rigorosamente o **Princípio do Menor Privilégio de Saltzer & Schroeder**: mesmo que o usuário seja Administrador, ele roda por padrão com um Token de usuário padrão. Privilégios elevados só são ativados pontualmente mediante confirmação do **UAC (User Account Control)**."*

#### Slide 09 — Ameaças e Superfície de Ataque
> *"No Slide 09, mapeamos a **Cadeia de Ataque (Kill Chain)** nos quatro passos universais: Acesso Inicial → Execução → Escalada de Privilégios → Persistência.*
>
> *No ecossistema Windows 11, por ser o sistema mais utilizado no mundo em endpoints corporativos, a superfície de ataque concentra:*
> 1. *Ataques de **Ransomware**, que tentam apagar as cópias de sombra de volume (`vssadmin delete shadows`) para forçar o pagamento de resgate;*
> 2. *Técnicas **Living-off-the-Land (LotL)**, onde o atacante não baixa vírus: ele abusa de ferramentas nativas e assinadas da Microsoft, como PowerShell, WMI e `certutil`, executando código malicioso puramente na memória (ataques fileless);*
> 3. *Ataques de **BYOVD (Bring Your Own Vulnerable Driver)**, onde invasores usam drivers antigos e vulneráveis — porém assinados digitalmente — para obter acesso de leitura e escrita direto no Ring 0."*

#### Slide 10 — Criptografia Aplicada e Proteção em Repouso
> *"No Slide 10, analisamos como a criptografia mitiga o roubo de dados em repouso.*
>
> *No diagrama, apresentamos a **Hierarquia de Chaves do Disco**:*
> * *O chip físico **TPM 2.0** valida os registradores PCR (Platform Configuration Registers) para atestar que o boot não foi adulterado;*
> * *Ele deslacra a **VMK (Volume Master Key)**;*
> * *A VMK alimenta o motor de cifra **XTS-AES com chaves de 128 ou 256 bits**, acelerado diretamente por instruções de silício da CPU (**Intel AES-NI**).*
>
> *No Windows 11 Pro, essa proteção atua em dois níveis:*
> * **BitLocker:** Criptografia de volume inteiro (Full Disk Encryption), que protege os arquivos, o swap e o próprio sistema operacional caso o notebook seja roubado ou o SSD conectado em outra máquina;*
> * **EFS (Encrypting File System):** Criptografia transparente no nível de arquivos e pastas no NTFS, utilizando pares de chaves assimétricas RSA do usuário;*
> * *E os segredos de senhas do sistema (DPAPI e processo LSASS) ficam isolados pelo **Credential Guard** dentro do enclave do hipervisor VBS."*

#### Slide 11 — Autenticação e Controle de Acesso
> *(Mário explica o diagrama de decisão do kernel MAC/DAC e você complementa com o Windows):*
> *"No Windows 11, o subsistema de autenticação é o **LSASS**, que valida credenciais locais ou corporativas via Kerberos e Windows Hello, gerando um **Access Token** para a sessão do usuário.*
>
> *O componente do kernel que atua como sentinela é o **SRM (Security Reference Monitor)**. Toda vez que um processo tenta abrir um arquivo ou objeto com `CreateFile()`, o SRM compara os SIDs do Token com as listas **DACL (Discretionary Access Control List)** do objeto.*
>
> *Além disso, o Windows aplica o **MIC (Mandatory Integrity Control)**: processos são classificados em níveis de integridade (Untrusted, Low, Medium, High e System). Um processo rodando em integridade Low (como o navegador Edge) não tem permissão para alterar arquivos de um processo de integridade Medium, mesmo que ambos pertençam ao mesmo usuário!"*

#### Slide 12 — Ferramentas Nativas Antimalware e Defesa
> *"E fechando a segurança no Slide 12, temos o modelo de **Defesa em Profundidade**: cada camada barra o que passou pela anterior.*
>
> *O Windows 11 Pro adota uma postura proativa e integrada:*
> 1. *Na camada de execução, o **AMSI (Antimalware Scan Interface)** intercepta scripts em PowerShell ou VBScript na memória após serem desofuscados, antes da execução;*
> 2. *No kernel, a tecnologia **HVCI (Integridade de Código Protegida por Hipervisor)** garante que nenhuma página de memória de kernel seja simultaneamente gravável e executável ($W \oplus X$ restrito);*
> 3. *E contra Ransomware, o Windows disponibiliza o **Acesso Controlado a Pastas (Controlled Folder Access)**, que impede qualquer executável desconhecido de alterar pastas como Documentos e Imagens."*

### 4. O que Mostrar na Planilha
* **Arquivo:** `modelo_estudo_caso_seguranca_preenchido.xlsx`
* **Onde focar:**
  * **Linha 1 ("Introdução a Segurança"):** Conceito de Zero Trust por hardware e Tríade CIA.
  * **Linha 2 ("Principais Ameaças"):** Vetores de Ransomware, Pass-the-Hash e BYOVD na coluna B.
  * **Linha 3 ("Técnicas de Criptografia"):** XTS-AES, BitLocker, EFS e DPAPI.
  * **Linha 4 ("Autenticação e Controle de Acesso"):** LSASS, SRM, Tokens, DACL e níveis MIC.
  * **Linha 5 ("Ferramentas Antimalware"):** Minifiltro `WdFilter.sys`, AMSI, HVCI e Exploit Guard.
  * **Coluna de Comandos (Coluna C):**
    * `manage-bde -status C:` (status do BitLocker e método de criptografia).
    * `Get-MpComputerStatus` (status de proteção em tempo real e assinaturas do Defender).
    * `whoami /all` (exibe SIDs, grupos e privilégios do token atual).
    * `icacls "C:\Caminho"` (inspeciona as listas DACL de arquivos).

### 5. Perguntas Prováveis da Banca & Resposta Cirúrgica
* **Pergunta do Prof. Douglas:** *"O que é o AMSI e por que um antivírus tradicional que só olha arquivos em disco não consegue deter ataques fileless em PowerShell?"*
  * **Sua Resposta:** *"Professor, atacantes modernos usam técnicas de ofuscação (como encodamento em Base64, concatenação de strings e reflexão) para que o script malicioso pareça inofensivo no disco. O **AMSI** é uma interface interna do Windows que se acopla aos interpretadores (PowerShell, VBScript, .NET). Ele aguarda o código ser desofuscado na memória RAM imediatamente antes da chamada de execução, e envia o buffer decifrado para o Defender analisar. Isso neutraliza o ataque fileless na raiz."*

---

## Síntese de Comandos Práticos (Slide 13)

Se o professor pedir uma demonstração ou pergunta rápida sobre ferramentas de terminal:

| Escopo | Comando Windows 11 (PowerShell / CMD) | O que faz / O que explicar |
| :--- | :--- | :--- |
| **Kernel / Boot** | `Confirm-SecureBootUEFI` | Confirma integridade e Secure Boot via UEFI. |
| **Processos** | `Get-Process \| Sort CPU -Desc \| Select -First 5` | Lista processos de maior consumo e PID. |
| **Memória** | `Get-Counter '\Memory\Pages/sec'` | Mede a taxa de faltas de página (Page Faults) por segundo. |
| **Arquivos** | `fsutil fsinfo ntfsinfo C:` | Inspeciona tamanho de clusters e setor da MFT do NTFS. |
| **Entrada e Saída**| `Get-PnpDevice -Status OK` | Lista todos os periféricos Plug-and-Play operacionais. |
| **Criptografia** | `manage-bde -status C:` | Verifica selagem de chaves TPM e cifra XTS-AES do volume. |
| **Controle Acesso** | `whoami /all` | Detalha Token, SIDs de usuário e privilégios ativos. |
| **Defesa Nativa** | `Get-MpComputerStatus` | Valida proteção em tempo real, nuvem e versão do antimalware. |

---

## 3 Conselhos Finais para Garantir a Nota Máxima

1. **Domínio Visual (Não leia o slide):** Olhe para o professor e aponte para o diagrama ou para a tabela do slide. O slide contém termos-chave de 2 a 3 palavras justamente para provar que você sabe a explicação completa e não está lendo texto corrido.
2. **Navegação Imediata no PPTX:** Tenha a apresentação aberta em tela cheia. Quando o professor disser: *"Apresentem o estudo de Memória"*, aperte `5` e depois `Enter` no teclado. O PowerPoint vai direto para o Slide 05 em 1 segundo.
3. **Use a Planilha como Evidência:** Se o professor demonstrar qualquer dúvida ou pedir aprofundamento, diga com segurança: *"Professor, detalhamos exatamente esse ponto na nossa planilha comparativa entregue, se o senhor quiser podemos abrir na linha correspondente para conferir os parâmetros exatos."* Isso demonstra preparação de nível sênior.

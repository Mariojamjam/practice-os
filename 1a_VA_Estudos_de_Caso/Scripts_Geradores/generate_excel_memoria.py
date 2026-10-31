import xlsxwriter
import os

def create_memory_comparative_spreadsheet(filepath):
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet("Estudo de Caso - Memória")
    
    # Page setup
    worksheet.set_landscape()
    worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
    
    # Formats
    header_fmt = workbook.add_format({
        'bold': True,
        'bg_color': '#1B365D', # Deep Navy Blue
        'font_color': '#FFFFFF',
        'font_name': 'Segoe UI',
        'font_size': 11,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True,
        'border': 1,
        'border_color': '#0B1E36'
    })
    
    topic_fmt = workbook.add_format({
        'bold': True,
        'bg_color': '#E8EEF5', # Soft Blue Gray
        'font_color': '#0F2537',
        'font_name': 'Segoe UI',
        'font_size': 10,
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1,
        'border_color': '#BDC3C7'
    })
    
    content_fmt = workbook.add_format({
        'font_name': 'Segoe UI',
        'font_size': 9.5,
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1,
        'border_color': '#BDC3C7'
    })
    
    cmd_fmt = workbook.add_format({
        'font_name': 'Consolas',
        'font_size': 9,
        'bg_color': '#FDFEFE',
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1,
        'border_color': '#BDC3C7'
    })

    title_fmt = workbook.add_format({
        'bold': True,
        'font_name': 'Segoe UI',
        'font_size': 14,
        'font_color': '#1B365D',
        'align': 'center',
        'valign': 'vcenter'
    })

    subtitle_fmt = workbook.add_format({
        'italic': True,
        'font_name': 'Segoe UI',
        'font_size': 10,
        'font_color': '#555555',
        'align': 'center',
        'valign': 'vcenter'
    })

    # Title rows
    worksheet.merge_range('A1:E1', 'ESTUDO DE CASO: GERENCIAMENTO DE MEMÓRIA EM SISTEMAS OPERACIONAIS', title_fmt)
    worksheet.merge_range('A2:E2', 'Disciplina: Sistemas Operacionais | Prof. Dr. Douglas Véras | Alunos: Luiz Maranhão & Mário Jorge (UFRPE)', subtitle_fmt)
    worksheet.set_row(0, 24)
    worksheet.set_row(1, 18)

    headers = [
        "Sistema Operacional /\nComparativo",
        "Windows 11 Pro (23H2 / 24H2)",
        "Windows 11 Pro – comandos (linha de comando ou especificar função na GUI)\n*listagem e breve descrição de comandos relevantes para visualização ou gerenciamento",
        "Ubuntu 24.04 LTS (Kernel Linux 6.8)",
        "Ubuntu 24.04 LTS – comandos (linha de comando ou especificar função na GUI)\n*listagem e breve descrição de comandos relevantes para visualização ou gerenciamento"
    ]

    worksheet.set_row(2, 45)
    for col_idx, h in enumerate(headers):
        worksheet.write(2, col_idx, h, header_fmt)

    data = [
        (
            "O SO utiliza paginação? Como é feito? (ex.: dados de uma página, tamanho da página, estrutura de dados, etc.)",
            # Windows 11
            "• Sim, o Windows 11 utiliza paginação multinível com suporte à arquitetura x86-64 (paginação de 4 níveis por padrão, e 5 níveis - PML5 em processadores que suportam LA57).\n"
            "• Tamanho de Página: Página padrão de 4 KB (Small Page). Suporta 'Large Pages' de 2 MB (habilitável via flag MEM_LARGE_PAGES na VirtualAlloc, requer privilégio SeLockMemoryPrivilege) e 'Huge Pages' de 1 GB para hipervisor e drivers.\n"
            "• Estruturas de Dados do Kernel:\n"
            "  - Tabela de Páginas Multinível: PML4 -> PDPT (Page Directory Pointer Table) -> PD (Page Directory) -> PT (Page Table) -> PTE (Page Table Entry de 64 bits).\n"
            "  - PTE (Hardware & Software): Contém bits Valid, Dirty, Accessed, Write, User/Supervisor, NX (No-Execute para prevenção contra exploits/DEP) e PFN (Page Frame Number).\n"
            "  - PFN Database (nt!_MMPFN): Vetor indexado no kernel que rastreia o estado físico de cada moldura de página na RAM (Active/Valid, Standby, Modified, ModifiedNoWrite, Free, Zeroed, Bad, Transition).\n"
            "  - Working Set List (nt!_MMWSL): Rastreia o conjunto de páginas residentes na RAM de cada processo.",
            
            # Windows 11 - Comandos
            "• CLI (PowerShell):\n"
            "  Get-Process | Select-Object Name, Id, WorkingSet64, VirtualMemorySize64 | Sort-Object WorkingSet64 -Descending\n"
            "  (Lista os processos ordenados pelo conjunto de trabalho de páginas na RAM).\n\n"
            "• CLI (Sysinternals):\n"
            "  rammap.exe / vmmap.exe\n"
            "  (Ferramentas avançadas que mapeiam as listas de páginas PFN, Standby, Modified, Heap, e memória comprometida em detalhe).\n\n"
            "• GUI (Monitor de Recursos - resmon.exe):\n"
            "  Guia 'Memória': Exibe o gráfico de barras com Memória Reservada para Hardware, Em Uso, Modificada, Em Espera (Standby) e Livre; tabela detalha Working Set, Privada e Compartilhada por processo.\n\n"
            "• GUI (Gerenciador de Tarefas):\n"
            "  Guia 'Desempenho' > 'Memória': Mostra pool paginável e não paginável, memória confirmada (Commit Charge) e páginas em cache.",

            # Ubuntu 24.04
            "• Sim, o Ubuntu 24.04 (Kernel 6.8) utiliza paginação multinível x86-64 em árvore com 4 níveis (4-level paging: PGD -> P4D -> PUD -> PMD -> PTE) e suporte compilado a 5 níveis (5-level paging / PML5 para espaços de endereçamento virtual de até 128 PB).\n"
            "• Tamanho de Página: Página base de 4 KB. Suporte nativo e automático a Transparent Huge Pages (THP) de 2 MB (reduz faltas no TLB agrupando 512 páginas de 4 KB contíguas) e HugeTLB de 1 GB (alocada estaticamente para bancos de dados e VMs).\n"
            "• Estruturas de Dados do Kernel:\n"
            "  - struct page / struct folio: Cada moldura física de 4 KB na RAM é representada pela 'struct page' (ou abstração moderna 'struct folio' no Kernel 6.8), rastreando contagem de referências (_refcount), flags (PG_locked, PG_active, PG_dirty, PG_lru) e mapeamento (_mapcount).\n"
            "  - mm_struct: Estrutura que descreve o espaço de memória de cada processo (aponta para pgd_t *pgd, endereço carregado no registrador CR3 na troca de contexto).\n"
            "  - vm_area_struct (VMA): Árvore Rubro-Negra (red-black tree) e maple tree que indexa intervalos virtuais contíguos do processo com permissões (read, write, exec, shared).",

            # Ubuntu 24.04 - Comandos
            "• CLI:\n"
            "  getconf PAGESIZE\n"
            "  (Retorna o tamanho da página de memória do sistema, padrão 4096 bytes).\n\n"
            "• CLI:\n"
            "  pmap -x <PID>  # ou  cat /proc/<PID>/smaps\n"
            "  (Mapeia todas as páginas e faixas de endereçamento virtual do processo, mostrando RSS, PSS e tamanho de páginas).\n\n"
            "• CLI:\n"
            "  cat /sys/kernel/mm/transparent_hugepage/enabled\n"
            "  (Verifica o status das Transparent Huge Pages - always, madvise ou never).\n\n"
            "• CLI:\n"
            "  grep -i hugepages /proc/meminfo\n"
            "  (Mostra HugePages_Total, HugePages_Free, Hugepagesize: 2048 kB).\n\n"
            "• GUI (Monitor do Sistema GNOME - gnome-system-monitor):\n"
            "  Aba 'Processos', clique direito no processo > 'Mapas de Memória' (Memory Maps): Exibe cada segmento VMA mapeado na memória virtual com seus endereços e permissões."
        ),
        (
            "O SO utiliza segmentação? Como é feito? (ex.: dados de um segmento, tipos de segmento, estrutura de dados, etc.)",
            # Windows 11
            "• No Windows 11 para x86-64, a segmentação por hardware é essencialmente desativada / colocada em modelo plano ('Flat Memory Model'), em conformidade com as especificações da arquitetura AMD64/Intel 64 (Long Mode).\n"
            "• Como é feito:\n"
            "  - Os seletores de segmento tradicionais (CS, DS, ES, SS) possuem base fixa em 0 e limite desconsiderado pelo hardware (cobre todos os 64 bits de endereçamento linear).\n"
            "  - O registrador de segmento GS é a grande exceção funcional: ele é utilizado pelo Windows como ponteiro base para estruturas de dados dependentes do thread ou do núcleo da CPU.\n"
            "    * Em Modo Kernel (Ring 0): O registrador GS aponta para a estrutura KPCR (Kernel Processor Control Region), que contém o contexto do processador atual, ponteiro da thread em execução (CurrentThread) e fila DPC.\n"
            "    * Em Modo Usuário (Ring 3): O registrador GS aponta para o TEB (Thread Environment Block), acessível via GS:[0x30], que por sua vez aponta para o PEB (Process Environment Block).\n"
            "  - A GDT (Global Descriptor Table) é mantida com descritores mínimos para Ring 0 e Ring 3, e a LDT (Local Descriptor Table) é praticamente inexistente/não utilizada.",

            # Windows 11 - Comandos
            "• CLI (WinDbg / LiveKD):\n"
            "  r gs, r cs, r ss; !pcr; !teb\n"
            "  (No depurador WinDbg, inspeciona os registradores de segmento e exibe os ponteiros para KPCR em Ring 0 e TEB em Ring 3).\n\n"
            "• CLI (PowerShell):\n"
            "  Get-Process | Format-Table Id, Name, BasePriority, HandleCount\n"
            "  (Embora não exponha seletores de segmento diretamente, obtém dados populados a partir do TEB/PEB e EPROCESS).\n\n"
            "• GUI (Process Explorer - Sysinternals):\n"
            "  Propriedades do Processo > Guia 'Environment' ou 'Threads': Ao inspecionar uma thread e clicar em 'Stack', visualiza-se o endereço base da stack derivado do TEB apontado pelo registrador GS.",

            # Ubuntu 24.04
            "• No Ubuntu 24.04 (Linux x86-64), a segmentação também é implementada sob o 'Flat Memory Model' (modelo de memória plana). O processador x86-64 ignora a base e os limites para CS, DS, ES e SS em modo de 64 bits.\n"
            "• Como é feito:\n"
            "  - GDT Mínima: O kernel Linux inicializa uma GDT (Global Descriptor Table) pequena por CPU, contendo seletores essenciais: __KERNEL_CS (0x10), __KERNEL_DS (0x18), __USER_CS (0x33), __USER_DS (0x2b) e a TSS (Task State Segment) para transição de privilégio e pilhas de interrupção (IST).\n"
            "  - Uso de FS e GS:\n"
            "    * Registrador FS: Utilizado pelo espaço de usuário (glibc / NPTL) para endereçar o Thread-Local Storage (TLS). Instruções leem e escrevem variáveis locais de thread via %fs:offset.\n"
            "    * Registrador GS: Utilizado pelo Kernel Linux para acessar variáveis 'per-CPU' (como o ponteiro current para a task_struct da CPU atual, pilhas de interrupção e contadores estatísticos). O comando assembly 'swapgs' troca a base de GS entre Ring 3 e Ring 0 na entrada de syscalls.\n"
            "  - LDT: Não utilizada por padrão para processos nativos de 64 bits, mas suportada para emulação (ex.: Wine / DOSBox via chamada modify_ldt()).",

            # Ubuntu 24.04 - Comandos
            "• CLI:\n"
            "  dmesg | grep -i -E 'gdt|segments|fsgsbase'\n"
            "  (Exibe suporte do kernel e da CPU à instrução FSGSBASE, permitindo manipulação direta e rápida dos registradores FS/GS sem syscall lenta).\n\n"
            "• CLI (GDB):\n"
            "  gdb -p <PID> -batch -ex 'info registers fs gs cs ss'\n"
            "  (Examina o conteúdo dos registradores de segmento do processo especificado).\n\n"
            "• CLI (Kernel Config):\n"
            "  grep -E 'CONFIG_X86_5LEVEL|CONFIG_MODIFY_LDT_SYSCALL' /boot/config-$(uname -r)\n"
            "  (Verifica as diretivas de compilação do kernel para paginação e chamadas de segmento LDT).\n\n"
            "• GUI (Monitor do Sistema GNOME):\n"
            "  Aba de processos, detalhes de thread e stack mostram que os endereços lineares operam em modelo contínuo plano de 64 bits."
        ),
        (
            "O SO faz uso Swap? Como é feito? (ex.: estrutura de dados, gerenciamento, etc.)",
            # Windows 11
            "• Sim, o Windows 11 faz uso extensivo de arquivo de paginação (Paging File / Swap), além de um subsistema inovador de Compactação de Memória na RAM.\n"
            "• Como é feito e Estruturas:\n"
            "  - Arquivo Paging: pagefile.sys (armazenado na raiz de C: ou outras unidades). Existe também o swapfile.sys (usado para suspender/hibernar aplicativos empacotados UWP/Store em segundo plano).\n"
            "  - Compactação de Memória (Memory Compression): Antes de descarregar uma página fria para o disco rígido/SSD, o Gerenciador de Memória do Windows compacta a página em um 'Store' na própria memória RAM (processo 'System' ou 'Memory Compression'), reduzindo leituras/gravações lentas de disco.\n"
            "  - Estrutura MMPAGING_FILE: Representa cada arquivo de paginação aberto, mantendo bitmaps (RtlBitmap) de blocos livres no arquivo de disco.\n"
            "  - Modified Page Writer: Thread em segundo plano que reúne páginas sujas da Modified List e realiza E/S em lote (*clustering*) para gravação no pagefile.sys.\n"
            "  - Gerenciamento Automático: O Windows gerencia dinamicamente o tamanho do pagefile de acordo com a carga de memória comprometida (Commit Limit).",

            # Windows 11 - Comandos
            "• CLI (PowerShell):\n"
            "  Get-CimInstance Win32_PageFileUsage | Select-Object Name, AllocatedBaseSize, CurrentUsage, PeakUsage\n"
            "  (Exibe o arquivo de swap configurado, tamanho alocado, uso atual e pico de utilização em MB).\n\n"
            "• CLI (PowerShell - Compactação):\n"
            "  Get-Process -Name 'System' | Select-Object Name, WS, PrivateMemorySize\n"
            "  (Permite avaliar o consumo de memória do processo System, responsável pelo pool de memória compactada).\n\n"
            "• GUI (Configurações Avançadas do Sistema):\n"
            "  sysdm.cpl > Guia 'Avançado' > 'Desempenho' (Configurações) > Guia 'Avançado' > 'Memória Virtual' (Alterar):\n"
            "  Permite configurar o tamanho inicial e máximo de pagefile.sys ou habilitar o gerenciamento automático pelo Windows.\n\n"
            "• GUI (Gerenciador de Tarefas):\n"
            "  Desempenho > Memória: Exibe o campo 'Confirmado' (Commit: RAM + Paging File) e 'Em uso (Compactada)' indicando quanto foi salvo via compressão.",

            # Ubuntu 24.04
            "• Sim, o Ubuntu 24.04 faz uso de Swap por meio de arquivos de swap (/swapfile) ou partições dedicadas (tipo 82 no MBR / swap GUID no GPT), integrando também tecnologias de swap comprimido em RAM (zswap / zRAM).\n"
            "• Como é feito e Estruturas:\n"
            "  - /swapfile: Padrão nas instalações modernas do Ubuntu (criado geralmente com 2 a 4 GB no diretório raiz).\n"
            "  - zRAM & zswap: zRAM cria dispositivos de bloco virtuais na RAM comprimidos via algoritmos como zstd ou lz4; zswap intercepta páginas prestes a ir para o disco e as compacta numa pool na RAM.\n"
            "  - swap_info_struct: O kernel mantém um array dessas estruturas para cada dispositivo de swap ativo, controlando prioridade, setores livres e flags.\n"
            "  - Parâmetro vm.swappiness: Controla o balanço entre esvaziar páginas anônimas para o swap vs. descartar páginas de cache de arquivo (Page Cache). Padrão típico: 60 (em desktops) ou menor em servidores.\n"
            "  - OOM Killer (Out-of-Memory Killer): Quando a RAM e o Swap esgotam simultaneamente, o kernel calcula um 'badness score' (/proc/<PID>/oom_score) e encerra o processo de maior consumo.",

            # Ubuntu 24.04 - Comandos
            "• CLI:\n"
            "  swapon --show  # ou  cat /proc/swaps\n"
            "  (Lista os arquivos/partições de swap ativos, tipos, tamanho total e prioridade).\n\n"
            "• CLI:\n"
            "  free -h\n"
            "  (Exibe rapidamente a memória total, usada, livre, buffers/cache e swap total/usado em unidades legíveis por humanos).\n\n"
            "• CLI (Swappiness):\n"
            "  cat /proc/sys/vm/swappiness  # ou  sysctl vm.swappiness\n"
            "  (Lê o índice de propensão ao swap; pode ser alterado com sudo sysctl vm.swappiness=10).\n\n"
            "• CLI (Criar/Modificar Swap):\n"
            "  sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile\n"
            "  (Sequência de comandos clássica para criar e ativar um novo arquivo de swap).\n\n"
            "• GUI (Monitor do Sistema GNOME):\n"
            "  Aba 'Recursos': Apresenta gráficos em tempo real de histórico de uso de memória física e histórico de uso do espaço Swap."
        ),
        (
            "O SO utiliza partições fixas ou variáveis? Quais técnicas/estruturas de alocação são utilizadas (ex.: bit map, lista encadeada, etc.)?",
            # Windows 11
            "• O Windows 11 utiliza PARTIÇÕES VARIÁVEIS (dinâmicas) para a alocação de memória aos processos e para as regiões internas de Heap e Pools do kernel.\n"
            "  (Nota teórica: no nível mais baixo de hardware/frames, as páginas possuem tamanho fixo de 4 KB, mas os espaços de memória e alocações de processos variam sob demanda).\n"
            "• Técnicas e Estruturas de Alocação:\n"
            "  - Low Fragmentation Heap (LFH) & Segment Heap: O heap moderno do Windows utiliza uma arquitetura de múltiplos níveis. O LFH divide a memória em buckets predefinidos por faixas de tamanho pré-categorizadas para alocações de até 16 KB, eliminando fragmentação externa.\n"
            "  - Bitmaps (RtlBitmap): Utilizados para indexação de slots livres dentro de sub-segmentos de páginas e para controle dos blocos livres no arquivo de paginação (MMPAGING_FILE).\n"
            "  - Listas Duplamente Encadeadas (LIST_ENTRY): Rastreiam blocos livres e ocupados de heap no NT Heap tradicional e os descritores de blocos nos pools do kernel.\n"
            "  - Pools do Kernel (Paged e Non-Paged Pool): O Paged Pool aloca memória de tamanho variável que pode ser enviada ao disco; o Non-Paged Pool garante que a memória física nunca seja paginada (para rotinas de interrupção ISR/DPC).",

            # Windows 11 - Comandos
            "• CLI (PowerShell / WMI):\n"
            "  Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory, TotalVirtualMemorySize, FreeVirtualMemory\n"
            "  (Verifica o particionamento dinâmico global da memória em KB).\n\n"
            "• CLI (Sysinternals):\n"
            "  coreinfo.exe -m  # Exibe topologia NUMA e nós de alocação física de memória.\n"
            "  vmmap.exe <PID>  # Detalha todas as regiões variáveis alocadas (Heap, Stack, Mapeadas).\n\n"
            "• GUI (Gerenciador de Tarefas):\n"
            "  Aba 'Desempenho' > 'Memória': Exibe os valores dinâmicos de 'Pool paginável' e 'Pool não paginável' alocados pelo kernel do Windows.\n\n"
            "• GUI (Monitor de Desempenho - perfmon.msc):\n"
            "  Contadores 'Memory\\Pool Paged Bytes' e 'Memory\\Pool Nonpaged Bytes' mostram a flutuação dinâmica das partições alocadas.",

            # Ubuntu 24.04
            "• O Ubuntu 24.04 (Kernel Linux 6.8) utiliza PARTIÇÕES VARIÁVEIS para alocação a processos e estruturas do sistema operacional, suportado por paginação subjacente.\n"
            "• Técnicas e Estruturas de Alocação:\n"
            "  - Buddy System (Sistema de Parceiros Binários): Estrutura mestre do kernel para alocação de páginas físicas. Agrupa blocos de páginas contíguas em ordens de potências de 2 ($2^0$ a $2^{10}$, ou seja, de 4 KB até 4 MB). Utiliza listas encadeadas duplas circulares (struct list_head) e bitmaps para verificar o bit do 'buddy' correspondente.\n"
            "  - Alocador SLUB (evolução do SLAB): Responsável por alocar objetos de tamanho fixo e pequeno dentro do kernel (ex.: task_struct, mm_struct, descritores de arquivos). Utiliza uma 'freelist' encadeada embutida dentro dos próprios objetos livres e um bitmap por página slab, atingindo alocação e liberação em tempo $O(1)$ sem fragmentação externa.\n"
            "  - User-space (glibc ptmalloc3): Organiza o Heap dos programas em blocos variáveis (*chunks*) com cabeçalho de controle, gerenciados por listas encadeadas circulares divididas em categorias (*bins*): Fastbins (LIFO simples), Smallbins (FIFO) e Unsorted Bins.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Buddy System):\n"
            "  cat /proc/buddyinfo\n"
            "  (Exibe a quantidade de blocos de memória contíguos livres por ordem $2^0$ a $2^{10}$ em cada nó NUMA e zona de memória).\n\n"
            "• CLI (Alocador de Objetos SLUB):\n"
            "  cat /proc/slabinfo  # ou ferramenta interativa: sudo slabtop -s c\n"
            "  (Lista todos os caches SLUB do kernel, objetos ativos, tamanho de cada objeto e uso total de memória).\n\n"
            "• CLI (Informações de Memória Geral):\n"
            "  cat /proc/meminfo | grep -E 'Slab|SReclaimable|SUnreclaim'\n"
            "  (Mostra o total de memória em partições SLUB, separando em recuperável e não recuperável).\n\n"
            "• GUI (Monitor do Sistema GNOME):\n"
            "  Aba 'Processos': Exibe a alocação de memória residente (RSS) e compartilhada variando dinamicamente em tempo real conforme as necessidades de cada aplicação."
        ),
        (
            "Quais algoritmos de alocação são utilizados (ex.: first-fit, best-fit, etc.)?",
            # Windows 11
            "• O Windows 11 adota algoritmos híbridos de alocação adaptados para cada subsistema e granularidade:\n"
            "• No Espaço de Usuário (Heaps de Aplicação):\n"
            "  - Segregated Free Lists (Listas Livres Segregadas): Para alocações de tamanho até 16 KB no LFH (Low Fragmentation Heap), o alocador pré-divide a memória em 'bins' de tamanhos fixos. Quando uma aplicação solicita N bytes, o algoritmo indexa diretamente a lista segregada correspondente em tempo constante $O(1)$, evitando varreduras lineares.\n"
            "  - Best-Fit / First-Fit em Listas Encadeadas: No NT Heap legado para alocações médias, e no Segment Heap para blocos maiores, o Windows emprega busca por Best-Fit ou First-Fit dentro de blocos livres para minimizar o desperdício de memória residual.\n"
            "  - VirtualAlloc Direta: Para alocações muito grandes (> 512 KB), o algoritmo bypassa o heap e chama diretamente a MMU para alocar páginas inteiras arredondadas para cima.\n"
            "• No Espaço de Kernel:\n"
            "  - Lookaside Lists: Listas LIFO rápidas para alocações frequentes de estruturas idênticas.\n"
            "  - Free Lists indexadas com coalescência imediata: Ao liberar um bloco adjacente a outro livre, o Windows funde os blocos (*merging*) para mitigar a fragmentação externa.",

            # Windows 11 - Comandos
            "• CLI (WinDbg):\n"
            "  !heap -s  # Exibe o resumo de todos os heaps do processo, indicando se utilizam LFH ou Segment Heap.\n"
            "  !heap -p -a <Endereço>  # Inspeciona um bloco específico de alocação de heap.\n\n"
            "• CLI (PowerShell):\n"
            "  Get-Process | Where-Object { $_.NonpagedSystemMemorySize64 -gt 10MB } | Format-Table Name, NonpagedSystemMemorySize64\n"
            "  (Monitora processos que solicitam alocações expressivas no pool não-paginável do kernel).\n\n"
            "• GUI (Process Hacker / System Informer):\n"
            "  Propriedades do Processo > Guia 'Heaps': Permite visualizar todos os heaps criados pelo processo, número de blocos alocados, blocos livres e taxa de fragmentação.\n\n"
            "• GUI (Monitor de Desempenho - perfmon.msc):\n"
            "  Objeto de contador 'Heap Locks' e 'Committed Bytes' para rastreamento de alocação dinâmica.",

            # Ubuntu 24.04
            "• O Ubuntu 24.04 (Linux 6.8) emprega diferentes algoritmos dependendo se a alocação ocorre no núcleo ou no espaço de usuário:\n"
            "• No Espaço de Kernel:\n"
            "  - Algoritmo do Buddy System (Sistema de Parceiros Binários): Aloca memória em blocos de tamanho $2^k \\times 4\\text{ KB}$. Se o bloco da ordem desejada não estiver livre, ele divide o bloco de ordem imediatamente superior em dois blocos 'parceiros' (buddies) até obter o tamanho exato. Na liberação, verifica se o buddy está livre por meio de uma operação bitwise XOR no endereço e os funde imediatamente (tempo $O(1)$).\n"
            "  - SLUB Allocator: Utiliza alocação exata para caches de tipos fixos (*object caches*), sem busca linear.\n"
            "• No Espaço de Usuário (glibc ptmalloc3):\n"
            "  - Exact-Fit: Utilizado para alocações pequenas através dos Fastbins (listas LIFO sem fusão imediata).\n"
            "  - Best-Fit Aproximado: Utilizado nos Largebins; as listas são organizadas por ordem decrescente de tamanho, e o alocador busca o menor chunk que satisfaça a requisição gerando a menor sobra possível.\n"
            "  - First-Fit: Utilizado no Unsorted Bin para reuso rápido de blocos liberados recentemente.",

            # Ubuntu 24.04 - Comandos
            "• CLI:\n"
            "  cat /proc/buddyinfo\n"
            "  (Permite auditar a disponibilidade de blocos para o algoritmo do Buddy System em tempo real).\n\n"
            "• CLI (Estatísticas do Alocador):\n"
            "  vmstat -m  # Exibe o uso dos caches SLAB/SLUB com tamanho de bloco e número de alocações.\n\n"
            "• CLI (Depuração de Heap com Ltrace/Valgrind):\n"
            "  ltrace -e malloc+free ls  # ou  valgrind --tool=massif ls\n"
            "  (Rastreia as chamadas da biblioteca glibc que acionam os algoritmos de alocação de memória no heap do processo).\n\n"
            "• GUI (Monitor do Sistema GNOME):\n"
            "  Na guia de processos e recursos, o monitoramento contínuo da memória privada demonstra o impacto dos algoritmos de alocação e liberação sem vazamento de memória (memory leaks)."
        ),
        (
            "Quais algoritmos de substituição de páginas são utilizados (ex.: LRU, FIFO, etc.)?",
            # Windows 11
            "• O Windows 11 utiliza uma política baseada em Working Set Trimming local combinada com o algoritmo de Substituição Global por Listas de Transição de Páginas (uma sofisticação do LRU com Envelhecimento / Aging):\n"
            "• Como funciona:\n"
            "  - Working Set Trimming: Cada processo possui cotas dinâmicas de páginas residentes (Working Set Mínimo e Máximo). Quando a demanda física global aumenta, o 'Balance Set Manager' inspeciona as páginas dos processos.\n"
            "  - Bits de Acesso e Aging: O processador marca o bit 'Accessed' na PTE ao ler/escrever na página. O Windows limpa periodicamente esse bit para estimar quais páginas foram menos referenciadas recentemente (Aproximação de LRU).\n"
            "  - Standby Page List (8 Níveis de Prioridade): Páginas removidas do Working Set mas que ainda não foram reutilizadas são enviadas para a Standby List, ranqueadas de 0 (baixa prioridade) a 7 (alta prioridade, usada para código prioritário do sistema). Se o processo requisitar a página novamente antes de sua reciclagem, ocorre um 'Soft Page Fault' (resolvido na própria RAM sem I/O de disco).\n"
            "  - SuperFetch / SysMain: Serviço preditivo que pré-carrega na Standby List as páginas mais utilizadas com base no histórico de hábitos do usuário.",

            # Windows 11 - Comandos
            "• CLI (PowerShell - Contadores de Desempenho):\n"
            "  Get-Counter '\\Memory\\Page Faults/sec', '\\Memory\\Page Reads/sec', '\\Memory\\Transition Faults/sec'\n"
            "  (Mede a taxa de faltas de página gerais, faltas que exigiram leitura em disco e faltas de transição resolvidas no Standby cache).\n\n"
            "• CLI / GUI (Sysinternals RAMMap):\n"
            "  Abra o RAMMap.exe > Guia 'Use Counts' e 'Priority Summary':\n"
            "  Exibe a Standby List discriminada por nível de prioridade (0 a 7), demonstrando graficamente a fila de substituição do algoritmo de aging.\n\n"
            "• GUI (Monitor de Desempenho - perfmon.msc):\n"
            "  Monitore '\\Memory\\Pages/sec' e '\\Memory\\Page Writes/sec' para observar a substituição ativa de páginas em cenários de pressão de memória.\n\n"
            "• GUI (Gerenciador de Tarefas):\n"
            "  Aba 'Desempenho' > 'Memória': A métrica 'Em cache' reflete o tamanho somado da Standby List e Modified List.",

            # Ubuntu 24.04
            "• O Ubuntu 24.04 (Kernel Linux 6.8) utiliza uma aproximação de LRU altamente sofisticada, destacando-se a transição para a moderna arquitetura MGLRU:\n"
            "• Como funciona:\n"
            "  - Algoritmo Clássico de Duas Listas (Active / Inactive Lists): Implementa uma aproximação de LRU baseada no Algoritmo de Relógio de Segunda Chance (Clock Algorithm). Novas páginas entram na Inactive List. Se forem referenciadas novamente (bit PG_referenced ativado), são promovidas para a Active List. Sob pressão de memória, o daemon 'kswapd' varre a Active List, despromove páginas sem reuso para a Inactive List e descarrega as mais antigas da Inactive List para o swap ou disco.\n"
            "  - MGLRU (Multi-Gen LRU) - Inovação do Kernel 6.8: Substitui o custo elevado da varredura de árvores de páginas por uma estrutura de múltiplas gerações temporais (geração mais nova até mais antiga). Utiliza histogramas de acessos em níveis de 'tiers' de páginas, reduzindo o uso de CPU para substituição de páginas em até 80% e mitigando engasgos sob alta carga de memória.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Verificar e Configurar MGLRU no Kernel 6.8):\n"
            "  cat /sys/kernel/mm/lru_gen/enabled\n"
            "  (Verifica se o Multi-Gen LRU está habilitado - ex.: 0x0007; pode ser ativado/desativado em tempo de execução via echo).\n\n"
            "• CLI (Visualizar Faltas de Página e Atividade do kswapd):\n"
            "  sar -B 1 5  # (Requer pacote sysstat, monitora page faults, pgpgin, pgpgout)\n"
            "  vmstat 1 5  # (Monitora colunas 'si' swap-in, 'so' swap-out e taxas de I/O de memória).\n\n"
            "• CLI (Estatísticas de Listas Ativas/Inativas):\n"
            "  grep -E 'Active|Inactive' /proc/meminfo\n"
            "  (Exibe Active(anon), Inactive(anon), Active(file) e Inactive(file), demonstrando o estado das listas do algoritmo de substituição).\n\n"
            "• GUI (Monitor do Sistema GNOME):\n"
            "  Aba 'Recursos': Permite monitorar a flutuação da memória de cache e o momento em que páginas são enviadas para a área de Swap."
        )
    ]

    # Column widths
    worksheet.set_column(0, 0, 24, topic_fmt)
    worksheet.set_column(1, 1, 38, content_fmt)
    worksheet.set_column(2, 2, 34, cmd_fmt)
    worksheet.set_column(3, 3, 38, content_fmt)
    worksheet.set_column(4, 4, 34, cmd_fmt)

    # Write data
    start_row = 3
    for i, row in enumerate(data):
        row_num = start_row + i
        worksheet.set_row(row_num, 210) # Enough height for rich formatted text
        worksheet.write(row_num, 0, row[0], topic_fmt)
        worksheet.write(row_num, 1, row[1], content_fmt)
        worksheet.write(row_num, 2, row[2], cmd_fmt)
        worksheet.write(row_num, 3, row[3], content_fmt)
        worksheet.write(row_num, 4, row[4], cmd_fmt)

    workbook.close()
    print(f"Spreadsheet generated successfully at: {filepath}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Planilhas")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "modelo_estudo_caso_memoria_preenchido.xlsx")
    create_memory_comparative_spreadsheet(out_file)

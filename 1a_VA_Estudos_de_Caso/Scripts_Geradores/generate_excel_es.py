import xlsxwriter
import os

def create_io_comparative_spreadsheet(filepath):
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet("Estudo de Caso - E-S")
    
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
    worksheet.merge_range('A1:E1', 'ESTUDO DE CASO: SUBSISTEMA DE ENTRADA E SAÍDA (E/S) EM SISTEMAS OPERACIONAIS', title_fmt)
    worksheet.merge_range('A2:E2', 'Disciplina: Sistemas Operacionais | Prof. Dr. Douglas Véras | Alunos: Luiz Maranhão & Mário Jorge (UFRPE)', subtitle_fmt)
    worksheet.set_row(0, 26)
    worksheet.set_row(1, 20)

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
        # Linha 1: Introdução a E/S
        (
            "Introdução a E/S dos SOs\n(Visão Geral, Arquitetura de Camadas e Abstração de Hardware)",
            # Windows 11
            "• Arquitetura do Subsistema de E/S do Windows 11:\n"
            "  - Modelo Modular Orientado a Pacotes: Baseado no E/S Manager (I/O Manager) no espaço do kernel (ntoskrnl.exe). Todo o fluxo de E/S é gerenciado por IRPs (I/O Request Packets), estruturas de dados dinâmicas passadas entre camadas de drivers.\n"
            "  - Abstração em Camadas de Drivers:\n"
            "    1. Filter Drivers: Antivírus, criptografia BitLocker, monitoramento de integridade.\n"
            "    2. Functional Device Drivers (FDO): Controlam a lógica de alto nível do dispositivo (ex.: sistema de arquivos NTFS/ReFS, class drivers).\n"
            "    3. Bus/Port Drivers & Storport: Gerenciam os barramentos de hardware (PCIe, USB, NVMe, SATA) e realizam interface com a HAL (Hardware Abstraction Layer).\n"
            "  - Abstração de Alto Nível: O Windows abstrai dispositivos como objetos no namespace de objetos (\\Device\\HarddiskVolumeX), expostos via links simbólicos (ex.: C:, COM1) acessados por APIs Win32 (CreateFile, ReadFile, DeviceIoControl).\n"
            "  - Suporte a E/S Assíncrona Nativa: I/O Completion Ports (IOCP) fornecem escalabilidade massiva para servidores e aplicações de alta concorrência.",
            
            # Windows 11 - Comandos
            "• CLI (PowerShell):\n"
            "  Get-PnpDevice -Class 'DiskDrive', 'SCSIAdapter'\n"
            "  (Lista os dispositivos de armazenamento Plug and Play e controladoras ativas).\n\n"
            "• CLI (Sysinternals):\n"
            "  procmon.exe (Process Monitor)\n"
            "  (Captura em tempo real chamadas de IRPs, CreateFile, ReadFile e WriteFile por processo).\n\n"
            "• CLI (DriverQuery):\n"
            "  driverquery /v /fo table\n"
            "  (Exibe todos os drivers de dispositivo do kernel em execução, tipo e modo de inicialização).\n\n"
            "• GUI (Gerenciador de Dispositivos - devmgmt.msc):\n"
            "  Permite inspecionar a árvore de dispositivos, barramentos, recursos de hardware (IRQs, portas de E/S, endereços de memória MMIO) e versões de drivers assinados.",

            # Ubuntu 24.04
            "• Arquitetura do Subsistema de E/S do Linux (Kernel 6.8):\n"
            "  - Filosofia Unix 'Tudo é Arquivo': Dispositivos são representados no sistema de arquivos sob o diretório /dev (nós especiais de caracteres e de blocos, com major/minor numbers criados dinamicamente pelo udev).\n"
            "  - Camadas de Abstração do Kernel:\n"
            "    1. VFS (Virtual File System): Fornece interface padronizada de chamadas de sistema (open, read, write, ioctl) independente do sistema de arquivos físico (ext4, Btrfs, XFS).\n"
            "    2. Block Layer & Multi-Queue (blk-mq): Camada de blocos de alto desempenho que organiza as requisições em estruturas 'struct bio' e 'struct request', suportando milhões de IOPS em SSDs NVMe.\n"
            "    3. Device Drivers: Módulos de kernel (.ko) que traduzem os pedidos do blk-mq em comandos específicos das controladoras.\n"
            "  - Gerenciamento Dinâmico com Sysfs e Udev: O diretório virtual /sys expõe a topologia do hardware e parâmetros do kernel em tempo de execução; o udevd gerencia eventos de hotplug do kernel.\n"
            "  - E/S Assíncrona de Última Geração: Suporte nativo ao 'io_uring' (Kernel 6.8), que substitui a E/S síncrona por anéis de submissão e conclusão de memória compartilhada sem troca de contexto.",

            # Ubuntu 24.04 - Comandos
            "• CLI:\n"
            "  lsblk -e 7 -o NAME,MAJ:MIN,RM,SIZE,RO,TYPE,MOUNTPOINTS\n"
            "  (Lista dispositivos de bloco, major/minor numbers e pontos de montagem, excluindo loops de snap).\n\n"
            "• CLI:\n"
            "  udevadm info --query=all --name=/dev/nvme0n1\n"
            "  (Exibe propriedades completas de hardware registradas no udev para o dispositivo).\n\n"
            "• CLI:\n"
            "  dmesg | grep -iE 'ata|scsi|nvme|pci'\n"
            "  (Inspeciona mensagens do anel de log do kernel sobre detecção de controladoras e discos durante o boot).\n\n"
            "• GUI (Discos do GNOME - gnome-disks):\n"
            "  Interface gráfica para inspecionar partições, taxas de transferência, SMART, e editar parâmetros de montagem."
        ),

        # Linha 2: Buffering e Caching com Ilustração/Fluxograma
        (
            "O SO utiliza armazenamento em buffer?\nComo isso é feito?\n(Buffering, Caching, Writeback e Fluxogramas explicativos)",
            # Windows 11
            "• Sim, o Windows 11 utiliza Buffering e Caching extensivos em múltiplos níveis:\n"
            "  1. Buffering de I/O no I/O Manager:\n"
            "     - Buffered I/O (DO_BUFFERED_IO): O I/O Manager aloca um buffer no Non-Paged Pool do kernel. Dados são copiados do espaço de usuário para o kernel antes da transferência. Usado em dispositivos lentos/pequenos.\n"
            "     - Direct I/O (DO_DIRECT_IO): Usa MDL (Memory Descriptor List) para travar páginas físicas de usuário na RAM e transferir via DMA sem cópia intermediária de CPU.\n"
            "     - Neither I/O: Para subsistemas críticos de alta velocidade.\n"
            "  2. Windows Cache Manager (Cc):\n"
            "     - Integrado ao Gerenciador de Memória Virtual (VMM) via seções de arquivo mapeadas na memória virtual.\n"
            "     - Lazy Writer: Thread assíncrono do kernel (CcScanDpc) que varre periodicamente páginas modificadas e grava no disco sem bloquear o processo.\n"
            "     - Read-Ahead Preditivo: Detecta padrões de acesso sequencial e carrega páginas adjacentes antecipadamente na Standby List.\n"
            "     - Suporta gravações Write-Through (síncrona direta) e Write-Back (em cache com confirmação imediata).\n\n"
            "• FLUXOGRAMA DE BUFFERING/CACHING NO WINDOWS:\n"
            "  [App: WriteFile] --> [I/O Manager (Cria IRP)]\n"
            "         |\n"
            "         v\n"
            "  [Windows Cache Manager (CcCopyWrite)]\n"
            "         |\n"
            "  +------+-------------------------+\n"
            "  | Write-Back (Padrão)            | Write-Through (FILE_FLAG_WRITE_THROUGH)\n"
            "  v                                v\n"
            "  [Grava na Memória RAM]           [Bypass de Cache]\n"
            "  [Marca página como Dirty]        [Envia IRP ao Storport Miniport]\n"
            "  [Retorna Sucesso ao App]         [Grava no Disco Imediatamente]\n"
            "         |\n"
            "         v (Assíncrono)\n"
            "  [Lazy Writer (CcScanDpc)] --> [Descarga em Bloco para o Disco]",

            # Windows 11 - Comandos
            "• CLI (PowerShell):\n"
            "  Get-Counter '\\Cache\\Sync Data Flushes/sec', '\\Cache\\Lazy Write Flushes/sec', '\\Cache\\Read Aheads/sec' -Continuous\n"
            "  (Monitora em tempo real a taxa de descargas de cache do Lazy Writer e leituras preditivas).\n\n"
            "• CLI (Sysinternals):\n"
            "  rammap.exe\n"
            "  (Aba 'File Summary': Exibe detalhadamente cada arquivo mapeado no Cache Manager e quanto ocupa em RAM).\n\n"
            "• CLI (fsutil):\n"
            "  fsutil behavior query MemoryUsage\n"
            "  (Verifica ajustes de alocação de memória do cache do sistema de arquivos NTFS).\n\n"
            "• GUI (Monitor de Recursos - resmon.exe):\n"
            "  Aba 'Memória' > Faixa azul-clara 'Em Espera' (Standby Cache): Representa blocos de arquivos em cache que podem ser reutilizados instantaneamente sem ler do disco.",

            # Ubuntu 24.04
            "• Sim, o Ubuntu 24.04 (Kernel 6.8) possui um dos sistemas de cache de buffer mais sofisticados do mundo:\n"
            "  1. Linux Page Cache Unificado:\n"
            "     - Toda leitura ou gravação de arquivos passa pelo Page Cache (páginas de 4 KB ou folios indexados pela estrutura 'address_space' usando xarray).\n"
            "     - Elimina o duplo cache histórico: o antigo Buffer Cache agora reside dentro do Page Cache (cada página armazena 'struct buffer_head' para metadados de blocos).\n"
            "  2. Mecanismo de Writeback e Flusher Threads:\n"
            "     - Quando um processo faz 'write()', os dados são copiados para a página na RAM e marcados com a flag PG_dirty (escrita Write-Back).\n"
            "     - O processo é liberado instantaneamente (latência de microssegundos).\n"
            "     - Threads de descarga do kernel ('kworker/u:X' com 'wb_workfn') sincronizam periodicamente as páginas sujas para o disco, disparadas por limites configuráveis de memória:\n"
            "       * dirty_background_ratio (padrão ~10% de RAM): Inicia descarga em segundo plano.\n"
            "       * dirty_ratio (padrão ~20% de RAM): Bloqueia novos writes do app até que o cache baixe.\n"
            "  3. Bypass de Cache:\n"
            "     - Suporta flag O_DIRECT no open() (ignora o Page Cache para bancos de dados como PostgreSQL/Oracle) e O_SYNC (gravação síncrona).\n\n"
            "• FLUXOGRAMA DE BUFFERING/PAGE CACHE NO LINUX:\n"
            "  [App: write(fd, buf, len)] --> [Chamada de Sistema: sys_write]\n"
            "         |\n"
            "         v\n"
            "  [VFS: vfs_write()] --> [Verifica Flag O_DIRECT?]\n"
            "         |\n"
            "    +----+--------------------------------+\n"
            "    | NÃO (Normal com Cache)              | SIM (Direto)\n"
            "    v                                     v\n"
            "  [Page Cache (struct address_space)]   [Bypass do Page Cache]\n"
            "  [Copia dados para struct folio/page]  [Aloca struct bio direta]\n"
            "  [Seta flag PG_dirty na página]        [Envia para Fila DMA do NVMe]\n"
            "  [Retorna sucesso ao processo]\n"
            "         |\n"
            "         v (Periódico / dirty_expire_centisecs)\n"
            "  [kworker: flusher thread (wb_workfn)] --> [blk-mq: Grava no Disco]",

            # Ubuntu 24.04 - Comandos
            "• CLI:\n"
            "  cat /proc/meminfo | grep -E 'Cached|Buffers|Dirty|Writeback'\n"
            "  (Exibe o tamanho em KB do Page Cache, Buffers de metadados, e páginas sujas pendentes de gravação).\n\n"
            "• CLI (Configurar Limiares de Writeback):\n"
            "  sysctl -a | grep -E 'dirty_background_ratio|dirty_ratio|dirty_writeback_centisecs'\n"
            "  (Permite ajustar os parâmetros de descarga de páginas sujas do kernel em tempo de execução).\n\n"
            "• CLI (Forçar Descarga Imediata do Cache):\n"
            "  sync  # ou  echo 3 > /proc/sys/vm/drop_caches\n"
            "  (Força a escrita de todas as páginas sujas para o disco e esvazia caches de páginas limpas).\n\n"
            "• CLI:\n"
            "  vmstat 1 5\n"
            "  (Monitora colunas 'bi' - blocks in e 'bo' - blocks out, evidenciando a atividade do subsistema de blocos)."
        ),

        # Linha 3: Algoritmos de Escalonamento de Braço e SSDs
        (
            "Quais algoritmos de escalonamento de braço de disco são utilizados?\nFuncionam com SSD?\n(Análise em HDDs magnéticos vs. SSDs SATA / NVMe)",
            # Windows 11
            "• Escalonamento de Disco no Windows 11:\n"
            "  1. Camada de Escalonamento do Kernel:\n"
            "     - O Windows não utiliza mais algoritmos clássicos de braço geométrico (como SCAN puro ou C-LOOK) no nível de software do SO.\n"
            "     - O escalonamento é baseado em Prioridades de E/S do I/O Manager (5 níveis: Very Low/Background, Low, Normal, High, Critical).\n"
            "     - Processos em segundo plano (como Windows Update e Windows Search Indexer) recebem prioridade 'Very Low', impedindo que travem a interface interativa do usuário.\n"
            "     - A ordenação física dos setores no prato magnético é delegada diretamente à controladora de hardware via NCQ (Native Command Queuing) em discos SATA AHCI ou tagged queuing em SCSI.\n\n"
            "  2. Comportamento e Otimização para SSDs e NVMes:\n"
            "     - O Windows detecta automaticamente dispositivos não rotacionais através da consulta SCSI/ATA (propriedade 'Seek Penalty = 0').\n"
            "     - Em SSDs, o escalonamento de braço é completamente desnecessário e prejudicial (pois o SSD tem tempo de busca quase nulo e suporte a acesso paralelo por múltiplos canais de memória flash).\n"
            "     - O Windows desativa a desfragmentação mecânica tradicional em SSDs e ativa o comando TRIM (Data Set Management / Deallocate) via Storport Miniport, informando ao controlador flash quais blocos foram liberados para que o Garbage Collector limpe os blocos antes de novas gravações.\n"
            "     - Despacho direto de comandos: Para SSDs NVMe, utiliza filas de submissão e conclusão de hardware sem overhead de reordenação.",

            # Windows 11 - Comandos
            "• CLI (PowerShell):\n"
            "  Get-PhysicalDisk | Select-Object DeviceId, FriendlyName, MediaType, BusType, SpindleSpeed\n"
            "  (Identifica se o disco é SSD ou HDD, tipo de barramento NVMe/SATA e velocidade de rotação).\n\n"
            "• CLI (Verificar Status do TRIM):\n"
            "  fsutil behavior query DisableDeleteNotify\n"
            "  (Retorna '0' indicando que o comando TRIM para SSDs está ATIVADO tanto para NTFS quanto para ReFS).\n\n"
            "• CLI (Otimização / Re-TRIM de SSDs):\n"
            "  Optimize-Volume -DriveLetter C -Defrag -Verbose  # Para HDD\n"
            "  Optimize-Volume -DriveLetter C -ReTrim -Verbose  # Para SSD\n"
            "  (Executa o processo de otimização adequado ao tipo de mídia detectado).\n\n"
            "• GUI (Desfragmentar e Otimizar Unidades - dfrgui.exe):\n"
            "  Exibe o tipo de mídia ('Unidade de estado sólido' vs 'Disco rígido') e programa a execução de TRIM semanal em SSDs.",

            # Ubuntu 24.04
            "• Escalonamento de E/S no Ubuntu 24.04 (Kernel Linux 6.8):\n"
            "  1. Camada Multi-Queue (blk-mq):\n"
            "     - O Linux aposentou a antiga camada single-queue e os escalonadores legados (CFQ, Deadline original, NOOP). Toda a pilha opera sobre 'blk-mq' com filas por CPU para escalabilidade multithread.\n"
            "  2. Algoritmos Disponíveis no Kernel 6.8:\n"
            "     - 'none': Sem escalonador de software; repassa os bios diretamente para a fila de hardware (modo FIFO ultrarrápido). É o PADRÃO para SSDs NVMe ultrarrápidos, pois qualquer algoritmo de software aumentaria a latência e o consumo de CPU.\n"
            "     - 'mq-deadline': Otimização do Deadline para blk-mq. Garante prazo máximo para leituras (500ms) e escritas (5s), agrupando setores contíguos. É o PADRÃO para HDDs rotacionais e SSDs SATA.\n"
            "     - 'bfq' (Budget Fair Queueing): Escalonador proporcional de alta precisão baseado em orçamentos. Ideal para computadores interativos e discos mecânicos lentos, pois garante que um app interativo nunca congele sob downloads pesados.\n"
            "     - 'kyber': Desenvolvido pelo Facebook/Meta, monitora a latência em tempo real e estrangula filas quando a latência ultrapassa limites estipulados. Excelente para SSDs rápidos sob carga massiva.\n\n"
            "  3. Comportamento e Otimização para SSDs e NVMes:\n"
            "     - O kernel verifica '/sys/block/<dev>/queue/rotational' (0 para SSD, 1 para HDD).\n"
            "     - Para SSDs, desativa algoritmos de busca mecânica, eleva o limite de comandos concorrentes e ativa suporte a TRIM/Discard (comandos de liberação de páginas flash para a FTL - Flash Translation Layer).\n"
            "     - O serviço systemd 'fstrim.timer' executa semanalmente a limpeza de blocos órfãos em todas as partições montadas.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Verificar e Trocar Escalonador do Disco em Execução):\n"
            "  cat /sys/block/sda/queue/scheduler  # Ex.: [mq-deadline] none bfq\n"
            "  echo 'bfq' | sudo tee /sys/block/sda/queue/scheduler\n"
            "  (Exibe o escalonador ativo entre colchetes e permite alterar o algoritmo sem reiniciar).\n\n"
            "• CLI (Verificar se o Disco é Detectado como Rotacional):\n"
            "  cat /sys/block/sda/queue/rotational\n"
            "  (Retorna '0' para SSDs e '1' para HDDs mecânicos).\n\n"
            "• CLI (Executar TRIM Manualmente em SSDs):\n"
            "  sudo fstrim -v -a\n"
            "  (Envia comandos TRIM para todos os pontos de montagem compatíveis e relata bytes liberados).\n\n"
            "• CLI (Verificar Status do Timer de TRIM do Systemd):\n"
            "  systemctl status fstrim.timer\n"
            "  (Confirma que a otimização periódica de blocos de SSD está ativa no sistema operacional)."
        ),

        # Linha 4: Suporte a RAID
        (
            "O sistema permite o uso de RAID?\nQuais níveis?\n(RAID via Software, Espaços de Armazenamento / MDADM e Hardware)",
            # Windows 11
            "• Sim, o Windows 11 suporta RAID em múltiplos níveis, tanto por software quanto por hardware:\n"
            "  1. RAID via Software no Windows 11 Pro:\n"
            "     A) Espaços de Armazenamento (Storage Spaces - Tecnologia Moderna):\n"
            "        - Simples (Simple - RAID 0): Divide os dados em listras (striping) entre 2 ou mais discos para maximizar desempenho. Sem tolerância a falhas.\n"
            "        - Espelhamento Bidirecional (Two-way mirror - RAID 1): Grava 2 cópias completas dos dados em discos separados. Tolera a falha de 1 disco.\n"
            "        - Espelhamento Tridirecional (Three-way mirror): Grava 3 cópias dos dados em pelo menos 5 discos físicos. Tolera a falha simultânea de até 2 discos.\n"
            "        - Paridade (Parity - RAID 5): Grava dados com informações de paridade distribuídas entre pelo menos 3 discos físicos. Tolera a falha de 1 disco (economiza espaço em relação ao espelhamento).\n"
            "     B) Discos Dinâmicos Legados (Gerenciador de Disco):\n"
            "        - Volume Distribuído (Spanned / JBOD), Volume Listrado (RAID 0) e Volume Espelhado (RAID 1). O RAID 5 em disco dinâmico é reservado às edições Windows Server.\n\n"
            "  2. Suporte a RAID via Hardware:\n"
            "     - Suporte transparente e irrestrito a todos os níveis de RAID (0, 1, 5, 6, 10, 50, 60) implementados em controladoras dedicadas de hardware (Adaptec, MegaRAID, Intel VROC/RST) por meio de drivers Storport assinados.",

            # Windows 11 - Comandos
            "• CLI (PowerShell - Gerenciamento de Storage Spaces):\n"
            "  Get-StoragePool; Get-VirtualDisk; Get-PhysicalDisk\n"
            "  (Lista os pools de armazenamento, discos virtuais RAID e discos físicos membros).\n\n"
            "• CLI (Criar Pool de Storage Spaces):\n"
            "  New-StoragePool -FriendlyName 'PoolRAID' -StorageSubsystemFriendlyName 'Windows Storage*' -PhysicalDisks $Disks\n"
            "  New-VirtualDisk -StoragePoolFriendlyName 'PoolRAID' -FriendlyName 'DiscoEspelhado' -ResiliencySettingName Mirror -Size 500GB\n"
            "  (Cria um volume RAID 1 espelhado via PowerShell).\n\n"
            "• CLI (Diskpart):\n"
            "  diskpart\n"
            "  list disk; list volume\n"
            "  (Lista o particionamento e os tipos de volumes dinâmicos listrados ou espelhados).\n\n"
            "• GUI (Configurações > Sistema > Armazenamento > Espaços de Armazenamento):\n"
            "  Interface gráfica moderna do Windows 11 para criar pools de discos, configurar resiliência (Espelhamento ou Paridade) e monitorar integridade física.",

            # Ubuntu 24.04
            "• Sim, o Ubuntu 24.04 possui um dos suportes a RAID mais completos e flexíveis da indústria computacional:\n"
            "  1. RAID via Software Nativo com MDADM (Módulo de Kernel MD):\n"
            "     - RAID 0 (Striping): Distribui blocos igualmente entre N discos para desempenho máximo. Sem redundância.\n"
            "     - RAID 1 (Mirroring): Espelhamento completo de dados entre 2 ou mais discos. Leitura acelerada e alta tolerância a falhas.\n"
            "     - RAID 4: Paridade em nível de bloco dedicada em um único disco específico.\n"
            "     - RAID 5: Dados divididos em faixas com paridade distribuída entre N discos (mínimo 3). Tolera a perda de 1 disco.\n"
            "     - RAID 6: Dupla paridade distribuída com algoritmo de Reed-Solomon (mínimo 4 discos). Tolera a perda simultânea de até 2 discos.\n"
            "     - RAID 10 (1+0): Combina espelhamento e listramento em layouts altamente configuráveis ('near', 'far', 'offset').\n"
            "     - Modos Lineares / JBOD: Concatena múltiplos discos de tamanhos distintos em um único volume lógico contínuo.\n\n"
            "  2. RAID via LVM2 e Sistemas de Arquivos Avançados:\n"
            "     - LVM2: Permite criar Logical Volumes com flags '--type raid1', '--type raid5', '--type striped'.\n"
            "     - Btrfs & ZFS on Linux: Suportam RAID nativo integrado ao sistema de arquivos com soma de verificação (checksum) e autocura de blocos corrompidos (RAIDZ1, RAIDZ2, RAIDZ3).\n\n"
            "  3. Suporte a RAID via Hardware:\n"
            "     - Suporte nativo a controladoras SAS/SATA/NVMe corporativas via módulos de kernel abertos ou proprietários.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Instalação e Monitoramento com MDADM):\n"
            "  sudo mdadm --detail /dev/md0\n"
            "  (Exibe o nível de RAID, status dos discos, blocos de paridade e integridade do arranjo).\n\n"
            "• CLI (Criar Arranjo RAID 5 via Terminal):\n"
            "  sudo mdadm --create /dev/md0 --level=5 --raid-devices=3 /dev/sdb /dev/sdc /dev/sdd\n"
            "  (Cria um volume RAID 5 de três discos com paridade distribuída).\n\n"
            "• CLI (Monitorar Rebuild de RAID em Tempo Real):\n"
            "  cat /proc/mdstat\n"
            "  (Exibe todos os arranjos ativos, nível de RAID, e a barra de porcentagem de reconstrução em caso de troca de disco).\n\n"
            "• CLI (Salvar Configuração de Inicialização):\n"
            "  sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf\n"
            "  sudo update-initramfs -u\n"
            "  (Garante que o arranjo RAID seja montado automaticamente pelo kernel durante o boot).\n\n"
            "• GUI (Discos do GNOME - gnome-disks):\n"
            "  Permite criar e gerenciar arranjos RAID MDADM através da interface gráfica com poucos cliques."
        ),

        # Linha 5: Lista de Comandos Principais
        (
            "Lista de Comandos Principais / Relevantes\n(Diagnóstico, Estatísticas de E/S, Desempenho e Monitoramento)",
            # Windows 11
            "• Diagnóstico e Gerenciamento de Discos:\n"
            "  - diskpart: Utilitário completo para particionamento, inicialização MBR/GPT e volumes.\n"
            "  - chkdsk C: /f /r: Analisa a integridade lógica e setores defeituosos do sistema de arquivos.\n"
            "  - fsutil volume diskfree C:: Exibe capacidade total, espaço livre e bytes disponíveis.\n\n"
            "• Monitoramento de Desempenho de E/S:\n"
            "  - Get-Counter '\\Disco Físico(*)\\*': Captura contadores de comprimento de fila de disco, latência média (ms/Transfer) e taxa de transferência (Bytes/s).\n"
            "  - typeperf '\\PhysicalDisk(_Total)\\% Disk Time' -si 1: Exibe em tempo real a taxa de ocupação da cabeça de disco no terminal.\n"
            "  - resmon.exe: Monitor de Recursos > Aba 'Disco' mostra tempo de resposta (ms), processos com mais I/O e fila do disco em tempo real.\n"
            "  - perfmon.exe: Monitor de Desempenho avançado para criar conjuntos de coletores de dados.\n\n"
            "• Ferramentas Avançadas Sysinternals:\n"
            "  - Process Monitor (procmon): Rastreia cada IRP e operação de E/S por thread.\n"
            "  - DiskView: Mostra visualmente a alocação de blocos e clusters em cada setor físico do disco.\n"
            "  - Contig: Analisa e desfragmenta arquivos específicos individualmente.",

            # Windows 11 - Comandos
            "• CLI (Exemplos Práticos PowerShell):\n"
            "  # Medir tempo de resposta de leitura/escrita do disco em tempo real:\n"
            "  Get-Counter -Counter '\\PhysicalDisk(_Total)\\Avg. Disk sec/Transfer' -SampleInterval 2 -MaxSamples 5\n\n"
            "  # Inspecionar detalhes de velocidade e barramento:\n"
            "  Get-Disk | Select-Object Number, FriendlyName, OperationalStatus, Size, PartitionStyle\n\n"
            "  # Verificar integridade física via SMART:\n"
            "  Get-PhysicalDisk | Select-Object DeviceId, FriendlyName, HealthStatus, OperationalStatus\n\n"
            "  # Iniciar otimização de volume via linha de comando:\n"
            "  Optimize-Volume -DriveLetter C -Defrag -Verbose",

            # Ubuntu 24.04
            "• Diagnóstico e Gerenciamento de Discos:\n"
            "  - fdisk -l / parted -l: Lista partições, tipos de tabela de partição (GPT/MBR) e setores.\n"
            "  - smartctl -a /dev/nvme0n1: Exibe relatório completo de saúde SMART, temperatura, setores realocados e horas de uso (requer smartmontools).\n"
            "  - hdparm -Tt /dev/sda: Mede a velocidade de leitura do cache de memória e a velocidade de leitura sequencial física do disco.\n\n"
            "• Monitoramento de Desempenho de E/S:\n"
            "  - iostat -xz 1 5 (do pacote sysstat): Apresenta estatísticas detalhadas de E/S por dispositivo (r/s, w/s, rMB/s, wMB/s, await - latência média em ms, e %util - utilização do disco).\n"
            "  - iotop -o: Monitor interativo tipo 'top' que exibe em tempo real os processos que estão executando leitura e escrita em disco no momento.\n"
            "  - pidstat -d 1: Mostra estatísticas de E/S por PID individualmente.\n\n"
            "• Rastreamento em Nível de Kernel:\n"
            "  - blktrace / blkparse: Rastreia eventos de baixo nível na camada de blocos do kernel.\n"
            "  - bpftrace / bcc tools (biosnoop, biolatency): Utiliza eBPF para medir latência de E/S sem overhead de performance.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Exemplos Práticos Linux):\n"
            "  # Monitorar latência e saturação de disco em tempo real:\n"
            "  iostat -xz 1\n\n"
            "  # Identificar qual processo está consumindo o disco no momento:\n"
            "  sudo iotop -only\n\n"
            "  # Testar taxa de transferência direta (sem cache):\n"
            "  dd if=/dev/zero of=teste.img bs=1G count=1 oflag=direct\n\n"
            "  # Inspecionar estatísticas do controlador NVMe:\n"
            "  nvme list\n"
            "  nvme smart-log /dev/nvme0\n\n"
            "  # Listar arquivos abertos e descritores de E/S por processo:\n"
            "  lsof -p <PID>"
        ),

        # Linha 6: Referências Bibliográficas
        (
            "Referências Bibliográficas e Fontes Acadêmicas\n(Livros Didáticos, Artigos Científicos e Documentação Oficial)",
            # Windows 11
            "1. RUSCHINOVICH, Mark E.; SOLOMON, David A.; IONESCU, Alex. Windows Internals, Part 2: Addressing Infrastructure, Storage, File Systems, and More. 7. ed. Redmond: Microsoft Press, 2021.\n"
            "2. MICROSOFT CORPORATION. Windows Hardware Developer: Storage and File System Architecture. Microsoft Learn Documentation, 2024. Disponível em: <https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/>.\n"
            "3. SILBERSCHATZ, Abraham; GALVIN, Peter Baer; GAGNE, Greg. Operating System Concepts. 10. ed. Hoboken: John Wiley & Sons, 2018. (Capítulo 13: I/O Systems; Capítulo 14: Mass-Storage Structure).\n"
            "4. TANENBAUM, Andrew S.; BOS, Herbert. Sistemas Operacionais Modernos. 4. ed. São Paulo: Pearson Education do Brasil, 2016. (Capítulo 5: Entrada/Saída; Capítulo 11: Estudo de Caso 2: Windows Vista/Windows 7/8/10).",
            
            # Windows 11 - Comandos
            "• Documentações Oficiais Microsoft:\n"
            "  - Microsoft Learn: 'Storport Driver Architecture'\n"
            "  - Microsoft Learn: 'Storage Spaces Overview'\n"
            "  - Windows Sysinternals Documentation (Mark Russinovich).",

            # Ubuntu 24.04
            "1. LOVE, Robert. Linux Kernel Development. 3. ed. Upper Saddle River: Addison-Wesley, 2010. (Capítulo 13: The Virtual Filesystem; Capítulo 14: The Block I/O Layer; Capítulo 16: The Page Cache and Page Writeback).\n"
            "2. BOVET, Daniel P.; CESATI, Marco. Understanding the Linux Kernel. 3. ed. Sebastopol: O'Reilly Media, 2005.\n"
            "3. CORBET, Jonathan; RUBINI, Alessandro; KROAH-HARTMAN, Greg. Linux Device Drivers. 3. ed. Sebastopol: O'Reilly Media, 2005.\n"
            "4. KERNEL.ORG. The Linux Kernel Documentation: Block Layer (blk-mq) & I/O Schedulers. Release 6.8, 2024. Disponível em: <https://docs.kernel.org/block/>.\n"
            "5. STALLINGS, William. Sistemas Operacionais: Projetos e Princípios Internos. 7. ed. São Paulo: Pearson, 2012. (Capítulo 11: Gerenciamento de E/S e Escalonamento de Disco).",

            # Ubuntu 24.04 - Comandos
            "• Manuais do Kernel e Man Pages:\n"
            "  - man 8 mdadm\n"
            "  - man 1 iostat\n"
            "  - man 8 fstrim\n"
            "  - Linux Kernel blk-mq Documentation: <https://www.kernel.org/doc/html/latest/block/blk-mq.html>"
        )
    ]

    # Column widths
    worksheet.set_column(0, 0, 24, topic_fmt)
    worksheet.set_column(1, 1, 38, content_fmt)
    worksheet.set_column(2, 2, 34, cmd_fmt)
    worksheet.set_column(3, 3, 38, content_fmt)
    worksheet.set_column(4, 4, 34, cmd_fmt)

    # Write data with appropriate row heights
    row_heights = [260, 310, 290, 290, 280, 220]
    start_row = 3
    for i, row in enumerate(data):
        row_num = start_row + i
        h = row_heights[i] if i < len(row_heights) else 240
        worksheet.set_row(row_num, h)
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
    out_file = os.path.join(out_dir, "modelo_estudo_caso_es_preenchido.xlsx")
    create_io_comparative_spreadsheet(out_file)

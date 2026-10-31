import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation(filepath):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank slide layout

    # Palette
    COLOR_NAVY = RGBColor(27, 54, 93)        # #1B365D Primary Dark
    COLOR_SLATE = RGBColor(41, 128, 185)     # #2980B9 Secondary Blue
    COLOR_WIN_ACCENT = RGBColor(0, 120, 215) # Windows Blue
    COLOR_WIN_BG = RGBColor(240, 246, 255)   # Very light blue
    COLOR_LNX_ACCENT = RGBColor(222, 70, 24) # Ubuntu Orange
    COLOR_LNX_BG = RGBColor(255, 245, 240)   # Very light orange
    COLOR_TEXT_MAIN = RGBColor(30, 30, 30)
    COLOR_TEXT_MUTED = RGBColor(90, 90, 90)
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_CARD_BORDER = RGBColor(215, 225, 235)

    def add_header(slide, title_text, category_text="ESTUDO DE CASO: SUBSISTEMA DE ENTRADA E SAÍDA (E/S)"):
        # Header banner shape
        header_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        header_box.fill.solid()
        header_box.fill.fore_color.rgb = COLOR_NAVY
        header_box.line.color.rgb = COLOR_NAVY

        # Category and Title text
        cat_tf = header_box.text_frame
        cat_tf.word_wrap = True
        cat_tf.margin_left = Inches(0.8)
        cat_tf.margin_top = Inches(0.18)
        p_cat = cat_tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = 'Segoe UI'
        p_cat.font.size = Pt(9.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = RGBColor(160, 200, 245)

        p_title = cat_tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = 'Segoe UI'
        p_title.font.size = Pt(20)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE

        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.35))
        ftf = footer_box.text_frame
        p_foot = ftf.paragraphs[0]
        p_foot.text = "Sistemas Operacionais | Prof. Dr. Douglas Véras | Alunos: Luiz Maranhão & Mário Jorge (UFRPE)"
        p_foot.font.name = 'Segoe UI'
        p_foot.font.size = Pt(8.5)
        p_foot.font.color.rgb = COLOR_TEXT_MUTED

    def add_comparison_cards(slide, win_points, lnx_points, win_cmds=None, lnx_cmds=None):
        card_w = Inches(5.6)
        card_h = Inches(5.65)
        card_y = Inches(1.3)
        win_x = Inches(0.8)
        lnx_x = Inches(6.933)

        # Windows Card Shape
        win_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, win_x, card_y, card_w, card_h)
        win_card.fill.solid()
        win_card.fill.fore_color.rgb = COLOR_WIN_BG
        win_card.line.color.rgb = COLOR_WIN_ACCENT
        win_card.line.width = Pt(1.5)

        # Ubuntu Card Shape
        lnx_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, lnx_x, card_y, card_w, card_h)
        lnx_card.fill.solid()
        lnx_card.fill.fore_color.rgb = COLOR_LNX_BG
        lnx_card.line.color.rgb = COLOR_LNX_ACCENT
        lnx_card.line.width = Pt(1.5)

        # Windows Content
        wtf = win_card.text_frame
        wtf.word_wrap = True
        wtf.margin_left = Inches(0.3)
        wtf.margin_right = Inches(0.3)
        wtf.margin_top = Inches(0.25)
        
        p0 = wtf.paragraphs[0]
        p0.text = "Windows 11 Pro (23H2 / 24H2)"
        p0.font.name = 'Segoe UI'
        p0.font.size = Pt(13.5)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_WIN_ACCENT

        for item in win_points:
            p = wtf.add_paragraph()
            p.space_before = Pt(3.5)
            p.level = 0
            if isinstance(item, tuple):
                p.text = f"• {item[0]}: "
                p.font.name = 'Segoe UI'
                p.font.size = Pt(9)
                p.font.bold = True
                p.font.color.rgb = COLOR_TEXT_MAIN
                run = p.add_run()
                run.text = item[1]
                run.font.bold = False
                run.font.color.rgb = COLOR_TEXT_MAIN
            else:
                p.text = f"• {item}"
                p.font.name = 'Segoe UI'
                p.font.size = Pt(9)
                p.font.color.rgb = COLOR_TEXT_MAIN

        if win_cmds:
            p_sep = wtf.add_paragraph()
            p_sep.space_before = Pt(5)
            p_sep.text = "🔧 Comandos e Ferramentas Práticas:"
            p_sep.font.name = 'Segoe UI'
            p_sep.font.size = Pt(9.5)
            p_sep.font.bold = True
            p_sep.font.color.rgb = COLOR_WIN_ACCENT

            for cmd in win_cmds:
                p_c = wtf.add_paragraph()
                p_c.space_before = Pt(1.5)
                p_c.text = f"> {cmd}"
                p_c.font.name = 'Consolas'
                p_c.font.size = Pt(8)
                p_c.font.color.rgb = RGBColor(20, 60, 110)

        # Ubuntu Content
        ltf = lnx_card.text_frame
        ltf.word_wrap = True
        ltf.margin_left = Inches(0.3)
        ltf.margin_right = Inches(0.3)
        ltf.margin_top = Inches(0.25)
        
        p0_l = ltf.paragraphs[0]
        p0_l.text = "Ubuntu 24.04 LTS (Kernel Linux 6.8)"
        p0_l.font.name = 'Segoe UI'
        p0_l.font.size = Pt(13.5)
        p0_l.font.bold = True
        p0_l.font.color.rgb = COLOR_LNX_ACCENT

        for item in lnx_points:
            p = ltf.add_paragraph()
            p.space_before = Pt(3.5)
            p.level = 0
            if isinstance(item, tuple):
                p.text = f"• {item[0]}: "
                p.font.name = 'Segoe UI'
                p.font.size = Pt(9)
                p.font.bold = True
                p.font.color.rgb = COLOR_TEXT_MAIN
                run = p.add_run()
                run.text = item[1]
                run.font.bold = False
                run.font.color.rgb = COLOR_TEXT_MAIN
            else:
                p.text = f"• {item}"
                p.font.name = 'Segoe UI'
                p.font.size = Pt(9)
                p.font.color.rgb = COLOR_TEXT_MAIN

        if lnx_cmds:
            p_sep_l = ltf.add_paragraph()
            p_sep_l.space_before = Pt(5)
            p_sep_l.text = "🔧 Comandos e Ferramentas Práticas:"
            p_sep_l.font.name = 'Segoe UI'
            p_sep_l.font.size = Pt(9.5)
            p_sep_l.font.bold = True
            p_sep_l.font.color.rgb = COLOR_LNX_ACCENT

            for cmd in lnx_cmds:
                p_c = ltf.add_paragraph()
                p_c.space_before = Pt(1.5)
                p_c.text = f"$ {cmd}"
                p_c.font.name = 'Consolas'
                p_c.font.size = Pt(8)
                p_c.font.color.rgb = RGBColor(120, 30, 10)

    # =========================================================================
    # SLIDE 1: Capa
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_NAVY
    bg1.line.color.rgb = COLOR_NAVY

    # Decorative accent line
    dec_line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(2.2), Inches(2.5), Inches(0.08))
    dec_line.fill.solid()
    dec_line.fill.fore_color.rgb = RGBColor(0, 190, 255)
    dec_line.line.color.rgb = RGBColor(0, 190, 255)

    title_box = s1.shapes.add_textbox(Inches(1.2), Inches(2.4), Inches(11.0), Inches(2.8))
    ttf = title_box.text_frame
    ttf.word_wrap = True
    
    p = ttf.paragraphs[0]
    p.text = "ESTUDO DE CASO: SUBSISTEMA DE E/S"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(160, 205, 255)

    p2 = ttf.add_paragraph()
    p2.text = "Gerenciamento de Entrada e Saída em Sistemas Operacionais"
    p2.font.name = 'Segoe UI'
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(8)

    p3 = ttf.add_paragraph()
    p3.text = "Análise Comparativa: Windows 11 Pro (23H2/24H2) vs. Ubuntu 24.04 LTS (Kernel 6.8)"
    p3.font.name = 'Segoe UI'
    p3.font.size = Pt(16)
    p3.font.color.rgb = RGBColor(220, 235, 250)
    p3.space_before = Pt(6)

    meta_box = s1.shapes.add_textbox(Inches(1.2), Inches(5.3), Inches(11.0), Inches(1.8))
    mtf = meta_box.text_frame
    mtf.word_wrap = True
    
    mp1 = mtf.paragraphs[0]
    mp1.text = "Universidade Federal Rural de Pernambuco (UFRPE) | Bacharelado em Ciência da Computação"
    mp1.font.name = 'Segoe UI'
    mp1.font.size = Pt(12)
    mp1.font.color.rgb = RGBColor(180, 205, 230)

    mp2 = mtf.add_paragraph()
    mp2.text = "Disciplina: Sistemas Operacionais | Docente: Prof. Dr. Douglas Véras"
    mp2.font.name = 'Segoe UI'
    mp2.font.size = Pt(12)
    mp2.font.color.rgb = RGBColor(180, 205, 230)
    mp2.space_before = Pt(4)

    mp3 = mtf.add_paragraph()
    mp3.text = "Discentes: Luiz Maranhão & Mário Jorge | Outubro de 2026"
    mp3.font.name = 'Segoe UI'
    mp3.font.size = Pt(13)
    mp3.font.bold = True
    mp3.font.color.rgb = RGBColor(255, 215, 0) # Gold
    mp3.space_before = Pt(8)

    # =========================================================================
    # SLIDE 2: Introdução e Arquitetura de E/S
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Introdução ao Subsistema de E/S e Arquitetura de Camadas")
    add_comparison_cards(
        s2,
        win_points=[
            ("Modelo Modular", "Orientado a IRPs (I/O Request Packets) criados pelo I/O Manager (ntoskrnl.exe)."),
            ("Camadas de Drivers", "Filter Drivers (BitLocker/Antivírus) -> Functional Device Drivers (NTFS/ReFS) -> Bus & Storport Miniports."),
            ("Abstração de Objetos", "Dispositivos expostos no Object Namespace (\\Device\\HarddiskVolumeX) com links simbólicos (C:, D:)."),
            ("E/S Assíncrona Nativa", "I/O Completion Ports (IOCP) com alta escalabilidade multithread para aplicações de servidor."),
            ("Controle de Hardware", "Comunicação via HAL (Hardware Abstraction Layer) isolando controladores de barramento PCIe/USB.")
        ],
        lnx_points=[
            ("Filosofia Unix", "'Tudo é Arquivo': periféricos mapeados em /dev como nós especiais de bloco (brw-) ou caractere (crw-)."),
            ("Camadas de Kernel", "VFS (Virtual File System) -> Page Cache -> Block Layer (blk-mq) -> Device Drivers (.ko)."),
            ("Gerenciamento Dinâmico", "Sysfs (/sys) expõe topologia do hardware; udevd gerencia hotplug e regras de permissões."),
            ("E/S Assíncrona Moderna", "Subsistema 'io_uring' (Kernel 6.8): anéis de submissão e conclusão de memória compartilhada sem troca de contexto."),
            ("Comunicação", "Acesso via chamadas de sistema unificadas (open, read, write, ioctl) e interfaces de barramento.")
        ],
        win_cmds=[
            "Get-PnpDevice -Class 'DiskDrive', 'SCSIAdapter'",
            "driverquery /v /fo table",
            "procmon.exe (Sysinternals Process Monitor)"
        ],
        lnx_cmds=[
            "lsblk -e 7 -o NAME,MAJ:MIN,SIZE,TYPE,MOUNTPOINTS",
            "udevadm info --query=all --name=/dev/nvme0n1",
            "dmesg | grep -iE 'ata|scsi|nvme|pci'"
        ]
    )

    # =========================================================================
    # SLIDE 3: Buffering e Caching
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "2. Armazenamento em Buffer e Cache (Buffering & Caching)")
    add_comparison_cards(
        s3,
        win_points=[
            ("Modos no I/O Manager", "Buffered I/O (Non-Paged Pool), Direct I/O (via MDL - Memory Descriptor List com DMA) e Neither I/O."),
            ("Windows Cache Manager", "Integrado ao Gerenciador de Memória Virtual (VMM) através de seções mapeadas de 256 KB."),
            ("Mecanismo Write-Back", "Chamadas WriteFile copiam para RAM e marcam página como Dirty com retorno instantâneo ao aplicativo."),
            ("Lazy Writer (CcScanDpc)", "Thread periódica do kernel que desperta a cada 1s e grava blocos sujos no disco assincronamente."),
            ("Read-Ahead Preditivo", "Detecta acessos sequenciais e pré-carrega blocos adjacentes na Standby Page List.")
        ],
        lnx_points=[
            ("Linux Page Cache", "Cache unificado: todo bloco de disco é mapeado em páginas de 4 KB ou 'struct folio' no address_space (XArray)."),
            ("Mecanismo Writeback", "Chamada write() copia para RAM via copy_from_user(), seta PG_dirty e retorna em microssegundos."),
            ("Flusher Threads", "Daemons kworker (wb_workfn) sincronizam páginas sujas governed por limiares do /proc/sys/vm/."),
            ("Limiares de Memória", "dirty_background_ratio (~10% RAM) inicia descarga; dirty_ratio (~20% RAM) bloqueia processos para evitar esgotamento."),
            ("Bypass de Cache", "Suporte a flag O_DIRECT (ignora cache para SGBDs) e O_SYNC (escrita síncrona imediata).")
        ],
        win_cmds=[
            "Get-Counter '\\Cache\\Lazy Write Flushes/sec' -Continuous",
            "rammap.exe (Sysinternals - Aba File Summary)",
            "resmon.exe (Monitor de Recursos - Faixa 'Em Espera')"
        ],
        lnx_cmds=[
            "cat /proc/meminfo | grep -E 'Cached|Buffers|Dirty'",
            "sysctl -a | grep -E 'dirty_background_ratio|dirty_ratio'",
            "sync; echo 3 > /proc/sys/vm/drop_caches"
        ]
    )

    # =========================================================================
    # SLIDE 4: Fluxograma de Buffering e Caching
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "2.1 Fluxograma Comparativo do Fluxo de Gravação em Buffer")
    add_comparison_cards(
        s4,
        win_points=[
            ("Passo 1 (User)", "Processo chama WriteFile(hFile, buf, len)."),
            ("Passo 2 (Kernel)", "I/O Manager monta IRP e despacha para o Cache Manager."),
            ("Passo 3 (RAM)", "CcCopyWrite copia os dados para página mapeada na memória virtual e ativa bit Dirty."),
            ("Passo 4 (Retorno)", "I/O Manager retorna sucesso imediato à aplicação."),
            ("Passo 5 (Descarga)", "Lazy Writer (CcScanDpc) desperta, agrupa páginas sujas e despacha IRP_MJ_WRITE em bloco para o driver Storport."),
            ("Passo 6 (Mídia)", "Controladora grava na mídia física e página passa para Standby List.")
        ],
        lnx_points=[
            ("Passo 1 (User)", "Processo chama write(fd, buf, count)."),
            ("Passo 2 (Kernel)", "VFS aciona vfs_write() e consulta o address_space via XArray."),
            ("Passo 3 (RAM)", "Copia dados para struct folio na RAM e marca a flag PG_dirty na página."),
            ("Passo 4 (Retorno)", "sys_write retorna contagem de bytes instantaneamente."),
            ("Passo 5 (Descarga)", "Flusher thread (wb_workfn) desperta por tempo ou limiar dirty_background_ratio e monta requisições struct bio."),
            ("Passo 6 (Mídia)", "Camada blk-mq envia para DMA da controladora e desativa a flag PG_dirty.")
        ],
        win_cmds=[
            "Get-Counter '\\Disco Físico(*)\\Gravações de Disco/s'",
            "fsutil behavior query MemoryUsage"
        ],
        lnx_cmds=[
            "vmstat 1 5 (Colunas 'bi' e 'bo')",
            "iostat -xz 1 (Métrica wMB/s e %util)"
        ]
    )

    # =========================================================================
    # SLIDE 5: Escalonamento de Braço de Disco
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "3. Escalonamento de Braço de Disco em Discos Rotacionais (HDDs)")
    add_comparison_cards(
        s5,
        win_points=[
            ("Abordagem Moderna", "O Windows 11 abandonou algoritmos geométricos no SO (SCAN/SSTF foram removidos do kernel)."),
            ("Delegação ao Hardware", "A ordenação de setores é delegada ao NCQ (Native Command Queuing) da controladora AHCI/SATA (fila de 32 comandos no firmware do HDD)."),
            ("Escalonamento por Prioridades", "O I/O Manager gerencia 5 níveis de prioridade de E/S (Very Low até Critical)."),
            ("Proteção Interativa", "Processos como Windows Update e Search Indexer rodam em 'Very Low', sendo estrangulados quando o usuário acessa o disco."),
            ("Storport Driver", "Garante despacho balanceado sem saturação de canal.")
        ],
        lnx_points=[
            ("Camada blk-mq", "Multi-Queue Block I/O Layer com filas por núcleo de CPU para escalabilidade multithread."),
            ("Escalonador mq-deadline", "Padrão para HDDs mecânicos: filas FIFO com prazos máximos (500 ms leitura, 5 s escrita) e ordenação por setor contíguo."),
            ("Escalonador bfq", "Budget Fair Queueing: distribui orçamentos de setores por processo, garantindo que tarefas pesadas não travem o desktop."),
            ("Fim do Starvation", "Tanto mq-deadline quanto bfq impedem que requisições distantes sofram inanição prolongada."),
            ("Configuração Dinâmica", "Permite trocar de algoritmo em tempo real sem reboot via interface do Sysfs.")
        ],
        win_cmds=[
            "Get-PhysicalDisk | Select DeviceId, FriendlyName, SpindleSpeed",
            "typeperf '\\PhysicalDisk(_Total)\\% Disk Time' -si 1",
            "resmon.exe (Aba Disco > Fila de Disco)"
        ],
        lnx_cmds=[
            "cat /sys/block/sda/queue/scheduler",
            "echo 'bfq' | sudo tee /sys/block/sda/queue/scheduler",
            "iotop -o (Processos ordenados por I/O ativo)"
        ]
    )

    # =========================================================================
    # SLIDE 6: Funcionamento com SSDs e NVMes
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "3.1 Comportamento do Escalonador com SSDs e NVMes")
    add_comparison_cards(
        s6,
        win_points=[
            ("Detecção de Flash", "Consulta SCSI/ATA: identifica Seek Penalty = 0 e classifica a unidade como SSD."),
            ("Sem Escalonamento Geométrico", "Tempo de busca quase nulo e múltiplos canais paralelos tornam reordenação mecânica inútil e prejudicial."),
            ("Desfragmentação Desativada", "O Windows substitui a desfragmentação mecânica por re-TRIM periódico (evita desgaste prematuro das células NAND)."),
            ("Comando TRIM Nativo", "Ativo por padrão (DisableDeleteNotify = 0); notifica o controlador para executar Garbage Collection antecipado."),
            ("Protocolo NVMe", "Despacho direto de IRPs para as filas de submissão do hardware PCIe.")
        ],
        lnx_points=[
            ("Detecção Automática", "Kernel verifica /sys/block/sdX/queue/rotational: valor 0 desliga otimizações de seek rotacional."),
            ("Escalonador 'none' (Padrão NVMe)", "Bypass completo de escalonador: requisições vão direto às filas de hardware em FIFO (elimina overhead de CPU)."),
            ("Escalonador 'kyber'", "Algoritmo leve do Facebook/Meta que monitora latência em tempo real e estrangula filas sob saturação."),
            ("Suporte a TRIM / Discard", "Serviço systemd fstrim.timer executa fstrim -av semanalmente para descarte de blocos órfãos."),
            ("Arquitetura NVMe Multi-Fila", "Aproveita até 64.000 filas de submissão/conclusão de hardware com milhões de IOPS.")
        ],
        win_cmds=[
            "fsutil behavior query DisableDeleteNotify",
            "Optimize-Volume -DriveLetter C -ReTrim -Verbose",
            "Get-Disk | Select Number, FriendlyName, BusType"
        ],
        lnx_cmds=[
            "cat /sys/block/nvme0n1/queue/scheduler  # Exibe: [none] mq-deadline",
            "sudo fstrim -v -a",
            "systemctl status fstrim.timer"
        ]
    )

    # =========================================================================
    # SLIDE 7: Suporte a RAID
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "4. Suporte a RAID (Redundant Array of Independent Disks)")
    add_comparison_cards(
        s7,
        win_points=[
            ("Espaços de Armazenamento", "Tecnologia moderna Storage Spaces: cria pools e discos virtuais com diferentes resiliências."),
            ("Níveis no Storage Spaces", "• Simples (RAID 0 - striping)\n• Espelhamento 2-way (RAID 1 - tolera 1 falha)\n• Espelhamento 3-way (tolera 2 falhas)\n• Paridade (RAID 5 - paridade distribuída)."),
            ("Discos Dinâmicos (Legado)", "Suporta Volumes Listrados (RAID 0) e Espelhados (RAID 1). RAID 5 é bloqueado no Windows 11 Pro (restrito ao Windows Server)."),
            ("RAID por Hardware", "Suporte completo e transparente a todos os níveis (0, 1, 5, 6, 10, 50, 60) via drivers Storport certificados WHQL.")
        ],
        lnx_points=[
            ("MDADM (Módulo md do Kernel)", "Padrão corporativo para Software RAID. Suporta nativamente RAID 0, RAID 1, RAID 4, RAID 5, RAID 6 e RAID 10."),
            ("Layouts Avançados no RAID 10", "Suporta geometrias 'near', 'far' e 'offset' para maximizar vazão de leitura com segurança de espelhamento."),
            ("LVM2 e Device-Mapper", "Permite criar Logical Volumes com flags --type raid1 e --type raid5 dinamicamente."),
            ("RAID em Sistemas de Arquivos", "Btrfs (RAID 0, 1, 1C3, 10 com autocura por checksum) e OpenZFS (RAIDZ1, RAIDZ2, RAIDZ3)."),
            ("RAID por Hardware", "Amplo suporte nativo sem restrições de licenciamento.")
        ],
        win_cmds=[
            "Get-StoragePool; Get-VirtualDisk",
            "New-StoragePool -FriendlyName 'PoolRAID' ...",
            "diskpart > list volume"
        ],
        lnx_cmds=[
            "sudo mdadm --create /dev/md0 --level=5 --raid-devices=3 ...",
            "sudo mdadm --detail /dev/md0",
            "cat /proc/mdstat (Monitora rebuild em tempo real)"
        ]
    )

    # =========================================================================
    # SLIDE 8: Comandos Principais e Monitoramento
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "5. Comandos Principais e Ferramentas Práticas de Diagnóstico")
    add_comparison_cards(
        s8,
        win_points=[
            ("diskpart", "Gerenciamento completo de partições MBR/GPT, volumes e letras de unidade."),
            ("chkdsk C: /f /r", "Verificação e reparo de integridade do sistema de arquivos NTFS/FAT."),
            ("Get-Counter", "Coleta contadores de desempenho de latência de disco, tamanho de fila e taxa de transferência."),
            ("resmon.exe", "Monitor de Recursos com gráficos em tempo real de latência (ms) e fila de disco."),
            ("procmon (Sysinternals)", "Rastreamento avançado de cada IRP e chamada CreateFile/ReadFile/WriteFile por thread."),
            ("DiskView (Sysinternals)", "Mapeamento gráfico de clusters e setores gravados na superfície do disco.")
        ],
        lnx_points=[
            ("fdisk / parted", "Manipulação de tabelas de partição GPT/MBR e alinhamento de setores."),
            ("smartctl -a /dev/sdX", "Inspeção completa de integridade física SMART, temperatura e setores defeituosos."),
            ("iostat -xz 1 5", "Estatísticas de E/S detalhadas da camada de blocos (r/s, w/s, await em ms, %util)."),
            ("iotop -o", "Monitor interativo em tempo real dos processos com maior consumo de E/S."),
            ("dd if=... of=... oflag=direct", "Teste de taxa de transferência bruta contornando o Page Cache."),
            ("lsof -p <PID>", "Lista todos os arquivos abertos e descritores de E/S do processo.")
        ],
        win_cmds=[
            "Get-Counter '\\PhysicalDisk(_Total)\\Avg. Disk sec/Transfer'",
            "Get-PhysicalDisk | Select DeviceId, HealthStatus",
            "Optimize-Volume -DriveLetter C -Defrag -Verbose"
        ],
        lnx_cmds=[
            "sudo iostat -xz 1",
            "sudo iotop -only",
            "sudo smartctl -a /dev/nvme0n1"
        ]
    )

    # =========================================================================
    # SLIDE 9: Matriz Comparativa Síntese
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "6. Matriz Comparativa Resumida (Windows 11 vs. Ubuntu 24.04)")

    table_shape = s9.shapes.add_table(7, 3, Inches(0.8), Inches(1.35), Inches(11.733), Inches(5.4))
    table = table_shape.table
    table.columns[0].width = Inches(2.733)
    table.columns[1].width = Inches(4.5)
    table.columns[2].width = Inches(4.5)

    headers_table = ["Critério de Comparação", "Windows 11 Pro (23H2 / 24H2)", "Ubuntu 24.04 LTS (Kernel Linux 6.8)"]
    for c_idx, h_text in enumerate(headers_table):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = 'Segoe UI'
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

    matrix_rows = [
        ("Arquitetura Central de E/S", "I/O Manager com IRPs + Storport Miniport", "VFS + blk-mq (Multi-Queue) + Módulos de Kernel"),
        ("Mecanismo de Buffering/Cache", "Windows Cache Manager (seções 256KB) + Lazy Writer", "Linux Page Cache unificado (struct folio / XArray) + Flushers"),
        ("Bypass de Cache (E/S Direta)", "Direct I/O via MDL (Memory Descriptor List)", "Flag de abertura O_DIRECT no open()"),
        ("Escalonamento em HDDs", "Delegado ao hardware via NCQ (AHCI) + 5 Prioridades SO", "Algoritmos blk-mq: mq-deadline ou bfq"),
        ("Escalonamento em SSDs / NVMes", "Sem reordenação mecânica; TRIM ativo por padrão", "Algoritmo 'none' (Bypass direto em FIFO) + fstrim.timer"),
        ("Suporte a RAID", "Storage Spaces (Simples, 2-way/3-way mirror, Paridade)", "mdadm (RAID 0,1,4,5,6,10), LVM2, Btrfs e ZFS nativos")
    ]

    for r_idx, (crit, win_val, lnx_val) in enumerate(matrix_rows, start=1):
        c0 = table.cell(r_idx, 0)
        c0.fill.solid()
        c0.fill.fore_color.rgb = COLOR_CARD_BORDER
        p0 = c0.text_frame.paragraphs[0]
        p0.text = crit
        p0.font.name = 'Segoe UI'
        p0.font.size = Pt(9.5)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_NAVY

        c1 = table.cell(r_idx, 1)
        c1.fill.solid()
        c1.fill.fore_color.rgb = COLOR_WIN_BG
        p1 = c1.text_frame.paragraphs[0]
        p1.text = win_val
        p1.font.name = 'Segoe UI'
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = COLOR_TEXT_MAIN

        c2 = table.cell(r_idx, 2)
        c2.fill.solid()
        c2.fill.fore_color.rgb = COLOR_LNX_BG
        p2 = c2.text_frame.paragraphs[0]
        p2.text = lnx_val
        p2.font.name = 'Segoe UI'
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = COLOR_TEXT_MAIN

    # =========================================================================
    # SLIDE 10: Referências Bibliográficas
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "7. Referências Bibliográficas e Documentações Oficiais")

    ref_box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(5.5))
    ref_box.fill.solid()
    ref_box.fill.fore_color.rgb = RGBColor(250, 252, 255)
    ref_box.line.color.rgb = COLOR_CARD_BORDER
    ref_box.line.width = Pt(1)

    rtf = ref_box.text_frame
    rtf.word_wrap = True
    rtf.margin_left = Inches(0.4)
    rtf.margin_right = Inches(0.4)
    rtf.margin_top = Inches(0.3)

    p_ref_head = rtf.paragraphs[0]
    p_ref_head.text = "Obras Acadêmicas e Manuais Técnicos Oficiais:"
    p_ref_head.font.name = 'Segoe UI'
    p_ref_head.font.size = Pt(13)
    p_ref_head.font.bold = True
    p_ref_head.font.color.rgb = COLOR_NAVY

    references = [
        "1. SILBERSCHATZ, Abraham; GALVIN, Peter Baer; GAGNE, Greg. Operating System Concepts. 10. ed. Hoboken: John Wiley & Sons, 2018. (Capítulo 13: I/O Systems; Capítulo 14: Mass-Storage Structure).",
        "2. TANENBAUM, Andrew S.; BOS, Herbert. Sistemas Operacionais Modernos. 4. ed. São Paulo: Pearson, 2016. (Capítulo 5: Entrada/Saída; Capítulo 10: Linux; Capítulo 11: Windows).",
        "3. STALLINGS, William. Sistemas Operacionais: Projetos e Princípios Internos. 7. ed. São Paulo: Pearson, 2012. (Capítulo 11: Gerenciamento de E/S e Escalonamento de Disco).",
        "4. RUSSINOVICH, Mark E.; SOLOMON, David A.; IONESCU, Alex. Windows Internals, Part 2: Addressing Infrastructure, Storage, File Systems, and More. 7. ed. Microsoft Press, 2021.",
        "5. LOVE, Robert. Linux Kernel Development. 3. ed. Upper Saddle River: Addison-Wesley, 2010. (Capítulo 14: The Block I/O Layer; Capítulo 16: The Page Cache and Page Writeback).",
        "6. KERNEL.ORG. The Linux Kernel Documentation: Block Layer (blk-mq) & Multi-Queue I/O Schedulers. Release 6.8, 2024. Disponível em: <https://docs.kernel.org/block/>.",
        "7. MICROSOFT LEARN. Storage and File System Architecture: Storport Miniports and Storage Spaces. 2024. Disponível em: <https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/>.",
        "8. PATTERSON, D. A.; GIBSON, G.; KATZ, R. H. A Case for Redundant Arrays of Inexpensive Disks (RAID). In: ACM SIGMOD Conference, 1988, Chicago. Proceedings... p. 109-116."
    ]

    for ref in references:
        pref = rtf.add_paragraph()
        pref.space_before = Pt(5)
        pref.text = ref
        pref.font.name = 'Segoe UI'
        pref.font.size = Pt(9.5)
        pref.font.color.rgb = COLOR_TEXT_MAIN

    prs.save(filepath)
    print(f"Presentation generated successfully at: {filepath}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Apresentacoes")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "Apresentacao_Estudo_de_Caso_ES.pptx")
    create_presentation(out_file)

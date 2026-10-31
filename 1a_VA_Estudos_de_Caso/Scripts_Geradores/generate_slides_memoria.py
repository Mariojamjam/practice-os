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
    COLOR_NAVY = RGBColor(27, 54, 93)      # #1B365D Primary Dark
    COLOR_SLATE = RGBColor(41, 128, 185)   # #2980B9 Secondary Blue
    COLOR_WIN_ACCENT = RGBColor(0, 120, 215) # Windows Blue
    COLOR_WIN_BG = RGBColor(240, 246, 255)   # Very light blue
    COLOR_LNX_ACCENT = RGBColor(222, 70, 24) # Ubuntu Orange
    COLOR_LNX_BG = RGBColor(255, 245, 240)   # Very light orange
    COLOR_TEXT_MAIN = RGBColor(30, 30, 30)
    COLOR_TEXT_MUTED = RGBColor(90, 90, 90)
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_CARD_BORDER = RGBColor(215, 225, 235)
    COLOR_CMD_BG = RGBColor(245, 247, 250)

    def add_header(slide, title_text, category_text="ESTUDO DE CASO: GERENCIAMENTO DE MEMÓRIA"):
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
        p0.font.size = Pt(14)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_WIN_ACCENT

        for item in win_points:
            p = wtf.add_paragraph()
            p.space_before = Pt(4)
            p.level = 0
            if isinstance(item, tuple):
                p.text = f"• {item[0]}: "
                p.font.name = 'Segoe UI'
                p.font.size = Pt(9.5)
                p.font.bold = True
                p.font.color.rgb = COLOR_TEXT_MAIN
                run = p.add_run()
                run.text = item[1]
                run.font.bold = False
                run.font.color.rgb = COLOR_TEXT_MAIN
            else:
                p.text = f"• {item}"
                p.font.name = 'Segoe UI'
                p.font.size = Pt(9.5)
                p.font.color.rgb = COLOR_TEXT_MAIN

        if win_cmds:
            p_sep = wtf.add_paragraph()
            p_sep.space_before = Pt(6)
            p_sep.text = "🔧 Comandos e Ferramentas Práticas:"
            p_sep.font.name = 'Segoe UI'
            p_sep.font.size = Pt(10)
            p_sep.font.bold = True
            p_sep.font.color.rgb = COLOR_WIN_ACCENT

            for cmd in win_cmds:
                p_c = wtf.add_paragraph()
                p_c.space_before = Pt(2)
                p_c.text = f"> {cmd}"
                p_c.font.name = 'Consolas'
                p_c.font.size = Pt(8.5)
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
        p0_l.font.size = Pt(14)
        p0_l.font.bold = True
        p0_l.font.color.rgb = COLOR_LNX_ACCENT

        for item in lnx_points:
            p = ltf.add_paragraph()
            p.space_before = Pt(4)
            p.level = 0
            if isinstance(item, tuple):
                p.text = f"• {item[0]}: "
                p.font.name = 'Segoe UI'
                p.font.size = Pt(9.5)
                p.font.bold = True
                p.font.color.rgb = COLOR_TEXT_MAIN
                run = p.add_run()
                run.text = item[1]
                run.font.bold = False
                run.font.color.rgb = COLOR_TEXT_MAIN
            else:
                p.text = f"• {item}"
                p.font.name = 'Segoe UI'
                p.font.size = Pt(9.5)
                p.font.color.rgb = COLOR_TEXT_MAIN

        if lnx_cmds:
            p_sep_l = ltf.add_paragraph()
            p_sep_l.space_before = Pt(6)
            p_sep_l.text = "🔧 Comandos e Ferramentas Práticas:"
            p_sep_l.font.name = 'Segoe UI'
            p_sep_l.font.size = Pt(10)
            p_sep_l.font.bold = True
            p_sep_l.font.color.rgb = COLOR_LNX_ACCENT

            for cmd in lnx_cmds:
                p_c = ltf.add_paragraph()
                p_c.space_before = Pt(2)
                p_c.text = f"$ {cmd}"
                p_c.font.name = 'Consolas'
                p_c.font.size = Pt(8.5)
                p_c.font.color.rgb = RGBColor(120, 30, 10)

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide (Capa)
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_NAVY
    bg1.line.fill.background()

    card_t = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.0), Inches(10.933), Inches(5.5))
    card_t.fill.solid()
    card_t.fill.fore_color.rgb = COLOR_WHITE
    card_t.line.color.rgb = COLOR_SLATE
    card_t.line.width = Pt(2)

    ctf = card_t.text_frame
    ctf.word_wrap = True
    ctf.margin_left = Inches(0.8)
    ctf.margin_right = Inches(0.8)
    ctf.margin_top = Inches(0.7)

    p = ctf.paragraphs[0]
    p.text = "UNIVERSIDADE FEDERAL RURAL DE PERNAMBUCO (UFRPE)"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_SLATE

    p = ctf.add_paragraph()
    p.text = "DEPARTAMENTO DE COMPUTAÇÃO | SISTEMAS OPERACIONAIS"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_MUTED
    p.space_after = Pt(24)

    p = ctf.add_paragraph()
    p.text = "ESTUDO DE CASO: GERENCIAMENTO DE MEMÓRIA"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    p = ctf.add_paragraph()
    p.text = "Análise Comparativa: Windows 11 Pro (23H2/24H2) vs. Ubuntu 24.04 LTS (Kernel Linux 6.8)"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_WIN_ACCENT
    p.space_after = Pt(36)

    p = ctf.add_paragraph()
    p.text = "• Discentes (Dupla): Luiz Maranhão & Mário Jorge\n• Docente: Prof. Dr. Douglas Véras\n• Tema: Paginação, Segmentação, Swap, Particionamento, Algoritmos de Alocação e Substituição"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    # -------------------------------------------------------------
    # SLIDE 2: Agenda / Roteiro da Apresentação
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Roteiro da Apresentação e Objetivos do Estudo")

    agenda_card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.65))
    agenda_card.fill.solid()
    agenda_card.fill.fore_color.rgb = COLOR_WHITE
    agenda_card.line.color.rgb = COLOR_CARD_BORDER
    agenda_card.line.width = Pt(1)

    atf = agenda_card.text_frame
    atf.word_wrap = True
    atf.margin_left = Inches(0.6)
    atf.margin_top = Inches(0.4)

    topics = [
        ("01", "Introdução ao Gerenciamento de Memória", "Hierarquia de memórias, memória virtual, funções da MMU/TLB e isolamento de proteção Ring 3 vs. Ring 0."),
        ("02", "Paginação e Memória Virtual x86-64", "Tabelas multiníveis (PML4/PML5), tamanhos de página (4 KB, Large/Huge Pages) e estruturas de kernel (PTE, PFN, Folios)."),
        ("03", "Segmentação de Memória", "Transição para o Modelo Plano (Flat Model) no x86-64 e o uso moderno dos registradores GS (Windows TEB/KPCR) e FS/GS (Linux TLS/per-CPU)."),
        ("04", "Swap, Paging e Compactação de Memória", "Pagefile.sys e Compactação na RAM (Windows) vs. Partição/Arquivo Swap e zRAM/zswap com OOM Killer (Linux)."),
        ("05", "Partições Fixas vs. Variáveis e Estruturas", "Particionamento dinâmico em RAM: LFH / Segment Heap e Bitmaps (Windows) vs. Buddy System binário e SLUB (Linux)."),
        ("06", "Algoritmos de Alocação e Substituição", "Best-Fit/First-Fit em listas segregadas vs. Buddy $O(1)$; Standby List de 8 Prioridades vs. Relógio de 2 Listas e MGLRU."),
        ("07", "Comandos Práticos, Ferramentas e Referências", "Mapeamento prático via PowerShell/Sysinternals e Linux CLI/procfs, fundamentado na literatura científica clássica.")
    ]

    p_a0 = atf.paragraphs[0]
    p_a0.text = "ESTRUTURA METODOLÓGICA DA ANÁLISE COMPARATIVA"
    p_a0.font.name = 'Segoe UI'
    p_a0.font.size = Pt(13)
    p_a0.font.bold = True
    p_a0.font.color.rgb = COLOR_NAVY
    p_a0.space_after = Pt(12)

    for num, title, desc in topics:
        p_t = atf.add_paragraph()
        p_t.space_before = Pt(6)
        p_t.text = f"[{num}]  {title} — "
        p_t.font.name = 'Segoe UI'
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_SLATE

        run = p_t.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = COLOR_TEXT_MAIN

    # -------------------------------------------------------------
    # SLIDE 3: Introdução Teórica ao Gerenciamento de Memória
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Introdução Teórica: Princípios e Arquitetura de Memória")

    c1 = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(5.6), Inches(5.65))
    c1.fill.solid()
    c1.fill.fore_color.rgb = COLOR_WHITE
    c1.line.color.rgb = COLOR_CARD_BORDER
    c1.line.width = Pt(1)

    c1_tf = c1.text_frame
    c1_tf.word_wrap = True
    c1_tf.margin_left = Inches(0.4)
    c1_tf.margin_right = Inches(0.4)
    c1_tf.margin_top = Inches(0.3)

    p = c1_tf.paragraphs[0]
    p.text = "1. Hierarquia de Memória e Ilusão de Escala"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(6)

    h_items = [
        ("Trade-off Custo x Capacidade x Latência", "A CPU acessa Registradores (~0.5 ns) e Caches L1/L2/L3 (~1 a 15 ns), enquanto a RAM física opera em ~60 ns e dispositivos secundários (SSDs/HDDs) em centenas de microssegundos a milissegundos."),
        ("Princípio da Localidade Temporal e Espacial", "Processos tendem a reutilizar instruções recentes (temporal) e acessar endereços vizinhos contíguos (espacial). A memória virtual explora essa premissa para manter em RAM apenas o conjunto ativo de trabalho (*Working Set*)."),
        ("Papel da Memória Virtual", "Desacopla o espaço de endereçamento lógico visto pelo programador da memória física real instalada, viabilizando execução de programas maiores que a RAM física.")
    ]
    for tit, dsc in h_items:
        p_i = c1_tf.add_paragraph()
        p_i.space_before = Pt(4)
        p_i.text = f"• {tit}: "
        p_i.font.name = 'Segoe UI'
        p_i.font.size = Pt(9.5)
        p_i.font.bold = True
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        r = p_i.add_run()
        r.text = dsc
        r.font.bold = False
        r.font.color.rgb = COLOR_TEXT_MAIN

    c2 = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), Inches(1.3), Inches(5.6), Inches(5.65))
    c2.fill.solid()
    c2.fill.fore_color.rgb = COLOR_WHITE
    c2.line.color.rgb = COLOR_CARD_BORDER
    c2.line.width = Pt(1)

    c2_tf = c2.text_frame
    c2_tf.word_wrap = True
    c2_tf.margin_left = Inches(0.4)
    c2_tf.margin_right = Inches(0.4)
    c2_tf.margin_top = Inches(0.3)

    p2 = c2_tf.paragraphs[0]
    p2.text = "2. MMU, Tradução e Objetivos Fundamentais"
    p2.font.name = 'Segoe UI'
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_NAVY
    p2.space_after = Pt(6)

    mmu_items = [
        ("MMU (Memory Management Unit)", "Dispositivo de hardware integrado à CPU que intercepta todas as instruções de acesso e realiza a tradução de Endereço Virtual -> Endereço Físico em tempo de execução."),
        ("TLB (Translation Lookaside Buffer)", "Cache associativa de altíssima velocidade na CPU que armazena traduções recentes de páginas virtuais para quadros físicos, evitando travessias caras na árvore de tabelas de páginas."),
        ("Proteção e Isolamento Estrito", "Cada processo reside em seu próprio espaço de endereçamento de 64 bits. O hardware (bits User/Supervisor e NX/DEP) bloqueia acessos indevidos entre aplicações ou violação da memória protegida do Kernel (Ring 0)."),
        ("Compartilhamento Eficiente", "Permite mapear bibliotecas de código comum (DLLs / Shared Objects .so) em múltiplas tabelas de páginas apontando para o mesmo quadro físico em modo leitura/cópia em escrita (*Copy-on-Write* - COW).")
    ]
    for tit, dsc in mmu_items:
        p_i = c2_tf.add_paragraph()
        p_i.space_before = Pt(4)
        p_i.text = f"• {tit}: "
        p_i.font.name = 'Segoe UI'
        p_i.font.size = Pt(9.5)
        p_i.font.bold = True
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        r = p_i.add_run()
        r.text = dsc
        r.font.bold = False
        r.font.color.rgb = COLOR_TEXT_MAIN

    # -------------------------------------------------------------
    # SLIDE 4: Tópico 1 - Paginação
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Tópico 1: O SO utiliza Paginação? Como é feito?")

    win4 = [
        ("Paginação x86-64 Nativa", "Suporte a 4 níveis de tabelas por padrão (PML4 -> PDPT -> PD -> PT) e 5 níveis (PML5 / LA57) em CPUs compatíveis."),
        ("Tamanhos de Página", "Páginas regulares de 4 KB. Suporte a Large Pages de 2 MB (via VirtualAlloc + MEM_LARGE_PAGES) e Huge Pages de 1 GB para virtualização/hipervisor."),
        ("Entrada de Tabela (PTE)", "PTE de 64 bits contendo PFN (Page Frame Number), bits Valid, Dirty, Accessed, Write, User/Supervisor e NX (No-Execute / DEP)."),
        ("PFN Database (nt!_MMPFN)", "Vetor global indexado do kernel que rastreia cada moldura física de RAM: Active, Standby, Modified, Free, Zeroed e Transition."),
        ("Working Set (nt!_MMWSL)", "Lista de páginas físicas residentes de cada processo; gerenciada ativamente pelo Memory Manager.")
    ]
    win4_cmd = [
        "Get-Process | Sort-Object WorkingSet64 -Desc | Select Name, Id, WorkingSet64",
        "Sysinternals RAMMap.exe (Análise completa do PFN Database)",
        "GUI: Monitor de Recursos (resmon.exe) > Guia 'Memória' (Working Set/Privada)"
    ]

    lnx4 = [
        ("Paginação Multinível em Árvore", "Arquitetura com 4 níveis (PGD -> P4D -> PUD -> PMD -> PTE) e 5 níveis compilado por padrão no Ubuntu 24.04 (suporte a até 128 PB de espaço virtual)."),
        ("Tamanhos de Página", "Página base de 4 KB. Suporte automático a Transparent Huge Pages (THP) de 2 MB e suporte dedicado a HugeTLB de 1 GB."),
        ("struct page & struct folio", "Cada moldura física é descrita por struct page / folio no Kernel 6.8, monitorando _refcount, flags (PG_active, PG_dirty, PG_lru) e mapeamento."),
        ("mm_struct & CR3", "A mm_struct encapsula o diretório de páginas (pgd_t), cujo endereço físico é carregado no registrador CR3 na comutação de contexto."),
        ("vm_area_struct (VMA)", "Maple Tree e Red-Black Tree indexam regiões virtuais contíguas de memória e permissões por processo.")
    ]
    lnx4_cmd = [
        "getconf PAGESIZE  # Retorna 4096 bytes",
        "pmap -x <PID>  # ou cat /proc/<PID>/smaps (mapeamento completo)",
        "cat /sys/kernel/mm/transparent_hugepage/enabled",
        "GUI: gnome-system-monitor > Processos > Clique direito > Mapas de Memória"
    ]
    add_comparison_cards(slide4, win4, lnx4, win4_cmd, lnx4_cmd)

    # -------------------------------------------------------------
    # SLIDE 5: Tópico 2 - Segmentação
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Tópico 2: O SO utiliza Segmentação? Como é feito?")

    win5 = [
        ("Modelo de Memória Plana (Flat Model)", "Em x86-64 (Long Mode), a segmentação por hardware é essencialmente desativada. Seletores CS, DS, ES e SS possuem base em 0 e limite desconsiderado pela CPU."),
        ("Uso Estratégico do Registrador GS", "O registrador de segmento GS é a chave de endereçamento de estruturas críticas de contexto:"),
        ("GS em Modo Kernel (Ring 0)", "Aponta para o KPCR (Kernel Processor Control Region), provendo acesso imediato a CurrentThread, temporizadores e filas DPC do núcleo."),
        ("GS em Modo Usuário (Ring 3)", "Aponta para o TEB (Thread Environment Block - GS:[0x30]), que por sua vez referencia o PEB (Process Environment Block)."),
        ("Tabelas de Descritores", "A GDT contém seletores estáticos mínimos; a LDT (Local Descriptor Table) é inexistente em aplicações nativas de 64 bits.")
    ]
    win5_cmd = [
        "WinDbg: r gs, r cs, r ss; !pcr; !teb (inspeciona KPCR e TEB)",
        "Process Explorer: Propriedades > Threads > Stack (endereço base do TEB)",
        "PowerShell: Get-Process (consome atributos de identificação do TEB/PEB)"
    ]

    lnx5 = [
        ("Flat Memory Model no x86-64", "Assim como no Windows, o Linux opera no modelo de memória linear plano. A CPU ignora base e limite para a maioria dos registradores de segmento."),
        ("GDT Mínima por CPU", "O kernel Linux inicializa uma GDT enxuta com descritores essenciais: __KERNEL_CS, __KERNEL_DS, __USER_CS, __USER_DS e TSS (para pilhas de interrupção IST)."),
        ("Registrador FS (User Space)", "Adotado pela glibc (NPTL) como ponteiro base para o Thread-Local Storage (TLS). Variáveis locais de thread são acessadas via %fs:offset."),
        ("Registrador GS (Kernel Space)", "Aponta para estruturas de dados per-CPU (ponteiro current, pilhas de interrupção, contadores). A instrução 'swapgs' troca a base de GS nas syscalls."),
        ("LDT Opcional", "Desativada por padrão; ativável seletivamente via chamada modify_ldt() para emuladores (Wine / DOSBox).")
    ]
    lnx5_cmd = [
        "dmesg | grep -i -E 'gdt|segments|fsgsbase'",
        "gdb -p <PID> -batch -ex 'info registers fs gs cs ss'",
        "grep CONFIG_MODIFY_LDT_SYSCALL /boot/config-$(uname -r)"
    ]
    add_comparison_cards(slide5, win5, lnx5, win5_cmd, lnx5_cmd)

    # -------------------------------------------------------------
    # SLIDE 6: Tópico 3 - Swap e Paging
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Tópico 3: O SO faz uso de Swap? Como é feito?")

    win6 = [
        ("Arquivos de Paginação", "Utiliza o 'pagefile.sys' (armazenamento secundário) e o 'swapfile.sys' (suspensão/hibernação de apps UWP)."),
        ("Compactação de Memória na RAM", "Antes de gravar no disco, o Gerenciador de Memória comprime páginas frias em um 'Compression Store' na própria RAM (processo System), economizando I/O."),
        ("Estrutura MMPAGING_FILE", "Mantém descritores de cada arquivo de paginação aberto e bitmaps de controle de blocos de disco livres."),
        ("Modified Page Writer", "Threads em segundo plano reúnem páginas modificadas em lotes (*clustering*) para gravação sequencial otimizada em disco."),
        ("Compromisso de Memória", "O limite de 'Commit' é a soma da RAM física com todos os pagefiles ativos.")
    ]
    win6_cmd = [
        "Get-CimInstance Win32_PageFileUsage | Select Name, AllocatedBaseSize, CurrentUsage",
        "Get-Process -Name 'System' | Select Name, WS, PrivateMemorySize (Compactada)",
        "GUI: sysdm.cpl > Avançado > Desempenho > Avançado > Memória Virtual (Alterar)"
    ]

    lnx6 = [
        ("Partição vs. Arquivo de Swap", "Ubuntu 24.04 utiliza por padrão '/swapfile' de tamanho dinâmico, suportando também partições dedicadas."),
        ("Tecnologia zRAM & zswap", "zRAM cria discos de bloco comprimidos na RAM (via zstd/lz4); zswap atua como cache frontal comprimido antes de descarregar no disco."),
        ("Estrutura swap_info_struct", "O kernel mantém um vetor global rastreando prioridades de dispositivos, setores livres e estatísticas de swap."),
        ("Parâmetro vm.swappiness", "Controla o balanço entre esvaziar páginas anônimas para swap vs. descartar Page Cache de arquivos do disco (padrão desktop: 60)."),
        ("OOM Killer", "Quando RAM e Swap esgotam, o kernel invoca o Out-of-Memory Killer para encerrar a tarefa de maior 'oom_score' preservando o SO.")
    ]
    lnx6_cmd = [
        "swapon --show  # ou cat /proc/swaps",
        "free -h  # Visão imediata de RAM e Swap usada/livre",
        "cat /proc/sys/vm/swappiness  # Leitura e ajuste via sysctl",
        "sudo fallocate -l 4G /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile"
    ]
    add_comparison_cards(slide6, win6, lnx6, win6_cmd, lnx6_cmd)

    # -------------------------------------------------------------
    # SLIDE 7: Tópico 4 - Partições Fixas ou Variáveis e Estruturas
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Tópico 4: Partições Fixas ou Variáveis e Técnicas/Estruturas")

    win7 = [
        ("Particionamento Variável Dinâmico", "Alocação aos processos e gerenciamento de heaps operam com partições de tamanho variável sob demanda (sobre molduras de paginação de 4 KB)."),
        ("Segment Heap & LFH", "O Low Fragmentation Heap (LFH) categoriza blocos de até 16 KB em 'buckets' predefinidos, eliminando fragmentação externa."),
        ("Mapas de Bits (RtlBitmap)", "Utilizados para rastrear slots livres em sub-segmentos de páginas e posições livres no arquivo de paginação."),
        ("Listas Duplamente Encadeadas", "Listas LIST_ENTRY conectam blocos livres do heap tradicional e pools de páginas."),
        ("Paged e Non-Paged Pools", "Paged Pool aloca estruturas variáveis que podem ser paginadas; Non-Paged Pool garante residência física para rotinas críticas (ISR/DPC).")
    ]
    win7_cmd = [
        "Get-CimInstance Win32_OperatingSystem | Select TotalVisibleMemorySize, FreePhysicalMemory",
        "Sysinternals coreinfo.exe -m  # Topologia NUMA e domínios de alocação",
        "Sysinternals vmmap.exe <PID>  # Mapeia todas as partições do heap",
        "GUI: Gerenciador de Tarefas > Desempenho > Memória (Pool Paginável/Não Paginável)"
    ]

    lnx7 = [
        ("Particionamento Variável no Kernel e User-Space", "O Linux opera com partições variáveis para processos, apoiado por estruturas hierárquicas altamente especializadas:"),
        ("Buddy System (Parceiros Binários)", "Alocador de páginas físicas contíguas do kernel em potências de 2 ($2^0$ a $2^{10}$ páginas). Utiliza struct list_head duplamente encadeada e bitmaps."),
        ("Alocador SLUB (Kernel Objects)", "Aloca estruturas internas (task_struct, mm_struct) com objetos de tamanho fixo em páginas reservadas, alcançando tempo $O(1)$ sem fragmentação externa."),
        ("User-Space (ptmalloc3 da glibc)", "Divide o heap em blocos variáveis com cabeçalhos de controle, gerenciados por listas encadeadas circulares em categorias (*bins*): Fast, Small e Unsorted.")
    ]
    lnx7_cmd = [
        "cat /proc/buddyinfo  # Blocos contíguos livres por ordem 2^k",
        "sudo slabtop -s c  # ou cat /proc/slabinfo (caches do alocador SLUB)",
        "grep -E 'Slab|SReclaimable' /proc/meminfo",
        "GUI: gnome-system-monitor > Processos (monitoramento de RSS/VIRT dinâmico)"
    ]
    add_comparison_cards(slide7, win7, lnx7, win7_cmd, lnx7_cmd)

    # -------------------------------------------------------------
    # SLIDE 8: Tópico 5 - Algoritmos de Alocação
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Tópico 5: Quais Algoritmos de Alocação são Utilizados?")

    win8 = [
        ("Segregated Free Lists em O(1)", "No LFH (Low Fragmentation Heap), alocações até 16 KB acessam diretamente a lista segregada do tamanho requerido sem busca linear."),
        ("Best-Fit & First-Fit em Listas Livres", "No NT Heap legado e no Segment Heap para blocos médios, algoritmos Best-Fit buscam o menor bloco suficiente para minimizar resíduos."),
        ("Coalescência Imediata de Blocos", "Ao desalocar memória, blocos adjacentes livres são imediatamente fundidos (*merging*) para conter fragmentação externa."),
        ("Lookaside Lists Rápidas no Kernel", "Listas LIFO de alocação ultrarrápida sem bloqueios pesados para estruturas recorrentes do SO."),
        ("VirtualAlloc para Grandes Alocações", "Requisições > 512 KB bypassam o heap e alocam diretamente molduras de páginas inteiras da MMU.")
    ]
    win8_cmd = [
        "WinDbg: !heap -s  (Sumário de todos os heaps e status de LFH/Segment Heap)",
        "WinDbg: !heap -p -a <Endereço> (Inspeciona alocador de bloco)",
        "PowerShell: Get-Process | Where {$_.NonpagedSystemMemorySize64 -gt 10MB}",
        "Process Hacker / System Informer: Guia 'Heaps' do processo"
    ]

    lnx8 = [
        ("Algoritmo do Buddy System", "Aloca blocos de ordem $2^k$. Se não houver bloco do tamanho exato, divide o bloco superior em dois parceiros (buddies). Na liberação, faz coalescência binária via operação XOR em $O(1)$."),
        ("Alocação Exata no SLUB", "Acesso imediato ao topo da freelist do slab para tipos fixos de estruturas sem qualquer pesquisa linear."),
        ("Exact-Fit (glibc Fastbins)", "Alocações pequenas no espaço de usuário utilizam listas LIFO sem coalescência imediata para máxima velocidade."),
        ("Best-Fit Aproximado (Largebins)", "Busca o menor bloco livre que atenda à requisição em listas ordenadas por tamanho decrescente."),
        ("First-Fit (Unsorted Bins)", "Reaproveita blocos recém-liberados no primeiro encaixe para acelerar padrões de alocação transitórios.")
    ]
    lnx8_cmd = [
        "cat /proc/buddyinfo  # Análise dos blocos de potências de 2 disponíveis",
        "vmstat -m  # Estatísticas dos caches de alocação de kernel",
        "ltrace -e malloc+free ls  # Rastreamento das chamadas da glibc",
        "valgrind --tool=massif ls  # Perfilamento detalhado de heap"
    ]
    add_comparison_cards(slide8, win8, lnx8, win8_cmd, lnx8_cmd)

    # -------------------------------------------------------------
    # SLIDE 9: Tópico 6 - Algoritmos de Substituição de Páginas
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Tópico 6: Quais Algoritmos de Substituição de Páginas são Utilizados?")

    win9 = [
        ("Working Set Trimming", "Cada processo tem cotas de páginas na RAM. Sob pressão física, o Balance Set Manager remove páginas excedentes do conjunto residente."),
        ("Bit Accessed e Aging (LRU Aproximado)", "O SO monitora o bit de acesso da CPU e decrementa contadores de envelhecimento para identificar páginas frias."),
        ("Standby Page List em 8 Prioridades", "Páginas limpas removidas vão para a Standby List organizada em 8 níveis (0 a 7). Se requisitadas antes do reuso, ocorre um Soft Page Fault instantâneo sem leitura em disco."),
        ("Modified Page List", "Páginas alteradas são enfileiradas e gravadas em lotes pelo Modified Page Writer antes de serem liberadas."),
        ("SuperFetch / SysMain", "Algoritmo heurístico que antecipa o carregamento de páginas na Standby List com base nos padrões horários do usuário.")
    ]
    win9_cmd = [
        "Get-Counter '\\Memory\\Page Faults/sec', '\\Memory\\Transition Faults/sec'",
        "Sysinternals RAMMap.exe > Guia 'Priority Summary' (Níveis 0 a 7 do Standby)",
        "perfmon.msc: Contadores \\Memory\\Pages/sec e \\Memory\\Page Writes/sec",
        "GUI: Gerenciador de Tarefas > Desempenho > Memória (Métrica 'Em Cache')"
    ]

    lnx9 = [
        ("Algoritmo de Relógio de Duas Listas", "Tradicional aproximação de LRU baseada no Algoritmo de Segunda Chance (Clock). Páginas circulam entre a Inactive List e a Active List conforme os acessos."),
        ("Daemon kswapd", "Processo do kernel que desperta quando a RAM atinge marcas d'água mínimas (watermarks), transferindo páginas inativas para o swap."),
        ("MGLRU (Multi-Gen LRU) - Inovação 6.8", "Grande avanço ativado no Kernel do Ubuntu 24.04: divide páginas em múltiplas gerações temporais com histogramas de acesso de vários níveis."),
        ("Vantagens do MGLRU", "Reduz em até 80% o uso de CPU para substituição de páginas e previne travamentos e latências de I/O em máquinas sob alta pressão de memória."),
        ("Page Cache Reclaim", "Páginas limpas de arquivos mapeados são descartadas instantaneamente sem necessidade de escrita em swap.")
    ]
    lnx9_cmd = [
        "cat /sys/kernel/mm/lru_gen/enabled  # Verifica e ativa o MGLRU",
        "grep -E 'Active|Inactive' /proc/meminfo  # Estado das duas listas",
        "vmstat 1 5  # Monitora campos si/so e trocas de páginas em tempo real",
        "sar -B 1 5  # Taxas de page fault e reclaim (pacote sysstat)"
    ]
    add_comparison_cards(slide9, win9, lnx9, win9_cmd, lnx9_cmd)

    # -------------------------------------------------------------
    # SLIDE 10: Tabela Consolidada de Comandos e Ferramentas
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Guia Prático: Comandos de Linha de Comando e GUI")

    grid_card = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.65))
    grid_card.fill.solid()
    grid_card.fill.fore_color.rgb = COLOR_WHITE
    grid_card.line.color.rgb = COLOR_CARD_BORDER
    grid_card.line.width = Pt(1)

    gtf = grid_card.text_frame
    gtf.word_wrap = True
    gtf.margin_left = Inches(0.4)
    gtf.margin_top = Inches(0.3)

    p_g0 = gtf.paragraphs[0]
    p_g0.text = "QUADRO COMPARATIVO DE FERRAMENTAS E COMANDOS"
    p_g0.font.name = 'Segoe UI'
    p_g0.font.size = Pt(12.5)
    p_g0.font.bold = True
    p_g0.font.color.rgb = COLOR_NAVY
    p_g0.space_after = Pt(8)

    cmd_rows = [
        ("Visão Geral de Memória", "PowerShell: Get-CimInstance Win32_OperatingSystem\nGUI: Gerenciador de Tarefas > Desempenho", "CLI: free -h  |  vmstat -s 1  |  cat /proc/meminfo\nGUI: gnome-system-monitor (Aba Recursos)"),
        ("Mapeamento por Processo", "PowerShell: Get-Process | Select Name, Id, WS, PM\nSysinternals: vmmap.exe <PID>", "CLI: pmap -x <PID>  |  cat /proc/<PID>/smaps\nGUI: gnome-system-monitor > Mapas de Memória"),
        ("Swap e Compactação", "PowerShell: Get-CimInstance Win32_PageFileUsage\nGUI: sysdm.cpl (Propriedades do Sistema > Memória Virtual)", "CLI: swapon --show  |  cat /proc/swaps\nsysctl vm.swappiness  |  dmesg | grep -i oom"),
        ("Alocadores e Heaps", "WinDbg: !heap -s  |  !pcr  |  !teb\nProcess Hacker: Guia Heaps e detecção LFH", "CLI: cat /proc/buddyinfo (Buddy System)\nsudo slabtop -s c  |  cat /proc/slabinfo (SLUB)"),
        ("Substituição e Faltas", "PowerShell: Get-Counter '\\Memory\\Page Faults/sec'\nSysinternals: rammap.exe (Listas Standby 0-7 e Modified)", "CLI: cat /sys/kernel/mm/lru_gen/enabled (MGLRU)\nvmstat 1  |  sar -B 1 5 (sysstat)")
    ]

    for cat, win, lnx in cmd_rows:
        p_c = gtf.add_paragraph()
        p_c.space_before = Pt(5)
        p_c.text = f"[{cat}]"
        p_c.font.name = 'Segoe UI'
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = COLOR_SLATE

        p_det = gtf.add_paragraph()
        p_det.space_before = Pt(1)
        p_det.text = f"  • Windows: {win.replace(chr(10), '  |  ')}"
        p_det.font.name = 'Consolas'
        p_det.font.size = Pt(8.5)
        p_det.font.color.rgb = COLOR_WIN_ACCENT

        p_det2 = gtf.add_paragraph()
        p_det2.space_before = Pt(1)
        p_det2.text = f"  • Ubuntu:  {lnx.replace(chr(10), '  |  ')}"
        p_det2.font.name = 'Consolas'
        p_det2.font.size = Pt(8.5)
        p_det2.font.color.rgb = COLOR_LNX_ACCENT

    # -------------------------------------------------------------
    # SLIDE 11: Síntese Comparativa & Conclusões Técnicas
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "Síntese Comparativa e Conclusões Técnicas")

    sc1 = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(5.6), Inches(5.65))
    sc1.fill.solid()
    sc1.fill.fore_color.rgb = COLOR_WHITE
    sc1.line.color.rgb = COLOR_CARD_BORDER
    sc1.line.width = Pt(1)

    sctf1 = sc1.text_frame
    sctf1.word_wrap = True
    sctf1.margin_left = Inches(0.4)
    sctf1.margin_right = Inches(0.4)
    sctf1.margin_top = Inches(0.3)

    p_s1 = sctf1.paragraphs[0]
    p_s1.text = "Pontos de Convergência (Hardware x86-64)"
    p_s1.font.name = 'Segoe UI'
    p_s1.font.size = Pt(12.5)
    p_s1.font.bold = True
    p_s1.font.color.rgb = COLOR_NAVY
    p_s1.space_after = Pt(6)

    conv = [
        ("Paginação Multinível Universal", "Ambos os sistemas convergem para o esquema padrão de paginação de 4 níveis (com expansão para 5 níveis - PML5) imposto pelo hardware x86-64 moderno."),
        ("Eliminação da Segmentação Clássica", "Tanto Windows quanto Linux abandonaram a segmentação tradicional em benefício do Modelo Plano (Flat Model), reaproveitando apenas registradores especiais (GS/FS) para TLS e dados do núcleo."),
        ("Particionamento Variável Dinâmico", "Em ambos, o espaço virtual de usuário e kernel é particionado dinamicamente sob demanda, combinando gerenciadores de blocos com molduras fixas de 4 KB."),
        ("Compactação de Memória na RAM", "Ambos perceberam o gargalo de I/O em disco e implementaram compactação na RAM (Windows Memory Compression e Linux zRAM/zswap) antes de acionar o swap secundário.")
    ]
    for tit, dsc in conv:
        p_i = sctf1.add_paragraph()
        p_i.space_before = Pt(4)
        p_i.text = f"• {tit}: "
        p_i.font.name = 'Segoe UI'
        p_i.font.size = Pt(9.5)
        p_i.font.bold = True
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        r = p_i.add_run()
        r.text = dsc
        r.font.bold = False
        r.font.color.rgb = COLOR_TEXT_MAIN

    sc2 = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), Inches(1.3), Inches(5.6), Inches(5.65))
    sc2.fill.solid()
    sc2.fill.fore_color.rgb = COLOR_WHITE
    sc2.line.color.rgb = COLOR_CARD_BORDER
    sc2.line.width = Pt(1)

    sctf2 = sc2.text_frame
    sctf2.word_wrap = True
    sctf2.margin_left = Inches(0.4)
    sctf2.margin_right = Inches(0.4)
    sctf2.margin_top = Inches(0.3)

    p_s2 = sctf2.paragraphs[0]
    p_s2.text = "Divergências de Engenharia e Trade-offs"
    p_s2.font.name = 'Segoe UI'
    p_s2.font.size = Pt(12.5)
    p_s2.font.bold = True
    p_s2.font.color.rgb = COLOR_NAVY
    p_s2.space_after = Pt(6)

    div = [
        ("Substituição: Prioridades vs. MGLRU", "O Windows aposta fortemente no Working Set Trimming com Standby List hierarquizada em 8 prioridades e predição (SuperFetch). O Linux inova com o MGLRU, gerando histogramas multigeracionais de baixíssimo overhead computacional."),
        ("Arquitetura de Alocadores", "O Windows utiliza o Segment Heap com LFH categorizado em buckets de 16 KB no user-space. O Linux utiliza o Buddy System estrito de potências de 2 no kernel, SLUB para objetos, e arenas ptmalloc3 na glibc."),
        ("Tratamento de Exaustão Extrema", "Sob esgotamento completo de RAM e Swap, o Windows tende a degradar o sistema sob 'thrashing' e negar alocações com erro; o Linux aciona o agressivo OOM Killer para abortar o processo com maior oom_score e restaurar a estabilidade do sistema."),
        ("Conclusão Geral", "O Windows prioriza suavidade interativa de desktop e compatibilidade retroativa; o Ubuntu prioriza vazão contínua de processamento, eficiência em contêineres e escalabilidade em servidores.")
    ]
    for tit, dsc in div:
        p_i = sctf2.add_paragraph()
        p_i.space_before = Pt(4)
        p_i.text = f"• {tit}: "
        p_i.font.name = 'Segoe UI'
        p_i.font.size = Pt(9.5)
        p_i.font.bold = True
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        r = p_i.add_run()
        r.text = dsc
        r.font.bold = False
        r.font.color.rgb = COLOR_TEXT_MAIN

    # -------------------------------------------------------------
    # SLIDE 12: Referências Bibliográficas
    # -------------------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    add_header(slide12, "Referências Bibliográficas e Leituras Recomendadas")

    ref_card = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.65))
    ref_card.fill.solid()
    ref_card.fill.fore_color.rgb = COLOR_WHITE
    ref_card.line.color.rgb = COLOR_CARD_BORDER
    ref_card.line.width = Pt(1)

    rtf = ref_card.text_frame
    rtf.word_wrap = True
    rtf.margin_left = Inches(0.6)
    rtf.margin_top = Inches(0.4)

    p_r0 = rtf.paragraphs[0]
    p_r0.text = "REFERÊNCIAS CIENTÍFICAS E LIVROS TEXTO FUNDAMENTAIS"
    p_r0.font.name = 'Segoe UI'
    p_r0.font.size = Pt(13)
    p_r0.font.bold = True
    p_r0.font.color.rgb = COLOR_NAVY
    p_r0.space_after = Pt(12)

    refs = [
        ("SILBERSCHATZ, Abraham; GALVIN, Peter B.; GAGNE, Greg.", "Operating System Concepts (Conceitos de Sistemas Operacionais). 10. ed. Hoboken: John Wiley & Sons, 2018. [Capítulos 9 e 10: Memória Principal e Memória Virtual]."),
        ("TANENBAUM, Andrew S.; BOS, Herbert.", "Modern Operating Systems (Sistemas Operacionais Modernos). 4. ed. Boston: Pearson, 2015. [Capítulo 3: Gerenciamento de Memória]."),
        ("RUSSINOVICH, Mark E.; SOLOMON, David A.; IONESCU, Alex.", "Windows Internals, Part 1: System architecture, processes, threads, memory management, and more. 7. ed. Redmond: Microsoft Press, 2017. [Capítulo 5: Memory Management]."),
        ("LOVE, Robert.", "Linux Kernel Development. 3. ed. Upper Saddle River: Addison-Wesley, 2010. [Capítulo 12: Memory Management e Capítulo 15: The Page Cache and Page Writeback]."),
        ("BOVET, Daniel P.; CESATI, Marco.", "Understanding the Linux Kernel. 3. ed. Sebastopol: O'Reilly Media, 2005. [Capítulo 8: Memory Management]."),
        ("GORMAN, Mel.", "Understanding the Linux Virtual Memory Manager. Upper Saddle River: Prentice Hall, 2004. [Buddy System, SLAB Allocator, Page Reclaim e Swap]."),
        ("STALLINGS, William.", "Operating Systems: Internals and Design Principles. 9. ed. Harlow: Pearson, 2018. [Capítulo 7: Gerenciamento de Memória e Capítulo 8: Memória Virtual]."),
        ("LINUX KERNEL DOCUMENTATION.", "Multi-Gen LRU (MGLRU) Documentation (Kernel 6.8). Disponível em: <https://docs.kernel.org/admin-guide/mm/multigen_lru.html>.")
    ]

    for authors, book in refs:
        p_ref = rtf.add_paragraph()
        p_ref.space_before = Pt(4)
        p_ref.text = f"• {authors} "
        p_ref.font.name = 'Segoe UI'
        p_ref.font.size = Pt(9.5)
        p_ref.font.bold = True
        p_ref.font.color.rgb = COLOR_TEXT_MAIN

        r = p_ref.add_run()
        r.text = book
        r.font.bold = False
        r.font.color.rgb = COLOR_TEXT_MUTED

    prs.save(filepath)
    print(f"Presentation generated successfully at: {filepath}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Apresentacoes")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "Apresentacao_Estudo_de_Caso_Memoria.pptx")
    create_presentation(out_file)

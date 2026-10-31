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

    def add_header(slide, title_text, category_text="ESTUDO DE CASO: GERENCIAMENTO DE PROCESSOS"):
        # Header banner shape
        header_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        header_box.fill.solid()
        header_box.fill.fore_color.rgb = COLOR_NAVY
        header_box.line.color.rgb = COLOR_NAVY

        # Category text
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

        # Title text
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

        # Windows Card
        win_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, win_x, card_y, card_w, card_h)
        win_card.fill.solid()
        win_card.fill.fore_color.rgb = COLOR_WIN_BG
        win_card.line.color.rgb = COLOR_WIN_ACCENT
        win_card.line.width = Pt(1.5)

        # Ubuntu Card
        lnx_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, lnx_x, card_y, card_w, card_h)
        lnx_card.fill.solid()
        lnx_card.fill.fore_color.rgb = COLOR_LNX_BG
        lnx_card.line.color.rgb = COLOR_LNX_ACCENT
        lnx_card.line.width = Pt(1.5)

        # Fill Windows Text
        wtf = win_card.text_frame
        wtf.word_wrap = True
        wtf.margin_left = Inches(0.3)
        wtf.margin_right = Inches(0.3)
        wtf.margin_top = Inches(0.25)
        
        p0 = wtf.paragraphs[0]
        p0.text = "🪟 Windows 11 Pro (23H2 / 24H2)"
        p0.font.name = 'Segoe UI'
        p0.font.size = Pt(15)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_WIN_ACCENT

        for pt in win_points:
            p = wtf.add_paragraph()
            p.text = "• " + pt
            p.font.name = 'Segoe UI'
            p.font.size = Pt(10.5)
            p.font.color.rgb = COLOR_TEXT_MAIN
            p.space_after = Pt(4)

        if win_cmds:
            p_cmd_hdr = wtf.add_paragraph()
            p_cmd_hdr.text = "Comandos & Inspeção Prática:"
            p_cmd_hdr.font.name = 'Segoe UI'
            p_cmd_hdr.font.size = Pt(11)
            p_cmd_hdr.font.bold = True
            p_cmd_hdr.font.color.rgb = COLOR_NAVY
            p_cmd_hdr.space_before = Pt(6)

            for cmd in win_cmds:
                pc = wtf.add_paragraph()
                pc.text = "  > " + cmd
                pc.font.name = 'Consolas'
                pc.font.size = Pt(9.5)
                pc.font.color.rgb = RGBColor(10, 60, 120)
                pc.space_after = Pt(2)

        # Fill Linux Text
        ltf = lnx_card.text_frame
        ltf.word_wrap = True
        ltf.margin_left = Inches(0.3)
        ltf.margin_right = Inches(0.3)
        ltf.margin_top = Inches(0.25)

        lp0 = ltf.paragraphs[0]
        lp0.text = "🐧 Ubuntu 24.04 LTS (Kernel Linux 6.8)"
        lp0.font.name = 'Segoe UI'
        lp0.font.size = Pt(15)
        lp0.font.bold = True
        lp0.font.color.rgb = COLOR_LNX_ACCENT

        for pt in lnx_points:
            p = ltf.add_paragraph()
            p.text = "• " + pt
            p.font.name = 'Segoe UI'
            p.font.size = Pt(10.5)
            p.font.color.rgb = COLOR_TEXT_MAIN
            p.space_after = Pt(4)

        if lnx_cmds:
            p_cmd_hdr = ltf.add_paragraph()
            p_cmd_hdr.text = "Comandos & Inspeção Prática:"
            p_cmd_hdr.font.name = 'Segoe UI'
            p_cmd_hdr.font.size = Pt(11)
            p_cmd_hdr.font.bold = True
            p_cmd_hdr.font.color.rgb = RGBColor(140, 40, 10)
            p_cmd_hdr.space_before = Pt(6)

            for cmd in lnx_cmds:
                pc = ltf.add_paragraph()
                pc.text = "  $ " + cmd
                pc.font.name = 'Consolas'
                pc.font.size = Pt(9.5)
                pc.font.color.rgb = RGBColor(120, 30, 0)
                pc.space_after = Pt(2)

    # ==========================================
    # SLIDE 1: CAPA
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_NAVY
    bg1.line.fill.background()

    # Title Box
    tbox = slide1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(10.933), Inches(4.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "UNIVERSIDADE FEDERAL RURAL DE PERNAMBUCO | DEPARTAMENTO DE COMPUTAÇÃO"
    p_badge.font.name = 'Segoe UI'
    p_badge.font.size = Pt(12)
    p_badge.font.bold = True
    p_badge.font.color.rgb = RGBColor(160, 200, 245)
    p_badge.space_after = Pt(14)

    p_main = tf1.add_paragraph()
    p_main.text = "Estudo de Caso:\nGerenciamento de Processos"
    p_main.font.name = 'Segoe UI'
    p_main.font.size = Pt(36)
    p_main.font.bold = True
    p_main.font.color.rgb = COLOR_WHITE
    p_main.space_after = Pt(14)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Análise Comparativa Aprofundada: Windows 11 Pro (23H2/24H2) vs. Ubuntu 24.04 LTS (Kernel 6.8)"
    p_sub.font.name = 'Segoe UI'
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = RGBColor(220, 230, 245)
    p_sub.space_after = Pt(30)

    p_info = tf1.add_paragraph()
    p_info.text = "Dupla: Luiz Maranhão & Mário Jorge\nProfessor: Dr. Douglas Véras | Disciplina: Sistemas Operacionais (BCC)"
    p_info.font.name = 'Segoe UI'
    p_info.font.size = Pt(14)
    p_info.font.color.rgb = RGBColor(180, 210, 240)

    # ==========================================
    # SLIDE 2: SUMÁRIO / ROTEIRO
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Roteiro da Apresentação & Agenda", "ESTRUTURA DA ANÁLISE")

    box2 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.5), Inches(10.933), Inches(5.2))
    box2.fill.solid()
    box2.fill.fore_color.rgb = RGBColor(250, 252, 255)
    box2.line.color.rgb = COLOR_CARD_BORDER
    tf2 = box2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = Inches(0.6)
    tf2.margin_top = Inches(0.4)

    agenda_items = [
        ("01. Introdução ao Gerenciamento de Processos", "Fundamentos de concorrência, o papel do SO e a abstração do Bloco de Controle de Processo (PCB)."),
        ("02. Identificação e Modelagem Interna", "Como Windows (EPROCESS/PEB) e Linux (task_struct//proc) armazenam e organizam processos no kernel."),
        ("03. Ciclo de Vida, Estados e Threads", "Diagramas de estados de transição, modelo 1:1 nativo e despachamento de tarefas leves."),
        ("04. Estrutura Hierárquica e Agrupamento", "Job Objects do Windows vs. Árvore genealógica canônica do systemd e cgroups v2 no Linux."),
        ("05. Comunicação (IPC) e Sincronização", "Mecanismos de troca de mensagens, memória compartilhada, exclusão mútua e primitiva Futex."),
        ("06. Políticas de Escalonamento e Prioridades", "Múltiplas filas e Thread Director no Windows 11 vs. o novo escalonador EEVDF no Linux 6.8."),
        ("07. Tratamento de Impasses (Deadlocks) & Comandos", "Abordagem do Algoritmo do Avestruz, ferramentas diagnósticas (WCT, Lockdep) e comandos práticos.")
    ]

    p0 = tf2.paragraphs[0]
    p0.text = "Tópicos Abordados no Estudo de Caso:"
    p0.font.name = 'Segoe UI'
    p0.font.size = Pt(16)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_NAVY
    p0.space_after = Pt(12)

    for tit, desc in agenda_items:
        p = tf2.add_paragraph()
        p.text = f"{tit}: {desc}"
        p.font.name = 'Segoe UI'
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_after = Pt(6)

    # ==========================================
    # SLIDE 3: INTRODUÇÃO TEÓRICA
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Introdução ao Gerenciamento de Processos", "FUNDAMENTAÇÃO TEÓRICA")

    c1 = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
    c1.fill.solid()
    c1.fill.fore_color.rgb = RGBColor(245, 248, 253)
    c1.line.color.rgb = COLOR_SLATE
    tf_c1 = c1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = Inches(0.4)
    tf_c1.margin_top = Inches(0.3)

    p = tf_c1.paragraphs[0]
    p.text = "Conceito Central & Importância"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(10)

    intro_pts = [
        "Definição: Um processo é um programa em execução. Enquanto o programa é uma entidade passiva (armazenada em disco), o processo é uma entidade ativa com espaço de endereçamento, contador de programa (PC), registradores e recursos associados.",
        "Multiplexação de Recursos: O SO gerencia o compartilhamento justo da CPU e periféricos entre múltiplos processos concorrentes através de preempção e fatias de tempo (quantuns).",
        "Proteção e Isolamento: Cada processo executa em seu próprio espaço de memória virtual privado protegido pela MMU (Memory Management Unit). Nenhum processo de usuário comum pode corromper a memória de outro ou do kernel.",
        "Eficiência e Throughput: O escalonador equilibra interatividade para tarefas do usuário com alto rendimento para rotinas de processamento em segundo plano."
    ]
    for pt in intro_pts:
        p_pt = tf_c1.add_paragraph()
        p_pt.text = "• " + pt
        p_pt.font.name = 'Segoe UI'
        p_pt.font.size = Pt(10.5)
        p_pt.font.color.rgb = COLOR_TEXT_MAIN
        p_pt.space_after = Pt(8)

    c2 = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), Inches(1.4), Inches(5.6), Inches(5.4))
    c2.fill.solid()
    c2.fill.fore_color.rgb = RGBColor(245, 248, 253)
    c2.line.color.rgb = COLOR_SLATE
    tf_c2 = c2.text_frame
    tf_c2.word_wrap = True
    tf_c2.margin_left = Inches(0.4)
    tf_c2.margin_top = Inches(0.3)

    p = tf_c2.paragraphs[0]
    p.text = "O Bloco de Controle de Processo (PCB)"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(10)

    pcb_pts = [
        "Papel Vital: Estrutura de dados primordial do kernel que atua como 'identidade' e registro histórico do processo.",
        "Comutação de Contexto (Context Switch): Ao alternar entre processos, o SO salva os registradores e estado do processo atual no PCB e restaura o estado do novo processo a executar.",
        "Componentes Típicos de um PCB:\n  - Identificador Único: PID e PPID (processo pai).\n  - Estado do Processo: Pronto, Executando, Bloqueado, etc.\n  - Contador de Programa e Registradores de Hardware.\n  - Informações de Escalonamento: Prioridade, quantum e ponteiros de filas.\n  - Gerenciamento de Memória: Tabelas de páginas e limites de memória.\n  - Descritores de Recursos: Arquivos abertos, sockets e dispositivos de E/S."
    ]
    for pt in pcb_pts:
        p_pt = tf_c2.add_paragraph()
        p_pt.text = "• " + pt
        p_pt.font.name = 'Segoe UI'
        p_pt.font.size = Pt(10.5)
        p_pt.font.color.rgb = COLOR_TEXT_MAIN
        p_pt.space_after = Pt(8)

    # ==========================================
    # SLIDE 4: SISTEMAS COMPARADOS (VISÃO GERAL)
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Visão Geral dos Sistemas Operacionais Comparados", "CONTEXTO DOS ESTUDOS DE CASO")

    win_over = [
        "Versão Analisada: Windows 11 Pro 64-bit (Edições 23H2 / 24H2 - Kernel NT 10.0).",
        "Paradigma de Kernel: Microkernel híbrido aperfeiçoado. O núcleo executivo opera em modo privilegiado (Ring 0) com drivers e subsistemas gráficos (win32k.sys).",
        "Unidade Fundamental de Escalonamento: Threads (ETHREAD/KTHREAD). O processo é apenas um contêiner de recursos e memória.",
        "Foco Arquitetural: Alta interatividade na interface gráfica (GUI), compatibilidade retroativa com aplicações Win32/Win64 e suporte avançado a hardware heterogêneo."
    ]
    lnx_over = [
        "Versão Analisada: Ubuntu 24.04 LTS ('Noble Numbat' - Kernel Linux 6.8).",
        "Paradigma de Kernel: Kernel Monolítico Modular. Todo o gerenciamento de processos, memória e drivers é executado no espaço de kernel (Ring 0) com suporte a módulos dinâmicos (LKM).",
        "Unidade Fundamental de Escalonamento: Tarefas (task_struct). O kernel unifica processos e threads sob o conceito de tarefas leves (LWP).",
        "Foco Arquitetural: Alto desempenho em servidores e contêineres, controle fino via linha de comando, previsibilidade e novo escalonador EEVDF."
    ]
    add_comparison_cards(slide4, win_over, lnx_over)

    # ==========================================
    # SLIDE 5: INFORMAÇÕES E MODELAGEM DOS PROCESSOS
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "1. Informações e Modelagem dos Processos", "ESTRUTURAS INTERNAS DO KERNEL")

    win_m5 = [
        "Abstração em 3 Níveis:\n  - KPROCESS (Kernel Layer): Ponteiro para diretório de páginas (CR3), afinidade de CPU e tempo de execução.\n  - EPROCESS (Executive Layer): Bloco PCB principal contendo PID, Token de Segurança, lista de handles de recursos e estatísticas.\n  - PEB (User Space): Process Environment Block acessível em modo usuário com variáveis de ambiente e DLLs carregadas.",
        "Organização: Unida pela lista circular duplamente encadeada global ActiveProcessLinks no kernel.",
        "Tokens de Segurança: Cada processo carrega um token com SID do usuário e privilégios associados."
    ]
    win_c5 = [
        "Get-Process -Id <PID> | Format-List *",
        "tasklist /v /fo list",
        "WinDbg: !process 0 0 | dt nt!_EPROCESS"
    ]
    lnx_m5 = [
        "A Estrutura Unificada struct task_struct (<linux/sched.h>):\n  - PID (Identificador do processo) e PPID (processo pai).\n  - TGID (Thread Group ID): Compartilhado por todas as threads de um mesmo processo.\n  - mm_struct: Descreve o espaço de memória virtual privado.\n  - files_struct: Tabela de descritores de arquivos abertos.",
        "Organização: Lista circular duplamente encadeada task_list + Tabela Hash pid_hash para localização instantânea O(1).",
        "Pseudo-Sistema /proc: Projeção direta das estruturas do kernel no VFS (ex.: /proc/<PID>/status e /proc/<PID>/maps)."
    ]
    lnx_c5 = [
        "cat /proc/<PID>/status | head -n 20",
        "ps aux --sort=-%cpu | head -n 10",
        "ls -l /proc/<PID>/fd (descritores abertos)"
    ]
    add_comparison_cards(slide5, win_m5, lnx_m5, win_c5, lnx_c5)

    # ==========================================
    # SLIDE 6: ESTADOS E TRANSIÇÕES POSSÍVEIS
    # ==========================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "2. Estados e Transições de Processos", "CICLO DE VIDA DE EXECUÇÃO")

    win_m6 = [
        "O Windows opera com 8 estados formais aplicados às THREADS:\n  1. Initialized: Thread em alocação inicial de memória.\n  2. Ready: Pronta para execução, aguardando alocação de CPU.\n  3. Standby: Selecionada para ser a próxima a executar em um núcleo específico.\n  4. Running: Atualmente em execução na CPU.\n  5. Waiting: Bloqueada aguardando evento, E/S ou objeto sincronizador.\n  6. Transition: Pronta, mas suas páginas de pilha de kernel foram paginadas.\n  7. Terminated: Execução concluída, aguardando liberação do handle.\n  8. DeferredReady: Otimização de despacho de fila em nós NUMA.",
        "Transição Direta: Ready -> Standby -> Running -> Waiting -> Ready."
    ]
    win_c6 = [
        "resmon.exe (Aba CPU -> Processos: Em Execução/Suspenso)",
        "System Informer: Aba Threads -> Coluna 'State' (Running/Wait)",
        "Get-Process | Select Id, ProcessName, Responding"
    ]
    lnx_m6 = [
        "Estados Canônicos da task_struct (Campo 'state'):\n  1. TASK_RUNNING (R): Executando na CPU ou pronta na fila de execução.\n  2. TASK_INTERRUPTIBLE (S): Bloqueada/dormindo aguardando recurso; acorda se receber um sinal POSIX.\n  3. TASK_UNINTERRUPTIBLE (D): Espera crítica em hardware (ex.: E/S síncrona); imune a sinais (inclusive kill -9) até que a E/S termine.\n  4. TASK_STOPPED (T): Pausada por sinal explícito (SIGSTOP / Ctrl+Z).\n  5. TASK_TRACED (t): Pausada para inspeção por depurador (gdb/ptrace).\n  6. EXIT_ZOMBIE (Z): Processo morto cujo pai ainda não chamou wait().\n  7. EXIT_DEAD (X): Estado final de destruição no kernel."
    ]
    lnx_c6 = [
        "ps -eo pid,stat,comm (Coluna STAT: R, S, D, T, Z)",
        "kill -STOP <PID> (força pausa em estado T)",
        "kill -CONT <PID> (retoma execução para estado R)"
    ]
    add_comparison_cards(slide6, win_m6, lnx_m6, win_c6, lnx_c6)

    # ==========================================
    # SLIDE 7: TIPO DE THREADS
    # ==========================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "3. Tipo de Threads e Concorrência", "MODELO DE THREADS & PARALELISMO")

    win_m7 = [
        "Modelo 1:1 Nativo (Kernel-Level Threads):\n  - No Windows NT, a thread (ETHREAD/KTHREAD) é a única entidade escalonada.\n  - Cada thread do espaço de usuário possui sua contraparte no kernel com pilha de kernel dedicada (Kernel Stack).\n  - O chaveamento de contexto é realizado em Ring 0.",
        "API de Fibras (Fibers - Modelo M:N cooperativo):\n  - Suporte legado no user mode via ConvertThreadToFiber e SwitchToFiber.\n  - Escalonamento cooperativo sem interrupção do kernel, útil historicamente em bancos de dados (ex.: SQL Server), mas raramente empregado hoje.",
        "Thread Pool da API Win32: Gerenciamento eficiente de pools de threads pelo executivo para evitar custo de criação contínua."
    ]
    win_c7 = [
        "(Get-Process -Id <PID>).Threads.Count",
        "Process Explorer -> Propriedades -> Aba Threads",
        "resmon.exe -> Monitor de Recursos -> Contadores de Threads"
    ]
    lnx_m7 = [
        "Modelo 1:1 Nativo via NPTL (Native POSIX Thread Library):\n  - O Linux implementa threads como Lightweight Processes (LWPs).\n  - Não há estrutura 'thread' separada no kernel: threads e processos utilizam a mesma struct task_struct.\n  - Criação via clone() com flags: CLONE_VM (mesma memória), CLONE_FILES, CLONE_FS e CLONE_SIGHAND.",
        "TGID (Thread Group ID) vs. TID (Thread ID):\n  - Para o kernel, cada LWP possui um TID próprio e independente.\n  - Para o usuário, a função getpid() retorna o TGID (o PID da thread líder).\n  - Suporte total ao padrão POSIX Threads (pthreads)."
    ]
    lnx_c7 = [
        "ps -eLf | grep <processo> (coluna LWP)",
        "top -H -p <PID> (modo de visualização por threads)",
        "ls /proc/<PID>/task/ (lista os TIDs de cada thread)"
    ]
    add_comparison_cards(slide7, win_m7, lnx_m7, win_c7, lnx_c7)

    # ==========================================
    # SLIDE 8: HIERARQUIA E AGRUPAMENTO DE PROCESSOS
    # ==========================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "4. Hierarquia e Agrupamento de Processos", "RELAÇÃO PAI-FILHO & ISOLAMENTO")

    win_m8 = [
        "Sem Árvore Rígida de Dependência no Kernel:\n  - O Windows grava o 'Creator/Parent Process ID' apenas na criação.\n  - Se o processo pai encerra, o processo filho continua sua execução de forma completamente autônoma, sem necessidade de adoção (reparenting).\n  - Árvores mostradas em ferramentas como Process Explorer são inferências baseadas no ID do criador enquanto ativo.",
        "Agrupamento Avançado via Job Objects:\n  - Objeto do kernel projetado para agregar processos relacionados.\n  - Permite impor limites compartilhados: cota global de CPU, limite máximo de memória de trabalho (Working Set) e encerramento em cascata.\n  - Base tecnológica para Windows Containers e isolamento de guias em navegadores modernos (Edge, Chrome)."
    ]
    win_c8 = [
        "Get-CimInstance Win32_Process | Select ProcessId, ParentProcessId, Name",
        "Process Explorer -> View -> Tree View",
        "Sysinternals JobObject: TestLimit.exe / Process Hacker"
    ]
    lnx_m8 = [
        "Hierarquia Estrita em Árvore Genealógica:\n  - Todo processo nasce de uma chamada fork() ou clone(), gerando uma árvore com raiz canônica no PID 1 (systemd).\n  - Reparenting Automático: Se um processo pai morre antes do filho (gerando um processo órfão), o kernel reatribui o órfão imediatamente ao PID 1 ou a um subreaper (PR_SET_CHILD_SUBREAPER) para garantir o recolhimento de status via wait().",
        "Agrupamentos Nativos:\n  - Process Groups (PGID): Agrupam processos de uma mesma sessão/pipeline para controle de jobs no terminal.\n  - Sessions (SID): Associadas a terminais de controle de login.\n  - Control Groups v2 (cgroups): Hierarquia unificada para controle e limitação rígida de CPU, RAM, I/O e rede."
    ]
    lnx_c8 = [
        "pstree -p (exibe árvore genealógica completa)",
        "ps -ef --forest (árvore formatada em ASCII)",
        "systemd-cgls (árvore de cgroups v2 do systemd)"
    ]
    add_comparison_cards(slide8, win_m8, lnx_m8, win_c8, lnx_c8)

    # ==========================================
    # SLIDE 9: COMUNICAÇÃO DE PROCESSOS (IPC)
    # ==========================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "5. Comunicação entre Processos (IPC)", "TROCA DE MENSAGENS E DADOS")

    win_m9 = [
        "Mecanismos Disponíveis no Windows:\n  1. ALPC (Advanced Local Procedure Calls): IPC interno de altíssima velocidade para troca de mensagens entre processos de usuário e subsistemas centrais (ex.: csrss.exe, lsass.exe).\n  2. Named Pipes: Comunicação bidirecional local e em rede (via protocolo SMB/CIFS).\n  3. Anonymous Pipes: Comunicação unidirecional entre processos com parentesco.\n  4. Memory-Mapped Files (Section Objects): O mecanismo mais veloz; mapeia páginas físicas de RAM diretamente no espaço virtual de múltiplos processos.\n  5. Winsock: Sockets de rede e loopback.\n  6. COM/DCOM e RPC: Chamadas de procedimentos remotos orientadas a objetos."
    ]
    win_c9 = [
        "Get-ChildItem \\\\.\\pipe\\ (listar Named Pipes no PowerShell)",
        "pipelist.exe (ferramenta Sysinternals)",
        "tcpview.exe (monitor de sockets e tráfego local)"
    ]
    lnx_m9 = [
        "Mecanismos Disponíveis no Linux (POSIX & System V):\n  1. Pipes Anônimos (|): Buffers de kernel unidirecionais entre processos pai e filho.\n  2. FIFOs (Named Pipes): Criados no VFS com mkfifo para processos independentes.\n  3. Sinais POSIX: Mensagens assíncronas de controle (SIGINT, SIGTERM, SIGKILL).\n  4. Memória Compartilhada: Implementações POSIX (shm_open, mmap) e System V (shmget) mapeadas em RAM de alta velocidade sob /dev/shm (tmpfs).\n  5. Filas de Mensagens e Semáforos IPC (POSIX e System V).\n  6. Unix Domain Sockets: Comunicação bidirecional ultrarrápida via sistema de arquivos.\n  7. D-Bus: Barramento de mensagens corporativo para serviços de sistema."
    ]
    lnx_c9 = [
        "ipcs -a (relatório completo de IPC: memória, semáforos, filas)",
        "ls -la /dev/shm (inspecionar segmentos de memória compartilhada)",
        "ss -x (listar todos os Unix Domain Sockets ativos)"
    ]
    add_comparison_cards(slide9, win_m9, lnx_m9, win_c9, lnx_c9)

    # ==========================================
    # SLIDE 10: EXCLUSÃO MÚTUA (SINCRONIZAÇÃO)
    # ==========================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "6. Sincronização e Exclusão Mútua", "PROTEÇÃO DE SEÇÕES CRÍTICAS")

    win_m10 = [
        "Primitivas de Kernel (Dispatcher Objects):\n  - Mutexes (Mutants): Sincronização interprocessos com suporte a detecção de abandono (se a thread morre, a trava é liberada com código especial).\n  - Semáforos: Controlam acesso concorrente limitado a um pool de recursos.\n  - Eventos (Manual e Auto-Reset): Mecanismo de notificação de conclusão de tarefas.",
        "Primitivas no Espaço do Usuário (User-Mode Locks):\n  - Critical Sections: Otimizadas para intra-processos; executam spinlock breve antes de acionar chamada de sistema no kernel.\n  - Slim Reader/Writer (SRW) Locks: Extremamente leves (tamanho de um ponteiro), sem alocação de objetos no kernel, suportando leituras concorrentes."
    ]
    win_c10 = [
        "WinDbg: !locks (inspecionar travas no kernel)",
        "Process Explorer: Handles -> Filtrar por 'Mutant' / 'Semaphore'",
        "System Informer: Visualização de Synchronization Handles"
    ]
    lnx_m10 = [
        "Primitivas no Kernel (Kernel Space):\n  - Mutexes (struct mutex): Travas com bloqueio e suspensão de tarefa.\n  - Spinlocks (spinlock_t): Espera ativa (busy-waiting) usada em código de interrupção (ISR) onde a tarefa não pode dormir.\n  - RCU (Read-Copy-Update): Leituras atômicas quase com custo zero de sincronização; essencial para alta performance em redes e VFS.",
        "Primitivas no Espaço do Usuário via Futex:\n  - Futex (Fast Userspace Mutex): Abordagem híbrida inovadora. A trava e liberação sem colisão ocorrem 100% no registrador da CPU via instruções atômicas (CAS). O kernel só é invocado por syscall se houver contenção real.\n  - Base de suporte para pthread_mutex_t e sem_t."
    ]
    lnx_c10 = [
        "lslocks (lista todas as travas ativas de arquivos do sistema)",
        "cat /proc/locks (locks mantidos pelo kernel)",
        "valgrind --tool=helgrind ./programa (detector de data races)"
    ]
    add_comparison_cards(slide10, win_m10, lnx_m10, win_c10, lnx_c10)

    # ==========================================
    # SLIDE 11: PRIORIDADES DE UM PROCESSO
    # ==========================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "7. Prioridades e Níveis de Escalonamento", "POLÍTICAS DE PREFERÊNCIA DE CPU")

    win_m11 = [
        "Escala de 32 Níveis (0 a 31):\n  - Nível 0: Zero-page thread (limpeza de páginas de RAM em repouso).\n  - Níveis 1 a 15: Prioridades Dinâmicas (aplicações normais do usuário e serviços).\n  - Níveis 16 a 31: Prioridades de Tempo Real (Real-Time, imunes a preempção por processos comuns).",
        "Classes de Prioridade Win32:\n  - Idle (4), Below Normal (6), Normal (8), Above Normal (10), High (13) e Realtime (24).",
        "Dynamic Priority Boost:\n  - Aumento temporário de prioridade para threads com foco de janela (Foreground Boost), ao despertar de operações de E/S ou para evitar starvation (Balance Set Manager)."
    ]
    win_c11 = [
        "(Get-Process -Name notepad).PriorityClass = 'High'",
        "start /high notepad.exe",
        "taskmgr -> Detalhes -> Definir prioridade (Tempo Real, Alta, etc.)"
    ]
    lnx_m11 = [
        "Esquema de 140 Níveis de Prioridade no Kernel:\n  - Prioridades 0 a 99 (Tempo Real - POSIX RT): Políticas SCHED_FIFO e SCHED_RR. Precedem qualquer processo comum de tempo compartilhado.\n  - Prioridades 100 a 139 (Normal / Time-Sharing): Gerenciadas pelo escalonador CFS/EEVDF (SCHED_OTHER, SCHED_BATCH).",
        "Escala Nice (Espaço do Usuário):\n  - Faixa de -20 (máxima prioridade / menos tolerante) a +19 (mínima prioridade / mais gentil).\n  - O valor nice padrão 0 corresponde à prioridade 120 no kernel.\n  - Apenas o superusuário (root) pode atribuir nice negativo."
    ]
    lnx_c11 = [
        "ps -eo pid,ni,pri,rtprio,comm (exibe Nice e Prioridade)",
        "nice -n -10 ./app (inicia com prioridade elevada via sudo)",
        "renice -n 5 -p <PID> (ajusta prioridade de processo ativo)",
        "sudo chrt -f -p 50 <PID> (define política SCHED_FIFO em tempo real)"
    ]
    add_comparison_cards(slide11, win_m11, lnx_m11, win_c11, lnx_c11)

    # ==========================================
    # SLIDE 12: ALGORITMO DE ESCALONAMENTO
    # ==========================================
    slide12 = prs.slides.add_slide(blank_layout)
    add_header(slide12, "8. Algoritmos de Escalonamento de Processos", "LÓGICA DO DESPACHANTE DE CPU")

    win_m12 = [
        "Escalonador Preemptivo por Prioridades com Múltiplas Filas:\n  - A thread pronta de maior prioridade sempre assume a CPU imediatamente.\n  - Threads de mesma prioridade compartilham a CPU em rodízio (Round-Robin) controlado por Quantum de tempo.",
        "Quantum Configurável:\n  - Versões Desktop (Windows 11): Quantums curtos (~30ms) otimizados para responsividade imediata na interface gráfica.\n  - Versões Server: Quantums longos (~120ms) para maximizar o rendimento (throughput).",
        "Escalonamento Heterogêneo (Intel Thread Director):\n  - O Windows 11 classifica as threads e direciona tarefas de alto desempenho/foco para núcleos de Performance (P-cores) e tarefas de fundo para núcleos de Eficiência (E-cores)."
    ]
    win_c12 = [
        "sysdm.cpl -> Avançado -> Desempenho -> Configurações -> Avançado",
        "powercfg /qh (inspecionar políticas de heterogeneidade de CPU)",
        "WinDbg: !sched (analisa estado do escalonador do kernel)"
    ]
    lnx_m12 = [
        "O Novo Escalonador EEVDF (Earliest Eligible Virtual Deadline First):\n  - Oficializado no Linux 6.6 e integrado ao Ubuntu 24.04 LTS (Kernel 6.8), sucedendo o clássico CFS (Completely Fair Scheduler).\n  - Princípio do EEVDF: Desacopla 'elegibilidade' (se a tarefa já usou sua cota proporcional de CPU) de 'deadline virtual' (urgência temporal da tarefa).\n  - Garante latência ultrabaixa para tarefas interativas sem necessidade de recorrer a privilégios de tempo real.",
        "Políticas de Tempo Real POSIX:\n  - SCHED_FIFO (executa continuamente até ceder a CPU ou sofrer preempção por prioridade superior).\n  - SCHED_RR (rodízio com fatias de tempo em tempo real).\n  - SCHED_DEADLINE (Earliest Deadline First para tarefas periódicas duras)."
    ]
    lnx_c12 = [
        "chrt -m (lista todas as políticas suportadas pelo kernel)",
        "cat /proc/sys/kernel/sched_* (parâmetros de ajuste do EEVDF)",
        "sudo perf sched record -- sleep 2 && sudo perf sched latency"
    ]
    add_comparison_cards(slide12, win_m12, lnx_m12, win_c12, lnx_c12)

    # ==========================================
    # SLIDE 13: TRATAMENTO DE DEADLOCKS
    # ==========================================
    slide13 = prs.slides.add_slide(blank_layout)
    add_header(slide13, "9. Tratamento de Impasses (Deadlocks)", "ESTRATÉGIAS DE DETECÇÃO & PREVENÇÃO")

    win_m13 = [
        "Adoção do Algoritmo do Avestruz (Ostrich Algorithm):\n  - O Windows não executa prevenção ou resolução automática para impasses entre processos normais de usuário em tempo de execução, dado o overhead proibitivo de algoritmos como o Banqueiro.\n  - A intervenção manual pelo usuário ou encerramento do processo é a abordagem padrão.",
        "Tecnologias Avançadas de Diagnóstico:\n  - Wait Chain Traversal (WCT): API integrada ao Windows que analisa nós de dependência entre threads (COM, ALPC, Critical Sections) e detecta deadlocks explicitamente.\n  - Driver Verifier (verifier.exe): Mecanismo do kernel que monitora locks e spinlocks de drivers para evitar deadlocks catastróficos que causariam tela azul (BSOD)."
    ]
    win_c13 = [
        "resmon.exe -> Botão direito no processo -> 'Analisar Cadeia de Espera'",
        "taskkill /F /PID <PID> (eliminação forçada do processo em impasse)",
        "verifier.exe (configuração de módulo Deadlock Detection em drivers)"
    ]
    lnx_m13 = [
        "Adoção do Algoritmo do Avestruz no Espaço de Usuário:\n  - Aplicações de usuário em deadlock não são interrompidas automaticamente pelo kernel; o administrador deve enviar sinais de término.",
        "Mecanismos de Prevenção e Diagnóstico no Kernel:\n  - Lockdep (Lock Dependency Validator): Validador no kernel que mapeia grafos de aquisição de travas e alerta no log do sistema (dmesg) antes que um deadlock cíclico ocorra (ordenação de locks).\n  - Hung Task Detector: Componente do kernel que detecta processos travados no estado D (TASK_UNINTERRUPTIBLE) por mais de 120s e emite alertas com call trace completo.\n  - Ferramentas de Profiling: Valgrind (Helgrind/DRD) para depuração de concorrência em tempo de código."
    ]
    lnx_c13 = [
        "kill -9 <PID> / pkill -9 -f <nome> (sinal SIGKILL irrecusável)",
        "dmesg | grep -i \"blocked for more than\" (alerta de hung task)",
        "gdb -p <PID> -> thread apply all bt (analisar call stack das threads)"
    ]
    add_comparison_cards(slide13, win_m13, lnx_m13, win_c13, lnx_c13)

    # ==========================================
    # SLIDE 14: QUADRO DE COMANDOS COMPARATIVO
    # ==========================================
    slide14 = prs.slides.add_slide(blank_layout)
    add_header(slide14, "Quadro Prático: Comandos de Gerenciamento", "GUIA OPERACIONAL COMPARADO")

    tbl_shape = slide14.shapes.add_table(7, 3, Inches(0.8), Inches(1.4), Inches(11.733), Inches(5.2))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(2.7)
    tbl.columns[1].width = Inches(4.5)
    tbl.columns[2].width = Inches(4.533)

    col_headers = ["Ação / Objetivo", "🪟 Windows 11 Pro (CLI & GUI)", "🐧 Ubuntu 24.04 LTS (CLI & GUI)"]
    for i, h in enumerate(col_headers):
        cell = tbl.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = 'Segoe UI'
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    cmd_rows = [
        ("Listar Processos Ativos", "Get-Process | Sort CPU -Desc\ntasklist /v\nGUI: Task Manager (Aba Detalhes)", "ps aux\nps -ef\nGUI: gnome-system-monitor"),
        ("Monitoramento Interativo", "resmon.exe (Resource Monitor)\nProcess Explorer (Sysinternals)", "top (pressionar 'c', 'M')\nhtop (F6 ordenar, F4 filtrar)"),
        ("Inspeção de Threads", "(Get-Process -Id <PID>).Threads\nProcess Explorer -> Aba Threads", "ps -eLf | grep <PID>\ntop -H -p <PID>\nls /proc/<PID>/task/"),
        ("Visualizar Hierarquia", "Get-CimInstance Win32_Process\nProcess Explorer (Árvore de Processos)", "pstree -p\nps -ef --forest\nsystemd-cgls"),
        ("Alterar Prioridade", "(Get-Process).PriorityClass = 'High'\nwmic process setpriority\nGUI: Task Manager -> Definir Prioridade", "nice -n -10 ./app\nrenice -n 5 -p <PID>\nsudo chrt -f -p 50 <PID>"),
        ("Finalizar / Matar Processo", "Stop-Process -Id <PID> -Force\ntaskkill /F /PID <PID>\nGUI: Task Manager -> Finalizar Tarefa", "kill -9 <PID>\npkill -9 <nome>\nkillall <nome>")
    ]

    for r_idx, row in enumerate(cmd_rows, start=1):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(250, 252, 255) if r_idx % 2 == 0 else RGBColor(240, 245, 252)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = 'Consolas' if c_idx > 0 else 'Segoe UI'
            p.font.size = Pt(9) if c_idx > 0 else Pt(10)
            p.font.bold = (c_idx == 0)
            p.font.color.rgb = COLOR_NAVY if c_idx == 0 else COLOR_TEXT_MAIN

    # ==========================================
    # SLIDE 15: CONCLUSÕES E SÍNTESE
    # ==========================================
    slide15 = prs.slides.add_slide(blank_layout)
    add_header(slide15, "Síntese Comparativa e Conclusões", "CONSIDERAÇÕES FINAIS")

    c_left = slide15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = RGBColor(245, 248, 253)
    c_left.line.color.rgb = COLOR_WIN_ACCENT
    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = Inches(0.4)
    tf_l.margin_top = Inches(0.3)

    p = tf_l.paragraphs[0]
    p.text = "Convergências Arquiteturais"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(10)

    conv_pts = [
        "Unidade Fundamental de Execução: Ambos os sistemas convergem para o modelo 1:1 nativo (Kernel-Level Threads), despachando threads diretamente nos núcleos de CPU.",
        "Proteção de Memória: Ambos utilizam isolamento de espaço de endereçamento virtual baseado em paginação de hardware (MMU) com separação rígida entre User Mode (Ring 3) e Kernel Mode (Ring 0).",
        "Tratamento Pragmático de Deadlocks: Ambos adotam o Algoritmo do Avestruz para aplicações normais de usuário, priorizando desempenho em tempo de execução e fornecendo ferramentas de diagnóstico sob demanda."
    ]
    for pt in conv_pts:
        p_pt = tf_l.add_paragraph()
        p_pt.text = "✔ " + pt
        p_pt.font.name = 'Segoe UI'
        p_pt.font.size = Pt(10.5)
        p_pt.font.color.rgb = COLOR_TEXT_MAIN
        p_pt.space_after = Pt(8)

    c_right = slide15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), Inches(1.4), Inches(5.6), Inches(5.4))
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = RGBColor(255, 248, 245)
    c_right.line.color.rgb = COLOR_LNX_ACCENT
    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = Inches(0.4)
    tf_r.margin_top = Inches(0.3)

    p = tf_r.paragraphs[0]
    p.text = "Divergências e Filosofias de Projeto"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(140, 40, 10)
    p.space_after = Pt(10)

    div_pts = [
        "Hierarquia de Processos: O Linux impõe árvore canônica estrita enraizada no PID 1 com reparenting obrigatório, enquanto o Windows adota independência de processos filhos e agrupamento via Job Objects.",
        "Modelagem do PCB: O Windows divide a abstração em múltiplas camadas (KPROCESS, EPROCESS, PEB), enquanto o Linux centraliza na macroestrutura task_struct projetada via VFS no /proc.",
        "Evolução do Escalonamento: O Windows 11 foca em otimizações para processadores heterogêneos (P/E cores com Thread Director), enquanto o Ubuntu 24.04 inova com o escalonador EEVDF focado em previsibilidade de latência virtual."
    ]
    for pt in div_pts:
        p_pt = tf_r.add_paragraph()
        p_pt.text = "⚡ " + pt
        p_pt.font.name = 'Segoe UI'
        p_pt.font.size = Pt(10.5)
        p_pt.font.color.rgb = COLOR_TEXT_MAIN
        p_pt.space_after = Pt(8)

    # ==========================================
    # SLIDE 16: REFERÊNCIAS
    # ==========================================
    slide16 = prs.slides.add_slide(blank_layout)
    add_header(slide16, "Referências Bibliográficas e Científicas", "EMBASAMENTO TÉCNICO")

    box_ref = slide16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.5), Inches(10.933), Inches(5.2))
    box_ref.fill.solid()
    box_ref.fill.fore_color.rgb = RGBColor(250, 252, 255)
    box_ref.line.color.rgb = COLOR_CARD_BORDER
    tf_ref = box_ref.text_frame
    tf_ref.word_wrap = True
    tf_ref.margin_left = Inches(0.6)
    tf_ref.margin_top = Inches(0.4)

    p0 = tf_ref.paragraphs[0]
    p0.text = "Literatura Acadêmica & Manuais Oficiais de Engenharia:"
    p0.font.name = 'Segoe UI'
    p0.font.size = Pt(16)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_NAVY
    p0.space_after = Pt(14)

    refs = [
        "1. SILBERSCHATZ, Abraham; GALVIN, Peter B.; GAGNE, Greg. Operating System Concepts. 10. ed. Hoboken: John Wiley & Sons, 2018.",
        "2. TANENBAUM, Andrew S.; BOS, Herbert. Sistemas Operacionais Modernos. 4. ed. São Paulo: Pearson, 2015.",
        "3. RUSSINOVICH, Mark E.; SOLOMON, David A.; IONESCU, Alex. Windows Internals: Part 1 - System architecture, processes, threads, memory management, and more. 7. ed. Redmond: Microsoft Press, 2017.",
        "4. LOVE, Robert. Linux Kernel Development. 3. ed. Boston: Addison-Wesley Professional, 2010.",
        "5. STALLINGS, William. Operating Systems: Internals and Design Principles. 9. ed. Boston: Pearson, 2018.",
        "6. HOON, Peter. EEVDF: Earliest Eligible Virtual Deadline First scheduling algorithm. IEEE Transactions on Real-Time Systems, 1995 (Implementação Kernel Linux 6.6+, 2023-2024).",
        "7. MICROSOFT LEARN. About Processes and Threads / Synchronization Primitives. Disponível em: <https://learn.microsoft.com/en-us/windows/win32/procthread/>. Acesso em: 2026."
    ]

    for r in refs:
        p = tf_ref.add_paragraph()
        p.text = r
        p.font.name = 'Segoe UI'
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_after = Pt(8)

    prs.save(filepath)
    print(f"Presentation saved successfully at: {filepath}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Apresentacoes")
    os.makedirs(out_dir, exist_ok=True)
    out_pptx = os.path.join(out_dir, "Apresentacao_Estudo_de_Caso_Processos.pptx")
    create_presentation(out_pptx)

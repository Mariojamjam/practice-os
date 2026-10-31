import xlsxwriter
import os

def create_comparative_spreadsheet(filepath):
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet("Estudo de Caso - Processos")
    
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
    worksheet.merge_range('A1:E1', 'ESTUDO DE CASO: GERENCIAMENTO DE PROCESSOS EM SISTEMAS OPERACIONAIS', title_fmt)
    worksheet.merge_range('A2:E2', 'Disciplina: Sistemas Operacionais | Prof. Dr. Douglas Véras | Alunos: Luiz Maranhão & Mário Jorge (UFRPE)', subtitle_fmt)
    worksheet.set_row(0, 24)
    worksheet.set_row(1, 18)

    headers = [
        "Sistema Operacional / Comparativo",
        "Windows 11 Pro (23H2 / 24H2)",
        "Windows 11 Pro – comandos (CLI ou passo-a-passo GUI)",
        "Ubuntu 24.04 LTS (Kernel Linux 6.8)",
        "Ubuntu 24.04 LTS – comandos (CLI ou passo-a-passo GUI)"
    ]

    worksheet.set_row(2, 35)
    for col_idx, h in enumerate(headers):
        worksheet.write(2, col_idx, h, header_fmt)

    data = [
        (
            "Informações de um processo",
            "No Windows, um processo é uma abstração do Executivo (objeto Process) que encapsula espaço de endereçamento virtual privado, código, dados e recursos.\n"
            "• Principais informações: PID (Process ID), Imagem executável, Session ID, Token de Segurança (credenciais e privilégios), Tabela de Handles (arquivos, portas, eventos), Working Set (páginas em RAM), Prioridade Base (0-31), Estatísticas de E/S, PEB (Process Environment Block) e Lista de Threads associadas.",
            "• CLI (PowerShell):\n"
            "  Get-Process -Id <PID> | Format-List *\n"
            "  Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Id, ProcessName, CPU, WorkingSet\n"
            "• CLI (CMD):\n"
            "  tasklist /v /fo list\n"
            "• GUI:\n"
            "  1. Ctrl + Shift + Esc (Gerenciador de Tarefas) -> Aba 'Detalhes' (clicar com botão direito no cabeçalho para adicionar colunas: PID, Usuário, Linha de Comando, Memória).\n"
            "  2. Sysinternals Process Explorer: Executar como Admin -> Duplo clique no processo -> Visualizar abas: Image, Performance, Threads, Handles, Security.",
            "No Linux, o processo é a representação de um programa em execução descrita pela estrutura task_struct no kernel.\n"
            "• Principais informações: PID (Process ID), PPID (Parent Process ID), TGID (Thread Group ID), Credenciais (UID, GID, eUID, eGID), Tabela de descritores de arquivos (files_struct), Mapa de memória virtual (mm_struct), Sinais pendentes/bloqueados, Prioridade dinâmica e estática (nice / rt_priority), Estado de execução e tempo de CPU (utime/stime).",
            "• CLI (Term):\n"
            "  ps aux | head -n 15\n"
            "  ps -ef --sort=-%cpu\n"
            "  cat /proc/<PID>/status\n"
            "  cat /proc/<PID>/cmdline\n"
            "  ls -l /proc/<PID>/fd (descritores abertos)\n"
            "• CLI Interativo:\n"
            "  top (pressionar 'c' para linhas de comando, 'M' para ordenar por RAM)\n"
            "  htop (F6 para ordenar, F4 para filtrar)\n"
            "• GUI:\n"
            "  gnome-system-monitor -> Aba 'Processos' -> Clique com botão direito no processo -> 'Propriedades'."
        ),
        (
            "Modelagem dos processos",
            "A modelagem no Windows é dividida em camadas:\n"
            "1. Kernel Layer: Estrutura KPROCESS (dados de baixo nível para despacho e hardware: ponteiro de diretório de tabelas de páginas - CR3, afinidade de CPU, lista de threads prontas).\n"
            "2. Executive Layer: Estrutura EPROCESS (Bloco de Controle de Processo - PCB principal), contendo ponteiros para KPROCESS, ActiveProcessLinks (lista duplamente encadeada circular unindo todos os processos ativos), cota de recursos, objeto de auditoria e lista de handles.\n"
            "3. User Space: PEB (Process Environment Block), acessível em modo usuário para carregar DLLs, parâmetros da linha de comando e variáveis de ambiente.",
            "• Depuração / Inspeção de Kernel:\n"
            "  WinDbg (Local Kernel Debug):\n"
            "  !process 0 0 (lista todos EPROCESS)\n"
            "  dt nt!_EPROCESS <endereço>\n"
            "  dt nt!_PEB @$peb\n"
            "• GUI:\n"
            "  Process Explorer -> View -> Show Lower Pane -> View Handles / DLLs para inspecionar componentes da modelagem e recursos alocados ao processo.",
            "O Linux utiliza o PCB consolidado na macroestrutura struct task_struct (definida em <linux/sched.h>).\n"
            "• Organização interna:\n"
            "  1. Lista circular duplamente encadeada global (task_list) ligando todas as tarefas do sistema.\n"
            "  2. Tabela Hash global (pid_hash) indexada pelo PID para busca O(1).\n"
            "  3. Árvores rubro-negras (Red-Black Trees) para tarefas prontas do escalonador CFS/EEVDF.\n"
            "• Pseudo-sistema VFS /proc: O kernel projeta a modelagem interna de cada processo como um diretório virtual em /proc/<PID>/ contendo mapa de memória, limites e estado.",
            "• Inspeção de Estrutura no Kernel:\n"
            "  cat /proc/<PID>/maps (mapeamento de memória virtual)\n"
            "  cat /proc/<PID>/limits (limites de recursos POSIX: nofile, stack, etc.)\n"
            "  cat /proc/<PID>/sched (estatísticas de modelagem do escalonador)\n"
            "• Inspeção via GDB/Crash (depuração de kernel):\n"
            "  crash /usr/lib/debug/boot/vmlinux /proc/kcore\n"
            "  task <PID>"
        ),
        (
            "Estados e transições possíveis",
            "No Windows, o escalonamento opera sobre THREADS, que possuem 8 estados formais:\n"
            "1. Initialized (sendo criada)\n"
            "2. Ready (pronta para executar em fila de prioridade)\n"
            "3. Standby (selecionada para executar no próximo chaveamento em uma CPU específica)\n"
            "4. Running (executando instruções na CPU)\n"
            "5. Waiting (aguardando objeto de sincronização, E/S ou temporizador)\n"
            "6. Transition (pronta, mas pilha de kernel/páginas estão paginadas em disco)\n"
            "7. Terminated (execução encerrada, aguardando liberação de handle)\n"
            "8. DeferredReady (pronta mas aguardando alocação de núcleo específico).\n"
            "• Transições: Ready -> Standby -> Running; Running -> Waiting; Waiting -> Ready (ou Transition); Running -> Terminated.",
            "• GUI:\n"
            "  1. Resource Monitor (resmon.exe) -> Aba CPU -> Tabela 'Processos' (mostra status: Em Execução / Suspenso).\n"
            "  2. System Informer / Process Hacker -> Duplo clique no processo -> Aba 'Threads' -> Coluna 'State' (Running, Wait:UserRequest, Wait:Executive).\n"
            "• CLI (PowerShell):\n"
            "  Get-Process | Select-Object Id, ProcessName, Responding",
            "No Linux, a task_struct possui o campo 'state' composto por flags bem definidas:\n"
            "1. TASK_RUNNING (R): Processo executando na CPU ou pronto na fila de execução.\n"
            "2. TASK_INTERRUPTIBLE (S): Dormindo/bloqueado aguardando recurso ou evento, mas pode ser acordado por sinais POSIX.\n"
            "3. TASK_UNINTERRUPTIBLE (D): Dormindo em espera crítica (normalmente E/S de disco síncrona ou lock de driver); NÃO responde a sinais (nem kill -9).\n"
            "4. TASK_STOPPED (T): Pausado explicitamente (ex: SIGSTOP, SIGTSTP / Ctrl+Z).\n"
            "5. TASK_TRACED (t): Pausado sob controle de depurador (ex: ptrace / gdb).\n"
            "6. EXIT_ZOMBIE (Z): Terminado, mas o processo pai ainda não chamou wait()/waitpid() para ler o exit code.\n"
            "7. EXIT_DEAD (X): Estado terminal sendo liberado do kernel.",
            "• CLI:\n"
            "  ps -eo pid,stat,comm (coluna STAT exibe: R, S, D, T, Z)\n"
            "  ps -eo pid,stat,comm | grep -w 'Z' (localizar zumbis)\n"
            "• Controle de transição de estados:\n"
            "  kill -STOP <PID> (força transição para TASK_STOPPED / T)\n"
            "  kill -CONT <PID> (reverte para TASK_RUNNING / R)\n"
            "• CLI Monitoramento:\n"
            "  top (coluna 'S' exibe o estado da tarefa em tempo real)"
        ),
        (
            "Tipo de threads",
            "• Modelo 1:1 Nativo (Kernel-Level Threads):\n"
            "  No Windows, o escalonador lida exclusivamente com threads (KTHREAD/ETHREAD). Todo processo nasce com pelo menos uma thread primária. A comutação de contexto é feita em modo kernel.\n"
            "• Suporte a Fibras (Fibers - Modelo M:N cooperativo):\n"
            "  O Windows oferece uma API de 'Fibers' no espaço de usuário (ConvertThreadToFiber, CreateFiber, SwitchToFiber) para escalonamento cooperativo sem transição para o kernel, embora seu uso seja restrito a cenários legados e engines de banco de dados (ex.: SQL Server). O padrão corporativo e de desenvolvimento moderno é 100% 1:1 nativo.",
            "• CLI (PowerShell):\n"
            "  (Get-Process -Id <PID>).Threads.Count\n"
            "  Get-Process -Name explorer | Select-Object -ExpandProperty Threads | Select-Object Id, BasePriority, ThreadState\n"
            "• GUI:\n"
            "  1. Gerenciador de Tarefas -> Aba 'Desempenho' -> CPU (exibe o contador global de Threads ativas no sistema).\n"
            "  2. Sysinternals Process Explorer -> Propriedades do Processo -> Aba 'Threads' -> Permite ver o endereço de início (StartAddress), Call Stack e encerrar/suspender threads individuais.",
            "• Modelo 1:1 Nativo via NPTL (Native POSIX Thread Library):\n"
            "  No Linux moderno, threads são implementadas como Lightweight Processes (LWP). O kernel trata processos e threads através da mesma estrutura primitiva (task_struct).\n"
            "  A criação de threads utiliza a chamada de sistema clone() com flags de compartilhamento de recursos: CLONE_VM (mesmo espaço de memória), CLONE_FS, CLONE_FILES (mesmos descritores de arquivos) e CLONE_SIGHAND.\n"
            "  Cada thread possui seu próprio TID (Thread ID) único no kernel, mas todas compartilham o mesmo TGID (Thread Group ID = PID do processo pai).",
            "• CLI:\n"
            "  ps -eLf | grep <nome_processo> (coluna LWP indica o ID de cada thread)\n"
            "  ps -T -p <PID> (exibe threads do processo com SPID)\n"
            "  ls /proc/<PID>/task/ (lista todas as threads LWPs vinculadas ao processo)\n"
            "• CLI Interativo:\n"
            "  top -H -p <PID> (executa o top no modo de visualização de threads)\n"
            "  htop (pressionar Shift+H para ativar/desativar exibição de threads de usuário)"
        ),
        (
            "Hierarquia/agrupamento de processos",
            "• Ausência de Árvore Rígida no Kernel:\n"
            "  O Windows armazena o 'Parent Process ID' (Creator PID) no bloco EPROCESS apenas no momento da criação. Não existe relação estrita de dependência genealógica: se o pai morre, o filho continua executando normalmente de forma independente, sem reparenting obrigatório.\n"
            "• Agrupamento por Job Objects:\n"
            "  O Windows implementa o conceito de 'Job Object' para agregar um ou mais processos em uma unidade gerenciável. Permite impor limites compartilhados de uso de CPU, limites de memória de trabalho, cotas de E/S e encerramento em cascata (se o Job for destruído, todos os processos membros são terminados). Usado nativamente por contêineres Windows e browsers modernos.",
            "• CLI (PowerShell):\n"
            "  Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name | Format-Table -AutoSize\n"
            "• GUI:\n"
            "  1. Sysinternals Process Explorer: Apresenta a árvore hierárquica visual (Tree View) em tempo real, agrupando processos filhos sob processos pais enquanto ambos estiverem ativos.\n"
            "  2. Task Manager: Agrupa processos por 'Aplicativos', 'Processos em segundo plano' e 'Processos do Windows'.",
            "• Hierarquia Estrita em Árvore Genealógica:\n"
            "  No Linux, todo processo (exceto o PID 0/swapper) é derivado de um processo pai via fork() ou clone(). Toda a árvore tem como raiz canônica o PID 1 (systemd em distribuições modernas).\n"
            "  Mecanismo de Reparenting: Se um processo pai é encerrado antes de seus filhos (órfãos), o kernel reatribui automaticamente esses filhos ao PID 1 ou a um subreaper local (PR_SET_CHILD_SUBREAPER), garantindo que todo processo termine com wait().\n"
            "• Agrupamentos Nativos:\n"
            "  1. Process Groups (PGID) para controle de tarefas em terminal (job control).\n"
            "  2. Sessions (SID) para gerenciar terminais de login.\n"
            "  3. Control Groups v2 (cgroups): Hierarquia unificada para limitação e isolamento de CPU, memória, I/O e rede.",
            "• CLI - Visualização em Árvore:\n"
            "  pstree -p (árvore completa com PIDs)\n"
            "  pstree -p <PID> (árvore de um processo específico)\n"
            "  ps -ef --forest (exibe a árvore genealógica formatada em ASCII)\n"
            "• CLI - Agrupamentos e Cgroups:\n"
            "  ps -eo pid,pgid,sid,comm\n"
            "  systemd-cgls (inspeciona a árvore de cgroups do systemd)\n"
            "  cat /proc/<PID>/cgroup"
        ),
        (
            "Comunicação de processos (IPC)",
            "O Windows oferece múltiplos mecanismos de IPC adequados para arquitetura distribuída e local:\n"
            "1. ALPC (Advanced Local Procedure Calls): Mecanismo de alta velocidade otimizado para o subsistema NT, usado para comunicação entre processos clientes e subsistemas (ex.: csrss.exe, lsass.exe).\n"
            "2. Named Pipes: Suporta comunicação duplex tanto local quanto através da rede corporativa (SMB/CIFS).\n"
            "3. Anonymous Pipes: Comunicação unidirecional entre processos pai e filho.\n"
            "4. Mailslots: Mecanismo de broadcast unidirecional (um-para-muitos).\n"
            "5. Shared Memory (Section Objects / Memory-Mapped Files): A forma mais rápida de compartilhar dados diretamente na memória física.\n"
            "6. Winsock (Sockets): TCP/IP e UDP para comunicação local (loopback) ou remota.\n"
            "7. COM/DCOM e RPC: Para chamadas de métodos orientadas a objetos entre componentes.",
            "• CLI (PowerShell):\n"
            "  [System.IO.Directory]::GetFiles('\\\\.\\pipe\\\\') (listar Named Pipes ativos)\n"
            "  Get-ChildItem \\\\.\\pipe\\\n"
            "• Ferramentas Sysinternals:\n"
            "  pipelist.exe (lista todos os Named Pipes abertos e instâncias)\n"
            "  tcpview.exe (monitora conexões de rede e sockets de loopback em tempo real)\n"
            "• GUI:\n"
            "  Process Explorer -> View Lower Pane -> Handles -> Filtrar por 'Section' (memória compartilhada) ou 'File' (pipes).",
            "O Linux disponibiliza uma suíte completa de padrões POSIX e System V para IPC:\n"
            "1. Pipes Anônimos (|): Comunicação unidirecional via buffers de kernel entre processos com parentesco.\n"
            "2. FIFOs (Named Pipes): Criados no sistema de arquivos com persistência de nome (mkfifo).\n"
            "3. Sinais POSIX: Mecanismo de notificação assíncrona (ex.: SIGINT, SIGKILL, SIGTERM, SIGUSR1).\n"
            "4. Memória Compartilhada: POSIX (shm_open, mmap) e System V (shmget, shmat) montados sob /dev/shm (tmpfs de alta velocidade).\n"
            "5. Filas de Mensagens: POSIX (mq_open) e System V (msgget).\n"
            "6. Semáforos IPC: POSIX (sem_open) e System V (semget).\n"
            "7. Unix Domain Sockets: Comunicação bidirecional orientada a fluxo/datagrama via VFS com desempenho superior a sockets de rede.\n"
            "8. D-Bus: Barramento de mensagens de alto nível para serviços de desktop e systemd.",
            "• CLI - Inspeção e Gestão:\n"
            "  ipcs -a (relatório completo de IPC System V: memória, semáforos, filas)\n"
            "  ipcs -m (somente memória compartilhada)\n"
            "  ipcrm -m <shmid> (remover segmento de memória compartilhada)\n"
            "  ls -la /dev/shm (inspecionar segmentos de memória compartilhada POSIX)\n"
            "  ss -x (listar todos os Unix Domain Sockets ativos)\n"
            "• CLI - Criação e Teste:\n"
            "  mkfifo /tmp/meupipe && cat /tmp/meupipe\n"
            "  busctl (monitoramento e chamada de métodos do barramento D-Bus)"
        ),
        (
            "Exclusão mútua",
            "O Windows implementa primitivas de sincronização divididas entre Espaço do Kernel e Espaço do Usuário:\n"
            "1. Primitivas de Kernel (Dispatcher Objects):\n"
            "   • Mutexes (Mutants): Exclusão mútua interprocessos com suporte a detecção de abandono (se a thread dona morre, a posse é passada com status abandonado).\n"
            "   • Semáforos: Controlam contagem de acessos concorrentes a um pool de recursos.\n"
            "   • Eventos (Auto-reset e Manual-reset): Sinalizam conclusão de tarefas para desbloquear threads.\n"
            "2. Primitivas de Usuário (User-Mode Synchronization):\n"
            "   • Critical Sections: Rápidas; utilizam spinlocks temporários antes de invocar um evento do kernel se a espera for prolongada.\n"
            "   • Slim Reader/Writer (SRW) Locks: Altamente otimizados, ocupam o tamanho de um ponteiro e diferenciam leituras compartilhadas de escritas exclusivas sem alocação no kernel.",
            "• Depuração no WinDbg:\n"
            "  !locks (exibe bloqueios de recursos no kernel)\n"
            "  !cs -s (analisa estado de seções críticas)\n"
            "• GUI:\n"
            "  Sysinternals Process Explorer: Selecionar processo -> View Lower Pane -> Handles -> Filtrar pelo tipo 'Mutant' ou 'Semaphore' para verificar quais travas de exclusão mútua o processo mantém abertas.",
            "O Linux provê mecanismos de sincronização robustos em ambos os níveis:\n"
            "1. No Kernel (Kernel Space):\n"
            "   • Mutexes do Kernel (struct mutex): Travas com suspensão de thread.\n"
            "   • Semáforos (struct semaphore): Controle de contagem no kernel.\n"
            "   • Spinlocks (spinlock_t): Travas ativas (busy waiting) usadas estritamente no kernel onde dormir não é permitido (ex.: manipuladores de interrupção - ISR).\n"
            "   • RCU (Read-Copy-Update): Técnica ultrarrápida sem travas para leituras concorrentes quase gratuitas com atualizações atômicas.\n"
            "2. No Espaço do Usuário (User Space via POSIX Threads):\n"
            "   • pthread_mutex_t, pthread_rwlock_t e semáforos (sem_t).\n"
            "   • Futex (Fast Userspace Mutex): Mecanismo híbrido de alto desempenho onde o caminho sem colisão opera inteiramente em registradores atômicos (CPU), e o kernel só é invocado por chamada de sistema (futex()) em caso de colisão real.",
            "• CLI:\n"
            "  lslocks (lista todas as travas ativas de arquivos no sistema operacional)\n"
            "  cat /proc/locks (exibe descritores brutos de locks de arquivo mantidos pelo kernel)\n"
            "• Diagnóstico e Depuração:\n"
            "  valgrind --tool=helgrind ./meu_programa (detecta condições de corrida em threads)\n"
            "  valgrind --tool=drd ./meu_programa\n"
            "  gdb -p <PID> -> (gdb) info threads -> thread apply all bt"
        ),
        (
            "Prioridades de um processo",
            "No Windows, as threads são escalonadas dentro de uma escala de 32 níveis (0 a 31):\n"
            "• Faixa 0: Reservada para a thread de paginação zero (Zero-page thread).\n"
            "• Faixa 1 a 15: Prioridades Dinâmicas (Time-sharing para aplicações normais de usuário e sistema).\n"
            "• Faixa 16 a 31: Prioridades de Tempo Real (Real-Time, não preemptadas por processos comuns).\n"
            "• Classes de Prioridade do Processo (API Win32):\n"
            "  Idle (Prioridade base 4), Below Normal (6), Normal (8), Above Normal (10), High (13) e Realtime (24).\n"
            "• Dynamic Priority Boost: O Windows incrementa temporariamente a prioridade de threads que recebem foco na interface gráfica (Foreground Boost), saem de operações de E/S ou foram salvas de starvation (Balance Set Manager).",
            "• CLI (PowerShell):\n"
            "  (Get-Process -Name notepad).PriorityClass = 'High'\n"
            "  Get-Process | Select-Object Name, Id, PriorityClass, BasePriority\n"
            "• CLI (CMD):\n"
            "  start /high cmd.exe (iniciar com prioridade Alta)\n"
            "  wmic process where name=\"notepad.exe\" CALL setpriority 128 (128=High, 32=Normal, 64=Low)\n"
            "• GUI:\n"
            "  1. Gerenciador de Tarefas -> Aba 'Detalhes' -> Clicar com botão direito no processo -> 'Definir prioridade' (Tempo real, Alta, Acima do normal, Normal, Abaixo do normal, Baixa).\n"
            "  2. 'Definir afinidade' (selecionar núcleos de CPU).",
            "O Linux utiliza um esquema de 140 níveis de prioridade no kernel:\n"
            "• Prioridades 0 a 99 (Tempo Real - POSIX RT):\n"
            "  Gerenciadas pelas políticas SCHED_FIFO e SCHED_RR. Têm precedência absoluta sobre processos normais.\n"
            "• Prioridades 100 a 139 (Normal / Time-sharing):\n"
            "  Gerenciadas pelo escalonador CFS/EEVDF (políticas SCHED_OTHER, SCHED_BATCH, SCHED_IDLE).\n"
            "• Escala Nice (Espaço do Usuário):\n"
            "  Mapeada sobre as prioridades normais de -20 (prioridade máxima/mais 'egoísta') a +19 (prioridade mínima/mais 'gentil'). O valor padrão é 0 (que corresponde à prioridade 120 no kernel). Apenas o root pode atribuir valores nice negativos.",
            "• CLI - Visualização:\n"
            "  ps -eo pid,ni,pri,rtprio,comm (exibe PID, valor Nice, Prioridade do Kernel e Prioridade RT)\n"
            "• CLI - Modificação:\n"
            "  nice -n -10 ./meu_programa (executa com prioridade mais alta - exige sudo)\n"
            "  nice -n 15 ./meu_programa (executa com prioridade mais baixa)\n"
            "  renice -n 5 -p <PID> (altera a prioridade nice de um processo em execução)\n"
            "  renice -u <usuario> -n 10 (altera a de todos os processos do usuário)\n"
            "  chrt -p <PID> (consulta política de escalonamento RT e prioridade)\n"
            "  sudo chrt -f -p 50 <PID> (muda política para SCHED_FIFO com prioridade RT 50)"
        ),
        (
            "Algoritmo de escalonamento de processos",
            "O Windows 11 utiliza um Escalonador Preemptivo Baseado em Prioridades com Múltiplas Filas:\n"
            "• Funcionamento: A thread de maior prioridade no estado Ready sempre executa. Threads de mesma prioridade compartilham a CPU em rodízio (Round-Robin) controlado por Quantum de tempo.\n"
            "• Quantum Configurável: Sistemas cliente (Windows 11) usam quantums curtos e variáveis (3 ticks de relógio, ~30ms com boosts dinâmicos) para garantir resposta imediata na interface gráfica; edições Server usam quantums longos e estáveis (~120ms).\n"
            "• Otimização para CPUs Híbridas (Intel Alder/Raptor Lake e AMD 3D V-Cache):\n"
            "  O escalonador integra suporte avançado ao Intel Thread Director: classifica threads pelo tipo de instrução e distribui threads de primeiro plano/pesadas em núcleos de performance (P-cores) e threads em segundo plano/leves em núcleos de eficiência (E-cores).",
            "• GUI - Ajuste de Quantum:\n"
            "  Sysdm.cpl (Propriedades do Sistema) -> Avançado -> Desempenho -> Configurações -> Avançado -> 'Ajustar para melhor desempenho de: Programas OU Serviços em segundo plano'.\n"
            "• CLI (PowerShell / PowerCFG):\n"
            "  powercfg /qh (inspecionar políticas de parking de núcleo e heterogeneidade de escalonamento de CPU).\n"
            "• Diagnóstico Avançado:\n"
            "  Windows Performance Toolkit (WPR / WPA) para rastrear comutações de contexto e latência de DPC/Interrupts.",
            "O Ubuntu 24.04 LTS (Kernel Linux 6.8) introduz oficialmente o escalonador EEVDF (Earliest Eligible Virtual Deadline First), que substitui o clássico CFS (Completely Fair Scheduler):\n"
            "• Do CFS para o EEVDF:\n"
            "  O CFS mantinha a justiça baseada no tempo de execução virtual (vruntime) em uma árvore rubro-negra, mas tinha limitações para garantir latência previsível para tarefas interativas.\n"
            "  O EEVDF (baseado no algoritmo de Peter Hoon de 1995) resolve isso separando 'elegibilidade' (se a tarefa já recebeu ou não sua cota de CPU) de 'deadline virtual' (urgência temporal da tarefa). Tarefas sensíveis a latência recebem deadlines mais curtos e são agendadas com prioridade imediata sem sacrificar a justiça global.\n"
            "• Políticas de Tempo Real POSIX:\n"
            "  SCHED_FIFO (executa até ceder CPU ou ser preemptado por prioridade maior), SCHED_RR (rodízio em tempo real) e SCHED_DEADLINE (Earliest Deadline First para tarefas periódicas duras).",
            "• CLI - Diagnóstico e Configuração:\n"
            "  chrt -m (mostra as políticas de escalonamento suportadas pelo kernel)\n"
            "  cat /proc/sys/kernel/sched_* (parâmetros de calibração do escalonador)\n"
            "  sudo sysctl -a | grep sched\n"
            "• CLI - Análise de Desempenho do Escalonador:\n"
            "  sudo perf sched record -- sleep 2\n"
            "  sudo perf sched latency (calcula tempo médio de espera e atraso de agendamento de cada tarefa)\n"
            "  sudo perf sched map (mapa gráfico de despacho de tarefas nas CPUs)"
        ),
        (
            "Tratamento de deadlocks",
            "• Postura Geral: Algoritmo do Avestruz (Ostrich Algorithm):\n"
            "  O Windows não tenta prevenir nem resolver ativamente deadlocks de processos em espaço de usuário em tempo de execução, presumindo que são raros e que o custo contínuo de algoritmos preventivos (ex.: Grafo de Alocação de Recursos ou Algoritmo do Banqueiro) degradaria severamente o desempenho global. O tratamento de processos travados fica sob responsabilidade do usuário ou do desenvolvedor.\n"
            "• Mecanismos Avançados de Diagnóstico e Prevenção no Windows:\n"
            "  1. Wait Chain Traversal (WCT): API integrada ao SO que rastreia cadeias de bloqueio e dependências entre threads e nós de sincronização (COM, ALPC, Critical Sections), identificando deadlocks explicitamente.\n"
            "  2. Driver Verifier (verifier.exe): Mecanismo do kernel com módulo de 'Deadlock Detection' que monitora spinlocks e mutexes de drivers para prevenir travamentos de sistema antes da tela azul (BSOD).",
            "• GUI - Resolução e Diagnóstico:\n"
            "  1. Monitor de Recursos (resmon.exe) -> Aba CPU -> Clicar com botão direito no processo travado -> 'Analisar Cadeia de Espera' (Analyze Wait Chain). Se houver deadlock, o Windows exibe as threads em impasse mútuo destacadas em vermelho.\n"
            "  2. Gerenciador de Tarefas -> 'Finalizar Tarefa'.\n"
            "• CLI:\n"
            "  taskkill /F /PID <PID> (eliminação forçada do processo em impasse)\n"
            "  verifier.exe (configurar verificação de deadlocks em drivers)",
            "• Postura Geral: Algoritmo do Avestruz (Ostrich Algorithm):\n"
            "  Assim como o Windows, o Linux adota o Algoritmo do Avestruz para processos de usuário comuns. Deadlocks entre aplicações de usuário não são desfeitos automaticamente pelo kernel, cabendo ao administrador ou watchdog intervir.\n"
            "• Tecnologias de Detecção e Prevenção no Linux:\n"
            "  1. Lockdep (Lock Dependency Validator): Subsistema do kernel Linux que analisa hierarquias e grafos de aquisição de locks. Se um código tenta adquirir travas em ordem propensa a deadlock (inversão de ordem AB-BA), o Lockdep gera alertas imediatos no dmesg.\n"
            "  2. Hung Task Detector: Componente do kernel que detecta threads presas em estado D (TASK_UNINTERRUPTIBLE) por mais de 120 segundos (tempo limite configurável), registrando call trace de depuração no log do sistema.\n"
            "  3. Ferramentas de Desenvolvimento: Valgrind (Helgrind/DRD) para detectar deadlocks em tempo de desenvolvimento.",
            "• CLI - Monitoramento e Resolução:\n"
            "  kill -9 <PID> (sinal SIGKILL para abortar o processo travado)\n"
            "  pkill -9 -f <nome_processo>\n"
            "  dmesg | grep -i \"blocked for more than 120 seconds\" (alerta de hung task no kernel)\n"
            "• Configuração de Timeout no Kernel:\n"
            "  sysctl kernel.hung_task_timeout_secs\n"
            "• Diagnóstico com GDB:\n"
            "  gdb -p <PID> -> (gdb) thread apply all bt (inspeciona o backtrace de todas as threads para localizar a trava de espera mútua)"
        )
    ]

    # Write data
    start_row = 3
    for idx, row_data in enumerate(data):
        curr_row = start_row + idx
        worksheet.write(curr_row, 0, row_data[0], topic_fmt)
        worksheet.write(curr_row, 1, row_data[1], content_fmt)
        worksheet.write(curr_row, 2, row_data[2], cmd_fmt)
        worksheet.write(curr_row, 3, row_data[3], content_fmt)
        worksheet.write(curr_row, 4, row_data[4], cmd_fmt)
        worksheet.set_row(curr_row, 140) # Generous row height for text wrapping

    # Reference footer
    ref_row = start_row + len(data)
    ref_title_fmt = workbook.add_format({
        'bold': True,
        'bg_color': '#D6EAF8',
        'font_color': '#1B365D',
        'font_name': 'Segoe UI',
        'font_size': 10,
        'align': 'left',
        'valign': 'top',
        'border': 1,
        'border_color': '#BDC3C7'
    })
    ref_content_fmt = workbook.add_format({
        'font_name': 'Segoe UI',
        'font_size': 9,
        'font_color': '#333333',
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1,
        'border_color': '#BDC3C7'
    })
    
    worksheet.write(ref_row, 0, "Referências Bibliográficas e Científicas", ref_title_fmt)
    ref_text = (
        "1. SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. Operating System Concepts. 10th ed. Hoboken: Wiley, 2018.\n"
        "2. TANENBAUM, A. S.; BOS, H. Modern Operating Systems. 4th ed. Boston: Pearson, 2015.\n"
        "3. RUSSINOVICH, M. E.; SOLOMON, D. A.; IONESCU, A. Windows Internals: Part 1 - System architecture, processes, threads, memory management, and more. 7th ed. Microsoft Press, 2017.\n"
        "4. LOVE, Robert. Linux Kernel Development. 3rd ed. Boston: Addison-Wesley, 2010.\n"
        "5. HOON, Peter. EEVDF: Earliest Eligible Virtual Deadline First scheduling algorithm. IEEE Real-Time Systems, 1995 (Kernel 6.6+ Adoption, 2023-2024).\n"
        "6. CORBET, J.; RUBINI, A.; KROAH-HARTMAN, G. Linux Device Drivers. 3rd ed. O'Reilly Media, 2005."
    )
    worksheet.merge_range(ref_row, 1, ref_row, 4, ref_text, ref_content_fmt)
    worksheet.set_row(ref_row, 90)

    # Column widths
    worksheet.set_column(0, 0, 24)  # Tópico
    worksheet.set_column(1, 1, 44)  # Windows 11 Descrição
    worksheet.set_column(2, 2, 40)  # Windows 11 Comandos
    worksheet.set_column(3, 3, 44)  # Ubuntu 24.04 Descrição
    worksheet.set_column(4, 4, 40)  # Ubuntu 24.04 Comandos

    workbook.close()
    print(f"Spreadsheet generated successfully at: {filepath}")

if __name__ == "__main__":
    import os
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Planilhas")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "modelo_estudo_caso_processos_preenchido.xlsx")
    create_comparative_spreadsheet(out_path)

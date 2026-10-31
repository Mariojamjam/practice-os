import xlsxwriter
import os

def create_filesystems_comparative_spreadsheet(filepath):
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet("Estudo de Caso - Arquivos")
    
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
    worksheet.merge_range('A1:E1', 'ESTUDO DE CASO: SISTEMAS DE ARQUIVOS EM SISTEMAS OPERACIONAIS', title_fmt)
    worksheet.merge_range('A2:E2', 'Disciplina: Sistemas Operacionais | Prof. Dr. Douglas Véras | Alunos: Luiz Maranhão & Mário Jorge (UFRPE)', subtitle_fmt)
    worksheet.set_row(0, 26)
    worksheet.set_row(1, 20)

    headers = [
        "Sistema Operacional /\nComparativo",
        "Windows 11 Pro (23H2 / 24H2) - NTFS / ReFS",
        "Windows 11 Pro – comandos (linha de comando ou especificar função na GUI)\n*listagem e breve descrição de comandos relevantes para visualização ou gerenciamento",
        "Ubuntu 24.04 LTS (Kernel Linux 6.8) - ext4 / Btrfs",
        "Ubuntu 24.04 LTS – comandos (linha de comando ou especificar função na GUI)\n*listagem e breve descrição de comandos relevantes para visualização ou gerenciamento"
    ]

    worksheet.set_row(2, 45)
    for col_idx, h in enumerate(headers):
        worksheet.write(2, col_idx, h, header_fmt)

    data = [
        # Linha 1: Introdução ao Sistema de Arquivos
        (
            "Introdução ao Sistema de Arquivos dos SOs\n(Visão Geral, Abstração de Arquivos, Hierarquia, Namespace e Arquitetura de Camadas)",
            # Windows 11
            "• Arquitetura e Abstração no Windows 11:\n"
            "  - Sistema de Arquivos Primário: NTFS (New Technology File System), com suporte empresarial a ReFS (Resilient File System).\n"
            "  - Arquitetura de Camadas (IFS - Installable File System): Operações de arquivo passam pelo I/O Manager (ntoskrnl.exe) e pelo Cache Manager (Cc), sendo despachadas via IRPs para o driver de sistema de arquivos (Ntfs.sys).\n"
            "  - Modelo de Namespace e Hierarquia: Namespace baseado em letras de unidades (ex.: C:\\, D:\\) com separador de barra invertida (\\), mapeadas via links simbólicos de namespace de objetos do Windows (\\Device\\HarddiskVolumeX).\n"
            "  - Conceito de Arquivo: Coleção de atributos tipados (metadados e dados) gerenciados como uma tupla chave-valor na Master File Table (MFT). Suporta fluxos de dados múltiplos (ADS - Alternate Data Streams).",

            # Windows 11 - Comandos
            "• CLI (fsutil - Inspecionar Driver e Sistema de Arquivos):\n"
            "  fsutil fsinfo volumeinfo C:\n"
            "  (Exibe nome do sistema de arquivos NTFS, número de série, tamanho de setor/cluster e flags suportadas).\n\n"
            "• CLI (PowerShell - Obter Volumes e Pontos de Montagem):\n"
            "  Get-Volume | Format-Table DriveLetter, FileSystemLabel, FileSystemType, SizeRemaining, Size\n"
            "  (Lista todos os volumes lógicos montados e formatos de arquivo).\n\n"
            "• GUI (Gerenciamento de Disco):\n"
            "  diskmgmt.msc\n"
            "  (Interface visual para criar partições, formatar em NTFS/ReFS/exFAT e atribuir letras de unidade).",

            # Ubuntu 24.04
            "• Arquitetura e Abstração no Linux (Ubuntu 24.04):\n"
            "  - Sistema de Arquivos Primário: ext4 (Fourth Extended Filesystem), com suporte nativo a Btrfs e ZFS.\n"
            "  - Arquitetura VFS (Virtual File System): Fornece uma camada de abstração uniforme e orientada a objetos no kernel (structs: inode, dentry, file, superblock), permitindo chamadas de sistema padronizadas (open, read, write) independente do meio físico.\n"
            "  - Modelo de Namespace e Árvore Unificada: Raiz única global (/), sem letras de unidade. Dispositivos de bloco são 'montados' em nós arbitrários da árvore de diretórios (ex.: /mnt, /home, /var).\n"
            "  - Conceito 'Tudo é um Arquivo': Arquivos comuns, diretórios, sockets de rede, pipes e dispositivos de hardware em /dev compartilham a mesma semântica de descritor de arquivo.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Exibir Tabela de Sistemas de Arquivos Montados):\n"
            "  findmnt -t ext4,btrfs,vfat\n"
            "  (Exibe a árvore hierárquica de pontos de montagem, dispositivos de bloco e opções de montagem ativas).\n\n"
            "• CLI (Inspecionar Superbloco do Sistema de Arquivos):\n"
            "  sudo tune2fs -l /dev/nvme0n1p3 | head -n 30\n"
            "  (Exibe metadados globais do ext4: UUID, estado do volume, contagem de inodos, blocos e flags de journaling).\n\n"
            "• GUI (Discos do GNOME):\n"
            "  gnome-disks\n"
            "  (Gerencia partições, pontos de montagem automáticos em /etc/fstab e opções de benchmarking)."
        ),

        # Linha 2: Estrutura Interna e Organização em Disco
        (
            "Estrutura Interna e Organização em Disco\n(Estrutura de Metadados: MFT vs Inodes, Superbloco e Indexação de Diretórios)",
            # Windows 11
            "• Organização Interna do NTFS (Windows 11):\n"
            "  1. Master File Table (MFT - $MFT):\n"
            "     - O NTFS trata tudo como um arquivo, inclusive seus próprios metadados. A MFT é uma tabela linear com registros fixos de 1024 bytes (1 KB) por arquivo/diretório.\n"
            "     - Arquivos de Metadados do Sistema: $MFT (índice mestre), $MFTMirr (cópia de segurança dos primeiros setores), $LogFile (log de transações), $Volume (nome e versão), $Bitmap (mapa de clusters livres), $BadClust (setores defeituosos).\n"
            "     - Atributos Residentes vs Não-Residentes: Arquivos pequenos (<700 bytes) têm seus dados armazenados diretamente dentro do próprio registro MFT (residente), eliminando busca em disco. Arquivos maiores têm seus clusters mapeados fora da MFT através de 'data runs' (extents).\n"
            "  2. Indexação de Diretórios (B-Trees):\n"
            "     - Diretórios no NTFS são indexados usando árvores B balanceadas (B-Trees) através dos atributos $INDEX_ROOT e $INDEX_ALLOCATION, garantindo busca de arquivos em tempo O(log n) mesmo em pastas com milhões de arquivos.",

            # Windows 11 - Comandos
            "• CLI (fsutil - Estatísticas da MFT):\n"
            "  fsutil fsinfo ntfsinfo C:\n"
            "  (Exibe tamanho dos setores, clusters, bytes por registro MFT e a zona reservada da MFT).\n\n"
            "• CLI (Sysinternals - Inspecionar Localização Física dos Arquivos):\n"
            "  contig.exe -v \"C:\\Windows\\notepad.exe\"\n"
            "  (Exibe a lista exata de clusters e extents ocupados pelo arquivo no disco).\n\n"
            "• CLI (PowerShell - Inspecionar Atributos Ocultos e Streams):\n"
            "  Get-Item -Path \"C:\\*\" -Force | Select-Object Name, Attributes, Length",

            # Ubuntu 24.04
            "• Organização Interna do ext4 (Ubuntu 24.04):\n"
            "  1. Grupos de Blocos (Block Groups) e Inodes:\n"
            "     - O volume ext4 é particionado em Grupos de Blocos. Cada grupo contém: Cópia de Superbloco, Descritor de Grupo, Bitmap de Blocos, Bitmap de Inodes, e a Tabela de Inodes.\n"
            "     - Inodes (Index Nodes): Estruturas fixas de metadados (tipicamente 256 bytes) que armazenam tamanho, permissões (mode), proprietário (UID/GID), timestamps (atime, mtime, ctime, crtime) e ponteiros para os dados.\n"
            "     - Nomes de arquivos NÃO ficam no inode: Ficam armazenados nas entradas de diretório (struct ext4_dir_entry_2), mapeando o nome para o número do inode correspondente.\n"
            "  2. Indexação de Diretórios (HTree):\n"
            "     - Diretórios pequenos usam lista encadeada simples. Diretórios volumosos utilizam HTree (árvore B baseada em hash de 32 bits das strings de nomes), permitindo inserção e busca ultrarrápidas sem overhead de ordenação alfabética completa.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Inspecionar Inode e Metadados Detalhados de um Arquivo):\n"
            "  stat /bin/bash\n"
            "  (Exibe número de inode, tamanho em bytes, blocos de 512B alocados, permissões e timestamps).\n\n"
            "• CLI (Inspecionar Bloco de Grupos e Estatísticas com dumpe2fs):\n"
            "  sudo dumpe2fs -h /dev/nvme0n1p3\n"
            "  (Exibe contagem total de inodos, inodos livres por grupo e recursos ativos do ext4).\n\n"
            "• CLI (Localizar Arquivo pelo Número do Inode):\n"
            "  sudo find / -inum 123456 2>/dev/null"
        ),

        # Linha 3: Métodos de Alocação de Espaço e Gerenciamento de Espaço Livre
        (
            "Métodos de Alocação de Espaço e Gerenciamento de Espaço Livre\n(Extents, Clusters, Bitmaps de Blocos, Fragmentação e Desfragmentação)",
            # Windows 11
            "• Alocação de Espaço no NTFS (Windows 11):\n"
            "  1. Unidade de Alocação (Cluster / Allocation Unit):\n"
            "     - A alocação ocorre em múltiplos de setores físicos chamados Clusters (padrão de 4 KB). O NTFS suporta clusters de até 2 MB em volumes gigantescos.\n"
            "  2. Alocação por Extents (Data Runs):\n"
            "     - Em vez de ponteiros individuais por bloco, o NTFS utiliza pares ordenados (Cluster Inicial, Quantidade de Clusters Contíguos), permitindo endereçar gigabytes com poucos bytes de metadados.\n"
            "  3. Gerenciamento de Espaço Livre ($Bitmap):\n"
            "     - O arquivo de sistema $Bitmap mantém um vetor de bits onde cada bit representa o estado de um cluster (0 = livre, 1 = alocado).\n"
            "  4. Fragmentação e Otimização Automática:\n"
            "     - O Windows 11 agenda o utilitário 'defrag' semanalmente. Em discos rígidos magnéticos (HDDs), realiza desfragmentação física contígua; em SSDs e NVMes, emite comandos TRIM para reaproveitamento limpo de blocos de memória flash.",

            # Windows 11 - Comandos
            "• CLI (Desfragmentar e Otimizar Unidade de Disco):\n"
            "  defrag C: /O /U /V\n"
            "  (/O seleciona automaticamente o método correto: desfragmentação para HDD ou retrim para SSDs).\n\n"
            "• CLI (PowerShell - Analisar Nível de Fragmentação do Volume):\n"
            "  Optimize-Volume -DriveLetter C -Analyze -Verbose\n"
            "  (Retorna percentual de fragmentação e recomendação de consolidação de espaço).\n\n"
            "• CLI (fsutil - Consultar Alocação de Clusters):\n"
            "  fsutil file queryextents \"C:\\Windows\\explorer.exe\"",

            # Ubuntu 24.04
            "• Alocação de Espaço no ext4 (Ubuntu 24.04):\n"
            "  1. Alocação Moderna por Extents (Substituição de Ponteiros Indiretos):\n"
            "     - O ext4 substituiu a árvore clássica de blocos indiretos do ext2/ext3 por Extents. Cada extent mapeia até 128 MB de blocos contíguos com apenas uma estrutura de 12 bytes (struct ext4_extent), reduzindo metadados e aumentando a taxa de transferência sequencial.\n"
            "  2. Alocação Tardia (Delayed Allocation / Delalloc):\n"
            "     - Quando o processo grava dados via write(), o kernel apenas aloca os buffers na RAM e adia a escolha dos blocos físicos até a descarga para o disco (writeback). Isso permite agrupar gravações contíguas gigantescas, diminuindo drasticamente a fragmentação inicial.\n"
            "  3. Gerenciamento de Espaço Livre (Block Bitmaps e mballoc):\n"
            "     - Utiliza o alocador multi-bloco (mballoc) e bitmaps de blocos por grupo. O mballoc tenta alocar múltiplos blocos contíguos de uma só vez para o arquivo.\n"
            "  4. Desfragmentação Online (e4defrag):\n"
            "     - O ext4 suporta desfragmentação com o sistema de arquivos montado e ativo sem interrupção de serviços.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Inspecionar Extents de um Arquivo no ext4):\n"
            "  sudo filefrag -v /var/log/syslog\n"
            "  (Exibe quantidade de extents, offset lógico, blocos físicos inicial e final e se há descontinuidade).\n\n"
            "• CLI (Desfragmentação Online com e4defrag):\n"
            "  sudo e4defrag -c /home   # Checa necessidade de desfragmentação\n"
            "  sudo e4defrag /home      # Executa desfragmentação online de blocos\n\n"
            "• CLI (Otimização TRIM em SSDs via systemd):\n"
            "  sudo fstrim -av\n"
            "  (Emite o comando TRIM em todos os pontos de montagem compatíveis)."
        ),

        # Linha 4: Confiabilidade, Journaling e Recuperação de Falhas
        (
            "Confiabilidade, Journaling e Recuperação de Falhas\n(Transações Atômicas, Logs do Sistema de Arquivos, Chkdsk e Fsck)",
            # Windows 11
            "• Confiabilidade e Journaling no NTFS (Windows 11):\n"
            "  1. Arquitetura de Transações com $LogFile:\n"
            "     - O NTFS adota journaling de metadados baseado no protocolo de log antecipado (Write-Ahead Logging / WAL) inspirado em bancos de dados relacionais.\n"
            "     - Antes de qualquer modificação estrutural (ex.: criar arquivo, estender tamanho), a intenção da operação é registrada como uma transação atômica no arquivo circular $LogFile.\n"
            "     - Em caso de queda de energia, durante o boot o NTFS lê o $LogFile e executa uma fase de Redo (reaplica transações confirmadas) e uma fase de Undo (desfaz operações parciais inacabadas), restaurando a consistência em segundos.\n"
            "  2. USN Journal (Update Sequence Number / $UsnJrnl):\n"
            "     - Mantém um log contínuo de todas as alterações ocorridas em arquivos e pastas para indexação ultrarrápida do Windows Search e antivírus.\n"
            "  3. Mecanismo de Autocura (Self-Healing NTFS) e Chkdsk:\n"
            "     - O driver Ntfs.sys corrige pequenas inconsistências em tempo de execução online sem desmontar o volume. Erros severos são isolados e reparados pelo utilitário Chkdsk durante a inicialização.",

            # Windows 11 - Comandos
            "• CLI (Verificar Status de Integridade do Volume NTFS):\n"
            "  fsutil dirty query C:\n"
            "  (Verifica se o 'dirty bit' está ativo, indicando se o sistema sofreu desligamento abrupto e requer reparo).\n\n"
            "• CLI (Auditar e Reparar Volume com Chkdsk):\n"
            "  chkdsk C: /scan\n"
            "  (Executa verificação online de metadados sem desmontar o volume e agenda correção se necessário).\n\n"
            "• CLI (fsutil - Consultar o USN Change Journal):\n"
            "  fsutil usn queryjournal C:\n"
            "  (Exibe métricas de ID e tamanho do log contínuo de alterações do NTFS).",

            # Ubuntu 24.04
            "• Confiabilidade e Journaling no ext4 (Ubuntu 24.04):\n"
            "  1. Subsistema JBD2 (Journaling Block Device 2):\n"
            "     - O ext4 utiliza o módulo de kernel JBD2 para gerenciar transações atômicas registradas em um inodo especial reservado de journal.\n"
            "     - Modos de Journaling Configuráveis:\n"
            "       * data=ordered (Padrão): Apenas os metadados são gravados no journal, mas o kernel força que os blocos de dados sejam gravados no disco antes que a transação de metadados seja confirmada. Excelente equilíbrio entre integridade e performance.\n"
            "       * data=journal: Tanto dados quanto metadados passam pelo journal antes de irem para o disco. Segurança máxima contra perda de dados, mas com impacto de desempenho (duplo write).\n"
            "       * data=writeback: Metadados são journalados, mas dados podem ser gravados em qualquer ordem.\n"
            "  2. Checksums no Journal (Metadados Protegidos por CRC32c):\n"
            "     - O ext4 calcula checksums criptográficos CRC32c para cada bloco de metadados e entradas do journal, detectando instantaneamente corrupções de hardware ou falhas de disco.\n"
            "  3. Manutenção e Recuperação com fsck / e2fsck:\n"
            "     - O utilitário e2fsck valida e repara superblocos, mapas de inodos e tabelas de blocos.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Inspecionar Opções e Modo de Journal Ativo):\n"
            "  cat /proc/mounts | grep ext4\n"
            "  (Exibe opções de montagem ativas, ex.: data=ordered, commit=5, errors=remount-ro).\n\n"
            "• CLI (Verificar Integridade com e2fsck / fsck - Simulação Leitura):\n"
            "  sudo e2fsck -fn /dev/nvme0n1p3\n"
            "  (Executa varredura de consistência em modo somente leitura sem alterar o disco).\n\n"
            "• CLI (Ajustar Parâmetros de Checagem Periódica):\n"
            "  sudo tune2fs -c 30 -i 180d /dev/nvme0n1p3\n"
            "  (Configura o sistema para forçar verificação de integridade a cada 30 montagens ou 180 dias)."
        ),

        # Linha 5: Links, Metadados e Atributos Especiais
        (
            "Links, Metadados e Atributos Especiais\n(Hard Links, Soft/Symbolic Links, Alternate Data Streams e Atributos Estendidos)",
            # Windows 11
            "• Links e Atributos Especiais no NTFS (Windows 11):\n"
            "  1. Hard Links, Symbolic Links e Junction Points:\n"
            "     - Hard Link: Cria uma nova entrada de nome apontando para o mesmo registro de arquivo na MFT dentro do mesmo volume. O arquivo só é excluído fisicamente quando todos os hard links são removidos.\n"
            "     - Symbolic Link (Symlink): Arquivo especial contendo o caminho relativo ou absoluto para outro arquivo ou diretório, suportando caminhos entre volumes diferentes (C:\\ para D:\\) e rede.\n"
            "     - Junction Point: Recurso clássico do NTFS para redirecionamento exclusivo de diretórios locais via pontos de nova análise (Reparse Points).\n"
            "  2. Reparse Points (Pontos de Nova Análise):\n"
            "     - Mecanismo fundamental do NTFS que permite interceptar aberturas de arquivos para serviços avançados (OneDrive Files On-Demand, pontos de montagem de volumes e Symlinks).\n"
            "  3. ADS (Alternate Data Streams):\n"
            "     - Permite associar múltiplos fluxos de dados a um único nome de arquivo (ex.: 'arquivo.txt:fluxo_oculto'). Usado pelo Windows para marcar a 'Zone.Identifier' (identifica arquivos baixados da web).",

            # Windows 11 - Comandos
            "• CLI (CMD - Criar Links Simbólicos, Hard Links e Junctions):\n"
            "  mklink link_simbolico.txt destino.txt        # Soft Symlink\n"
            "  mklink /H hardlink.txt destino.txt            # Hard Link\n"
            "  mklink /J C:\\MinhaJunction D:\\DestinoPasta   # Directory Junction\n\n"
            "• CLI (PowerShell - Inspecionar Alternate Data Streams):\n"
            "  Get-Item -Path \"download.zip\" -Stream *\n"
            "  (Revela a stream Zone.Identifier que dispara o aviso de segurança do SmartScreen).\n\n"
            "• CLI (fsutil - Gerenciamento de Hard Links):\n"
            "  fsutil hardlink list \"C:\\Windows\\notepad.exe\"",

            # Ubuntu 24.04
            "• Links e Atributos Especiais no Linux / ext4 (Ubuntu 24.04):\n"
            "  1. Hard Links vs. Soft/Symbolic Links:\n"
            "     - Hard Link: Cria uma nova entrada em diretório apontando diretamente para o mesmo número de inodo existente. Incrementa o contador de links ('links count') do inodo. Restrito ao mesmo sistema de arquivos e proibido para diretórios (para evitar laços cíclicos).\n"
            "     - Symbolic Link (Symlink): Inodo independente de tipo especial (S_IFLNK) que armazena a string de texto do caminho de destino. Se o caminho tiver menos de 60 bytes, é salvo inline dentro do próprio inodo (*fast symlink*).\n"
            "  2. Atributos Estendidos do Sistema de Arquivos (xattr):\n"
            "     - Permite associar pares chave-valor arbitrários a inodos. Usado por módulos de segurança como SELinux/AppArmor (rótulos de segurança 'security.*') e ACLs POSIX ('system.posix_acl_access').\n"
            "  3. Atributos de Baixo Nível do ext4 (chattr / lsattr):\n"
            "     - Permite definir flags especiais no inodo, como '+i' (imutável - nem o root pode alterar ou deletar) e '+a' (append-only - apenas permite anexar dados ao final, ideal para logs de segurança).",

            # Ubuntu 24.04 - Comandos
            "• CLI (Criar Links Hard e Simbólicos no Terminal):\n"
            "  ln arquivo_original.txt hardlink.txt\n"
            "  ln -s /caminho/destino /caminho/symlink\n\n"
            "• CLI (Definir Atributo Imutável no Inode com chattr):\n"
            "  sudo chattr +i /etc/resolv.conf\n"
            "  lsattr /etc/resolv.conf\n"
            "  (Torna o arquivo 100% imutável contra exclusão ou alteração acidental).\n\n"
            "• CLI (Manipular Atributos Estendidos xattr):\n"
            "  getfattr -d /var/log/syslog\n"
            "  setfattr -n user.projeto -v \"SistemasOperacionais\" arquivo.txt"
        ),

        # Linha 6: Referências Bibliográficas
        (
            "Referências Bibliográficas e Fontes Acadêmicas\n(Livros Didáticos, Normas Internacionais, Artigos Científicos e Documentação Oficial)",
            # Windows 11
            "1. RUSCHINOVICH, Mark E.; IONESCU, Alex. Windows Internals, Part 2: Addressing Infrastructure, Storage, File Systems, and More. 7. ed. Redmond: Microsoft Press, 2021. (Capítulo 8: File Systems; Capítulo 9: NTFS Design and Architecture).\n"
            "2. MICROSOFT CORPORATION. NTFS Technical Reference and Architecture. Microsoft Learn Documentation, 2024. Disponível em: <https://learn.microsoft.com/en-us/windows-server/storage/file-server/ntfs-overview>.\n"
            "3. SILBERSCHATZ, Abraham; GALVIN, Peter Baer; GAGNE, Greg. Operating System Concepts. 10. ed. Hoboken: John Wiley & Sons, 2018. (Capítulo 13: File-System Interface; Capítulo 14: File-System Implementation).\n"
            "4. TANENBAUM, Andrew S.; BOS, Herbert. Sistemas Operacionais Modernos. 4. ed. São Paulo: Pearson Education do Brasil, 2016. (Capítulo 4: Sistemas de Arquivos; Capítulo 11: Windows Vista/7/10 NTFS).",

            # Windows 11 - Comandos
            "• Documentações Oficiais Microsoft Learn:\n"
            "  - Microsoft Learn: 'Resilient File System (ReFS) Overview'\n"
            "  - Microsoft Learn: 'NTFS Self-Healing and File System Corruption Handling'\n"
            "  - Windows Sysinternals File Utilities Reference (Mark Russinovich).",

            # Ubuntu 24.04
            "1. LOVE, Robert. Linux Kernel Development. 3. ed. Upper Saddle River: Addison-Wesley Professional, 2010. (Capítulo 13: The Virtual Filesystem; Capítulo 14: The Block I/O Layer).\n"
            "2. KERRISK, Michael. The Linux Programming Interface: A Linux and UNIX System Programming Handbook. San Francisco: No Starch Press, 2010. (Capítulo 14: File Systems; Capítulo 15: File Attributes; Capítulo 18: Directories and Links).\n"
            "3. BOVET, Daniel P.; CESATI, Marco. Understanding the Linux Kernel. 3. ed. Sebastopol: O'Reilly Media, 2005. (Capítulo 12: The Virtual Filesystem; Capítulo 18: The Ext2 and Ext3/Ext4 Filesystems).\n"
            "4. THE LINUX KERNEL ORGANIZATION. Ext4 Filesystem Documentation. Release 6.8, 2024. Disponível em: <https://docs.kernel.org/filesystems/ext4/>.\n"
            "5. STALLINGS, William. Sistemas Operacionais: Projetos e Princípios Internos. 7. ed. São Paulo: Pearson Education, 2012. (Capítulo 12: Gerenciamento de Arquivos).",

            # Ubuntu 24.04 - Comandos
            "• Manuais Oficiais e Man Pages:\n"
            "  - man 5 ext4\n"
            "  - man 8 tune2fs\n"
            "  - man 8 e2fsck\n"
            "  - man 1 stat\n"
            "  - man 1 chattr\n"
            "  - Linux VFS Documentation: <https://www.kernel.org/doc/html/latest/filesystems/vfs.html>"
        )
    ]

    # Column widths
    worksheet.set_column(0, 0, 24, topic_fmt)
    worksheet.set_column(1, 1, 38, content_fmt)
    worksheet.set_column(2, 2, 34, cmd_fmt)
    worksheet.set_column(3, 3, 38, content_fmt)
    worksheet.set_column(4, 4, 34, cmd_fmt)

    # Write data with appropriate row heights
    row_heights = [270, 310, 310, 310, 310, 240]
    start_row = 3
    for i, row in enumerate(data):
        row_num = start_row + i
        h = row_heights[i] if i < len(row_heights) else 260
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
    out_file = os.path.join(out_dir, "modelo_estudo_caso_arquivos_preenchido.xlsx")
    create_filesystems_comparative_spreadsheet(out_file)

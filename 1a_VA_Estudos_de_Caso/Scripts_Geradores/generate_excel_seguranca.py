import xlsxwriter
import os

def create_security_comparative_spreadsheet(filepath):
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet("Estudo de Caso - Seguranca")
    
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
    worksheet.merge_range('A1:E1', 'ESTUDO DE CASO: SEGURANÇA E PROTEÇÃO EM SISTEMAS OPERACIONAIS', title_fmt)
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
        # Linha 1: Introdução a Segurança dos SOs
        (
            "Introdução à Segurança dos SOs\n(Fundamentos, Princípios de Projeto, Tríade CIA e Proteção por Hardware)",
            # Windows 11
            "• Fundamentos e Filosofia de Segurança no Windows 11:\n"
            "  - Arquitetura Zero Trust por Hardware: O Windows 11 estabelece como pré-requisito mandatório a raiz de confiança em hardware (TPM 2.0, UEFI Secure Boot, CPU com VMX/SVM e proteção DMA de kernel).\n"
            "  - Tríade CIA (Confidencialidade, Integridade, Disponibilidade):\n"
            "    * Confidencialidade: Criptografia transparente em repouso (BitLocker) e em trânsito (SMB Encryption/TLS 1.3), além de isolamento de segredos em memória via VBS.\n"
            "    * Integridade: Código em execução no kernel rigorosamente assinado e validado por HVCI (Hypervisor-Protected Code Integrity); Secure Boot protege o processo de inicialização desde a UEFI.\n"
            "    * Disponibilidade: Recuperação automática de falhas, isolamento de processos por anéis de proteção (Ring 3 vs Ring 0) e cotas de recursos do Gerenciador de Objetos.\n"
            "  - Princípios de Saltzer & Schroeder Aplicados:\n"
            "    * Menor Privilégio: Introdução e evolução do UAC (User Account Control), tokens de processo restritos e sandboxing de aplicativos empacotados (AppContainer).\n"
            "    * Defesa em Profundidade: Camadas concêntricas de proteção (Hardware -> Hipervisor Hyper-V -> Kernel NT -> Subsistema Win32 -> Aplicações).",

            # Windows 11 - Comandos
            "• CLI (PowerShell - Inspecionar Segurança por Hardware e VBS):\n"
            "  Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\\Microsoft\\Windows\\DeviceGuard | Format-List SecurityServicesConfigured, SecurityServicesRunning, VirtualizationBasedSecurityStatus\n"
            "  (Verifica se o VBS e a proteção por virtualização estão habilitados e ativos no sistema).\n\n"
            "• CLI (PowerShell - Validar UEFI Secure Boot):\n"
            "  Confirm-SecureBootUEFI\n"
            "  (Retorna 'True' confirmando que a inicialização segura com verificação de assinaturas digitais está ativa).\n\n"
            "• CLI (PowerShell - Consultar Chip TPM 2.0):\n"
            "  Get-Tpm\n"
            "  (Verifica presença, inicialização, especificação do chip TPM 2.0 e status das chaves de endosso).\n\n"
            "• GUI (Informações do Sistema):\n"
            "  msinfo32.exe\n"
            "  (Resumo do Sistema > 'Segurança Baseada em Virtualização', 'Configuração de Bloqueio de Kernel DMA' e 'Estado de Inicialização Segura').",

            # Ubuntu 24.04
            "• Fundamentos e Filosofia de Segurança no Linux (Kernel 6.8):\n"
            "  - Herança Unix e Princípio da Mediação Completa: Todos os acessos a arquivos, dispositivos e sockets de rede são mediados pelo Virtual File System (VFS) e interceptados pelos hooks dos Linux Security Modules (LSM).\n"
            "  - Tríade CIA (Confidencialidade, Integridade, Disponibilidade):\n"
            "    * Confidencialidade: Criptografia de disco em nível de bloco (LUKS2/dm-crypt) e controle de permissões no sistema de arquivos (POSIX DAC, ACLs e AppArmor).\n"
            "    * Integridade: Módulos de kernel validados criptograficamente (Kernel Module Signing), suporte a UEFI Secure Boot com 'shim' e modo Kernel Lockdown ativado em nível 'integrity'.\n"
            "    * Disponibilidade: Limites rígidos de recursos por processo via cgroups v2, limites de arquivos abertos (pam_limits / ulimit) e OOM Killer (Out-Of-Memory Killer) determinístico.\n"
            "  - Princípios de Saltzer & Schroeder Aplicados:\n"
            "    * Menor Privilégio: Fragmentação do superusuário root em dezenas de Linux Capabilities independentes; uso extensivo de 'sudo' para privilégios temporários auditáveis.\n"
            "    * Economia de Mecanismo e Transparência: Código-fonte do kernel aberto para auditoria contínua pela comunidade global e pesquisadores de cibersegurança.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Validar UEFI Secure Boot):\n"
            "  mokutil --sb-state\n"
            "  (Informa se o Secure Boot está 'SecureBoot enabled' ou 'disabled' via Machine Owner Key).\n\n"
            "• CLI (Auditoria Global de Segurança do Sistema):\n"
            "  systemd-analyze security\n"
            "  (Mede a pontuação de exposição e nível de isolamento de todos os daemons e serviços ativos).\n\n"
            "• CLI (Verificar Modo Lockdown do Kernel):\n"
            "  cat /sys/kernel/security/lockdown\n"
            "  (Exibe o status do lockdown: '[none]', 'integrity' ou 'confidentiality').\n\n"
            "• CLI (Verificar Suporte a TPM 2.0):\n"
            "  dmesg | grep -iE 'tpm|security|apparmor'\n"
            "  (Exibe o anel de mensagens do kernel confirmando a inicialização do driver TPM e dos módulos LSM)."
        ),

        # Linha 2: Principais Ameaças Sofridas (Pontos Fracos)
        (
            "Quais as principais ameaças sofridas pelo SO?\n(Principais pontos fracos, superfície de ataque e vetores de exploração)",
            # Windows 11
            "• Superfície de Ataque e Ameaças Críticas no Windows 11:\n"
            "  1. Ransomware Corporativo e Trojans Focados em Usuário:\n"
            "     - Maior base de estações de trabalho e endpoints do mundo corporativo, atraindo 85%+ do volume global de ameaças financeiras, trojans bancários e infecções por phishing/engenharia social.\n"
            "  2. Ataque BYOVD (Bring Your Own Vulnerable Driver):\n"
            "     - Atacantes instalam drivers antigos e legítimos de fabricantes terceiros com assinatura válida da Microsoft, mas que possuem falhas conhecidas de buffer overflow. Através deles, executam código em Ring 0 e desativam o EDR/Antivírus.\n"
            "  3. Abuso de Binários Legítimos (LOLBins - Living off the Land Binaries):\n"
            "     - Utilização de utilitários legítimos do SO (ex.: powershell.exe, mshta.exe, certutil.exe, rundll32.exe, wmic.exe) para baixar e executar payloads maliciosos sem disparar alertas de antivírus tradicional.\n"
            "  4. Extração de Credenciais em Memória (LSASS Dumping):\n"
            "     - O processo lsass.exe armazena hashes NTLM e tíquetes Kerberos na memória RAM para logon único (SSO); ferramentas como Mimikatz visam roubar esses artefatos para ataques de Pass-the-Hash e movimento lateral em redes Active Directory.\n"
            "  5. Complexidade e Código Legado:\n"
            "     - Trilhões de linhas de código acumuladas com retrocompatibilidade para aplicações Win32 de décadas passadas mantêm superfície exposta a falhas de corrupção de memória.",

            # Windows 11 - Comandos
            "• CLI (PowerShell - Auditar Tentativas de Login com Sucesso e Falha):\n"
            "  Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624,4625} -MaxEvents 15 | Select-Object TimeCreated, Id, Message\n"
            "  (Permite auditar eventos de logon: 4624 = Sucesso, 4625 = Falha por senha incorreta/ataque de força bruta).\n\n"
            "• CLI (PowerShell - Monitorar Execução de Processos Suspeitos - Evento 4688):\n"
            "  Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} -MaxEvents 10 | Format-Table TimeCreated, Message -Wrap\n"
            "  (Identifica processos filhos criados recentemente, fundamental para rastrear abusos de LOLBins).\n\n"
            "• CLI (Inspecionar Drivers de Filtro em Execução):\n"
            "  fltmc.exe\n"
            "  (Lista drivers de minifiltro do sistema de arquivos para auditar agentes de segurança e potenciais interceptadores).\n\n"
            "• GUI (Visualizador de Eventos):\n"
            "  eventvwr.msc > Logs do Windows > Segurança\n"
            "  (Interface gráfica para inspeção granular de eventos de autenticação, elevação de privilégio e auditoria).",

            # Ubuntu 24.04
            "• Superfície de Ataque e Ameaças Críticas no Linux (Ubuntu 24.04):\n"
            "  1. Ataques Remotos a Serviços e Daemons de Rede Expostos:\n"
            "     - Predominância massiva em servidores web, servidores de nuvem e roteadores. As principais ameaças exploram portas abertas (ex.: SSH, HTTP/HTTPS, APIs) via varreduras automatizadas, ataques de força bruta e injeções de código em serviços expostos.\n"
            "  2. Escalonamento de Privilégios Locais (LPE - Local Privilege Escalation):\n"
            "     - Uma vez que o atacante obtém acesso sem privilégios (usuário comum ou 'www-data'), busca vulnerabilidades no kernel Linux (ex.: falhas históricas como Dirty COW, Dirty Pipe, use-after-free em netfilter/io_uring) ou exploração de daemons com privilégios de sistema (ex.: Polkit/PwnKit) para saltar para o UID 0 (root).\n"
            "  3. Abuso de Binários SUID Mal Configurados:\n"
            "     - Executáveis com o bit SUID ativo rodam com privilégios de root; permissões indevidas em binários com funções de shell escape (catálogo GTFOBins) permitem obtenção instantânea de terminal root.\n"
            "  4. Supply Chain Attacks em Repositórios e Contêineres:\n"
            "     - Inclusão de código malicioso em pacotes de repositórios upstream, PPAs comunitários ou dependências em ecossistemas de desenvolvimento (npm, pip); imagens maliciosas do Docker Hub.\n"
            "  5. Container Escape (Quebra de Isolamento):\n"
            "     - Em ambientes Docker/Kubernetes, contêineres compartilham o mesmo kernel do host. Falhas de configuração (modo '--privileged') ou vulnerabilidades em runtimes (runc) permitem que o invasor escape do namespace e assuma o controle do nó host.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Varredura de Binários SUID Perigosos):\n"
            "  find / -perm -4000 -type f -exec ls -la {} + 2>/dev/null\n"
            "  (Varre todo o sistema em busca de executáveis com permissão SUID root ativa, auditando vetores de LPE).\n\n"
            "• CLI (Inspecionar Sockets e Portas em Escuta):\n"
            "  ss -tulpen\n"
            "  (Exibe todos os sockets TCP e UDP abertos, portas de escuta e os respectivos processos e UIDs proprietários).\n\n"
            "• CLI (Monitorar Força Bruta contra o Daemon SSH):\n"
            "  sudo journalctl -u ssh -g \"Failed password\" -n 15\n"
            "  (Exibe as últimas tentativas fracassadas de autenticação por senha no serviço OpenSSH).\n\n"
            "• CLI (Histórico de Logins Inválidos no Sistema):\n"
            "  sudo lastb -n 10\n"
            "  (Lê o arquivo binário /var/log/btmp e lista os últimos logins rejeitados por credenciais incorretas)."
        ),

        # Linha 3: Técnicas de Criptografia Aplicadas
        (
            "Técnicas de criptografia são aplicadas?\nQuais são as técnicas e o que pode ser protegido com elas no SO?\n(FDE, Criptografia de Arquivos, Proteção de Chaves e Comunicação)",
            # Windows 11
            "• Sim, o Windows 11 aplica criptografia extensiva em múltiplos subsistemas:\n"
            "  1. Criptografia de Volume Completo (FDE - Full Disk Encryption):\n"
            "     - BitLocker Drive Encryption: Criptografa o volume do sistema utilizando os algoritmos XTS-AES de 128 ou 256 bits.\n"
            "     - Ancoragem no Hardware TPM 2.0: As chaves mestras de criptografia do volume (VMK) são seladas no chip TPM e liberadas apenas se os registradores de configuração de plataforma (PCRs 7 e 11) confirmarem que a cadeia de boot (UEFI, bootloader, kernel) não foi adulterada.\n"
            "     - BitLocker To Go: Estende a criptografia para pendrives e discos removíveis externos.\n"
            "  2. Criptografia em Nível de Arquivo e Diretório:\n"
            "     - EFS (Encrypting File System): Integrado ao NTFS. Utiliza criptografia híbrida: o arquivo é criptografado com chave simétrica AES rápida (FEK - File Encryption Key), e a FEK é criptografada com a chave pública assimétrica RSA do certificado do usuário (armazenada via DPAPI).\n"
            "  3. Proteção de Credenciais e Chaves de Sistema:\n"
            "     - DPAPI (Data Protection API): Primitiva de criptografia do SO que protege senhas salvas, certificados de rede e cookies de navegadores com base na chave de logon do usuário.\n"
            "     - Windows Defender Credential Guard: Utiliza VSM (Virtual Secure Mode) para isolar os segredos do processo LSASS em uma partição de memória virtual segura inacessível até mesmo para um atacante com privilégios de kernel NT.\n"
            "  4. Comunicação Segura de Rede:\n"
            "     - Suporte nativo a SMB Encryption (AES-128-GCM e AES-256-GCM) para tráfego de rede e pilha Schannel para TLS 1.3.",

            # Windows 11 - Comandos
            "• CLI (Gerenciamento e Auditoria Completa do BitLocker):\n"
            "  manage-bde -status\n"
            "  (Exibe o status de criptografia de todos os volumes, método de cifra XTS-AES, status de proteção e proteção por TPM).\n\n"
            "• CLI (PowerShell - Obter Detalhes do Volume BitLocker):\n"
            "  Get-BitLockerVolume -MountPoint \"C:\" | Format-List VolumeType, MountPoint, EncryptionMethod, VolumeStatus, KeyProtector\n"
            "  (Detalha os protetores de chave ativos: TPM, chave de recuperação numérica e PIN).\n\n"
            "• CLI (Inspecionar Arquivos Criptografados via EFS):\n"
            "  cipher /c \"C:\\Caminho\\Arquivo.txt\"\n"
            "  (Exibe o certificado do usuário proprietário e a chave de recuperação do arquivo cifrado por EFS).\n\n"
            "• GUI (Painel de Controle):\n"
            "  control.exe /name Microsoft.BitLockerDriveEncryption\n"
            "  (Interface gráfica para ativar, suspender proteção e salvar chave de recuperação no Azure AD / conta Microsoft).",

            # Ubuntu 24.04
            "• Sim, o Ubuntu 24.04 implementa criptografia robusta de ponta a ponta:\n"
            "  1. Criptografia de Volume Completo (FDE - Full Disk Encryption):\n"
            "     - LUKS2 (Linux Unified Key Setup v2) sobre dm-crypt: Padrão da indústria para criptografia de dispositivos de bloco do kernel Linux. Utiliza cifras AES-XTS-plain64 de 256 ou 512 bits via Crypto API nativa do kernel.\n"
            "     - Integração com TPM 2.0 (systemd-cryptenroll): Permite vincular o desbloqueio do volume LUKS2 aos registradores PCR do chip TPM 2.0 (PCR 0, 2, 7), permitindo decriptação automática segura e resistência a ataques offline de roubo de disco.\n"
            "  2. Criptografia em Nível de Sistema de Arquivos (Per-Directory Encryption):\n"
            "     - fscrypt: Módulo integrado nativamente aos sistemas de arquivos ext4 e f2fs. Permite que diretórios individuais sejam criptografados de forma transparente com chaves atreladas a senhas de usuários ou PAM, com desempenho superior ao legado eCryptfs.\n"
            "  3. Proteção de Credenciais e Chaves de Sistema:\n"
            "     - Linux Kernel Keyrings (keyrings): Subsistema de gerenciamento de chaves seguro mantido pelo kernel, permitindo que processos armazenem chaves de sessão e tokens sem expô-los em memória de usuário.\n"
            "     - Criptografia de Senhas em /etc/shadow: Algoritmos modernos de derivação de chave resistentes a GPU (yescrypt e sha512crypt) com salt dinâmico único de 64 bits por usuário.\n"
            "  4. Comunicação Segura de Rede:\n"
            "     - Protocolo OpenSSH nativo (SSHv2 com cifras modernas ChaCha20-Poly1305 e Curve25519) e túneis VPN WireGuard integrados diretamente ao kernel Linux.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Consultar Status da Criptografia dm-crypt Ativa):\n"
            "  sudo cryptsetup status dm_crypt-0\n"
            "  (Informa dispositivo subjacente, algoritmo de cifra ex.: aes-xts-plain64, tamanho da chave de 512 bits e setor inicial).\n\n"
            "• CLI (Inspecionar Cabeçalho e Chaves do LUKS2):\n"
            "  sudo cryptsetup luksDump /dev/nvme0n1p3\n"
            "  (Exibe versão do LUKS, UUID, algoritmo KDF argon2id, tempo de derivação e slots de chaves ocupados).\n\n"
            "• CLI (Consultar Vinculação com TPM 2.0 via systemd):\n"
            "  systemd-cryptenroll /dev/nvme0n1p3 --tpm2-device=list\n"
            "  (Lista os dispositivos TPM2 disponíveis e parâmetros para enrolamento de chaves de boot medido).\n\n"
            "• CLI (Inspecionar o Anel de Chaves de Segurança do Kernel):\n"
            "  keyctl show\n"
            "  (Exibe as chaves de criptografia e credenciais alocadas no anel de chaves do kernel do Linux para a sessão atual)."
        ),

        # Linha 4: Autenticação e Controle de Acesso aos Dados
        (
            "Como é feita a autenticação e controle de acesso aos dados?\n(DAC, MAC, RBAC, Estrutura de Permissões, PAM, SIDs, Tokens e Biometria)",
            # Windows 11
            "• Arquitetura de Controle de Acesso e Autenticação no Windows 11:\n"
            "  1. Modelos de Controle de Acesso Implementados:\n"
            "     - DAC (Discretionary Access Control): Cada objeto possui proprietário que define permissões via listas de controle de acesso discricionárias (DACLs).\n"
            "     - MAC Suplementar via MIC (Mandatory Integrity Control): Mecanismo mandatório do Windows. Classifica processos e objetos em 4 níveis de integridade: Untrusted, Low (apps sandboxed), Medium (usuários normais), High (administradores elevados) e System (serviços de kernel). Impede que um processo de nível inferior escreva em processos superiores (regra 'No-Write-Up').\n"
            "     - Suporte a RBAC e CBAC (Dynamic Access Control): Controle de acesso baseado em funções e reivindicações de atributos (Claims) de usuário/dispositivo em ambientes Active Directory.\n"
            "  2. Estrutura de Permissões (Security Descriptors e Tokens):\n"
            "     - SIDs (Security Identifiers): Identificadores únicos globais atribuídos a usuários e grupos (ex.: S-1-5-21...).\n"
            "     - Access Token: Criado pelo processo LSASS no momento do logon. Contém o SID do usuário, SIDs de grupos pertencentes, privilégios de sistema (Privileges) e o nível de integridade MIC. Toda thread herda o token do processo pai.\n"
            "     - Security Descriptor: Cada recurso (arquivo, chave de registro, mutex) possui um descritor de segurança contendo Owner SID, Group SID, DACL (ACEs de 'Permitir' ou 'Negar') e SACL (System Access Control List - para auditoria).\n"
            "  3. Mecanismos de Autenticação:\n"
            "     - Windows Hello: Autenticação biométrica (facial infravermelho e impressão digital) e PIN baseado no padrão FIDO2. As chaves privadas assimétricas nunca saem do chip TPM.\n"
            "     - Kerberos v5: Protocolo de autenticação padrão para redes e domínios corporativos baseados em tíquetes criptográficos (TGT e Service Tickets).\n"
            "     - NTLMv2: Protocolo desafio-resposta mantido por compatibilidade para autenticação local e legado.",

            # Windows 11 - Comandos
            "• CLI (Visualizar Token Completo do Processo Atual):\n"
            "  whoami /all\n"
            "  (Exibe nome da conta, SID de usuário, todos os grupos com seus respectivos SIDs, atributos e privilégios ativos).\n\n"
            "• CLI (Auditar Privilégios do Token de Segurança):\n"
            "  whoami /priv\n"
            "  (Lista privilégios do token, ex.: SeBackupPrivilege, SeDebugPrivilege, e se estão 'Habilitados' ou 'Desabilitados').\n\n"
            "• CLI (Consultar e Gerenciar Listas de Controle de Acesso - DACL):\n"
            "  icacls \"C:\\Caminho\\Pasta\" /t\n"
            "  (Exibe as entradas de controle de acesso (ACEs), usuários concedidos e permissões de herança: (OI)(CI)(F)).\n\n"
            "• GUI (Gerenciamento do Computador):\n"
            "  lusrmgr.msc (Usuários e Grupos Locais) e secpol.msc (Política de Segurança Local - Políticas de Conta e Auditoria).",

            # Ubuntu 24.04
            "• Arquitetura de Controle de Acesso e Autenticação no Linux (Ubuntu 24.04):\n"
            "  1. Modelos de Controle de Acesso Implementados:\n"
            "     - DAC Clássico Unix: Modelo de 3 classes (Owner, Group, Others) com permissões 'rwx' (Leitura, Escrita, Execução) e bits especiais (SUID - executa como dono, SGID - herda grupo, Sticky Bit - restringe exclusão em /tmp).\n"
            "     - POSIX ACLs: Extensão que permite definir permissões discricionárias detalhadas para múltiplos usuários e grupos específicos em um mesmo arquivo (além do trio padrão dono/grupo/outros).\n"
            "     - MAC Avançado (Mandatory Access Control): AppArmor ativo por padrão no Ubuntu (e suporte opcional a SELinux). Confinamento forçado e obrigatório de processos com base em perfis pré-definidos de sistema, ignorando privilégios de usuário.\n"
            "  2. Estrutura de Permissões e Fragmentação do Root:\n"
            "     - Identificadores Numéricos: UID (User ID, sendo UID 0 reservado ao root) e GID (Group ID).\n"
            "     - Linux Capabilities: Fragmenta o poder onipotente do root em mais de 40 capacidades atômicas (ex.: CAP_NET_BIND_SERVICE para abrir portas <1024 sem ser root, CAP_SYS_ADMIN, CAP_DAC_OVERRIDE), mitigando o princípio do menor privilégio.\n"
            "     - Namespaces e cgroups v2: Fornecem isolamento de visualização (PID, Rede, Pontos de Montagem, Usuários) e cotas de recursos físicos (CPU, Memória, E/S).\n"
            "  3. Mecanismos de Autenticação:\n"
            "     - PAM (Pluggable Authentication Modules): Arquitetura flexível e modular (/etc/pam.d/) que intercepta todos os pedidos de autenticação (login, sshd, sudo, su). Permite intercalar senhas com biometria (fprintd), chaves FIDO2/U2F e tokens MFA (Google Authenticator).\n"
            "     - Arquivo /etc/shadow: Armazena hashes criptográficos de senha isolados, com permissão de leitura restrita exclusivamente ao root (0640 / 0600).\n"
            "     - Mecanismo Sudo: Delegação controlada de comandos administrativos (/etc/sudoers) com auditoria detalhada via syslog.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Inspecionar Permissões Tradicionais DAC e Bits Especiais):\n"
            "  ls -l /usr/bin/passwd\n"
            "  (Exibe o bit SUID ativo 'rwsr-xr-x' permitindo que usuários normais atualizem seu hash em /etc/shadow com segurança).\n\n"
            "• CLI (Consultar e Definir POSIX ACLs Detalhadas):\n"
            "  getfacl /var/log/syslog\n"
            "  setfacl -m u:aluno:rw- /var/log/syslog\n"
            "  (Exibe a ACL estendida e adiciona permissão de leitura e escrita para um usuário específico sem alterar o dono).\n\n"
            "• CLI (Auditar Capabilities de Executáveis de Sistema):\n"
            "  sudo getcap -r /usr/bin/\n"
            "  (Lista binários com capabilities especiais atribuídas, ex.: ping com 'cap_net_raw+ep' dispensando ser SUID root).\n\n"
            "• CLI (Inspecionar Configuração Modular do PAM):\n"
            "  cat /etc/pam.d/common-auth\n"
            "  (Visualiza os módulos de autenticação requeridos e a pilha de políticas de login do sistema)."
        ),

        # Linha 5: Ferramentas do Próprio SO para Impedir Malware
        (
            "Quais ferramentas, do próprio SO, são utilizadas para impedir ataques de diversos tipos de malware?\nComo funcionam?\n(Antivírus, EDR, Proteções de Memória, Sandboxing, Isolamento de Núcleo e Firewalls)",
            # Windows 11
            "• Conjunto de Ferramentas Nativas Antimalware do Windows 11:\n"
            "  1. Microsoft Defender Antivirus & EDR Integrado:\n"
            "     - Proteção em tempo real com mecanismos de inteligência em nuvem (Cloud Protection) e verificação comportamental contínua.\n"
            "     - AMSI (Antimalware Scan Interface): Interface do SO que intercepta comandos e scripts executados por interpretadores (PowerShell, VBScript, WScript, VBA/Office) após sua desofuscação na memória RAM, enviando o payload cru para análise do Defender antes da execução.\n"
            "  2. Isolamento de Núcleo e VBS (Virtualization-Based Security):\n"
            "     - HVCI (Hypervisor-Protected Code Integrity): Utiliza o hipervisor Hyper-V para isolar o ambiente seguro VSM (Virtual Secure Mode). Garante que nenhuma página de código executável do kernel seja modificada em tempo de execução (regra W^X: Write XOR Execute) e valida que todos os drivers possuem assinaturas digitais confiáveis antes da carga no kernel.\n"
            "  3. Exploit Protection (Windows Defender Exploit Guard):\n"
            "     - DEP (Data Execution Prevention / NX Bit): Impede a execução de código malicioso alocado na pilha (Stack) ou no Heap de memória.\n"
            "     - ASLR Mandatório e de Alta Entropia: Randomiza dinamicamente as posições de memória de módulos, executáveis e pilhas a cada execução, inviabilizando ataques de Return-Oriented Programming (ROP) e estouro de buffer.\n"
            "     - CFG (Control Flow Guard) e XFG: Adiciona validação de integridade de fluxo em ponteiros de função indiretos para impedir desvios de execução maliciosos.\n"
            "  4. UAC (User Account Control) & SmartScreen:\n"
            "     - UAC executa administradores por padrão com token limitado de usuário comum, exigindo elevação explícita.\n"
            "     - Microsoft Defender SmartScreen: Avalia reputação de URLs e executáveis baixados da internet contra listas de bloqueio em nuvem.",

            # Windows 11 - Comandos
            "• CLI (PowerShell - Obter Status Detalhado do Microsoft Defender):\n"
            "  Get-MpComputerStatus | Select-Object AMServiceEnabled, RealTimeProtectionEnabled, AntivirusSignatureVersion, QuickScanAge\n"
            "  (Informa se o serviço do Defender, proteção em tempo real e assinaturas em nuvem estão funcionando).\n\n"
            "• CLI (PowerShell - Consultar Mitigações de Exploração de Memória Ativas):\n"
            "  Get-ProcessMitigation -System\n"
            "  (Exibe as políticas globais de DEP, ASLR, CFG e SEHOP aplicadas a todos os processos do sistema).\n\n"
            "• CLI (PowerShell - Iniciar Varredura Antimalware via Linha de Comando):\n"
            "  Start-MpScan -ScanType QuickScan\n"
            "  (Dispara uma varredura rápida imediata nos processos em execução e locais de persistência de malware).\n\n"
            "• GUI (Segurança do Windows):\n"
            "  windowsdefender:// (Proteção contra vírus e ameaças > Isolamento de Núcleo > 'Integridade da Memória' ativada).",

            # Ubuntu 24.04
            "• Conjunto de Ferramentas Nativas Antimalware no Ubuntu 24.04:\n"
            "  1. AppArmor (Mandatory Access Control por Perfis):\n"
            "     - Confinamento Mandatório Baseado em Caminhos: Opera como um Linux Security Module (LSM) dentro do kernel. Associa perfis rigorosos a binários vulneráveis (ex.: Firefox, evince, daemons de rede, snap apps). Mesmo se um malware explorar uma vulnerabilidade de zero-day ou buffer overflow no aplicativo, o AppArmor bloqueia sumariamente qualquer tentativa de acessar arquivos fora do perfil (ex.: impede leitura de /etc/shadow ou execução de /bin/sh).\n"
            "  2. UFW (Uncomplicated Firewall) e Pilha Netfilter/nftables:\n"
            "     - Firewall de filtragem de pacotes e inspeção com estado integrado ao kernel Linux. Bloqueia tentativas de conexão de rede de entrada não solicitadas, varreduras de portas e comunicação de Command & Control (C2).\n"
            "  3. Mitigações de Memória e Endurecimento do Kernel Linux:\n"
            "     - KASLR (Kernel Address Space Layout Randomization): Randomiza a base de endereçamento das estruturas do próprio kernel no boot.\n"
            "     - SECCOMP (Secure Computing Mode): Permite que processos declarem filtros restritivos de chamadas de sistema (syscalls). Qualquer tentativa do processo (ou de um malware injetado nele) de invocar uma syscall proibida resulta no encerramento imediato do processo via SIGSYS.\n"
            "     - Proteções de Compilação Ativas (GCC / Glibc): Fortify Source, Canários de Pilha (Stack Smashing Protector - fstack-protector-strong) e execução desabilitada no hardware (No-Execute / NX bit).\n"
            "  4. Subsistema de Auditoria de Segurança (Auditd):\n"
            "     - Módulo de rastreamento do kernel que monitora e gera alertas imediatos para chamadas de sistema suspeitas, modificações de arquivos críticos (/etc/passwd, /etc/sudoers) e tentativas de elevação de privilégio.",

            # Ubuntu 24.04 - Comandos
            "• CLI (Inspecionar Status do AppArmor e Processos Confinados):\n"
            "  sudo aa-status\n"
            "  (Exibe o número de perfis carregados em modo 'enforce', modo 'complain' e todos os processos atualmente confinados).\n\n"
            "• CLI (Gerenciar e Auditar o Firewall Nativo UFW):\n"
            "  sudo ufw status verbose\n"
            "  (Exibe o estado do firewall do sistema, políticas padrão de entrada/saída e portas de rede liberadas).\n\n"
            "• CLI (Consultar Registros de Violação de Segurança do AppArmor):\n"
            "  sudo ausearch -m avc -ts recent   # ou: sudo dmesg | grep -i apparmor\n"
            "  (Filtra eventos em tempo real onde o AppArmor bloqueou ações ilegais tentadas por processos confinados).\n\n"
            "• CLI (Inspecionar Parâmetros de Endurecimento do Kernel Linux):\n"
            "  sysctl kernel.kptr_restrict kernel.dmesg_restrict kernel.unprivileged_bpf_disabled\n"
            "  (Verifica proteções contra vazamento de ponteiros de memória e restrições a eBPF não privilegiado)."
        ),

        # Linha 6: Referências Bibliográficas
        (
            "Referências Bibliográficas e Fontes Acadêmicas\n(Livros Didáticos, Normas Internacionais, Artigos Científicos e Documentação Oficial)",
            # Windows 11
            "1. RUSCHINOVICH, Mark E.; SOLOMON, David A.; IONESCU, Alex. Windows Internals, Part 1: System architecture, processes, threads, memory management, and more. 7. ed. Redmond: Microsoft Press, 2017. (Capítulo 7: Security).\n"
            "2. RUSCHINOVICH, Mark E.; IONESCU, Alex. Windows Internals, Part 2: Addressing Infrastructure, Storage, File Systems, and More. 7. ed. Redmond: Microsoft Press, 2021.\n"
            "3. MICROSOFT CORPORATION. Windows Security Architecture and Mitigation Documentation. Microsoft Learn, 2024. Disponível em: <https://learn.microsoft.com/en-us/windows/security/>.\n"
            "4. CENTER FOR INTERNET SECURITY. CIS Microsoft Windows 11 Enterprise Benchmark v3.0.0. CIS, 2024. Disponível em: <https://www.cisecurity.org/cis-benchmarks/>.\n"
            "5. SILBERSCHATZ, Abraham; GALVIN, Peter Baer; GAGNE, Greg. Operating System Concepts. 10. ed. Hoboken: John Wiley & Sons, 2018. (Capítulo 16: Security; Capítulo 17: Protection).\n"
            "6. STALLINGS, William. Sistemas Operacionais: Projetos e Princípios Internos. 7. ed. São Paulo: Pearson, 2012. (Capítulo 15: Segurança em Sistemas Operacionais).",

            # Windows 11 - Comandos
            "• Documentações Oficiais Microsoft Learn:\n"
            "  - Microsoft Learn: 'Virtualization-Based Security (VBS) and Hypervisor-Protected Code Integrity (HVCI)'\n"
            "  - Microsoft Learn: 'BitLocker Overview and Architecture'\n"
            "  - Microsoft Learn: 'Windows Defender Exploit Protection Reference'\n"
            "  - Microsoft Learn: 'Antimalware Scan Interface (AMSI) Architecture'\n"
            "  - NIST SP 800-147: 'BIOS Protection Guidelines'\n"
            "  - NIST SP 800-193: 'Platform Firmware Resiliency Guidelines'",

            # Ubuntu 24.04
            "1. LOVE, Robert. Linux Kernel Development. 3. ed. Upper Saddle River: Addison-Wesley, 2010. (Capítulo 14: The Security Subsystem; Capítulo 18: Debugging and Kernel Hardening).\n"
            "2. KERRISK, Michael. The Linux Programming Interface: A Linux and UNIX System Programming Handbook. San Francisco: No Starch Press, 2010. (Capítulo 8: Users and Groups; Capítulo 9: Process Credentials; Capítulo 38: Capabilities).\n"
            "3. TANENBAUM, Andrew S.; BOS, Herbert. Sistemas Operacionais Modernos. 4. ed. São Paulo: Pearson Education do Brasil, 2016. (Capítulo 9: Segurança; Capítulo 10: Estudo de Caso 1: Unix/Linux).\n"
            "4. CANONICAL LTD. Ubuntu Server Guide: Security and Hardening (24.04 LTS). Canonical Documentation, 2024. Disponível em: <https://ubuntu.com/server/docs/security>.\n"
            "5. THE LINUX KERNEL ORGANIZATION. Linux Security Module (LSM) & AppArmor Documentation. Release 6.8, 2024. Disponível em: <https://docs.kernel.org/security/>.\n"
            "6. CENTER FOR INTERNET SECURITY. CIS Ubuntu Linux 24.04 LTS Benchmark v1.0.0. CIS, 2024.",

            # Ubuntu 24.04 - Comandos
            "• Manuais Oficiais e Man Pages:\n"
            "  - man 8 apparmor\n"
            "  - man 8 cryptsetup\n"
            "  - man 8 ufw\n"
            "  - man 7 capabilities\n"
            "  - man 8 systemd-cryptenroll\n"
            "  - Linux Kernel Hardening Documentation: <https://www.kernel.org/doc/html/latest/security/index.html>"
        )
    ]

    # Column widths
    worksheet.set_column(0, 0, 24, topic_fmt)
    worksheet.set_column(1, 1, 38, content_fmt)
    worksheet.set_column(2, 2, 34, cmd_fmt)
    worksheet.set_column(3, 3, 38, content_fmt)
    worksheet.set_column(4, 4, 34, cmd_fmt)

    # Write data with appropriate row heights
    row_heights = [260, 290, 310, 320, 320, 240]
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
    out_file = os.path.join(out_dir, "modelo_estudo_caso_seguranca_preenchido.xlsx")
    create_security_comparative_spreadsheet(out_file)

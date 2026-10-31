import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_security_presentation(filepath):
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

    def add_header(slide, title_text, category_text="ESTUDO DE CASO: SEGURANÇA E PROTEÇÃO EM SISTEMAS OPERACIONAIS"):
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
        p0.font.size = Pt(13)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_WIN_ACCENT

        for item in win_points:
            p = wtf.add_paragraph()
            p.space_before = Pt(3)
            p.level = 0
            if isinstance(item, tuple):
                p.text = f"• {item[0]}: "
                p.font.name = 'Segoe UI'
                p.font.size = Pt(8.5)
                p.font.bold = True
                p.font.color.rgb = COLOR_TEXT_MAIN
                run = p.add_run()
                run.text = item[1]
                run.font.bold = False
                run.font.color.rgb = COLOR_TEXT_MAIN
            else:
                p.text = f"• {item}"
                p.font.name = 'Segoe UI'
                p.font.size = Pt(8.5)
                p.font.color.rgb = COLOR_TEXT_MAIN

        if win_cmds:
            p_sep = wtf.add_paragraph()
            p_sep.space_before = Pt(4)
            p_sep.text = "🔧 Comandos e Ferramentas Práticas:"
            p_sep.font.name = 'Segoe UI'
            p_sep.font.size = Pt(9)
            p_sep.font.bold = True
            p_sep.font.color.rgb = COLOR_WIN_ACCENT

            for cmd in win_cmds:
                p_c = wtf.add_paragraph()
                p_c.space_before = Pt(1.5)
                p_c.text = f"> {cmd}"
                p_c.font.name = 'Consolas'
                p_c.font.size = Pt(7.8)
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
        p0_l.font.size = Pt(13)
        p0_l.font.bold = True
        p0_l.font.color.rgb = COLOR_LNX_ACCENT

        for item in lnx_points:
            p = ltf.add_paragraph()
            p.space_before = Pt(3)
            p.level = 0
            if isinstance(item, tuple):
                p.text = f"• {item[0]}: "
                p.font.name = 'Segoe UI'
                p.font.size = Pt(8.5)
                p.font.bold = True
                p.font.color.rgb = COLOR_TEXT_MAIN
                run = p.add_run()
                run.text = item[1]
                run.font.bold = False
                run.font.color.rgb = COLOR_TEXT_MAIN
            else:
                p.text = f"• {item}"
                p.font.name = 'Segoe UI'
                p.font.size = Pt(8.5)
                p.font.color.rgb = COLOR_TEXT_MAIN

        if lnx_cmds:
            p_sep_l = ltf.add_paragraph()
            p_sep_l.space_before = Pt(4)
            p_sep_l.text = "🔧 Comandos e Ferramentas Práticas:"
            p_sep_l.font.name = 'Segoe UI'
            p_sep_l.font.size = Pt(9)
            p_sep_l.font.bold = True
            p_sep_l.font.color.rgb = COLOR_LNX_ACCENT

            for cmd in lnx_cmds:
                p_c = ltf.add_paragraph()
                p_c.space_before = Pt(1.5)
                p_c.text = f"$ {cmd}"
                p_c.font.name = 'Consolas'
                p_c.font.size = Pt(7.8)
                p_c.font.color.rgb = RGBColor(120, 30, 10)

    # =========================================================================
    # SLIDE 1: Capa
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_NAVY
    bg1.line.color.rgb = COLOR_NAVY

    dec_line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(2.1), Inches(2.5), Inches(0.08))
    dec_line.fill.solid()
    dec_line.fill.fore_color.rgb = RGBColor(0, 190, 255)
    dec_line.line.color.rgb = RGBColor(0, 190, 255)

    title_box = s1.shapes.add_textbox(Inches(1.2), Inches(2.3), Inches(11.0), Inches(3.0))
    ttf = title_box.text_frame
    ttf.word_wrap = True
    
    p = ttf.paragraphs[0]
    p.text = "ESTUDO DE CASO: SEGURANÇA E PROTEÇÃO EM SISTEMAS OPERACIONAIS"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(160, 205, 255)

    p2 = ttf.add_paragraph()
    p2.text = "Segurança, Controle de Acesso, Criptografia e Antimalware"
    p2.font.name = 'Segoe UI'
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(8)

    p3 = ttf.add_paragraph()
    p3.text = "Análise Comparativa: Windows 11 Pro (23H2/24H2) vs. Ubuntu 24.04 LTS (Kernel Linux 6.8)"
    p3.font.name = 'Segoe UI'
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(220, 230, 242)
    p3.space_before = Pt(6)

    meta_box = s1.shapes.add_textbox(Inches(1.2), Inches(5.6), Inches(11.0), Inches(1.3))
    mtf = meta_box.text_frame
    p_meta1 = mtf.paragraphs[0]
    p_meta1.text = "Universidade Federal Rural de Pernambuco (UFRPE) | Bacharelado em Ciência da Computação"
    p_meta1.font.name = 'Segoe UI'
    p_meta1.font.size = Pt(10.5)
    p_meta1.font.color.rgb = RGBColor(180, 205, 230)

    p_meta2 = mtf.add_paragraph()
    p_meta2.text = "Disciplina: Sistemas Operacionais | Docente: Prof. Dr. Douglas Véras"
    p_meta2.font.name = 'Segoe UI'
    p_meta2.font.size = Pt(10.5)
    p_meta2.font.color.rgb = RGBColor(180, 205, 230)
    p_meta2.space_before = Pt(3)

    p_meta3 = mtf.add_paragraph()
    p_meta3.text = "Discentes: Luiz Maranhão & Mário Jorge | Outubro de 2026"
    p_meta3.font.name = 'Segoe UI'
    p_meta3.font.size = Pt(11)
    p_meta3.font.bold = True
    p_meta3.font.color.rgb = RGBColor(0, 210, 255)
    p_meta3.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: Fundamentos e Tríade CIA
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Introdução à Segurança de SOs: Tríade CIA e Princípios")
    
    win_p2 = [
        ("Filosofia de Segurança", "Arquitetura Zero Trust por Hardware. Exigência mandatória de TPM 2.0, Secure Boot e VBS/HVCI."),
        ("Confidencialidade", "Criptografia transparente em repouso com BitLocker e isolamento de credenciais na memória via VSM/Credential Guard."),
        ("Integridade", "Assinatura digital obrigatória de drivers e código do kernel, validada criptograficamente pelo hipervisor em tempo de execução."),
        ("Princípios de Saltzer & Schroeder", "Menor Privilégio via UAC e AppContainers; Defesa em Profundidade em camadas concêntricas (Hardware -> Hyper-V -> Kernel -> Win32 -> Apps).")
    ]
    win_c2 = [
        "Confirm-SecureBootUEFI",
        "Get-CimInstance -ClassName Win32_DeviceGuard",
        "Get-Tpm | Select-Object TpmPresent, TpmReady"
    ]

    lnx_p2 = [
        ("Filosofia de Segurança", "Mediação Completa Unix e Módulos LSM. Todos os acessos no VFS são interceptados por políticas de segurança."),
        ("Confidencialidade", "Criptografia de bloco com LUKS2/dm-crypt e controle de acesso estrito no sistema de arquivos (POSIX DAC, ACLs, AppArmor)."),
        ("Integridade", "Kernel Lockdown Mode ativado por padrão com UEFI Secure Boot; validação de assinatura de módulos de kernel (.ko)."),
        ("Princípios de Saltzer & Schroeder", "Fragmentação de privilégios com Linux Capabilities; Economia de Mecanismo e código aberto auditável globalmente.")
    ]
    lnx_c2 = [
        "mokutil --sb-state",
        "systemd-analyze security",
        "cat /sys/kernel/security/lockdown"
    ]
    add_comparison_cards(s2, win_p2, lnx_p2, win_c2, lnx_c2)

    # =========================================================================
    # SLIDE 3: Principais Ameaças Sofridas
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "2. Principais Ameaças Sofridas e Superfície de Ataque")

    win_p3 = [
        ("Foco Predominante", "Maior base de estações e endpoints do mundo; alvo de 85%+ do volume global de ransomware e trojans bancários."),
        ("Ataque BYOVD", "Bring Your Own Vulnerable Driver: atacantes carregam drivers antigos legítimos com falhas para burlar o antivírus em Ring 0."),
        ("Abuso de LOLBins", "Living off the Land Binaries: uso de binários nativos (powershell, certutil, mshta) para descarregar malware sem alertar antivírus."),
        ("LSASS Dumping", "Extração de hashes NTLM e tíquetes Kerberos da memória do processo lsass.exe (Mimikatz, Pass-the-Hash e movimento lateral).")
    ]
    win_c3 = [
        "Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624,4625} -MaxEvents 10",
        "Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} -MaxEvents 10",
        "fltmc.exe (Auditoria de Minifiltros de Sistema de Arquivos)"
    ]

    lnx_p3 = [
        ("Foco Predominante", "Servidores web, nuvem pública e clusters de infraestrutura; varreduras e ataques remotos a serviços expostos."),
        ("Escalonamento Local (LPE)", "Exploração de falhas de memória no kernel (ex.: Dirty COW, Dirty Pipe, bugs em netfilter) para obter UID 0 (root)."),
        ("Abuso de Binários SUID", "Permissões SUID indevidas em binários com brechas de shell escape (catálogo GTFOBins) geram acesso root instantâneo."),
        ("Container Escape", "Quebra de isolamento em contêineres Docker mal configurados ('--privileged'), permitindo controle do nó host compartilhado.")
    ]
    lnx_c3 = [
        "find / -perm -4000 -type f -exec ls -la {} + 2>/dev/null",
        "ss -tulpen (Inspecionar portas abertas e daemons expostos)",
        "sudo journalctl -u ssh -g 'Failed password' -n 15"
    ]
    add_comparison_cards(s3, win_p3, lnx_p3, win_c3, lnx_c3)

    # =========================================================================
    # SLIDE 4: Técnicas de Criptografia
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "3. Técnicas de Criptografia: FDE, Arquivos e Chaves")

    win_p4 = [
        ("Full Disk Encryption (BitLocker)", "Criptografia de volume completo com XTS-AES 128/256 bits acoplada a medições de PCRs 7 e 11 no chip TPM 2.0."),
        ("Criptografia de Arquivo (EFS)", "Encrypting File System no NTFS; cifra híbrida com AES-256 para o arquivo e RSA para a chave simétrica FEK."),
        ("Proteção de Credenciais (DPAPI)", "Data Protection API protege senhas e tokens; Credential Guard isola segredos em partição de memória segura VSM."),
        ("Segurança em Rede", "SMB Encryption nativo com AES-128/256-GCM para tráfego de arquivos e Schannel com TLS 1.3.")
    ]
    win_c4 = [
        "manage-bde -status",
        "Get-BitLockerVolume -MountPoint 'C:' | Format-List",
        "cipher /c 'C:\\Caminho\\Arquivo.txt'"
    ]

    lnx_p4 = [
        ("Full Disk Encryption (LUKS2)", "dm-crypt com AES-XTS-512 bits; suporte a boot medido TPM 2.0 via systemd-cryptenroll (PCRs 0, 2 e 7)."),
        ("Criptografia por Diretório (fscrypt)", "Criptografia nativa em sistemas ext4 e f2fs por pasta, sem sobrecarga de imagens virtuais estáticas."),
        ("Proteção de Credenciais", "Linux Kernel Keyrings para armazenar chaves de sessão no kernel; senhas em /etc/shadow com hashes yescrypt/sha512crypt."),
        ("Segurança em Rede", "OpenSSH nativo com cifras ChaCha20-Poly1305 / Curve25519 e túneis VPN WireGuard integrados ao kernel.")
    ]
    lnx_c4 = [
        "sudo cryptsetup status dm_crypt-0",
        "sudo cryptsetup luksDump /dev/nvme0n1p3",
        "sudo systemd-cryptenroll --tpm2-device=list"
    ]
    add_comparison_cards(s4, win_p4, lnx_p4, win_c4, lnx_c4)

    # =========================================================================
    # SLIDE 5: Autenticação e Controle de Acesso
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "4. Autenticação e Controle de Acesso aos Dados")

    win_p5 = [
        ("Modelos de Acesso", "DAC (DACLs por objeto) complementado por MAC mandatório via MIC (Mandatory Integrity Control com 4 níveis)."),
        ("Estrutura de Segurança", "SIDs identificam entidades; Access Tokens associados a processos contêm SIDs, privilégios e nível MIC."),
        ("Regra de Integridade MIC", "No-Write-Up: processos em integridade inferior não podem escrever ou injetar DLLs em processos superiores."),
        ("Autenticação Moderna", "Windows Hello com biometria facial e FIDO2 ancorado no TPM 2.0; Kerberos v5 para autenticação distribuída.")
    ]
    win_c5 = [
        "whoami /all",
        "whoami /priv",
        "icacls 'C:\\Caminho\\Pasta' /t"
    ]

    lnx_p5 = [
        ("Modelos de Acesso", "DAC clássico Unix (Owner, Group, Others) + POSIX ACLs estendidas + MAC mandatório por perfis via AppArmor."),
        ("Fragmentação do Root", "Linux Capabilities dividem o poder do UID 0 em mais de 40 capacidades atômicas (ex.: CAP_NET_BIND_SERVICE)."),
        ("Isolamento de Processos", "Namespaces isolam tabelas de processos, rede e montagem; cgroups v2 controlam consumo de CPU, RAM e E/S."),
        ("Autenticação Modular", "Arquitetura PAM (/etc/pam.d/) permitindo intercalar senhas com biometria e MFA; delegação granular com sudo.")
    ]
    lnx_c5 = [
        "ls -l /usr/bin/passwd (Bit SUID ativo)",
        "getfacl /var/log/syslog",
        "sudo getcap -r /usr/bin/ (Auditar Capabilities)"
    ]
    add_comparison_cards(s5, win_p5, lnx_p5, win_c5, lnx_c5)

    # =========================================================================
    # SLIDE 6: Ferramentas Nativas Antimalware
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "5. Ferramentas do Próprio SO contra Malware")

    win_p6 = [
        ("Microsoft Defender & AMSI", "Proteção comportamental em nuvem; AMSI desofusca scripts na RAM e inspeciona antes da execução pelo interpretador."),
        ("Isolamento de Núcleo (HVCI)", "Hypervisor-Protected Code Integrity: o hipervisor Hyper-V garante regra W^X e impede injeção de código no kernel."),
        ("Exploit Protection", "Mitigações forçadas de memória: DEP (hardware NX bit), ASLR de alta entropia e CFG (Control Flow Guard)."),
        ("UAC e SmartScreen", "User Account Control força execução padrão sem privilégios; SmartScreen valida reputação de executáveis na web.")
    ]
    win_c6 = [
        "Get-MpComputerStatus | Format-List RealTimeProtection*",
        "Get-ProcessMitigation -System",
        "Start-MpScan -ScanType QuickScan"
    ]

    lnx_p6 = [
        ("AppArmor (LSM)", "Confinamento obrigatório por perfis de caminhos; bloqueia desvios mesmo se o binário sofrer buffer overflow/RCE."),
        ("UFW e Netfilter/nftables", "Firewall de filtragem com estado no kernel; bloqueio de portas não autorizadas e tráfego malicioso de C2."),
        ("Hardening de Kernel", "KASLR randomiza endereços do kernel no boot; SECCOMP restringe syscalls permitidas; Stack Canaries evitam buffer overflow."),
        ("Audit Subsystem (Auditd)", "Módulo de auditoria no kernel que registra execuções privilegiadas e modificações em arquivos críticos.")
    ]
    lnx_c6 = [
        "sudo aa-status",
        "sudo ufw status verbose",
        "sudo ausearch -m avc -ts recent"
    ]
    add_comparison_cards(s6, win_p6, lnx_p6, win_c6, lnx_c6)

    # =========================================================================
    # SLIDE 7: Comandos Práticos e Diagnóstico
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "6. Quadro Resumo: Comandos de Diagnóstico e Auditoria")

    # Table comparing commands
    rows, cols = 7, 3
    left = Inches(0.8)
    top = Inches(1.35)
    width = Inches(11.733)
    height = Inches(5.4)

    table_shape = s7.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(3.2)
    table.columns[1].width = Inches(4.266)
    table.columns[2].width = Inches(4.266)

    headers_tbl = ["Categoria de Segurança", "Windows 11 Pro (PowerShell / CMD)", "Ubuntu 24.04 LTS (Bash / Terminal)"]
    for c_idx, h_text in enumerate(headers_tbl):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = 'Segoe UI'
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

    tbl_data = [
        ("Identidade e Privilégios", "whoami /all\nwhoami /priv", "id\nsudo -l\nsudo getcap -r /usr/bin/"),
        ("Integridade de Boot e Hardware", "Confirm-SecureBootUEFI\nGet-Tpm\nmsinfo32.exe", "mokutil --sb-state\nsystemd-analyze security\ncat /sys/kernel/security/lockdown"),
        ("Auditoria de Criptografia", "manage-bde -status\nGet-BitLockerVolume -MountPoint 'C:'\ncipher /c 'arquivo.txt'", "sudo cryptsetup status dm_crypt-0\nsudo cryptsetup luksDump /dev/nvme0n1p3\nsystemd-cryptenroll --tpm2-device=list"),
        ("Controle de Acesso / ACLs", "icacls 'C:\\Pasta' /t\nsecedit /export /cfg C:\\secpol.inf", "ls -l /arquivo\ngetfacl /arquivo\nsudo setfacl -m u:aluno:rwx arquivo"),
        ("Defesa Antimalware / EDR", "Get-MpComputerStatus\nGet-ProcessMitigation -System\nStart-MpScan -ScanType QuickScan", "sudo aa-status\nsudo ufw status verbose\nsudo ausearch -m avc -ts recent"),
        ("Auditoria de Logons e Ameaças", "Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624,4625}\nfltmc.exe", "sudo journalctl -u ssh -g 'Failed password'\nsudo lastb -n 10\nss -tulpen")
    ]

    for r_idx, row in enumerate(tbl_data, start=1):
        for c_idx, cell_value in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if r_idx % 2 == 0 else COLOR_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = cell_value
            p.font.name = 'Consolas' if c_idx > 0 else 'Segoe UI'
            p.font.size = Pt(8.5)
            p.font.bold = (c_idx == 0)
            p.font.color.rgb = COLOR_NAVY if c_idx == 0 else COLOR_TEXT_MAIN

    # =========================================================================
    # SLIDE 8: Conclusão Comparativa
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "7. Conclusões e Síntese Comparativa")

    c_w = Inches(5.6)
    c_h = Inches(5.5)
    c_y = Inches(1.35)

    # Win Conclusion Card
    w_card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), c_y, c_w, c_h)
    w_card.fill.solid()
    w_card.fill.fore_color.rgb = COLOR_WIN_BG
    w_card.line.color.rgb = COLOR_WIN_ACCENT
    w_card.line.width = Pt(1.5)
    wtf8 = w_card.text_frame
    wtf8.word_wrap = True
    wtf8.margin_left = Inches(0.35)
    wtf8.margin_right = Inches(0.35)
    wtf8.margin_top = Inches(0.3)
    p = wtf8.paragraphs[0]
    p.text = "Windows 11 Pro: Segurança Centrada em Hardware (Zero Trust)"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_WIN_ACCENT

    win_concl = [
        ("Abordagem Estratégica", "Imposição rigorosa de requisitos de hardware (TPM 2.0, Secure Boot, VBS/HVCI) para criar barreiras invioláveis no Ring -1."),
        ("Vantagens Principais", "Isolamento robusto de segredos (Credential Guard), proteção em tempo real contra scripts (AMSI) e experiência passwordless amigável (Windows Hello)."),
        ("Desafios Centrais", "Superfície de ataque gigantesca herdada por compatibilidade de décadas com código Win32 e vulnerabilidades em drivers de terceiros (BYOVD).")
    ]
    for tit, desc in win_concl:
        p_c = wtf8.add_paragraph()
        p_c.space_before = Pt(8)
        p_c.text = f"• {tit}: "
        p_c.font.name = 'Segoe UI'
        p_c.font.size = Pt(9.5)
        p_c.font.bold = True
        p_c.font.color.rgb = COLOR_TEXT_MAIN
        run = p_c.add_run()
        run.text = desc
        run.font.bold = False

    # Linux Conclusion Card
    l_card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), c_y, c_w, c_h)
    l_card.fill.solid()
    l_card.fill.fore_color.rgb = COLOR_LNX_BG
    l_card.line.color.rgb = COLOR_LNX_ACCENT
    l_card.line.width = Pt(1.5)
    ltf8 = l_card.text_frame
    ltf8.word_wrap = True
    ltf8.margin_left = Inches(0.35)
    ltf8.margin_right = Inches(0.35)
    ltf8.margin_top = Inches(0.3)
    p = ltf8.paragraphs[0]
    p.text = "Ubuntu 24.04 LTS: Confinamento Modular e Mediação Completa"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_LNX_ACCENT

    lnx_concl = [
        ("Abordagem Estratégica", "Herança Unix de controle granular, fragmentação do poder root via Capabilities e confinamento forçado de processos com AppArmor."),
        ("Vantagens Principais", "Transparência total de código, suporte nativo a criptografia de alto desempenho (LUKS2/fscrypt), SECCOMP para sandboxing e flexibilidade em servidores."),
        ("Desafios Centrais", "Dependência de configuração experiente por parte do administrador; riscos de LPE no kernel e misconfigurations em ambientes de contêineres Docker/OCI.")
    ]
    for tit, desc in lnx_concl:
        p_c = ltf8.add_paragraph()
        p_c.space_before = Pt(8)
        p_c.text = f"• {tit}: "
        p_c.font.name = 'Segoe UI'
        p_c.font.size = Pt(9.5)
        p_c.font.bold = True
        p_c.font.color.rgb = COLOR_TEXT_MAIN
        run = p_c.add_run()
        run.text = desc
        run.font.bold = False

    # =========================================================================
    # SLIDE 9: Referências Bibliográficas
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "8. Referências Bibliográficas e Fontes Acadêmicas")

    ref_box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(5.5))
    ref_box.fill.solid()
    ref_box.fill.fore_color.rgb = RGBColor(248, 250, 252)
    ref_box.line.color.rgb = COLOR_CARD_BORDER
    ref_box.line.width = Pt(1)

    rtf = ref_box.text_frame
    rtf.word_wrap = True
    rtf.margin_left = Inches(0.4)
    rtf.margin_right = Inches(0.4)
    rtf.margin_top = Inches(0.3)

    p_r0 = rtf.paragraphs[0]
    p_r0.text = "Literatura Clássica, Normas Internacionais e Documentação Oficial:"
    p_r0.font.name = 'Segoe UI'
    p_r0.font.size = Pt(11)
    p_r0.font.bold = True
    p_r0.font.color.rgb = COLOR_NAVY

    refs = [
        "SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. Operating System Concepts. 10. ed. Hoboken: John Wiley & Sons, 2018. (Cap. 16: Security; Cap. 17: Protection).",
        "TANENBAUM, A. S.; BOS, H. Sistemas Operacionais Modernos. 4. ed. São Paulo: Pearson, 2016. (Cap. 9: Segurança; Cap. 10: Unix/Linux; Cap. 11: Windows).",
        "STALLINGS, W. Sistemas Operacionais: Projetos e Princípios Internos. 7. ed. São Paulo: Pearson, 2012. (Capítulo 15: Segurança em Sistemas Operacionais).",
        "RUSCHINOVICH, M. E.; SOLOMON, D. A.; IONESCU, A. Windows Internals, Part 1 & Part 2. 7. ed. Redmond: Microsoft Press, 2017/2021. (Security Architecture).",
        "LOVE, Robert. Linux Kernel Development. 3. ed. Upper Saddle River: Addison-Wesley, 2010. (Cap. 14: Security Subsystems).",
        "KERRISK, Michael. The Linux Programming Interface. San Francisco: No Starch Press, 2010. (Cap. 8: Users/Groups; Cap. 38: Capabilities).",
        "SALTZER, J. H.; SCHROEDER, M. D. The protection of information in computer systems. Proceedings of the IEEE, v. 63, n. 9, p. 1278-1308, 1975.",
        "CENTER FOR INTERNET SECURITY (CIS). CIS Microsoft Windows 11 Enterprise Benchmark v3.0.0 & CIS Ubuntu Linux 24.04 LTS Benchmark v1.0.0, 2024.",
        "NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. NIST SP 800-147 (BIOS Protection) & SP 800-193 (Platform Firmware Resiliency), 2018.",
        "MICROSOFT CORPORATION & KERNEL.ORG. Windows Security Learn Docs & Linux Kernel Security Documentation (LSM/AppArmor/Lockdown), 2024."
    ]

    for ref in refs:
        p_ref = rtf.add_paragraph()
        p_ref.space_before = Pt(3.5)
        p_ref.text = f"• {ref}"
        p_ref.font.name = 'Segoe UI'
        p_ref.font.size = Pt(8.5)
        p_ref.font.color.rgb = COLOR_TEXT_MAIN

    prs.save(filepath)
    print(f"Presentation generated successfully at: {filepath}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Apresentacoes")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "Apresentacao_Estudo_de_Caso_Seguranca.pptx")
    create_security_presentation(out_file)

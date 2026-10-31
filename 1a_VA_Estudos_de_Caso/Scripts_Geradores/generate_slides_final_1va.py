"""
Apresentação Final — 1ª VA (Sistemas Operacionais, UFRPE)
Windows 11 Pro (23H2/24H2) vs. Ubuntu 24.04 LTS (Kernel 6.8)

Princípios de design aplicados:
  - Um diagrama por slide (esquerda) + tabela comparativa de palavras-chave (direita).
  - Textos curtos (2 a 5 palavras por célula); o detalhamento fica nas NOTAS DO APRESENTADOR.
  - Fundo branco, uma única cor de destaque, cores de marca apenas para identificar cada SO.
  - Indicador de progresso (6 segmentos) mostrando em qual entrega parcial estamos.
"""
import os
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml.ns import qn

# =============================================================================
# DESIGN TOKENS
# =============================================================================
FONT = "Segoe UI"
MONO = "Consolas"

WHITE = RGBColor(255, 255, 255)
BG_PANEL = RGBColor(248, 250, 252)   # slate 50
BG_SOFT = RGBColor(241, 245, 249)    # slate 100
LINE = RGBColor(226, 232, 240)       # slate 200
LINE_MID = RGBColor(203, 213, 225)   # slate 300
MUTED_2 = RGBColor(148, 163, 184)    # slate 400
MUTED = RGBColor(100, 116, 139)      # slate 500
BODY = RGBColor(51, 65, 85)          # slate 700
NAVY_2 = RGBColor(30, 41, 59)        # slate 800
DARK = RGBColor(15, 23, 42)          # slate 900

ACCENT = RGBColor(37, 99, 235)       # cor única de destaque
ACCENT_TINT = RGBColor(219, 234, 254)
WIN = RGBColor(0, 120, 212)
LNX = RGBColor(233, 84, 32)
TEAL = RGBColor(13, 148, 136)
TEAL_TINT = RGBColor(204, 251, 241)
RED = RGBColor(220, 38, 38)
RED_TINT = RGBColor(254, 226, 226)
GREEN = RGBColor(22, 163, 74)
GREEN_TINT = RGBColor(220, 252, 231)

L, C, R = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MID = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE


def I(v):
    return Inches(v)


# =============================================================================
# PRIMITIVAS
# =============================================================================
def write_paras(tf, paras, align=L, spacing=2):
    for i, spec in enumerate(paras):
        t, size, bold, color = spec[:4]
        font = spec[4] if len(spec) > 4 else FONT
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if i > 0 and spacing:
            p.space_before = Pt(spacing)
        r = p.add_run()
        r.text = t
        r.font.name = font
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color


def text(slide, x, y, w, h, paras, align=L, anchor=TOP, spacing=2):
    tb = slide.shapes.add_textbox(I(x), I(y), I(w), I(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    write_paras(tf, paras, align, spacing)
    return tb


def shape(slide, kind, x, y, w, h, fill=None, line=None, lw=1.0, radius=None, dash=False):
    s = slide.shapes.add_shape(kind, I(x), I(y), I(w), I(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
        if dash:
            s.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    if radius is not None:
        try:
            s.adjustments[0] = radius
        except IndexError:
            pass
    try:
        s.shadow.inherit = False
    except Exception:
        pass
    return s


def label(shp, paras, align=C, anchor=MID, margin=0.06, spacing=1):
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = I(margin)
    tf.margin_top = tf.margin_bottom = I(0.02)
    tf.vertical_anchor = anchor
    write_paras(tf, paras, align, spacing)


def arrow(slide, x1, y1, x2, y2, color=MUTED_2, width=1.5, dashed=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, I(x1), I(y1), I(x2), I(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    if dashed:
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    ln = c.line._get_or_add_ln()
    tail = etree.SubElement(ln, qn("a:tailEnd"))
    tail.set("type", "triangle")
    tail.set("w", "med")
    tail.set("len", "med")
    return c


def line_seg(slide, x1, y1, x2, y2, color=LINE, width=1.0):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, I(x1), I(y1), I(x2), I(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    return c


def set_alpha(shp, alpha):
    sf = shp._element.spPr.find(qn("a:solidFill"))
    if sf is not None and len(sf):
        a = etree.SubElement(sf[0], qn("a:alpha"))
        a.set("val", str(int(alpha * 100000)))


def notes(slide, txt):
    slide.notes_slide.notes_text_frame.text = txt


# =============================================================================
# LOGOS (desenhados com formas nativas)
# =============================================================================
def win_logo(slide, x, y, size):
    g = size * 0.06
    q = (size - g) / 2
    for dx in (0, q + g):
        for dy in (0, q + g):
            shape(slide, MSO_SHAPE.RECTANGLE, x + dx, y + dy, q, q, fill=WIN)


def ubuntu_logo(slide, x, y, size):
    shape(slide, MSO_SHAPE.OVAL, x, y, size, size, fill=LNX)
    ring = size * 0.56
    d = shape(slide, MSO_SHAPE.DONUT, x + (size - ring) / 2, y + (size - ring) / 2, ring, ring, fill=WHITE)
    d.adjustments[0] = 0.14
    import math
    cx, cy = x + size / 2, y + size / 2
    dot = size * 0.17
    rad = size * 0.30
    for ang in (0, 120, 240):
        a = math.radians(ang - 90 + 30)
        px = cx + rad * math.cos(a) - dot / 2
        py = cy + rad * math.sin(a) - dot / 2
        shape(slide, MSO_SHAPE.OVAL, px, py, dot, dot, fill=WHITE, line=LNX, lw=max(1.0, size * 4))


# =============================================================================
# ESTRUTURA DE SLIDE
# =============================================================================
MODULES = ["Arquitetura", "Processos", "Memória", "Arquivos", "E/S", "Segurança"]


def header(slide, tag, title, module=None):
    shape(slide, MSO_SHAPE.RECTANGLE, 0, 0, 13.333, 0.05, fill=ACCENT)
    text(slide, 0.75, 0.38, 8.8, 0.25, [(tag.upper(), 9, True, ACCENT)])
    text(slide, 0.75, 0.64, 9.0, 0.6, [(title, 24, True, DARK)])

    if module:
        seg_w, gap = 0.38, 0.08
        x0 = 12.58 - (6 * seg_w + 5 * gap)
        text(slide, x0, 0.36, 6 * seg_w + 5 * gap, 0.22,
             [(f"MÓDULO {module} DE 6  ·  {MODULES[module - 1].upper()}", 7.5, True, MUTED)], align=R)
        for i in range(6):
            col = ACCENT if i + 1 == module else (MUTED_2 if i + 1 < module else LINE)
            shape(slide, MSO_SHAPE.RECTANGLE, x0 + i * (seg_w + gap), 0.64, seg_w, 0.06, fill=col)


def footer(slide, page):
    text(slide, 0.75, 7.02, 9.0, 0.25,
         [("Windows 11 Pro vs. Ubuntu 24.04 LTS   ·   Sistemas Operacionais   ·   UFRPE", 8, False, MUTED_2)])
    text(slide, 11.58, 7.02, 1.0, 0.25, [(f"{page:02d}", 8, True, MUTED)], align=R)


def os_header(slide, x, w, is_win):
    if is_win:
        win_logo(slide, x, 1.62, 0.3)
        text(slide, x + 0.45, 1.56, w - 0.45, 0.6,
             [("Windows 11 Pro", 12, True, DARK), ("23H2 / 24H2", 8.5, False, MUTED)], spacing=0)
    else:
        ubuntu_logo(slide, x, 1.62, 0.32)
        text(slide, x + 0.45, 1.56, w - 0.45, 0.6,
             [("Ubuntu 24.04 LTS", 12, True, DARK), ("Kernel Linux 6.8", 8.5, False, MUTED)], spacing=0)
    shape(slide, MSO_SHAPE.RECTANGLE, x, 2.17, w, 0.03, fill=WIN if is_win else LNX)


# Geometria fixa dos slides de módulo
PX, PY, PW, PH = 0.75, 1.55, 5.15, 4.95       # painel do diagrama
AX, AW = 6.25, 1.45                            # coluna "aspecto"
WX, WW = 7.80, 2.33                            # coluna Windows
LX, LW = 10.25, 2.33                           # coluna Ubuntu
ROW_Y0, ROW_H = 2.30, 0.88


def comparison_table(slide, rows, cli):
    os_header(slide, WX, WW, True)
    os_header(slide, LX, LW, False)

    for i, (aspect, (w_key, w_sub), (l_key, l_sub)) in enumerate(rows):
        y = ROW_Y0 + i * ROW_H
        text(slide, AX, y + 0.14, AW - 0.1, 0.6, [(aspect.upper(), 8, True, MUTED)])
        text(slide, WX, y + 0.12, WW, 0.72, [(w_key, 11, True, DARK), (w_sub, 9, False, MUTED)], spacing=1)
        text(slide, LX, y + 0.12, LW, 0.72, [(l_key, 11, True, DARK), (l_sub, 9, False, MUTED)], spacing=1)
        if i < len(rows) - 1:
            line_seg(slide, AX, y + ROW_H, LX + LW, y + ROW_H, LINE, 0.75)

    if cli:
        y = 5.95
        text(slide, AX, y + 0.17, AW, 0.3, [("COMANDOS", 8, True, MUTED)])
        for x, w, cmd in ((WX, WW, cli[0]), (LX, LW, cli[1])):
            pill = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, 0.55, fill=BG_SOFT, line=LINE, lw=0.75, radius=0.18)
            label(pill, [(cmd, 9, False, DARK, MONO)], align=L, margin=0.12)


def diagram_panel(slide, caption):
    shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, PX, PY, PW, PH, fill=BG_PANEL, radius=0.04)
    text(slide, PX + 0.25, PY + 0.2, PW - 0.5, 0.25, [(caption.upper(), 8, True, MUTED)])


# =============================================================================
# DIAGRAMAS (coordenadas relativas ao painel)
# =============================================================================
def diag_rings(s):
    cx, cy = PX + PW / 2, PY + 2.55
    rings = [
        (2.0, RGBColor(239, 246, 255), RGBColor(191, 219, 254), "RING 3  ·  Aplicações"),
        (1.5, RGBColor(219, 234, 254), RGBColor(147, 197, 253), "RING 0  ·  Kernel"),
        (1.0, RGBColor(191, 219, 254), RGBColor(96, 165, 250), "RING -1  ·  Hipervisor"),
    ]
    for r, fill, ln, lbl in rings:
        shape(s, MSO_SHAPE.OVAL, cx - r, cy - r, 2 * r, 2 * r, fill=fill, line=ln, lw=1)
        text(s, cx - 1.2, cy - r + 0.13, 2.4, 0.3, [(lbl, 8.5, True, NAVY_2)], align=C)
    core = shape(s, MSO_SHAPE.OVAL, cx - 0.5, cy - 0.5, 1.0, 1.0, fill=NAVY_2)
    label(core, [("Hardware", 9, True, WHITE), ("TPM 2.0", 7.5, False, MUTED_2)])
    text(s, PX, cy + 2.08, PW, 0.25, [("Quanto mais ao centro, maior o privilégio", 8.5, False, MUTED)], align=C)


def diag_states(s):
    def node(x, y, t, hot=False):
        n = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + x, PY + y, 1.35, 0.5,
                  fill=ACCENT if hot else WHITE, line=None if hot else LINE_MID, lw=1, radius=0.5)
        label(n, [(t, 10, True, WHITE if hot else DARK)])

    def lbl(x, y, w, t, al=C):
        text(s, PX + x, PY + y, w, 0.25, [(t, 8, False, MUTED)], align=al)

    def arr(x1, y1, x2, y2, col=MUTED_2):
        arrow(s, PX + x1, PY + y1, PX + x2, PY + y2, col, 1.25)

    arr(0.975, 1.25, 0.975, 2.15); lbl(1.05, 1.58, 1.0, "admitido", L)
    arr(1.65, 2.3, 3.5, 2.3, ACCENT); lbl(1.65, 2.03, 1.85, "escalonado")
    arr(3.5, 2.52, 1.65, 2.52); lbl(1.65, 2.57, 1.85, "preempção")
    arr(4.175, 2.15, 4.175, 1.25); lbl(4.25, 1.58, 0.85, "concluído", L)
    arr(3.9, 2.65, 3.0, 3.55); lbl(3.55, 3.02, 1.4, "aguarda E/S", L)
    arr(2.2, 3.55, 1.2, 2.65); lbl(0.15, 3.02, 1.35, "E/S pronta", R)

    node(0.3, 0.75, "Novo")
    node(3.5, 0.75, "Terminado")
    node(0.3, 2.15, "Pronto")
    node(3.5, 2.15, "Executando", hot=True)
    node(1.9, 3.55, "Bloqueado")
    text(s, PX, PY + 4.4, PW, 0.25,
         [("Troca de contexto: registradores salvos e restaurados no PCB", 8.5, False, MUTED)], align=C)


def diag_paging(s):
    tints = [
        (RGBColor(219, 234, 254), RGBColor(96, 165, 250)),
        (RGBColor(204, 251, 241), RGBColor(45, 212, 191)),
        (RGBColor(255, 237, 213), RGBColor(251, 146, 60)),
        (RGBColor(237, 233, 254), RGBColor(167, 139, 250)),
        (RGBColor(226, 232, 240), RGBColor(148, 163, 184)),
    ]
    mapping = {0: 3, 1: 0, 2: None, 3: 4, 4: 1}
    vx, rx, cw, ch = PX + 0.3, PX + 3.6, 1.25, 0.45

    def cy(i):
        return PY + 0.95 + i * 0.55

    text(s, vx, PY + 0.6, cw, 0.3, [("Virtual", 9, True, BODY)], align=C)
    text(s, rx, PY + 0.6, cw, 0.3, [("RAM física", 9, True, BODY)], align=C)

    # setas (desenhadas antes, ficam "por trás" da MMU)
    for p, f in mapping.items():
        col = tints[p][1]
        if f is None:
            arrow(s, vx + cw, cy(p) + ch / 2, rx, PY + 4.25, RED, 1.25, dashed=True)
        else:
            arrow(s, vx + cw, cy(p) + ch / 2, rx, cy(f) + ch / 2, col, 1.25)

    for i in range(5):
        fill, ln = tints[i]
        v = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, vx, cy(i), cw, ch, fill=fill, line=ln, lw=1, radius=0.15)
        label(v, [(f"Página {i}", 9, True, DARK)])

    owner = {f: p for p, f in mapping.items() if f is not None}
    for j in range(5):
        if j in owner:
            fill, ln = tints[owner[j]]
            q = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, rx, cy(j), cw, ch, fill=fill, line=ln, lw=1, radius=0.15)
            label(q, [(f"Quadro {j}", 9, True, DARK)])
        else:
            q = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, rx, cy(j), cw, ch, fill=WHITE, line=LINE_MID, lw=1, radius=0.15, dash=True)
            label(q, [("livre", 9, False, MUTED_2)])

    mmu = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 2.0, PY + 1.45, 1.15, 1.75, fill=NAVY_2, radius=0.1)
    label(mmu, [("MMU", 12, True, WHITE), ("TLB +", 8, False, MUTED_2), ("tabela de", 8, False, MUTED_2), ("páginas", 8, False, MUTED_2)], spacing=0)

    disk = shape(s, MSO_SHAPE.CAN, rx, PY + 3.85, cw, 0.8, fill=BG_SOFT, line=LINE_MID, lw=1)
    label(disk, [("Swap /", 8.5, True, BODY), ("pagefile", 8.5, True, BODY)], spacing=0)
    text(s, PX + 0.3, PY + 4.0, 2.9, 0.6,
         [("Página fora da RAM gera page fault", 8.5, True, RED), ("e é trazida do disco", 8.5, False, MUTED)], spacing=0)


def diag_fs(s):
    # Registro de metadados
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 0.3, PY + 0.7, 2.0, 2.9, fill=WHITE, line=LINE_MID, lw=1, radius=0.05)
    hdr = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 0.3, PY + 0.7, 2.0, 0.45, fill=NAVY_2, radius=0.15)
    label(hdr, [("Inode / Registro MFT", 9, True, WHITE)])
    fields = ["Permissões", "Tamanho", "Datas", "Extents"]
    for k, f in enumerate(fields):
        hot = f == "Extents"
        b = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 0.42, PY + 1.27 + k * 0.55, 1.76, 0.43,
                  fill=ACCENT_TINT if hot else BG_PANEL, line=None, radius=0.2)
        label(b, [(f + ("  →" if hot else ""), 9, hot, ACCENT if hot else BODY)], align=L, margin=0.12)

    # Grade de blocos
    text(s, PX + 2.75, PY + 0.7, 2.1, 0.3, [("Blocos no disco", 9, True, BODY)], align=C)
    ext_a = {(1, c) for c in range(4)}
    ext_b = {(4, c) for c in range(3)}
    used = {(0, 0), (0, 1), (0, 4), (2, 1), (2, 2), (3, 3), (3, 4), (5, 0), (5, 1), (5, 2)}
    for r in range(6):
        for c in range(5):
            x, y = PX + 2.8 + c * 0.42, PY + 1.1 + r * 0.42
            if (r, c) in ext_a:
                fill, ln = ACCENT_TINT, WIN
            elif (r, c) in ext_b:
                fill, ln = RGBColor(255, 237, 213), LNX
            elif (r, c) in used:
                fill, ln = LINE_MID, None
            else:
                fill, ln = WHITE, LINE
            shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, 0.34, 0.34, fill=fill, line=ln, lw=1, radius=0.15)
    ey = PY + 1.27 + 3 * 0.55 + 0.215
    arrow(s, PX + 2.18, ey, PX + 2.8, PY + 1.1 + 0.42 + 0.17, WIN, 1.25)
    arrow(s, PX + 2.18, ey, PX + 2.8, PY + 1.1 + 4 * 0.42 + 0.17, LNX, 1.25)

    # Journal
    text(s, PX + 0.3, PY + 4.07, 0.9, 0.3, [("JOURNAL", 8, True, MUTED)])
    steps = ["1  Registra", "2  Grava", "3  Confirma"]
    for k, st in enumerate(steps):
        x = PX + 1.25 + k * 1.3
        chip = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, PY + 3.95, 1.0, 0.48, fill=WHITE, line=LINE_MID, lw=1, radius=0.3)
        label(chip, [(st, 8.5, True, BODY)])
        if k < 2:
            arrow(s, x + 1.0, PY + 4.19, x + 1.3, PY + 4.19, MUTED_2, 1.25)


def diag_io(s):
    layers = [
        ("Aplicação", RGBColor(241, 245, 249), DARK),
        ("API  ·  ReadFile / read()", RGBColor(226, 232, 240), DARK),
        ("I/O Manager  ·  VFS", RGBColor(203, 213, 225), DARK),
        ("Driver  ·  WDF / módulo .ko", MUTED, WHITE),
        ("Controladora (NVMe, USB)", NAVY_2, WHITE),
    ]
    arrow(s, PX + 0.17, PY + 0.75, PX + 0.17, PY + 3.8, MUTED_2, 1.25)
    for k, (t, fill, fc) in enumerate(layers):
        b = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 0.35, PY + 0.7 + k * 0.66, 2.7, 0.52, fill=fill, radius=0.15)
        label(b, [(t, 9, True, fc)], align=L, margin=0.15)

    cpu = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 3.75, PY + 1.0, 1.1, 0.75, fill=WHITE, line=LINE_MID, lw=1, radius=0.12)
    label(cpu, [("CPU", 11, True, DARK)])
    ram = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 3.75, PY + 3.27, 1.1, 0.66, fill=TEAL_TINT, line=TEAL, lw=1, radius=0.12)
    label(ram, [("RAM", 11, True, TEAL)])

    arrow(s, PX + 3.05, PY + 3.62, PX + 3.75, PY + 3.62, TEAL, 2)
    text(s, PX + 3.05, PY + 3.33, 0.7, 0.25, [("DMA", 8.5, True, TEAL)], align=C)
    arrow(s, PX + 3.05, PY + 3.34, PX + 4.1, PY + 1.75, ACCENT, 1.25, dashed=True)
    text(s, PX + 3.85, PY + 2.3, 1.0, 0.25, [("IRQ", 8.5, True, ACCENT)])
    text(s, PX + 0.3, PY + 4.15, 4.6, 0.6,
         [("O DMA copia os dados direto para a RAM;", 8.5, False, MUTED),
          ("a CPU só é avisada no fim, por interrupção", 8.5, False, MUTED)], spacing=0)


def diag_killchain(s):
    steps = [
        ("Acesso inicial", "Phishing  ·  RDP ou SSH expostos"),
        ("Execução", "PowerShell (LotL)  ·  shell reverso"),
        ("Escalada de privilégio", "Driver vulnerável  ·  falha de kernel / SUID"),
        ("Persistência", "Registro e serviços  ·  cron e systemd"),
    ]
    line_seg(s, PX + 0.6, PY + 1.0, PX + 0.6, PY + 0.75 + 3 * 0.95 + 0.25, RGBColor(252, 165, 165), 1.5)
    for k, (t, sub) in enumerate(steps):
        y = PY + 0.75 + k * 0.95
        c = shape(s, MSO_SHAPE.OVAL, PX + 0.35, y, 0.5, 0.5, fill=RED_TINT, line=RED, lw=1.25)
        label(c, [(str(k + 1), 11, True, RED)], margin=0)
        text(s, PX + 1.1, y + 0.0, 3.8, 0.6, [(t, 11.5, True, DARK), (sub, 9, False, MUTED)], spacing=1)
    text(s, PX, PY + 4.4, PW, 0.25, [("Cadeia típica de ataque a um sistema operacional", 8.5, False, MUTED)], align=C)


def diag_crypto(s):
    tpm = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 0.45, PY + 0.7, 1.8, 0.6, fill=WHITE, line=LINE_MID, lw=1, radius=0.15)
    label(tpm, [("TPM 2.0", 10, True, DARK), ("chip de segurança", 7.5, False, MUTED)], spacing=0)
    pin = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 2.9, PY + 0.7, 1.8, 0.6, fill=WHITE, line=LINE_MID, lw=1, radius=0.15)
    label(pin, [("PIN / Senha", 10, True, DARK), ("fator do usuário", 7.5, False, MUTED)], spacing=0)

    arrow(s, PX + 1.35, PY + 1.3, PX + 2.2, PY + 1.75, MUTED_2, 1.25)
    arrow(s, PX + 3.8, PY + 1.3, PX + 2.95, PY + 1.75, MUTED_2, 1.25)

    mk = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 1.4, PY + 1.75, 2.35, 0.6, fill=NAVY_2, radius=0.15)
    label(mk, [("Chave mestra", 10, True, WHITE), ("VMK  ·  LUKS Master Key", 7.5, False, MUTED_2)], spacing=0)
    arrow(s, PX + 2.575, PY + 2.35, PX + 2.575, PY + 2.8, MUTED_2, 1.25)

    aes = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 1.4, PY + 2.8, 2.35, 0.6, fill=ACCENT, radius=0.15)
    label(aes, [("AES-XTS 256", 10, True, WHITE), ("acelerado por AES-NI", 7.5, False, ACCENT_TINT)], spacing=0)
    arrow(s, PX + 2.575, PY + 3.4, PX + 2.575, PY + 3.75, MUTED_2, 1.25)

    disk = shape(s, MSO_SHAPE.CAN, PX + 1.75, PY + 3.75, 1.65, 0.9, fill=BG_SOFT, line=LINE_MID, lw=1)
    label(disk, [("Disco cifrado", 9, True, BODY)])


def diag_access(s):
    cx = PX + 2.55
    p = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 1.3, PY + 0.65, 2.5, 0.55, fill=WHITE, line=LINE_MID, lw=1, radius=0.3)
    label(p, [("Processo", 10, True, DARK), ("Token  ·  UID", 7.5, False, MUTED)], spacing=0)

    def gate(y, name, fill, ln, side):
        arrow(s, cx, PY + y - 0.3, cx, PY + y, MUTED_2, 1.25)
        d = shape(s, MSO_SHAPE.FLOWCHART_DECISION, PX + 1.85, PY + y, 1.4, 0.85, fill=fill, line=ln, lw=1.25)
        label(d, [(name, 10, True, ln)])
        text(s, PX + 0.1, PY + y + 0.2, 1.65, 0.5, [(side[0], 8.5, True, BODY), (side[1], 8, False, MUTED)], align=R, spacing=0)
        arrow(s, PX + 3.25, PY + y + 0.425, PX + 3.75, PY + y + 0.425, RED, 1.25)
        text(s, PX + 3.25, PY + y + 0.17, 0.5, 0.22, [("não", 8, False, RED)], align=C)
        n = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 3.75, PY + y + 0.2, 1.1, 0.45, fill=RED_TINT, line=RED, lw=1, radius=0.5)
        label(n, [("Negado", 9, True, RED)])
        text(s, cx + 0.08, PY + y + 0.88, 0.4, 0.22, [("sim", 8, False, GREEN)])

    gate(1.5, "MAC", TEAL_TINT, TEAL, ("Obrigatório", "MIC  ·  AppArmor"))
    gate(2.7, "DAC", ACCENT_TINT, ACCENT, ("Discricionário", "DACL  ·  rwx / ACL"))
    arrow(s, cx, PY + 3.55, cx, PY + 3.9, MUTED_2, 1.25)
    g = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, PX + 1.3, PY + 3.9, 2.5, 0.55, fill=GREEN_TINT, line=GREEN, lw=1, radius=0.5)
    label(g, [("Acesso concedido", 10, True, GREEN)])
    text(s, PX, PY + 4.58, PW, 0.25, [("O kernel verifica toda abertura de arquivo ou recurso", 8.5, False, MUTED)], align=C)


def diag_defense(s):
    cx, cy = PX + PW / 2, PY + 2.55
    layers = [
        (4.5, 3.9, WHITE, LINE_MID, "REDE  ·  Firewall  ·  SmartScreen", BODY),
        (3.5, 2.95, BG_SOFT, LINE_MID, "EXECUÇÃO  ·  AMSI  ·  Seccomp", BODY),
        (2.5, 2.0, LINE, MUTED_2, "MEMÓRIA  ·  ASLR  ·  DEP/NX", BODY),
    ]
    for w, h, fill, ln, t, fc in layers:
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, cx - w / 2, cy - h / 2, w, h, fill=fill, line=ln, lw=1, radius=0.12)
        text(s, cx - w / 2 + 0.1, cy - h / 2 + 0.13, w - 0.2, 0.25, [(t, 8.5, True, fc)], align=C)
    core = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, cx - 0.75, cy - 0.45, 1.5, 1.0, fill=NAVY_2, radius=0.15)
    label(core, [("KERNEL", 10, True, WHITE), ("HVCI  ·  Lockdown", 7.5, False, MUTED_2)], spacing=0)
    text(s, PX, PY + 4.6, PW, 0.25,
         [("Defesa em profundidade: cada camada barra o que passou pela anterior", 8.5, False, MUTED)], align=C)


def diag_cia(s):
    cx, cy, r = PX + PW / 2, PY + 2.5, 1.15
    circles = [
        (cx, cy - 0.62, ACCENT, "Confidencialidade", (cx - 0.9, cy - 1.42, 1.8)),
        (cx - 0.72, cy + 0.48, TEAL, "Integridade", (cx - 1.67, cy + 0.88, 1.3)),
        (cx + 0.72, cy + 0.48, LNX, "Disponibilidade", (cx + 0.37, cy + 0.88, 1.3)),
    ]
    for x, y, col, _, _ in circles:
        c = shape(s, MSO_SHAPE.OVAL, x - r, y - r, 2 * r, 2 * r, fill=col, line=col, lw=1.5)
        set_alpha(c, 0.14)
    for _, _, col, t, (lx, ly, lw) in circles:
        text(s, lx, ly, lw, 0.3, [(t, 10, True, col)], align=C)
    text(s, cx - 0.5, cy - 0.12, 1.0, 0.45, [("SO", 9, True, DARK), ("seguro", 9, True, DARK)], align=C, spacing=0)
    text(s, PX, PY + 4.4, PW, 0.25, [("Tríade CIA: os três objetivos de segurança de um SO", 8.5, False, MUTED)], align=C)


# =============================================================================
# CONSTRUÇÃO DO DECK
# =============================================================================
def build(filepath):
    prs = Presentation()
    prs.slide_width = I(13.333)
    prs.slide_height = I(7.5)
    blank = prs.slide_layouts[6]
    page = [0]

    def new_slide(dark=False):
        s = prs.slides.add_slide(blank)
        page[0] += 1
        if dark:
            shape(s, MSO_SHAPE.RECTANGLE, 0, 0, 13.333, 7.5, fill=DARK)
        return s

    def module_slide(tag, title, module, caption, diag, rows, cli, note):
        s = new_slide()
        header(s, tag, title, module)
        diagram_panel(s, caption)
        diag(s)
        comparison_table(s, rows, cli)
        footer(s, page[0])
        notes(s, note)

    # ------------------------------------------------------------------ 01 CAPA
    s = new_slide(dark=True)
    shape(s, MSO_SHAPE.RECTANGLE, 0, 0, 13.333, 0.06, fill=ACCENT)
    text(s, 0.9, 1.0, 7.5, 0.3, [("ESTUDO DE CASO  ·  1ª VA  ·  SISTEMAS OPERACIONAIS", 10, True, RGBColor(147, 197, 253))])
    text(s, 0.9, 1.45, 7.6, 1.9, [("Engenharia e Arquitetura de Sistemas Operacionais Modernos", 34, True, WHITE)])
    text(s, 0.9, 3.45, 7.4, 0.7, [("Windows 11 Pro (23H2 / 24H2)  vs.  Ubuntu 24.04 LTS (Kernel 6.8)", 15, False, MUTED_2)])
    shape(s, MSO_SHAPE.RECTANGLE, 0.9, 4.4, 0.8, 0.05, fill=ACCENT)
    text(s, 0.9, 5.55, 7.5, 1.2, [
        ("Luiz Maranhão  &  Mário Jorge", 14, True, WHITE),
        ("Prof. Dr. Douglas Véras  ·  Sistemas Operacionais", 11, False, MUTED_2),
        ("UFRPE  ·  Bacharelado em Ciência da Computação", 11, False, MUTED_2),
    ], spacing=4)

    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 8.75, 1.45, 3.85, 4.55, fill=NAVY_2, radius=0.05)
    win_logo(s, 9.2, 2.2, 1.2)
    text(s, 10.4, 2.55, 0.6, 0.5, [("vs", 16, True, MUTED_2)], align=C)
    ubuntu_logo(s, 11.0, 2.2, 1.2)
    text(s, 8.95, 3.65, 1.7, 0.6, [("Windows 11", 11, True, WHITE), ("Kernel NT 10.0", 8.5, False, MUTED_2)], align=C, spacing=1)
    text(s, 10.75, 3.65, 1.7, 0.6, [("Ubuntu 24.04", 11, True, WHITE), ("Kernel Linux 6.8", 8.5, False, MUTED_2)], align=C, spacing=1)
    line_seg(s, 9.1, 4.6, 12.25, 4.6, BODY, 0.75)
    text(s, 9.0, 4.8, 3.35, 0.9, [("Arquitetura  ·  Processos  ·  Memória", 9, False, MUTED_2),
                                  ("Arquivos  ·  E/S  ·  Segurança", 9, False, MUTED_2)], align=C, spacing=2)
    notes(s, "Abertura. Apresentar a dupla e o objetivo: comparar Windows 11 Pro e Ubuntu 24.04 LTS em todos os "
             "temas estudados na 1ª VA — arquitetura, processos, memória, arquivos, E/S e segurança.")

    # ------------------------------------------------------------------ 02 ROTEIRO
    s = new_slide()
    header(s, "Roteiro", "Seis entregas parciais, um estudo de caso")
    agenda = [
        ("Arquitetura", "Introdução, kernel, boot"),
        ("Processos", "PCB, escalonamento"),
        ("Memória", "Paginação, swap"),
        ("Arquivos", "NTFS vs. ext4"),
        ("Entrada e Saída", "Drivers, DMA"),
        ("Segurança", "Ameaças, cripto, acesso"),
    ]
    step = 11.83 / 6
    line_seg(s, 0.75 + step / 2, 3.2, 0.75 + step * 5.5, 3.2, LINE_MID, 1.5)
    for i, (t, sub) in enumerate(agenda):
        cxa = 0.75 + step * (i + 0.5)
        c = shape(s, MSO_SHAPE.OVAL, cxa - 0.45, 2.75, 0.9, 0.9, fill=WHITE, line=ACCENT, lw=2)
        label(c, [(f"{i + 1:02d}", 15, True, ACCENT)], margin=0)
        text(s, cxa - 0.92, 3.95, 1.84, 1.0, [(t, 12.5, True, DARK), (sub, 9.5, False, MUTED)], align=C, spacing=3)
    text(s, 0.75, 5.75, 1.2, 0.3, [("E AINDA", 8, True, MUTED)])
    for k, t in enumerate(["Comandos essenciais", "Conclusão", "Referências"]):
        chip = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 1.75 + k * 2.15, 5.65, 1.95, 0.45, fill=BG_SOFT, line=LINE, lw=0.75, radius=0.5)
        label(chip, [(t, 9.5, True, BODY)])
    footer(s, page[0])
    notes(s, "Mostrar que a apresentação cobre as seis entregas parciais da disciplina. Cada slide traz no topo a "
             "entrega correspondente e uma barra de progresso de 6 segmentos.")

    # ------------------------------------------------------------------ 03 ARQUITETURA
    module_slide(
        "Entrega parcial 01  ·  Introdução e arquitetura", "Arquitetura do kernel e anéis de privilégio", 1,
        "Anéis de privilégio da CPU", diag_rings,
        [
            ("Tipo de kernel", ("Híbrido NT", "ntoskrnl.exe + HAL"), ("Monolítico modular", "módulos .ko sob demanda")),
            ("Chamadas de sistema", ("ntdll.dll → syscall", "API Win32"), ("glibc → syscall", "interface POSIX")),
            ("Isolamento", ("VBS / Hyper-V", "Ring -1 protege o kernel"), ("Namespaces + cgroups v2", "base dos containers")),
            ("Boot seguro", ("TPM 2.0 + Secure Boot", "obrigatórios no Win 11"), ("shim + GRUB assinados", "Kernel Lockdown")),
        ],
        ("Confirm-SecureBootUEFI", "uname -r\nmokutil --sb-state"),
        "Aplicações rodam em Ring 3 e só chegam ao kernel (Ring 0) por chamadas de sistema. "
        "Windows: kernel híbrido — Executivo NT (ntoskrnl.exe) sobre a HAL; o Hyper-V cria o Ring -1 (VBS/VTL1), que "
        "protege credenciais e a integridade do código mesmo se o kernel for comprometido. "
        "Ubuntu: kernel monolítico com módulos carregáveis; isolamento leve por namespaces e cgroups v2. "
        "Boot: Windows 11 exige TPM 2.0 e Secure Boot; Ubuntu usa a cadeia shim → GRUB → kernel assinada e o Lockdown, "
        "que impede até o root de alterar a memória do kernel.",
    )

    # ------------------------------------------------------------------ 04 PROCESSOS
    module_slide(
        "Entrega parcial 02  ·  Gerenciamento de processos", "Processos, threads e escalonamento", 2,
        "Ciclo de vida de um processo", diag_states,
        [
            ("Estrutura (PCB)", ("EPROCESS / ETHREAD", "thread é a unidade escalonada"), ("task_struct", "processo e thread = task")),
            ("Criação", ("CreateProcess()", "novo espaço de endereços"), ("fork() + exec()", "Copy-on-Write")),
            ("Escalonador", ("Prioridades 0 a 31", "preemptivo + boost"), ("EEVDF", "sucessor do CFS")),
            ("Sincronização / IPC", ("Mutex, Event, ALPC", "objetos do kernel"), ("Futex, pipes, sockets", "padrão POSIX")),
        ],
        ("Get-Process\ntasklist /v", "ps -ef --forest\nhtop"),
        "Diagrama: estados clássicos. Ao sair de Executando, a CPU salva os registradores no PCB (troca de contexto). "
        "Windows: PCB = EPROCESS/ETHREAD; escalona threads com 32 níveis de prioridade (16–31 tempo real) e dá boost à "
        "janela em primeiro plano. Criar processo é mais caro (CreateProcess monta um espaço novo). "
        "Ubuntu: tudo é task_struct; fork() usa Copy-on-Write, copiando páginas só quando há escrita. "
        "Desde o kernel 6.6 o escalonador é o EEVDF, que substituiu o CFS mantendo a árvore rubro-negra por vruntime.",
    )

    # ------------------------------------------------------------------ 05 MEMÓRIA
    module_slide(
        "Entrega parcial 03  ·  Gerenciamento de memória", "Memória virtual e paginação", 3,
        "Tradução de endereços", diag_paging,
        [
            ("Espaço virtual", ("128 TB por processo", "árvore de VADs"), ("128 TB (4 níveis)", "VMAs em Maple Tree")),
            ("Substituição", ("Working Set", "listas Standby / Modified"), ("LRU ativa / inativa", "MGLRU no kernel 6.x")),
            ("Falta de RAM", ("Compressão em RAM", "+ pagefile.sys"), ("Swapfile", "OOM Killer em último caso")),
            ("Proteção", ("ASLR + DEP/NX", "alta entropia"), ("KASLR + NX", "SMEP / SMAP")),
        ],
        ("Get-Counter '\\Memory\\*'", "free -h\nvmstat 1"),
        "Cada processo enxerga um espaço virtual próprio; a MMU traduz páginas virtuais em quadros físicos, usando a "
        "TLB como cache. Se a página não está na RAM ocorre page fault e o SO a busca no disco. "
        "Windows: controla o Working Set de cada processo; páginas retiradas vão para listas Standby/Modified e, antes de "
        "ir ao pagefile, podem ser comprimidas na própria RAM. "
        "Ubuntu: listas LRU (MGLRU), alocador Buddy/SLUB, overcommit e o OOM Killer quando a memória acaba.",
    )

    # ------------------------------------------------------------------ 06 ARQUIVOS
    module_slide(
        "Entrega parcial 04  ·  Sistemas de arquivos", "Organização dos sistemas de arquivos", 4,
        "Metadados, blocos e journal", diag_fs,
        [
            ("Sistema padrão", ("NTFS", "padrão desde o NT"), ("ext4", "padrão no Ubuntu")),
            ("Metadados", ("MFT", "registro de 1 KB por arquivo"), ("Inodes", "256 bytes por arquivo")),
            ("Alocação", ("Runlists (extents)", "arquivo pequeno fica na MFT"), ("Extents + alocação tardia", "menos fragmentação")),
            ("Consistência", ("$LogFile", "journaling transacional"), ("JBD2 (modo ordered)", "checksums CRC32c")),
        ],
        ("fsutil fsinfo ntfsinfo C:", "df -Th\nls -li"),
        "Todo arquivo tem um registro de metadados (MFT no NTFS, inode no ext4) que aponta para extents — sequências "
        "contíguas de blocos. NTFS guarda arquivos muito pequenos dentro do próprio registro da MFT e indexa diretórios "
        "em árvore B+. ext4 divide o disco em grupos de blocos e usa alocação tardia para reduzir fragmentação; no Linux "
        "o VFS unifica todos os sistemas de arquivos. "
        "Journal: registra a intenção antes de alterar o disco; após uma queda de energia basta reaplicar o log.",
    )

    # ------------------------------------------------------------------ 07 E/S
    module_slide(
        "Entrega parcial 05  ·  Entrada e saída", "Subsistema de entrada e saída", 5,
        "Pilha de E/S e DMA", diag_io,
        [
            ("Modelo de driver", ("WDM / WDF", "KMDF e UMDF"), ("Módulos do kernel", "udev gerencia /dev")),
            ("Requisição", ("IRP", "pacote percorre a pilha"), ("bio + blk-mq", "filas por núcleo")),
            ("E/S assíncrona", ("IOCP", "I/O Completion Ports"), ("io_uring", "filas compartilhadas")),
            ("DMA", ("IOMMU", "Kernel DMA Protection"), ("IOMMU", "VT-d / AMD-Vi")),
        ],
        ("Get-PnpDevice\nGet-PhysicalDisk", "lsblk\nlspci -k"),
        "A requisição desce da aplicação até a controladora. Windows encapsula cada pedido num IRP que atravessa a pilha "
        "de drivers (WDF; UMDF permite drivers em modo usuário). Linux trata dispositivos como arquivos em /dev, "
        "gerenciados pelo udev, e usa blk-mq com uma fila por núcleo para SSDs NVMe. "
        "Assíncrono: IOCP no Windows e io_uring no Linux (anéis de submissão/conclusão compartilhados, menos syscalls). "
        "DMA: a controladora escreve direto na RAM e avisa a CPU por interrupção; a IOMMU impede acessos indevidos.",
    )

    # ------------------------------------------------------------------ 08 SEGURANÇA — INTRO
    module_slide(
        "Entrega parcial 06  ·  Segurança  ·  1/5", "Introdução à segurança dos SOs", 6,
        "Objetivos de segurança", diag_cia,
        [
            ("Confidencialidade", ("BitLocker  ·  ACLs", "dados só para autorizados"), ("LUKS2  ·  permissões", "dados só para autorizados")),
            ("Integridade", ("Secure Boot  ·  HVCI", "só código confiável"), ("Lockdown  ·  assinaturas", "só código confiável")),
            ("Disponibilidade", ("Defender  ·  VSS", "proteção e recuperação"), ("systemd  ·  snapshots", "serviços e recuperação")),
            ("Menor privilégio", ("UAC", "admin só quando preciso"), ("sudo", "root só quando preciso")),
        ],
        None,
        "Segurança de SO busca três objetivos (tríade CIA): confidencialidade, integridade e disponibilidade. "
        "O SO é a base de confiança: se ele cair, tudo acima dele cai junto. Ambos aplicam o princípio do menor "
        "privilégio — UAC no Windows e sudo no Ubuntu. Nos próximos slides: ameaças, criptografia, controle de acesso e "
        "ferramentas antimalware.",
    )

    # ------------------------------------------------------------------ 09 AMEAÇAS
    module_slide(
        "Entrega parcial 06  ·  Segurança  ·  2/5", "Principais ameaças e pontos fracos", 6,
        "Cadeia de ataque", diag_killchain,
        [
            ("Alvo típico", ("Desktops corporativos", "Active Directory"), ("Servidores e nuvem", "containers")),
            ("Malware dominante", ("Ransomware", "apaga cópias de sombra"), ("Botnets e mineradores", "serviços expostos")),
            ("Técnica comum", ("Living off the Land", "PowerShell, WMI"), ("Escalada local (LPE)", "SUID, sudo, kernel")),
            ("Ponto fraco", ("Drivers vulneráveis", "BYOVD → Ring 0"), ("Má configuração", "SSH, permissões, Docker")),
        ],
        ("Get-WinEvent\n-LogName Security", "journalctl -u ssh\nfind / -perm -4000"),
        "Windows é o maior alvo por ser maioria nos desktops: ransomware que apaga as cópias de sombra (vssadmin), "
        "ataques 'Living off the Land' com ferramentas legítimas (PowerShell, WMI), roubo de credenciais do LSASS e "
        "drivers antigos assinados (BYOVD) para chegar ao Ring 0. "
        "Ubuntu domina servidores: falhas de kernel para virar root (nf_tables, io_uring), binários SUID e sudo mal "
        "configurados, SSH exposto e escape de containers. O ponto fraco do Linux costuma ser a configuração.",
    )

    # ------------------------------------------------------------------ 10 CRIPTOGRAFIA
    module_slide(
        "Entrega parcial 06  ·  Segurança  ·  3/5", "Criptografia: o que é protegido e como", 6,
        "Hierarquia de chaves do disco", diag_crypto,
        [
            ("Disco inteiro", ("BitLocker", "XTS-AES 128 / 256"), ("LUKS2 + dm-crypt", "AES-XTS")),
            ("Arquivo / pasta", ("EFS (NTFS)", "AES + par RSA do usuário"), ("fscrypt (ext4)", "por diretório")),
            ("Proteção da chave", ("Selada no TPM 2.0", "liberada se o boot é íntegro"), ("Argon2id", "TPM via systemd-cryptenroll")),
            ("Segredos do usuário", ("DPAPI  ·  Credential Guard", "isolados por VBS"), ("Keyring  ·  yescrypt", "senhas em /etc/shadow")),
        ],
        ("manage-bde -status", "cryptsetup luksDump"),
        "Criptografia protege dados em repouso: se o notebook for roubado, o disco é ilegível. "
        "Windows: BitLocker cifra o volume com XTS-AES; a chave mestra (VMK) fica selada no TPM e só é liberada se a "
        "cadeia de boot não foi alterada. EFS cifra arquivos individuais. DPAPI e Credential Guard protegem segredos. "
        "Ubuntu: LUKS2/dm-crypt cifra a partição; a senha passa pelo Argon2id, resistente a força bruta com GPU; "
        "fscrypt cifra diretórios do ext4; senhas locais usam hash yescrypt. AES-NI faz isso sem perda perceptível.",
    )

    # ------------------------------------------------------------------ 11 CONTROLE DE ACESSO
    module_slide(
        "Entrega parcial 06  ·  Segurança  ·  4/5", "Autenticação e controle de acesso", 6,
        "Decisão de acesso no kernel", diag_access,
        [
            ("Autenticação", ("LSASS + Windows Hello", "Kerberos, NTLM, FIDO2"), ("PAM", "senha, FIDO2, LDAP")),
            ("Identidade", ("Access Token", "SIDs + privilégios"), ("UID / GID", "+ capabilities")),
            ("DAC", ("ACLs (DACL)", "permissões granulares"), ("rwx + POSIX ACL", "chmod, setfacl")),
            ("MAC / elevação", ("Integridade + UAC", "níveis Low → System"), ("AppArmor + sudo", "perfis por aplicação")),
        ],
        ("whoami /all\nicacls C:\\Dados", "id  ·  getfacl\nsudo aa-status"),
        "Autenticação prova quem é o usuário; controle de acesso decide o que ele pode fazer. "
        "Windows: LSASS valida o login (senha, Kerberos, Windows Hello) e gera um Access Token; a cada abertura de "
        "objeto o Security Reference Monitor compara o token com a DACL. Níveis de integridade impedem que um processo "
        "Low altere um High. Ubuntu: PAM autentica de forma modular; o kernel checa permissões rwx/ACL do UID e o "
        "AppArmor (MAC) confina programas por perfil, mesmo rodando como root.",
    )

    # ------------------------------------------------------------------ 12 ANTIMALWARE
    module_slide(
        "Entrega parcial 06  ·  Segurança  ·  5/5", "Ferramentas nativas contra malware", 6,
        "Camadas de proteção", diag_defense,
        [
            ("Antivírus nativo", ("Microsoft Defender", "assinaturas + nuvem"), ("Sem antivírus padrão", "defesa por isolamento")),
            ("Execução", ("AMSI + SmartScreen", "inspeciona scripts"), ("Seccomp + Snap", "restringe syscalls")),
            ("Integridade do kernel", ("HVCI", "só código assinado"), ("Kernel Lockdown", "módulos assinados")),
            ("Ransomware / rede", ("Pastas controladas", "+ Windows Firewall"), ("UFW (nftables)", "+ auditd")),
        ],
        ("Get-MpComputerStatus", "systemd-analyze security"),
        "Windows: o Defender usa um minifiltro no kernel que analisa arquivos antes de executar; o AMSI inspeciona "
        "scripts já desofuscados na memória; o HVCI, validado pelo hipervisor, impede código não assinado no kernel; "
        "o Acesso Controlado a Pastas bloqueia ransomware. "
        "Ubuntu não traz antivírus ativo por padrão (ClamAV é opcional): aposta em isolamento — Seccomp-BPF, sandbox de "
        "Snaps com AppArmor, KASLR/SMEP/SMAP, Lockdown e firewall UFW. São filosofias diferentes: detectar vs. confinar.",
    )

    # ------------------------------------------------------------------ 13 COMANDOS
    s = new_slide()
    header(s, "Lista de comandos", "Comandos essenciais por tema")
    tx, tw = 0.75, 2.6
    cwx, cww = 3.55, 4.4
    clx, clw = 8.15, 4.43
    os_header(s, cwx, cww, True)
    os_header(s, clx, clw, False)
    cmds = [
        ("Kernel e boot", "Confirm-SecureBootUEFI", "uname -r  ·  mokutil --sb-state"),
        ("Processos", "Get-Process  ·  tasklist /v", "ps -ef --forest  ·  htop"),
        ("Memória", "Get-Counter '\\Memory\\*'", "free -h  ·  vmstat 1"),
        ("Arquivos", "fsutil fsinfo ntfsinfo C:", "df -Th  ·  ls -li"),
        ("Entrada e saída", "Get-PnpDevice  ·  Get-PhysicalDisk", "lsblk  ·  lspci -k"),
        ("Criptografia", "manage-bde -status", "sudo cryptsetup luksDump <dev>"),
        ("Acesso e defesa", "whoami /all  ·  Get-MpComputerStatus", "id  ·  sudo aa-status"),
    ]
    for i, (t, wc, lc) in enumerate(cmds):
        y = 2.3 + i * 0.6
        chip = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, tx, y + 0.15, 0.42, 0.3, fill=ACCENT_TINT, radius=0.3)
        label(chip, [(f"{i + 1:02d}", 8, True, ACCENT)], margin=0)
        text(s, tx + 0.6, y + 0.16, tw - 0.6, 0.3, [(t, 11, True, DARK)])
        text(s, cwx, y + 0.17, cww, 0.3, [(wc, 10.5, False, DARK, MONO)])
        text(s, clx, y + 0.17, clw, 0.3, [(lc, 10.5, False, DARK, MONO)])
        if i < len(cmds) - 1:
            line_seg(s, tx, y + 0.6, clx + clw, y + 0.6, LINE, 0.75)
    footer(s, page[0])
    notes(s, "Resumo prático: para cada tema, um comando equivalente em cada sistema. Se houver tempo, demonstrar "
             "ao vivo 'whoami /all' no Windows e 'id' / 'sudo aa-status' no Ubuntu.")

    # ------------------------------------------------------------------ 14 CONCLUSÃO
    s = new_slide()
    header(s, "Conclusão", "Dois projetos, duas filosofias")
    cards = [
        (0.75, True, "Windows 11 Pro", "Segurança integrada ao hardware e gestão centralizada",
         ["Segurança por virtualização (VBS)", "Gestão corporativa (AD, GPO)", "Ecossistema amplo de drivers e apps"]),
        (6.84, False, "Ubuntu 24.04 LTS", "Desempenho, modularidade e código aberto auditável",
         ["Desempenho (EEVDF, io_uring)", "Isolamento leve (namespaces, cgroups)", "Transparência e personalização"]),
    ]
    for x, is_win, name, phil, items in cards:
        col = WIN if is_win else LNX
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 1.6, 5.74, 3.65, fill=WHITE, line=LINE, lw=1, radius=0.04)
        shape(s, MSO_SHAPE.RECTANGLE, x, 1.6, 5.74, 0.05, fill=col)
        (win_logo if is_win else ubuntu_logo)(s, x + 0.4, 2.0, 0.55)
        text(s, x + 1.2, 1.98, 4.3, 0.7, [(name, 16, True, DARK), (phil, 10, False, MUTED)], spacing=2)
        for k, it in enumerate(items):
            y = 3.05 + k * 0.62
            shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.45, y + 0.08, 0.14, 0.14, fill=col, radius=0.3)
            text(s, x + 0.8, y, 4.7, 0.35, [(it, 12, False, BODY)])
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.75, 5.5, 11.83, 0.95, fill=BG_PANEL, radius=0.15)
    text(s, 1.05, 5.5, 1.8, 0.95, [("MELHOR ENCAIXE", 8, True, MUTED)], anchor=MID)
    text(s, 2.9, 5.5, 4.5, 0.95, [("Estações corporativas  →  Windows 11 Pro", 12, True, WIN)], anchor=MID)
    text(s, 7.6, 5.5, 4.8, 0.95, [("Servidores e nuvem  →  Ubuntu 24.04 LTS", 12, True, LNX)], anchor=MID)
    footer(s, page[0])
    notes(s, "Não existe vencedor absoluto. O Windows 11 aposta em segurança apoiada no hardware (TPM, VBS) e gestão "
             "centralizada; o Ubuntu aposta em desempenho, modularidade e isolamento leve. A escolha depende do contexto.")

    # ------------------------------------------------------------------ 15 REFERÊNCIAS
    s = new_slide()
    header(s, "Referências", "Referências bibliográficas")
    refs = [
        "TANENBAUM, A. S.; BOS, H. Sistemas Operacionais Modernos. 4. ed. São Paulo: Pearson, 2016.",
        "SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. Fundamentos de Sistemas Operacionais. 9. ed. Rio de Janeiro: LTC, 2015.",
        "STALLINGS, W. Operating Systems: Internals and Design Principles. 9. ed. Boston: Pearson, 2018.",
        "YOSIFOVICH, P. et al. Windows Internals, Part 1. 7. ed. Redmond: Microsoft Press, 2017.",
        "ALLIEVI, A. et al. Windows Internals, Part 2. 7. ed. Redmond: Microsoft Press, 2021.",
        "LOVE, R. Linux Kernel Development. 3. ed. Upper Saddle River: Addison-Wesley, 2010.",
        "MICROSOFT. Windows 11 Security Book. Microsoft Learn, 2024.",
        "CANONICAL. Ubuntu 24.04 LTS Security Documentation. Ubuntu Docs, 2024.",
    ]
    for k, ref in enumerate(refs):
        y = 1.7 + k * 0.6
        text(s, 0.75, y, 0.5, 0.3, [(f"{k + 1:02d}", 10, True, ACCENT)])
        text(s, 1.3, y, 11.2, 0.4, [(ref, 11, False, BODY)])
    footer(s, page[0])

    # ------------------------------------------------------------------ 16 ENCERRAMENTO
    s = new_slide(dark=True)
    shape(s, MSO_SHAPE.RECTANGLE, 0, 0, 13.333, 0.06, fill=ACCENT)
    text(s, 0.9, 2.5, 7.0, 1.0, [("Obrigado!", 48, True, WHITE)])
    text(s, 0.9, 3.55, 7.0, 0.5, [("Perguntas?", 22, False, MUTED_2)])
    shape(s, MSO_SHAPE.RECTANGLE, 0.9, 4.35, 0.8, 0.05, fill=ACCENT)
    text(s, 0.9, 5.6, 8.0, 0.8, [("Luiz Maranhão  &  Mário Jorge", 13, True, WHITE),
                                 ("Sistemas Operacionais  ·  Prof. Dr. Douglas Véras  ·  UFRPE", 10.5, False, MUTED_2)], spacing=4)
    win_logo(s, 9.6, 2.85, 1.0)
    ubuntu_logo(s, 11.05, 2.85, 1.0)

    prs.save(filepath)
    print(f"OK: {len(prs.slides)} slides -> {filepath}")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Apresentacao_Final_1VA_Consolidada.pptx")
    build(out)

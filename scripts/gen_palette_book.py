#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档封面配色·版式设计书 生成脚本
=====================================
配色系统：C 雾林奶咖（主用·日常）＋ A 栗皮本色（备用·正式），共用锚点色 #492D22
版权所有：湫黎（2026-11-10）——CC BY-NC 4.0：保留署名「湫黎」，允许非商用的使用、修改与分发；商用需另行书面授权

依赖（均为宽松开源许可，允许商用）：
  - Python 3.8+，reportlab（BSD-style 许可）
字体（不随本脚本分发）：
  - Noto Serif SC / 思源宋体，SIL Open Font License 1.1（可商用·可嵌入·可再分发）
  - 默认路径 /usr/share/fonts/truetype/noto-serif-sc/ ，可用 --font-dir 指定

用法：
  python3 gen_palette_book.py                  # 当前目录生成两版 PDF
  python3 gen_palette_book.py --out 输出目录     # 指定输出目录

输出：
  配色版式设计书_V2.3_无版权.pdf  （无版权元数据）
  配色版式设计书_V2.3.1_带版权.pdf（元数据 dc:creator=湫黎，许可 CC BY-NC 4.0 署名·非商用）

声明：本脚本为原创代码，未复制/未引用任何 Z.AI skill 或其他第三方受限代码；
      与 docx/pdf/pptx/charts 等 Proprietary skill 无关，依赖链无第三方商用限制。
      本脚本自身的许可由版权人自选（现为 CC BY-NC 4.0，见上）。
"""

import argparse
import os
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as _canvas

# ============================================================
# 参数区（改这里即可重新生成整套设计书）
# ============================================================

PALETTES = {
    "C": {
        "name": "雾林奶咖",
        "tag": "主用 · 日常文档",
        "en": "MIST & CREAM",
        "colors": [
            ("雾白", "#F7F1E7", "书脊版封面底 · 护眼内页底 · 反白文字"),
            ("浅驼", "#E3D0BA", "分隔线 · 表格隔行 · 底纹"),
            ("奶咖", "#B08968", "标签 · 图表主色 · 页眉页脚"),
            ("栗棕", "#6B4028", "大标题 · 章节标题"),
            ("深栗", "#492D22", "正文 · 书脊 · 表头 · 锚点色"),
        ],
    },
    "A": {
        "name": "栗皮本色",
        "tag": "备用 · 正式文档（封面/扉页深底）",
        "en": "CHESTNUT PELAGE",
        "colors": [
            ("墨栗", "#331E14", "页脚细线 · 表头（深底内页）"),
            ("主栗", "#492D22", "封面主底 · 扉页底 · 锚点色"),
            ("赤栗", "#7C4324", "章节色块 · 图表第二色"),
            ("焦糖", "#B26B3F", "强调点缀 · 高亮（≤10% 面积）"),
            ("蜜白", "#EAD9C0", "深底标题与正文（反白）"),
        ],
    },
}

# 字号级数：(级数名, 字号pt, 行距pt, 用色hex, 用途)
TYPE_SCALE = [
    ("主标题", 26, 34, "#6B4028", "封面 · 文档题名"),
    ("章节标题", 16, 22, "#6B4028", "页内大节标题"),
    ("小节标题", 13, 18, "#492D22", "小节标题"),
    ("正文", 10.5, 16, "#492D22", "段落文字 · 表格正文"),
    ("辅助", 9, 13, "#B08968", "页眉页脚 · 图注 · 标签"),
    ("标注", 8, 11, "#B08968", "尺寸标注 · 编号"),
]

# 对比度核查对：(前景名, 前景hex, 背景名, 背景hex, 用途说明)
CONTRAST_PAIRS = [
    ("深栗", "#492D22", "雾白", "#F7F1E7", "正文字色（日常内页）"),
    ("栗棕", "#6B4028", "雾白", "#F7F1E7", "各级标题（日常内页）"),
    ("奶咖", "#B08968", "雾白", "#F7F1E7", "标签页脚（不作正文）"),
    ("深栗", "#492D22", "浅驼", "#E3D0BA", "底纹上的文字"),
    ("蜜白", "#EAD9C0", "主栗", "#492D22", "深底标题与正文（正式封面）"),
    ("蜜白", "#EAD9C0", "赤栗", "#7C4324", "赤栗色块上的标题"),
    ("焦糖", "#B26B3F", "主栗", "#492D22", "仅限点缀条与图形"),
    ("深栗", "#492D22", "奶咖", "#B08968", "胶囊标签文字（辅助信息）"),
]

# Word 样式映射（兜底②：在 Word 里手动复刻用）
WORD_MAP_ROWS = [
    ("页面文字 / 正文", ("#492D22", "深栗"), ("#EAD9C0", "蜜白")),
    ("标题一", ("#6B4028", "栗棕"), ("#EAD9C0", "蜜白·赤栗块")),
    ("标题二", ("#B08968", "奶咖·≥14pt"), ("#B26B3F", "焦糖·仅点缀")),
    ("强调文字", ("#492D22", "深栗·加粗"), ("#B26B3F", "焦糖·≥18pt")),
    ("表格表头", ("#492D22", "深栗底·雾白字"), ("#331E14", "墨栗底·蜜白字")),
    ("表格隔行底纹", ("#E3D0BA", "浅驼"), ("—", "")),
    ("页眉 / 页脚", ("#B08968", "奶咖"), ("#EAD9C0", "蜜白")),
]

USAGE_RULES = [
    "正文字色一律深栗／深底一律蜜白；奶咖对雾白底对比度不足，只作标签、页脚与图形色。",
    "焦糖只作点缀条与高亮，面积占比 ≤10%；大面积永远让给雾白与深栗两极。",
    "两板共用锚点 #492D22：正式文档＝A 封面（深底）＋纸白内页，可自由混搭。",
    "内页底默认纸白（屏幕最锐利 · 印刷零墨）；用户点名护眼/柔和时切雾白 #F7F1E7（深栗字压雾白偏费眼，实测拍板）。",
    "图表色序（自深而浅）：深栗 → 栗棕 → 奶咖 → 浅驼；需要第五色时引入赤栗。",
    "深底（A）上不作焦糖文字；赤栗色块上文字用蜜白。",
    "屏显直接使用 HEX；送印一律以 CMYK 打样为准，深栗大面积建议改专色（见 06）。",
]

PRINT_NOTES = [
    "深栗 #492D22 四色值约 C0 M38 Y53 K71——大面积平网易偏红发闷，建议改专色（深棕系色卡对色打样）后再上机。",
    "雾白 #F7F1E7 在涂布纸偏冷、非涂布蒙肯纸偏暖；选纸后以打样为准再定封面底色。",
    "封面四边出血 3mm（成品 210×297 → 出血 216×303）；书脊色条与深底压满出血。",
    "反白文字最小 6pt（无衬线）/ 8pt（衬线）；蜜白反白建议 ≥10.5pt。",
    "表格与分隔线 0.5pt 起；胶囊标签圆角 4.5mm（高度 9mm 时）。",
]

# 版式几何（A4 mm 坐标，原点左下，用于模板图绘制与规格表）
GEOM = {
    "page": (210, 297),
    "spine_w": 8,          # 书脊色条宽
    "margin_l": 28,        # 版心左（书脊外 20）
    "margin_r": 20,
    "margin_t": 35,        # 天头（内容区顶到页顶）
    "margin_b": 25,        # 地脚
    "eyebrow_y": 262,     # 眉头基线
    "title1_y": 216,      # 主标题第一行基线
    "title2_y": 203,      # 主标题第二行基线
    "subtitle_y": 189,    # 副题基线
    "info_y": 177,        # 信息行基线
    "pill_cy": 163,       # 胶囊标签中心
    "rule_y": 30,         # 底部细线
    "foot_y": 21,         # 页脚基线
    "title_pt": 26,
    "subtitle_pt": 12,
    "info_pt": 10.5,
}

TITLE_TEXT_1 = "文档封面配色"
TITLE_TEXT_2 = "版式设计书"
SUBTITLE_TEXT = "雾林奶咖 × 栗皮本色 —— 共锚 #492D22 的双色板系统"
EYEBROW_TEXT = "PALETTE · TYPE · LAYOUT SPEC"
INFO_TEXT = "2026 年 11 月"
PILL_TEXT = "SPEC · NO.01"
FOOT_TEXT = "PALETTE SPEC · 2026"

DOC_TITLE = "文档封面配色·版式设计书"
CREATOR_ID = "湫黎"
COPYRIGHT_LINE = "版权所有 © 2026 湫黎 · CC BY-NC 4.0（署名 · 非商用 · 商用需书面授权）"

PAGE_W, PAGE_H = A4  # pt

# ============================================================
# 颜色工具
# ============================================================

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2cmyk_str(rgb):
    r, g, b = (v / 255.0 for v in rgb)
    k = 1.0 - max(r, g, b)
    if k >= 1.0:
        return "C0 M0 Y0 K100"
    c = (1.0 - r - k) / (1.0 - k)
    m = (1.0 - g - k) / (1.0 - k)
    y = (1.0 - b - k) / (1.0 - k)
    return "C%d M%d Y%d K%d" % tuple(round(v * 100) for v in (c, m, y, k))


def _lum_channel(v):
    v = v / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(hexcolor):
    r, g, b = hex2rgb(hexcolor)
    return 0.2126 * _lum_channel(r) + 0.7152 * _lum_channel(g) + 0.0722 * _lum_channel(b)


def contrast_ratio(fg, bg):
    la, lb = luminance(fg), luminance(bg)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def wcag_verdict(ratio):
    if ratio >= 7:
        return "AAA 正文"
    if ratio >= 4.5:
        return "AA 正文"
    if ratio >= 3.0:
        return "AA 大字"
    return "仅图形底"


# ============================================================
# 字体
# ============================================================

FONT_DIR = "/usr/share/fonts/truetype/noto-serif-sc"
FONT_FILES = {
    "NSC": "NotoSerifSC-Regular.ttf",
    "NSC-SB": "NotoSerifSC-SemiBold.ttf",
    "NSC-B": "NotoSerifSC-Bold.ttf",
    "NSC-XB": "NotoSerifSC-ExtraBold.ttf",
}

# 跨平台字体探测候选目录（相对路径按用户主目录展开）
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/noto-serif-sc",
    "/usr/share/fonts/opentype/noto-serif-sc",
    "/usr/local/share/fonts/noto-serif-sc",
    "~/.fonts/noto-serif-sc",
    "~/.local/share/fonts/noto-serif-sc",
    "~/Library/Fonts/noto-serif-sc",
    "C:/Program Files/Noto Serif SC",
    "C:/Windows/Fonts",
]


def _find_font_dir():
    """按候选目录与 fc-match 探测 Noto Serif SC 所在目录，找不到返回 None。"""
    import glob as _glob
    import subprocess
    for cand in _FONT_CANDIDATES:
        p = os.path.expanduser(cand)
        if os.path.exists(os.path.join(p, FONT_FILES["NSC"])):
            return p
    try:  # fc-match（Linux/macOS 常见）
        out = subprocess.run(
            ["fc-match", "-f", "%{file}", "Noto Serif SC"],
            capture_output=True, text=True, timeout=10).stdout.strip()
        if out and os.path.basename(out) == FONT_FILES["NSC"]:
            return os.path.dirname(out)
    except Exception:
        pass
    for pat in ("~/.fonts/**/NotoSerifSC-Regular.ttf",
                "~/fonts/**/NotoSerifSC-Regular.ttf"):  # 兜底递归
        hits = _glob.glob(os.path.expanduser(pat), recursive=True)
        if hits:
            return os.path.dirname(hits[0])
    return None


def register_fonts(font_dir=None):
    base = (font_dir
            or os.environ.get("NOTO_SERIF_SC_DIR")
            or _find_font_dir()
            or FONT_DIR)
    missing = [f for f in FONT_FILES.values()
               if not os.path.exists(os.path.join(base, f))]
    if missing:
        raise FileNotFoundError(
            "缺少字体 %s\nNoto Serif SC（思源宋体，SIL OFL 1.1，可商用可嵌入）"
            "安装方式任选其一：\n"
            "  · 官方下载解压后：设置环境变量 NOTO_SERIF_SC_DIR 指向解压目录\n"
            "  · 或运行时 --font-dir /path/to/fonts 指定\n"
            "  · Linux: sudo apt install fonts-noto-serif-cjk-sc（注意发行版文件名可能不同）\n"
            "  · macOS: 下载 NotoSerifSC 官方包，拖入 ~/Library/Fonts\n"
            "  · Google Fonts 仓库：https://fonts.google.com/noto/specimen/Noto+Serif+SC"
            % ", ".join(missing)
        )
    for alias, fname in FONT_FILES.items():
        pdfmetrics.registerFont(TTFont(alias, os.path.join(base, fname)))


# ============================================================
# 绘图辅助
# ============================================================

PT = 1.0  # reportlab 单位即 pt


def txt(c, x, y, s, font="NSC", size=10.5, color="#492D22", cs=0.0):
    """写一行文字（可带字距），x/y 为基线（pt 坐标）。"""
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(cs)
    t.setFillColor(HexColor(color))
    t.textOut(s)
    c.drawText(t)
    return t


def txt_r(c, x_right, y, s, font="NSC", size=10.5, color="#492D22", cs=0.0):
    """右对齐写一行。"""
    w = pdfmetrics.stringWidth(s, font, size) + cs * max(0, len(s) - 1)
    txt(c, x_right - w, y, s, font, size, color, cs)


def txt_c(c, x_center, y, s, font="NSC", size=10.5, color="#492D22", cs=0.0):
    w = pdfmetrics.stringWidth(s, font, size) + cs * max(0, len(s) - 1)
    txt(c, x_center - w / 2.0, y, s, font, size, color, cs)


def fit_check(s, font, size, max_w, tag=""):
    """排版前断言：文字不溢出给定宽度。"""
    w = pdfmetrics.stringWidth(s, font, size)
    assert w <= max_w, "文字溢出 [%s]: %r 宽 %.1fpt > %.1fpt" % (tag, s, w, max_w)
    return w


def chip(c, x, y, w, h, hexcolor, r=2 * mm):
    c.setFillColor(HexColor(hexcolor))
    c.setStrokeColor(HexColor("#D8CCBB"))
    c.setLineWidth(0.4)
    c.roundRect(x, y, w, h, r, stroke=1, fill=1)


def dot(c, cx, cy, d, hexcolor):
    c.setFillColor(HexColor(hexcolor))
    c.circle(cx, cy, d / 2.0, stroke=0, fill=1)


def hr(c, x, y, w, hexcolor, lw=0.6):
    c.setStrokeColor(HexColor(hexcolor))
    c.setLineWidth(lw)
    c.line(x, y, x + w, y)


def pill(c, cx, cy, text, bg, fg, font="NSC-SB", size=9.5, pad_h=5.5 * mm, h=9 * mm):
    w = pdfmetrics.stringWidth(text, font, size) + pad_h * 2
    c.setFillColor(HexColor(bg))
    c.roundRect(cx - w / 2.0, cy - h / 2.0, w, h, h / 2.0, stroke=0, fill=1)
    txt_c(c, cx, cy - size * 0.34, text, font, size, fg)
    return w


# ---------- 尺寸标注（版式规格页用） ----------

def dim_h(c, x1, x2, y, label, color="#B08968"):
    """水平尺寸线：两端短竖线 + 中间标签。"""
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(0.5)
    c.line(x1, y, x2, y)
    for x in (x1, x2):
        c.line(x, y - 2, x, y + 2)
    txt_c(c, (x1 + x2) / 2.0, y + 3, label, "NSC-SB", 8, color, cs=0.3)


def dim_v(c, x, y1, y2, label, color="#B08968"):
    """垂直尺寸线：两端短横线 + 旋转标签。"""
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(0.5)
    c.line(x, y1, x, y2)
    for y in (y1, y2):
        c.line(x - 2, y, x + 2, y)
    c.saveState()
    c.translate(x - 3, (y1 + y2) / 2.0)
    c.rotate(90)
    txt_c(c, 0, 0, label, "NSC-SB", 8, color, cs=0.3)
    c.restoreState()


def leader(c, x1, y1, x2, y2, color="#E3D0BA"):
    """引线（细线 + 起点小圆点）。"""
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(0.5)
    c.line(x1, y1, x2, y2)
    dot(c, x1, y1, 1.6, color)


# ============================================================
# 页面骨架
# ============================================================

ML, MR = 24 * mm, 20 * mm          # 版心左右
CW = PAGE_W - ML - MR              # 版心宽
M_TOP, M_BOT = 272 * mm, 16 * mm   # 内容顶/底（pt）
FOOT_L = "文档封面配色 · 版式设计书"
FOOT_R_TPL = "%02d / 07"


def page_bg(c, hexcolor="#F7F1E7"):
    c.setFillColor(HexColor(hexcolor))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)


def page_header(c, zh, en, idx):
    txt(c, ML, M_TOP, zh, "NSC-SB", 16, "#6B4028")
    txt_r(c, PAGE_W - MR, M_TOP + 2, en, "NSC-SB", 9, "#B08968", cs=1.8)
    hr(c, ML, M_TOP - 6, CW, "#E3D0BA", 0.6)
    page_footer(c, idx)


def page_footer(c, idx):
    txt(c, ML, M_BOT, FOOT_L, "NSC", 9, "#B08968")
    txt_r(c, PAGE_W - MR, M_BOT, FOOT_R_TPL % idx, "NSC-SB", 9, "#B08968", cs=1.0)


def section_label(c, x, y, zh, tag, en):
    """组标题：中文名 + 右侧小标签。返回新 y。"""
    txt(c, x, y, zh, "NSC-SB", 13, "#492D22")
    txt(c, x + pdfmetrics.stringWidth(zh, "NSC-SB", 13) + 8, y, tag, "NSC", 9, "#B08968")
    txt_r(c, x + 150 * mm, y, en, "NSC-SB", 8.5, "#B08968", cs=1.5)
    return y - 8 * mm


# ============================================================
# 封面模板绘制（mm 坐标 → pt，供 P1/P3/P4/P5 复用）
# ============================================================

def _mm(x):
    return x * mm


def draw_spine_cover(c, ox, oy, s, full_text=True):
    """书脊版封面（日常 C）。(ox,oy)=模板左下角 pt；s=缩放（pt per mm）。"""
    W, H = 210, 297
    g = GEOM
    # 底
    c.setFillColor(HexColor("#F7F1E7"))
    c.setStrokeColor(HexColor("#B08968"))
    c.setLineWidth(0.8)
    c.rect(ox, oy, _mm(W) * s, _mm(H) * s, stroke=1, fill=1)
    # 书脊
    c.setFillColor(HexColor("#492D22"))
    c.rect(ox, oy, _mm(g["spine_w"]) * s, _mm(H) * s, stroke=0, fill=1)
    X = lambda mx: ox + _mm(mx) * s
    Y = lambda my: oy + _mm(my) * s
    lx = X(g["margin_l"])
    if full_text:
        txt(c, lx, Y(g["eyebrow_y"]), EYEBROW_TEXT, "NSC-SB", 9 * s, "#B08968", cs=2 * s)
        txt(c, lx, Y(g["title1_y"]), TITLE_TEXT_1, "NSC-XB", g["title_pt"] * s, "#6B4028")
        txt(c, lx, Y(g["title2_y"]), TITLE_TEXT_2, "NSC-XB", g["title_pt"] * s, "#6B4028")
        txt(c, lx, Y(g["subtitle_y"]), SUBTITLE_TEXT, "NSC", g["subtitle_pt"] * s, "#492D22")
        txt(c, lx, Y(g["info_y"]), INFO_TEXT, "NSC", g["info_pt"] * s, "#492D22")
        pill(c, lx + 18 * mm * s, Y(g["pill_cy"]), PILL_TEXT, "#B08968", "#492D22",
             size=9.5 * s, h=9 * mm * s, pad_h=5.5 * mm * s)
        hr(c, lx, Y(g["rule_y"]), _mm(W - g["margin_l"] - g["margin_r"]) * s, "#E3D0BA", 0.6)
        txt(c, lx, Y(g["foot_y"]), FOOT_TEXT, "NSC-SB", 8 * s, "#B08968", cs=2 * s)
        txt_r(c, ox + _mm(W - g["margin_r"]) * s, Y(g["foot_y"]), "NO.01",
              "NSC-SB", 8 * s, "#B08968", cs=2 * s)
    else:
        # wireframe：文字全部用色条表达
        def bar(mx, my, wmm, hmm, hexc, r=0):
            c.setFillColor(HexColor(hexc))
            if r > 0:
                c.roundRect(X(mx), Y(my), _mm(wmm) * s, _mm(hmm) * s, r, stroke=0, fill=1)
            else:
                c.rect(X(mx), Y(my), _mm(wmm) * s, _mm(hmm) * s, stroke=0, fill=1)
        bar(g["margin_l"], g["eyebrow_y"], 34, 3.2, "#B08968", 1.6)
        bar(g["margin_l"], g["title1_y"] - 3, 62, 9.5, "#6B4028", 1.5)
        bar(g["margin_l"], g["title2_y"] - 3, 48, 9.5, "#6B4028", 1.5)
        bar(g["margin_l"], g["subtitle_y"] - 2, 72, 3.6, "#492D22")
        bar(g["margin_l"], g["info_y"] - 2, 30, 3.2, "#492D22")
        bar(g["margin_l"], g["pill_cy"] - 4.5, 26, 9, "#B08968", 4.5)
        hr(c, X(g["margin_l"]), Y(g["rule_y"]), _mm(W - g["margin_l"] - g["margin_r"]) * s, "#E3D0BA", 0.6)
        bar(g["margin_l"], g["foot_y"] - 1.5, 26, 3, "#B08968", 1.5)


def draw_fullbleed_cover(c, ox, oy, s, full_text=True):
    """全幅版封面（正式 A，深底）。"""
    W, H = 210, 297
    X = lambda mx: ox + _mm(mx) * s
    Y = lambda my: oy + _mm(my) * s
    c.setFillColor(HexColor("#492D22"))
    c.setStrokeColor(HexColor("#B26B3F"))
    c.setLineWidth(0.8)
    c.rect(ox, oy, _mm(W) * s, _mm(H) * s, stroke=1, fill=1)
    # 浅色书脊（与 C 版深栗条同位同宽 8mm，正负镜像，双版式风格对位；TA 定稿浅驼）
    c.setFillColor(HexColor("#E3D0BA"))
    c.rect(ox, oy, _mm(GEOM["spine_w"]) * s, _mm(H) * s, stroke=0, fill=1)
    lx = X(28)
    if full_text:
        txt(c, lx, Y(262), "PALETTE · TYPE · LAYOUT SPEC", "NSC-SB", 9 * s, "#EAD9C0", cs=2 * s)
        txt(c, lx, Y(216), "文档主标题第一行", "NSC-XB", 30 * s, "#EAD9C0")
        txt(c, lx, Y(196), "文档主标题第二行", "NSC-XB", 30 * s, "#EAD9C0")
        c.setFillColor(HexColor("#B26B3F"))
        c.rect(lx, Y(184), _mm(36) * s, _mm(4) * s, stroke=0, fill=1)
        txt(c, lx, Y(170), "副题 · 单位或系列说明", "NSC", 12 * s, "#EAD9C0")
        txt(c, lx, Y(158), "编制单位 · 2026 年 11 月", "NSC", 10.5 * s, "#EAD9C0")
        # 底部层级短条组
        for i, hexc in enumerate(["#331E14", "#7C4324", "#B26B3F"]):
            c.setFillColor(HexColor(hexc))
            c.rect(lx, Y(23) + i * _mm(7) * s, _mm(28) * s, _mm(4) * s, stroke=0, fill=1)
        txt_r(c, ox + _mm(210 - 20) * s, Y(21), "NO.01", "NSC-SB", 8 * s, "#EAD9C0", cs=2 * s)
    else:
        def bar(mx, my, wmm, hmm, hexc, r=0):
            c.setFillColor(HexColor(hexc))
            if r > 0:
                c.roundRect(X(mx), Y(my), _mm(wmm) * s, _mm(hmm) * s, r, stroke=0, fill=1)
            else:
                c.rect(X(mx), Y(my), _mm(wmm) * s, _mm(hmm) * s, stroke=0, fill=1)
        bar(28, 262, 34, 3.2, "#EAD9C0", 1.6)
        bar(28, 216 - 4, 68, 11, "#EAD9C0", 1.5)
        bar(28, 196 - 4, 54, 11, "#EAD9C0", 1.5)
        bar(28, 184, 36, 4, "#B26B3F")
        bar(28, 170 - 2, 60, 3.6, "#EAD9C0")
        bar(28, 158 - 2, 34, 3.2, "#EAD9C0")
        for i, hexc in enumerate(["#331E14", "#7C4324", "#B26B3F"]):
            bar(28, 23 + i * 7, 28, 4, hexc)


def draw_inner_page(c, ox, oy, s):
    """内页缩略图（纸白底 wireframe · 默认）。"""
    W, H = 210, 297
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(HexColor("#B08968"))
    c.setLineWidth(0.8)
    c.rect(ox, oy, _mm(W) * s, _mm(H) * s, stroke=1, fill=1)
    X = lambda mx: ox + _mm(mx) * s
    Y = lambda my: oy + _mm(my) * s

    def bar(mx, my, wmm, hmm, hexc, r=0):
        c.setFillColor(HexColor(hexc))
        if r > 0:
            c.roundRect(X(mx), Y(my), _mm(wmm) * s, _mm(hmm) * s, r, stroke=0, fill=1)
        else:
            c.rect(X(mx), Y(my), _mm(wmm) * s, _mm(hmm) * s, stroke=0, fill=1)
    # 页眉
    bar(20, 275, 40, 3, "#B08968", 1.5)
    hr(c, X(20), Y(270), _mm(210 - 40) * s, "#E3D0BA", 0.5)
    # 章节标题 + 正文行（隔行浅驼）
    bar(20, 240, 44, 6.5, "#6B4028", 1)
    for i in range(9):
        yy = 226 - i * 9
        hexc = "#E3D0BA" if i % 2 == 1 else "#B08968"
        bar(20, yy, 170 if i % 4 != 3 else 120, 2.6, hexc)
    # 表格
    bar(20, 118, 170, 7, "#492D22", 1)
    for i in range(4):
        yy = 110 - i * 7
        bar(20, yy, 170, 6.6, "#E3D0BA" if i % 2 == 1 else "#F7F1E7")
    # 页脚
    hr(c, X(20), Y(18), _mm(170) * s, "#E3D0BA", 0.5)
    bar(20, 12, 30, 2.4, "#B08968", 1.2)


# ============================================================
# 页面构建
# ============================================================

def page_01_cover(c):
    """P1 封面（书脊版 · 自演示）。"""
    page_bg(c)
    draw_spine_cover(c, 0, 0, 1.0, full_text=True)
    # 出血角标（提示这是 A4 原大）
    txt_r(c, PAGE_W - 20 * mm, PAGE_H - 14 * mm, "A4 · 210 × 297 mm", "NSC-SB", 9, "#B08968", cs=1.0)


def page_02_palettes(c):
    """P2 色板总览（HEX/RGB）。"""
    page_bg(c)
    page_header(c, "01 · 色板总览", "PALETTES", 2)
    y = M_TOP - 18 * mm
    for key in ("C", "A"):
        pal = PALETTES[key]
        y = section_label(c, ML, y, "%s · %s" % (key, pal["name"]), "「%s」" % pal["tag"], pal["en"])
        for cname, chex, crole in pal["colors"]:
            chip(c, ML, y - 13 * mm, 24 * mm, 13 * mm, chex, r=2 * mm)
            rgb = hex2rgb(chex)
            txt(c, ML + 30 * mm, y - 2.5 * mm, cname, "NSC-SB", 12, "#6B4028")
            name_w = pdfmetrics.stringWidth(cname, "NSC-SB", 12)
            txt(c, ML + 30 * mm + name_w + 6, y - 2.5 * mm, crole, "NSC", 9.5, "#492D22")
            txt(c, ML + 30 * mm, y - 9.5 * mm,
                "HEX %s    RGB %d %d %d    %s" % (chex.upper(), *rgb, rgb2cmyk_str(rgb)),
                "NSC-SB", 9, "#B08968", cs=0.4)
            y -= 16.8 * mm
        y -= 4 * mm
    # 锚点注
    c.setFillColor(HexColor("#E3D0BA"))
    c.roundRect(ML, y - 14 * mm, CW, 14 * mm, 2 * mm, stroke=0, fill=1)
    txt(c, ML + 6 * mm, y - 9.5 * mm,
        "两板共用锚点 #492D22 深栗：C 的书脊/表头即 A 的封面主底，两板可自由混搭。",
        "NSC-SB", 10, "#492D22")


def page_03_system(c):
    """P3 组合系统与 Word 映射。"""
    page_bg(c)
    page_header(c, "02 · 组合系统与 Word 映射", "SYSTEM & WORD STYLES", 3)
    y0 = M_TOP - 20 * mm

    # ---- 左列：两种组合模式 ----
    lw = 86 * mm
    txt(c, ML, y0, "模式一 · 日常（书脊封面 × 纸白内页）", "NSC-SB", 12, "#492D22")
    s = 0.19  # mini 缩放（pt per mm）
    mw, mh = 210 * mm * s, 297 * mm * s  # ≈40×56.6mm
    y1 = y0 - 8 * mm - mh
    draw_spine_cover(c, ML, y1, s, full_text=False)
    draw_inner_page(c, ML + mw + 8 * mm, y1, s)
    txt(c, ML, y1 - 5 * mm, "封面 · 书脊版", "NSC", 9, "#B08968")
    txt(c, ML + mw + 8 * mm, y1 - 5 * mm, "内页 · 纸白（默认）", "NSC", 9, "#B08968")

    y2 = y1 - 12 * mm
    txt(c, ML, y2, "模式二 · 正式（A 封面 × 纸白内页）", "NSC-SB", 12, "#492D22")
    y3 = y2 - 8 * mm - mh
    draw_fullbleed_cover(c, ML, y3, s, full_text=False)
    draw_inner_page(c, ML + mw + 8 * mm, y3, s)
    txt(c, ML, y3 - 5 * mm, "封面 · 全幅版", "NSC", 9, "#B08968")
    txt(c, ML + mw + 8 * mm, y3 - 5 * mm, "内页 · 纸白（默认）", "NSC", 9, "#B08968")

    # ---- 右列：Word 样式映射表 ----
    tx = ML + 88 * mm + 8 * mm
    tw = PAGE_W - MR - tx                       # ≈70mm
    txt(c, tx, y0, "Word 样式映射（兜底 · 手动复刻用）", "NSC-SB", 12, "#492D22")
    rows = WORD_MAP_ROWS
    col1, col2 = 26 * mm, (tw - 26 * mm) / 2.0  # 值列各 ≈22mm
    rh = 13.2 * mm
    ty = y0 - 8 * mm - rh
    # 表头
    c.setFillColor(HexColor("#492D22"))
    c.roundRect(tx, ty, tw, rh, 1.5 * mm, stroke=0, fill=1)
    txt(c, tx + 2.5 * mm, ty + rh - 5.2 * mm, "Word 元素", "NSC-SB", 8.5, "#EAD9C0")
    txt(c, tx + col1 + 2 * mm, ty + rh - 5.2 * mm, "日常 C", "NSC-SB", 8.5, "#EAD9C0")
    txt(c, tx + col1 + col2 + 2 * mm, ty + rh - 5.2 * mm, "深底 A", "NSC-SB", 8.5, "#EAD9C0")
    ty -= rh
    for i, (elem, cv, av) in enumerate(rows):
        if i % 2 == 0:
            c.setFillColor(HexColor("#E3D0BA"))
            c.rect(tx, ty, tw, rh, stroke=0, fill=1)
        txt(c, tx + 2.5 * mm, ty + rh - 5.2 * mm, elem, "NSC", 8.5, "#492D22")
        for j, (val, note) in enumerate((cv, av)):
            cx0 = tx + col1 + j * col2
            if val != "—":
                dot(c, cx0 + 2.7 * mm, ty + rh - 3.5 * mm, 2.6 * mm, val)
            txt(c, cx0 + 4.8 * mm, ty + rh - 4.0 * mm, val, "NSC-SB", 8.5,
                "#6B4028" if j == 0 else "#492D22")
            if note:
                for k, ln in enumerate(wrap_zh(note, "NSC", 7.5, col2 - 5 * mm)):
                    txt(c, cx0 + 2 * mm, ty + rh - 8.4 * mm - k * 3.8 * mm, ln,
                        "NSC", 7.5, "#B08968")
        ty -= rh
    # 表注
    ty -= 2 * mm
    txt(c, tx, ty, "注：焦糖 #B26B3F 对主栗底仅 3.2:1，深底上不作文字；", "NSC", 8.5, "#B08968")
    txt(c, tx, ty - 4.5 * mm, "奶咖 #B08968 对雾白底 2.8:1，仅作标签与图形色（见 05）。", "NSC", 8.5, "#B08968")


def _spec_list(c, tx, ty, spec):
    """右侧规格明细：每行一张浅驼卡片，值列自动折行。返回底部 y。"""
    tw = PAGE_W - MR - tx
    txt(c, tx, ty, "规格明细", "NSC-SB", 12, "#492D22")
    ty -= 3 * mm
    key_w = 19 * mm
    val_x = tx + key_w
    val_w = tw - key_w - 1 * mm
    for k, v in spec:
        lines = wrap_zh(v, "NSC", 8.5, val_w)
        rh = max(11.2 * mm, 4.6 * mm * len(lines) + 6.4 * mm)
        c.setFillColor(HexColor("#E3D0BA"))
        c.roundRect(tx, ty - rh, tw, rh, 1.5 * mm, stroke=0, fill=1)
        txt(c, tx + 2.5 * mm, ty - 7.8 * mm, k, "NSC-SB", 9, "#6B4028")
        for j, ln in enumerate(lines):
            txt(c, val_x, ty - 7.8 * mm - j * 4.6 * mm, ln, "NSC", 8.5, "#492D22")
        ty -= rh + 1.6 * mm
    return ty


def page_04_spine_layout(c):
    """P4 封面版式 · 书脊版规格。"""
    page_bg(c)
    page_header(c, "03 · 封面版式 · 书脊版（日常）", "SPINE LAYOUT", 4)
    g = GEOM
    s = 0.42                                   # 模板等比缩放
    ox, oy = ML, 48 * mm
    tpl_w, tpl_h = 210 * mm * s, 297 * mm * s  # ≈88 × 125 mm
    draw_spine_cover(c, ox, oy, s, full_text=True)
    # 尺寸标注
    dim_v(c, ox - 5 * mm, oy, oy + tpl_h, "297")
    dim_h(c, ox, ox + tpl_w, oy - 6 * mm, "210")
    dim_h(c, ox, ox + _mm(g["spine_w"]) * s, oy + tpl_h + 5 * mm, "8", "#E3D0BA")
    dim_h(c, ox + _mm(g["spine_w"]) * s, ox + _mm(g["margin_l"]) * s,
          oy + _mm(g["eyebrow_y"]) * s + 5 * mm, "20", "#E3D0BA")
    dim_v(c, ox + tpl_w + 5 * mm, oy, oy + _mm(g["rule_y"]) * s, "30", "#E3D0BA")
    txt(c, ox, oy + tpl_h + 11 * mm, "模板等比缩放 42% · 单位 mm · 原大 210 × 297",
        "NSC", 8.5, "#B08968")
    # 右侧规格明细
    tx = ox + tpl_w + 14 * mm
    spec = [
        ("画幅", "A4 210×297 · 出血3mm"),
        ("书脊色条", "宽8mm · 深栗 #492D22 · 通高"),
        ("版心", "左28·右20·天头35·地脚25mm"),
        ("眉头", "9pt 奶咖 · 字距2pt · 高262mm"),
        ("主标题", "26pt 思源宋XB · 栗棕 · 行距13mm"),
        ("副题", "12pt Regular · 深栗"),
        ("信息行", "10.5pt Regular · 深栗"),
        ("胶囊标签", "奶咖底·深栗字 9.5pt · 高9mm"),
        ("底部细线", "浅驼 0.5pt · 高30mm 处"),
        ("页脚编号", "8pt 奶咖 · 字距2pt"),
    ]
    ty = _spec_list(c, tx, M_TOP - 10 * mm, spec)
    ty -= 2 * mm
    txt(c, tx, ty, "Word 复刻：页边距按版心设置；色条用矩形", "NSC", 8, "#B08968")
    txt(c, tx, ty - 4.5 * mm, "形状填充 #492D22 压住左边距，文字不入色条。", "NSC", 8, "#B08968")


def page_05_fullbleed_layout(c):
    """P5 封面版式 · 全幅版规格。"""
    page_bg(c)
    page_header(c, "04 · 封面版式 · 全幅版（正式）", "FULL-BLEED LAYOUT", 5)
    s = 0.42
    ox, oy = ML, 48 * mm
    tpl_w, tpl_h = 210 * mm * s, 297 * mm * s
    # 出血框（虚线，3mm × s）
    c.setStrokeColor(HexColor("#B26B3F"))
    c.setLineWidth(0.5)
    c.setDash(2, 2)
    c.rect(ox - 3 * mm * s, oy - 3 * mm * s,
           tpl_w + 6 * mm * s, tpl_h + 6 * mm * s, stroke=1, fill=0)
    c.setDash()
    draw_fullbleed_cover(c, ox, oy, s, full_text=True)
    dim_v(c, ox - 10 * mm, oy, oy + tpl_h, "297")
    dim_h(c, ox, ox + tpl_w, oy - 6 * mm, "210")
    txt(c, ox, oy + tpl_h + 11 * mm, "虚线 = 出血 3 mm（成品 216 × 303）· 单位 mm",
        "NSC", 8.5, "#B08968")
    tx = ox + tpl_w + 14 * mm
    spec = [
        ("满版底色", "主栗 #492D22 · 压满出血"),
        ("浅色书脊", "宽8mm · 浅驼 #E3D0BA · 通高"),
        ("眉头", "9pt 蜜白 · 字距2pt · 高262mm"),
        ("主标题", "30pt ExtraBold · 蜜白 · 行距20mm"),
        ("焦糖短条", "36×4mm · 标题下"),
        ("副题", "12pt 蜜白"),
        ("信息行", "10.5pt 蜜白"),
        ("层级短条组", "墨栗/赤栗/焦糖 · 各28×4mm"),
        ("编号", "8pt 蜜白 · 字距2pt · 右下"),
        ("内页", "纸白默认 · 护眼可切雾白（见02）"),
        ("封底", "版式 B' · 装订镜像 · 书脊右置 · 可选 EAN-13"),
    ]
    ty = _spec_list(c, tx, M_TOP - 10 * mm, spec)
    ty -= 2 * mm
    txt(c, tx, ty, "深底印刷前必读 06 · 印刷对照。", "NSC", 8, "#B08968")


def page_06_type_contrast(c):
    """P6 字号级数 · 对比度 · 使用守则。"""
    page_bg(c)
    page_header(c, "05 · 字号级数 · 对比度 · 使用守则", "TYPE & CONTRAST", 6)

    # ---- 字号级数表 ----
    y = M_TOP - 16 * mm
    txt(c, ML, y, "字号级数", "NSC-SB", 12, "#492D22")
    y -= 6 * mm
    cols = [("级数", 22 * mm), ("字号/行距", 26 * mm), ("用色", 0), ("用途", 0)]
    tw = CW
    c.setFillColor(HexColor("#492D22"))
    c.roundRect(ML, y - 8 * mm, tw, 8 * mm, 1.5 * mm, stroke=0, fill=1)
    txt(c, ML + 3 * mm, y - 5.8 * mm, "级数", "NSC-SB", 9.5, "#EAD9C0")
    txt(c, ML + 26 * mm, y - 5.8 * mm, "字号 / 行距", "NSC-SB", 9.5, "#EAD9C0")
    txt(c, ML + 60 * mm, y - 5.8 * mm, "用色", "NSC-SB", 9.5, "#EAD9C0")
    txt(c, ML + 100 * mm, y - 5.8 * mm, "用途", "NSC-SB", 9.5, "#EAD9C0")
    y -= 8 * mm
    rh = 8 * mm
    for i, (name, size, leading, hexc, use) in enumerate(TYPE_SCALE):
        if i % 2 == 0:
            c.setFillColor(HexColor("#E3D0BA"))
            c.rect(ML, y - rh, tw, rh, stroke=0, fill=1)
        txt(c, ML + 3 * mm, y - 5.8 * mm, name, "NSC-SB", 9.5, "#492D22")
        txt(c, ML + 26 * mm, y - 5.8 * mm, "%g pt / %g pt" % (size, leading), "NSC", 9.5, "#492D22")
        dot(c, ML + 62.2 * mm, y - 3 * mm, 3.4 * mm, hexc)
        txt(c, ML + 66 * mm, y - 5.8 * mm, hexc.upper(), "NSC-SB", 9, "#B08968", cs=0.4)
        txt(c, ML + 100 * mm, y - 5.8 * mm, use, "NSC", 9.5, "#492D22")
        y -= rh
    y -= 8 * mm

    # ---- 对比度表（左） + 守则（右） ----
    half = (CW - 8 * mm) / 2.0
    # 对比度
    txt(c, ML, y, "对比度核查（WCAG 2.1，脚本实算）", "NSC-SB", 12, "#492D22")
    y2 = y - 6 * mm
    ch = 7.6 * mm
    c.setFillColor(HexColor("#492D22"))
    c.roundRect(ML, y2 - ch, half, ch, 1.5 * mm, stroke=0, fill=1)
    txt(c, ML + 3 * mm, y2 - 5.4 * mm, "前景 / 背景", "NSC-SB", 9, "#EAD9C0")
    txt(c, ML + 33 * mm, y2 - 5.4 * mm, "比值", "NSC-SB", 9, "#EAD9C0")
    txt(c, ML + 45 * mm, y2 - 5.4 * mm, "判定（WCAG 2.1）", "NSC-SB", 9, "#EAD9C0")
    y2 -= ch
    for i, (fn, fh, bn, bh, use) in enumerate(CONTRAST_PAIRS):
        if i % 2 == 0:
            c.setFillColor(HexColor("#E3D0BA"))
            c.rect(ML, y2 - ch, half, ch, stroke=0, fill=1)
        ratio = contrast_ratio(fh, bh)
        txt(c, ML + 3 * mm, y2 - 5.4 * mm, "%s / %s" % (fn, bn), "NSC", 8.5, "#492D22")
        txt(c, ML + 33 * mm, y2 - 5.4 * mm, "%.1f:1" % ratio, "NSC-SB", 8.5, "#6B4028")
        txt(c, ML + 45 * mm, y2 - 5.4 * mm, wcag_verdict(ratio), "NSC", 8.5, "#492D22")
        y2 -= ch
    # 守则
    rx = ML + half + 8 * mm
    txt(c, rx, y, "使用守则", "NSC-SB", 12, "#492D22")
    ry = y - 8 * mm
    for i, rule in enumerate(USAGE_RULES, 1):
        txt(c, rx, ry, "%02d" % i, "NSC-SB", 10, "#B08968", cs=0.5)
        # 手动折行：按宽度切句
        max_w = CW - (rx - ML) - 8 * mm
        lines = wrap_zh(rule, "NSC", 9.5, max_w)
        for j, ln in enumerate(lines):
            txt(c, rx + 10 * mm, ry, ln, "NSC", 9.5, "#492D22")
            ry -= 5.2 * mm
        ry -= 2.4 * mm


_TOKEN = re.compile(r"[0-9A-Za-z#+×.%°/·\-—≥≤±~≈]+|.")


def wrap_zh(s, font, size, max_w):
    """按宽度折行：ASCII 连续串为原子（mm/pt/#492D22 不断开），
    闭合标点禁落行首（行首禁则），必要时连同前一 token 一起下移。"""
    tokens = _TOKEN.findall(s)
    NO_START = "）」』】》〉”！？。，、；："
    lines, cur = [], []
    for tok in tokens:
        if pdfmetrics.stringWidth("".join(cur) + tok, font, size) <= max_w:
            cur.append(tok)
        elif len(tok) == 1 and tok in NO_START and cur:
            prev = cur.pop()
            lines.append("".join(cur))
            cur = [prev, tok]
        else:
            lines.append("".join(cur))
            cur = [tok]
    if cur:
        lines.append("".join(cur))
    return lines


def page_07_print(c, copyrighted=False):
    """P7 印刷对照与注意事项 + 版权页脚。"""
    page_bg(c)
    page_header(c, "06 · 印刷对照与注意事项", "PRINT NOTES", 7)

    y = M_TOP - 16 * mm
    txt(c, ML, y, "CMYK 对照（简易转换 · 打样为准）", "NSC-SB", 12, "#492D22")
    y -= 6 * mm
    rh = 8.2 * mm
    c.setFillColor(HexColor("#492D22"))
    c.roundRect(ML, y - rh, CW, rh, 1.5 * mm, stroke=0, fill=1)
    for label, xoff in (("色名", 3), ("色样", 22), ("HEX", 40), ("CMYK", 72), ("用途", 108)):
        txt(c, ML + xoff * mm, y - 5.8 * mm, label, "NSC-SB", 9, "#EAD9C0")
    y -= rh
    for key in ("C", "A"):
        for i, (cname, chex, crole) in enumerate(PALETTES[key]["colors"]):
            if (i + (0 if key == "C" else 5)) % 2 == 0:
                c.setFillColor(HexColor("#E3D0BA"))
                c.rect(ML, y - rh, CW, rh, stroke=0, fill=1)
            txt(c, ML + 3 * mm, y - 5.8 * mm, "%s · %s" % (key, cname), "NSC", 9, "#492D22")
            chip(c, ML + 22 * mm, y - 6.4 * mm, 12 * mm, 5 * mm, chex, r=1 * mm)
            txt(c, ML + 40 * mm, y - 5.8 * mm, chex.upper(), "NSC-SB", 9, "#6B4028", cs=0.4)
            txt(c, ML + 72 * mm, y - 5.8 * mm, rgb2cmyk_str(hex2rgb(chex)), "NSC-SB", 9, "#492D22", cs=0.4)
            txt(c, ML + 108 * mm, y - 5.8 * mm, crole, "NSC", 9, "#492D22")
            y -= rh
    y -= 8 * mm

    txt(c, ML, y, "印刷注意", "NSC-SB", 12, "#492D22")
    y -= 8 * mm
    for note in PRINT_NOTES:
        lines = wrap_zh("· " + note, "NSC", 9.5, CW - 6 * mm)
        for ln in lines:
            txt(c, ML + 3 * mm, y, ln, "NSC", 9.5, "#492D22")
            y -= 5.4 * mm
        y -= 1.8 * mm

    # ---- 版权栏（版本区分处） ----
    cy = 44 * mm
    hr(c, ML, cy, CW, "#E3D0BA", 0.6)
    txt(c, ML, cy - 6.5 * mm, "本设计书由 gen_palette_book.py 生成（reportlab · BSD 许可）", "NSC", 8.5, "#B08968")
    txt(c, ML, cy - 11.5 * mm, "字体：Noto Serif SC 思源宋体（SIL OFL 1.1 · 可商用可嵌入）", "NSC", 8.5, "#B08968")
    if copyrighted:
        txt(c, ML, cy - 16.5 * mm, COPYRIGHT_LINE, "NSC-SB", 8.5, "#6B4028")
    else:
        txt(c, ML, cy - 16.5 * mm, "脚本与依赖许可见包内「授权与依赖说明」。", "NSC", 8.5, "#B08968")


# ============================================================
# 构建
# ============================================================

PAGES = [page_01_cover, page_02_palettes, page_03_system,
         page_04_spine_layout, page_05_fullbleed_layout, page_06_type_contrast]


def build(path, copyrighted=False):
    c = _canvas.Canvas(path, pagesize=A4)
    c.setTitle(DOC_TITLE)
    if copyrighted:
        c.setAuthor(CREATOR_ID)
        c.setSubject(COPYRIGHT_LINE)
        c.setKeywords("配色,版式,设计书,雾林奶咖,栗皮本色,湫黎")
        c.setCreator(CREATOR_ID)
    for i, fn in enumerate(PAGES, 1):
        fn(c)
        c.showPage()
    page_07_print(c, copyrighted=copyrighted)
    c.showPage()
    c.save()


def main():
    ap = argparse.ArgumentParser(description="生成《文档封面配色·版式设计书》双版本")
    ap.add_argument("--out", default=".", help="输出目录")
    ap.add_argument("--font-dir", default=None, help="Noto Serif SC 字体目录")
    args = ap.parse_args()
    register_fonts(args.font_dir)
    os.makedirs(args.out, exist_ok=True)
    p1 = os.path.join(args.out, "配色版式设计书_V2.3_无版权.pdf")
    p2 = os.path.join(args.out, "配色版式设计书_V2.3.1_带版权.pdf")
    build(p1, copyrighted=False)
    build(p2, copyrighted=True)
    # stdout 打印对比度核查值（交付前 sanity）
    print("== 对比度核查（WCAG 2.1） ==")
    for fn, fh, bn, bh, use in CONTRAST_PAIRS:
        r = contrast_ratio(fh, bh)
        print("  %-4s on %-4s : %5.2f:1  %s | %s" % (fn, bn, r, wcag_verdict(r), use))
    print("已生成：")
    print("  " + p1)
    print("  " + p2)


if __name__ == "__main__":
    main()

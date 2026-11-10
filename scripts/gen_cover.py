#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一封面生成器（三版式）· 1:1 A4 210×297
  --layout spine      书脊版 · 版式 A · C 雾林奶咖 · 浅底 —— 日常文档封面
  --layout fullbleed  全幅版 · 版式 B · A 栗皮本色 · 深底 —— 正式文档封面（默认）
  --layout back       封底 · 版式 B' · A 栗皮本色 · 深底 —— 与全幅版镜像配套（书脊条右置贴装订缝）
复用 gen_palette_book.py（五级字体探测链 + 绘图辅助 + 母版几何），
版式几何分别照搬母版 draw_spine_cover / draw_fullbleed_cover，不可混用。
许可随主脚本：CC BY-NC 4.0（署名 湫黎 · 非商用）。

用法示例：
  python3 gen_cover.py --layout fullbleed \\
      --eyebrow "API USAGE SUMMARY" --title1 "API 消费小结" \\
      --title2 "2026 年 10 月—11 月" --subtitle "30 天账单复盘 · 费用与用量" \\
      --info "统计区间 2026-10-12 — 2026-11-10" --corner-no "SUMMARY · NO.01" \\
      --out 封面_全幅版.pdf --bleed 3 --png 150
  python3 gen_cover.py --layout back --barcode "978-0-000000-00-0" \\
      --out 封底.pdf            # 封底：默认不带条码；传真实 EAN-13 才画（无码不出码）
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gen_palette_book as gp
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as _canvas

# 版心可用文字宽（210 - 左28 - 右20）
MAX_TEXT_W = 162 * mm
LAYOUT_NAMES = {"spine": "书脊版", "fullbleed": "全幅版", "back": "封底"}


def _fits(tag, s, font, size, cs, max_w):
    """排版前断言：文字不溢出版心，超宽即 WARN 并返回 False。"""
    w = gp.pdfmetrics.stringWidth(s, font, size) + cs * max(0, len(s) - 1)
    ok = w <= max_w
    print("%s  %-8s 宽 %.1fmm / 限 %.0fmm" % ("PASS" if ok else "WARN", tag, w / mm, max_w / mm))
    return ok


def draw_fullbleed(c, eyebrow, title1, title2, subtitle, info, corner_no):
    """全幅版（版式 B · A 配色深底）。坐标 mm，原点左下，与母版 draw_fullbleed_cover 一致。"""
    g = gp._mm
    c.setFillColor(HexColor("#492D22"))
    c.rect(0, 0, 210 * mm, 297 * mm, stroke=0, fill=1)
    # 浅色书脊（浅驼 8mm 通高，与书脊版深栗条同位同宽，正负镜像；TA 2026-11-10 定稿）
    c.setFillColor(HexColor("#E3D0BA"))
    c.rect(0, 0, g(gp.GEOM["spine_w"]), g(297), stroke=0, fill=1)
    lx = g(28)
    gp.txt(c, lx, g(262), eyebrow, "NSC-SB", 9, "#EAD9C0", cs=2)
    gp.txt(c, lx, g(216), title1, "NSC-XB", 30, "#EAD9C0")
    gp.txt(c, lx, g(196), title2, "NSC-XB", 30, "#EAD9C0")
    # 焦糖短条 36×4mm，紧贴标题下
    c.setFillColor(HexColor("#B26B3F"))
    c.rect(lx, g(184), g(36), g(4), stroke=0, fill=1)
    gp.txt(c, lx, g(170), subtitle, "NSC", 12, "#EAD9C0")
    gp.txt(c, lx, g(158), info, "NSC", 10.5, "#EAD9C0")
    # 底部层级短条组：墨栗 / 赤栗 / 焦糖，各 28×4mm，纵向间距 7mm
    for i, hexc in enumerate(["#331E14", "#7C4324", "#B26B3F"]):
        c.setFillColor(HexColor(hexc))
        c.rect(lx, g(23) + i * g(7), g(28), g(4), stroke=0, fill=1)
    # 右下编号 8pt 蜜白 · 字距 2pt · 右对齐版心右缘
    gp.txt_r(c, g(190), g(21), corner_no, "NSC-SB", 8, "#EAD9C0", cs=2)


# ---- EAN-13 编码表（行业标准，公有领域） ----
_EAN_L = ["0001101", "0011001", "0010011", "0111101", "0100011",
          "0110001", "0101111", "0111011", "0110111", "0001011"]
_EAN_G = ["0100111", "0110011", "0011011", "0100001", "0011101",
          "0111001", "0000101", "0010001", "0001001", "0010111"]
_EAN_R = ["1110010", "1100110", "1101100", "1000010", "1011100",
          "1001110", "1010000", "1000100", "1001000", "1110100"]
_EAN_PARITY = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG",
               "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]


def _ean13_bits(code):
    """13 位数字 → 95 模块位串（起始符/左数据/中缝/右数据/终止符）。"""
    bits = "101"
    parity = _EAN_PARITY[int(code[0])]
    for i in range(6):
        d = int(code[i + 1])
        bits += (_EAN_L if parity[i] == "L" else _EAN_G)[d]
    bits += "01010"
    for i in range(6):
        bits += _EAN_R[int(code[7 + i])]
    bits += "101"
    return bits


def _ean13_checksum_ok(code):
    s = sum(int(code[i]) * (1 if i % 2 == 0 else 3) for i in range(12))
    return (10 - s % 10) % 10 == int(code[12])


def _draw_barcode(c, code):
    """EAN-13 · 80% 放大率：雾白衬底 + 墨栗条 + 数字行。位置：左轴 X=28，距底 12mm。
    无码不出码：本函数仅在调用方验过 13 位后才执行。"""
    g = gp._mm
    mx = 0.264                                   # 模块宽（80% 放大）
    # 雾白衬底 40×34mm（含 EAN 静区富余 ≥3.6mm）
    c.setFillColor(HexColor("#F7F1E7"))
    c.rect(g(28), g(12), g(40), g(34), stroke=0, fill=1)
    # 条块：95 模块 × 0.264 = 25.08mm，水平居中于衬底
    x0 = 28 + (40 - 95 * 0.264) / 2
    bits = _ean13_bits(code)
    c.setFillColor(HexColor("#331E14"))
    for i, bit in enumerate(bits):
        if bit == "1":
            guard = i < 3 or 45 <= i <= 49 or i >= 92
            y, h = (20, 20) if guard else (22, 18)   # 守卫条向下延伸 2mm（经典样式）
            c.rect(g(x0 + i * mx), g(y), g(mx), g(h), stroke=0, fill=1)
    # 数字行：首位在条块左侧，左右半区各居中（经典口袋式）
    ink = "#331E14"
    gp.txt(c, g(x0 - 3.2), g(13.5), code[0], "NSC-SB", 7.5, ink)
    gp.txt_c(c, g(x0 + (3 + 42 / 2) * mx), g(13.5), code[1:7], "NSC-SB", 7.5, ink)
    gp.txt_c(c, g(x0 + (50 + 42 / 2) * mx), g(13.5), code[7:], "NSC-SB", 7.5, ink)


def draw_back(c, eyebrow, info, corner_no, barcode):
    """封底（版式 B' · A 配色深底 · 装订镜像）：书脊条右置贴装订缝，
    层级条组右下，编号/条码左下（开口侧）。坐标 mm，原点左下。"""
    g = gp._mm
    c.setFillColor(HexColor("#492D22"))
    c.rect(0, 0, 210 * mm, 297 * mm, stroke=0, fill=1)
    # 浅驼书脊 8mm 右置（双面装订后与封面书脊条同贴装订缝，TA 2026-11-10 定稿）
    c.setFillColor(HexColor("#E3D0BA"))
    c.rect(g(202), 0, g(8), g(297), stroke=0, fill=1)
    lx = g(28)
    # 中区（品牌锚点）：眉头标识 + 焦糖短条 + 年份行
    gp.txt(c, lx, g(150), eyebrow, "NSC-SB", 9, "#EAD9C0", cs=2.2)
    c.setFillColor(HexColor("#B26B3F"))
    c.rect(lx, g(139), g(36), g(4), stroke=0, fill=1)
    gp.txt(c, lx, g(126), info, "NSC", 10.5, "#EAD9C0", cs=1.2)
    # 层级短条组右下（镜像：焦糖→赤栗→墨栗，贴装订缝一端）
    for i, hexc in enumerate(["#B26B3F", "#7C4324", "#331E14"]):
        c.setFillColor(HexColor(hexc))
        c.rect(g(190 - 28), g(21) + i * g(10), g(28), g(4), stroke=0, fill=1)
    # 左下：条码（如有）与编号（无码时编号独立在 y=15，有码时上移成组）
    if barcode:
        _draw_barcode(c, barcode)
        gp.txt(c, lx, g(50), corner_no, "NSC-SB", 8, "#EAD9C0", cs=2)
    else:
        gp.txt(c, lx, g(15), corner_no, "NSC-SB", 8, "#EAD9C0", cs=2)


def main():
    ap = argparse.ArgumentParser(description="三版式生成器（书脊版·浅底 / 全幅版·深底 / 封底·装订镜像）")
    ap.add_argument("--layout", default="fullbleed", choices=["spine", "fullbleed", "back"],
                    help="spine=书脊版（浅底·用户点名要浅色时用）；fullbleed=全幅版（深底·默认，不传即深色）；"
                         "back=封底（深底·装订镜像，书脊条右置；≥8 页或正式文档时建议加）")
    ap.add_argument("--eyebrow", default=gp.EYEBROW_TEXT, help="眉头文字（封底作系列标识行）")
    ap.add_argument("--title1", default=gp.TITLE_TEXT_1, help="主标题第一行")
    ap.add_argument("--title2", default=gp.TITLE_TEXT_2, help="主标题第二行")
    ap.add_argument("--subtitle", default=gp.SUBTITLE_TEXT, help="副题")
    ap.add_argument("--info", default=gp.INFO_TEXT, help="信息行")
    ap.add_argument("--pill", default=gp.PILL_TEXT, help="胶囊标签文字（仅书脊版）")
    ap.add_argument("--foot", default=gp.FOOT_TEXT, help="底部页脚行（仅书脊版）")
    ap.add_argument("--corner-no", default="NO.01", help="编号（全幅版右下 / 封底左下）")
    ap.add_argument("--barcode", default=None, metavar="EAN13",
                    help="封底条码：13 位 EAN-13（连字符/空格允许）；不传不画——无码不出码，仅 --layout back 可用")
    ap.add_argument("--out", default=None, help="输出 PDF 路径（默认 当前目录/封面_版式_日期.pdf）")
    ap.add_argument("--bleed", type=float, default=0, metavar="MM",
                    help="出血 mm：全幅版四边出血（216×303）；书脊版仅色条侧（213×297）；默认 0 净尺寸")
    ap.add_argument("--png", type=int, default=None, metavar="DPI",
                    help="同时渲染 PNG 的 DPI（需系统 pdftoppm，可选）")
    args = ap.parse_args()

    # ---- 条码参数前置校验（无码不出码；错码不出码） ----
    barcode = None
    if args.barcode is not None:
        if args.layout != "back":
            ap.error("--barcode 仅 --layout back 可用")
        barcode = "".join(ch for ch in args.barcode if ch.isdigit())
        if len(barcode) != 13:
            ap.error("--barcode 需 13 位数字（EAN-13），收到 %d 位：%s" % (len(barcode), args.barcode))
        if not _ean13_checksum_ok(barcode):
            print("WARN  条码校验位不匹配（EAN-13 末位应为校验位），扫枪可能拒读——请核验码值。")

    gp.register_fonts(None)

    # ---- 溢出自检（三版共用的版心宽 162mm） ----
    title_pt = 26 if args.layout == "spine" else 30
    all_ok = True
    if args.layout == "back":
        all_ok &= _fits("眉头", args.eyebrow, "NSC-SB", 9, 2.2, MAX_TEXT_W)
        all_ok &= _fits("年份行", args.info, "NSC", 10.5, 1.2, MAX_TEXT_W)
    else:
        all_ok &= _fits("眉头", args.eyebrow, "NSC-SB", 9, 2, MAX_TEXT_W)
        all_ok &= _fits("标题一", args.title1, "NSC-XB", title_pt, 0, MAX_TEXT_W)
        all_ok &= _fits("标题二", args.title2, "NSC-XB", title_pt, 0, MAX_TEXT_W)
        all_ok &= _fits("副题", args.subtitle, "NSC", 12, 0, MAX_TEXT_W)
        all_ok &= _fits("信息行", args.info, "NSC", 10.5, 0, MAX_TEXT_W)
    if args.layout in ("fullbleed", "back"):
        all_ok &= _fits("编号", args.corner_no, "NSC-SB", 8, 2, MAX_TEXT_W)
    if not all_ok:
        print("存在超宽文字，建议缩短文案或换行后再出正式稿。")

    # ---- 画布（出血处理：封底同全幅版四边出血，书脊条向右压出血） ----
    b = args.bleed * mm
    if args.layout in ("fullbleed", "back"):
        size = ((210 + 2 * args.bleed) * mm, (297 + 2 * args.bleed) * mm)
    else:
        size = ((210 + args.bleed) * mm, 297 * mm)
    out = args.out or "封面_%s_%s.pdf" % (LAYOUT_NAMES[args.layout], date.today().strftime("%Y%m%d"))
    c = _canvas.Canvas(out, pagesize=size)
    c.setTitle("文档封面 · %s" % LAYOUT_NAMES[args.layout])
    c.setAuthor("湫黎")
    c.setSubject("版权所有 © 2026 湫黎 · CC BY-NC 4.0（署名 · 非商用）")

    if args.layout == "spine":
        # 预铺满出血区雾白，再平移到裁切坐标
        c.setFillColor(HexColor("#F7F1E7"))
        c.rect(0, 0, size[0], size[1], stroke=0, fill=1)
        c.translate(b, 0)
        gp.EYEBROW_TEXT = args.eyebrow
        gp.TITLE_TEXT_1 = args.title1
        gp.TITLE_TEXT_2 = args.title2
        gp.SUBTITLE_TEXT = args.subtitle
        gp.INFO_TEXT = args.info
        gp.PILL_TEXT = args.pill
        gp.FOOT_TEXT = args.foot
        gp.draw_spine_cover(c, 0, 0, 1.0, full_text=True)
        if b > 0:
            # 书脊色条压出血：裁切线外延 bleed mm（带 0.2mm 搭接防接缝）
            c.setFillColor(HexColor("#492D22"))
            c.rect(-b, 0, b + 0.2 * mm, 297 * mm, stroke=0, fill=1)
    elif args.layout == "back":
        c.setFillColor(HexColor("#492D22"))
        c.rect(0, 0, size[0], size[1], stroke=0, fill=1)
        c.translate(b, b)
        draw_back(c, args.eyebrow, args.info, args.corner_no, barcode)
        if b > 0:
            # 浅驼书脊条（右置）压出血：向右延伸至裁切线外（带 0.2mm 搭接防接缝）
            c.setFillColor(HexColor("#E3D0BA"))
            c.rect(210 * mm, 0, b + 0.2 * mm, 297 * mm, stroke=0, fill=1)
    else:
        c.setFillColor(HexColor("#492D22"))
        c.rect(0, 0, size[0], size[1], stroke=0, fill=1)
        c.translate(b, b)
        draw_fullbleed(c, args.eyebrow, args.title1, args.title2,
                       args.subtitle, args.info, args.corner_no)
        if b > 0:
            # 浅驼书脊条压出血：向左延伸至裁切线外（带 0.2mm 搭接防接缝）
            c.setFillColor(HexColor("#E3D0BA"))
            c.rect(-b, 0, b + 0.2 * mm, 297 * mm, stroke=0, fill=1)

    c.showPage()
    c.save()
    print("已生成：" + out)

    # ---- 可选 PNG 渲染（供目检/交付预览） ----
    if args.png:
        if shutil.which("pdftoppm"):
            subprocess.run(["pdftoppm", "-png", "-r", str(args.png), out,
                            os.path.splitext(out)[0]], check=True)
            print("已渲染 PNG（同目录同名）")
        else:
            print("提示：未找到 pdftoppm，跳过 PNG 渲染。")


if __name__ == "__main__":
    main()

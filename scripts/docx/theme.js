/* 雾林奶咖主题 · Node/docx 路线（自研，版权 湫黎，CC BY-NC 4.0）
 * 色值唯一来源：../../references/palette.json（与 reportlab 路线共用同一份数据契约）
 * 本文件禁止出现手写色值；要色，从 palette 取。
 * 依赖：docx (MIT)
 */
const path = require('path');
const {
  Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, TableLayoutType,
} = require('docx');

const PALETTE = require(path.join(__dirname, '..', '..', 'references', 'palette.json'));

/** 按色名取 docx 用的无 # 十六进制值 */
function hex(name, paletteKey = 'C') {
  const p = PALETTE.palettes[paletteKey];
  const hit = p.colors.find((c) => c.name === name);
  if (!hit) throw new Error('palette 里没有色名: ' + name);
  return hit.hex.replace('#', '');
}

/** 按字号级数名取 docx half-point 与行距 twip */
function type(name) {
  const t = PALETTE.type_scale.find((x) => x.name === name);
  if (!t) throw new Error('type_scale 里没有级数: ' + name);
  return { size: Math.round(t.pt * 2), line: Math.round(t.leading * 20), pt: t.pt };
}

const CREAM = hex('雾白');
const SAND = hex('浅驼');
const COFFEE = hex('奶咖');
const CHEST = hex('栗棕');
const DEEP = hex('深栗');

/* 字体策略：docx 只引用字体名、不嵌字体。默认用 SimSun/SimHei（宋/黑）——
 * Windows / WPS 全平台必有，打开即正确；追求与 PDF 路线（Noto Serif SC）完全
 * 同观感时，把下面两行 eastAsia 换成 'Noto Serif SC'，目标机需装该字体（OFL 1.1）。
 */
const BODY = { ascii: 'Times New Roman', eastAsia: 'SimSun', hAnsi: 'Times New Roman' };
const HEAD = { ascii: 'Times New Roman', eastAsia: 'SimHei', hAnsi: 'Times New Roman' };

const NB = { style: BorderStyle.NONE, size: 0, color: CREAM };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNo = { top: NB, bottom: NB, left: NB, right: NB, insideHorizontal: NB, insideVertical: NB };

const MM = 56.7;
const mm = (v) => Math.round(v * MM);

const body = (text) => new Paragraph({
  spacing: { line: type('正文').line, before: 0, after: 140 },
  alignment: AlignmentType.JUSTIFIED,
  indent: { firstLine: 480 },
  children: [new TextRun({ text, font: BODY, size: type('正文').size, color: DEEP })],
});

const bullet = (text) => new Paragraph({
  spacing: { line: type('正文').line, after: 70 },
  indent: { left: 480, hanging: 240 },
  children: [new TextRun({ text: '\u00b7 ' + text, font: BODY, size: type('正文').size, color: DEEP })],
});

const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 320, after: 160, line: type('章节标题').line },
  children: [new TextRun({ text, font: HEAD, bold: true, size: type('章节标题').size, color: CHEST })],
});

const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 280, after: 140, line: type('小节标题').line },
  children: [new TextRun({ text, font: HEAD, bold: true, size: type('小节标题').size, color: CHEST })],
});

const caption = (text) => new Paragraph({
  spacing: { before: 160, after: 120, line: type('辅助').line },
  keepNext: true,
  children: [new TextRun({ text, font: BODY, size: type('辅助').size, color: COFFEE, characterSpacing: 20 })],
});

const cell = (text, opts = {}) => new TableCell({
  margins: { top: 90, bottom: 90, left: 120, right: 120 },
  shading: opts.head ? { type: ShadingType.CLEAR, fill: DEEP }
    : (opts.zebra ? { type: ShadingType.CLEAR, fill: SAND } : undefined),
  width: opts.width ? { size: opts.width, type: WidthType.PERCENTAGE } : undefined,
  children: [new Paragraph({
    spacing: { line: Math.round(type('正文').line * 0.9), before: 0, after: 0 },
    alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
    children: [new TextRun({
      text, font: BODY, size: type('正文').size, bold: !!opts.head,
      color: opts.head ? CREAM : DEEP,
    })],
  })],
});

const mkTable = (headers, rows, widths, centerCols = []) => new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  layout: TableLayoutType.FIXED,
  borders: {
    top: { style: BorderStyle.SINGLE, size: 8, color: DEEP },
    bottom: { style: BorderStyle.SINGLE, size: 8, color: DEEP },
    left: NB, right: NB,
    insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: SAND },
    insideVertical: NB,
  },
  rows: [
    new TableRow({
      tableHeader: true, cantSplit: true,
      children: headers.map((t, j) => cell(t, { head: true, center: true, width: widths[j] })),
    }),
    ...rows.map((r, i) => new TableRow({
      cantSplit: true,
      children: r.map((t, j) => cell(String(t), { center: centerCols.includes(j), width: widths[j], zebra: i % 2 === 1 })),
    })),
  ],
});

/** Document 样式覆盖：把 docx 库内置的 Office 蓝默认样式全部压成色板色，
 *  否则 styles.xml 里会残留 2E74B5/1F4D78/0563C1 等名单外色（潜伏漂移）。
 *  用法：new Document({ styles: T.docStyles(), ... })
 */
function docStyles() {
  return {
    default: {
      document:  { run: { font: BODY, color: DEEP, size: type('正文').size } },
      title:     { run: { font: HEAD, color: CHEST, size: type('主标题').size, bold: true } },
      heading1:  { run: { font: HEAD, color: CHEST, size: type('章节标题').size, bold: true },
                   paragraph: { spacing: { before: 320, after: 160 } } },
      heading2:  { run: { font: HEAD, color: CHEST, size: type('小节标题').size, bold: true },
                   paragraph: { spacing: { before: 240, after: 120 } } },
      heading3:  { run: { font: BODY, color: DEEP, size: type('小节标题').size } },
      heading4:  { run: { font: BODY, color: DEEP, size: type('正文').size } },
      heading5:  { run: { font: BODY, color: DEEP, size: type('辅助').size } },
      heading6:  { run: { font: BODY, color: DEEP, size: type('标注').size } },
      hyperlink: { run: { color: CHEST } },
      caption:   { run: { font: BODY, color: COFFEE, size: type('标注').size },
                   paragraph: { spacing: { before: 80, after: 200 } } },
      footnoteText: { run: { font: BODY, color: COFFEE, size: type('标注').size } },
    },
  };
}

module.exports = {
  PALETTE, hex, type, docStyles,
  CREAM, SAND, COFFEE, CHEST, DEEP,
  BODY, HEAD, NB, noBorders, allNo, mm,
  body, bullet, h1, h2, caption, cell, mkTable,
};

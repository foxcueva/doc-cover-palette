/* 书脊版封面（docx 路线）· 自研，版权 湫黎，CC BY-NC 4.0
 * 色值来自 ./palette.json（唯一来源），本文件不写任何手写色值。
 * 用法：buildSpineCover({ eyebrow, title1, title2, subtitle, info, pill, footLeft, footRight })
 */
const path = require('path');
const {
  Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, ShadingType, BorderStyle, TableLayoutType,
} = require('docx');
const T = require(path.join(__dirname, 'theme.js'));

const CREAM = T.CREAM, SAND = T.SAND, COFFEE = T.COFFEE, CHEST = T.CHEST, DEEP = T.DEEP;
const SERIF = T.BODY;
const HEAD = T.HEAD;
const NB = { style: BorderStyle.NONE, size: 0, color: CREAM };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNo = { top: NB, bottom: NB, left: NB, right: NB, insideHorizontal: NB, insideVertical: NB };
const mm = T.mm;

/* 版式几何：设计书 GEOM（mm） */
const GEO = {
  spine_w: 8,
  margin_l: 28,
  margin_r: 20,
  margin_t: 35,
  eyebrow_y: 262,
  title_pt: 26,
  subtitle_pt: 12,
  info_pt: 10.5,
};

const line = (n) => new Paragraph({ spacing: { before: n }, children: [new TextRun({ text: '', size: 2 })] });

const blanks = (total) => {
  const out = [];
  let left = total;
  while (left > 0) { const s = Math.min(left, 1800); out.push(line(s)); left -= s; }
  return out;
};

const ruleBar = (hTwip, color) => new Table({
  width: { size: 100, type: WidthType.PERCENTAGE }, layout: TableLayoutType.FIXED, borders: allNo,
  rows: [new TableRow({
    height: { value: hTwip, rule: 'exact' },
    children: [new TableCell({
      shading: { type: ShadingType.CLEAR, fill: color }, borders: noBorders,
      children: [new Paragraph({ spacing: { before: 0, after: 0, line: 20 }, children: [new TextRun({ text: '', size: 2 })] })],
    })],
  })],
});

const pill = (text) => new Table({
  width: { size: 2300, type: WidthType.DXA }, layout: TableLayoutType.FIXED, borders: allNo,
  rows: [new TableRow({
    height: { value: mm(9), rule: 'exact' },
    children: [new TableCell({
      shading: { type: ShadingType.CLEAR, fill: COFFEE }, borders: noBorders, verticalAlign: 'center',
      children: [new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0, line: 240 },
        children: [new TextRun({ text, size: 16, color: DEEP, font: SERIF, characterSpacing: 40 })],
      })],
    })],
  })],
});

function buildSpineCover(cfg) {
  const c = cfg || {};
  const titleSize = T.type('主标题').size;

  const content = [
    ...blanks(Math.round(GEO.margin_t * 56.7)),
    new Paragraph({
      spacing: { after: 1900, line: 260 },
      children: [new TextRun({ text: c.eyebrow || '', size: T.type('辅助').size, color: COFFEE, font: SERIF, characterSpacing: 60 })],
    }),
    new Paragraph({
      spacing: { after: 60, line: 800, lineRule: 'atLeast' },
      children: [new TextRun({ text: c.title1 || '', size: titleSize, color: CHEST, font: HEAD })],
    }),
    new Paragraph({
      spacing: { after: 420, line: 800, lineRule: 'atLeast' },
      children: [new TextRun({ text: c.title2 || '', size: titleSize, color: CHEST, font: HEAD })],
    }),
    new Paragraph({
      spacing: { after: 200, line: 320 },
      children: [new TextRun({ text: c.subtitle || '', size: Math.round(GEO.subtitle_pt * 2), color: DEEP, font: SERIF })],
    }),
    new Paragraph({
      spacing: { after: 700, line: 320 },
      children: [new TextRun({ text: c.info || '', size: Math.round(GEO.info_pt * 2), color: DEEP, font: SERIF })],
    }),
    pill(c.pill || ''),
    ...blanks(5600),
    ruleBar(6, SAND),
    new Paragraph({ spacing: { before: 220 }, children: [new TextRun({ text: '', size: 2 })] }),
    new Paragraph({
      spacing: { after: 0, line: 280 },
      children: [
        new TextRun({ text: c.footLeft || '', size: 16, color: COFFEE, font: SERIF, characterSpacing: 30 }),
        new TextRun({ text: '\t\t\t\t\t\t\t\t\t\t\t' }),
        new TextRun({ text: c.footRight || '', size: 16, color: COFFEE, font: SERIF, characterSpacing: 30 }),
      ],
    }),
  ];

  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE }, layout: TableLayoutType.FIXED, borders: allNo,
    rows: [new TableRow({
      height: { value: 16838, rule: 'exact' },
      children: [
        new TableCell({
          width: { size: mm(GEO.spine_w), type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, fill: DEEP }, borders: noBorders,
          children: [new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: '', size: 2 })] })],
        }),
        new TableCell({
          borders: noBorders, margins: { top: 0, bottom: 0, left: mm(GEO.margin_l - GEO.spine_w), right: mm(GEO.margin_r) },
          children: content,
        }),
      ],
    })],
  })];
}

module.exports = { buildSpineCover, GEO };

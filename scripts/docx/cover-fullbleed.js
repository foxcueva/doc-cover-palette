/* 全幅版封面（docx 路线 · 默认封面）· 自研，版权 湫黎，CC BY-NC 4.0
 * 色值唯一来源：references/palette.json（A 板），本文件不写任何手写色值。
 * 用法：buildFullbleedCover({ eyebrow, title1, title2, subtitle, info, cornerNo })
 * 几何照 palette-spec.md §四（与 PDF 路线 draw_fullbleed_cover 同源）：
 * 满版主栗深底 + 左 8mm 浅驼书脊 + 蜜白字 + 焦糖短条 + 左下三段层级短条 + 右下编号。
 */
const path = require('path');
const {
  Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, ShadingType, BorderStyle, TableLayoutType,
} = require('docx');
const T = require(path.join(__dirname, 'theme.js'));

/* A 板取色（palette.json 唯一来源，禁止手写 hex） */
const MAIN = T.hex('主栗', 'A');      // 满版深底
const SAND = T.hex('浅驼', 'C');      // 浅色书脊条（与 C 板共用该色值）
const HONEY = T.hex('蜜白', 'A');     // 深底反白字
const INK = T.hex('墨栗', 'A');       // 层级短条一
const RUSSET = T.hex('赤栗', 'A');    // 层级短条二
const CARAMEL = T.hex('焦糖', 'A');   // 焦糖短条 / 层级短条三

const SERIF = T.BODY;
const HEAD = T.HEAD;
const NB = { style: BorderStyle.NONE, size: 0, color: MAIN };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNo = { top: NB, bottom: NB, left: NB, right: NB, insideHorizontal: NB, insideVertical: NB };
const mm = T.mm;

/* 版式几何：palette-spec.md §四（mm） */
const GEO = {
  spine_w: 8,
  margin_l: 28,
  margin_r: 20,
  title_pt: 30,
};

const line = (n) => new Paragraph({ spacing: { before: n }, children: [new TextRun({ text: '', size: 2 })] });

const blanks = (total) => {
  const out = [];
  let left = total;
  while (left > 0) { const s = Math.min(left, 1800); out.push(line(s)); left -= s; }
  return out;
};

/* 定宽色条（wMm × hMm）——columnWidths 必须给：不给则 tblGrid 填废值，
 * LibreOffice/WPS 按 tblGrid 平分列宽，条会画错（MS Word 才会自愈）。 */
const bar = (wMm, hMm, color) => new Table({
  width: { size: mm(wMm), type: WidthType.DXA }, columnWidths: [mm(wMm)], layout: TableLayoutType.FIXED, borders: allNo,
  rows: [new TableRow({
    height: { value: mm(hMm), rule: 'exact' },
    children: [new TableCell({
      shading: { type: ShadingType.CLEAR, fill: color }, borders: noBorders,
      children: [new Paragraph({ spacing: { before: 0, after: 0, line: 20 }, children: [new TextRun({ text: '', size: 2 })] })],
    })],
  })],
});

/* 精确下沉：单段 + 行高锁 1pt（多段空段会各自带行高，把后续元素顶出页外） */
const spacer = (twip) => new Paragraph({
  spacing: { before: twip, after: 0, line: 20, lineRule: 'exact' },
  children: [new TextRun({ text: '', size: 2 })],
});

function buildFullbleedCover(cfg) {
  const c = cfg || {};
  const titleSize = GEO.title_pt * 2; // half-points

  const content = [
    spacer(1720),                                             // 天头 35mm（眉头条基线）
    new Paragraph({                                          // 眉头 9pt 蜜白 字距2pt
      spacing: { after: 1550, line: 260 },
      children: [new TextRun({ text: c.eyebrow || '', size: T.type('辅助').size, color: HONEY, font: SERIF, characterSpacing: 60 })],
    }),
    new Paragraph({                                          // 主标题一 30pt 蜜白
      spacing: { after: 60, line: 1000, lineRule: 'atLeast' },
      children: [new TextRun({ text: c.title1 || '', size: titleSize, color: HONEY, font: HEAD, bold: true })],
    }),
    new Paragraph({                                          // 主标题二 30pt 蜜白
      spacing: { after: 700, line: 1000, lineRule: 'atLeast' },
      children: [new TextRun({ text: c.title2 || '', size: titleSize, color: HONEY, font: HEAD, bold: true })],
    }),
    bar(36, 4, CARAMEL),                                     // 焦糖短条 36×4mm
    spacer(560),                                            // 间隔 ~10mm
    new Paragraph({                                          // 副题 12pt 蜜白
      spacing: { after: 480, line: 320 },
      children: [new TextRun({ text: c.subtitle || '', size: Math.round(12 * 2), color: HONEY, font: SERIF })],
    }),
    new Paragraph({                                          // 信息行 10.5pt 蜜白
      spacing: { after: 0, line: 320 },
      children: [new TextRun({ text: c.info || '', size: Math.round(10.5 * 2), color: HONEY, font: SERIF })],
    }),
    spacer(6300),                                           // 下沉到左下角条区
    bar(28, 4, INK),                                         // 层级短条一 墨栗
    spacer(160),
    bar(28, 4, RUSSET),                                      // 层级短条二 赤栗
    spacer(160),
    bar(28, 4, CARAMEL),                                     // 层级短条三 焦糖
    spacer(40),
    new Paragraph({                                          // 右下编号 8pt 蜜白 字距2pt
      alignment: AlignmentType.RIGHT,
      spacing: { before: 0, after: 0, line: 240 },
      children: [new TextRun({ text: c.cornerNo || '', size: 16, color: HONEY, font: SERIF, characterSpacing: 60 })],
    }),
  ];

  return [new Table({
    width: { size: mm(210), type: WidthType.DXA },
    columnWidths: [mm(GEO.spine_w), mm(210 - GEO.spine_w)],
    layout: TableLayoutType.FIXED, borders: allNo,
    rows: [new TableRow({
      height: { value: 16838, rule: 'exact' },
      children: [
        new TableCell({                                      // 浅驼书脊 8mm 通高
          width: { size: mm(GEO.spine_w), type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, fill: SAND }, borders: noBorders,
          children: [new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: '', size: 2 })] })],
        }),
        new TableCell({                                      // 满版主栗深底内容区
          width: { size: mm(210 - GEO.spine_w), type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, fill: MAIN }, borders: noBorders,
          margins: { top: 0, bottom: 0, left: mm(GEO.margin_l - GEO.spine_w), right: mm(GEO.margin_r) },
          children: content,
        }),
      ],
    })],
  })];
}

module.exports = { buildFullbleedCover, GEO };

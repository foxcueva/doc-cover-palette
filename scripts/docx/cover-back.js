/* 封底（docx 路线 · 版式 B' · A 配色 · 装订镜像）· 自研，版权 湫黎，CC BY-NC 4.0
 * 色值唯一来源：references/palette.json，本文件不写任何手写色值。
 * 用法：buildBackCover({ eyebrow, info, cornerNo, barcode })
 *   - barcode：可选 13 位 EAN-13（非数字自动剔除，位数不对抛错；校验位不符 WARN）；不传 = 无码不出码
 * 几何（与 PDF 路线 draw_back 同源，坐标 mm 从页底）：
 *   书脊条右置 8mm（装订镜像）｜眉头 y150｜焦糖短条 y139-143｜信息行 y126｜
 *   层级条组右下 y21-45（墨栗上·焦糖下）｜条码左下 y12-46（衬底 40×34）｜编号 y15（无码）/y50（有码，与码成组）
 * 布局：底区用双列表格（左=条码/编号栈 40mm，右=层级条组靠右），
 *   并排解决流式堆叠出页问题；全部表格 columnWidths 显式给（tblGrid 废值 bug 教训）。
 */
const path = require('path');
const {
  Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, ShadingType, BorderStyle, TableLayoutType, VerticalAlign,
} = require('docx');
const T = require(path.join(__dirname, 'theme.js'));

const MAIN = T.hex('主栗', 'A');
const SAND = T.hex('浅驼', 'C');
const HONEY = T.hex('蜜白', 'A');
const CREAM = T.hex('雾白', 'C');
const INK = T.hex('墨栗', 'A');
const RUSSET = T.hex('赤栗', 'A');
const CARAMEL = T.hex('焦糖', 'A');

const SERIF = T.BODY;
const NB = { style: BorderStyle.NONE, size: 0, color: MAIN };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNo = { top: NB, bottom: NB, left: NB, right: NB, insideHorizontal: NB, insideVertical: NB };
const mm = T.mm;

const GEO = {
  spine_w: 8, margin_l: 28, margin_r: 20,
  eyebrow_pt: 9, info_pt: 10.5, corner_pt: 8,
};

const spacer = (twip) => new Paragraph({
  spacing: { before: twip, after: 0, line: 20, lineRule: 'exact' },
  children: [new TextRun({ text: '', size: 2 })],
});

const bar = (wMm, hMm, color) => new Table({
  width: { size: mm(wMm), type: WidthType.DXA }, columnWidths: [mm(wMm)],
  layout: TableLayoutType.FIXED, borders: allNo,
  rows: [new TableRow({
    height: { value: mm(hMm), rule: 'exact' },
    children: [new TableCell({
      shading: { type: ShadingType.CLEAR, fill: color }, borders: noBorders,
      children: [new Paragraph({ spacing: { before: 0, after: 0, line: 20 }, children: [new TextRun({ text: '', size: 2 })] })],
    })],
  })],
});

/* EAN-13 编码表（行业标准，公有领域） */
const EAN_L = ["0001101","0011001","0010011","0111101","0100011","0110001","0101111","0111011","0110111","0001011"];
const EAN_G = ["0100111","0110011","0011011","0100001","0011101","0111001","0000101","0010001","0001001","0010111"];
const EAN_R = ["1110010","1100110","1101100","1000010","1011100","1001110","1010000","1000100","1001000","1110100"];
const EAN_PARITY = ["LLLLLL","LLGLGG","LLGGLG","LLGGGL","LGLLGG","LGGLLG","LGGGLL","LGLGLG","LGLGGL","LGGLGL"];

function ean13Bits(code) {
  let bits = "101";
  const parity = EAN_PARITY[parseInt(code[0], 10)];
  for (let i = 0; i < 6; i++) {
    const d = parseInt(code[i + 1], 10);
    bits += (parity[i] === "L" ? EAN_L : EAN_G)[d];
  }
  bits += "01010";
  for (let i = 0; i < 6; i++) bits += EAN_R[parseInt(code[7 + i], 10)];
  bits += "101";
  return bits;
}

function ean13ChecksumOk(code) {
  let s = 0;
  for (let i = 0; i < 12; i++) s += parseInt(code[i], 10) * (i % 2 === 0 ? 1 : 3);
  return (10 - s % 10) % 10 === parseInt(code[12], 10);
}

/* 条码：1×95 表格逐列染色（0.264mm/模块 = 25.08mm），雾白衬底 40×34 */
function barcodeBlock(code) {
  const bits = ean13Bits(code);
  const MW = Math.round(0.264 * 56.7);            // ≈15 twip/模块
  const cells = bits.split("").map(b => new TableCell({
    width: { size: MW, type: WidthType.DXA }, borders: noBorders,
    shading: { type: ShadingType.CLEAR, fill: b === "1" ? INK : CREAM },
    children: [new Paragraph({ spacing: { before: 0, after: 0, line: 20 }, children: [new TextRun({ text: '', size: 2 })] })],
  }));
  const stripes = new Table({
    width: { size: MW * 95, type: WidthType.DXA }, columnWidths: Array(95).fill(MW),
    layout: TableLayoutType.FIXED, borders: allNo,
    rows: [new TableRow({
      height: { value: Math.round(18 * 56.7), rule: 'exact' },
      children: cells,
    })],
  });
  const digitRow = new Paragraph({
    spacing: { before: 60, after: 0, line: 240 },
    indent: { left: mm(6.4) },
    children: [new TextRun({ text: code, size: 15, color: INK, font: SERIF, characterSpacing: 30 })],
  });
  return new Table({
    width: { size: mm(40), type: WidthType.DXA }, columnWidths: [mm(40)],
    layout: TableLayoutType.FIXED, borders: allNo,
    rows: [new TableRow({
      height: { value: mm(34), rule: 'exact' },        // 锁 34mm 总高（条 18 + 数字 + 上下静区）
      children: [new TableCell({
        width: { size: mm(40), type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: CREAM }, borders: noBorders,
        children: [spacer(240), stripes, digitRow],
      })],
    })],
  });
}

/* 右下层级条组：墨栗(上)→赤栗→焦糖(下)，右对齐 28mm 宽 */
function hierarchyBars() {
  const mk = (color) => new TableRow({
    height: { value: mm(4), rule: 'exact' },
    children: [new TableCell({
      width: { size: mm(28), type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: color }, borders: noBorders,
      children: [new Paragraph({ spacing: { before: 0, after: 0, line: 20 }, children: [new TextRun({ text: '', size: 2 })] })],
    })],
  });
  const gap = () => new TableRow({
    height: { value: mm(6), rule: 'exact' },
    children: [new TableCell({
      width: { size: mm(28), type: WidthType.DXA }, borders: noBorders,
      children: [new Paragraph({ spacing: { before: 0, after: 0, line: 20 }, children: [new TextRun({ text: '', size: 2 })] })],
    })],
  });
  return new Table({
    alignment: AlignmentType.RIGHT,
    width: { size: mm(28), type: WidthType.DXA }, columnWidths: [mm(28)],
    layout: TableLayoutType.FIXED, borders: allNo,
    rows: [mk(INK), gap(), mk(RUSSET), gap(), mk(CARAMEL)],
  });
}

/* 底区双列表格：左 40mm（编号+条码栈 / 无码=编号沉底），右 122mm（层级条组靠右） */
function bottomZone(bc) {
  const hasCode = !!bc.code;
  const leftChildren = hasCode
    ? [
        new Paragraph({                                // 编号 y≈50（与码成组）
          spacing: { before: 0, after: 0, line: 240 },
          children: [new TextRun({ text: bc.cornerNo || '', size: GEO.corner_pt * 2, color: HONEY, font: SERIF, characterSpacing: 40 })],
        }),
        spacer(170),
        barcodeBlock(bc.code),
      ]
    : [
        new Paragraph({                                // 无码：编号沉到 y≈15
          spacing: { before: 0, after: 0, line: 240 },
          children: [new TextRun({ text: bc.cornerNo || '', size: GEO.corner_pt * 2, color: HONEY, font: SERIF, characterSpacing: 40 })],
        }),
      ];
  return new Table({
    width: { size: mm(162), type: WidthType.DXA },
    columnWidths: [mm(40), mm(122)],
    layout: TableLayoutType.FIXED, borders: allNo,
    rows: [new TableRow({
      height: { value: mm(41), rule: 'exact' },         // 底区行：上沿≈243（码顶 250/编号 243）/ 下沿 284（y13 页底向）
      children: [
        new TableCell({                                 // 左：编号+条码（无码时编号沉底 y≈15）
          width: { size: mm(40), type: WidthType.DXA }, borders: noBorders,
          verticalAlign: hasCode ? VerticalAlign.TOP : VerticalAlign.BOTTOM,
          children: leftChildren,
        }),
        new TableCell({                                 // 右：层级条组（顶对齐 + 前导 8mm，条组落 y21-45）
          width: { size: mm(122), type: WidthType.DXA }, borders: noBorders,
          verticalAlign: VerticalAlign.TOP,
          children: [spacer(450), hierarchyBars()],
        }),
      ],
    })],
  });
}

function buildBackCover(cfg) {
  const c = cfg || {};
  let barcode = null;
  if (c.barcode) {
    const clean = String(c.barcode).replace(/\D/g, '');
    if (clean.length !== 13) throw new Error('barcode 需 13 位数字（EAN-13）');
    if (!ean13ChecksumOk(clean)) console.error('WARN  条码校验位不匹配，扫枪可能拒读——请核验码值。');
    barcode = clean;
  }

  const content = [
    spacer(8200),                                        // 天头 → 眉头基线 y≈150mm
    new Paragraph({                                      // 眉头 9pt 蜜白 字距2.2pt
      spacing: { after: 0, line: 260 },
      children: [new TextRun({ text: c.eyebrow || '', size: GEO.eyebrow_pt * 2, color: HONEY, font: SERIF, characterSpacing: 44 })],
    }),
    spacer(265),                                        // 焦糖短条上距
    bar(36, 4, CARAMEL),                                // 焦糖短条 y≈139-143
    spacer(650),                                        // 信息行上距
    new Paragraph({                                      // 信息/年份行 10.5pt 蜜白 字距1.2pt
      spacing: { after: 0, line: 320 },
      children: [new TextRun({ text: c.info || '', size: Math.round(GEO.info_pt * 2), color: HONEY, font: SERIF, characterSpacing: 24 })],
    }),
    spacer(3850),                                        // 下沉至底区行（上沿≈243，两版统一）
    bottomZone({ code: barcode, cornerNo: c.cornerNo }),
  ];

  return [new Table({
    width: { size: mm(210), type: WidthType.DXA },
    columnWidths: [mm(210 - GEO.spine_w), mm(GEO.spine_w)],   // 内容列在左，书脊条在右（装订镜像）
    layout: TableLayoutType.FIXED, borders: allNo,
    rows: [new TableRow({
      height: { value: 16838, rule: 'exact' },
      children: [
        new TableCell({                                  // 满版主栗深底内容区
          width: { size: mm(210 - GEO.spine_w), type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, fill: MAIN }, borders: noBorders,
          margins: { top: 0, bottom: 0, left: mm(GEO.margin_l - GEO.spine_w), right: mm(20) },
          children: content,
        }),
        new TableCell({                                  // 浅驼书脊 8mm 右置
          width: { size: mm(GEO.spine_w), type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, fill: SAND }, borders: noBorders,
          children: [new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: '', size: 2 })] })],
        }),
      ],
    })],
  })];
}

module.exports = { buildBackCover, GEO };

/* 演示报告 · D 路线（docx 可编辑）· 色值全部来自 references/palette.json
 * 用法：node example_report.js [输出.docx]
 * 注：本文数据为演示占位（非真实账单），用于展示封面/目录/正文/表格全套版式。
 */
const { Document, Packer, Paragraph, TextRun, SectionType, Footer, PageNumber, TableOfContents, NumberFormat } = require('docx');
const fs = require('fs');
const path = require('path');
const T = require(path.join(__dirname, 'theme.js'));
const { buildFullbleedCover } = require(path.join(__dirname, 'cover-fullbleed.js'));
const { buildBackCover } = require(path.join(__dirname, 'cover-back.js'));
// 浅色封面改用：require('./cover-spine.js') 的 buildSpineCover（字段 pill/footLeft/footRight）
// 封底默认不出（≥8 页或正式文档时建议加）；条码仅用户提供真实 EAN-13 才传 barcode 字段

const daily = [
  ['10-12', 0.90], ['10-13', 0.60], ['10-14', 0.65], ['10-15', 1.50],
  ['10-16', 1.70], ['10-17', 0.45], ['10-18', 0.60], ['10-19', 0.70],
  ['10-20', 0.65], ['10-21', 1.80], ['10-22', 2.20], ['10-23', 1.10],
  ['10-24', 1.45], ['10-25', 0.45], ['10-26', 0.80], ['10-27', 5.60],
  ['10-28', 4.90], ['10-29', 3.80], ['10-30', 2.80], ['10-31', 0.40],
  ['11-01', 0.60], ['11-02', 4.60], ['11-03', 4.05], ['11-04', 7.00],
  ['11-05', 1.40], ['11-06', 1.50], ['11-07', 0.65], ['11-08', 0.55],
  ['11-09', 4.80], ['11-10', 0.35],
].map(([d, c]) => [d, c.toFixed(2)]);

const structure = [
  ['输入，未命中缓存', '18,700,000', '25.80', '44.0%'],
  ['输入，命中缓存', '758,800,000', '21.00', '35.8%'],
  ['输出', '2,130,000', '11.60', '19.8%'],
  ['工具调用与请求计数', '8,050', '0.27', '0.5%'],
  ['合计', '779,600,000', '58.65', '100%'],
];

const gap = () => new Paragraph({ spacing: { after: 140, line: 300 }, children: [new TextRun({ text: '', size: 16 })] });

const body = [
  T.h1('一、总体情况'),
  T.body('演示数据：统计区间共 30 天，总花费 58.65 元，平均每天约 1.95 元。其中模型调用占绝对大头，工具调用占比极小。'),
  T.body('正文段落演示：两级标题、正文、列表、表格与页脚页码的完整层级。实际使用时替换为报告内容即可，版式会自动保持一致。'),
  T.bullet('30 天合计发起约 8,000 次请求'),
  T.bullet('合计约 7.8 亿 token，折算 0.075 元每百万 token'),
  T.bullet('仅调用一款模型，占全部费用的 99.5%'),
  T.bullet('单次请求平均 0.007 元'),

  T.h1('二、每日费用分布'),
  T.body('下表为每日扣费明细（演示数据，四舍五入到分）。多数日子在 0.5 元到 2 元之间，中位数约 1.4 元。'),
  T.caption('表 1　每日 API 费用（元）'),
  T.mkTable(['日期', '金额'], daily, [40, 30], [0, 1]),
  gap(),
  T.body('超过 3.5 元的有 7 天（10-27 至 11-09 之间的若干峰值日），峰值约 7.0 元，通常出现在改配置、排查问题、开长会话的日子。'),

  T.h1('三、成本结构'),
  T.body('按计费类型拆开看，钱的去向比较集中。'),
  T.caption('表 2　按调用类型的成本分布'),
  T.mkTable(['类型', 'token 量', '金额（元）', '占比'], structure, [32, 26, 22, 20], [1, 2, 3]),
  gap(),
  T.body('缓存命中 97.6%。命中的 7.59 亿 token 只花 21.0 元，未命中的 0.19 亿 token 花 25.8 元——两者单价差约 50 倍，体积小得多的未命中部分反而是最大开支。'),

  T.h1('四、结论'),
  T.bullet('花费不高，30 天不到 60 元，没有异常的日子。'),
  T.bullet('钱主要花在没命中缓存的输入和输出上，不在 token 总量。'),
  T.bullet('想再省，先减少新开会话的次数，其次控制回复长度。'),

  T.h1('五、改进措施'),
  T.body('减少新开会话：缓存按前缀匹配，很多次短会话各自把注入文件读一遍，是未命中偏高的主因。'),
  T.body('把稳定内容放前面：系统规则、工具说明放前面，时间戳和临时状态放后面，开头一变整段缓存失效。'),
  T.caption('表 3　下一个周期的目标'),
  T.mkTable(
    ['指标', '当前值', '目标值'],
    [
      ['30 天总费用', '58.65 元', '不超过 45 元'],
      ['日均费用', '1.95 元', '不超过 1.50 元'],
      ['未命中输入占比', '44.0%', '不超过 30%'],
      ['单日峰值', '7.00 元', '不超过 5.00 元'],
    ],
    [44, 28, 28], [1, 2]
  ),
  gap(),
  T.body('监控方式：日报里加一行未命中占比，超过 50% 报警；单日超过 5 元，当天排查长会话与重复任务。'),
  new Paragraph({
    spacing: { before: 480, line: 320 }, alignment: 'right',
    children: [new TextRun({ text: '—— 湫黎', font: T.BODY, size: T.type('辅助').size, color: T.COFFEE })],
  }),
];

const pageNumFooter = () => new Footer({
  children: [new Paragraph({
    alignment: 'center',
    children: [new TextRun({ children: [PageNumber.CURRENT], font: T.BODY, size: 16, color: T.COFFEE })],
  })],
});

const pgSize = { width: 11906, height: 16838 };
const pgMargin = { top: T.mm(28), bottom: T.mm(22), left: T.mm(28), right: T.mm(20) };

const doc = new Document({
  background: { color: T.CREAM },
  styles: T.docStyles(),
  sections: [
    { properties: { page: { size: pgSize, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
      children: buildFullbleedCover({
        eyebrow: 'API USAGE SUMMARY',
        title1: 'API 消费小结',
        title2: '2026 年 10 月—11 月',
        subtitle: '30 天账单复盘 · 费用与用量（演示数据）',
        info: '统计区间 2026-10-12 — 2026-11-10',
        cornerNo: 'SUMMARY · NO.01',
      }) },
    { properties: { type: SectionType.NEXT_PAGE, page: { size: pgSize, margin: pgMargin, pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } } },
      footers: { default: pageNumFooter() },
      children: [
        new Paragraph({ spacing: { before: 600, after: 520 }, children: [new TextRun({ text: '目　录', bold: true, size: T.type('章节标题').size, font: T.HEAD, color: T.CHEST })] }),
        new TableOfContents('Table of Contents', { hyperlink: true, headingStyleRange: '1-3' }),
        new Paragraph({ spacing: { before: 240 }, children: [new TextRun({ text: '注：目录由域代码生成，页码若显示不准，右键目录选“更新域”即可。', italics: true, size: 16, color: T.COFFEE, font: T.BODY })] }),
      ] },
    { properties: { type: SectionType.NEXT_PAGE, page: { size: pgSize, margin: pgMargin, pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } },
      footers: { default: pageNumFooter() }, children: body },
    { properties: { type: SectionType.NEXT_PAGE, page: { size: pgSize, margin: { top: 0, bottom: 0, left: 0, right: 0, footer: 0, header: 0 } } },
      footers: { default: new Footer({ children: [] }) },   // 封底必须覆盖空页脚（footer 距离也归零）：整页表格遇页脚占位会裂成两页
      children: buildBackCover({                          // 封底（演示用法；实际使用按 SKILL 规则在 ≥8 页或正式文档时建议）
        eyebrow: 'API CONSUMPTION · QUARTERLY',
        info: '2026 · SUMMARY',
        cornerNo: 'SUMMARY · NO.01',
      }) },
  ],
});

const out = process.argv[2] || path.join(process.cwd(), 'API消费小结_D路线示例.docx');
Packer.toBuffer(doc).then((b) => { fs.mkdirSync(require('path').dirname(out), { recursive: true }); fs.writeFileSync(out, b); console.log('WROTE ' + out + ' ' + b.length); });

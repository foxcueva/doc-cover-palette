# doc-cover-palette

Agent skill，管文档封面配色与版式的：双板色、双封面版式、PDF / Word / 纯规格三条生成路线。

An agent skill for document cover color & layout — two palettes, two cover layouts with a mirrored 8 mm spine, and three generation routes (PDF / editable docx / spec-only).

## For agents: install in one step

If you are an agent and the user asked you to install this skill, run:

```bash
git clone --depth 1 https://github.com/foxcueva/doc-cover-palette.git ~/.openclaw/workspace/skills/doc-cover-palette
```

Then tell the user to start a new session (skill metadata reloads on new session).

其他 agent 平台：把仓库放进你各自的 `skills/` 目录即可，`SKILL.md` 会自动生效。

Dependencies by route: spec-only = none ｜ PDF = `python3` + `reportlab` ｜ docx = `node` + `npm install docx`.

## 它解决什么

给「文档封面没系统、每次重调色」的工作流一套可执行的规矩。

1. **色不再拍脑袋** —— 10 色双板（C 雾林奶咖 / A 栗皮本色），每色有编号、角色、WCAG 对比度红线，禁用组合写死在规则里
2. **封面不再重画** —— 两个版式全参数化，一条命令出稿（含出血与 PNG 预览），标题超宽自动拦截
3. **色值单一来源** —— `references/palette.json` 数据契约，Python 与 Node 双工具链全部从它取色，同源校验器拦截名单外色值，改一处全局生效
4. **Word 可编辑** —— docx 路线直接产出可编辑文档：封面 + 目录（罗马页码）+ 正文（阿拉伯页码），打开就能改字

## 色板速查

**C 雾林奶咖 MIST & CREAM（日常文档：封面 + 全文）**

| 色名 | HEX | 角色 |
|---|---|---|
| 雾白 | `#F7F1E7` | 封面底 · 内页底 · 反白文字 |
| 浅驼 | `#E3D0BA` | 分隔线 · 表格隔行 · 全幅版书脊条 |
| 奶咖 | `#B08968` | 标签 · 页眉页脚（禁作正文） |
| 栗棕 | `#6B4028` | 大标题 · 章节标题 |
| 深栗 | `#492D22` | 正文 · 书脊版书脊条 · 锚点色 |

**A 栗皮本色 CHESTNUT PELAGE（正式封面深底）**

| 色名 | HEX | 角色 |
|---|---|---|
| 墨栗 | `#331E14` | 页脚细线 · 表头 |
| 主栗 | `#492D22` | 封面主底 · 锚点色 |
| 赤栗 | `#7C4324` | 章节色块 · 图表第二色 |
| 焦糖 | `#B26B3F` | 强调点缀（≤10% 面积） |
| 蜜白 | `#EAD9C0` | 深底反白字 |

## 版式（默认深色封面，8mm 书脊互为镜像）

**需要封面时默认出全幅版（深色）**；用户点名浅色才切书脊版。出封面时告知用户可切换——别让人翻脚本找选项。

**封底默认不出**；文档 ≥8 页或要打印装订时，agent 主动建议加。封底书脊条**右置**（装订镜像：双面打印装订后与封面书脊条同贴装订缝）。**条码仅当用户提供真实 EAN-13 码值才生成**——agent 不建议、不预填、不出演示码；无码不出码，无码零占位。

| 版式 | 底面 | 书脊条 | 何时用 | 命令 |
|---|---|---|---|---|
| 全幅封面 | 主栗深底 | 浅驼 `#E3D0BA` 左置 | **默认** | `gen_cover.py`（不传 --layout） |
| 书脊封面 | 雾白浅底 | 深栗 `#492D22` 左置 | 用户点名浅色 | `gen_cover.py --layout spine` |
| 封底 | 主栗深底 | 浅驼 `#E3D0BA` **右置** | ≥8 页/正式文档（agent 建议，用户点头） | `gen_cover.py --layout back`（条码加 `--barcode "EAN13"`） |

正文内页默认**纸白**（不铺色 · 印刷零墨 · 屏幕最锐利）；用户点名护眼/柔和才切雾白 `#F7F1E7`。A 只上封面/封底。

版本历史见 [CHANGELOG.md](CHANGELOG.md)。Agent 使用前必读 [AGENT_RULES.md](AGENT_RULES.md)（六条强制规则）与 [BODY_SPEC.md](BODY_SPEC.md)（正文精确配方）。

## 快速验证

```bash
# PDF 封面（默认深色全幅版；--bleed 3 加出血，--png 150 渲染预览图）
python3 scripts/gen_cover.py \
  --title1 "标题" --title2 "第二行" --subtitle "副题" --info "日期" --out t.pdf --png 150

# 封底（装订镜像；条码仅用户给真实 EAN-13 才加 --barcode）
python3 scripts/gen_cover.py --layout back --eyebrow "DOC SERIES" \
  --info "2026 · SUMMARY" --corner-no "NO.01" --out back.pdf --png 150

# Word 文档（封面+目录+正文+封底全套示例）
cd scripts/docx && npm install docx && node example_report.js demo.docx
```

## 目录

```
doc-cover-palette/
├── SKILL.md                      # 触发词、选型路由、六条铁律、三条路线
├── README.md                     # 当前你正在看的
├── LICENSE.txt                   # 中文许可要点与依赖声明
├── references/
│   ├── palette.json              # 色彩数据契约（色值唯一来源）
│   └── palette-spec.md           # 全量规格：CMYK/字号级数/逐元素坐标/印刷参数
├── assets/
│   ├── 配色版式设计书_V2.3_无版权.pdf
│   └── 配色版式设计书_V2.3.1_带版权.pdf
└── scripts/
    ├── gen_palette_book.py       # 设计书生成器（参数化母版）
    ├── gen_cover.py              # 三版式 CLI：封面×2+封底（出血/预览/宽度自检/EAN-13 条码）
    └── docx/                     # Word 路线：theme.js / cover-fullbleed.js（默认深色封面）/ cover-spine.js（浅色）/ cover-back.js（封底·装订镜像）/ 同源校验 / 页码补丁
```

## License

CC BY-NC 4.0（详见 [LICENSE](LICENSE) 与 [LICENSE.txt](LICENSE.txt)）：署名 **湫黎**，非商用自由使用；商用需版权人书面授权（开 GitHub Issue 联系）。

Dependencies: reportlab (BSD) · docx (MIT) · Noto Serif SC (SIL OFL 1.1, fonts not distributed in-repo).

---
name: doc-cover-palette
description: '文档封面配色与版式系统「雾林奶咖 × 栗皮本色」（湫黎设计）。当用户需要：文档封面设计、给报告/文档做封面、封面配色、Word 文档主题色、报告排版配色、文档样式规范、按既有配色出封面、查色号或搭配、海报/卡片用这套棕色系时使用。封面默认规则：需要封面时一律先出全幅版（A 栗皮本色深底 + 8mm 浅驼书脊，正式有分量），并主动告知用户可改浅色书脊版（C 雾白浅底 + 8mm 深栗书脊）——不让用户读脚本猜。封底默认规则：封底默认不出；文档 ≥8 页或正式文档（打印装订）时主动建议加封底（装订镜像：书脊条右置）；条码仅当用户提供真实 EAN-13 码值才生成，agent 不建议不预填不出演示码。正文底规则：内页默认纸白（不铺色、印刷零墨、屏幕最锐利），用户点名护眼/柔和才切雾白。PDF 定稿用 gen_cover.py 一键生成（默认深色，--layout spine 切浅色，--layout back 出封底，支持出血与 PNG 预览），可编辑 Word 文档用 scripts/docx 路线（Node docx, MIT），全部色值单一来源 references/palette.json。提供完整色值（HEX/RGB/CMYK）、WCAG 对比度约束、字号级数、三套版面几何（封面×2+封底）与可运行生成脚本。Use when the user needs document cover design, a brown/cream palette system, document theme colors, or typography specs; cover defaults to dark full-bleed (mirrored 8mm sand spine), switchable to light spine cover on request — always tell the user; back cover off by default but suggested for formal docs / docs ≥8 pages (binding-mirrored, spine bar right); barcode only with user-provided real EAN-13, never suggested; body pages default to paper white (no fill, zero print ink), cream only when the user asks for eye-care; PDF via gen_cover.py (dark by default), editable docx via scripts/docx; single color source palette.json.'
license: CC BY-NC 4.0 (author: 湫黎)
metadata:
  author: 湫黎
  version: "2.3.0"
  tags:
    - 配色
    - 封面设计
    - 版式
    - 文档主题
---

# 文档封面配色系统 · 雾林奶咖 × 栗皮本色

一套双板色系统：**C 雾林奶咖**（主用 · 日常文档全文）＋ **A 栗皮本色**（备用 · 正式文档封面/扉页深底），共用锚点色 **#492D22**。设计语言：栗子壳的暖棕 × 奶咖的浅雾白，克制、温润、印刷友好。

## 色值速查（核心数据，直接引用）

**C 雾林奶咖 MIST & CREAM（日常文档：封面 + 全文）**

| 色名 | HEX | RGB | 角色 |
| --- | --- | --- | --- |
| 雾白 | #F7F1E7 | 247 241 231 | 封面底 · 内页底 · 反白文字 |
| 浅驼 | #E3D0BA | 227 208 186 | 分隔线 · 表格隔行 · 底纹 |
| 奶咖 | #B08968 | 176 137 104 | 标签 · 图表主色 · 页眉页脚 |
| 栗棕 | #6B4028 | 107 64 40 | 大标题 · 章节标题 |
| 深栗 | #492D22 | 73 45 34 | 正文 · 书脊 · 表头 · 锚点色 |

**A 栗皮本色 CHESTNUT PELAGE（正式文档：封面/扉页深底）**

| 色名 | HEX | RGB | 角色 |
| --- | --- | --- | --- |
| 墨栗 | #331E14 | 51 30 20 | 页脚细线 · 表头（深底内页） |
| 主栗 | #492D22 | 73 45 34 | 封面主底 · 扉页底 · 锚点色 |
| 赤栗 | #7C4324 | 124 67 36 | 章节色块 · 图表第二色 |
| 焦糖 | #B26B3F | 178 107 63 | 强调点缀 · 高亮（≤10% 面积） |
| 蜜白 | #EAD9C0 | 234 217 192 | 深底标题与正文（反白） |

分工口诀：**A 管封面/封底深底，C 管浅色封面与装饰**——正式文档 = A 封面 + 纸白内页；**内页底默认纸白（不铺色 · 印刷零墨 · 屏幕最锐利），用户点名护眼/柔和才切雾白 #F7F1E7**（TA 2026-11-10 实测拍板：深栗字压雾白偏费眼）；通篇深底不做（墨量、可读性、印刷成本三输）。

## 封面封底选型路由（默认深色封面，封底默认不出）

**规则（照做，别让用户读脚本猜）：**

1. **封面默认**：文档需要封面（如有或用户要求）→ 出**全幅版**（版式 B · A 栗皮本色深底 + 8mm 浅驼书脊条），`gen_cover.py` 不传 `--layout` 即是它；docx 路线用 `cover-fullbleed.js` 的 `buildFullbleedCover`。
2. **封面切换**：用户点名「浅色 / 日常 / 轻一点 / 白底」→ 出**书脊版**（版式 A · C 雾白浅底 + 8mm 深栗书脊条），`gen_cover.py --layout spine`；docx 路线用 `cover-spine.js` 的 `buildSpineCover`。
3. **封面告知义务（每次出封面都要做）**：交付封面时附一句——「封面默认用了深色全幅版；想换浅色书脊版，说一声就行。」
4. **封底默认不出**；但**文档 ≥8 页或正式文档（要打印装订）时，主动建议加封底**——「这份文档建议配封底（打印装订更完整），要吗？」用户点头才加。版式 B'（A 深底 + 8mm 浅驼书脊条**右置**——装订镜像，与封面书脊条同贴装订缝）：`gen_cover.py --layout back`；docx 路线用 `cover-back.js` 的 `buildBackCover`。
5. **条码铁律**：封底条码**仅当用户提供真实 EAN-13 码值**（ISBN/EAN）才生成（`--barcode` / `barcode` 字段），位数不对报错、校验位不符 WARN；**agent 永不主动建议加条码、永不预填、永不出演示码**——个人文档用户没有码是常态，主动提是打扰。无码不出码，无码零占位（无衬底块残留）。

| 版式 | 配色与底面 | 何时用 | 一键生成 |
| --- | --- | --- | --- |
| 版式 B · 全幅封面（默认） | A 栗皮本色：满版深栗 #492D22 深底 + 左侧 8mm 浅驼书脊条，蜜白反白字 + 焦糖短条 | 需要封面时的默认 | `gen_cover.py`（不传 --layout） |
| 版式 A · 书脊封面（切换） | C 雾林奶咖：雾白浅底 + 左侧 8mm 深栗书脊条，深字 | 用户点名浅色时 | `gen_cover.py --layout spine` |
| 版式 B' · 封底（建议项） | A 深底 + 右侧 8mm 浅驼书脊条（装订镜像），层级条组右下，编号/条码左下 | ≥8 页或正式文档，agent 建议后用户点头 | `gen_cover.py --layout back`（条码加 `--barcode "EAN13"`） |

- 封面两版是**不同版式，不是同一版式换色**：书脊版 26pt 标题 + 胶囊标签 + 页脚行；全幅版 30pt 标题 + 焦糖短条 + 左下三段层级短条 + 右下编号。几何、字号、专属元素不可混用。
- 封面/封底/内页共同锚点——**8mm 书脊条**：封面浅驼 #E3D0BA 压主栗底（左侧），封底浅驼右置（装订镜像，双面装订后两条同贴装订缝）；书脊版封面则深栗压雾白（左侧）。同宽同色语言，位置按装订物理定。
- 正文内页无论配哪版封面，**默认纸白**（docx 不设 background 即白页；reportlab 不铺底）——印刷零墨、屏幕阅读最锐利；用户点名「护眼 / 柔和 / 暖一点」时切雾白 #F7F1E7（docx `background: { color: T.CREAM }`）。雾白底的深栗字依然 AAA（11.1:1），只是长时间屏幕阅读比纸白费眼——默认别用。

## 六条铁律（改任何东西前先过一遍）

1. **正文只用深栗 #492D22（浅底）或蜜白 #EAD9C0（深底）**。奶咖对雾白实测 2.8:1，不达正文标准，只能作标签、页脚与图形色——不是审美判断，是 WCAG 实算结论。
2. **焦糖 #B26B3F 只作点缀**，面积 ≤10%；大面积永远留给雾白与深栗两极，这是系统的呼吸感来源。
3. **浅驼 #E3D0BA 是唯一的底纹色**（表格隔行、分隔块），深栗字压浅驼实测 8.3:1，可放心作正文。
4. **#492D22 是双板锚点**：C 的正文色 = A 的封面主底。任何一板改锚点色，两板必须同步改。
5. **别加第六色**。需要图表第三色时用同色阶加深/提亮（如 #5C3A2B、#C9A87F），保持栗色系家族感。
6. **留白即设计**：雾白区域不小于版面的 40%，不要用底纹把页面填满。

## WCAG 对比度实测（引用时直接报数）

| 前景/背景 | 比值 | 判定 | 可用作 |
| --- | --- | --- | --- |
| 深栗 on 雾白 | 11.1:1 | AAA | 正文（日常内页） |
| 栗棕 on 雾白 | 7.8:1 | AAA | 各级标题 |
| 深栗 on 浅驼 | 8.3:1 | AAA | 底纹上的文字 |
| 蜜白 on 主栗 | 9.0:1 | AAA | 深底标题与正文 |
| 蜜白 on 赤栗 | 5.7:1 | AA | 赤栗色块上的标题 |
| 焦糖 on 主栗 | 3.0:1 | AA大字 | 仅限点缀条与图形（≥18pt） |
| 深栗 on 奶咖 | 3.9:1 | AA大字 | 胶囊标签文字（辅助信息） |
| 奶咖 on 雾白 | 2.8:1 | 不达标 | 禁作文字，仅图形/标签底 |

## 执行路由（按环境三选一）

**路线 S —— 环境可运行 Python（推荐产出成品 PDF 时）**
脚本在本 skill 的 `scripts/` 目录：
```bash
pip install reportlab                            # 唯一依赖，BSD 许可
# 默认深色封面（全幅版 · A 配色）——需要封面时默认走这条
python3 scripts/gen_cover.py \
    --eyebrow "EN EYEBROW" --title1 "文档主标题" --title2 "副题或年月" \
    --subtitle "一句话说明" --info "日期或编号信息" \
    --corner-no "NO.01" --out 封面_全幅版.pdf
# 浅色封面（书脊版 · C 配色）——用户点名浅色时才用
python3 scripts/gen_cover.py --layout spine \
    --eyebrow "EN EYEBROW" --title1 "文档主标题" --title2 "副题或年月" \
    --subtitle "一句话说明" --info "日期或编号信息" \
    --pill "标签文字" --foot "FOOT · 2026" --out 封面_书脊版.pdf
# 封底（版式 B' · 装订镜像）——≥8 页或正式文档时建议加
python3 scripts/gen_cover.py --layout back \
    --eyebrow "DOC SERIES" --info "2026 · SUMMARY" \
    --corner-no "NO.01" --out 封底.pdf
# 封底带条码——仅用户提供真实 EAN-13 时（无码不出码，无码零占位）
python3 scripts/gen_cover.py --layout back --barcode "978-XXXXXXXXXXX" --out 封底_带码.pdf
python3 scripts/gen_palette_book.py --out 输出目录   # 出整本设计规格书（7页双版本）
```
- 文字全部走命令行参数（`--eyebrow/--title1/--title2/--subtitle/--info/--pill/--foot/--corner-no`），不传用默认占位文字；版式几何锁死在母版函数里，不要改；
- 送印加 `--bleed 3`：全幅版四边出血（216×303），书脊版色条侧出血（213×297），与印刷注意事项一致；
- `--png 150` 顺手渲同目录 PNG 供目检（需 pdftoppm，缺了自动跳过）；
- 生成前自动跑文字宽度自检（版心限宽 162mm），超宽打 WARN——见 WARN 先改文案再出稿；
- 需要换字体时：环境变量 `NOTO_SERIF_SC_DIR` 指向 Noto Serif SC 目录，或 `--font-dir` 参数；脚本自带五级字体探测（候选路径 → fc-match → 报错带安装指引）；
- 脚本当前绑定 Noto Serif SC（SIL OFL，可商用可嵌入）。换其他字体前查该字体的商用/嵌入许可。

**路线 D —— 环境可运行 Node（出可编辑 Word/docx 文档）**
脚本在本 skill 的 `scripts/docx/` 目录（Node ≥18；npm 包 docx，MIT）：
```bash
cd scripts/docx && npm install docx      # 首次
node example_report.js 我的文档.docx     # 先跑示例：封面+目录+正文+封底全套（正文纸白默认）
# 自建文档：写 build.js，require('./theme.js') 拿色号/字号/构造器，
# 封面默认深色：require('./cover-fullbleed.js') 用 buildFullbleedCover（eyebrow/title1/title2/subtitle/info/cornerNo）
# 用户点名浅色：require('./cover-spine.js') 用 buildSpineCover（另支持 pill/footLeft/footRight）
# 封底（≥8 页或正式文档建议加）：require('./cover-back.js') 用 buildBackCover
#   （eyebrow/info/cornerNo；barcode 字段仅用户给真实 EAN-13 才传）
# 封底节必须覆盖空页脚且页脚距归零：
#   footers: { default: new Footer({ children: [] }) }
#   page: { size, margin: { top:0, bottom:0, left:0, right:0, footer:0, header:0 } }
#   ——整页封面表遇到页脚占位（哪怕空段落）会裂成两页
bash docx_build.sh /abs/path/build.js   # 构建入口（构建前自动跑色值同源校验）
python3 docx_footer_fix.py 我的文档.docx # 收尾：WPS 页码域兼容补丁
```
- **色值唯一来源 `references/palette.json`**：theme.js / cover-fullbleed.js / cover-spine.js / 业务脚本一律 `T.hex('色名', '板键')` 取色（A 板色传第二参 `'A'`），禁止手写色值；`docx_palette_check.js` 扫描名单外色值直接报错退出（构建入口已内置）；
- docx 存色**不带 #**（写 `492D22` 不是 `#492D22`），只用 RGB；CMYK/印刷参数属 PDF 路线，docx 表达不了；
- docx **只引用字体名不嵌字体**：theme.js 默认 SimSun/SimHei（全平台必有，打开即正确）；要与 PDF 路线完全同观感，把 eastAsia 换成 `Noto Serif SC`，目标机需装该字体（OFL 1.1）；
- 标准三节结构：封面（默认全幅版：零边距表格拼版 + 8mm 浅驼书脊条压主栗深底）→ 目录（罗马页码，域代码 TOC，打开后右键「更新域」）→ 正文（阿拉伯页码）；
- 样式一律走 `T.docStyles()`（内置样式全量压成色板色，Office 默认蓝已归零），表格用 `T.mkTable()`。

**路线 R —— 环境无 Python / 需要其他格式（SVG / HTML / Word 指引）**
读 `references/palette-spec.md`：完整版式几何（两套封面全部坐标、字号级数、Word 样式映射、印刷参数）。规格是格式无关的，照参数手写 SVG/HTML 同样成立。给 Word 用户的交付：把「Word 样式映射」表直接给出去，照表几分钟搭出同款主题。

**路线 Q —— 用户只要色值/搭配咨询**
本页色值速查表 + 六条铁律就是答案，不需要读任何文件。搭配建议按「分工口诀」+ 对比度表给。

## 交付前质量门（每次都要过）

- 文字溢出/叠压/截断：渲染成图目检，或至少按最长文本串算过宽度（`gen_cover.py` 已内置 162mm 限宽自检，WARN 必须处理后再出稿）；
- 单位换算坑：版式几何表以 mm 计，字号以 pt 计——**mm×2.83 才是 pt**，混用必叠压（历史事故：字号误乘 2.83 导致标题行塌陷）；
- 中文折行：数字与单位不可拆（「262mm」是原子），闭合标点禁落行首（「）」掉行首是硬伤）；
- 对比度红线：见上表，奶咖永不作正文字色。

## 深入数据（按需读取，不进常驻上下文）

- `references/palette.json` —— **色彩数据契约**：所有工具链（reportlab / Node docx / 未来的 SVG/HTML）的色值单一来源，改色只改这一处
- `references/palette-spec.md` —— CMYK 值、字号级数全表、书脊版/全幅版封面逐元素坐标、Word 映射表、印刷注意事项、换字体 FAQ
- `assets/配色版式设计书_V2.3_无版权.pdf` / `assets/配色版式设计书_V2.3.1_带版权.pdf` —— 完整设计书（7 页，双版本），用户要看成品效果或复核细节时给这份
- `scripts/gen_cover.py` —— 三版式生成器（默认 fullbleed 全幅封面深底，`--layout spine` 浅底封面，`--layout back` 封底装订镜像；`--barcode` EAN-13 可选条码，无码不出码；CLI 参数化，`--bleed` 出血、`--png` 预览、内置宽度自检）
- `scripts/gen_palette_book.py` —— 参数化生成器（色板/字号/几何都是顶部常量，改完重跑；design book 与 palette.json 均由此导出）
- `scripts/docx/` —— docx 可编辑路线（theme.js 构造器 / cover-fullbleed.js 深色封面（默认）/ cover-spine.js 浅色封面 / cover-back.js 封底（装订镜像，可选条码）/ example_report.js 全套示例（封面+目录+正文+封底）/ docx_palette_check.js 同源校验 / docx_footer_fix.py 页码补丁）

## 授权与边界

- 本 skill 内容与脚本：**CC BY-NC 4.0**，署名「湫黎」，非商用自由使用/修改/分发，商用需版权人书面授权（版权人自用不受限）。
- 色号本身不受著作权保护——许可约束的是本包的文案、规格表达与脚本代码。
- 依赖（全部宽松许可，可商用）：**reportlab（BSD）**、**npm docx（MIT）**；字体 Noto Serif SC（SIL OFL 1.1，可商用可嵌入），字体文件不随包分发。
- `scripts/docx/node_modules/` 不随包分发；终端用户自行 `npm install docx`（MIT）。
- 示例 `example_report.js` 中数据为演示占位，非真实账单。
- 禁止把本 skill 代码与 Z.AI 专有 skill（docx/pdf/pptx/charts 等，仅限非商用）混同分发。

## 变更记录

- **2.3.0（2026-11-10）**：正文底策略反转——**默认纸白**（docx 不设 background / reportlab 不铺底；印刷零墨、屏幕最锐利），雾白 #F7F1E7 降为护眼选项（用户点名才切；TA + 朋友盲测拍板：深栗字压雾白长时间阅读偏费眼）；设计书升 V2.3/V2.3.1 并补封底版式 B' 条目与纸白规则；示例文档正文页转纸白；新增 CHANGELOG.md（版本历史入库）。
- **2.2.0（2026-11-10）**：新增封底版式 B'（A 深底 + 8mm 浅驼书脊条**右置**——装订镜像，双面装订后与封面书脊条同贴装订缝；层级条组右下、编号/条码左下）；封底默认不出，文档 ≥8 页或正式文档时 agent 主动建议（TA 拍板）；EAN-13 条码自绘（80% 放大、雾白衬底、墨栗条，机读回验通过），仅用户提供真实码值才生成、agent 永不建议；docx 路线 `cover-back.js`（底区双列表格并排：条码/编号栈 + 层级条组，全部 columnWidths 显式）。
- **2.1.0（2026-11-10）**：封面默认规则改为深色全幅版——需要封面时一律先出全幅版，用户点名浅色才切书脊版，且每次出封面必须告知用户可切换（TA 拍板）；docx 路线新增 `cover-fullbleed.js`（buildFullbleedCover，此前 docx 只有浅色封面）；`gen_cover.py` 不传 `--layout` 默认出深色全幅版。
- **2.0.0（2026-11-10）**：全幅版封面新增左侧 8mm 浅驼 #E3D0BA 书脊条（与书脊版深栗条同位同宽、色彩互为镜像，TA 定稿）；新增路线 D（docx 可编辑文档，Node docx MIT）；新增 `references/palette.json` 色彩数据契约（双工具链色值单一来源，机器导出+回读校验）；docx 内置样式全量压色（Office 默认蓝归零，产物 XML 色值 100% 白名单）；示例数据脱敏；设计书升 V2/V2.1。
- **1.1.0**：gen_cover.py 统一封面生成器（双版式 CLI、--bleed 出血、--png 预览、162mm 限宽自检）。
- **1.0.0**：初始版本（双板色板、设计书、gen_palette_book.py）。

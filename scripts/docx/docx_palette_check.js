#!/usr/bin/env node
/* 同源校验：扫描指定 JS 文件里的十六进制色值，必须全部来自 palette.json。
 * 用法：docx_palette_check.js <file.js> [more.js ...]
 * 退出码 1 = 发现名单外色值（漂移）。
 * 自研脚本（纯 Node 标准库）· 版权 湫黎 · CC BY-NC 4.0（版权人自用不受限）
 * 未使用任何 Z.AI skill 代码；依赖链无第三方商用限制。
 */
const fs = require('fs');
const path = require('path');

const PALETTE_PATH = path.join(__dirname, '..', '..', 'references', 'palette.json');
const P = JSON.parse(fs.readFileSync(PALETTE_PATH, 'utf8'));

const allowed = new Set();
for (const key of Object.keys(P.palettes)) {
  for (const c of P.palettes[key].colors) allowed.add(c.hex.replace('#', '').toUpperCase());
}
for (const t of P.type_scale) allowed.add(t.color.replace('#', '').toUpperCase());
allowed.add(P.anchor.replace('#', '').toUpperCase());

const files = process.argv.slice(2);
if (!files.length) {
  console.error('用法: docx_palette_check.js <file.js> [more.js ...]');
  process.exit(2);
}

let bad = 0;
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8');
  // 匹配 'FFAA00' / "ffaa00" / 8 位带 alpha 的写法取前 6 位
  const re = /['"]([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})?['"]/g;
  let m;
  const seen = new Set();
  while ((m = re.exec(src)) !== null) {
    const h = m[1].toUpperCase();
    if (seen.has(h)) continue;
    seen.add(h);
    if (!allowed.has(h)) {
      console.log('❌ ' + path.basename(f) + ' 出现名单外色值: ' + h);
      bad++;
    }
  }
  console.log((bad ? '· ' : '✅ ') + path.basename(f) + ' 检查完毕，色值 ' + seen.size + ' 个');
}

if (bad) {
  console.log('\n共 ' + bad + ' 处色值不在 palette.json 内 → 校验失败');
  process.exit(1);
}
console.log('\n全部色值与 palette.json 同源 ✅');

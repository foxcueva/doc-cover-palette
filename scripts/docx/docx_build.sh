#!/bin/bash
# docx 路线构建入口：构建前自动跑同源校验（色值必须全部来自 references/palette.json）
# 用法: docx_build.sh <build.js> [输出.docx]
# 依赖: node ≥ 18；npm 包 docx（MIT）。首次使用：npm install docx
# 自研脚本（bash + node）· 版权 湫黎 · CC BY-NC 4.0（版权人自用不受限）
# 未使用任何 Z.AI skill 代码；依赖链无第三方商用限制。
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL_ROOT="$(cd "$HERE/../.." && pwd)"

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "usage: docx_build.sh <abs-path-to-build.js> [输出.docx]" >&2
  exit 2
fi
BUILD_JS="$1"; shift || true
if [ ! -f "$BUILD_JS" ]; then
  echo "refuse: build 脚本不存在: $BUILD_JS" >&2
  exit 2
fi

# 构建前同源校验：目标脚本 + 主题库 + 封面库，三者色值全部受 palette.json 约束
node "$HERE/docx_palette_check.js" "$BUILD_JS" "$HERE/theme.js" "$HERE/cover-spine.js" \
  || { echo "palette 校验失败，终止构建" >&2; exit 3; }

# NODE_PATH 兼容：docx 装在全局或 .pylibs 风格目录时也能找到
export NODE_PATH="${NODE_PATH:+$NODE_PATH:}$HERE/node_modules:$(npm root -g 2>/dev/null || true)"

exec node "$BUILD_JS" "$@"

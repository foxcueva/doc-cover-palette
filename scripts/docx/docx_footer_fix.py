#!/usr/bin/env python3
"""Patch docx footers for WPS compatibility: add PAGE format switches, drop empty pgNumType.

Usage: docx_footer_fix.py <file.docx> [--roman-first N]
Roman footers are the first N footer parts in document order (default 1).

自研脚本（纯 Python 标准库）· 版权 湫黎 · CC BY-NC 4.0（版权人自用不受限）
未使用任何 Z.AI skill 代码；依赖链无第三方商用限制。
"""
import sys, re, shutil, zipfile, os

path = sys.argv[1]
roman_count = 1
if "--roman-first" in sys.argv:
    roman_count = int(sys.argv[sys.argv.index("--roman-first") + 1])

tmp = path + ".tmpfix"
with zipfile.ZipFile(path) as zin:
    names = zin.namelist()
    footers = sorted([n for n in names if re.match(r"word/footer\d+\.xml$", n)],
                     key=lambda n: int(re.search(r"(\d+)", n).group(1)))
    data = {n: zin.read(n) for n in names}

for idx, name in enumerate(footers):
    xml = data[name].decode("utf-8")
    fmt = "ROMAN" if idx < roman_count else "arabic"
    xml2 = re.sub(r"(<w:instrText[^>]*>)\s*PAGE\s*(</w:instrText>)",
                  lambda m: '%s PAGE \\* %s \\* MERGEFORMAT %s' % (m.group(1), fmt, m.group(2)),
                  xml)
    data[name] = xml2.encode("utf-8")
    print("patched %s -> %s" % (name, fmt))

doc = data["word/document.xml"].decode("utf-8")
n_pg = doc.count("<w:pgNumType/>")
doc = doc.replace("<w:pgNumType/>", "")
data["word/document.xml"] = doc.encode("utf-8")
print("removed empty pgNumType: %d" % n_pg)

with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for n in names:
        zout.writestr(n, data[n])
shutil.move(tmp, path)
print("done: %s (%d bytes)" % (path, os.path.getsize(path)))

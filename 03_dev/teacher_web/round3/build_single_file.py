#!/usr/bin/env python3
"""build_single_file.py
把 src/index.html + 所有引用的 components/ vendor/ assets/ _assets/
全部 inline 成一个 self-contained HTML。
产出：round3/Tomoshibi_v3_single.html（demo 携带用，双击即跑）
"""
import re, base64, mimetypes
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
SRC  = ROOT / 'src'
OUT  = ROOT / 'Tomoshibi_v3_single.html'

html = (SRC / 'index.html').read_text(encoding='utf-8')

# Step 1: 把 components/ vendor/ 的 jsx / js 文件内联（如果还是 src= 形式）
def inline_script(m):
    rel = m.group(1) if m.group(1) else m.group(2)
    p = SRC / rel
    if not p.exists():
        print(f'  !! missing {rel}'); return m.group(0)
    body = p.read_text(encoding='utf-8')
    type_attr = f' type="text/babel"' if rel.endswith('.jsx') else ''
    return f'<script{type_attr} data-source="{rel}">\n{body}\n</script>'

# text/babel src=
html = re.sub(r'<script type="text/babel" src="(components/[^"]+)"></script>', inline_script, html)
# vendor js src=
html = re.sub(r'<script src="(vendor/[^"]+)"></script>', inline_script, html)

# Step 2: 把 woff2 字体 / PNG 图标用 data: URL 替换
def data_uri(path):
    p = SRC / path
    if not p.exists():
        return None
    mime = mimetypes.guess_type(str(p))[0]
    if not mime:
        if p.suffix == '.woff2': mime = 'font/woff2'
        elif p.suffix == '.png': mime = 'image/png'
        else: mime = 'application/octet-stream'
    b64 = base64.b64encode(p.read_bytes()).decode('ascii')
    return f'data:{mime};base64,{b64}'

# 替换 CSS 里的 url("_assets/xxx.woff2")
def replace_css_url(m):
    path = m.group(1)
    uri = data_uri(path)
    if uri is None: return m.group(0)
    return f'url("{uri}")'

html = re.sub(r'url\("(_assets/[^"]+\.woff2)"\)', replace_css_url, html)
html = re.sub(r"url\('(_assets/[^']+\.woff2)'\)", replace_css_url, html)

# 替换 window.__resources (tomoshibi-icon.png 等)
icon_uri = data_uri('assets/tomoshibi-icon.png')
if icon_uri:
    html = re.sub(
        r'window\.__resources\s*=\s*\{[^}]*\};',
        f'window.__resources = {{ tomoshibiIcon: "{icon_uri}" }};',
        html,
    )

OUT.write_text(html, encoding='utf-8')
size_mb = OUT.stat().st_size / 1024 / 1024
print(f'✅ 生成 {OUT.name} · {size_mb:.1f} MB')
print(f'   双击即可跑，U 盘拷这 1 个文件就行')

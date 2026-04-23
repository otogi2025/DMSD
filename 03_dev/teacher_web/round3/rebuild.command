#!/bin/bash
# 双击这个 → 把 src/components/*.jsx 全部重新内联到 src/index.html
# 这样 src/index.html 可以直接双击打开（file:// 也能跑，不用 server）
#
# 什么时候跑：改完 src/components/ 里任何 .jsx 后，双击这个重生成

cd "$(dirname "$0")"

python3 <<'PY'
import re
from pathlib import Path

root = Path('.').resolve()
idx_path = root / 'src' / 'index.html'

html = idx_path.read_text(encoding='utf-8')

# Step 1: 先把之前内联过的 <script data-source=...>...</script> 还原成 src= 形式
html = re.sub(
    r'<script type="text/babel" data-source="(components/[^"]+)">\n.*?\n</script>',
    r'<script type="text/babel" src="\1"></script>',
    html,
    flags=re.DOTALL,
)

# Step 2: 再把 src= 的都读取最新内容内联
def inline(m):
    rel = m.group(1)
    jsx_path = root / 'src' / rel
    if not jsx_path.exists():
        return m.group(0)
    body = jsx_path.read_text(encoding='utf-8')
    return f'<script type="text/babel" data-source="{rel}">\n{body}\n</script>'

new_html = re.sub(r'<script type="text/babel" src="(components/[^"]+)"></script>', inline, html)
idx_path.write_text(new_html, encoding='utf-8')

n = len(re.findall(r'data-source="components/', new_html))
print(f"✅ {n} 个 jsx 重新内联到 src/index.html · {idx_path.stat().st_size // 1024} KB")
print()
print("ブラウザで src/index.html をリロード（Cmd+R）")
PY

echo ""
echo "按回车关闭窗口..."
read

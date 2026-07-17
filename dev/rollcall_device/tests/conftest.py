"""pytest 公共设置 —— 把 rollcall_device 根目录放上 sys.path，好 `import src.xxx`。"""

import sys
from pathlib import Path

# tests/ 的上一级 = rollcall_device/，含 src 包
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

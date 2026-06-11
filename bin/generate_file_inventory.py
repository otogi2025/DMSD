#!/usr/bin/env python3
"""
文件清单自动生成 — 机器管「有哪些文件」，人只管「这文件干嘛」。

itsuki 2026-06-11 拍板（TODO §B「联动单一真值改造」落地第一步）：
- 文件名 / 行数 / 增删 这类机器能查的，跑 `git ls-files` 永远是真的，不再手写（手写必漂移）
- 「这文件干嘛用」只有人知道，存 00_admin/文件批注.tsv（路径<TAB>一句话说明）
- 本脚本把两者拼成 00_admin/文件清单_自动生成.md，并列出「新文件还没批注」「批注的文件已不存在」

收尾流程用法（session-wrap 核对表第 7 项）：
  1. python3 bin/generate_file_inventory.py        ← 先跑，刷新清单
  2. 看输出里的「未批注」新文件 → CC 读文件补一句批注进 文件批注.tsv → 再跑一遍
"""

import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANNOT = ROOT / "00_admin" / "文件批注.tsv"
OUT = ROOT / "00_admin" / "文件清单_自动生成.md"


def git_files():
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return [line for line in out.splitlines() if line.strip()]


def load_annotations():
    annots = {}
    if ANNOT.exists():
        for line in ANNOT.read_text().splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t", 1)
            if len(parts) == 2:
                annots[parts[0].strip()] = parts[1].strip()
    return annots


def count_lines(path: Path):
    """文本文件数行数；二进制（图片 / db / 字体等）返回 None"""
    try:
        data = path.read_bytes()
        if b"\x00" in data[:8192]:
            return None
        return data.count(b"\n")
    except Exception:
        return None


def main():
    files = git_files()
    annots = load_annotations()

    by_dir = defaultdict(list)
    for f in files:
        top = f.split("/")[0] if "/" in f else "（根目录）"
        by_dir[top].append(f)

    unannotated = [f for f in files if f not in annots]
    stale = [p for p in annots if p not in set(files)]

    lines = [
        "# 文件清单（自动生成 — 勿手改）",
        "",
        "> 生成器：`bin/generate_file_inventory.py`（git ls-files + `00_admin/文件批注.tsv` 合成）。",
        f"> 共 **{len(files)}** 个已提交文件；已批注 {len(files) - len(unannotated)} / 未批注 {len(unannotated)}。",
        "> 改批注 → 编辑 `文件批注.tsv` 后重跑生成器；本文件手改必被覆盖。",
        "",
    ]

    for top in sorted(by_dir, key=lambda d: (-len(by_dir[d]), d)):
        group = sorted(by_dir[top])
        lines.append(f"## {top}（{len(group)} 文件）")
        lines.append("")
        lines.append("| 文件 | 行数 | 干嘛用 |")
        lines.append("|---|---|---|")
        for f in group:
            n = count_lines(ROOT / f)
            n_s = str(n) if n is not None else "二进制"
            note = annots.get(f, "⬜")
            lines.append(f"| `{f}` | {n_s} | {note} |")
        lines.append("")

    OUT.write_text("\n".join(lines))

    print(f"✅ 已生成 {OUT.relative_to(ROOT)}（{len(files)} 文件）")
    print(f"   已批注 {len(files) - len(unannotated)} / 未批注 {len(unannotated)}")
    if unannotated:
        print("   ⬜ 未批注（前 15 个，收尾时 CC 补）:")
        for f in unannotated[:15]:
            print(f"      {f}")
        if len(unannotated) > 15:
            print(f"      … 还有 {len(unannotated) - 15} 个")
    if stale:
        print(f"   🗑 批注里有 {len(stale)} 条对应的文件已不存在（可从 tsv 删掉）:")
        for p in stale[:10]:
            print(f"      {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

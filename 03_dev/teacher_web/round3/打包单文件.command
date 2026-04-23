#!/bin/bash
# 双击这个 → 从 src/ 打包成 Tomoshibi_v3_single.html（单文件，demo 携带用）
# 用途：demo 当天 U 盘拷这一个文件走，双击就能跑
# 执行前确保：已经跑过 rebuild.command（把最新的 jsx 内联到 src/index.html）

cd "$(dirname "$0")"
python3 build_single_file.py

echo ""
echo "按回车关闭窗口..."
read

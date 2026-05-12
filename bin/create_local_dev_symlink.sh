#!/usr/bin/env zsh
set -euo pipefail

# ─────────────────────────────────────────────────────────────
# 本脚本用途（2026-04-20 加注释，对应 backlog T8）
# ─────────────────────────────────────────────────────────────
# 作用：在 $HOME/dev/DMSD 创建指向本 repo 的软链接（symlink），
# 让 Xcode / VS Code 能用短路径打开项目。
#
# 适用场景：**只在 VPS 上需要跑**
#   - VPS 的 repo 通常 clone 到 $HOME/DMSD （路径短，但和 Mac 本地不一致）
#   - 本脚本会建 $HOME/dev/DMSD -> $HOME/DMSD  的软链接
#   - 好处：Mac 本地和 VPS 上"DMSD 项目"都能用 ~/dev/DMSD 路径访问
#
# 不适用场景：**Mac 本地 repo（已经在 ~/dev/DMSD）不需要跑**
#   - Mac 上 clone 后本身就在 ~/dev/DMSD，跑这个会让软链接指向自己
#   - 下面有自动检测会在这种情况报错退出
#
# 运行：
#   zsh 00_admin/create_local_dev_symlink.sh
# ─────────────────────────────────────────────────────────────

SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="$HOME/dev"
LINK_PATH="$TARGET_DIR/DMSD"

# 自检：如果当前 SRC_DIR 已经等于目标 LINK_PATH 的实体路径
# (= Mac 本地 repo 已经在 ~/dev/DMSD)，跑这个脚本没意义，甚至会
# 建"指向自己"的循环软链接。直接报错退出。
if [ "$SRC_DIR" = "$LINK_PATH" ]; then
    echo "⚠️  当前 repo 已经在 $LINK_PATH"
    echo "    不需要创建软链接（软链接指向自己是循环）"
    echo "    本脚本主要为 VPS 场景设计（VPS 的 repo 在 ~/DMSD，需要链接到 ~/dev/DMSD）"
    exit 0
fi

# 如果 LINK_PATH 已存在但不是软链接（是真实目录），避免覆盖
if [ -e "$LINK_PATH" ] && [ ! -L "$LINK_PATH" ]; then
    echo "❌ $LINK_PATH 已存在但不是软链接（是真实目录）"
    echo "   拒绝覆盖。请手动检查："
    echo "     ls -la $LINK_PATH"
    exit 1
fi

mkdir -p "$TARGET_DIR"
ln -sfn "$SRC_DIR" "$LINK_PATH"

echo "✅ 软链接已创建/更新："
echo "   $LINK_PATH -> $SRC_DIR"
echo "   （Xcode / VS Code 可以从 $LINK_PATH 打开项目）"

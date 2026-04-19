#!/usr/bin/env bash
# DMSD hooks 一次性安装脚本
#
# 在每个 clone 了本 repo 的机器上跑一次（Mac 和 VPS 各跑一次）。
#
# 作用：
#   1. git config core.hooksPath 00_admin/hooks  —— 让 git 去 00_admin/hooks 找 hook（可 track）
#   2. chmod +x 让 hook 脚本可执行
#
# 为什么 hook 不放在 .git/hooks/？
#   .git/hooks/ 不被 git 追踪，每台机器都要重放。
#   把 hook 放在 00_admin/hooks/ 可以随代码一起同步，一次 install 到处生效。

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

# 1. 设置 git 去 00_admin/hooks 找 hooks
git config core.hooksPath 00_admin/hooks

# 2. 确保 hook 可执行
chmod +x 00_admin/hooks/pre-commit

echo ""
echo "✅ DMSD hooks 已安装"
echo "   core.hooksPath = $(git config --get core.hooksPath)"
echo ""
echo "测试："
echo "   随便改一行文字 → 试 git commit → 含过期版本号会被拦下"
echo ""
echo "卸载："
echo "   git config --unset core.hooksPath"
echo ""

#!/usr/bin/env bash
# DMSD 文件联动 - 中途随时查工具
#
# 是什么：
#   CC（或 itsuki 自己）在会话中途改完一组文件后，随时跑一下，
#   查"我改了 X，但联动文件 Y / Z 还没改"。
#   不用等到 commit 时 pre-commit hook 提醒。
#
# 为什么需要：
#   CLAUDE.md §会话结束 §3 文件关联追踪表只在「会话结束」执行 1 次。
#   中途改了 5 个文件 → 收尾翻 5 次表 → 漏的概率上升。
#   本脚本 = 把 §3 表「随时可查」化。
#
# 用法：
#   bash bin/sync-check.sh             # 检查全部 working tree（modified + staged + untracked）
#   bash bin/sync-check.sh --staged    # 只检查 git add 过的（模拟 pre-commit 行为）
#   bash bin/sync-check.sh <file1> <file2>  # 检查指定文件
#
# 输出：
#   每条触发的规则一段中文 warning + 缺失文件列表 + 原因
#   exit 0 始终（仅提示，不阻断）
#
# 2026-05-04 itsuki 拍板新建（A+B 方案 — pre-commit 加内容检查 + 本脚本中途查）

# 不开 set -u / set -e — 函数 return 非 0 是「触发条数」非错误，与 set -e 不兼容

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [ -z "$REPO_ROOT" ]; then
    echo "❌ 不在 git 仓库内" >&2
    exit 1
fi

cd "$REPO_ROOT"

LIB="$REPO_ROOT/00_admin/hooks/lib/sync-rules.sh"
if [ ! -f "$LIB" ]; then
    echo "❌ 找不到规则库: $LIB" >&2
    exit 1
fi

# shellcheck source=../00_admin/hooks/lib/sync-rules.sh
source "$LIB"

# ============================================================
# 参数解析
# ============================================================

MODE="all"        # all = working tree 全部 / staged = 只 staged
EXPLICIT_FILES=()

if [ $# -ge 1 ]; then
    case "$1" in
        --staged)
            MODE="staged"
            ;;
        --help|-h)
            sed -n '2,30p' "$0"
            exit 0
            ;;
        *)
            EXPLICIT_FILES=("$@")
            MODE="explicit"
            ;;
    esac
fi

# ============================================================
# 收集要检查的文件列表
# ============================================================

CHANGED_FILES=""
NEW_FILES=""

if [ "$MODE" = "explicit" ]; then
    CHANGED_FILES=$(printf '%s\n' "${EXPLICIT_FILES[@]}")
elif [ "$MODE" = "staged" ]; then
    CHANGED_FILES=$(git -c core.quotepath=false diff --cached --name-only)
    NEW_FILES=$(git -c core.quotepath=false diff --cached --name-status | awk '$1 == "A" {print $2}')
else
    # all: working tree（modified + added + untracked）
    PORCELAIN=$(git -c core.quotepath=false status --porcelain)
    # 取 status 行的文件名部分（处理 M / A / ?? / R 等标记）
    CHANGED_FILES=$(echo "$PORCELAIN" | sed -E 's/^...(.+)$/\1/' | awk -F' -> ' '{print $NF}')
    NEW_FILES=$(detect_new_files "$PORCELAIN")
fi

# ============================================================
# 跑检查
# ============================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  DMSD 文件联动检查（mode: ${MODE}）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -z "$CHANGED_FILES" ]; then
    echo ""
    echo "  ✅ 当前没有改动文件 — 没什么可查"
    echo ""
    exit 0
fi

CHANGED_COUNT=$(echo "$CHANGED_FILES" | grep -c . || true)
echo ""
echo "  改动文件数: $CHANGED_COUNT"
echo "  改动文件列表:"
echo "$CHANGED_FILES" | sed 's/^/    /'

# 跑联动规则
# 2026-05-22 修 FC-033：临时把 IFS 设成换行符（让 shell 按行拆参数，
# 不按空格拆），保护带空格的路径
SC_OLD_IFS=$IFS
IFS=$'\n'
SYNC_OUTPUT=$(check_sync_for_files $CHANGED_FILES 2>&1)
IFS=$SC_OLD_IFS

# 跑新建声明性文件检查
DECL_OUTPUT=""
if [ -n "$NEW_FILES" ]; then
    DECL_OUTPUT=$(check_new_declarative_files "$NEW_FILES" 2>&1)
fi

if [ -z "$SYNC_OUTPUT" ] && [ -z "$DECL_OUTPUT" ]; then
    echo ""
    echo "  ✅ 全部联动规则通过 — 没有漏改"
    echo ""
    exit 0
fi

echo ""
echo "─────────────────────────────────────────────"
echo "  ⚠️  以下规则触发（仅提示，不阻断）"
echo "─────────────────────────────────────────────"

if [ -n "$SYNC_OUTPUT" ]; then
    echo "$SYNC_OUTPUT"
fi

if [ -n "$DECL_OUTPUT" ]; then
    echo "$DECL_OUTPUT"
fi

echo ""
echo "─────────────────────────────────────────────"
echo "  规则源: 00_admin/hooks/lib/sync-rules.sh"
echo "  规则表（人类可读）: CLAUDE.md §会话结束 §3 文件关联追踪"
echo "─────────────────────────────────────────────"
echo ""

exit 0

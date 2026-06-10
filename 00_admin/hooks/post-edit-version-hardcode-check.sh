#!/usr/bin/env bash
# DMSD CC PostToolUse hook — 版本号硬编码实时拦
#
# 配置位置：.claude/settings.json hooks.PostToolUse[matcher="Write|Edit"]
# 触发时机：CC 改了声明性文件
#
# 工作流：
# 1. 读 stdin 提取 file_path
# 2. 判断是否在「禁硬编码版本号」白名单（同 git pre-commit 规则）
# 3. 提取新增内容（git diff HEAD ^+ 行 / untracked 全文）
# 4. grep `vX.Y.Z` 模式的行，但行末没 `<!-- VERSION_OK -->` 豁免
# 5. 命中 → 提醒
#
# 跟 git pre-commit 关系：
# - pre-commit 是 commit 时拦（block）
# - 本 hook 是 Write/Edit 时拦（warn）— 早一步发现
# - 单源真值：CHANGELOG.md 顶部
# - 其他声明性文件用「当前版本见 CHANGELOG.md 顶部」指针
#
# 受检文件（同 pre-commit）：
# - CLAUDE.md
# - 00_admin/WIP.md
# - 00_admin/TODO.md
#
# 2026-05-04 itsuki 拍板新建（5 hook 一波加）

set -e
trap 'exit 0' ERR

INPUT=$(cat 2>/dev/null || echo "{}")

if [ -z "$INPUT" ] || [ "$INPUT" = "{}" ]; then
  exit 0
fi

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/Users/kurekoduki/dev/DMSD}"
RELATIVE_PATH="${FILE_PATH#$PROJECT_DIR/}"

if [[ "$RELATIVE_PATH" == /* ]]; then
  exit 0
fi

# ============================================================
# 受检声明性文件白名单（同 pre-commit）
# ============================================================

case "$RELATIVE_PATH" in
  "CLAUDE.md"|"00_admin/WIP.md"|"00_admin/TODO.md")
    : # 受检
    ;;
  *)
    exit 0  # 不在白名单
    ;;
esac

if [ ! -f "$PROJECT_DIR/$RELATIVE_PATH" ]; then
  exit 0
fi

cd "$PROJECT_DIR" 2>/dev/null || exit 0

# ============================================================
# 提取新增内容
# ============================================================

NEW_CONTENT=""
if git ls-files --error-unmatch -- "$RELATIVE_PATH" &>/dev/null; then
  # tracked — git diff
  NEW_CONTENT=$(git diff HEAD -- "$RELATIVE_PATH" 2>/dev/null \
    | grep '^+' | grep -v '^+++' \
    | sed 's/^+//' || true)
else
  # untracked — 整文件
  NEW_CONTENT=$(cat "$RELATIVE_PATH" 2>/dev/null || true)
fi

if [ -z "$NEW_CONTENT" ]; then
  exit 0
fi

# ============================================================
# 找硬编码版本号 — 行内 vX.Y.Z 模式 + 行末没 VERSION_OK 豁免
# ============================================================

# Pattern: 行内含 vX.Y.Z（X/Y/Z 都是数字），且行末没 VERSION_OK 注释
VIOLATIONS=$(echo "$NEW_CONTENT" \
  | grep -nE '\bv[0-9]+\.[0-9]+\.[0-9]+\b' \
  | grep -v 'VERSION_OK' \
  | head -5 || true)

if [ -z "$VIOLATIONS" ]; then
  exit 0
fi

# ============================================================
# 输出
# ============================================================

ADDITIONAL_CONTEXT="🔢 版本号硬编码实时拦（${RELATIVE_PATH}）

⚠️ 检测到新增内容里有硬编码版本号 \`vX.Y.Z\`（行末没 \`<!-- VERSION_OK -->\` 豁免）。

违反行（前几条）：
$(echo "$VIOLATIONS" | sed 's/^/     /')

📜 单源真值规则：
- 版本号 single source = \`CHANGELOG.md\` 顶部
- 声明性文件（CLAUDE.md / WIP / TODO）只用指针：\"当前版本见 CHANGELOG.md 顶部\"
- 例外（极少）：历史引用（\"v0.2.0 时决定...\"）→ 行末加 \`<!-- VERSION_OK -->\` 豁免

→ 修复 2 选 1：
   A. 改成指针：\`当前版本见 CHANGELOG.md 顶部\`
   B. 历史引用：保留版本号 + 行末加 \`<!-- VERSION_OK -->\`

⚠️ 比 git pre-commit 早一步拦 — 不修的话 commit 时 pre-commit 会再阻塞一次。"

jq -n --arg ctx "$ADDITIONAL_CONTEXT" \
  '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'

exit 0

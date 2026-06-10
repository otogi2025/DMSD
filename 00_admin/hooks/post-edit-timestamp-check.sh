#!/usr/bin/env bash
# DMSD CC PostToolUse hook — 声明性文件「最后更新」时间戳检查
#
# 配置位置：.claude/settings.json hooks.PostToolUse[matcher="Write|Edit"]
# 触发时机：CC 改了 WIP / TODO / 文档同步点清单 等声明性文件
#
# 工作流：
# 1. 读 stdin 提取 file_path
# 2. 判断是否在声明性文件白名单（只对这些文件 strict 检查）
# 3. 读文件头部 30 行找「最后更新: YYYY-MM-DD」字段
# 4. 解析日期 → 跟今天对比
# 5. 不一致 → 提醒「时间戳没更新」
#
# 受检文件：
# - 00_admin/WIP.md
# - 00_admin/TODO.md
# - 00_admin/文档同步点清单.md
# - CHANGELOG.md（顶部 ## [vX.Y.Z] - YYYY-MM-DD 也算时间戳）
#
# CLAUDE.md 不查 — 因为没有「最后更新」字段，靠 git log 看
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
# 受检文件白名单
# ============================================================

WATCHED=""
case "$RELATIVE_PATH" in
  "00_admin/WIP.md"|"00_admin/TODO.md"|"00_admin/文档同步点清单.md"|"CHANGELOG.md")
    WATCHED="$RELATIVE_PATH"
    ;;
  *)
    exit 0  # 不在白名单 — skip
    ;;
esac

if [ ! -f "$PROJECT_DIR/$RELATIVE_PATH" ]; then
  exit 0
fi

# ============================================================
# 提取「最后更新」时间戳
# ============================================================

TODAY=$(date +%Y-%m-%d)

# 头部 30 行内找 YYYY-MM-DD 模式（最后更新 / [vX.Y.Z] - YYYY-MM-DD 都符合）
HEAD_30=$(head -30 "$PROJECT_DIR/$RELATIVE_PATH" 2>/dev/null)

# 提取所有 YYYY-MM-DD 形式的日期（取最近一次出现）
LAST_DATE=$(echo "$HEAD_30" | grep -oE '\b20[0-9]{2}-[0-9]{2}-[0-9]{2}\b' | head -1)

if [ -z "$LAST_DATE" ]; then
  # 头部没找到日期 — 文件可能没有时间戳字段，提醒添加
  ADDITIONAL_CONTEXT="📅 时间戳检查（${RELATIVE_PATH}）

⚠️ 头部 30 行没找到「最后更新: YYYY-MM-DD」字段。

声明性文件应该有时间戳让协作者快速判断新鲜度。建议头部加一行：

\`> **最后更新**: ${TODAY}（这次会话改动: <一句话>）\`"

  jq -n --arg ctx "$ADDITIONAL_CONTEXT" \
    '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'
  exit 0
fi

# ============================================================
# 跟今天对比
# ============================================================

if [ "$LAST_DATE" = "$TODAY" ]; then
  exit 0  # 时间戳已是今天 — 通过
fi

# 时间戳过时 — 提醒
ADDITIONAL_CONTEXT="📅 时间戳过时（${RELATIVE_PATH}）

文件头部「最后更新」时间戳：${LAST_DATE}
今天日期：${TODAY}

⚠️ 改动了文件但时间戳没同步更新 → 协作者看时间戳会以为这文件没动过。

→ 修复：改文件头部「最后更新」字段为 ${TODAY}（顺手加一句话本次改动概要）

例：\`> **最后更新**: ${TODAY}（修订: <这次改了什么>）\`

⚠️ false positive：如果文件本来就用历史日期作引用（如 \"v0.6.0 close 2026-04-30\"），那行不该改。看上下文判断。"

jq -n --arg ctx "$ADDITIONAL_CONTEXT" \
  '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'

exit 0

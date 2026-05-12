#!/usr/bin/env bash
# DMSD CC PostToolUse hook — Write/Edit 命中 memory 目录时提醒更新 MEMORY.md 索引
#
# 配置位置：.claude/settings.json hooks.PostToolUse[matcher="Write|Edit"]
# 触发时机：CC 调 Write/Edit 完成后（跟 post-edit-sync-check.sh 并列跑）
#
# 工作流：
# 1. 读 stdin PostToolUse JSON
# 2. 提取 tool_input.file_path
# 3. 判断是否在 memory 目录（/Users/kurekoduki/.claude/projects/-Users-itsuki-dev-DMSD/memory/）
# 4. 排除 MEMORY.md 自己（避免改索引时又触发提醒）
# 5. 检查 MEMORY.md 是否包含新文件名 → 没有就提醒
# 6. 注入 hookSpecificOutput.additionalContext
#
# 设计原则：
# - 只在 memory dir 触发，其他目录 silent exit
# - 不阻塞（warn-only）
# - 避免对 MEMORY.md 自己触发（infinite loop 风险）
#
# 2026-05-04 itsuki 拍板新建（连同 memory-write skill 一起）

set -e
trap 'exit 0' ERR

INPUT=$(cat 2>/dev/null || echo "{}")

if [ -z "$INPUT" ] || [ "$INPUT" = "{}" ]; then
  exit 0
fi

# 提取 file_path
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# memory 目录路径
MEMORY_DIR="/Users/kurekoduki/.claude/projects/-Users-kurekoduki-dev-DMSD/memory"
MEMORY_INDEX="${MEMORY_DIR}/MEMORY.md"

# 是否在 memory 目录
if [[ "$FILE_PATH" != "${MEMORY_DIR}/"* ]]; then
  exit 0
fi

# 提取文件名
FILENAME=$(basename "$FILE_PATH")

# 排除 MEMORY.md 自己（改索引文件不需要再提醒）
if [ "$FILENAME" = "MEMORY.md" ]; then
  exit 0
fi

# 排除非 .md 文件
if [[ "$FILENAME" != *.md ]]; then
  exit 0
fi

# ============================================================
# 检查：MEMORY.md 是否引用了新文件
# ============================================================

WARNINGS=""

if [ -f "$MEMORY_INDEX" ]; then
  if ! grep -q "$FILENAME" "$MEMORY_INDEX" 2>/dev/null; then
    WARNINGS="📝 memory-write 提醒：

刚改 / 新建：${FILENAME}

⚠️ MEMORY.md 索引里**没找到**对此文件的引用 — 必须加一行索引否则未来 CC 永远找不到这条 memory：

\`- [一句话标题](${FILENAME}) — 一句话钩子说明这条 memory 干嘛的（≤150 字符）\`

→ 详细写法见 memory-write skill (.claude/skills/memory-write/SKILL.md §5)"
  fi
fi

# 检查 frontmatter 完整性（如果新建/改的文件本地存在）
if [ -f "$FILE_PATH" ]; then
  HEAD_3=$(head -3 "$FILE_PATH" 2>/dev/null || echo "")
  if ! echo "$HEAD_3" | head -1 | grep -q "^---"; then
    if [ -n "$WARNINGS" ]; then WARNINGS="${WARNINGS}

"; fi
    WARNINGS="${WARNINGS}⚠️ ${FILENAME} 顶部没看到 frontmatter（应该以 \`---\` 开头）。

memory 文件必须有 frontmatter：
\`\`\`
---
name: {名字}
description: {一行具体描述 — 含触发场景 + 核心结论}
type: {user|feedback|project|reference}
---
\`\`\`

→ 见 memory-write skill §3"
  fi
fi

# ============================================================
# 输出
# ============================================================

if [ -n "$WARNINGS" ]; then
  jq -n \
    --arg ctx "$WARNINGS" \
    '{
      hookSpecificOutput: {
        hookEventName: "PostToolUse",
        additionalContext: $ctx
      }
    }'
fi

exit 0

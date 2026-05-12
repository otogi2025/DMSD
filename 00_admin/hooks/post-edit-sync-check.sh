#!/usr/bin/env bash
# DMSD CC PostToolUse hook — Write/Edit 工具调用后自动跑联动检查
#
# 配置位置：.claude/settings.json hooks.PostToolUse[matcher="Write|Edit"]
# 触发时机：CC 调 Write 或 Edit 工具完成后
#
# 工作流：
# 1. 从 stdin 读 PostToolUse JSON 输入
# 2. 提取 tool_input.file_path
# 3. source 00_admin/hooks/lib/sync-rules.sh
# 4. 跑 check_sync_for_files <file>
# 5. 如有警告 → 用 hookSpecificOutput.additionalContext 注入给 CC
#
# 比 git pre-commit hook 早一步（CC 中途没 commit 也能拦联动漏改）
#
# 2026-05-04 itsuki 拍板新建（连同 file-linkage skill 一起）

set -e

# ============================================================
# Step 1: 读 stdin JSON
# ============================================================

INPUT=$(cat)

# 没 stdin 输入 → 直接 exit（防御性）
if [ -z "$INPUT" ]; then
  exit 0
fi

# ============================================================
# Step 2: 提取 file_path
# ============================================================

# Write 和 Edit 工具的 tool_input 都有 file_path 字段
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# 转成相对项目根的路径（CLAUDE_PROJECT_DIR 由 CC 注入）
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/Users/kurekoduki/dev/DMSD}"
RELATIVE_PATH="${FILE_PATH#$PROJECT_DIR/}"

# 如果还是绝对路径（说明不在项目内）→ skip
if [[ "$RELATIVE_PATH" == /* ]]; then
  exit 0
fi

# ============================================================
# Step 3: source sync-rules.sh
# ============================================================

SYNC_RULES="$PROJECT_DIR/00_admin/hooks/lib/sync-rules.sh"

if [ ! -f "$SYNC_RULES" ]; then
  exit 0  # rules 文件不在 → 静默退出（不影响 CC）
fi

source "$SYNC_RULES"

# ============================================================
# Step 4: 跑联动检查
# ============================================================

# check_sync_for_files 输出多行 warning（每条触发规则一段）
# 注意它的 return 值 = 触发数（非 0 不代表失败，warn-only 设计）
WARNINGS=$(check_sync_for_files "$RELATIVE_PATH" 2>&1 || true)

# ============================================================
# Step 5: 注入给 CC（如果有警告）
# ============================================================

if [ -n "$WARNINGS" ]; then
  # 先在 shell 里拼好完整 context 字符串（避免 jq 字符串里 shell 变量展开 edge case）
  ADDITIONAL_CONTEXT="📌 文件联动检查（PostToolUse hook on ${RELATIVE_PATH}）：

${WARNINGS}

→ 详细联动规则见 file-linkage skill（.claude/skills/file-linkage/SKILL.md）；忽略此提醒前请确认这些联动是否真的不需要。"

  # 用 jq 构造 PostToolUse hook 标准输出 — additionalContext 会注入 CC 上下文
  jq -n \
    --arg ctx "$ADDITIONAL_CONTEXT" \
    '{
      hookSpecificOutput: {
        hookEventName: "PostToolUse",
        additionalContext: $ctx
      }
    }'
fi

exit 0

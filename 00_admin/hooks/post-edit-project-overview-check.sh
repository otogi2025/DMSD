#!/usr/bin/env bash
# DMSD CC PostToolUse hook — project-overview 同步检查（全项目覆盖版）
#
# 配置位置：.claude/settings.json hooks.PostToolUse[matcher="Write|Edit"]
# 触发时机：CC 写 / 改任何 DMSD 项目内文件后
#
# 目的：防 project-overview SKILL.md 跟实际文件树漂移
#
# itsuki 2026-05-19 拍板 v2 — 改成全项目覆盖
#   v1（5-13 加 / 白名单触发）漏覆盖 routers / services / alembic / Android 真代码 / iOS Features 等
#   → 5-19 对账发现 9 处漂移 → itsuki 拍板「hook 覆盖整个项目」
#
# 工作流：
# 1. 提取 file_path
# 2. 只 skip 必要项：project-overview 自身 / 临时文件 / .gitignore 排除目录
# 3. 其他全部触发 — grep project-overview 看有没有引用 → 没有就 warn 提醒

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

# 不在项目内 skip
if [[ "$RELATIVE_PATH" == /* ]]; then
  exit 0
fi

# ============================================================
# 必要的 skip 名单（最小化 — 只 skip 真不需要检查的）
# ============================================================

case "$RELATIVE_PATH" in
  # 改 project-overview 自身 — 避免循环触发
  .claude/skills/project-overview/*) exit 0 ;;

  # 临时文件 / 备份 / 锁文件
  *.lock|*.log|*.bak|*.bak2|*.swp|*.tmp) exit 0 ;;
  /tmp/*) exit 0 ;;

  # .gitignore 排除的目录（git 看不见，project-overview 也不会列）
  graphify-out/*|.beads/*|.scratch/*) exit 0 ;;
  node_modules/*|*/node_modules/*) exit 0 ;;
  __pycache__/*|*/__pycache__/*) exit 0 ;;
  .venv/*|*/.venv/*) exit 0 ;;
  DerivedData/*|*/DerivedData/*) exit 0 ;;
  *.swiftpm/*|*/.swiftpm/*) exit 0 ;;

  # macOS / IDE 元数据
  *.DS_Store|*/xcuserdata/*) exit 0 ;;
esac

# ============================================================
# 全项目其他文件 — 一律检查
# ============================================================

OVERVIEW="$PROJECT_DIR/.claude/skills/project-overview/SKILL.md"
if [ ! -f "$OVERVIEW" ]; then
  exit 0
fi

FILENAME=$(basename "$RELATIVE_PATH")

# grep 文件名 + 路径片段是否在 project-overview 里
HAS_NAME=0
HAS_PATH=0
if grep -q "$FILENAME" "$OVERVIEW" 2>/dev/null; then
  HAS_NAME=1
fi
if grep -q "$RELATIVE_PATH" "$OVERVIEW" 2>/dev/null; then
  HAS_PATH=1
fi

# ============================================================
# 输出提醒
# ============================================================

if [ "$HAS_NAME" = "1" ] && [ "$HAS_PATH" = "1" ]; then
  # 文件名 + 路径都在 — 结构 OK，但描述可能漂
  WARNING="📋 project-overview 提醒（${RELATIVE_PATH}）

✅ 文件名 + 路径都已在 project-overview 引用 — 结构层面 OK。

⚠️ 但请确认本次改动是否影响**描述准确性**：
- 文件作用 / 状态 描述是否还准
- 行数 / 文件数等数字是否要更新

→ 若改了文件**实质内容**（不只是 typo），考虑同步 \`.claude/skills/project-overview/SKILL.md\` 对应章节描述"
elif [ "$HAS_PATH" = "1" ]; then
  # 路径在但名字对不上（罕见 — 通常 grep 文件名也会命中路径里的文件名片段）
  exit 0
elif [ "$HAS_NAME" = "1" ]; then
  # 文件名在 — 算 OK（project-overview 用短引用是常态）
  # 2026-05-21 修复（B-021 同源 bug）：原版要求完整路径 + 文件名都在才 OK
  # → 误报严重（每次改 TODO.md / WIP.md / flow_design.md 等都报「路径漂」，
  #   project-overview 用短引用 `TODO.md` 而不是完整路径 `00_admin/TODO.md` 是常态）
  # → 改成：文件名在 = OK，提醒描述准确性即可
  WARNING="📋 project-overview 提醒（${RELATIVE_PATH}）

✅ 文件名 \`${FILENAME}\` 在 project-overview 有引用 — 结构层面 OK（用短引用是常态）。

⚠️ 但请确认本次改动是否影响**描述准确性**：
- 文件作用 / 状态 描述是否还准
- 行数 / 文件数等数字是否要更新

→ 若改了**实质内容**（不只是 typo），考虑同步 \`.claude/skills/project-overview/SKILL.md\` 对应章节描述"
else
  # 完全没引用 — 新建文件 / 整段没列
  WARNING="📋 project-overview 同步检查（${RELATIVE_PATH}）

⚠️ 这个文件**没在 project-overview SKILL.md 里找到任何引用** — 可能是：

1. **新建文件** → 应该加进 project-overview 对应章节
2. **新建子目录里的文件** → 整个子目录可能 project-overview 没列过（例如 5-19 校准前 backend/v1/alembic/ 9 文件完全没列）
3. **改名了** → 旧引用全失效

→ 修复：Edit \`.claude/skills/project-overview/SKILL.md\` 对应章节加新 entry（含文件名 / 一句话作用 / 状态）

→ 出处：itsuki 2026-05-13 立规则 / 5-19 改成全项目覆盖（防 hook 视野外目录漂移）"
fi

jq -n --arg ctx "$WARNING" \
  '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'

exit 0

#!/usr/bin/env bash
# DMSD CC PostToolUse hook — project-overview 同步检查
#
# 配置位置：.claude/settings.json hooks.PostToolUse[matcher="Write|Edit"]
# 触发时机：CC 写 / 改文件后
#
# 目的: 防止 project-overview SKILL.md 跟实际文件树漂移
# itsuki 2026-05-13 怒怼后立 — 历史漂移：5-13 整理 26 文件后没同步 project-overview，
#   itsuki "我看不到的地方也会出现文件乱"。
#
# 工作流:
# 1. 提取 file_path
# 2. skip：改的是 project-overview / raw log / memory / 归档 (内容不影响结构)
# 3. 是重要结构变动文件 (00_admin/*.md / 01_specs/*.md / 02_design/*.md / hook / 5 端 README) → 触发检查
# 4. grep project-overview SKILL.md 看是否有引用 → 没有就 warn 提醒加 / 改

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
# 排除 skip 名单（内容文件不影响项目结构）
# ============================================================

case "$RELATIVE_PATH" in
  # 改 project-overview 自身 — 避免循环
  .claude/skills/project-overview/*) exit 0 ;;

  # 内容文件（raw log / dev_log / problem_solving / decision_log / learning_path / project_evolution）
  05_logs/raw/*|05_logs/dev_log/*|05_logs/problem_solving/*) exit 0 ;;
  05_logs/decision_log.md|05_logs/learning_path.md|05_logs/project_evolution.md) exit 0 ;;

  # memory 系统（CC 自动 memory）
  *.claude/projects/*/memory/*) exit 0 ;;

  # 归档区不影响活动结构
  99_archive/*) exit 0 ;;

  # 临时文件
  *.lock|*.log|*.bak|*.swp) exit 0 ;;
  /tmp/*) exit 0 ;;

  # graphify / .beads / .scratch — .gitignore 排除
  graphify-out/*|.beads/*|.scratch/*) exit 0 ;;
esac

# ============================================================
# 触发白名单（结构相关文件改动 / 新建时检查）
# ============================================================

TRIGGERED=""
case "$RELATIVE_PATH" in
  # 00_admin 顶层 .md（不含已 skip 的）
  00_admin/*.md) TRIGGERED="00_admin" ;;
  00_admin/hooks/*) TRIGGERED="hooks" ;;

  # 01_specs 主体 + 字典
  01_specs/*.md|01_specs/*/*.md) TRIGGERED="01_specs" ;;

  # 02_design 主体
  02_design/*.md) TRIGGERED="02_design" ;;

  # 5 端 README + DESIGN_LOG
  03_dev/*/README.md|03_dev/*/*_DESIGN_LOG.md) TRIGGERED="design_log" ;;

  # 5 端实装层文件（v1/ 主入口 / 配置）— 重要新建检查
  03_dev/backend/v1/app/*.py) TRIGGERED="backend_app" ;;
  03_dev/student_ios/v1/TomoshibiApp/Root/*.swift) TRIGGERED="ios_root" ;;
  03_dev/student_ios/v1/TomoshibiApp/Foundation/*.swift) TRIGGERED="ios_foundation" ;;
  03_dev/rollcall_device/src/*.py) TRIGGERED="device" ;;

  # skill / 根目录顶层 .md
  .claude/skills/*/SKILL.md) TRIGGERED="skill" ;;
  CLAUDE.md|README.md|CHANGELOG.md) TRIGGERED="root" ;;

  # 其他 — skip
  *) exit 0 ;;
esac

# ============================================================
# 检查 project-overview 是否引用了这文件
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
# 也查路径片段（catch 重命名了文件名但旧路径还在的情况）
if grep -q "$RELATIVE_PATH" "$OVERVIEW" 2>/dev/null; then
  HAS_PATH=1
fi

# ============================================================
# 输出提醒
# ============================================================

if [ "$HAS_NAME" = "1" ] && [ "$HAS_PATH" = "1" ]; then
  # 文件名 + 路径都在 — 大概率 OK，但还是温和提醒可能描述漂移
  WARNING="📋 project-overview 提醒（${RELATIVE_PATH}）

✅ 文件名 + 路径都已在 project-overview 引用 — 结构层面 OK。

⚠️ 但请确认本次改动是否影响**描述准确性**：
- 文件作用 / 状态 / AC 价值 描述是否还准
- 行数 / 文件数等数字是否要更新

→ 若改了文件**实质内容**（不只是 typo），考虑同步 \`.claude/skills/project-overview/SKILL.md\` 对应章节描述"
elif [ "$HAS_PATH" = "1" ]; then
  # 路径在但名字对不上（罕见）
  exit 0
elif [ "$HAS_NAME" = "1" ]; then
  # 文件名在但路径不在 — 可能改名 / 移位
  WARNING="📋 project-overview 漂移检测（${RELATIVE_PATH}）

⚠️ 文件名 \`${FILENAME}\` 在 project-overview 里有引用，但**完整路径 \`${RELATIVE_PATH}\` 没找到** — 可能：

1. 文件改名了 → project-overview 引用的旧路径已失效
2. 文件移位了 → project-overview 引用的旧路径要更新

→ 修复：Edit \`.claude/skills/project-overview/SKILL.md\` 找到 \`${FILENAME}\` 引用 → 改成新路径"
else
  # 完全没引用 — 新建文件
  WARNING="📋 project-overview 同步检查（${RELATIVE_PATH}）

⚠️ 这个文件**没在 project-overview SKILL.md 里找到任何引用** — 可能是：

1. **新建文件** → 应该加进 project-overview 对应章节
2. 改名了 → project-overview 引用的旧名 + 旧路径都已失效

触发分类：${TRIGGERED}

→ 修复：Edit \`.claude/skills/project-overview/SKILL.md\` 对应章节加新 entry（含文件名 / 状态 / 作用 / AC 价值）

→ 出处：itsuki 2026-05-13 立的铁律 — '改文件就看 project-overview 同步'"
fi

jq -n --arg ctx "$WARNING" \
  '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'

exit 0

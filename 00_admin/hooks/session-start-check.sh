#!/usr/bin/env bash
# DMSD CC SessionStart hook — 会话启动时自动跑轻量状态扫描
#
# 配置位置：.claude/settings.json hooks.SessionStart
# 触发时机：CC 会话启动时（startup / resume / clear / compact）
#
# 工作流：
# 1. 读 stdin SessionStart JSON（含 hook_event_name / source）
# 2. 跑轻量 git 状态扫描（git status / 未 push commit / stash）
# 3. 读 WIP.md 顶部 / CHANGELOG.md 顶部
# 4. 把状态以 hookSpecificOutput.additionalContext 注入 CC 上下文
# 5. CC 看到 context 后跑 session-start skill 详细 7 步流程（如需要）
#
# 设计原则：
# - 轻量（<1s 完成）— 重头戏在 session-start skill，hook 只做不可省的状态扫描
# - 不阻塞（即使脚本失败也 exit 0，不影响 CC 启动）
# - 注入信息要精简（CC 看 context 加载，太长浪费 token）
#
# 2026-05-04 itsuki 拍板新建（连同 session-start skill 一起）

set -e

# 防御：脚本失败不能影响 CC 启动
trap 'exit 0' ERR

# ============================================================
# Step 1: 读 stdin（防御性 — 即使没 stdin 也继续）
# ============================================================

INPUT=$(cat 2>/dev/null || echo "{}")

# source 字段：startup / resume / clear / compact
SOURCE=$(echo "$INPUT" | jq -r '.source // "unknown"' 2>/dev/null || echo "unknown")

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/Users/itsuki/dev/DMSD}"

# 不在 DMSD 项目目录 → skip
if [ ! -d "$PROJECT_DIR/.git" ]; then
  exit 0
fi

cd "$PROJECT_DIR" 2>/dev/null || exit 0

# ============================================================
# Step 2: 轻量 git 扫描
# ============================================================

# 当前 branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

# 工作树污染统计
MODIFIED_COUNT=$(git status --porcelain 2>/dev/null | grep -c "^ M" || true)
UNTRACKED_COUNT=$(git status --porcelain 2>/dev/null | grep -c "^??" || true)
STAGED_COUNT=$(git status --porcelain 2>/dev/null | grep -cE "^[AMD] " || true)

# 残留垃圾文件（典型嫌疑）
SUSPICIOUS=$(git status --porcelain 2>/dev/null | grep -E "\.(bak|bak[0-9]|DS_Store)$|File\.txt$" | head -5 | sed 's/^/  /')

# 未 push commit 数
UNPUSHED_COUNT=$(git log --oneline origin/main..HEAD 2>/dev/null | wc -l | tr -d ' ' || echo "0")

# stash 数
STASH_COUNT=$(git stash list 2>/dev/null | wc -l | tr -d ' ' || echo "0")

# ============================================================
# Step 3: 读 WIP / CHANGELOG 顶部
# ============================================================

WIP_HEAD=""
if [ -f "00_admin/WIP.md" ]; then
  # 取前 30 行（够覆盖头部 + 当下焦点 + 最近会话）
  WIP_HEAD=$(head -30 00_admin/WIP.md 2>/dev/null || echo "")
fi

CHANGELOG_HEAD=""
if [ -f "CHANGELOG.md" ]; then
  CHANGELOG_HEAD=$(head -5 CHANGELOG.md 2>/dev/null || echo "")
fi

# ============================================================
# Step 4: 拼 additionalContext
# ============================================================

# 只在 source = startup 或 resume 时注入（compact / clear 已经在会话内，少加 token）
if [ "$SOURCE" != "startup" ] && [ "$SOURCE" != "resume" ]; then
  exit 0
fi

ADDITIONAL_CONTEXT="🌅 SessionStart hook — DMSD repo 状态自动扫描（source=${SOURCE}）

【Git 状态】
- branch: ${BRANCH}
- 已修改未 staged: ${MODIFIED_COUNT}
- untracked: ${UNTRACKED_COUNT}
- staged: ${STAGED_COUNT}
- 未 push commit: ${UNPUSHED_COUNT}
- stash: ${STASH_COUNT}"

if [ -n "$SUSPICIOUS" ]; then
  ADDITIONAL_CONTEXT="${ADDITIONAL_CONTEXT}

【⚠️ 疑似残留垃圾文件】
${SUSPICIOUS}"
fi

if [ -n "$CHANGELOG_HEAD" ]; then
  ADDITIONAL_CONTEXT="${ADDITIONAL_CONTEXT}

【CHANGELOG 顶部】
${CHANGELOG_HEAD}"
fi

if [ -n "$WIP_HEAD" ]; then
  ADDITIONAL_CONTEXT="${ADDITIONAL_CONTEXT}

【WIP.md 顶部 30 行】
${WIP_HEAD}"
fi

ADDITIONAL_CONTEXT="${ADDITIONAL_CONTEXT}

→ 这是 hook 自动扫描的轻量快照。如 itsuki 说「启动 / 我回来了 / 继续」等触发词，调用 session-start skill 跑完整 7 步流程（含多会话占用诊断 / 报告模板）。
→ 不要主动催进度 / 不主动列 TODO（违反 CLAUDE.md 启动铁律）。"

# ============================================================
# Step 5: 输出 hookSpecificOutput
# ============================================================

jq -n \
  --arg ctx "$ADDITIONAL_CONTEXT" \
  '{
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: $ctx
    }
  }'

exit 0

#!/usr/bin/env bash
# DMSD project-overview 漂移对账脚本
#
# 干啥：跑 git ls-files 拿顶级目录真实文件数 → 跟 project-overview §0.1 体量表对比 → 差异列出来
#
# 怎么跑：
#   - SessionStart hook 自动触发（注册在 .claude/settings.json）
#   - itsuki 手动跑：bash bin/check_overview_drift.sh
#
# 出处：itsuki 2026-05-19 拍板 C 方案（A hook 全覆盖 + B 启动对账）— A 解决 CC 当下改文件，B 解决跨会话 / 外部工具改文件漂

set -e
trap 'exit 0' ERR

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/Users/kurekoduki/dev/DMSD}"
cd "$PROJECT_DIR" 2>/dev/null || exit 0

OVERVIEW="$PROJECT_DIR/.claude/skills/project-overview/SKILL.md"

if [ ! -f "$OVERVIEW" ]; then
  exit 0
fi

# ============================================================
# 1. 跑 git ls-files 拿顶级目录真实数
# ============================================================

TOTAL_REAL=$(git ls-files 2>/dev/null | wc -l | tr -d ' ')

if [ "$TOTAL_REAL" = "0" ]; then
  # 不在 git 仓库或 git ls-files 失败 — 静默退出
  exit 0
fi

# 顶级目录文件数（含根目录散件）— 只算 committed（git ls-files）
REAL_DIRS=$(git ls-files | awk -F/ 'NF==1 {print "ROOT"} NF>1 {print $1}' | sort | uniq -c | awk '{print $2"="$1}')

# 顶级目录文件数（含 untracked / staged）— 用 git ls-files + git status 跟 ??/A 标记
# 修复 2026-05-21（B-021）：原版用 git ls-files 不区分 staged / committed，
# 导致 project-overview 已 list 但未 commit 的文件被报「漂」。
# 改算法：用 ls-files + 把 status -s 里 ??/A/M 标记的也算上 = "应该 in git 的"
REAL_DIRS_ALL=$(
  {
    git ls-files
    git status --porcelain | awk '$1 ~ /^(\?\?|A)/ {print $2}'
  } | sort -u | awk -F/ 'NF==1 {print "ROOT"} NF>1 {print $1}' | sort | uniq -c | awk '{print $2"="$1}'
)
UNCOMMITTED_COUNT=$(git status --porcelain | awk '$1 ~ /^(\?\?|A)/' | wc -l | tr -d ' ')

# ============================================================
# 2. 从 project-overview §0.1 体量表抽数字
# ============================================================
#
# 表格行格式：| `03_dev/` | 546 | 57% | ... |
# 或：| 根目录 | 6 | 0.6% | ... |
# 或：| **总计** | **957** | 100% | |
#
# 修复 2026-05-21（B-021）：必须 scoped 到 §0.1 体量表上下文，否则会误抓 §1.8.1 .claude/ 23 行表里的「| `.claude/` | 23 |」、§1.8.2 等其他表。
# 算法：找到 `### 0.1` 标题 → in_table=1；遇到下一个 `### 0.2` 或 `##`/`###` 别的 → in_table=0。

# 抽顶级目录数（带反引号 + 斜杠的）— 限定到 §0.1 体量表
# 允许数字后跟 `+`（如 `9+` 表示「9 或更多」— 当前 .claude/ 这么写）
OVERVIEW_DIRS=$(awk -F'|' '
  /^### 0\.1 / { in_table=1; next }
  /^### 0\.2 / { in_table=0 }
  /^## / && !/^### 0\.1/ { in_table=0 }
  in_table && /\| `[^`]+\/` *\| *[0-9]+\+? *\|/ {
    gsub(/[ ` ]/, "", $2);
    gsub(/\//, "", $2);
    gsub(/[ +]/, "", $3);
    print $2"="$3
  }
' "$OVERVIEW")

# 抽根目录数 + 总计 — 同样限定到 §0.1
OVERVIEW_ROOT=$(awk -F'|' '
  /^### 0\.1 / { in_table=1; next }
  /^### 0\.2 / { in_table=0 }
  /^## / && !/^### 0\.1/ { in_table=0 }
  in_table && /\| 根目录 *\| *[0-9]+ *\|/ {
    gsub(/ /, "", $3);
    print $3
  }
' "$OVERVIEW")

OVERVIEW_TOTAL=$(awk -F'|' '
  /^### 0\.1 / { in_table=1; next }
  /^### 0\.2 / { in_table=0 }
  /^## / && !/^### 0\.1/ { in_table=0 }
  in_table && /\| \*\*总计\*\* *\| *\*\*[0-9]+\*\* *\|/ {
    gsub(/[* ]/, "", $3);
    print $3
  }
' "$OVERVIEW")

# ============================================================
# 3. 对比 — 区分真漂 vs 仅未 commit
# ============================================================
#
# 修复 2026-05-21（B-021）：原版只对比 committed = git ls-files。
# 但 project-overview 写的数字常常 anticipate 即将 commit 的文件（如
# 加 check_overview_drift.sh 时已写进 §0.1 但还未 commit）。
# 改算法：
#   - committed = git ls-files 数
#   - all = committed + (untracked / staged / modified)
#   - written 写的数字 = overview §0.1 体量表
#   - 真漂 = written ≠ all（overview 跟「实际想 in git 的」对不上）
#   - 仅未 commit = written == all 但 written ≠ committed（overview 已含未 commit 文件）

DRIFT_LINES=""        # 真漂
UNCOMMITTED_LINES=""  # 仅未 commit
ALL_OK=true
HAS_UNCOMMITTED=false

# 顶级目录逐个对比 — 用 REAL_DIRS_ALL（含 untracked / staged）
while IFS= read -r line; do
  [ -z "$line" ] && continue
  dir=$(echo "$line" | cut -d= -f1)
  real_all=$(echo "$line" | cut -d= -f2)
  real_committed=$(echo "$REAL_DIRS" | grep "^${dir}=" | head -1 | cut -d= -f2)
  [ -z "$real_committed" ] && real_committed=0

  if [ "$dir" = "ROOT" ]; then
    written="$OVERVIEW_ROOT"
    label="根目录"
  else
    written=$(echo "$OVERVIEW_DIRS" | grep "^${dir}=" | head -1 | cut -d= -f2)
    label="$dir/"
  fi

  if [ -z "$written" ]; then
    DRIFT_LINES+="  - ${label}: 写 (没找到) / 实际 ${real_all}"$'\n'
    ALL_OK=false
  elif [ "$written" = "$real_all" ] && [ "$written" != "$real_committed" ]; then
    # 跟 all 对上,但跟 committed 对不上 → overview 含未 commit 文件
    delta=$((real_all - real_committed))
    UNCOMMITTED_LINES+="  - ${label}: 写 ${written} = committed ${real_committed} + 未 commit ${delta}"$'\n'
    HAS_UNCOMMITTED=true
  elif [ "$written" != "$real_all" ]; then
    DRIFT_LINES+="  - ${label}: 写 ${written} / 实际 ${real_all} (committed ${real_committed} + 未 commit $((real_all - real_committed)))"$'\n'
    ALL_OK=false
  fi
done <<< "$REAL_DIRS_ALL"

# 总计对比 — 拿 all 计数
TOTAL_ALL=$((TOTAL_REAL + UNCOMMITTED_COUNT))
if [ -n "$OVERVIEW_TOTAL" ] && [ "$OVERVIEW_TOTAL" != "$TOTAL_ALL" ] && [ "$OVERVIEW_TOTAL" != "$TOTAL_REAL" ]; then
  ALL_OK=false
fi

# ============================================================
# 4. 输出
# ============================================================

if [ "$ALL_OK" = "true" ] && [ "$HAS_UNCOMMITTED" = "false" ]; then
  echo "✅ project-overview §0.1 对账（启动时跑）：${TOTAL_REAL} 文件全部对上 — 没漂"
elif [ "$ALL_OK" = "true" ] && [ "$HAS_UNCOMMITTED" = "true" ]; then
  echo "✅ project-overview §0.1 对账（启动时跑）：没漂"
  echo ""
  echo "ℹ️ 但有未 commit 文件（overview 已 anticipate）："
  printf '%s' "$UNCOMMITTED_LINES"
  echo ""
  echo "→ 记得 commit 让 overview 跟 git 真实状态对齐"
else
  echo "⚠️ project-overview §0.1 漂移检测（启动时跑）："
  echo ""
  echo "总计：写 ${OVERVIEW_TOTAL:-未找到} / committed ${TOTAL_REAL} + 未 commit ${UNCOMMITTED_COUNT} = 实际 ${TOTAL_ALL}"
  echo ""
  if [ -n "$DRIFT_LINES" ]; then
    echo "顶级目录漂移："
    printf '%s' "$DRIFT_LINES"
  fi
  if [ -n "$UNCOMMITTED_LINES" ]; then
    echo ""
    echo "顶级目录仅未 commit（不算漂）："
    printf '%s' "$UNCOMMITTED_LINES"
  fi
  echo ""
  echo "→ 修复：Edit \`.claude/skills/project-overview/SKILL.md\` §0.1 体量表 + 对应章节描述"
  echo "→ 出处：itsuki 2026-05-19 拍板加 SessionStart 对账（B 方案）/ 2026-05-21 修 awk + staged/committed 区分（B-021）"
fi

exit 0

#!/usr/bin/env bash
# DMSD 文件联动规则表（共享库）
#
# 目的：CLAUDE.md §会话结束 §3「文件关联追踪表」的代码化。
#       pre-commit hook 和 bin/sync-check.sh 都 source 这个文件，复用同一份规则。
#
# 规则模型：
#   改了 trigger 模式的文件 → 必查 must 模式的文件是否也改了 → 没改就警告
#   每条规则附中文 reason 说明「为什么联动」，让 itsuki 看 warn 就能理解。
#
# 用法：
#   source 00_admin/hooks/lib/sync-rules.sh
#   check_sync_for_files <file1> <file2> ...     # 输入改过的文件列表
#   → 输出: 多行 warning 文本（每条规则触发 → 一段输出）
#   → exit code 始终 0（warn-only，不阻断）
#
# 维护：
#   加规则 → 在下面 add_rule 段调用 add_rule + 同步 CLAUDE.md §会话结束 §3 表 + hooks/README.md
#
# 2026-05-04 itsuki 拍板新建（A+B 方案 — pre-commit 内容检查 + sync-check 中途查）
#
# 注: 不开 set -u / set -e — 本文件被 source 后会污染父 shell；
#     函数 return 非 0 会被父 shell 的 set -e 误触发为致命错误（warn-only 设计与 set -e 不兼容）。

# ============================================================
# 5 个并行数组存规则（避免单字符串分隔符与 ERE 中 | 冲突）
# ============================================================

RULE_NAMES=()
RULE_TRIGGERS=()    # ERE pattern，匹配 trigger 文件路径
RULE_MUSTS=()       # 逗号分隔的 must pattern（mode=must 时检查）
RULE_REASONS=()     # 中文说明
RULE_MODES=()       # "must" or "action"

add_rule() {
  RULE_NAMES+=("$1")
  RULE_TRIGGERS+=("$2")
  RULE_MUSTS+=("$3")
  RULE_REASONS+=("$4")
  RULE_MODES+=("$5")
}

# ============================================================
# 规则定义（基于 CLAUDE.md §会话结束 §3 文件关联追踪表）
# ============================================================

add_rule \
  "backend-models" \
  '^03_dev/backend/v1/app/models\.py$' \
  '03_dev/backend/v1/app/schemas\.py,03_dev/backend/v1/alembic/versions/.+\.py,03_dev/backend/v1/app/routers/.+\.py,03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels\.swift' \
  '后端 ORM model 改了 → 必须连带更新: schemas.py(Pydantic) / alembic migration / routers / iOS NetworkModels.swift（字段对齐）' \
  "must"

add_rule \
  "backend-routers" \
  '^03_dev/backend/v1/app/routers/.+\.py$' \
  '03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/Endpoints/.+\.swift' \
  '后端 API 端点改 → iOS 客户端 Endpoints/*API.swift 必须改对应(URL / 参数 / 返回类型对齐)' \
  "must"

add_rule \
  "system-features" \
  '^02_design/system_features\.md$' \
  '03_dev/backend/BACKEND_DESIGN_LOG\.md,03_dev/student_ios/IOS_DESIGN_LOG\.md,03_dev/teacher_web/WEB_DESIGN_LOG\.md' \
  '共用层 system_features 改 → 各端 *_DESIGN_LOG.md 引用是否要更新(至少 1 个端通常会受影响)' \
  "must"

add_rule \
  "ios-route" \
  '^03_dev/student_ios/v1/TomoshibiApp/Foundation/Routing/Route\.swift$' \
  '03_dev/student_ios/v1/TomoshibiApp/Root/RootView\.swift' \
  'Route 加 case → RootView switch 必须补对应分支，否则编译失败' \
  "must"

add_rule \
  "spec-body" \
  '^01_specs/.+\.md$' \
  '' \
  '01_specs/ 主体改 → 触发 00_admin/版本管理SOP.md §10 4 问，可能要 bump 版本号' \
  "action"

add_rule \
  "design-doc" \
  '^02_design/(flow_design|hardware_design|teacher_requirements)\.md$' \
  '' \
  '主设计文档改 → 触发 00_admin/版本管理SOP.md §2 决策树，Minor 候选' \
  "action"

# 注: hooks trigger 用简单 [^/]+ 匹配 hooks 目录下所有文件（不细分扩展名，避免 ERE 嵌套捕获组）
add_rule \
  "hooks" \
  '^00_admin/hooks/[^/]+$' \
  '00_admin/hooks/README\.md' \
  'hooks 改 → README.md 必须同步(除非改的就是 README 自己)' \
  "must"

add_rule \
  "bin-script" \
  '^bin/[^/]+\.sh$' \
  'CLAUDE\.md,00_admin/文档同步点清单\.md,00_admin/hooks/README\.md' \
  'bin/ 脚本改了 → CLAUDE.md / 文档同步点清单.md / hooks README 是否要提到(新脚本 / 用法变化)' \
  "must"

# 注: ios-foundation trigger 用基础 .+ 单独检查文件名片段（不嵌套 ERE 分组）
add_rule \
  "ios-foundation-pill" \
  '^03_dev/student_ios/v1/TomoshibiApp/Foundation/.*Pill.*\.swift$' \
  '' \
  'iOS Foundation Pill 组件 props 可能改了 → grep 全 repo 找用到的地方，避免 caller 编译失败' \
  "action"

add_rule \
  "ios-foundation-card" \
  '^03_dev/student_ios/v1/TomoshibiApp/Foundation/.*Card.*\.swift$' \
  '' \
  'iOS Foundation Card 组件 props 可能改了 → grep 全 repo 找用到的地方' \
  "action"

add_rule \
  "ios-foundation-avatar" \
  '^03_dev/student_ios/v1/TomoshibiApp/Foundation/.*Avatar.*\.swift$' \
  '' \
  'iOS Foundation Avatar 组件 props 可能改了 → grep 全 repo 找用到的地方' \
  "action"

add_rule \
  "ios-foundation-glasssheet" \
  '^03_dev/student_ios/v1/TomoshibiApp/Foundation/.*GlassSheet.*\.swift$' \
  '' \
  'iOS Foundation GlassSheet 组件 props 可能改了 → grep 全 repo 找用到的地方' \
  "action"

# ============================================================
# 函数：check_sync_for_files
#   输入：参数 = 改过的文件路径列表
#   输出：触发的规则，每条一段 warning（中文 reason + 缺失文件列表）
# ============================================================

check_sync_for_files() {
  local changed_files
  changed_files=$(printf '%s\n' "$@" | grep -v '^$' || true)

  if [ -z "$changed_files" ]; then
    return 0
  fi

  local triggered_count=0
  local i
  for i in "${!RULE_NAMES[@]}"; do
    local name="${RULE_NAMES[$i]}"
    local trigger="${RULE_TRIGGERS[$i]}"
    local must="${RULE_MUSTS[$i]}"
    local reason="${RULE_REASONS[$i]}"
    local mode="${RULE_MODES[$i]}"

    local matched_triggers
    matched_triggers=$(echo "$changed_files" | grep -E "$trigger" 2>/dev/null || true)
    if [ -z "$matched_triggers" ]; then
      continue
    fi

    if [ "$mode" = "action" ]; then
      echo ""
      echo "  ⚠️  [$name] 触发"
      echo "     原因：$reason"
      echo "     触发文件："
      echo "$matched_triggers" | sed 's/^/       - /'
      triggered_count=$((triggered_count + 1))
      continue
    fi

    # must 型：must 列表里至少 1 个 pattern 命中改动 → 通过
    local must_satisfied=0
    local must_patterns
    IFS=',' read -ra must_patterns <<< "$must"

    local pattern
    for pattern in "${must_patterns[@]}"; do
      [ -z "$pattern" ] && continue
      if echo "$changed_files" | grep -qE "$pattern" 2>/dev/null; then
        must_satisfied=1
        break
      fi
    done

    if [ $must_satisfied -eq 0 ]; then
      echo ""
      echo "  ⚠️  [$name] 联动文件未改"
      echo "     原因：$reason"
      echo "     触发文件："
      echo "$matched_triggers" | sed 's/^/       - /'
      echo "     缺以下任一(至少改 1 个)："
      for pattern in "${must_patterns[@]}"; do
        [ -z "$pattern" ] && continue
        echo "       - $pattern"
      done
      triggered_count=$((triggered_count + 1))
    fi
  done

  # ============================================================
  # demo scaffold 检测（独立检查，不通过 add_rule — 需要内容判断 + git diff）
  # 2026-05-04 itsuki 拍板加：删 demo-clean skill 后补的自动维护机制
  # ============================================================
  local f
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if _check_demo_scaffold "$f"; then
      triggered_count=$((triggered_count + 1))
    fi
  done <<< "$changed_files"

  return $triggered_count
}

# ============================================================
# 函数：_check_demo_scaffold
#   输入：单个文件路径（相对项目根）
#   行为：iOS .swift / backend .py 文件如果 git diff 新增行包含 demo|bypass|stub|fake|mock|hack
#         字眼 → 提醒「记得加到 system_features.md 末尾 demo scaffold 清单」
#   返回：0 = 没触发；1 = 触发了 warning
# ============================================================

_check_demo_scaffold() {
  local file="$1"

  # 只对 iOS .swift / backend .py 检查
  if ! echo "$file" | grep -qE '^03_dev/(student_ios/v1/.+\.swift|backend/v1/app/.+\.py)$'; then
    return 0
  fi

  # 必须在 git 仓库
  if ! git rev-parse --git-dir &>/dev/null; then
    return 0
  fi

  # 文件不存在（被删了）→ skip
  if [ ! -f "$file" ]; then
    return 0
  fi

  # 看新增内容是否含 demo 字眼
  # - tracked 文件：用 git diff HEAD 看新增行（^+ 但不含 ^+++）
  # - untracked 新文件：直接 grep 整个文件内容（git diff 不显示）
  local new_demo
  if git ls-files --error-unmatch -- "$file" &>/dev/null; then
    # tracked
    new_demo=$(git diff HEAD -- "$file" 2>/dev/null \
      | grep '^+' | grep -v '^+++' \
      | grep -iE '\b(demo|bypass|stub|fake|mock|hack)\b' \
      | head -3 || true)
  else
    # untracked — 整文件视为新增
    new_demo=$(grep -niE '\b(demo|bypass|stub|fake|mock|hack)\b' "$file" 2>/dev/null \
      | head -3 || true)
  fi

  if [ -z "$new_demo" ]; then
    return 0
  fi

  echo ""
  echo "  ⚠️  [demo-scaffold-detect] 新增 demo / bypass / stub / fake / mock 字眼"
  echo "     原因：$file 新加了 demo 关键词 — 如果是为 v1.0 上线后要删的临时 scaffold，"
  echo "          记得加到 02_design/system_features.md 末尾「v1.0 上线前必删 demo scaffold 清单」"
  echo "          否则 v1.0 准备时会漏删 → 生产环境安全漏洞"
  echo "     新增内容（前 3 行）："
  echo "$new_demo" | sed 's/^/       /'
  return 1
}

# ============================================================
# 函数：detect_new_files
# ============================================================

detect_new_files() {
  local porcelain="$1"
  echo "$porcelain" | grep -E '^\?\?' | sed 's/^?? //' || true
}

# ============================================================
# 函数：check_new_declarative_files
#   新建 00_admin/*.md 或 CLAUDE.md → 提醒登记到 文档同步点清单.md
# ============================================================

check_new_declarative_files() {
  local new_files="$1"
  local doc_sync_list="00_admin/文档同步点清单.md"
  local hit=""

  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if echo "$f" | grep -qE '^(CLAUDE\.md|00_admin/[^/]+\.md)$'; then
      # 排除已登记的常规文件
      if ! echo "$f" | grep -qE '^(00_admin/(WIP|TODO|progress_overview|文档同步点清单|文件结构指南|版本管理SOP|CLAUDE_CODE_记录指南)\.md)$'; then
        hit="${hit}${f}\n"
      fi
    fi
  done <<< "$new_files"

  if [ -n "$hit" ]; then
    echo ""
    echo "  ⚠️  [new-declarative] 新建声明性文件"
    echo "     原因：新建 CLAUDE.md / 00_admin/*.md → 考虑加入 $doc_sync_list 让 hook 保护它"
    echo "     新文件："
    printf "$hit" | sed 's/^/       - /'
  fi
}

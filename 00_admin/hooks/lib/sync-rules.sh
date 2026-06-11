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
  '03_dev/backend/v1/app/schemas\.py,03_dev/backend/v1/alembic/versions/.+\.py,03_dev/backend/v1/app/routers/.+\.py,03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels\.swift,03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/data/model/Models\.kt' \
  '后端 ORM model 改了 → 核对下游是否跟上: schemas.py(Pydantic) / alembic migration / routers / iOS NetworkModels.swift / Android Models.kt。注:这是「至少改 1 个就放行」的或语义,不保证每个都改 — iOS + Android 两端字段要各自核对,别只改一端就当过了' \
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
  '03_dev/backend/BACKEND_DESIGN_LOG\.md,03_dev/student_ios/IOS_DESIGN_LOG\.md,03_dev/student_android/ANDROID_DESIGN_LOG\.md,03_dev/teacher_web/WEB_DESIGN_LOG\.md,03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG\.md' \
  '共用层 system_features 改 → 5 端 *_DESIGN_LOG.md 引用是否要更新(至少 1 个端通常会受影响)' \
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
  '01_specs/ 主体改 → 触发 version-bump skill §10 4 问，可能要 bump 版本号' \
  "action"

add_rule \
  "design-doc" \
  '^02_design/(flow_design|hardware_design|teacher_requirements)\.md$' \
  '' \
  '主设计文档改 → 触发 version-bump skill §2 决策树，Minor 候选' \
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
# 反向规则：业务代码 → 自端 *_DESIGN_LOG.md（2026-05-08 加 — 5 端对称 action 提醒）
# 之前只覆盖「设计→代码」+「数据层字段对齐」，这批补「代码→设计」反方向。
# action 模式（不是 must）— typo / 重命名 / 重构不一定要改设计；只温和提醒让 itsuki/CC 当场判断。
# ============================================================

add_rule \
  "ios-business-design" \
  '^03_dev/student_ios/v1/TomoshibiApp/Features/.+\.swift$' \
  '' \
  'iOS Features 业务代码改 → 判断是否同步 IOS_DESIGN_LOG.md(改 UI / 流程 / 字段需要;typo / 重构不用)，多端涉及时 system_features.md 也要更新' \
  "action"

add_rule \
  "android-business-design" \
  '^03_dev/student_android/.+/(ui|features)/.+\.kt$' \
  '' \
  'Android 业务代码改 → 判断是否同步 ANDROID_DESIGN_LOG.md，多端涉及时 system_features.md 也要更新' \
  "action"

add_rule \
  "backend-business-design" \
  '^03_dev/backend/v1/app/(routers|services)/.+\.py$' \
  '' \
  '后端业务代码改 → 判断是否同步 BACKEND_DESIGN_LOG.md，多端涉及时 system_features.md 也要更新' \
  "action"

add_rule \
  "web-business-design" \
  '^03_dev/teacher_web/v1/src/index\.html$|^03_dev/teacher_web/v1/src/index\.css$|^03_dev/teacher_web/v1/src/api/.+\.js$' \
  '' \
  'teacher_web 业务代码改 → 判断是否同步 WEB_DESIGN_LOG.md，多端涉及时 system_features.md 也要更新。活代码 = index.html + index.css + api/*.js（单文件 React，不编译 TS）。trigger 精确平铺这三类，刻意不含 vendor/(react/babel 第三方库) / _assets/(字体) / assets/(图标) / 废弃的 client.ts，避免它们误报' \
  "action"

add_rule \
  "rollcall-device-business-design" \
  '^03_dev/rollcall_device/src/.+\.py$' \
  '' \
  '点呼机业务代码改 → 判断是否同步 ROLLCALL_DEVICE_DESIGN_LOG.md，多端涉及时 system_features.md 也要更新' \
  "action"

add_rule \
  "design-log-to-system-features" \
  '^03_dev/.+/(BACKEND|IOS|ANDROID|WEB|ROLLCALL_DEVICE)_DESIGN_LOG\.md$' \
  '' \
  '某端 *_DESIGN_LOG 改 → 多端涉及时 system_features.md 也要更新(共用层真值)' \
  "action"

# ============================================================
# 点呼机架构链（2026-06-03 加 — 补 6-02 漂移事故的漏）
# 4 个文件是同一条「点呼机怎么读写 NFC」的链，改一个其余常跟着改。
# 用 action 模式（每次触发都无条件提醒）而不是 must — must 是「这些文件至少改 1
# 个就闭嘴」，正好会漏掉 6-02 那种「只改了 hardware_design 一个、其余三个没动」的情形。
# trigger 用 4 个完整路径加 | 平铺、每段自带 ^...$、无括号分组（避免 ERE 嵌套捕获组）。
# ============================================================

add_rule \
  "rollcall-arch-chain" \
  '^02_design/hardware_design\.md$|^02_design/flow_design\.md$|^03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG\.md$|^00_admin/项目心智模型\.md$' \
  '' \
  '点呼机架构链改一个 → 核对其余三个是否漂移：hardware_design.md(硬件选型) / flow_design.md(签到流程) / ROLLCALL_DEVICE_DESIGN_LOG.md(点呼机软件) / 项目心智模型.md(项目骨架) 是同一条链，改一个其余常跟着改（6-02 手机读→写反转就因缺这条链漏改了后三个）' \
  "action"

# ============================================================
# 后端路由 → 老师网页接口对接（2026-06-03 加 — 补 web 客户端裸奔的漏）
# backend-routers(Rule 2,must) 已管 iOS Endpoints，但 teacher_web 的 client.js
# 同样直连后端路由，过去无任何规则覆盖。单独用 action（不并入 Rule 2 的 must），
# 因为 iOS 和 web 是两个独立客户端、后端路由改了两个都可能要改，
# 而 must 是「列表里至少改 1 个就放行」会被 iOS 的改动满足、漏掉 web。
# ============================================================

add_rule \
  "backend-routers-web" \
  '^03_dev/backend/v1/app/routers/.+\.py$' \
  '' \
  '后端 API 路由改 → 老师网页 03_dev/teacher_web/v1/src/api/client.js（约 65 处直连后端接口路径）核对是否要跟改。注：与 backend-routers(must 管 iOS Endpoints) 互补，本条单独 action 提醒 web 端' \
  "action"

# ============================================================
# spec 字典链（2026-06-03 加 — 跟点呼机架构链同性质的真实链）
# RollCall_Spec.md §8 自声明「与字典四件套相互引用」，主体正文多处显式
# 引用字典为权威；后端 schemas.py/models.py 又实装了这些字段/枚举。
# action 模式（同点呼机链理由：must 会漏「只改字典、主体和后端没跟」）。
# ============================================================

add_rule \
  "spec-dict-chain" \
  '^01_specs/rollcall/FIELD_REGISTRY\.md$|^01_specs/rollcall/ENUM_REGISTRY\.md$|^01_specs/rollcall/ERROR_CODES\.md$|^01_specs/rollcall/DEVICE_REGISTRY\.md$|^01_specs/rollcall/RollCall_Spec\.md$' \
  '' \
  'spec 字典四件套(FIELD_REGISTRY 字段 / ENUM_REGISTRY 枚举 / ERROR_CODES 错误码 / DEVICE_REGISTRY 设备)与主体 RollCall_Spec.md 相互引用(主体 §8 声明)，后端 schemas.py/models.py 实装了这些字段枚举 → 改一个核对其余是否漂移' \
  "action"

# ============================================================
# 版本号链（2026-06-03 加 — 文档同步点清单 §1 双源同步的联动化）
# 版本号单一真值 = CHANGELOG.md（仓库根），二级源 = WIP.md 头部「当前版本」。
# 过去靠 post-edit-version-hardcode-check.sh 拦硬编码 + version-bump skill 人肉流程，
# 联动系统本身对「改一处提醒核对另一处」零覆盖，补 action 提醒。
# ============================================================

add_rule \
  "version-number-chain" \
  '^CHANGELOG\.md$|^00_admin/WIP\.md$|^05_logs/版本演变一览\.md$' \
  '' \
  '版本号单一真值 = CHANGELOG.md（改文件版本以它为准）。改 CHANGELOG = 迭代版本 → 必同步：① WIP.md 头部「当前版本」② 05_logs/版本演变一览.md（加总表行+详细段，AC 素材；itsuki 6-05 拍板 CHANGELOG↔版本演变一览 绑定）③ 三端客户端版本号（iOS project.yml CFBundleShortVersionString / Android app/build.gradle.kts versionName / teacher_web src/theme.ts APP_VERSION — minor 必同步，patch 可攒；6-09 重排后三端停在 0.15.0 就是漏了这条）。完整流程见 version-bump skill' \
  "action"

# ============================================================
# 联动系统自身的同步（2026-06-03 加 — codex 审查揪出的盲点）
# 规则代码 sync-rules.sh 与人读版 file-linkage/SKILL.md 必须同步,
# 但 sync-rules.sh 在 hooks/lib/ 下,Rule 8「hooks」只匹配 hooks/ 一层、捕获不到它,
# 导致「改了规则代码、人读版没跟」过去无任何提醒。用 must 强制同步。
# ============================================================

add_rule \
  "sync-rules-self" \
  '^00_admin/hooks/lib/sync-rules\.sh$' \
  '.claude/skills/file-linkage/SKILL\.md' \
  '联动规则代码 sync-rules.sh 改了 → 给人读的 .claude/skills/file-linkage/SKILL.md 必须同步(两边漂了联动系统就半失效:hook 按代码跑、人按表查,对不上)' \
  "must"

add_rule \
  "api-conventions" \
  '^01_specs/API_CONVENTIONS\.md$' \
  '' \
  'API 全局约定改了 → 核对四端 API 实装是否跟约定一致: 后端 routers/schemas.py + iOS Endpoints/NetworkModels.swift + Android data/network + teacher_web src/api/client.js。itsuki 常改 API,故每次触发都提醒(action)' \
  "action"

add_rule \
  "scope-freeze" \
  '^01_specs/v1\.[0-9]+_范围冻结决策\.md$' \
  '00_admin/v1\.0上线缺口看板\.html,01_specs/v1\.0_范围冻结决策\.md,01_specs/v1\.1_范围冻结决策\.md,01_specs/v1\.2_范围冻结决策\.md,00_admin/TODO\.md' \
  '范围冻结决策改了(功能在 v1.0/v1.1/v1.2 之间挪动) → 核对: ① 另外两份范围冻结文件(功能从 A 挪出必挪入 B,两份都要动) ② 00_admin/v1.0上线缺口看板.html(v1.0 范围变 = 看板缺口项变) ③ 00_admin/TODO.md §A 上线必做层(范围进出 = 必做清单进出)' \
  "must"

# 启动流程真值链 — dmsd-startup §2 是启动步骤唯一真值,CLAUDE.md/WIP 只写指针
# (itsuki 2026-06-11 拍板;历史教训:两处复述步骤都漂移过)
add_rule \
  "startup-truth-chain" \
  '^\.claude/skills/dmsd-startup/SKILL\.md$' \
  'CLAUDE\.md,00_admin/WIP\.md' \
  '启动流程说明书改了 → 核对: ① CLAUDE.md「dmsd-startup 强制加载」段 + skills 表(只许写指针,发现复述步骤内容就删成指针) ② 00_admin/WIP.md 顶部「会话开始」行(同样只许指针)' \
  "must"

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
      if ! echo "$f" | grep -qE '^(00_admin/(WIP|TODO|文档同步点清单|文件结构指南|版本管理SOP|CLAUDE_CODE_记录指南)\.md)$'; then
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

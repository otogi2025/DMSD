# DMSD Hooks（Git + CC PostToolUse）

## 是什么

DMSD 用了 **2 类 hook**（2026-05-04 itsuki 拍板补 CC PostToolUse hook 后升级）：

### Git hook（commit 时触发）

`git commit` 前自动跑 3 件事（按这个顺序）：

1. **版本号一致性检查**（阻塞型，2026-04-19 加）— "声明性文件"（`CLAUDE.md` / `WIP.md` / `TODO.md` / `progress_overview.md`）**不能硬编码版本号**。单源真值 = `CHANGELOG.md` 顶部。其他文件用 "当前版本见 CHANGELOG" 指针。
2. **版本 bump 提醒**（非阻塞，2026-04-29 加）— 改了 `01_specs/` / `02_design/` / `03_dev/*_DESIGN_LOG` 时提醒检查 version-bump skill `§2 决策树`。
3. **文件联动提醒**（非阻塞，2026-05-04 加）— 改了某文件但联动文件没动 → 警告。规则表 = `lib/sync-rules.sh`，详细联动矩阵见 `.claude/skills/file-linkage/SKILL.md`。**配套**：`bin/sync-check.sh` = 中途随时手动跑（不用等到 commit）。

### ⭐ CC PostToolUse hook（CC 调 Write/Edit 时立刻触发，2026-05-04 深夜加）

**比 git pre-commit 早一步**，CC 在中途没 commit 也能拦联动漏改。同 matcher 下挂 2 条 hook（并行跑）：

#### A. `post-edit-sync-check.sh` — 文件联动检查
- 配置文件：`.claude/settings.json`（hooks.PostToolUse[matcher="Write|Edit"][0]）
- 工作流：jq 解析 stdin → 提取 file_path → source `lib/sync-rules.sh` → `check_sync_for_files` → 注入 additionalContext
- 详细联动规则人类可读版：`.claude/skills/file-linkage/SKILL.md`

#### B. `post-edit-memory-check.sh` — Memory 索引检查（2026-05-04 加）
- 配置文件：`.claude/settings.json`（hooks.PostToolUse[matcher="Write|Edit"][1]）
- 触发条件：file_path 在 `/Users/itsuki/.claude/projects/-Users-itsuki-dev-DMSD/memory/` 且不是 `MEMORY.md` 自己
- 工作流：grep MEMORY.md 看是否引用新文件 → 没有就提醒「补索引」 + 检查 frontmatter 完整性
- 配套 skill：`.claude/skills/memory-write/SKILL.md`

### ⭐ CC SessionStart hook（每次会话起自动跑，2026-05-04 加）

- 配置文件：`.claude/settings.json`（hooks.SessionStart）
- 触发脚本：`00_admin/hooks/session-start-check.sh`
- 工作流：jq 解析 stdin（含 source: startup/resume/clear/compact）→ 跑轻量 git 状态扫描（branch / 工作树污染 / 未 push commit / stash / 残留垃圾文件嫌疑）→ 读 WIP.md 顶部 30 行 + CHANGELOG.md 顶部 5 行 → 注入 additionalContext
- 设计原则：轻量（<1s）/ 不阻塞 / 只在 startup/resume 注入（compact/clear 跳过省 token）
- 配套 skill：`.claude/skills/session-start/SKILL.md`（详细 7 步 SOP，hook 是开场快照）

### 测试方法

```bash
# 在 CC 内输入 /hooks 查看是否注册成功

# 手动 dry-run 测：
echo '{"source":"startup"}' | bash 00_admin/hooks/session-start-check.sh
echo '{"tool_input":{"file_path":"/Users/itsuki/.claude/projects/-Users-itsuki-dev-DMSD/memory/test.md"}}' | bash 00_admin/hooks/post-edit-memory-check.sh
echo '{"tool_input":{"file_path":"/Users/itsuki/dev/DMSD/03_dev/backend/app/models.py"}}' | bash 00_admin/hooks/post-edit-sync-check.sh
```

## 为什么（2026-04-19 发现）

DMSD 已经迭代了很多个版本，但 `CLAUDE.md` / `WIP` / `TODO` 等文件里还写着 "v0.2 修订进行中" 等过期版本号。

这是 **同一信息多处存储 → 必然漂移** 的典型问题。

系统性解 = 三件套：
1. **Single Source of Truth** — 版本号只写在 `CHANGELOG.md`
2. **同步点清单** — `00_admin/文档同步点清单.md` 列所有同步点
3. **pre-commit hook**（本目录）— 每次 commit 自动跑检查，拒绝不一致

## 安装（首次 clone 后必跑）

在每个 clone 了本 repo 的机器上跑**一次**：

```bash
bash 00_admin/hooks/install.sh
```

这会：
1. 设置 `git config core.hooksPath 00_admin/hooks`（让 git 去这个目录找 hook）
2. 把 `pre-commit` 设为可执行

**Mac 和 VPS 都要跑一次** — `core.hooksPath` 是 local git config，不跨机器同步。

## 使用

平时不用做任何事。每次 `git commit` 前 hook 会自动跑：

- ✅ 检查通过 → commit 正常进行
- ❌ 检查失败 → 看 hook 输出的错误信息，改掉硬编码版本号再 commit

## 豁免机制

如果某行**必须**写具体版本号（比如历史引用 / 文字模板示例），在该行末尾加 `<!-- VERSION_OK -->` 注释，hook 会跳过。

例：

```markdown
当前版本：见 CHANGELOG.md 顶部
上个版本 v0.2.0 做了字典重构 <!-- VERSION_OK -->
```

第二行因为引用历史决策，所以豁免；第一行用指针。

## 紧急绕过（不推荐）

```bash
git commit --no-verify -m "紧急修复"
```

**什么时候可以用 `--no-verify`**：
- hook 本身有 bug（临时跳）
- 真正紧急的修复（比如线上事故）

**不要绕过的场景**：
- 觉得 hook 烦 → 改规则或调整 hook，**不要绕过**（那等于把防线自己拆了）

## 如何调整

### 新增"声明性文件"
编辑 `pre-commit` 的 `DECLARATIVE_FILES` 数组 + 同步更新 `00_admin/文档同步点清单.md §1`。

### 加新检查项（比如检查路径死链）
在 `pre-commit` 里加新的 check 段 + 更新本 README "是什么"。

### 改豁免语法
改 `pre-commit` 里的 `grep -v "VERSION_OK"` 行 + 更新本 README "豁免机制"。

### 加新「文件联动规则」
编辑 `lib/sync-rules.sh` 调一次 `add_rule "<名字>" "<trigger ERE>" "<must 列表>" "<reason>" "must|action"`。规则原则:
- **must 模式** = 改了 trigger 文件 → must 列表里至少 1 个文件也要改（否则 warn）
- **action 模式** = 不查 must，仅输出 reason 提示（用于"改完跑某个脚本"这类提醒）
- 一定要同步更新 `CLAUDE.md §会话结束 §3 文件关联追踪表`（规则源是规则表，但人类查 CLAUDE.md）

## 中途随时查（不用等 commit）

```bash
bash bin/sync-check.sh             # 检查全部 working tree（包括 untracked）
bash bin/sync-check.sh --staged    # 只检查已 git add 的（模拟 pre-commit 行为）
bash bin/sync-check.sh <file1> ... # 指定文件
```

CC 会话中改完一组文件就跑一次，提早发现联动漏改。仅提示，不阻断。

## 卸载

```bash
git config --unset core.hooksPath
```

## 相关文件

- `00_admin/文档同步点清单.md` — 完整同步点清单 + Release Checklist + Onboarding Checklist
- `00_admin/2026-04-19_项目审查_backlog.md` — 发现本问题的审查报告（D22 / D23 / D25 / L11）
- `05_logs/raw/2026-04-19.md` — 发现 + 解决的原始记录（AC 素材）

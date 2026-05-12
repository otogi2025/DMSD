# DMSD Hooks（Git + CC PostToolUse）

## 是什么

DMSD 用了 **3 类 hook**（2026-05-04 itsuki 拍板补 CC PostToolUse hook 后升级 / 2026-05-11 加 graphify post-commit + post-checkout）：

### Git hook（commit 时触发）

`git commit` 前自动跑 3 件事（按这个顺序）：

1. **版本号一致性检查**（阻塞型，2026-04-19 加）— "声明性文件"（`CLAUDE.md` / `WIP.md` / `TODO.md` / `progress_overview.md`）**不能硬编码版本号**。单源真值 = `CHANGELOG.md` 顶部。其他文件用 "当前版本见 CHANGELOG" 指针。
2. **版本 bump 提醒**（非阻塞，2026-04-29 加）— 改了 `01_specs/` / `02_design/` / `03_dev/*_DESIGN_LOG` 时提醒检查 version-bump skill `§2 决策树`。
3. **文件联动提醒**（非阻塞，2026-05-04 加）— 改了某文件但联动文件没动 → 警告。规则表 = `lib/sync-rules.sh`，详细联动矩阵见 `.claude/skills/file-linkage/SKILL.md`。**配套**：`bin/sync-check.sh` = 中途随时手动跑（不用等到 commit）。

### ⭐ CC PostToolUse hook（5 条，CC 调 Write/Edit 时立刻并行触发，2026-05-04 深夜加）

**比 git pre-commit 早一步**，CC 在中途没 commit 也能拦各种漂移。同 matcher 下挂 5 条 hook（并行跑）：

#### A. `post-edit-sync-check.sh` — 文件联动检查 + demo scaffold 检测
- **18 条联动规则**（路径触发，详见 file-linkage skill）— 2026-05-08 从 12 条扩到 18 条:加 5 端反向「业务代码→自端 DESIGN_LOG」+ 端→共用层（Rule 14-19）+ Rule 3 system-features 必查列表加 ANDROID + ROLLCALL_DEVICE
- **demo scaffold 字眼检测**：iOS .swift / backend .py 改动 git diff 新增行如有 `demo|bypass|stub|fake|mock|hack` 字眼 → 提醒加到 `system_features.md` 末尾清单

#### B. `post-edit-memory-check.sh` — Memory 索引检查
- 触发条件：file_path 在 memory dir 且不是 MEMORY.md 自己
- grep MEMORY.md 看是否引用新文件 → 没有就提醒「补索引」 + 检查 frontmatter 完整性

#### C. `post-edit-japanese-comment-check.sh` — 中文铁律 / 日语注释扫描
- 触发条件：`.swift / .py / .kt / .ts / .tsx / .js / .jsx` 文件改动
- 提取新增内容（git diff ^+ 行 / untracked 全文）→ 找 `//` / `#` 注释里有 hiragana（U+3040-309F）/ katakana（U+30A0-30FF）字眼 → 提醒
- 出处：memory `feedback_code_comments_chinese_strict.md`（2026-05-03 itsuki 拍板）
- false positive 风险：`//` 出现在字符串字面量里（如 URL `https://...`）会误报，看上下文判断

#### D. `post-edit-timestamp-check.sh` — 声明性文件时间戳检查
- 触发条件：`WIP.md / TODO.md / progress_overview.md / 文档同步点清单.md / CHANGELOG.md` 改动
- 头部 30 行找 `YYYY-MM-DD` → 跟今天对比 → 不一致提醒「时间戳没更新」
- 没找到字段 → 提醒「考虑加最后更新字段」

#### E. `post-edit-version-hardcode-check.sh` — 版本号硬编码实时拦
- 触发条件：`CLAUDE.md / WIP.md / TODO.md / progress_overview.md` 改动
- 提取新增内容找 `vX.Y.Z` 模式行 + 行末没 `<!-- VERSION_OK -->` 豁免 → 提醒
- 比 git pre-commit 早一步拦（commit 前发现，不等 commit 才阻塞）

### ⭐ CC PreToolUse hook（1 条，CC 调 Bash 前触发，2026-05-04 加，2026-05-12 改 warn 模式）

#### F. `pre-bash-destructive-block.sh` — 破坏性命令**提醒**（warn 模式，不阻断）
- 触发条件：所有 Bash 命令（matcher="Bash"）
- 警告清单（命中后 CC 看到警告，但命令照跑）：
  - `rm -rf <非临时路径>`（白名单 /tmp / node_modules / DerivedData / dist / build）
  - `git reset --hard`
  - `git clean -f`
  - `git checkout -- ` / `git restore -- `
  - `git branch -D`
  - `git push --force` / `-f`
  - `git push origin :refs`（删 remote ref）
  - `rm` 涉及 `.git` 目录
- **2026-05-12 itsuki 拍板**：从 `exit 2`（block 拦死）改为 `exit 0` + JSON `additionalContext` 注入警告。理由：太严 — 临时文件 cleanup / 已授权操作都被拦，CC 必须每次解释，烦。
- 命中 → exit 0 + JSON additionalContext（"⚠️ 破坏性操作 / 强制反思 / 先跟 itsuki 确认"）→ CC 看到警告但命令不阻断
- CC 自觉性：看到警告**应该**停下来跟 itsuki 确认，**技术上**可以直接跑（hook 不再 block）
- 文件名保留 `pre-bash-destructive-block.sh`（避免改名引发 settings.json + README 等多处联动）

### ⭐ Git post-commit / post-checkout hook（graphify 知识图谱自动重建，2026-05-11 加）

#### G. `post-commit` — graphify AST 增量重建
- 触发时机：每次 `git commit` 后
- 干什么：检测改了哪些代码文件（git diff HEAD~1 HEAD）→ 在后台跑 graphify 的 AST 重抽（不调 LLM 不烧 token）→ 更新 `graphify-out/graph.json` + `GRAPH_REPORT.md`
- 安全性：rebase / merge / cherry-pick 期间会跳过；后台 `nohup` 跑不阻塞 commit
- doc / image 改了**不自动跑**（要手动 `/graphify --update`）

#### H. `post-checkout` — graphify 切分支后重建
- 触发时机：每次 `git checkout <branch>` 后
- 干什么：分支切了 → 文件树可能大变 → 重抽图谱

源代码：`00_admin/hooks/post-commit` / `00_admin/hooks/post-checkout`（graphify CLI 自动生成）。

### 测试方法

```bash
# 在 CC 内输入 /hooks 查看是否注册成功

# 手动 dry-run 测：
echo '{"tool_input":{"file_path":"/Users/kurekoduki/.claude/projects/-Users-itsuki-dev-DMSD/memory/test.md"}}' | bash 00_admin/hooks/post-edit-memory-check.sh
echo '{"tool_input":{"file_path":"/Users/kurekoduki/dev/DMSD/03_dev/backend/v1/app/models.py"}}' | bash 00_admin/hooks/post-edit-sync-check.sh
echo '{"tool_input":{"command":"git reset --hard"}}' | bash 00_admin/hooks/pre-bash-destructive-block.sh; echo "exit=$?"
```

### SessionStart hook（已删，2026-05-04 同日加同日删）

> itsuki 反问后判断启动时 git 状态扫描没价值（CC 自己 `git status` 就行 / itsuki 已知 repo 状态），把这段检查挪到 session-wrap skill §5.5.9 收尾段。`session-start-check.sh` 已删 / `.claude/settings.json` SessionStart hook 配置已删。

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

## ⚠️ graphify hook install 漂移注意（2026-05-11 踩坑记）

跑 `graphify hook install` 会**改 git `core.hooksPath`** 到它自己创建的 `.beads/hooks/` 目录，**覆盖 DMSD 原本设的 `00_admin/hooks/`** → DMSD 的 `pre-commit`（版本号 / bump / 联动 3 检查）整个失效。

**修法**：

```bash
# 1. 把 graphify 的 hook copy 进 DMSD 主 hook 目录
cp .beads/hooks/post-commit 00_admin/hooks/post-commit
cp .beads/hooks/post-checkout 00_admin/hooks/post-checkout
chmod +x 00_admin/hooks/post-commit 00_admin/hooks/post-checkout

# 2. 改回 hooksPath
git config core.hooksPath 00_admin/hooks

# 3. .beads/ 留着不删（万一 graphify hook uninstall 命令依赖它做 marker），.gitignore 里已加排除
```

**预防**：任何第三方工具的 install 命令跑完后立刻验证 — `git config --get core.hooksPath` 是不是还指向 `00_admin/hooks`。如果被改了，按上面修。

详细发现 + AC 叙事：`05_logs/raw/2026-05-11.md §D`。

## 相关文件

- `00_admin/文档同步点清单.md` — 完整同步点清单 + Release Checklist + Onboarding Checklist
- `00_admin/2026-04-19_项目审查_backlog.md` — 发现本问题的审查报告（D22 / D23 / D25 / L11）
- `05_logs/raw/2026-04-19.md` — 发现 + 解决的原始记录（AC 素材）
- `05_logs/raw/2026-05-11.md §D` — graphify 上线 + vendor 污染 + .beads 漂移发现（AC 素材）

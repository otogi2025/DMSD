# DMSD Git Hooks

## 是什么

`git commit` 前自动检查"声明性文件"（`CLAUDE.md` / `WIP.md` / `TODO.md` / `progress_overview.md`）**没有硬编码版本号**。

单源真值 = `CHANGELOG.md` 顶部。其他文件用 "当前版本见 CHANGELOG" 指针。

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

## 卸载

```bash
git config --unset core.hooksPath
```

## 相关文件

- `00_admin/文档同步点清单.md` — 完整同步点清单 + Release Checklist + Onboarding Checklist
- `00_admin/2026-04-19_项目审查_backlog.md` — 发现本问题的审查报告（D22 / D23 / D25 / L11）
- `05_logs/raw/2026-04-19.md` — 发现 + 解决的原始记录（AC 素材）

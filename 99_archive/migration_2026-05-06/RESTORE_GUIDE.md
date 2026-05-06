# 新机迁移恢复指南（2026-05-06 备份）

> **写给：新机上的 Claude Code（你）+ itsuki**
>
> **触发条件**：itsuki 在新 Mac 上 clone DMSD 后，对你说「读 `99_archive/migration_2026-05-06/RESTORE_GUIDE.md`，按里面恢复」。
>
> **背景**：itsuki 把 Mac mini 退货换新机。退货前在原机做了完整 push + 备份。本文件让新机恢复"原 Mac 状态"。
>
> **配套文档**：环境从零搭起来跑 `00_admin/MAC_MINI_SETUP.md` §1-§7（装 brew / Xcode / Android Studio / Claude Code 等）；本文件 = §8（恢复 Claude memory + scheduled + settings）。
>
> **顺序**：先跑完 `MAC_MINI_SETUP.md`（基础工具齐全），再跑本文件（数据恢复）。

---

## 0. 给新机 CC 的开场白

你好 — itsuki 是中国留日高中生，编程零基础，用中文交流，每个英文/缩写第一次出现要翻译。他目标筑波大学 AC 入試 2027。本项目 DMSD（Dormitory Management System Digitalization）是核心 AC 叙事项目，Tomoshibi（灯火）是面向用户的系统名。

执行本恢复步骤时：
- 每步开始前简短说"正在做什么 / 为什么"
- 跑完一步打 ✅ 给 itsuki 看
- 报错就停下来分析根因，**不要重试 / 不要跳过**
- 不要 push / tag / commit（这是恢复操作，不是开发动作）
- 路径里所有 `/Users/itsuki/` 用 `$HOME` 替代或先 `echo $HOME` 确认实际路径

---

## 1. 备份内容总览

本目录 `99_archive/migration_2026-05-06/` 包含 4 类备份：

| 子目录 | 内容 | 恢复目标 |
|---|---|---|
| `dmsd-claude-memory/` | 37 个 DMSD memory `.md`（feedback / project / user 全套） | `~/.claude/projects/-Users-itsuki-dev-DMSD/memory/` |
| `global-claude-memory/` | 3 个全局 memory（`MEMORY.md` / `user_profile.md` / `reference_dmsd.md`） | `~/.claude/projects/-Users-itsuki/memory/` |
| `claude-settings/` | `~/.claude/settings.json` + `settings.local.json` | `~/.claude/` 顶层 |
| `claude-scheduled/` | 4 个 quota-reset 提醒 `SKILL.md` | `~/Documents/Claude/Scheduled/` |

**iCloud 双备份**（自动同步，不在 git，但你可对照确认完整性）：
- `~/Library/Mobile Documents/com~apple~CloudDocs/_claude_memory_backup/DMSD-memory-2026-05-06.zip` — memory 整包
- `~/Library/Mobile Documents/com~apple~CloudDocs/_claude_memory_backup/DMSD-sessions-2026-05-06.zip` — 25 个 `.jsonl` 会话历史（26MB，AC 叙事原始素材）

---

## 2. 恢复步骤（按顺序）

### 2.1 验证 git 状态干净

```bash
cd ~/dev/DMSD
git status                        # 应该 clean，新 clone
git log -1 --format="%H %s"       # 最新 commit 应该是 "chore(migration): ..."
git log @{u}..HEAD 2>&1 | wc -l   # 应该输出 0（远端=本地）
```

✅ 验证：3 个命令都符合期望。如果不符合 — 停下来问 itsuki。

### 2.2 安装 git hooks

```bash
bash 00_admin/hooks/install.sh
```

预期输出：`✅ DMSD hooks 已安装` + `core.hooksPath = 00_admin/hooks`。

✅ 验证：

```bash
git config --get core.hooksPath   # 应该输出 00_admin/hooks
ls -l 00_admin/hooks/pre-commit   # 应该可执行（rwxr-xr-x）
```

### 2.3 恢复 DMSD memory（37 个）

```bash
mkdir -p ~/.claude/projects/-Users-itsuki-dev-DMSD/memory
cp -p 99_archive/migration_2026-05-06/dmsd-claude-memory/*.md \
       ~/.claude/projects/-Users-itsuki-dev-DMSD/memory/
ls ~/.claude/projects/-Users-itsuki-dev-DMSD/memory/ | wc -l
```

✅ 验证：最后一个命令应该输出 `37`。

### 2.4 恢复全局 memory（3 个）

```bash
mkdir -p ~/.claude/projects/-Users-itsuki/memory
cp -p 99_archive/migration_2026-05-06/global-claude-memory/*.md \
       ~/.claude/projects/-Users-itsuki/memory/
ls ~/.claude/projects/-Users-itsuki/memory/ | wc -l
```

✅ 验证：最后一个命令应该输出 `3`。

### 2.5 恢复 Claude 用户级 settings

```bash
cp -p 99_archive/migration_2026-05-06/claude-settings/settings.json       ~/.claude/
cp -p 99_archive/migration_2026-05-06/claude-settings/settings.local.json ~/.claude/
```

✅ 验证：

```bash
cat ~/.claude/settings.json        # 应该看到 "defaultMode": "auto" + Swift LSP plugin
cat ~/.claude/settings.local.json  # 应该看到 5 条 brew/npm 权限白名单
```

### 2.6 恢复 Scheduled tasks（4 个 quota reset 提醒）

```bash
mkdir -p ~/Documents/Claude/Scheduled
cp -rp 99_archive/migration_2026-05-06/claude-scheduled/* \
       ~/Documents/Claude/Scheduled/
ls ~/Documents/Claude/Scheduled/
```

✅ 验证：应该看到 4 个目录 `claude-quota-reset-0400/0nnnn/...`

### 2.7 GitHub CLI 重新登录（token 不会跨机迁移）

```bash
gh auth status   # 应该报 "not logged in" 或类似
gh auth login    # 选 GitHub.com → HTTPS → Login with browser
```

按提示打开浏览器登 GitHub `otogi2025`，授权 scopes: `gist`, `read:org`, `repo`, `workflow`。

✅ 验证：

```bash
gh auth status   # 应该看到 "Logged in to github.com account otogi2025"
gh repo view otogi2025/DMSD --json name,visibility   # 能拉到信息 = OK
```

### 2.8 iCloud Drive 同步等待（非命令行步骤）

打开 Finder → 左侧栏「iCloud Drive」→ 等所有 ☁️ 图标变成实心（=已下载到本地）。

特别确认这 3 个路径下文件齐全：
- `02_学习与知识/升学/AC/筑波大学 AC入試 準備/`（AC 文件家族 —「03_素材_候选」/「04_素材_成品」/「05_产出」）
- `04_Dev/Projects/_deprecated_AC_DMSD_旧镜像_至2026-04-24/`（旧镜像，参考用）
- `_claude_memory_backup/`（含 `DMSD-memory-2026-05-06.zip` + `DMSD-sessions-2026-05-06.zip`）

✅ 验证：3 个路径在 Finder 中可见且无 `.icloud` 占位文件。

### 2.9 iCloud Keychain 启用（让 Apple Dev 证书自动同步）

系统设置 → Apple 账户 → iCloud → 钥匙串 → **启用**。

启用后等 5-10 分钟同步。Xcode 打开后应该能看到 `Apple Development: LIU YIFEI (S7P4VDJSS7)` 证书自动出现。

如果没出现：Xcode → Settings → Accounts → 加 Apple ID → Manage Certificates → Apple Development（点 +）。

### 2.10 Tomoshibi-iOS 独立 repo 处理（仅当要用 Cloud Agent 才做）

**背景**：DMSD 主 repo 是单源真值；Tomoshibi-iOS 是独立 repo，**专给 Anthropic Cloud Agent 用**（agent 跑 Tomoshibi-iOS 拿不到 DMSD 文件，需要用 `bin/sync-ios-refs.sh` 把 DMSD 设计文档复制到 Tomoshibi-iOS/refs/）。

**远端最新 commit 是 2026-04-23**（备份当天 5-06 算，已落后 13 天）。最近所有 iOS 工作都在 DMSD 主 repo `03_dev/student_ios/v1/`。

如果你（itsuki）打算用 Cloud Agent 跑 iOS routine，新机第一次启动前要做：

```bash
cd ~/dev
gh repo clone otogi2025/Tomoshibi-iOS TomoshibiiOSApp
cd ~/dev/DMSD
bash bin/sync-ios-refs.sh        # 把 DMSD 设计文档复制到 Tomoshibi-iOS/refs/
cd ~/dev/TomoshibiiOSApp
git status                        # 看 refs/ 下有什么变化
git add refs/
git commit -m "sync(refs): from DMSD 2026-05-06 状态"
git push
```

如果暂时不用 Cloud Agent — **可以跳过本步骤**，等真要用时再做。

### 2.11 Android repo 4 个 worktree（如果还需要 4 路并行开发）

```bash
cd ~/dev/TomoshibiAndroidApp   # 这个 repo 你已经 clone（应该跟 DMSD 同时 clone）
git worktree list              # 应该只有 main
# 4 个 feature/* branch 已经在远端，需要时再开 worktree：
git worktree add ../tomoshibi-A feature/A-infra
git worktree add ../tomoshibi-B feature/B-auth-home
git worktree add ../tomoshibi-C feature/C-apply-mypage
git worktree add ../tomoshibi-D feature/D-community
```

如果不打算 4 路并行 — **跳过**。Branch 数据在远端永远不丢。

### 2.12 Backend 重建（如要跑后端）

```bash
cd ~/dev/DMSD/03_dev/backend/v1
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # 如果有 requirements.txt
cp .env.example .env               # 编辑 .env 填本地 PostgreSQL 连接
```

注：原机也没有真 `.env`，demo 阶段 backend 没真起来过。如果新机要真起来，照 `.env.example` 填值 + 装 PostgreSQL（`brew install postgresql@16`）。

---

## 3. 验证清单（恢复完成检查）

在 `~/dev/DMSD/` 下跑：

```bash
# 1. memory 完整性
ls ~/.claude/projects/-Users-itsuki-dev-DMSD/memory/ | wc -l   # 期望 37
ls ~/.claude/projects/-Users-itsuki/memory/ | wc -l            # 期望 3

# 2. settings 在位
test -f ~/.claude/settings.json && echo OK || echo MISSING
test -f ~/.claude/settings.local.json && echo OK || echo MISSING

# 3. scheduled 在位
ls ~/Documents/Claude/Scheduled/ | wc -l   # 期望 4

# 4. git hooks 装上
git config --get core.hooksPath   # 期望 00_admin/hooks

# 5. gh auth 通
gh auth status 2>&1 | grep "Logged in" && echo OK || echo MISSING

# 6. 远端 = 本地
git log @{u}..HEAD 2>&1 | wc -l   # 期望 0
```

全部通过 → 恢复完成 ✅

---

## 4. 常见问题

**Q: memory 文件复制后 CC 还是不认得我**
A: CC 会在新会话时自动加载 memory 索引（`MEMORY.md`）。如果不识别 — 检查 `~/.claude/projects/-Users-itsuki-dev-DMSD/memory/MEMORY.md` 是否存在 + 内容跟备份一致。

**Q: gh auth login 浏览器打不开**
A: 命令行会显示 8 位代码 + URL，手动复制 URL 到任何浏览器打开 + 输入代码即可。

**Q: iCloud 同步卡住**
A: 系统设置 → Apple 账户 → iCloud → iCloud Drive → 关掉再开。重新登录。

**Q: 我能不能直接从 iCloud zip 恢复 memory（不走 git）**
A: 可以。`unzip ~/Library/Mobile\ Documents/com~apple~CloudDocs/_claude_memory_backup/DMSD-memory-2026-05-06.zip -d ~/.claude/projects/-Users-itsuki-dev-DMSD/`。这是 git 方案的 fallback。

**Q: 旧 jsonl 会话历史要不要恢复到 ~/.claude/projects/.../**
A: 不需要恢复到本地路径 — 那是 Claude Code 运行时自己生成的（每次会话写一个 jsonl）。zip 在 iCloud 是 AC 叙事的原始素材保存，需要时直接解压看。**新机不要把它们解压回 `~/.claude/projects/...`，会跟新会话冲突**。

---

## 5. 完成后清理（可选）

恢复全部成功 + 你确认新机能正常工作后：

```bash
# 选项 A: 保留 99_archive/migration_2026-05-06/ 不删（占盘 ~250KB，作为历史归档）— 推荐
# 选项 B: 删除节省空间（不推荐，因为下次换机有参考价值）
# rm -rf 99_archive/migration_2026-05-06/
```

iCloud 的 zip 也可以保留作为冷备份（26MB session + 75KB memory）。

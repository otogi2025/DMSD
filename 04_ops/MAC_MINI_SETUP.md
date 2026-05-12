# Mac mini 首次启动 setup 指南

> **本文件是给 Claude Code 看的执行清单。**
>
> itsuki 在 Mac mini 上 clone 完 DMSD 仓后，第一句话对 CC 说：「读 `00_admin/MAC_MINI_SETUP.md`，按里面跑完所有步骤」。
>
> CC 要做的事：按 §1-§7 顺序执行，每完成一步打 ✅ 给 itsuki 看；遇到错误停下来问 itsuki，不要硬冲。
>
> **背景**：itsuki 把原 Mac 给别人，换到 Mac mini。原 Mac 上所有未 commit 工作已经 push（commit `debcb07`），Claude memory 28 个文件已备份到 iCloud。本文件让 Mac mini 跟原 Mac 一样能跑。
>
> **🆕 2026-05-06 第二次迁移注记**（Mac mini → 新机）：从这次起 Claude memory + settings + scheduled 备份**首选走 git 内快照**（路径 `99_archive/migration_2026-05-06/`，clone 后立即可用，不用等 iCloud 同步）。本文件 §5 的 iCloud 路径降级为 **fallback**。新机走完 §1-§4 后，**直接读 `99_archive/migration_2026-05-06/RESTORE_GUIDE.md` §2 恢复数据**，跳过本文件 §5。

---

## 0. 给 CC 的开场白

你好 — itsuki 是中国留日高中生，编程零基础，用中文交流，每个英文/缩写第一次出现要翻译。他目标筑波大学 AC 入試 2027。本项目 DMSD（Dormitory Management System Digitalization）是核心 AC 叙事项目，Tomoshibi（灯火）是面向用户的系统名。

**你做这个 setup 时**：
- 每步执行前简短告诉 itsuki "正在做什么 / 为什么做"
- 每个命令解释作用（特别是 brew / npm / venv 这种英文词）
- 跑完一步打 ✅，进下一步
- 命令报错了停下来分析原因，不要重试或者跳过
- 不要 push / tag / 创建 commit（除非 itsuki 明示）
- 如果 itsuki home 路径不是 `/Users/kurekoduki`，把命令里所有路径替换成实际路径（用 `echo $HOME` 确认）

---

## 1. 装基础工具（约 30 分钟，主要是等 Xcode 下载）

### 1.1 Homebrew（包管理器 — 翻译: 帮你装命令行工具的工具，类似 Mac 上的"App Store 命令行版"）

```bash
# 检查是否已装
which brew

# 没装的话执行这个
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 装完后按提示把 brew 加到 PATH（Apple Silicon Mac mini 一般要跑这两行）
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# 验证
brew --version
```

✅ 验证标准：`brew --version` 输出版本号

### 1.2 Python / Node / Git

```bash
brew install python@3.11 node git
```

验证：

```bash
python3 --version    # 期望 3.11.x
node --version       # 期望 v20+
git --version        # 期望 2.40+
```

### 1.3 Xcode 26（最大、最慢，先开始下载）

```bash
# 这个不能用 brew，要去 App Store
open "macappstore://apps.apple.com/app/xcode/id497799835"
```

→ App Store 点「获取」/「下载」/「打开」（约 12 GB，1-2 小时）

下载完 **必须开一次 Xcode** 让它装 Command Line Tools。Xcode 启动后会弹窗"Install additional components" → 同意 + 输 Mac 密码。

验证：

```bash
xcodebuild -version    # 期望 Xcode 26.x
```

### 1.4 Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

验证：

```bash
claude --version
```

---

## 2. 配 git 身份 + GitHub 凭证

### 2.1 配身份

```bash
git config --global user.name "itsuki"
git config --global user.email "otogi2025@gmail.com"
```

### 2.2 GitHub 登录方式 — 用 Personal Access Token（PAT — 翻译: 个人访问令牌，是 GitHub 给你的密码替代品，比真密码安全）

第一次 push 时，git 会问用户名 + 密码：
- 用户名：`otogi2025`
- 密码：**不是真密码！是 PAT**

如果 itsuki 找不到 PAT，去这个网址生成新的：
- https://github.com/settings/tokens
- 点「Generate new token (classic)」
- Note: `Mac mini DMSD`
- Expiration: 选 90 天或更久
- Scopes: 勾选 `repo`（最重要）+ `workflow`
- 生成后**复制下来**（只显示一次！）

把 PAT 存到 macOS 钥匙串（下次自动登录）：

```bash
git config --global credential.helper osxkeychain
```

---

## 3. clone DMSD 仓

```bash
mkdir -p ~/dev
cd ~/dev
git clone https://github.com/otogi2025/DMSD.git
cd DMSD
```

第一次 push / pull 会要 GitHub 用户名 + PAT，输一次后钥匙串记住，以后不用再输。

---

## 4. 装项目级配置

### 4.1 pre-commit hook（防止文档版本号漂移）

```bash
cd ~/dev/DMSD
bash 00_admin/hooks/install.sh
```

验证：

```bash
ls .git/hooks/pre-commit
# 期望存在
```

### 4.2 备份的全局 CLAUDE.md（如果 itsuki 之前备份了）

检查 iCloud 备份是否已同步过来：

```bash
ls "$HOME/Library/Mobile Documents/com~apple~CloudDocs/_claude_memory_backup/" 2>/dev/null
```

如果有 `global_CLAUDE.md` 文件：

```bash
mkdir -p ~/.claude
cp "$HOME/Library/Mobile Documents/com~apple~CloudDocs/_claude_memory_backup/global_CLAUDE.md" ~/.claude/CLAUDE.md
```

---

## 5. 恢复 Claude memory（28 个文件 — iCloud fallback 方案）

> **2026-05-06 起首选不是这条路径**。新机 clone 完 DMSD 后直接读 `99_archive/migration_2026-05-06/RESTORE_GUIDE.md` §2，里面包含 memory + settings + scheduled 一站式恢复。
>
> 本 §5 保留作为 **iCloud fallback**：当 git 内快照丢失 / 损坏时使用。

### 5.1 等 iCloud 同步

Mac mini 第一次登 Apple ID 后，iCloud Drive 同步**不是瞬时的**（第一次同步 28 个小文件大概几分钟到几十分钟）。

检查同步是否完成：

```bash
# 列 iCloud 里的备份文件夹
ls "$HOME/Library/Mobile Documents/com~apple~CloudDocs/_claude_memory_backup/"
```

期望看到 `DMSD-memory-2026-05-02/` 文件夹。如果文件名末尾日期更新（itsuki 之后又备份过），用最新那个。

### 5.2 数文件数确认完整

```bash
ls "$HOME/Library/Mobile Documents/com~apple~CloudDocs/_claude_memory_backup/DMSD-memory-2026-05-02/" | wc -l
# 期望 28（如果 < 28 表示 iCloud 还没同步完，等几分钟再试）
```

### 5.3 拷回 ~/.claude/

```bash
mkdir -p ~/.claude/projects/-Users-kurekoduki-dev-DMSD
cp -R "$HOME/Library/Mobile Documents/com~apple~CloudDocs/_claude_memory_backup/DMSD-memory-2026-05-02" \
      ~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory
```

⚠️ **关键路径检查**：上面命令假设 Mac mini 上的 home 路径也是 `/Users/kurekoduki`。

确认：

```bash
echo $HOME
# 期望 /Users/kurekoduki
```

如果**不是** `/Users/kurekoduki`（比如新 Mac 上用户名不同变成了 `/Users/itsuki`），所有命令里的路径要替换：
- `~/.claude/projects/-Users-kurekoduki-dev-DMSD/` → `~/.claude/projects/-Users-itsuki-dev-DMSD/`（或对应你新 home 的写法）

### 5.4 验证 memory 加载

```bash
ls ~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/ | wc -l
# 期望 28
ls ~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/MEMORY.md
# 期望存在
```

之后开 Claude Code 会话时，问 CC「我是谁」，它应该答出"itsuki / 中国留日高中生 / 筑波 AC 2027"。

---

## 6. 装项目依赖

### 6.1 backend Python 环境

```bash
cd ~/dev/DMSD/03_dev/backend/v1
python3 -m venv .venv          # 建虚拟环境（venv — 翻译: 项目独立的 Python 环境，避免污染系统 Python）
source .venv/bin/activate       # 激活 venv（命令行前面会出现 (.venv) 标识）
pip install -r requirements.txt # 装依赖（约 1-2 分钟）
python seed.py                  # 生成 demo 数据库（含 demo 学生 + 老师种子数据）
```

验证 backend 能跑：

```bash
uvicorn app.main:app --reload
# 浏览器打开 http://localhost:8000/docs 看到 Swagger UI = 成功
# Ctrl+C 关掉
```

### 6.2 teacher_web Node 环境

```bash
cd ~/dev/DMSD/03_dev/teacher_web/v1
npm install      # 装依赖（约 1-2 分钟）
```

验证 teacher_web 能跑：

```bash
npm run dev
# 浏览器打开 http://localhost:5173 看到登录页 = 成功
# Ctrl+C 关掉
```

### 6.3 iOS 项目

打开 Xcode（不能命令行直接验证，要 itsuki 点）：

```bash
open ~/dev/DMSD/03_dev/student_ios/v1/TomoshibiApp.xcodeproj
```

让 itsuki 在 Xcode 里：
1. 第一次开会要登 Apple ID（签名用 — Apple Developer 账号免费档够用）
2. 顶部 scheme 切到 `TomoshibiAppDemo`
3. 选 iPhone 17 Pro Simulator
4. ⌘+R 跑起来
5. 看到 Login 屏 = 成功

如果要跑 production 版（无 demo 数据）：scheme 切 `TomoshibiApp`，再 ⌘+R。

---

## 7. 验证清单（全跑完打 ✅）

| 项 | 怎么验证 | 通过标准 |
|---|---|---|
| Homebrew | `brew --version` | 输出版本号 |
| Python | `python3 --version` | 3.11.x |
| Node | `node --version` | v20+ |
| Git | `git --version` | 2.40+ |
| Xcode | `xcodebuild -version` | 26.x |
| Claude Code | `claude --version` | 输出版本 |
| Git 凭证 | `cd ~/dev/DMSD && git pull` | 不报错 |
| pre-commit hook | `ls ~/dev/DMSD/.git/hooks/pre-commit` | 存在 |
| Claude memory | `ls ~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/ \| wc -l` | 28 |
| backend | `uvicorn app.main:app --reload` | http://localhost:8000/docs 打得开 |
| iOS demo | Xcode Run TomoshibiAppDemo | Simulator 启动 + 看到 Login |
| iOS production | Xcode Run TomoshibiApp | 同上 |
| teacher_web | `npm run dev` | http://localhost:5173 打得开 |
| iCloud AC 目录 | `ls "~/Library/Mobile Documents/com~apple~CloudDocs/02_学习与知识/升学/AC/"` | 看到 AC 目录 |

---

## 8. 完成后告诉 itsuki

```
✅ Mac mini 全部就位。
- 装了哪些工具：[列表]
- backend / iOS / teacher_web 都能跑
- Claude memory 28 个文件加载完成
- 现在跟原 Mac 一样能开发了

如果验证清单里某项没通过，告诉我哪一项 + 具体报错。
```

---

## 9. 常见问题

### Q: brew install 卡住 / 失败

A: 网络问题（中国到 Homebrew 镜像慢）。换镜像：
```bash
git -C "$(brew --repo)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git
```

### Q: Xcode 下载到一半中断

A: App Store 自动续传，再点开就行。如果 App Store 卡死，去 https://developer.apple.com/download/all/ 手动下载 Xcode .xip 文件（要 Apple ID 登录）。

### Q: git push 反复要密码

A: 钥匙串没保存 PAT。手动加：
- 打开「钥匙串访问」app
- 找到 `github.com` 条目
- 改密码 → 输 PAT → 保存

### Q: Claude memory 28 文件少几个

A: iCloud 同步没完。等 5-10 分钟再 `ls` 看，或者打开 Finder → iCloud Drive → `_claude_memory_backup/DMSD-memory-2026-05-02/` 强制触发同步。

### Q: backend 跑 `pip install -r requirements.txt` 报 `bcrypt` 编译错误

A: macOS 缺 Rust 工具链。装：
```bash
brew install rust
```
然后重新 `pip install -r requirements.txt`。

### Q: iOS `xcodebuild` 报 `No such module 'SwiftUI'`

A: Xcode Command Line Tools 没装好。强制装：
```bash
sudo xcode-select --install
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
```

---

## 10. setup 完成后 itsuki 接下来要做的事（不在本文档范围）

读 `00_admin/WIP.md` 看当前任务进度。

`00_admin/TODO.md` 是完整待办清单。

下一阶段重点：
- App Icon 修改（Apple Icon Composer 路线，5-02 决定）
- iOS↔backend 字段对齐（已 commit `4be8121` 落地，验证联调）
- 给 Claude Design 发 Android Round 1 包（5-01 准备好）

---

**END** — 跑完本文档 → Mac mini 跟原 Mac 一样能开发。

---

## 附录: 历次迁移备份清单

| 备份日期 | 备份位置 | memory 数 | 备注 |
|---|---|---|---|
| 2026-05-02 | iCloud `_claude_memory_backup/DMSD-memory-2026-05-02/` | 28 | 原 Mac → Mac mini 第一次迁移 |
| 2026-05-06 | git `99_archive/migration_2026-05-06/` + iCloud `_claude_memory_backup/DMSD-{memory,sessions}-2026-05-06.zip` | 37 | Mac mini → 新机第二次迁移；首次 git 内快照 |

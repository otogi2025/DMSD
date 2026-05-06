# 给 itsuki 自己读的换机指南（2026-05-06）

> 这份是给你自己读的大白话版。技术细节的版本是同目录下 `RESTORE_GUIDE.md`（那份是给新机的 Claude Code 看的执行清单）。
>
> 你只要做下面 3 件事 → 新机就能继续。

---

## 第 1 件事：退 Mac mini 之前确认这 3 个

**1) iCloud Drive 全部上传完毕**

- Finder 打开「iCloud Drive」
- 看左侧栏图标，所有 ☁️（云朵）图标都变成实心 → 表示已经上传到云
- 重点检查这两个目录有没有「☁️ 还在」的文件：
  - `02_学习与知识/升学/AC/筑波大学 AC入試 準備/`（你的 AC 文件家族 — 03_素材_候选 / 04_素材_成品 / 05_产出 都在这里）
  - `_claude_memory_backup/`（应该有 `DMSD-memory-2026-05-06.zip` 和 `DMSD-sessions-2026-05-06.zip`）

如果有些文件还是 ☁️，不要关机 — 等同步完。

**2) iCloud 钥匙串开着**

- 系统设置 → Apple 账户 → iCloud → 钥匙串 → 是「启用」状态
- 这一步是为了让 Apple Developer 证书自动同步到新机（`Apple Development: LIU YIFEI` 那个）
- 否则新机 Xcode 要重新申请证书，麻烦

**3) GitHub 上看一眼这两个 repo 是最新的**

打开浏览器：
- https://github.com/otogi2025/DMSD — 顶部应该看到最新 commit 是「chore(migration): ...」
- https://github.com/otogi2025/Tomoshibi-Android — 顶部看到 4 个分支（main + feature/A-D），最新 commit 是图标更新

如果看不到最新的 — 告诉我，我没 push 成功。

---

## 第 2 件事：拿到新 Mac 后干什么

**装基础工具**（约 1 小时，主要等 Xcode 下载）：

打开终端（Terminal.app），按顺序敲：

```bash
# 装 Homebrew（这个是命令行的 App Store）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 装 git + node + python（开发用）
brew install git node python@3.11 gh

# 装 Claude Code
npm install -g @anthropic-ai/claude-code
```

然后去 App Store 装 Xcode（搜「Xcode」点获取，约 12GB 要等 1-2 小时）+ Android Studio（也是 App Store）+ VS Code（App Store 或 [code.visualstudio.com](https://code.visualstudio.com)）。

**clone 项目**：

```bash
mkdir -p ~/dev
cd ~/dev
gh auth login                    # 浏览器登 GitHub otogi2025
gh repo clone otogi2025/DMSD
gh repo clone otogi2025/Tomoshibi-Android TomoshibiAndroidApp
```

---

## 第 3 件事：让 CC 帮你把数据恢复

打开终端：

```bash
cd ~/dev/DMSD
claude
```

CC 启动后，**第一句对它说**：

> 读 `99_archive/migration_2026-05-06/RESTORE_GUIDE.md`，按里面 §2 把数据恢复

CC 会按那份文档一步步：
- 装 git hook（`bash 00_admin/hooks/install.sh`）
- 把 memory（37 个 .md）拷回 `~/.claude/projects/...`
- 把 settings 拷回 `~/.claude/`
- 把 scheduled 拷回 `~/Documents/Claude/Scheduled/`
- 验证全套到位

整个过程大概 10 分钟。

---

## 完成后怎么知道恢复 OK 了

让 CC 跑这一句验证：

```bash
ls ~/.claude/projects/-Users-itsuki-dev-DMSD/memory/ | wc -l
```

输出 **37** = OK ✅

或者更简单 — 问 CC「我是谁」，它能答出「itsuki / 中国留日高中生 / 筑波 AC 2027 / DMSD 项目」就 OK。

---

## 注意事项

**新机用户名不一定还是 `itsuki`**：

- 如果新 Mac 的家目录是 `/Users/liuyifei` 或别的 — CC 要把所有路径里的 `itsuki` 替换
- CC 的 memory 路径会变成 `~/.claude/projects/-Users-XXX-dev-DMSD/memory/`（XXX = 新用户名）
- 这一步 CC 自己会处理（RESTORE_GUIDE 里有提醒），你不用管

**iCloud 同步没完不要急着开始恢复**：

- 新机第一次登 Apple ID 后，iCloud Drive 同步是渐进的（几分钟到几小时取决于文件量）
- 在等 iCloud 的同时可以先装工具 + clone repo
- AC 素材没同步完不影响 git 内备份恢复（git 备份是自包含的）

**如果某一步卡住**：

不要硬冲，把报错截图发给我（或下次会话直接告诉 CC）。重启 / 重装 / 删配置常常**比直接修问题要糟**。

---

## 关键文件位置速查

| 你要的东西 | 在哪 |
|---|---|
| 项目代码 | `~/dev/DMSD` + `~/dev/TomoshibiAndroidApp` |
| AC 文件家族 | iCloud Drive `02_学习与知识/升学/AC/筑波大学 AC入試 準備/` |
| 跟 CC 的对话历史 | iCloud Drive `_claude_memory_backup/DMSD-sessions-2026-05-06.zip`（解开看） |
| Memory 备份 | git 内 `99_archive/migration_2026-05-06/dmsd-claude-memory/` |
| 旧 DMSD 镜像 | iCloud Drive `04_Dev/Projects/_deprecated_AC_DMSD_旧镜像_至2026-04-24/`（参考用，已 deprecated） |

---

**就这些。退货前确认 3 件 → 新机做 3 件 → 验证 1 个数字 → 完成**。

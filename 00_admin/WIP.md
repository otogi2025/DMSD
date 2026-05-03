# 当前工作状态 (Work In Progress)

> **本文件 = Claude Code 的「当下书签 + 多会话协调」清单。短小为美。**
>
> **职责分工（重要 — 别再重叠）**:
>
> | 文件 | 内容 | 给谁看 |
> |---|---|---|
> | **WIP.md（本文件）** | 当下书签 + 最近 5 次会话 1-2 行总结 + 多会话占用 + 阻塞项 | CC（每次会话开始读全文）|
> | **TODO.md** | **所有未完成事项的完整 backlog**（真值）| itsuki + CC（每次会话开始扫顶部 200 行）|
> | **progress_overview.md** | 长期章节目录（稳定，每次 close 版本时更新）| itsuki + 教授读 |
> | **CHANGELOG.md** | 已发布版本编年史 | 全部读者 |
> | **commit history** | 每次改动的细节 | git log 可查 |
>
> **铁律**：未完成的事**只写在 TODO.md**。本文件**绝不**复述 TODO 的内容。
>
> - **会话开始**: CC 读本文件全文 + `TODO.md` 顶部 200 行 + `git status`
> - **会话结束**: CC 更新「最近会话」+「多会话占用」；新增的 backlog **写到 TODO.md** 不写这里

---

**当前版本**: v0.8.0 <!-- VERSION_OK -->
**版本管理 SOP**: `00_admin/版本管理SOP.md`（CC 改 spec / 02_design / 03_dev 主体后必读 §2 决策树）

---

## 🎯 当前焦点

**当前版本之后的阶段**（版本号见 `CHANGELOG.md` 顶部） — 三端代码层启动完毕，下一步重点：
1. 老师公告 4 端实装（iOS + Android + Web + Backend）— spec 已落 `system_features.md §7.15`
2. 学生注册码 v1.0 实装（4 端 spec 已就位 2026-05-03 上午别会话）
3. 文档欠债：`progress_overview.md` 章节级里程碑刷新（4-17 之后没动）

→ 完整 backlog 看 `TODO.md`。

---

## 📜 最近会话（最多保留 5 条，老的删 — 详细历史看 commit log + raw/）

### 2026-05-03 下午+晚上 by [Mac-mini-Opus 4.7]

**主题**：iOS Tomoshibi 集中改 + 老师公告 spec + MyPage 方案 B + 收尾流程升级

- iOS 修：真机装机签名死锁修复（删 `.pbxproj` 3 处 `CODE_SIGNING_ALLOWED = NO`）/ GlassSheet 底部留白 / AI 头像位置 + loading state（5.5s 兜底覆盖 cold start）/ 行事予定日历 cell layout 重构 + 修「2,026」逗号 / 巴士入口统一 / MyPage 方案 B 大改（学習/点呼/減点 Card 化置顶）
- 文档：老师公告 §7.15 完整 spec（12 子节、Apple Intelligence on-device 推理路线）/ CLAUDE.md §会话结束 大改 + 4 条 itsuki 新规则 / IOS_DESIGN_LOG §5 重写方案 B + §12 工程修复集 / linter 加 §3.9-3.11
- AC dump：`raw/2026-05-03.md §12-§19` 详细
- xcodebuild 全程 BUILD SUCCEEDED
- **未提交改动**（这次会话开始时 git status 已显示）：backend `models.py` / `routers/study.py` / `schemas.py` / `alembic/versions/c3d4e5f6a7b8_add_study_absence_period.py`（新 migration） / iOS `ApplyStubs.swift` / `StayListStubs.swift` / `AppStore.swift` / `StudyAPI.swift` / `NetworkModels.swift` / `.pbxproj.bak` ×2

### 2026-05-03 上午（3 ラウンド累積）by [Mac-mini-Opus 4.7]

**主题**：Tomoshibi Android 8 项 iOS 对齐 + 2 轮反馈迭代

- 累積 3 commit（`0cb29a0` 主体 / `77bc7d2` 中央按钮 icon+gradient / `1855192` 中央按钮位置+RollCallSheet 重写）13 files +1018 -384，**全部本地未 push**
- BottomTabs / ApplicationsScreen / ApplyNew / AccountScreen 完全重写 / TopRollBar / LoginScreen demo bypass / Routes
- emulator click 卡住 workaround：`uiautomator dump` 找按钮真实 bounds
- **残**：Stage 1 升级（plan `~/.claude/plans/a-ios-app-immutable-peach.md`）/ push 3 commit 待 itsuki 明示

### 2026-05-02 晚 by [Mac-主会话]

**主题**：🎉 v0.8.0 close + push + tag

- commit `41f6191` + tag `v0.8.0` 已推 GitHub
- 自 v0.7.0 以来 31 commit 全收
- v0.8.0 主题：三端代码层全启动（Android Compose bootstrap + 10 屏 / iOS 网络层 + AppStore 切真后端 / teacher_web v1 TS+Vite+Zustand / backend rollcall+study+teachers + Alembic / iOS↔backend 字段对齐 F1-F5+Q1）
- 项目第一次「三端 + 后端 + 文档 五条线同时推进」

### 2026-05-02 夜 by [Mac-mini-Opus 4.7]

**主题**：⭐⭐⭐ Tomoshibi Android 端 0→1 bootstrap + 4 会话并行架构落地

- 一夜从 zero 干到 23 屏 Compose App + 视觉对齐 iOS + push public GitHub（`otogi2025/Tomoshibi-Android`，47 .kt / ~6000 行 Kotlin）
- CLAUDE.md 加 2 条 AC 叙事根本性原则（CC 决定/动作=itsuki 做的 + 没素材也硬凹）
- 4 worktree 并行（A/B/C/D contract stub 设计 + 文件白名单）→ 0 conflict merge

### 2026-05-02 by [Mac-主会话]

**主题**：iOS 网络层完整建设 + AppStore 切真 API（7 commit）

- 新建 NetworkModels / 4 Endpoints / KeychainService（JWT 持久化）
- 改造 APIClient / ApplicationStatus / LoginView / StayForm / AppStore / StayList
- backend pytest 19 passed / iOS swiftc -typecheck 0 error

---

## 🤝 多会话占用（避免冲突）

*当前无并行会话占用任何文件。*

> 如启动多会话并行：在此列出谁正在改哪些文件 + 开始时间，其他会话避让。改完登记完成移走。

---

## 🚧 阻塞项

*当前无阻塞项。*

> 阻塞项 = 等 itsuki 答复才能推进的硬卡点（如 Q1/Q2 字段对齐拍板）。无阻塞时本节为空。

---

## 🔒 多会话协调规则

### 会话标识（建议命名）

`[设备-主题]` 格式：`[Mac-主会话]` / `[Mac-mini-Opus 4.7]` / `[Mac-后端]` / `[Mac-iOS]` / `[Mac-Android]` / `[Mac-Web]` / `[Code-Agent]`。

### 避免冲突的硬规则

1. 每个「占用」任务必须标出涉及文件 / 目录
2. 其他会话不能动正在被占用的文件
3. **共享文件**（`CLAUDE.md` / `WIP.md` / `progress_overview.md` / `CHANGELOG.md` / `TODO.md`）：一次只能一个会话改，改完立刻 commit + push
4. 改 `WIP.md` 本身：先 pull，改完立刻 push
5. git conflict：停下来问 itsuki，不自己猜合并

### 关键文件边界

| 目录 | 归谁管 |
|------|-------|
| `03_dev/backend/` | 后端会话 |
| `03_dev/student_ios/` | iOS 会话 |
| `03_dev/teacher_web/` | Web 会话 |
| `03_dev/device/` | 设备会话（Pi）|
| `01_specs/` | 一次只允许一个会话改（规格冻结区）|
| `00_admin/` | 主会话管理 |
| `05_logs/raw/` | 各会话写自己今天的，文件名不撞 |

---

## 📝 给新会话的上下文（关键信息）

读完 `CLAUDE.md` + 本文件 + `TODO.md` 顶部应该知道：

1. **当前版本**：见上方 + `CHANGELOG.md` 顶部
2. **上线姿态**（4-19 G2 决策）：取消分阶段；v1.0 直接 iOS + Android + 卡 一次上线
3. **防作弊核心**：动态 NFC 贴纸 ST25DV16K（10 秒 nonce）+ ECDSA 签名 + 老师监督 + 语音播报（原创设计 → `05_logs/decision_log.md`）
4. **版本体系**：0.x.x = 开发中，1.0.0 = 宿舍正式上线
5. **记录体系**：CC 侧 `00_admin/CLAUDE_CODE_记录指南.md`；总章 `AC入试记录指南_v3.md` 在 iCloud（CC 不读）
6. **文件地图**：`CLAUDE.md §目录结构` + `00_admin/文件结构指南.md`
7. **文档一致性**：声明性文件不写硬编码版本号，见 `CLAUDE.md §文档一致性规则`
8. **itsuki 偏好**：选项用 A/B/C 不用甲乙丙 / α β γ；决策她拍板；不盲从 AI

---

## 🕘 本文件自己的更新日志

- **2026-05-04** — 🔧 **大改 by [Mac-mini-Opus 4.7]**：itsuki 指出 WIP 跟 TODO 重叠 → 拍板方案 A → 砍「🔄 进行中的任务」section（218 行，跟 TODO 重叠）+ 砍「✅ 最近完成」长尾历史（170 行，commit history 已记录）+ 头部「最后更新」长串历史压缩到「最近会话」5 条 → 全文 600 → ~160 行；分工规则写明铁律「未完成的事只写在 TODO」；CC 启动流程加「扫 TODO 顶部 200 行」。备份 `/tmp/WIP_backup_2026-05-04.md`
- 更早历史 — 见 `git log -- 00_admin/WIP.md`

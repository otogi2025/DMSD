# Android Round 1 Handoff — itsuki 操作清单

> 这是「**发给 Claude Design 之前你要做什么**」的清单。所有要发的东西都在这个文件夹里。

## 📂 文件夹内容

```
round1_handoff/
├── README.md                ← 本文件（你看的）
├── Round1_Prompt.md         ← ⭐ 主提示词（直接 paste 给 Claude Design）
├── Design_Tokens.md         ← 颜色 / 字体 / 圆角 / 间距 token 全清单
├── iOS_Inventory.md         ← 31 .swift 文件索引 + Route + 数据模型 + AppStore state
├── iOS_source_pack/         ← 28 个关键 .swift 文件（参考实装）
├── spec_excerpts/
│   ├── system_features.md   ← 共用规则（含老师 38 反馈 + 投诉系统 + 学習 NFC 化）
│   └── IOS_DESIGN_LOG.md    ← iOS 设计决策（多步注册 / 锁定升级 等）
└── screenshots/             ← ⚠️ 你自己截 15-20 张关键页面（步骤见下）
```

## 📸 你需要截的 iOS 截图（15-20 张，5 分钟）

**前提**：Xcode 顶部 scheme 选 `TomoshibiAppDemo` → Run → 在 iPhone 17 Pro Simulator 跑 demo 版。

按以下顺序截（Cmd+S 保存 simulator 截图到 Desktop，然后挪到 `screenshots/` 文件夹，名字按顺序 `01_login.png` `02_home.png` 这样）：

### 必截（核心页 12 张）

| # | 文件名 | 怎么到达 |
|---|---|---|
| 01 | `01_login.png` | App 首启动到 Splash 自动跳 Login |
| 02 | `02_home_idle.png` | Login → 任意账号密码（demo1234）→ 进 Home（amber Card 显示扣分态）|
| 03 | `03_home_study_active.png` | Home → **长按 amber Card 0.6 秒** 切 1 次 = 学習 10 分前 → **再长按 1 次** = 学習中（看到 NFC 3 dot 进度）|
| 04 | `04_studycheckin_sheet.png` | 上一步 → 点「NFC で签到」按钮 → sheet 弹出 |
| 05 | `05_apply_new_grid.png` | 底部「申し込み」→ 右上 + button → 8 grid |
| 06 | `06_stay_form.png` | 上一步 → 点「外泊」→ StayForm |
| 07 | `07_stay_list.png` | マイページ → 申請履歴 |
| 08 | `08_stay_detail_chain.png` | 上一步 → 点 a1（审査中外泊）→ 看到承認の流れ timeline |
| 09 | `09_stay_edit.png` | 上一步 → 点底部「修改届を提出」（若 status 为 returned 才显示，可点 a2）|
| 10 | `10_mypage_landing.png` | 底部「マイページ」→ 9 grid |
| 11 | `11_my_study.png` | マイページ → 「学習履歴」grid block |
| 12 | `12_music_view.png` | Home → リクエスト曲卡片（紫色音符）→ 看到 hint banner + 通報 button |

### 加分截（5-8 张，最好都截）

| # | 文件名 | 怎么到达 |
|---|---|---|
| 13 | `13_song_report_sheet.png` | 上一步 → 点任一首「⚠ 通報」→ sheet 弹出 |
| 14 | `14_register_step1.png` | Login → 「新規登録」→ Step 1（看到「学生区分」chip）|
| 15 | `15_lockout.png` | Login → 故意输错密码（不是 demo1234 / 00）→ 进 lockout |
| 16 | `16_my_points_chart.png` | マイページ → 減点明細 → 推移 → 12 ヶ月 chart |
| 17 | `17_notifications.png` | Home 右上铃铛 → NotificationsView |
| 18 | `18_bottom_nav.png` | 任意页面 → BottomNav 3 button（看 Liquid Glass active capsule）|
| 19 | `19_my_settings_demo.png` | マイページ → 通知設定 → 滚到底（看 demo push 4 button）|
| 20 | `20_breadcrumb_popup.png` | 任意 L2 页 → 长按左上 ホーム/← 0.4 秒 → 小 popup |

截图技巧：
- iPhone 17 Pro Simulator 跑着的时候，**Cmd + S** 自动存到 Desktop（Mac）
- 名字默认 `Simulator Screenshot - iPhone 17 Pro - 2026-05-01 at XX.XX.XX.png` — 重命名为上面的 `0X_xxx.png`
- 全挪到 `~/dev/DMSD/03_dev/student_android/v1/round1_handoff/screenshots/`

## 📤 怎么发给 Claude Design

### 方案 A — 直接打包发（推荐）

```bash
cd ~/dev/DMSD/03_dev/student_android/v1/
zip -r round1_handoff.zip round1_handoff/
```

→ 把 `round1_handoff.zip` 拖进 Claude Design 对话框。

### 方案 B — paste 文件 + 附件

1. 主 prompt：把 `Round1_Prompt.md` 全文 **复制 paste** 到 Claude Design 对话框
2. 附件：上传以下文件（拖进对话框）
   - `Design_Tokens.md`
   - `iOS_Inventory.md`
   - `spec_excerpts/system_features.md`
   - `spec_excerpts/IOS_DESIGN_LOG.md`
   - `iOS_source_pack/*.swift`（28 个文件，全选拖进去）
   - `screenshots/*.png`（15-20 张）

### 注意

- Claude Design 一次对话有 token / 文件限制 — 如果一次发不完，分批发
- **第一条消息** 必发 `Round1_Prompt.md` 内容（让它知道任务）
- 第二条消息发 `Design_Tokens.md` + `iOS_Inventory.md` + 截图
- 第三条消息发 `spec_excerpts/`
- 第四条消息发 `iOS_source_pack/` 关键文件

## ⚠️ 关键约束（已写进 Round1_Prompt.md，你不用再说）

1. **直接用 Kotlin + Jetpack Compose**，禁止 HTML / React / KMM 中转
2. **代码注释用中文**（你 native）
3. **日本語文案逐字照抄 iOS**，不翻译
4. **数据模型 / Route case 名 1:1 对齐 iOS**
5. **双 Build Variant**（production / demo），demo 含演示 hack
6. **38 条老师反馈 + 5-01 投诉系统 + 学習 NFC 化 全部要做**

## ✅ 检查清单（发出前过一遍）

- [ ] 顶部 Xcode 切到 `TomoshibiAppDemo` Run，simulator 跑起来
- [ ] 按上面 12 张「必截」+ 5-8 张「加分截」截图，挪到 `screenshots/`
- [ ] 文件夹结构对：`Round1_Prompt.md` 在最顶层、其他文档同层
- [ ] `iOS_source_pack/` 里 28 个 .swift 文件存在
- [ ] `spec_excerpts/system_features.md` + `IOS_DESIGN_LOG.md` 存在
- [ ] zip 打包 OR 拖进 Claude Design

## 🤔 Claude Design 出来后

- Phase A 它给 3 variations × 5 关键页 = 15 个 Compose Preview 截图 → **你选一个 variation**
- Phase B 出全工程（全部 30+ Composable + Gradle build + AndroidManifest）
- 你 clone Phase B 工程到 `~/dev/Tomoshibi-Android/`（独立 repo，跟 iOS 一样）→ Android Studio 打开 → Run

## ❓ 它做不了 / 不清楚的事

Claude Design 会写一个 `Round1_OpenQuestions.md` 列疑问 — 你回答后它继续。常见疑问：
- NFC 真扫描 vs Mock（demo 版肯定 mock，production 版接 NfcAdapter）
- FCM keystore / API key（暂时空，接 backend 时填）
- 留学生 flag UI 摆放（已实装在 Register Step 1）
- 等等

---

**就这样。截图 + 打包 + 拖到 Claude Design 对话框 — 开干。**

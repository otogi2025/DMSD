# Tomoshibi 学生 iOS App · 设计决策完整归档

> **作用**：itsuki 提过的所有 iOS 设计要求 + 自主决定 + 待决清单的完整归档。防遗忘 / 下次会话快速恢复 context / AC 素材 / Claude Design prompt 的 single source of truth。
> **建立**：2026-04-22 晚 by [Mac-demo-sprint]
> **最后更新**：2026-05-28（§3.3 + §3.9.2 注册页 demo 默认空 + 送后端转数字码修真 bug）/ 2026-05-27（§实装进度速查表 5 个 🟡 全 ✅）。早些更新：2026-05-21 A-029 / 2026-05-03（§3.9.2 注册 flow 5→6 step + §3.12「登録コード入力」）/ 2026-05-02 §11.9 I1/I2 / 2026-04-22 晚 Round 1
> **同型档案对照**：`teacher_web/WEB_DESIGN_LOG.md`（老师 Web 的等价档）

## ⚠️ 实装进度速查表（2026-05-27 全 ✅ 化）

| 层 | 进度 | 说明 |
|---|---|---|
| 设计文档（本文） | ✅ ~95% | 989 行设计，主体 v2 已落 + 5-03 注册 flow 更新 |
| Network/Endpoints | ✅ | Auth / Applications / Study / Announcements / RollCall / Bus / **Events**（2026-06-04 杭田一-9：行事予定从 SEED.events 切真后端 GET /events，三态仿 BusListView）全加（A-024 已修） |
| Features/Home | ✅ | Home omnibus 完成；amber Card 三态 long-press demo 包 `#if DEMO`（A-033 5-26 做法 B 落地） |
| Features/Auth | ✅ | 注册 flow 6 step UI 完成；密码预填 / 000000 后门全包 `#if DEMO`（A-035 已修） |
| Features/StayList | ✅ | UI 完成；listMine + detail/audit 切真 API + unauthorized → mock 兜底（A-037 5-21 + 5-27 切回完成） |
| AppStore seed | ✅ | 公告 demo seed 全包 `#if DEMO`（A-038 已修） |
| SEED.user | ✅ | reviewer 060218 包 `#if DEMO`（A-036 已修） |
| 依赖管理 | ✅ N/A | C-044: iOS 工程无外部 SPM 依赖（xcodeproj 内 XCRemoteSwiftPackageReference 为空），不需要 Package.resolved；全靠系统 Foundation / SwiftUI |

---

## 1. 时间线（按发生顺序）

| 时刻 | 事件 |
|---|---|
| 2026-04-21 晚 · [Code-Agent] session | 写 `DESIGN_BRIEF.md` v1（4 tab 架构，签到不在 App 内）→ **已归档为 `_archived_v1_DESIGN_BRIEF_2026-04-21.md`** |
| 2026-04-22 晚 · [Mac-demo-sprint] 早段 | itsuki 提供完整新架构：**3 按钮 nav + Home omnibus + 中央点呼按钮 + 注册 flow + 锁定升级**，推翻旧 4-tab 方案 |
| 2026-04-22 晚 · [Mac-demo-sprint] 中段 | itsuki 答 Q1-Q8 + N1-N20 + 00 号 seed 详细配置；"其他由你决定" → 全默认采纳 |
| 2026-04-22 晚 · [Mac-demo-sprint] 晚段 | 本 LOG 最终化 + `round1_handoff/Round1_Prompt.md` 落盘 + references 导入 + DESIGN_BRIEF.md 升到 v2 final |
| 2026-04-22 晚 · 18:45 | itsuki 拍板：**Pi 3A+ 购买不及 → demo 当天用银行卡 + iPhone 快捷指令代替点呼機**。[Code-Agent] 在 `teacher_web/round3/` 实装 `demo_server.py`（POST `/checkin?no=XX`）+ `live-roll-call.jsx` polling + SpeechSynthesis 日语 TTS + `NFC_DEMO_SETUP.md` 教程。见 `teacher_web/NFC_DEMO_SETUP.md`（iPhone 快捷指令配置 + 局域网 IP + 演示台本） |
| 2026-04-22 夜 · 19:10 | itsuki 拍板 **外泊申请提交期限规则**：出发日所在那周的周三 23:59、或出发前 48 小时，取较早的那个。iOS App 侧必须在期限后屏蔽提交（界面：提交按钮禁用 + 说明「期限を過ぎました。寮監と直接相談してください」+ 通往寮监室的导引）。Web 侧已经在 `teacher_web/round3/src/components/applications.jsx` + `outstay-detail-modal.jsx` 实装好（`outstayDeadline()` 辅助函数 / 列表的期限标记 / 详情弹窗的「§提出期限」段 + 需面谈警示 + 说明横幅）· 写 iOS Round 1/2 Prompt 时要把这条规则加到申请流程 step 2 或 3 |

---

## 2. 架构级决策（v2 · 2026-04-22 拍板）

### 2.1 核心架构变化 vs 旧版

| 项 | 旧版（归档） | **新版（当前真值）** |
|---|---|---|
| 底部 nav | 4 tab（ホーム / 申請 / 規律 / マイ） | **3 按钮**（申し込み / ⭐点呼 / マイページ）|
| 签到入口 | "不在 App 里发生"（纯 Shortcut） | **中央点呼按钮 → Liquid Glass sheet → 扫 NFC → 绿勾** |
| Home 承载 | 点呼状态 + 通知 only | **Community + 扣分 + 快递 + 遗失物 + 点歌 + 顶部点呼 bar + 中央按钮** |
| 认证 | demo 切学生下拉（无注册） | **完整注册 flow + 账号锁定升级策略** |
| 视觉 | Ryō 沿用 | **iOS 26 原生 Liquid Glass**（非 CSS 模拟 — Swift `.glassEffect()`）|

### 2.2 底部 3 按钮 nav（image #3 手绘参考 · 文件 `references/02_bottom_nav_sketch.png`）

| 左 | 中（大 + 徽章）| 右 |
|---|---|---|
| ✉ **申し込み** | ⭐ **点呼** action button | ✦ **マイページ** |

中央按钮**不是 tab**，是 action button — 点一下弹 sheet 覆盖当前页，不跳转 tab。

### 2.3 Home omnibus 原则

Home 包含 **除了 申し込み 和 マイページ 之外的所有功能**：
- 顶部点呼状态 bar（持久 + 可点 → 反馈 sheet）
- 扣分点数三色
- Community 全量（~~宿舍墙~~(2026-06-03 削除) / 点歌 / 遗失物 / 活动 / 巴士 / 建议）
- 快递 / 通知
- **Home 分 section + 内部 tab** 防止下滑过长（Q3 ✅）

### 2.4 中央点呼按钮 flow（image #4 / #5 参考 · `references/03/04_scan_sheet_ref_*.png`）

灵感源 = SUNTORY ジハンピ（Liquid Glass 遮罩 + 白 bottom sheet 从下滑上 + 圆形手机插画 + キャンセル）

| 态 | 视觉 |
|---|---|
| ① 待触发 | ⭐ 金色徽章 按钮 |
| ② 就绪（Liquid Glass 遮罩）| 白 sheet 滑上 + 「スキャンの準備ができました」+ 圆形手机往前碰循环动画 + キャンセル |
| ③ 成功 | 绿色大勾 ✅ + 判定 badge（時間内 / 遅刻）+ 3 秒退场 |
| ④ 失败 | 红 ❌ + 原因 + 再試行 |

### 2.5 导航规则

| 层级 | 左上 icon |
|---|---|
| Home | 无 |
| 申し込み / マイページ L1 | 🏠 **line-icon 简笔画 Home**（不是 emoji）→ 回 Home |
| L2+ | `←` 返回箭头 → 上一级 |
| **长按 `←`**（0.4 秒，N9）| 弹 breadcrumb + 各级跳转 + Home |

---

## 3. 注册 flow（2026-04-22 拍板）

### 3.1 字段（4 step）

| Step | 字段 |
|---|---|
| 1 基本情报 | 氏名 / **生日**（N1 ✅，从生日自动算年龄）/ 性别（决定寮分配 — 男寮/女寮 N7）/ 头像（相册 only，N6）|
| 2 学生类别 | 一般寮生 or サッカー部（N2 ✅ 只 2 选项）|
| 3 联络先 | 邮箱（不验证，用于未来重置密码识别）/ 电话（宿管联系用）|
| 4 密码 | 密码 × 2 确认 + ⚠ "无法自改" banner |

### 3.2 ⭐ 00 号测试账户 seed（2026-04-22 itsuki 指定）

Claude Design **必须**默认创建 00 号账户，seed 数据：

| 字段 | 值 |
|---|---|
| 号码 | **00** |
| 氏名 | **リュウイヒ** |
| 生日 | **2006-10-14**（19 岁）|
| 性别 | 女 |
| 自动分配寮 | 女寮 |
| 部屋 | **W101**（和 web ROSTER 一致）|
| 类别 | 一般寮生 |
| 邮箱 | `ryu_ihi@tomoshibi.local`（mock）|
| 电话 | `090-0000-0000`（mock）|
| 头像 | 默认（リ 字母 + cobaltSoft 底）|
| 本月扣分 | **4 分** → 主页显示 🟡 **罚扫待定（下月）** |
| 扣分组成 | 迟到 2 次（1 分）+ 缺席 3 次（3 分）= 合計 4 分 |
| 扣分发生日期（mock）| 遅刻 2026-04-05 / 2026-04-12；欠席 2026-04-08 / 2026-04-15 / 2026-04-20 |

### 3.3 Demo 注册魔法（2026-04-22 itsuki 指定）

- **Demo 模式下注册 flow 是演示动画**，不真写入后端
- itsuki 走一遍 4 step（在观众面前输入 リュウイヒ / 20061014 / 女 / 一般生 / 邮箱 / 电话 / 密码）
- 点击"注册完成" → 自动**登入已 seed 的 00 号账户**（不创建新账户）
- 之后看到 Home 已有 4 分扣分记录（剧本效果：管理员震惊"这么多数据！"）
- **2026-05-28 追加**：demo 模式下 step 2（学年/组/番号）+ step 4（房间号）4 个字段**不预填**（原来预填 SEED 假数据）。目的：演示时当着管理员面现场输入，让账号番号（アカウント番号）随输入实时跳动，展示 6 桁学号怎么算出来。step 1 的氏名/生日/性别仍预填（跟账号番号无关）。

### 3.4 账号分配（v1.0 未来）

- 后端 `student_id` int PK 自增
- UI 展示为 **2 位 0 填充**（00 / 01 / 02 / …）
- Claude Design seed 的 00 号是"demo 本体"
- 真实学生注册从 01 起

### 3.5 登录

- 号码 + 密码 2 字段
- **永久保持**（直到主动 ログアウト）
- 成功登录 → 错误 counter 清零（N3 ✅）
- 首次启动 → 没 session → 注册 flow
- 后续启动 → 有 session → Home

### 3.6 密码锁定升级策略

| 触发 | 锁定 | 动作 |
|---|---|---|
| 连续 3 次错 | 30 秒 | **通报老师**（老师 Web `/discipline` 底部 card，N5）|
| 解锁后再错 1 次 | 1 分钟 | 通报老师 |
| 再错 1 次 | 5 分钟 | 通报老师 |
| 再错 1 次 | 30 分钟 | 通报老师 |
| 再错 1 次 | 1 小时 | 通报老师 |
| 再错 | **永久锁死 → 「宿監に連絡してください」** | — |

锁定升级规则：**解锁后再错 1 次就升级**（N4 ✅）。

### 3.7 密码重置

- App 内**无自助重置**
- 学生本人找宿管
- 宿管在老师 Web 后台手动改
- **⚠ 老师 Web 新需求**：要加"学生アカウント管理 / パスワード重置"页（纳入 teacher_web 的 Round 3 补充 或 Round 4；本 LOG §9 记录）

### 3.8 注册页底部警示（必有）

> ⚠️「パスワードは自分では変更できません。変更には寮監への連絡が必要です。入力時は慎重にお願いします。」

---

### 3.9 学号体系 6 桁（2026-04-23 拍板）

**⚠ 权威源是 `02_design/system_features.md §3`。这里只是 iOS 视角的摘录 + App 专有的界面规格。**

#### 3.9.1 编码

`学年(2) + 组(2) + 番号(2)` = 6 桁，例 `060218` = 高3 / B组 / 18 番。

- 学年: 中1=01, 中2=02, 中3=03, 高1=04, 高2=05, 高3=06（6 年制中高一贯）
- 组: A=01, B=02（本校只到 B 组）
- 番号: 01〜99（班里顺序号）

#### 3.9.2 注册流程新增的步骤

旧 4 步 → **新 6 步**（2026-05-03 itsuki 拍板把第 6 步「登録コード」（教师发的注册码）加到最后一步 — App Store 上架对策 §3.12）:

| 步 | 字段 |
|---|---|
| 1 基本信息 | 氏名 / 生日 / 性别 / アバター（头像）|
| **2 学年・组・番号** ⭐ 新增 | 学年选择器（中1〜高3）/ 组选择器（A/B）/ 番号输入框（数字，01-99）→ 自动生成显示 060218 |
| 3 学生类别 | 一般寮生 / サッカー部（足球部）|
| 4 房间号 ⭐ 新增字段 | 房间号输入框（例 `M101` / `W203`，校验见 §3.10）|
| 5 联络先 + 密码 | メール（邮箱）/ 電話（电话）/ パスワード（密码）× 2 |
| **6 登録コード** ⭐ 新增（2026-05-03） | 教师发行的 6 桁数字注册码输入框（§3.12 / 共用层 §7.16）|

**界面规则**:
- 第 2 步学年・组・番号 3 个都填好后，下方用 30pt 钴蓝色显示「あなたの学号: `060218`」（预览）
- 番号重复检查（后端 `GET /accounts/check?student_no=XXXXXX`）→ 重复时红色错误「この番号は既に使用されています。班里最末番号 + 1 で入力してください」
- **送后端时转数字码**（2026-05-28 修真 bug）：画面显示学年用中文「高3」、组用「B」，但提交注册接口的 `registrationDraft` 三字段必须转成数字码 —— `grade_code=06`（按 §3.9.1 编码表）/ `class_code=02` / `seat_no` 补足 2 位（"1" → "01"）。后端 `schemas.py §588-590` 三字段都校验 `^\d{2}$`（正好 2 位数字），送中文/字母/1 位数会被打回（注册失败）。配套：`canNext` 守卫挡出席号 > 99（>99 同样过不了 `^\d{2}$`）。

#### 3.9.3 demo seed 更新

リュウ イヒ（demo seed 本体、架空サンプル）:
- **旧**: 番号 `00`
- **新**: 学号 `060218`
- 生日 `2006-10-14` → 2026 年 4 月时在读高3 → 跟 `grade_code=06` 一致 ✅

#### 3.9.4「マイページ」（我的页面）的编辑

在「個人情報」段可以编辑学年 / 组 / 番号（应对升级・转校）:
- 按编辑按钮 → 弹窗「学年・組・番号を変更しますか？学号が変わります」
- 保存 → §3.11 改动履历自动记录 + 通知老师 Web

---

### 3.10 房间号（2026-04-23 拍板）

**⚠ 权威源是 `02_design/system_features.md §4`。**

#### 3.10.1 注册时

- 学生本人手动输入
- 格式: 推荐 `[MW]\d{3}`，但 demo 阶段**允许任意字符串**（不校验）
- 性别和 `[MW]` 的一致性检查留到 v1.1 加（demo 阶段跳过）

#### 3.10.2「マイページ」（我的页面）的编辑

- 只读 / 可编辑的切换，由「老师一括分配是否生效」决定
- **demo 阶段**: 始终可编辑（一括分配还没实装）
- v1.1 以后: 一括分配生效后变只读 + 显示「部屋変更は寮監へ相談してください」文案

#### 3.10.3 一括分配接收（v1.1 将来功能）

- 老师 Web 执行 `POST /room-assignments/batch` → 给学生 App 发静默推送
- App 收到 → 我的页面房间号自动更新 + 通知「あなたの部屋が M101 → M205 に変更されました（2026-04-25 09:30 寮監による割当）」
- §3.11 改动履历自动记录（actor=teacher）

---

### 3.11 学生改动履历（审计日志，2026-04-23 拍板）

**⚠ 权威源是 `02_design/system_features.md §5`。**

#### 3.11.1 原则

**学生在 App 内做的所有信息变更，老师 Web 都能查看。**

对象字段:
- 学号构成（grade_code / class_code / seat_no）
- 房间号（自己编辑 + 老师一括分配）
- メール（邮箱）/ 電話（电话）/ アバター（头像）
- パスワード（密码，只记变更事实，不记哈希值）
- 氏名（订正误输入，需老师批准 ⏳ v1.1）

#### 3.11.2「マイページ」的「変更履歴」（变更历史）入口

- 我的页面末尾加一行「変更履歴」按钮 → 点击进历史画面（按时间排的列表）
- 显示项目: `日时 / 字段名（日语）/ 旧值 → 新值 / 变更者（本人 / 寮监 / 系统）`
- 期间筛选: 全部 / 过去 30 天 / 过去 1 年
- 只能看自己改的行（看不到别的学生的历史）

#### 3.11.3 Web 端联动

老师 Web「学生アカウント管理」→ 学生详情弹窗的「アクティビティ履歴」tab 按时间排显示（见 WEB_DESIGN_LOG）。

---

### 3.12 登録コード（注册码）输入（2026-05-03 拍板、App Store 上架对策）

**⚠ 权威源是 `02_design/system_features.md §7.16`。这里只是 iOS 视角的界面规格。**

#### 3.12.1 动机

itsuki 2026-05-03 拍板。App Store 上架 = 向全人类开放下载渠道。在注册入口加一道门，让「物理上能接触到老师的人」才能注册。

#### 3.12.2 界面规格（iOS 专属）

- **位置**: 注册流程的**最后一步（step 6）**（密码设置 step 5 的下一步）
- **标题**: 「登録コード」
- **说明文**: 「教師に発行された 6 桁の数字コードを入力してください」
- **输入框**:
  - 6 桁数字专用、一次性密码风格的输入框（推荐每位一格的分隔框，仿 Apple 短信验证界面）
  - 键盘用 `numberPad`
  - **不用**自动填充 `oneTimeCode`（防止系统从短信自动补全 — 这个码不是走短信发的）
- **提交按钮**: 「登録を完了する」
  - 6 位没填满前禁用
- **错误显示**:
  - 失败时 → 输入框红色抖动（错误触感反馈）+ 下方显示「コードが正しくないか、有効期限が切れています。教師に再発行を依頼してください。」
  - 可以立刻重试（频率限制在后端做，比如 5 次 / 分）
- **返回**: 用返回按钮能回到 step 5（已填数据保留）

#### 3.12.3 后段流程

- 提交成功 → 后端用全部 step 数据 + `registration_code` 接收 `POST /accounts` → 校验码 → DB 创建学生 → 发永久 session
- 成功画面 → §3.13 ⭐「ようこそ、{氏名}さん」+ 显示账号番号 060218
- 失败（码错 / 过期）→ 输入框错误（同上）

#### 3.12.4 ⚠️ Demo 阶段的处理

2026-05-03 itsuki 拍板 = 从 v1.0 开始实装。Demo 4-28 已经结束，所以**不需要 Demo 跳过**。新入学季（预定 2026-04）= v1.0 范围。

实装范围:
- Step 6 view（一次性密码风格的 6 桁输入框）
- 错误状态（输入框红色抖动 + 触感反馈）
- 后端 API 对接（`POST /accounts` body 加 `registration_code` 字段）

未实装（推后到 v1.1+）:
- 用 Touch ID / Face ID 保护「最近的码」做自动填充 — 不需要（只用一次）
- 通过 QR 码输入（老师 Web 显示 QR → 学生扫）— v1.1 再考虑
- 每个寮单位用不同的码（按 dorm_unit 分）— v1.1 再考虑

---

### 3.13 启动跳转策略（2026-05-07 itsuki 拍板，App Store 上架对策）

**问题**：之前 SplashView 启动 2.2s 后强制跳 onboarding → 已注册老用户每次启动都看 onboarding → 烦。Apple 审核员第一屏看到强制 onboarding + 注册码门进不去 app → reject 风险。

**新逻辑**（SplashView.onAppear）：
- Keychain 已恢复 token（`app.authToken != nil`）→ 自动登录跳 home
- 没 token → 跳 login（不再走 onboarding）
- onboarding 不再强制路径，保留代码为 v1.x 后做引导入口可选

**login 第一屏的好处**：
- 老用户：Keychain 自动登录无感
- 新用户：login 底部「新規登録」link 一键跳 RegisterStep1
- 审核员：用 Reviewer Notes 给的 demo 学号 + 密码直接登录，绕过注册码门

**实装**：
- `Features/Auth/AuthStubs.swift` SplashView 加 `@EnvironmentObject app: AppStore` + onAppear 内 token 判断
- LoginView「新規登録」按钮（line 1583）已有，跳 `.registerStep1`，不动
- onboarding 入口暂无 button（dead code 但不删，v1.x 加引导触发）

**双端同步**：上架版 fork + 主项目（`03_dev/student_ios/v1/`）同步改完 2026-05-07（fork 已退役，主项目为唯一开发线）

---

### 3.14 账号删除入口（2026-05-07 itsuki 拍板，Apple 5.1.1(v) 强制）

**位置**：`Features/MyPage/MyPageStubs.swift` MySettingsView 末尾「アカウント」section。

**UI**：
- Section 标题：`アカウント`（小字 inkMute）
- Card：红色 destructive button「アカウントを削除」+ ProgressView（删除中）
- 副提示：`削除すると元に戻せません。`
- 二次确认：SwiftUI alert，destructive button「削除する」/ cancel button「キャンセル」
- alert message 说明：`削除すると元に戻せません。点呼履歴・申請履歴・プロフィール情報がすべて閲覧できなくなります。`

**调用流**：
- 用户点「削除する」→ `Task { await performDelete() }` → `AccountsAPI.deleteMyAccount()` 调 `DELETE /api/v1/accounts/me`
- 成功 → `app.authToken = nil` → didSet 清 Keychain + APIClient.token → RootView 触发 SplashView → 跳 login
- 失败 → toast 风格 alert 显示 error message

**Backend 接 endpoint**：见 `BACKEND_DESIGN_LOG §5.1.6`

**双端同步**：2026-05-22 主项目 v1 backport 完成（上架版 fork 已退役归档，主项目变唯一开发线）。改动落在 `MyPageStubs.swift` MySettingsView（state + accountDeletionSection + performDelete）+ `AuthAPI.swift` AccountsAPI.deleteMyAccount()。

---

### 3.15 忘记密码按钮 v1.0 隐藏（2026-05-07 itsuki 拍板）

**问题**：LoginView 原有「パスワードを忘れた →」按钮跳 `.pwreset`，但 PwResetView 是 placeholder（无 backend 实装）。Apple 4.0 死按钮 reject 风险。

**处理**：
- LoginView footer HStack 删掉「パスワードを忘れた」Button block，仅留「新規登録」
- PwResetView 代码不删（保留为 v1.1 实装基础）
- 留 `// v1.0 上架版：忘记密码功能未实装 → 入口隐藏，避免 Apple 4.0 死按钮 reject` 注释

**用户路径替代**：忘密码 → 看 support.md → 联系 otogi2025@gmail.com → 寮管理者人工重置

**双端同步**：fork + 主项目 v1 都改完 2026-05-07

---

### 3.16 Demo 账号双用 + Reviewer 永久码（2026-05-08 itsuki 拍板）

**权威 spec**：`02_design/system_features.md §7.20` + 后端 schema `BACKEND_DESIGN_LOG §5.x.4`。

**iOS 端涉及**（**无 UI 改动 / 无客户端字段改动**）：
- LoginView：Apple 审核员 / 老师都用同一组凭证直接登录 → 学号 `999999` + 密码 `Tomoshibi-Reviewer-2026!`
- RegisterStep5：老师可选体验完整 6 步注册流程时输注册码 `999999`（is_reviewer=True 永久有效）— 但仅一次（第二次注册同学号会撞 `STUDENT_NO_TAKEN`）

**iOS 端不需改的原因**：
- backend `is_demo` / `is_reviewer` 是 server 端 schema，client 完全不感知
- API 端点 URL / 参数 / 返回类型不变 → `AuthAPI` / `AccountsAPI` / `RegisterStep5` 都不动
- LoginView 不加「demo 登录」按钮 — 普通学生 login 画面看不到 demo 入口（防引导误用）

**5-08 修复联动**：
- 5-08 上架冲刺 fork 直接塞 `999999` 永久码进 prod DB 出 5 个 bug（详见 §7.20 末尾历史教训），主 CC review 后重做 — backend schema 加 `is_demo` / `is_reviewer` flag 双层防御。**iOS 不动**，只是 server 行为升级

**Reviewer Notes 文案**（Apple 提交时填）：
- ✅ 学号 `999999` + 密码 `Tomoshibi-Reviewer-2026!`
- ❌ 不写 `999999` 注册码（防 OCR 泄漏）

---

## 4. Home 顶部点呼状态 bar

### 4.1 三态

| 态 | 显示 |
|---|---|
| 点呼中（老师 iPad 开启点呼）| 倒计时「あと X 分 Y 秒で遅刻判定」+ 可点 |
| 日常（idle） | 时间 + 下次点呼预告「次の点呼：21:00」|
| 已签到 | 绿色满 bar「チェックイン済 HH:MM ✓」|

### 4.2 点击 → 反馈 sheet · 3 选 1

- 体調問題を報告
- 今回欠席の申請
- その他の問題（自由文本 + 类型 tag · N13）

### 4.3 持久范围（Q8 · itsuki "其他你决定" → 我决定）

**全 App 持久**（跨 tab 跨层级）—— 但 sheet / modal 遮罩时消失（N10 ✅）。

---

## 5. 个人主页（マイページ）内容（2026-05-03 itsuki 拍板「方案 B 分层重设计」）

> **5-03 大改原因**：原 8-grid 把「学習履歴 / 点呼履歴 / 減点明細」全塞 grid 一格小图标，重要信息沒有显眼位置。itsuki 反馈「学習履歴塞最下不显眼 / 点呼明細只显示本月不够 / 整体要扩展」→ 拍板方案 B（参照 Apple Health / Activity 信息架构）。實裝完了 = `MyPageStubs.swift` MyLandingView 全面重写。

### 5.1 整体结构（上 → 下）

```
PageHeader「マイページ」
├─ profileSection（紧凑：avatar 56pt + 氏名 + アカウント番号 + 寮室 Pill 一行）
├─ ⭐ 学習ステータス Card（只对学习对象学生显示）
│    └─ 状态文字（対象外 / 開始まで X:XX / 進行中 / 本日完了 ✅）+「履歴を見る →」
├─ ⭐ 今月の点呼 Card
│    └─ 時間内 / 遅刻 / 欠席 三色统计 +「詳細を見る →」
├─ 減点明細 Card
│    └─ 大字号点数 + 状态 Pill（良好 / 罰掃 注意 / 禁足）+「詳細を見る →」
├─ ─── 「履歴」section header
├─ 履歴 grid（6 件 · 2-col）
│    ├─ 個人情報 / 処分履歴 / 体調報告履歴
│    └─ 申請履歴 / 掃除提出履歴 / 荷物受取履歴
└─ settingsSection
     └─ 行事予定 / 通知設定 / Tomoshibi について / ログアウト
```

### 5.2 旧版（4-22 设计）vs 方案 B（5-03 拍板）

| 项目 | 旧版（8-grid） | 方案 B |
|---|---|---|
| profile | avatar 64 + name + account + 2 Pill 竖排 | avatar 56 + 紧凑横一列 |
| 学習履歴 | grid 第 9 格（只给学习对象加，在最下） | 顶部第 2 块卡片化（最显眼） |
| 点呼履歴 | grid 第 2 格（emoji + label） | 卡片化 + 含本月统计 |
| 減点明細 | grid 第 3 格（emoji + 数字 badge） | 卡片化 + 含点数 + 状态 Pill |
| 履歴 grid | 8-9 件 | 6 件（去掉点呼 / 减点 / 学习） |
| settings | 行事予定 + 特別運航便 + 通知設定 + About + ログアウト | 删特別運航便（5-03 搬到 Home busCard） |

### 5.3 重要性优先级

itsuki 拍板「在マイページ核心信息概览 + 详情入口」模式（参考 Apple Health / Activity）。查看顺位:
1. 我是谁（profile）
2. 学习中? 正常吗?（学習 Card）— 只对学习对象学生
3. 点呼没问题吧?（点呼 Card）
4. 减点线没问题吧?（減点 Card）
5. 其他历史（grid 6 件）
6. 设置

### 5.4 统计数据算出（v1.0 demo）

- 学習ステータス: `app.studyState`（idle / upcoming / active / done）+ `app.studyCountdownSec`
- 点呼本月统计: 把 `SEED.rollcall` 按 state 分别 count（時間内 / 遅刻 / 欠席）
- 减点点数: `SEED.user.points`（5-03 = 4.5）+ 阈值判定（< 4 良好 / 4-7 罰掃 注意 / ≥ 8 禁足）— 阈值跟 §7.12 + RollCall_Spec.md 一致

> **v1.1 扩展预定**: 学习历史统计（出席率 / 异常次数）/ 点呼趋势（跟上月比）/ 减点 12 月推移图（旧版有过，在 Card 内 mini chart 复活）。

### 5.5 实装文件

`03_dev/student_ios/v1/TomoshibiApp/Features/MyPage/MyPageStubs.swift` — `MyLandingView`（line 51〜）。

5-03 大改的实装要点:
- `blocks` 缩到 6 件（点呼 / 减点 / 学习删除）
- `body` 5 块结构（profile + 状态 Card 群 + 「履歴」header + grid + settings）
- 新 helper: `studyStatusCard` / `rollcallStatusCard` / `pointsStatusCard` / `landingCardBg` / `landingCardBorder` / `monthRollcallStats` / `statBlock` / `studyStateText` / `formatCountdown`
- `settingsSection` 删掉「特別運航便」row（移到 Home busCard）

---

## 6. 视觉风格（v2 · iOS 26 Native）

### 6.1 设计语言 — Phase 1 选型

itsuki Q5 指示：**像 Web Round 1 一样，Claude Design 先列 3 variations，itsuki 选定**。本 Round 1 Prompt 里**不预设**，让 Claude Design 提案。

### 6.2 iOS 26 Liquid Glass

- 使用 **Swift 原生 `.glassEffect()`** API（iOS 26 + Xcode 17）
- Claude Design 在 HTML 里用 `backdrop-filter: blur() saturate()` 模拟
- 最终实装 SwiftUI 直接调原生 API
- itsuki iPhone 17 Pro 已是 iOS 26

### 6.3 默认头像

- 姓名首字母 + cobaltSoft 背景圆形（和 web select-teacher 一致）
- Settings 可上传自己的（相册 only · N6）

### 6.4 App icon / Logo 使用范围

- **仅启动页（Splash）使用**（Q5 · itsuki 指示 "logo 在开始界面用就好了"）
- Home / Nav / TabBar / マイページ 均**不放** logo
- 白底 + 红橙火焰 + 中央黄球
- 需从源图（`references/01_tomoshibi_logo.png` · 已带白底圆角）导出 **1024×1024 方形无圆角**（iOS 自动加圆角）

### 6.5 横屏 / 暗色模式

- 横屏：**不支持**，纯 portrait（N19 ✅）
- 暗色模式：**v1.0 不做 / v2 再做**（N18 — 2026-05-25 itsuki 拍板。v1.0 用 `TomoshibiApp.swift:22 .preferredColorScheme(.light)` 强制 light 避免黑闪；v2 真做时全 app token `T.paper` / `T.ink` 等加 dark variant）

---

## 7. 全 App 页面清单（v2 · 63 页 + 10 组件 = 73 项）

> 详见 `DESIGN_BRIEF.md §4` + `round1_handoff/Round1_Prompt.md`（字段级）。清单概要：

| Section | 范围 | 数量 |
|---|---|---|
| §0 认证 / 启动 | Splash + Onboarding + 注册 4 step + 登录 + 锁定 + 密码重置说明 | 10 |
| §1 Home 主屏 | 主屏 + 10 卡片（分 section / tab）+ 顶部 bar + 3 选 1 sheet + 中央按钮 4 态 | 8 |
| §1.4 Home 子页 | 通知 / 快递 / 遗失物 / 点歌 / ~~宿舍墙~~(2026-06-03 削除) / 活动 / 巴士 / ~~匿名建议~~(2026-06-04 削除) | 18→13 |
| §2 申し込み | Landing + 7 类申请 form + 详情 + 免点呼查询 + 历史 | 13 |
| §3 マイページ | Landing + 个人情報 + 8 类历史 + 设置 + 关于 + ログアウト | 14 |
| §4 跨页组件 | TabBar + home icon + back + 持久 bar + 举报 + 空状态 + 错误 + loading + DEMO badge + confirm | 10 |

---

## 8. ✅ 决策已全部 resolved（2026-04-22 晚）

### 8.1 Q1-Q8 答复

| # | 问题 | 答复 |
|---|---|---|
| Q1 | iPhone 机型 + iOS 版本 | **iPhone 17 Pro + iOS 26** |
| Q2 | iOS 26 Liquid Glass | **Swift 原生 `.glassEffect()`**；HTML mockup 用 backdrop-filter 模拟 |
| Q3 | Home 子页 UI 密度 | **加 tabs + sections** 防过长 |
| Q4 | Claude Design 出法 | **一轮全出** 73 页（先 Phase A: 3 variations → 选定 → Phase B: 全页面）|
| Q5 | 设计模板 | **Claude 列 3 variations 像 Web Round 1**，itsuki 选 + logo 仅 splash 用 |
| Q6 | 注册字段后端存法（"其他你决定"）| 后端存：号码 / 氏名 / 生日 / 性别 / 类别 / password_hash / 邮箱 / 电话；demo 邮箱/电话不功能化 |
| Q7 | 老师 Web 密码重置页位置（"其他你决定"）| 另起 Round 4 补丁，不污染 Round 3（Round 3 prompt 已写好未发）|
| Q8 | 顶部点呼 bar 持久范围（"其他你决定"）| **全 App 持久**，但 sheet 覆盖时消失 |

### 8.2 N1-N20 答复（"其他由你决定" → 全部默认采纳推荐）

| # | 决策 | 采纳 |
|---|---|---|
| N1 | 年龄 vs 生日 | **生日**（itsuki 确认 20061014 格式）|
| N2 | 部活选项 | 只 **一般寮生 / サッカー部** 2 选项 |
| N3 | 成功登录 counter 清零 | ✅ Yes |
| N4 | 锁定升级触发 | 解锁后再错 1 次升级 |
| N5 | 通报老师 web 呈现 | /discipline 底部 card |
| N6 | 头像 source | 相册 only |
| N7 | 男女寮标识 | 单一"男寮/女寮" |
| N8 | 注册激活 | 即激活（推翻旧"面签"激活规则）|
| N9 | 长按返回时长 | 0.4 秒 |
| N10 | sheet 上顶部 bar | 不显示 |
| N11 | 非点呼时段点中央按钮 | 提示 + 允许演示扫描 |
| N12 | 点呼 sheet 动画源 | CSS 动画（HTML mockup 用）/ SwiftUI 原生 .glassEffect + Animation（实装）|
| N13 | "其他问题" form | 自由文本 + 类型 tag |
| N14 | Home 全寮统计 | 不显示 |
| N15 | 快递未领 badge | 红点 + 数字 |
| N16 | ~~宿舍墙身份~~（2026-06-03 削除，落实 4-29 拍板） | ~~实名~~ |
| N17 | 点歌 source | Apple Music link paste |
| N18 | 暗色模式 | v1.0 不做 / v2 再做（2026-05-25 推翻） |
| N19 | 横屏 | 不支持 |
| N20 | Demo 切学生 | 砍（注册 flow 取代）|

---

## 9. 跨文档同步（ACTION REQUIRED · 需在本会话 / 下会话执行）

本次 iOS 讨论产生的**跨文档影响**：

| # | 改动 | 目标 | 状态 |
|---|---|---|---|
| 9.1 | `§账号规则` "面签激活" → "即激活" + 新增锁定升级策略 | 主指令档 | ✅ **2026-05-26 自动消除** — 主指令档重写后整段被砍，不再含「面签激活/即激活/账号规则」字样 |
| 9.2 | 老师 Web 加"学生账号管理 / 密码重置"页 | `teacher_web/round3/src/components/accounts.jsx` | **✅ 2026-04-22 晚 [Code-Agent] 直接在 Round 3 里加完** — 番号/氏名/部屋/邮箱/电话/最终登录/状态 列表 + 详情 modal（プロフィール 编辑 + 密码重置 + ロック解除 + アクティビティ 时间线）。Shell 左 nav 加「学生アカウント管理」入口。seed 24 人（00 = リュウ イヒ，01-23 真实学生） |
| 9.3 | 老师 Web `/discipline` 加"被锁定学生通知"card | 同上 | 🔄 **2026-05-26 转 Web 端 backlog（N-003）** — 归属从 iOS 设计日志 §9 移到 Web 端待办（这条本来就是 Web 活，iOS 侧不动） |
| 9.4 | demo 冲刺文档纳入"iOS App 注册 flow + 锁定策略" | demo 冲刺文档 | ✅ **2026-04-29 自动消除** — demo 冲刺文档整段已归档，不在活跃区，无需再同步 |

---

## 10. 下一步

1. ✅ `round1_handoff/Round1_Prompt.md` 已写
2. ⏳ itsuki 扫 Prompt → 找漏洞 / 微调
3. ⏳ itsuki 开 claude.ai Design project → 拖入 `round1_handoff/` 整个文件夹 → 贴 prompt → 让 Claude Design 先出 3 variations
4. ⏳ itsuki 选定 variation → Claude Design Phase B 输出全 73 页
5. ⏳ standalone HTML 下载到本目录 → 代码 agent 接入 SwiftUI

---

## 11. v1.0 实装清单（2026-04-30 加）

> **作用**: 给 Swift code agent 接手 v1.0 实装的入口章。
> **agent 阅读顺序**（两层结构）:
> 1. **共用层（必读）**: `02_design/system_features.md` —— 角色 / 数据模型 / §7 14 子节功能矩阵 / R1-R4 / 38 条要件
> 2. **专属层（本档全文）**: 本 LOG §1-§9 = iOS 设计决策 + §10 跨档同步 + 本 §11 = 实装层
> 3. **后端 API 契约**: `03_dev/backend/BACKEND_DESIGN_LOG.md`
>
> **单 repo**（2026-05-06 退役独立 repo / 2026-05-21 C-012 清理）: Swift 实装直接在 `03_dev/student_ios/v1/TomoshibiApp/`，跟 backend / Android / Web / 点呼机 全在 DMSD 单 repo 里。原跨 repo 同步规则已废。
>
> **决策标记**: ✅ 已定 / 🟡 CC 假设（itsuki 有否决权）/ ⏳ 待拍板（聚集到 §11.9）

### 11.1 P0 范围

| 编号 | 模块 | 来源 |
|---|---|---|
| #1 | 自分の届のみ submit（代提交防止） | system_features §7.2 |
| #2 | 帰省 / 外泊 / 帰国 3 種フィールド | 同上 §7.2.1 |
| #3 | 出寮日 = 明日以降 | 同上 |
| #4 | 動的非表示（不要な field 隠す） | 同上 |
| #5 | 承認状態可視化 | 同上 §7.2.2 |
| #6 | 役职メール通知 (R1) | iOS 側 = backend が email 送信、iOS は POST するだけ |
| #13 | 役职コメント受信 | push + in-app |
| 注册 | 5 step（学年・組・番号・房间号・留学生 flag）| 本档 §3.9 |
| 認証 | login + 锁定升级 6 段階 | 本档 §3.5 §3.6 |

**P0 範圍外**: 学習欠席届 (Q3) → P1 / 路径 B BTR + Universal Link → P1 / リクエスト曲 → P3 / 個人デ ータ aggregated → P2 / 巴士 + 行事 → P2 / 規律可視 → P3。

### 11.2 技术栈（✅ 已定）

| 層 | 選定 | 理由 |
|---|---|---|
| 言語 | **Swift 5.10+** | iOS 26 SDK 必須 |
| UI | **SwiftUI** | iOS 26 Liquid Glass `.glassEffect()` SwiftUI 専用 API |
| Min iOS | **26.0** 妥協なし | itsuki iPhone 17 Pro 確認 / AC 評価軸「最新」 / Liquid Glass demo 価値 |
| 端末 | **iPhone Portrait Only** | 本档 §6.5 |
| Dark Mode | **対応** | 本档 §6.5 |
| Persistence | UserDefaults + Keychain（token） | ⏳ §11.9-I1 |
| Networking | URLSession + async/await | ⏳ §11.9-I2 / Combine 不採用 |
| 状態管理 | `@Observable` macro (Swift 5.9+) | ⏳ §11.9-I5 |
| 依存 | Apple framework only | AC 「自分で全部書いた」叙事 |

### 11.3 demo only scaffold 削除清单（v1 ship 前必ず除去）

v1 上线前必须移除的 demo-only 桩清单。具体ファイル:

| 場所 | 内容 |
|---|---|
| `Features/Home/HomeStubs.swift` | 点数カード `LongPressGesture` → `app.cycleDemoRollState()` |
| `Foundation/AppState/AppStore.swift` | `cycleDemoRollState()` / `tickCountdown()` / `simulateCheckin()` |
| 同上 | `SEED.user` 硬编码 リュウ イヒ / 060218 / 男寮 M101 / 4.5 点 |
| `AppStore.changeLog` | "高2→高3" seed |
| 各 toast | "Demo · ..." prefix 文案 |

実装方針: P0 で API 接続するタイミングで削除 / `#if DEBUG` 限定で preview/snapshot 用に temporary 保留。

### 11.4 全局约束（实装层 — 设计层見上 §3〜§6）

#### R4 — dorm 表示

学生は自分の `dorm_unit` のみ表示。マイページ「あなたの寮」で `1` / `2` / `4` を「男寮 (1 寮)」「男寮 (2 寮)」「女寮 (4 寮)」表示（system_features §3.3）。

#### 通知

- **push (APNs)**: 役职決定 / コメント受信 / 学号変更確認 / お知らせ
- **in-app**: 同上 + 承認チェーン更新（push permission 拒否でも in-app 来る）
- email: 学生は受けない（教師のみ R1）

> **⏳ §11.9-I3**: APNs 設定（dev / prod cert / Push Notification capability）は v1 ship までに必要。P0 段階で push framework は組むが実 APNs は P1。

#### オフライン

- 出寮届 submit はオフライン保存 → リトライ（`URLSession.waitsForConnectivity = true`）
- マイページ履歴は last fetch をキャッシュ + pull-to-refresh 更新
- フォーム入力中はオートセーブ（`UserDefaults` で draft 保存、submit 成功 / cancel で破棄）

#### i18n

P0 = **日本語 only**。⏳ §11.9-I4 — 留学生用に英 / 中 toggle は v1.1+。

#### セキュリティ

- access_token / refresh_token = **Keychain**
- 学号 / 房間号 / メール = UserDefaults（暗号化不要）
- **デバッグログに学号 / 名前 / メール出さない**

#### アクセシビリティ

- VoiceOver 対応（Apple HIG 必須）
- Dynamic Type 対応（最低 + 1 サイズまで layout 崩れない）
- 緑 / 黄 / 赤 で意味伝える時必ず icon + 文字 label 併用

### 11.5 状態管理 / Networking layer

```swift
// AppStore (singleton, @Observable)
@Observable class AppStore {
  var session: Session?
  var lockedUntil: Date?
  var lockLevel: Int
  var student: Student?
  var myApplications: [Application] = []
  var pendingApplications: [Application] {
    myApplications.filter { $0.status == .pending || $0.status == .approvedPartial }
  }
  var unreadNotifications: [Notification] = []
}

// APIClient
struct APIClient {
  let baseURL: URL              // env から
  let auth: AuthStore           // token 管理

  func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T
}
```

- `Endpoint` enum で全 endpoint 定義（path / method / body type / response type）
- 401 → `AuthStore.refresh()` 自動呼び → 失敗時 logout
- backend error code → typed Swift error throw（`APIError.accountLocked(until: Date)` など）

### 11.6 機能別 — UI 設計と API 調用映射

> UI の見た目 / 字段 / flow は本档 §3-§7 が真値。本節 = **どの screen がどの backend API を叩くか** の対応表のみ。

| Screen | backend API（参 BACKEND_DESIGN_LOG §5）|
|---|---|
| RegisterStep5（§3.1 §3.9）| `POST /api/v1/accounts` |
| Step2 番号 check | `GET /api/v1/accounts/check?student_no=060218` |
| LoginView（§3.5 §3.6）| `POST /api/v1/sessions/student` |
| ApplyForm submit | `POST /api/v1/applications` + `Idempotency-Key` header |
| ApplicationHistoryList（マイページ §5）| `GET /api/v1/applications/mine?status=&from=&to=` |
| ApplicationDetailView（承認チェーン）| `GET /api/v1/applications/:id` |
| 撤回 button（⏳ §11.9-I7）| `DELETE /api/v1/applications/:id` |
| LogoutView | `DELETE /api/v1/sessions/current` |
| 通知センター | `GET /api/v1/notifications/mine` |
| Token refresh（自動）| `POST /api/v1/sessions/refresh` |

**出寮届 ApplyForm の動的字段（#4）**: kind 切替時 → 不要 field は「非表示 + 値リセット」（メモリ残存防止 + UX 直感）。

**出寮日 #3 制約**:
```swift
DatePicker("出寮日", selection: $leaveDate, in: tomorrow..., displayedComponents: .date)
// tomorrow = Calendar.current.date(byAdding: .day, value: 1, to: Date.now)!
// JST 強制: Calendar(identifier: .gregorian) + TimeZone(identifier: "Asia/Tokyo")
```

**API 失败 → iOS 動作 mapping**:

| backend code | iOS 動作 |
|---|---|
| `INVALID_CREDENTIALS` | failed_count + 1; counter 表示「あと {3-N} 回」 |
| `ACCOUNT_LOCKED` | LockedView 全画面 + counter（locked_until / lock_level） |
| `ACCOUNT_INACTIVE` | error toast「アカウントが無効です」 |
| `LEAVE_DATE_NOT_FUTURE` | DatePicker focus + error |
| `INVALID_KIND_FIELDS` | field-level error highlight |
| `FORBIDDEN_PROXY_SUBMIT` | ありえない（student_id 自動）→ 起きたら logout 強制 |

### 11.7 共通 Component（HTML → Swift 写起こし）

| HTML 要素 | Swift |
|---|---|
| Liquid Glass scan sheet | `View.glassEffect(.regular, in: .rect(cornerRadius: 28))` |
| 中央 ⭐ 点呼 button | `Circle().fill(LinearGradient(...))` + scale animation on press |
| Bottom 3-button nav | カスタム `TabView`（`SwiftUI.TabView` だと中央 action button 不可） |
| iOS 26 native blur | `.glassEffect()` (新 API) — fallback `.background(.ultraThinMaterial)` |
| 顶部点呼 bar | `RollCallStatusBar` view — 全画面 overlay（sheet 出てる時 hidden） |

**HTML の color value をそのまま Swift `Color` 化**:
```swift
// theme.swift
extension Color {
  static let cobalt = Color(hex: "#2b4d8c")
  static let cobaltSoft = Color(hex: "#e5ebf5")
  static let okGreen = Color(hex: "#2f7a55")
  // ...
}
```

### 11.8 テスト + 配信

#### テスト

- XCTest + Swift Testing
- 単体: 学号 generator / 出寮日制約 #3 / 5 step 注册遷移 / kind 切替動的非表示
- snapshot: ApplicationDetailView 各 status 表示
- UI test: 注册 5 step end-to-end → ホーム / 出寮届 submit → confirm → success / locked screen

#### 配信

- Xcode 17+ / iOS 26 SDK
- TestFlight 配信（itsuki 自分のデバイス確認）
- App Store 申請: AC 入試後 / itsuki 卒業後 ⏳

### 11.9 ⏳ 待 itsuki 拍板（P0 阻塞）

> **2026-04-30 進捗**：I1-I10 全部拍板。**残**：I11（実物表対応の動的 chain 表示）。
> **2026-05-27 進捗**：I11 ✅ — `ApprovalChainBuilder.chain(for: kind, isOverseas:)`（`StayListStubs.swift:164-191`）已实装外泊届 3/5 行 + 帰省/帰国 暫定同外泊。帰省/帰国 实物表 evidence 到达后只需调 `holidayChain` 即可。
> **2026-05-28 进度条样式拍板**：itsuki 推翻原「役职名 chip 链」UI，改成**进度横线 + 无名节点**样式 — `StayListStubs.swift chainDots`。规则：(1) 节点不显示役职名，只用圆点状态色（绿 = approved / 灰 = pending / 红 X = rejected）(2) 节点下方一条横线，approved 数量决定绿色填充比例（公式 `approvedCount / total`）(3) **无论 approve 顺序如何，进度只往右推进**（不按时间倒序，按 chain 顺序填进度）(4) 任一节点 rejected → 进度条变红色。理由 = 役职名密集显示太乱（5 役职留学生 chip 占满宽度），节点风格更直观传达「已通过 N 个 / 总共 N 个」。详细联动 → `02_design/system_features.md §7.2.6`。

| ID | 決策 | 状态 |
|---|---|---|
| **I1** | Persistence | ✅ **JWT は Keychain / その他は UserDefaults**（2026-05-02 实装、commit `cf5c9fa`：`Foundation/Network/KeychainService.swift` 新建。理由 = JWT は機密、UserDefaults は明文 plist で脆弱）/ SwiftData は P2 で再検討 |
| **I2** | Networking | ✅ **URLSession + async/await**（Combine 不採用）/ 2026-05-02 endpoint module 5 個実装済（commit `624fea1`+`a992b4f`）|
| **I3** | APNs | ✅ P0 = **framework だけ**、実 push test は P1（学習欠席届と一緒） |
| **I4** | i18n（英 / 中文） | ✅ **不要**（日本語 only）、v1.1 で再考 |
| **I5** | 状態管理 | ✅ **`@Observable`** macro (Swift 5.9+) |
| **I6** | 注册 = 即 active vs 教師承認 pending | ✅ **即 active**（backend D10 連動） |
| **I7** | 学生は届を撤回できる？ | ✅ **可**（leave_date 24h 前まで、backend D3 連動） |
| **I8** | demo scaffold 削除タイミング | ✅ **API 接続後即** + `#if DEBUG` で preview/snapshot 用 temporary 保留 |
| **I9** | 学号 6 桁 入力 UX | ✅ **3 picker**（本档 §3.9.2 既決） |
| **I10** | iOS 26 Min 制約 | ✅ **iOS 26 only** 既決 |
| **I11** | **ApplicationDetailView 承认 chain 显示**（実物表対照、2026-04-30 D4 から）| ✅ 2026-05-27 完成 — `ApprovalChainBuilder.chain(for: kind, isOverseas:)` 実装。**外泊届**: 一般 = 3 行（担任 / 寮務課長 / 管理係）/ 留学生 = 5 行（+ 国際交流部長 / 寮務部長）。**帰省 / 帰国届** chain は暫定で外泊と同一（実物表 evidence 待ち、helper `holidayChain` で差し替え可）。「国際交流課長」役职は存在するが外泊届チェーンには出現しない（他届で関与する可能性）|

### 11.10 P1 / P2 / P3

#### P1
- 路径 B BTR + Universal Link 実装（`com.tomoshibi://checkin?session=&device=`）
- Core NFC framework integration
- 学習欠席届 提出 (Q3 / 19:40 前)
- 通知センター 完成（filter）
- Push (APNs) 実 cert 設定 + production
- マイページ 個人情報 編集（学号 / 房間号 / メール）

#### P2
- 巴士一覧 表示（マイページ「バス時刻」）
- 帰省方法 = bus dropdown（external bus_route_id 関連付）
- 行事予定 表示（Calendar UI）
- 個人デ ータ aggregated（出寮履歴 / 学習履歴 / 点呼履歴 全部 tab）
- 学号 / 房間号 履歴 表示
- 帰寮通知

#### P3
- リクエスト曲（音楽 #37）
- 規律処分 表示（自分の累計減点 / アラート）
- 罚则可視化
- iCloud アカウント連携（バックアップ）

---

**END** — 本档随 iOS 设计新决策累积更新。下次重大变动时加一条"时间线"记录 + 对应 section。

---

## 12. 5-03 工程修復集 + 平台姿态拍板（2026-05-03 追加）

### 12.1 codesign 修復（真機装機ブロック解除）

**症状**: build 成功するが iPhone install 時「The executable is not codesigned」/「No code signature found」で失敗。GUI Signing & Capabilities は正常（LIU YIFEI Team / Apple Development cert / Bundle Identifier OK）。

**原因**: `project.pbxproj` の 3 build configuration（Debug / Demo / Release）に過去のどこかの editing で `CODE_SIGNING_ALLOWED = NO` + `CODE_SIGNING_REQUIRED = NO` がハードコードされていた。GUI 上の signing 設定は装飾、底層 build setting が「サイン禁止」だったため codesign step がスキップされ unsigned `.app` が出力されていた。

**修**: 3 箇所の `CODE_SIGNING_ALLOWED = NO` + `CODE_SIGNING_REQUIRED = NO` を削除（default = YES に戻す）。`project.pbxproj.bak2` バックアップ作成。

**学び**: GUI と底層 build setting の不整合に注意。Xcode は底層 setting を優先し GUI は読み取り表示のみ。

### 12.2 GlassSheet 底部留白修復

**症状**: 自研 bottom sheet（点呼 / FeedbackSheet / HealthSheet / AbsenceSheet / OtherSheet 全部使用）の home indicator 上方に灰色空白が出る。

**原因**: `GlassSheet` 容器が `.ignoresSafeArea(edges: .bottom)` を持たず、safe area 境界で停止していた。

**修**: 外側 VStack に `.ignoresSafeArea(edges: .bottom)` 追加。内部 `.padding(.bottom, 40)` は残し、ボタンは home indicator 上方 ~6pt に配置（iOS 標準 bottom sheet 視覚規範）。

**影響範囲**: GlassSheet を使う全 sheet が一括修正。

### 12.3 注册 AI 头像位置 + loading state

**位置調整**: 「写真を選択 / AI で生成 / デフォルトを使う」の縦並びで AI 按钮が真ん中に挟まる UX 不格好 → AI 按钮を最下に移動（itsuki 拍板）。

**Loading state（perceived performance 戦略）**: Apple Image Playground の sheet 初回開く時 ML model cold start で ~5 秒間隔がある。Apple は public prewarm API を提供しないため真の高速化不可。代替策として:

- 「AI で生成」tap → ボタン即座に「準備中…」+ ProgressView spinner に切替 + `disabled(true)`
- 5.5 秒後の DispatchQueue で兜底復位（cold start 最長覆盖）
- 背景色 70% opacity で視覚 feedback

**実装**: `AuthStubs.swift` `RegisterStep1View` line 587 `@State isLoadingImagePlayground` 追加 + line 690〜 ボタン UI 切替。

### 12.4 行事予定 日历 layout 修復

**症状 1**: タイトル「2,026 年 4 月」に千位分隔符 comma が混入。
**原因**: SwiftUI `Text("\(Int)")` は iOS 16+ 以降 Locale formatting が自動適用され Int を groupedDecimal に変換する場合がある。
**修**: `Text(verbatim:)` で localization を完全 bypass。

**症状 2**: 日付 cell の青ドット（イベント有り標記）が日付数字と重なる。
**原因**: `ZStack(alignment: .bottom)` で数字とドット両方が底部に整列、ドット `.offset(y: -3)` でも数字に重なる。
**修**: `ZStack`（default center alignment）で数字を中央配置 + ドットを `VStack { Spacer(); HStack {...}.padding(.bottom, 3) }` で底部配置。

**実装**: `ScheduleStubs.swift` line 75 + line 119-138。

### 12.5 特別運航便 入口統一（MyPage → Home）

**症状**: Home busCard tap → 旧 `BusView()`（簡素一覧、filter なし）/ MyPage settings「特別運航便」tap → 新 `BusListView()`（filter 付き）。同じ機能 2 箇所、品質バラ付き。

**修**: Home busCard の `router.go(.homeBus)` を `router.go(.busList)` に変更 + MyPage settings から「特別運航便」row 削除。`system_features.md §7.6.2` 入口位置更新。

**実装**: `HomeStubs.swift` line 875 + `MyPageStubs.swift` line 211〜 + `02_design/system_features.md` §7.6.2。

### 12.6 ⭐ 重大决策: Apple Intelligence on-device 推理路线统一（2026-05-03 itsuki 拍板）

アバター生成 / お知らせ AI 要約 / 翻訳 すべて Apple 平台原生 framework で統一実装。クラウド AI API（ChatGPT / Gemini / Claude API）依存ゼロ。

| 機能 | 採用 framework | 必要 OS | デバイス制約 |
|---|---|---|---|
| アバター生成 | Apple Image Playground | iOS 18.2+ | iPhone 15 Pro+ / Apple Intelligence ON |
| お知らせ AI 要約 | Foundation Models framework | iOS 26+ | 同上 |
| 翻訳（日 ⇄ 中） | Translation framework | iOS 17.4+ | 言語 pack download 後オフライン |

**根拠 5 軸**:
1. **クラウド API 依存ゼロ** — 運用コスト 0、API key 管理不要
2. **学生 privacy 完全保持** — お知らせ本文 / 返信内容が第三者サーバに出ない
3. **オフライン可動** — 寮内 wi-fi トラブル時も使える
4. **Apple Intelligence 非対応端末は機能 hide で UX 一致** — 「ボタン無いだけ」、エラーメッセージ無し
5. **Image Playground と統一理念** — app 全体が Apple 平台原生 AI 能力に統一押注

**AC 叙事**: `system_features.md §7.15.12` AC 叙事段に同内容落档。

### 12.7 SourceKit 誤報問題（環境）

**症状**: 編集後に「Cannot find 'T' / 'RouterStore' / 'AppStore' / 'SEED' in scope」が大量に出るが `xcodebuild -sdk iphonesimulator` で BUILD SUCCEEDED。

**原因**: Xcode 26.4.1（release）+ iPhone iOS 26.5（beta）SDK 不整合により SourceKit indexer が module type を解決できない。実際の compile は通る。

**対処**: 真の build 結果のみ信頼。SourceKit の lint 赤叉は無視。⌘B で確認。

**根本解決（後送り）**: Xcode 26.5 beta インストール or iPhone を 26.4 release にダウングレード。当面 Apple Developer から Xcode 26.5 beta を落として upgrade 検討。

---

**END v2** — 5-03 大量改動を反映（§5 重写 + §12 新増）。

---

## 13. 老师公告 iOS 端 完成（2026-05-04 拍板 + 落地）

> spec 共用層 = `02_design/system_features.md §7.15`。本节 = iOS 専属 UI 仕様 + 実装ファイル对応。

### 13.1 itsuki 5-04 拍板

5-03 spec §7.15 で「AI 要約 / 翻訳 = v1.1 後送」だったが、5-04 itsuki の指示で **v1.0 範囲に格上げ**：
- 主页に公告入口 card が無く「機能あるのに UX 上見えない」状態 → HomeView 入口 card 追加
- AI 要約 + 中翻 = AC 叙事 §12.6「Apple 平台原生 AI 三件套」の核心、後送ではなく v1.0 で実装してこそ叙事が立つ → 同日落地
- backend 接続なしでも UX 確認できるよう demo seed 5 件（日本語 / 全寮 + 男寮 mix）+ 数件 reply

### 13.2 HomeView 入口 card（spec §7.15.3）

**位置**: `HomeView` body 内、§2 减点 amber Card と §3 LifeTab の間に新セクション §2.5。

**構成**:
- 📢 megaphone icon + 未読 N badge（red、N>0 のみ）
- 「お知らせ」タイトル + 「N 件未読」or「すべて確認済」サブテキスト
- 最新 1 件 preview（`announcements.first`）= タイトル / 投稿者名 / 相対時刻
- card 全体タップ → `.homeAnnouncements`（一覧 view）

**実装**: `Features/Home/HomeStubs.swift` `HomeView.announcementsCard` + `announcementRelative()` helper。

### 13.3 詳細 view 内 AI 要約（spec §7.15.5）

**Framework**: `import FoundationModels` (iOS 26+)。

**判定**: `SystemLanguageModel.default.availability == .available` で button 表示。Apple Intelligence 未対応端末は **button 自体を hide**（spec §7.15.5「UX 一致」遵守）。

**Prompt 構成**: `タイトル：... / 本文：... / 返信：- author：body ...` を 1 つの文字列にまとめ、「日本語で 1〜2 行に要約してください」と指示。

**UI**: `actionButtonsRow` に sparkles icon + 「AI 要約」/「要約中…」/ 既生成済 = button disable + summary banner 表示（×ボタンで dismiss 可）。

**実装**: `AnnouncementDetailView.generateSummary()` + `summaryBanner` + state `aiSummary / isSummarizing / summaryError`。

### 13.4 公告详情页·正文母语翻译（spec §7.15.5 / 2026-06-12 全面改版）

> 框架：`@preconcurrency import Translation`（iOS 18.0+ 程序化接口）。
> `@preconcurrency` 是必须的：`TranslationSession` 未标 Sendable，Swift 6 完全并发下从 `.translationTask` 的 MainActor 闭包调 nonisolated 的 `translate` 会报「sending session」数据竞争——这是苹果框架并发标注没跟上 Swift 6 时的官方过渡手段。

**2026-06-12 改版（废弃旧的系统翻译浮层 `.translationPresentation`）**：
- 旧实装只是弹屏幕中央一个系统小窗。itsuki 看实机截图后否决 →「不要弹框，要把本文本身翻成母语」。
- 新实装 = **正文原地替换成译文** + 译文下方「○○ に翻訳しました · 原文に戻す」状态条切回原文；翻译中转圈 / 失败「再試行」。

**对应语言（4 个 — 宿舍留学生主要母语）**：English / 简体中文(zh-Hans) / ไทย(th) / Tiếng Việt(vi)。

**动作**：
- 点「翻訳」→ 设过默认语言就直接翻；没设默认就弹语言选择窗 `langPickerSheet`
- 语言选择窗里勾「次回からこの言語に翻訳する」→ 存 `@AppStorage("translate_default_lang")`（空串 = 每次弹窗）
- `AnnouncementTranslateRunner`（@available(iOS 18.0) 的隐藏子视图，把 `TranslationSession.Configuration` 这个 iOS 18 专属类型从详情页本体隔离出去）在 `.translationTask` 里 `session.translate(body)`；靠 `.id(req.id)` 贴换重建来支持换语言 / 重试
- source: nil（自动判定原文语言，公告是日语）；target = 选中语言

**设置页联动**：`MySettingsView`（原「通知設定」升级为综合「設定」页）的「お知らせの翻訳」section 改默认语言，含「毎回選択する」回到每次弹窗；与详情页共用同一 `translate_default_lang` key。

**iOS 18 未满**：「翻訳」按钮整颗 hide（程序化接口 iOS 18+ 才有）。

**实装**：`HomeStubs.swift` 的 `TranslateLang` enum / `TranslateRequest` / `AnnouncementTranslateRunner` / `AnnouncementDetailView` 翻译 state + `langPickerSheet`；`MyPageStubs.swift` 的 `translateSettingSection`。双 scheme BUILD SUCCEEDED。

### 13.5 AppStore demo seed（⚠️ DEMO-ONLY）

**目的**: backend 起動なしでも simulator + 真機で完全に UX 確認できる。

**仕組み**:
- `AppStore.init()` で `seedDemoAnnouncements()` を call → `announcements / announcementUnreadCount / announcementDetails` 3 つに seed 投入
- `loadAnnouncementList / loadAnnouncementDetail` の catch 句で「seed cache 命中時は throw しない」分岐追加
- `postAnnouncementReply` も catch で local 偽 reply 生成 → cache append
- v1.0 上線前に `seedDemoAnnouncements()` 関数本体 + init() 呼び出し + 3 catch 分岐の DEMO 部分すべて削除

**seed 内容**: 5 件（点呼時間変更 / GW 出寮届 / 男寮浴室点検 / リクエスト曲募集 / 学習対象者更新）+ 3 件の reply chain（学生 + 教員）。UUID 固定（`11111111-...` 〜 `55555555-...`）で list ↔ detail 対応。

### 13.6 一覧 view error 表示順序の修正

**改前**: `isLoading → loadError → empty → list` の優先順 → seed cache あっても backend 失敗時 error banner で隠れる。

**改後**: `!announcements.isEmpty → isLoading → loadError → empty` に変更 → seed/cache 優先表示。backend 接続成功時は seed を上書き、失敗時は seed のまま見える。

### 13.7 実装ファイル映射（5-04 落地分）

| 機能 | 主ファイル | 補助 |
|---|---|---|
| HomeView 入口 card | `Features/Home/HomeStubs.swift` `HomeView.announcementsCard` | — |
| AI 要約 | 同上 `AnnouncementDetailView.generateSummary` | `import FoundationModels` |
| 一键翻訳 | 同上 `runTranslation / startTranslation` | `import Translation`、`AnnouncementReplyRow.overrideBody` |
| demo seed | `Foundation/AppState/AppStore.swift` `seedDemoAnnouncements()` | `init()` + 3 catch fallback |
| spec | `02_design/system_features.md §7.15.11` 表更新 | — |

xcodebuild iPhone 17 simulator BUILD SUCCEEDED 確認済（2026-05-04）。

---

## 14. 宿舍申請类实物表補完 — iOS 影响（2026-05-28）

> **起因**: itsuki 2026-05-28 提供宿舍真实纸质申请表「届け類.pdf」(朝日塾中等教育学校 寮)9 种扫描件。CC + codex 双读核对一致。**共用业务规则**(字段 / 审批链 / 注意事项)已写 `02_design/system_features.md` §7.2(出寮届補完)+ §7.3.5(学習欠席届 在线学习类型 A 補完)+ §7.21(4 种全新申請)+ §8(数据模型)。**本节只记 iOS 专属实装映射**, 不重复业务规则。

### 14.1 iOS 现有承载

- **ApplyForm**(出寮届提交表单)+ **StayList**(申請履歴一覧 / 详情)= 现承载帰省 / 外泊 / 帰国三兄弟
- 学習欠席届 = §7.3.5 类型 B(体調不良 / 特別課題), iOS 已有

### 14.2 实物补完对 iOS 的 4 个影响点

| # | 影响点 | iOS 侧改动 | 优先级建议 |
|---|---|---|---|
| 1 | 帰省分**通常時 / 長期休暇**两种 | ApplyForm 帰省下加 `is_long_vacation` 选择(段控件或子选项) | 低改动, 可进 v1.0 |
| 2 | 出寮届**新字段**(同行者 / 行先都市 / 領収書提交标记 / 食事日本人 vs 留学生差异 / 命名班车西口便等) | ApplyForm 动态字段扩展(§7.2.1 補完), 留学生 / 日本人分支 | 中改动, 建议 v1.0 |
| 3 | 学習**在线学习申请(类型 A)** | 现 iOS 只有类型 B。类型 A 要新字段: 期间 + 周时间表(月~金)+ 契约书凭证 + 3 天前提交 → 扩展学習欠席 ApplyForm 或新建 view | 中改动, 可 v1.1 |
| 4 | **4 种全新表单** | 见 §14.3 逐个取舍 | 待 itsuki 拍 v1.0 范围 |

### 14.3 4 种全新表单的 iOS 取舍

| 实物表 | 谁提交 | iOS 学生端做不做 | 理由 |
|---|---|---|---|
| 寮生行事企画申請書(様式4-2) | 学生 / 团体 | ✅ 需新 ApplyForm + 列表 | 学生主动提交 |
| 寮日課変更願(様式9) | 责任者(老师 / 干部) | ❌ 大概率不做 iOS 学生端 | 普通学生不提此表, 归老师 Web |
| 冷蔵庫購入届 | 学生 | ✅ 需新 view(含 A / B 商品选择) | 学生提交, 但采购 + 缴费流程复杂 |
| 物品所持許可願(様式2-1) | 学生(+ 家长盖章) | ✅ 需新 ApplyForm | 学生提交 |

### 14.4 iOS 实装优先级建议(等 itsuki 拍 v1.0 范围)

- **最小做法**(若 v1.0 只扩出寮届): 影响点 1 + 2(现有 ApplyForm 扩展), 新 4 种 + 在线学习放 v1.1
- **完整做法**(若 v1.0 全做): 影响点 1-4 全做, 工作量大 — 3 个新 ApplyForm(行事企画 / 冷蔵庫 / 物品所持)+ 在线学习 view + 出寮届字段扩展

### 14.5 跨端同步状态

| 端 | 状态 |
|---|---|
| 共用业务规则 | ✅ system_features.md §7.2 / §7.3.5 / §7.21 / §8 已写 |
| iOS 具体 view / 字段 | ✅ **实装完成（2026-05-28，见 §14.6）** |
| Android | ⏳ 待 Android 会话同步 ANDROID_DESIGN_LOG |
| 老师 Web(审批 / 处理) | ⏳ 待 Web 会话同步 WEB_DESIGN_LOG |
| 后端(model / API) | ✅ 实装完成（2026-05-28，commit c6ccee0，见 BACKEND_DESIGN_LOG §12）|

### 14.6 iOS 实装完成（2026-05-28 — codex gpt-5.5 xhigh 干活 + CC 审查 + 独立 xcodebuild 验证）

本节只记 iOS 工程层结果。

**改的文件**：
- `ApplyStubs.swift` — 出寮届 StayForm 扩展（contact_phone / companion / dest_cities / is_long_vacation 通常時vs長期休暇 / 命名班车 / 食事日本人vs留学生分支）+ APPLY_TYPES 加 4 新类型 + dispatcher 分派
- `ApplicationsCreateBodies.swift` / `NetworkModels.swift` — 出寮届请求体 + ApplicationOut 补 6 字段 + 4 种新申请响应模型
- `StayListStubs.swift` — `ApprovalRole` 枚举加「校長」case（修帰国届审批链显示 bug）
- `StudyAPI.swift` — 加在线学习 submit/list API

**新建的文件**：
- `Features/Apply/StudyOnlineForm.swift` — 在线学习申请表单 + 我的列表（周时间表月~金动态时间段 + 3 天前限制）
- `Features/Apply/DormLifeForms.swift` — 行事企画 / 冷蔵庫購入 / 物品所持 三表单 + 各自列表
- `Features/Apply/ApplyFormSupport.swift` — 新表单共用的日期 / 时间 / section 辅助
- `Foundation/Network/Endpoints/DormLifeAPI.swift` — 行事企画 / 冷蔵庫 / 物品所持 接口包装

**路由**：`Route.swift` + `RootView.swift` 加 4 个列表路由（dormEventList / studyOnlineList / fridgeList / itemList）。

**工程配置**：`project.yml` 重写 — 加 Debug/Release/Demo 三配置 + 演示版独立 bundle id + DEMO 编译开关 + 两个 scheme（修 codex 跑 xcodegen 擦掉 Demo 配置的回归）。

**验证**：正式版 + 演示版都 `xcodebuild` 编译通过。逐屏运行点查未做（工具限制）。

**没做**：日課変更（设计上 iOS 学生端不做，归老师 Web）。

---

### 14.7 修改届（StayEditForm）接真后端 — IX-004 + 多轮 Codex 收敛（2026-05-31）

「B 类：演示假数据 → 真后端」推进的一环。改届表单原来只调 `StayListMock.applyAmendment` 纯本地 mock，现在接 `PUT /applications/:id`。

**改的文件**：
- `Features/StayList/StayListStubs.swift` — `StayEditForm.load`（已登录→`ApplicationsAPI.detail` 拉真申请预填）+ `submitAsync`（已登录→`ApplicationUpdateBody` 调 PUT）。**修改理由 `amendReason` 发后端新字段 `amend_reason`**（之前 UI 强制填但提交丢、后端看不到）。**日期 / 方法只发真改过的字段**（无条件发出寮日会触发后端「出寮日>今日」校验、误拒只改帰寮的旧届）。audit mapper 加 `application.update` 文案 + 履历显示 amend_reason。修改理由去空白用 `.whitespacesAndNewlines`（防纯换行绕过必填）。演示 / 未登录态仍走 mock。
- `Foundation/Network/Endpoints/ApplicationsCreateBodies.swift` — `ApplicationUpdateBody` 加 `amend_reason` 字段（snake_case 直接对齐后端，nil 不发）。

**后端配套**（详见 BACKEND_DESIGN_LOG §12 / 2026-05-31 行）：加 `amend_reason` 字段写 audit、改届后 status 重置 pending、`returned` 可编辑、no-op 守卫、audit 老师范围检查。

**验证**：生产 + 演示双 scheme `xcodebuild` BUILD SUCCEEDED；后端 pytest 201 passed；5 轮 Codex 5.5 xhigh 审查（每轮挑出真问题→核实→修→复审到收敛）。

---

### 14.8 当前用户接 /me — IX-008（2026-05-31）

73 处写死的演示假用户 `SEED.user` → 登录拉真实用户。

**改的文件**：
- `AppStore.swift` — `currentUser` + `displayUser = currentUser ?? SEED.user` + `loadMe()`（拉 `/me` → `mapMeToUser` → 设 currentUser **并写回 SEED.user 当安全网**覆盖没法用 app 的站点）；登录 + 启动调 loadMe；登出 didSet 清 currentUser + SEED.user 复位 `demoUserSeed`（防真实用户残留）。
- `AuthAPI.swift` — `StudentMeOut` + `StudentsAPI.me()`。
- `SEED.swift` — 加 `demoUserSeed` 不可变副本（登出复位用）。
- `HomeStubs.swift` — 7 处 `SEED.user` → `app.displayUser`。
- `MyPageStubs.swift` — 学習卡片去隐藏门控（常显）+ `MyStudyView` 非学習対象显「学習対象外です」。

**自挑的值**（itsuki 拍板）：统计字段（points/迟到/欠席）真人先 0（4.5 是 demo）；isStudyTarget 默认 false（老师后台手动设的才是）；UI 入口可见、点进去显「不需要晚自习」。

**残留**：IX-008b 扣分统计接入 / 老师退回(returned)动作 / is_study_target 后端字段（已记入待办）。Codex 独立审查待额度恢复补。

**验证**：生产 + 演示双 scheme BUILD SUCCEEDED；后端 209 passed（含 4 个 /me 测试）。

### 14.9 IX-008 第二阶段审查修复 + IX-008b 扣分统计接入（2026-06-02）

§14.8 的「安全网」做法（登录写回全局 `SEED.user`）经 Codex 5.5 xhigh + Claude 4 维对抗审查双路独立复核，挑出真漏洞。修 + 补完。

**第二阶段修复（commit `6142ef0` iOS 部分 + `d21a2b8`）**：
- **注册路径补 loadMe** — 之前只登录路径拉 /me，注册完进主页 currentUser 仍 nil → 显演示假人到冷启动。`createAccount` 补 `await loadMe()`。
- **loadMe 健壮性** — await 后复查登录态（防登出竞态）；401 清令牌强制重登（不再默默回退假身份）；失败打日志；演示构建 `#if DEMO` 直接 return（真隔离）。
- **注册第一步写 SEED.user 加 `#if DEMO` 守卫** — 生产注册只走真实数据通道，防真名配演示残留统计的混血资料。
- **MyInfoEditView 预填** — `@State` 默认值不再 view-init 抓 SEED.user，改 `.onAppear` 从 `app.displayUser` 填（防 loadMe 晚到 / 切账号不刷新）。

**Batch 2 — 剩余身份站点迁 `app.displayUser`（commit `d21a2b8`）**：MyPage（profileSection / 减点卡 / MyInfoView rows / summaryCard 学習対象）、Apply（StayForm 申請者本人 8 处）、StayList（identitySection ID 卡 6 行）。登出生产构建（`#if !DEMO`）清 changeLog/studyHistory/announcements* 等用户绑定状态（防跨账号残留）。

**IX-008b 扣分统计接入（后端 `0f84be9` + iOS `d21a2b8`）**：后端 `GET /discipline/me/summary` 返当月扣分汇总；iOS `DisciplineAPI.mySummary()` + `loadMe` 拉 summary 填 currentUser 的 points/lateCount/absentCount。真人现显真实当月扣分/迟到/欠席（按当月算，照系统已有约定）。

**残留（低危，文档记）**：3 表单 `@State` 预填（contactPhone/roomNo — 登录路径已真实、仅冷启动窗口旧）+ MyPointsView 图表内部（router-only 视图靠安全网）。

**验证**：iOS 双 scheme BUILD SUCCEEDED；后端 217 passed。

### 14.10 IX-034 请假计数按月接后端（2026-06-02，commit `e0c150c`）

学生端「本月学習欠席届（晚自习请假）次数」原来只在 `AppStore.studyLeaveCountThisMonth`（@Published 内存变量）累加 —— app 重启丢、跨月不清零 = 数字错。接成后端按月真实计数：

- `StudyAPI.swift` 加 `MyAbsenceSummaryOut` Decodable + `myAbsenceSummary()`（GET `/study/absence-requests/me/summary`）。
- `AppStore.loadMe` 拉到 /me + 扣分汇总后再拉请假当月数，写回 `studyLeaveCountThisMonth`（写回前 `guard isAuthenticated` 防登出竞态）。登录 / 注册 / 启动恢复令牌三条路径都会拉真实当月数。
- 演示构建 `#if DEMO` 天然不拉（loadMe 顶部 return），保持初始 3。
- 口径：按 target_date 算当月 / 数全部状态 / 不加硬上限（IX-034 严格只修计数）。

**✅ Codex 6 轮对抗复审收敛关闭**（过夜 GOAL，commit `7a9922c`→`7fecd21`→`508c9b1`→`2dff6b7`→`6c58799`→`30032ea`，pass6 终判「IX-034 收敛可关闭」）：① `submitStudyLeave` 只当月 +1 + 提交后拉 canonical 当月数收敛；② `loadMe` 捕获 `tokenAtStart` 每 await 后比对令牌（含 401 分支）；③ 测试 monkeypatch `study._now_jst` 固定日期去 flaky + 加 12 月跨年边界；④ `formatYMD`/`parseYMD`（StayForm 新建 + StayList 编辑两对）+ 编辑页 DatePicker 时区环境全固定 JST；⑤ 加 `absenceCountRevision` 代次守卫挡旧 summary 覆盖；⑥ 提交/canonical 两个 await 后都抛 `CancellationError` 让调用方静默中止（登出/切用户不导航完成页、不写别人状态）。

**验证**：iOS 双 scheme BUILD SUCCEEDED；后端 221 passed。

### 14.11 IX-009 通知不泄漏假数据（2026-06-02，commit `7e4a180`→`2dff6b7`→`6c58799`，Codex pass5 收敛）

`AppStore.allNotifications` 原 = `pushNotifications + SEED.notifications`（5 条假通知生产泄漏）。改：`SEED.notifications` 声明圈 `#if DEMO`（不进生产二进制）；生产 `allNotifications` = push + `announcementNotifications`（真公告映射成通知卡、未読=公告未読驱动铃铛 badge）；`unreadNotificationCount` 生产用 `push 未読 + announcementUnreadCount`（不依赖懒加载列表），`loadMe` 登录/启动拉公告未読数；公告 4 方法（list/unreadCount/detail/postReply）全加 token-at-entry 守卫防串号；`NotificationsView .task` 进入拉真公告。审批结果/包裹通知聚合 + 通知 id 下标身份 + 时间排序推迟（交接 §7.3）。

### 14.12 IX-007 申请详情页生产不读 SEED（2026-06-02，commit `457077f`，Option A）

`ApplyDetailView.body` 原靠 SEED 的 `item.type` 路由、生产里 `item` 总 fallback 到 `SEED.applications[0]`（恰好 stay 型）才碰巧走对。改 `#if DEMO` 分构建：生产显式只 `StayDetailView(id)`（后端只支持出寮届系 帰省/外泊/帰国），演示保留 SEED 路由 + otherDetailBody（修繕/来訪/代理受取）讲叙事。Option B（真做这几类申请功能）推迟。

### 14.13 低风险残留清理 — 表单预填迁 displayUser + 在线自习日期固定 JST（2026-06-03）

IX-008 Batch 2 收尾的低危残留一并清掉：

1. **3 个表单的 `@State` 预填不再抓全局假人 SEED.user** —— `StayForm.contactPhone`（ApplyStubs）/ `FridgePurchaseForm.contactPhone` / `ItemPossessionForm.roomNo`（DormLifeForms）原 `@State` 默认值直接读 `SEED.user.phone` / `.room`，view init 时一次性捕获、loadMe 晚到 / 切账号都不刷新（冷启动 sub 秒窗口会拿到旧假数据）。改成 `@State` 默认空 + `.onAppear` 带 `didPrefill` 守卫从 `app.displayUser` 填一次（同 `MyInfoEditView.loadCurrentInfo` 做法）。演示构建 `displayUser = SEED.user`，行为不变。

2. **在线自习表单（StudyOnlineForm）日期固定 JST** —— `ApplyFormDate.formatYMD` 漏了 `timeZone`（对比同文件 `displayDateTime` 有），非 JST 设备上 period_from/to 提交口径偏一天；两个 `ApplyDateField`（开始日 / 終了日）也补 `.environment(\.timeZone, JST)`，让选日跟提交口径一致（跟 `ApplyStubs.formatYMD` / StayList 编辑页 IX-034 修复④ 同款）。

验证：生产 + 演示双 scheme `BUILD SUCCEEDED`。

> **Codex 5.5 xhigh 审查加固（2026-06-03，2 中风险已修）**：① `ApplyFormDate.threeDaysLater` 改用 JST 固定日历 `tokyoCalendar`（原 `Calendar.current` 走设备时区，非 JST 设备「最早可选日 = 今天+3」偏一天）+ StudyOnlineForm 两个 `ApplyDateField` 注入 `.environment(\.calendar)` JST。② 3 表单预填加 `.onChange(of: app.currentUser?.account)` 补填 —— 自动登录冷启动 `loadMe` 晚到时，`.onAppear` 生产构建不写假人（`guard app.currentUser != nil`），等真实用户到达再填一次，避免 `didPrefill` 守卫把演示假数据锁死。Codex 终判：删除 Wall 0 问题 / 0 blocker。再次双 scheme `BUILD SUCCEEDED`。

### 14.14 删除寮ウォール（学生掲示板）— 落实 4-29 拍板（2026-06-03）

`system_features.md §889` 早在 2026-04-29 就拍板「学生掲示板 🚫 砍」（社区功能不在核心价值 = 点呼/出寮届/学習/扣分），但 iOS 代码里的**寮ウォール**（`WallView` = 宿舍墙 = 学生互相发帖的墙）从没真删 —— 文档砍了、代码漂了 1 个多月，itsuki 反复要求未落实。本次删干净：

- `CommunityStubs.swift` 删 `WallView` / `WallNewView` / `WallDetailView` 3 个 struct + 各自 `#Preview`（§10–§12，约 295 行）
- `Route.swift` 删 `homeWall` / `homeWallNew` / `homeWallDetail` 3 个 case + 标题映射
- `RootView.swift` 删 3 行路由映射
- `SEED.swift` 删 `wall` 假数据（5 条假帖）+ `SeedModels.swift` 删 `WallPost` 类型

后端无 wall 表 / Android 无 Wall 屏 → 五端仅 iOS 一处。生产 + 演示双 scheme `BUILD SUCCEEDED`，全工程 0 残留。

> **✅ 同类项已处理（2026-06-04）**：匿名建議 4-29 就拍板砍了（`system_features.md §891`「匿名建議 投稿 🚫 砍」），但代码一直漂着 —— 跟寮ウォール一样「文档砍了代码没删」。本次 itsuki 拍板一并删：iOS 删 `SuggestView`（§16）+ `SuggestFeedView`（§17）+ `SuggestItem` 类型 + `SEED.suggestions` 假数据 + 路由（`homeSuggest` / `homeSuggestFeed`）+ 首页入口卡片；Android 删 `FeedbackScreen` 整屏 + 路由（`Route.Feedback`）+ `AppState.feedback` 字段；teacher_web 匿名建議 tab 5-27 已删。五端 0 残留。

### 14.15 演示数据修正 + 出寮届表单对齐实物表 + 页面切换黑屏修复（2026-06-03，itsuki 逐屏审）

itsuki 实机逐屏看演示版，揪出一批演示假数据矛盾 + 表单跟真实纸质表不符 + 页面切换闪黑，逐条修：

**演示假数据（`SEED.swift` / 各 Stubs）**：
- 删 2 条矛盾申请假数据：`a5`「早帰」（点进去因 `return` 类型误走 `StayDetailView` 显示成帰国届、宿泊先栏塞「晩点呼」）+ `a2`「その他·共用エリア掃除」（宿舍现实无此申请）
- 删 4 处界面 ID 显示（申请列表卡片 `ApplyStubs` + StayList 卡片 + `StayDetailView` headerCard + `otherDetailBody`）—— 内部 `id` 字段保留（路由 / 详情查找用），仅去掉给用户看的「ID: a1」假编号
- 通知 / 主页 / 行事予定 / 包裹确认页去 Amazon 品牌 +「新入生歓迎会 / 食堂」→「誕生日会 / カフェテリア」+ 外泊承认去「田中先生」具名

**出寮届表单对齐实物表（`StayForm`，对照 様式3-1 帰国許可願 + 様式3-2 外泊許可願）**：
- §3「出寮（寮を出る）」/ §4「帰寮（寮に戻る）」删多余括号 →「出寮」「帰寮」
- 「滞在先」→「宿泊先」（実物外泊許可願用「宿泊先」；与 `system_features.md §7.2.1` 一致，原 iOS 漂移）
- 交通方法从单一共用列表拆成 **出寮 / 帰寮两串不同选项**（実物去程 / 回程班次不同）：出寮 =「西口1/2便·金川1/2便」、帰寮 =「西口 / 金川登校便」，共通「寮生特別運行 / JR / 自家用車 / タクシー / 教員 / その他」。删原漂移的「バス + 出寮混入登校便」
- 「教員送迎」→「教員」（実物無「送迎」）
- 「飛行機」从交通 chip 移除 → 帰国坐飞机走 §7 飛行機专属段单独填（航班时刻 ≠ 出寮时刻）；加「寮生特別運行」

**页面切换黑屏（`RootView.swift`）**：去掉 content 的 `.transition(.opacity)` + `.animation(value: router.current)`。opacity 转场中间帧双页半透明露出底层 `systemBackground`（深色 = 黑）→ 视觉「闪黑」。改瞬时硬切；底部导航胶囊 morph 动画独立、不受影响。

**外出申请（`GenericApplyForm`，纯演示桩未接后端）**：删日期 / 帰寮時刻（按提交时刻算）+ 联系方式预填 `displayUser.phone` 可改 + 行き先设真必填；交通手段（出行方式）保留。

联动：`system_features.md §7.2.1` 移动方式段已同步（出寮帰寮选项不同 + 教員 + 飞机单独填）。后端 `leave_method` / `return_method` 为自由文本（`Text` / `str`），本次**无需改**。验证：演示 scheme `BUILD SUCCEEDED`（codex 审查待跑）。

> **✅ itsuki 2026-06-03 拍板**：① 早帰（`return`）/ その他（`other`）申请类型**删掉**（`APPLY_TYPES` 移除两 entry，新建网格不再显示）；② 外泊**不填飞机**（维持现状，飞机段仅帰国）；③ 帰国**隐藏「行先（都市名）」**（`StayForm §5` 行先字段加 `if !isReturnCountry`，帰国只填「宿泊先」住所）。三项已实装，双 scheme `BUILD SUCCEEDED`。

### 14.16 出租车预约「タクシー予約」功能 — 4 端（2026-06-03，itsuki 拍板）

学生外出 / 外泊要坐出租车去车站，希望手机直接预约、老师提前知道并安排车。后端字段 `applications.taxi_reservation_time`（`Time` / nullable，null = 不预约 / 有值 = 想坐车时刻）三种出寮届 + 外出共通。iOS 侧：

- `ApplicationsCreateBodies.swift` 4 个 body（Kishei / Gaihaku / Kikoku / Update）加 `taxi_reservation_time`
- `StayForm`：加 `taxiReserved` 开关 + `taxiTime` 时刻 state + §4 帰寮后「タクシー予約」section（`Toggle` + `TimeField`，全出寮届共通）+ 提交时三 body 带 `taxi_reservation_time`（开关关 = nil）
- `NetworkModels.ApplicationOut` + `StayApplication` + `toStayApplication()` 加字段 → `StayDetailView.fieldsCard` 详情显示「タクシー予約」行
- 外出（`GenericApplyForm`，纯桩未接后端）加 `if isOuting` 出租车 UI 占位
- 验证：演示 + 正式双 scheme `BUILD SUCCEEDED`；后端 221 测试绿、老师网页「タクシー」tab 实装（check_jsx 0 错）。Android 待接后端时做（详见 `ANDROID_DESIGN_LOG.md §10` + TODO N-004）

### 14.17 出租车预约 UI 改交互 — 出寮方法连动（2026-06-04，itsuki 拍板）

§14.16 的独立「タクシー予約」开关框（在 §4 帰寮下面，要先开 `Toggle` 才出时刻）交互被推翻。itsuki 要的是：出寮方法选了「タクシー」就当场在 §3 出寮卡片里露出时刻选择器，不用再去下面单独找一个开关。只管出寮（帰寮方法即使选タクシー也不出预约时刻 —— 后端 `taxi_reservation_time` 只有一个字段，不为帰寮加第二个）。`StayForm` 改动（`ApplyStubs.swift`）：

- 删 §4 帰寮后那整个「タクシー予約」section（`SectionLabel(n: "T")` + `Toggle` + 条件 `TimeField`）
- 删没用了的 `taxiReserved` 开关 state，保留 `taxiTime`
- §3 出寮卡片：出寮方法 `ChipGroup` 下面加 `if leaveMethod == "タクシー" { TimeField }`，标题「タクシー希望時刻」
- 提交逻辑 `taxiTimeValue`：来源从 `taxiReserved` 改成 `leaveMethod == "タクシー"`（三 body 提交点不变）
- 验证：`xcodebuild` 编 `ApplyStubs.swift` 零 error（整体 build 另有 `BusAPI.swift` 未登记进工程的无关报错，是并行会话遗留，待处理）
- 注：下面「外出」表单（`GenericApplyForm` / §14.16 第 4 条的占位）仍是旧的独立开关式，纯桩未接后端，本次不动

### 14.18 申请表单加「寮生特別運行の時刻表」快捷按钮 + 时刻表页接真后端（2026-06-04，itsuki 拍板）

学生在出寮届选移动方式时，想当场看「寮生特別運行」（学校给寮生开的特别巴士）几点发车，不用退出去别处找。出寮方法 / 帰寮方法两组选项里都能选「寮生特別運行」，所以两处下方各加一个按钮跳时刻表。itsuki 要求前后端一起改（不只是 iOS 跳转）。改动：

- `ApplyStubs.swift`（`StayApplyView`，三种出寮届共用）：加 `busTimetableButton`（🚌 + 文字 + `chevron.right`，点了 `router.go(.busList)`），放在出寮方法 + 帰寮方法两个 `ChipGroup` 下面各一个
- `BusListStubs.swift`（`BusListView` 特別運航便一覧）：原来全用 `BusListMock`（假数据），现改成 `.task` 拉真后端 —— 已登录调 `BusAPI.listRoutes()` / 未登录 / 失败回退 mock（巴士时刻是公开参考信息无隐私，兜底假数据无安全风险）。加 `BusRouteMapper`：把后端 `schedule_at`（完整日期时间）按日本时区拆成日期 / 时分 / 曜日，并标出「次便」（第一个未过的便）
- `Endpoints/BusAPI.swift`（新建）：`listRoutes(kind:)` 调 `GET /api/v1/bus/routes`，解包后端 `{items:[...]}`
- `NetworkModels.swift`：加 `BusRouteOut` + `BusRouteListOut` 解码模型，字段对齐后端 `schemas.BusRouteOut`
- 后端 `seed.py`：dev 种子加 7 条巴士便（4 条寮生特別運行 + 3 条平日上下学班车），挂 `shingu`（寮務部長）名下 —— 后端接口 `/api/v1/bus/routes` 早已实装 + 测试，但之前 dev 种子没数据，iOS 拉过去会空
- 验证：`xcodegen` 重生成工程收录 `BusAPI.swift` → `xcodebuild`（iPhone 17 Debug）`BUILD SUCCEEDED`；后端 `test_events_and_bus.py` 20 测试绿；dev 种子真跑 7 条巴士便正确入库

### 14.19 登录空字段校验 + 账号去空格（2026-06-04，itsuki 逐屏审 + codex 复审）

itsuki 实机测：账号密码空着点登录，弹的是「通信エラーが発生しました。電波を確認してください」（通信错误请检查信号）—— 因为 `tryLogin()`（`AuthStubs.swift`）没做空字段校验，直接拿空值请求后端、失败落到 network 分支的提示，跟「用户没填」对不上、误导人。改动：

- `LoginView.tryLogin()`：メール mode 提前返回之后、`#if DEMO` magic 判断之前，加空字段校验 —— 账号或密码（去首尾空格后）任一为空 → `app.showToast("アカウント番号とパスワードを入力してください")` + return，不再发请求
- 账号去空格：加 `let trimmedAcc = acc.trimmingCharacters(in: .whitespaces)`，空检查 / DEMO magic 判断 / 真实 `AuthAPI.loginStudent` 三处统一用 `trimmedAcc`（学号是 6 桁数字、空格永远非法，复制粘贴常带空格）
- **密码不 trim**：原样发后端。codex 建议账号密码都 trim，CC 评估后只 trim 账号 —— 密码可能含用户故意输入的空格、后端 `schemas.py` 只校验长度 6–128 不 strip，砍密码空格反而可能砍掉真实密码。codex 复审同意此取舍
- 顺手（codex 审 §14.17 出租车改交互时挑出）：`StayForm` 加 `private static let TAXI_METHOD = "タクシー"`，原来散在数组定义 / UI 条件 / 提交逻辑三处的字面量「タクシー」全引用这个常量，防将来改文案漏改某处静默失效。`RETURN_TRANSPORTS`（帰寮）里的「タクシー」不参与出租车预约判断，故意不改
- 验证：正式版 `TomoshibiApp` + 演示版 `TomoshibiAppDemo` 双 scheme `BUILD SUCCEEDED`；codex gpt-5.5 xhigh 复审 0 未解决问题

### 14.17 オンライン学習 契約書（合同）文件上传 — 2026-06-04（itsuki 要求）

itsuki：「オンライン学習要可以上传图片，上传合同」+「选择上传时有弹窗选照片或文件，很多 iOS app 都带这个」。生产版（非 demo）。
- 新 `Foundation/Components/ContractFilePicker.swift`：点「契約書を添付」从屏幕底部弹 `confirmationDialog` 三选项「写真を撮る／アルバムから選ぶ／ファイルを選ぶ」。拍照用 `UIImagePickerController` 桥 UIKit（SwiftUI 无原生相机）/ 相册 `photosPicker` / 选文件 `fileImporter`（PDF + 图片）
- 图片统一转 JPEG（`UIGraphicsImageRenderer` 缩放最长边 2400 + 质量 0.8）—— iPhone 拍照默认 HEIC，老师网页浏览器显示 HEIC 兼容差；PDF 原样
- `APIClient` 抽出 `decodeResponse` 共用 + 加手搓 multipart `upload<Res>` 方法；`StudyAPI.uploadOnlineContract`
- `StudyOnlineForm` 第 3 部分加文件选择 + 補足説明；submit 改两步（先建申请拿 id，再传文件；第二步失败提示但不回退申请）
- codex 5.5 xhigh 审出并修：multipart 文件名去 CR/LF/引号防 header 破坏 / 提交按钮加 `isSubmitting` 防连点重复申请 / 相机用 `isSourceTypeAvailable(.camera)` 不可用时不显示拍照项防崩
- 验证：双 scheme `generic/platform=iOS Simulator` `BUILD SUCCEEDED`
- ⚠️ 未做（记 TODO）：第二步上传失败后列表无补传入口 / 学生看不到自己已传的合同预览 / 契約書是否强制（现「任意」）待 itsuki 拍板

### 14.20 マイページ精致化 + 外出申請を単一先生確認に — 2026-06-04（itsuki 实机审）

**起因**: itsuki 实机看演示版，① 个人页面太丑、「行事予定」做太小；② 外出不需要审查、一个老师确认即可。

**マイページ（`MyPageStubs.swift`）精致化**（沿用现有卡片风格、不换新视觉）:
- 顶部新增「行事予定」日程卡：列今日（含）之后最近 3 条活动（演示版 today 固定 2026-04-23，跟 ScheduleView 一致）+「すべて見る →」入口跳 ScheduleView。原来「行事予定」只是底部设置列表一行小字 → 删掉那行
- 履歴 6 宫格图标：emoji（👤⚖️🤒📄🧹📦）换成统一 SF Symbols（person.text.rectangle / exclamationmark.triangle / cross.case / doc.text / sparkles / shippingbox）+ 38×38 淡 teal 圆角底块，跟三状态卡图标视觉统一
- 删 `EmojiIcon` struct（无人再用）

**外出申請 進捗を 2 步に（`ApplyStubs.swift`）**:
- 外出（`type=="outing"`，走 otherDetailBody）从「提出 → 審査 → 完了・承認」3 步改成「提出 → 先生確認」2 步，去掉審査
- 确认后显示「確認 · 松本 先生」（演示版代表名；真正按登录老师账号自动记录确认者 = 后端待做）
- `StepMeta` 加 `activeNote` 字段，把原硬编码「担当者：松本 先生 · 審査中」改成按步骤数据显示；其它申请类型仍走原 3 步审查，未动

**设计文档**: `system_features.md` §7.2.7 新增「外出申請 — 単一先生確認」规则（与出寮届区别表 + 确认者自动记录 + 后端待实装）

**验证**: Demo / Release 两 scheme `generic/platform=iOS Simulator` 全部 BUILD SUCCEEDED

**未做（记 TODO）**: 后端外出建表 + 确认接口（按登录账号自动记确认者）+ 老师网页确认按钮

---

### 14.21 番号再設定（学年更新）— 学生自设番号 — 2026-06-05（itsuki 拍板）

学号每年变（出席番号年年调），改成学生自设（推翻 4-30 老师代改，spec §4.2）。iOS 学生端：
- `AuthAPI.swift`：`StudentMeOut` 加 `needs_renewal: Bool?`（Optional 兜底，防分阶段部署解码失败）+ 新 `StudentRenewalAPI.renewNumber` 接 `POST /students/me/renew-number`
- `AppStore.swift`：加 `@Published needsRenewal`（loadMe 从 /me 读 / 登出清）+ `submitRenewStudentNo`（令牌守卫 + 成功后 loadMe 收敛新学号、不丢扣分统计）
- `SheetKind.renewStudentNo` + `GlobalOverlays` 渲染分发
- 主页 `needsRenewal=true` 时顶部「学籍番号の更新が必要です」横幅 → 点开 `RenewStudentNoSheet`（HomeStubs）
- `RenewStudentNoSheet`：选 学年/组/出席番号（radioChip + 输入）+ 实时预览新学号 + 撞号 422 原样弹后端日语提示（走 `APIError.unprocessable`）

**验证**：Demo / Release 双 scheme BUILD SUCCEEDED。

### 14.22 最低支持降到 iOS 16 — 2026-06-05（itsuki 拍板）

原最低支持 iOS 26，降到 16。按编译器报错逐个改 iOS 17+ 专属写法：
- `TopRollBar.swift` `symbolEffect(.pulse)` → `if #available(iOS 17)` 判断（16 无脉冲动画）
- `onChange` 两参数（iOS 17）→ 新建 `Foundation/Components/ViewCompat.swift` 的 `onChangeCompat` 跨版本封装（DormLifeForms / ApplyStubs / AuthStubs / MyPageStubs / ContractFilePicker 共 5 处）
- 减点趋势图 Canvas `Text.foregroundStyle`（iOS 17 才返 Text，否则 `ctx.draw` 不认）→ 改 `font(design:.monospaced)` + `foregroundColor`（2 处）
- `project.yml` 三处部署目标 26→16 + 顺带写入 Xcode 推荐设置 `ENABLE_USER_SCRIPT_SANDBOXING` / `STRING_CATALOG_GENERATE_SYMBOLS`

**验证**：双 scheme BUILD SUCCEEDED。

---

**END v2** — 5-04 老师公告 v1.0 完成（§13）; 5-28 申請实物表補完 iOS 影响（§14）+ iOS 实装完成（§14.6）; 5-31 修改届接后端（§14.7）+ 当前用户接 /me（§14.8）; 6-02 IX-008 二审修复 + IX-008b 扣分统计（§14.9）+ IX-034 请假计数按月（§14.10）+ IX-009 通知（§14.11）+ IX-007 详情页（§14.12）+ 6-03 低风险残留清理（表单预填迁 displayUser + 在线自习日期 JST）（§14.13）+ 删除寮ウォール（学生掲示板，落实 4-29 拍板）（§14.14）+ 演示数据修正 + 出寮届表单对齐实物表 + 页面切换黑屏修复（§14.15）+ 早帰/その他类型删除 + 帰国隐藏行先都市名 + 出租车预约 4 端（§14.16）；6-09 iOS 上线缺口 11 功能实装 + codex 4 轮对抗复审收敛（§15）。

---

## §15 [2026-06-09] iOS 上线缺口 11 功能实装 + codex 4 轮对抗复审

施工图列的第二档🟡+第一档代码项共 11 个缺口功能，每功能单独 commit、正式版+演示版双 scheme BUILD SUCCEEDED。

### §15.1 ① 手机点呼签到 — CoreNFC 写 ST25DV Mailbox（最重要的新设计）

按 2026-06-02「架构反转」（手机不联网，用 CoreNFC 把学号写进墙上 ST25DV16K 的 Mailbox，点呼机读走发后端）实装：
- 新建 `Foundation/Network/NFC/ST25DVWriter.swift`：`writeCheckin(studentId:type:)`。写进 Mailbox 的数据格式 = 1字节版本 0x01 + 1字节类型（0x01点呼/0x02学習）+ 16字节 UUID 原始值。ISO15693 自定义命令字节占位 `// TODO[硬件]` 待 ST25DV16K datasheet + 点呼机 `st25dv.py` 对齐。
- `HomeStubs.swift` 点呼 + 学習 `simulate()` 分轨：演示版 `#if DEMO` 保留假动作；生产版 `#else` 真写 ST25DV、本地物理确认（做法 A）不等后端、失败显 fail 态。
- `RollCallAPI.checkin` 注释从旧 nonce 方案纠正成架构反转说明、标学生端弃用勿删（可能给老师代点用）。
- **Swift 6 并发处理**：用 completion handler 版绕开 async Task 闭包的 'sending' parameter data race 检查；`@preconcurrency import CoreNFC` + 类标 `@unchecked Sendable` + NSLock 原子管理 continuation + `withTaskCancellationHandler`（取消时 invalidate session）+ `cancelRequested` 标志把「创建+begin session」整段挪进锁内（经 codex 4 轮复审逐层封住 NFC 取消竞态）。

### §15.2 其余 10 功能（简表）
- ② 图标：保留 itsuki 6-07 做的 Xcode 26 `.icon` 玻璃火苗（不建 appiconset，编译验证 iOS16 出图标）。
- ③⑩ `project.yml`：NFC 用途说明 + 加密合规标志 `ITSAppUsesNonExemptEncryption` + `CODE_SIGN_ENTITLEMENTS` 接线。
- ④ AppStore `ListLoadState` 枚举 + 4 状态字段，减点/点呼/掃除/点歌/遗失物 5 界面空态改三态（加载中/失败/真空），防网断把「有减点」显成「減点なし」。
- ⑤ `RootView` 加 `onChange(of: app.authToken)` 全局令牌守卫（单参 iOS16 兼容），令牌变 nil 统一跳登录。
- ⑥ `displayUser` getter：生产已登录但没拉到资料返回 `User.placeholder` + `profileIsPlaceholder` 标志，不回退演示假人「リュウ イヒ」。
- ⑦ 删 `BusView` 死页 + `.homeBus` 路由；我的页行事卡接 `EventsAPI`。
- ⑧ `PrivacyInfo.xcprivacy` 据实补 6 类数据收集声明。⑨ 删暗色死控件开关。⑪ 通知开关加「接通后生效」说明。

### §15.3 codex 4 轮对抗复审
gpt-5 + high（非预期 gpt-5.5 + xhigh）逐层挖 `ST25DVWriter` NFC 取消竞态：一轮 2 阻塞（session 被 ARC 提前释放 / continuation 跨线程双重 resume）+ 4 重大 + 1 次要 → 二/三轮 M-1 越挖越深 → 四轮核实死锁判断 + 0 阻塞 0 重大收敛。CC 不盲信（指出 codex 高估了 B-2「双重 resume 崩溃」，单线程本不崩）+ 修完自己 xcodebuild 双 scheme 验。

## §16 [2026-06-11] 6-10 全量审查「🔴 重大已验证 5 组」R-1~R-5 清零

6-10 iOS 全量审查逮出 5 组生产版「显示假数据 / 假锁定 / 假病历」缺口。背景：iOS v1.0 只为上架 App Store 占位、学生暂不真用，所以目标是「界面好看完整、不露假数据破绽」（v1.0 不支持手机签到=方案 A，但 6-09 的 `ST25DVWriter` 代码保留留 v1.1，itsuki「别动」）。两个会话做完，双 scheme BUILD SUCCEEDED。

### §16.1 R-1 / R-2 点呼显示链接真（会话 B，方案 B = 动后端补接口）
根因：iOS 从来没有「从后端拉今日本人点呼时间窗 + 判定结果」的链路，所以签到弹窗永远显「点呼時間外」、签到成功硬编码「時間内」、详情页開始/締切写死 07:00/21:00。
- 后端新建学生端 `GET /rollcall/me/today`（`rollcall.py` `my_today_rollcall` + `schemas.py` `MyRollCallTodaySession`，commit `8cdff97`）：返回今日本人寮场次 + 四个 scheduled_* 时间窗 + 我的判定。
- iOS `RollCallAPI.myToday()` + `AppStore.refreshRollStateFromSessions()` 时间窗状态机：用四时间窗 + 当前时刻真实算 idle / 进行中倒计时 / 時間内 / 遅刻，驱动 `rollState` 的 .active/.absent（原本全工程零写入点 = R-2 死件）。`HomeStubs` done hero 用 `checkinKind`、banner 按 rollState（commit `20776b6`）。
- R-1③：profile 接口 join session 带窗口时刻，`ProfileRollCallEntry` 两端加 `scheduled_window_start_at`/`scheduled_on_time_end_at`，详情页生产显真实窗口（commit `9f92d00`）。

### §16.2 R-3 三个点呼上报弹窗防连点（commit `d3d0439`）
`HomeStubs` 的 `HealthSheet`/`AbsenceSheet`/`OtherSheet` 提交无在途守卫，慢网连点重复 POST。照 `RenewStudentNoSheet` 现成范本各加 `@State submitting`：按钮 `enabled` 追加 `!submitting` + title 显「送信中…」+ 生产版 `submit()` 进 Task 前置 `submitting=true`、catch 失败复位让学生重试。

### §16.3 R-4 登录锁定以后端为真值（commit `7841f5a`）
原本 iOS 本地 5 段阶锁定纯内存假戏（杀 app 清零、「永久」无出口），后端真锁 423 / 停用 403 反掉进笼统 server 错误丢日语文案。
- 生产版 401（凭证错、后端尚未锁）只 `showToast` 提示，不再走本地写死倒计时的假 `LockoutView`；演示版 `#if DEMO` 保留本地锁定升级演出。
- 新增 `catch APIError.server(423, let msg)` → 显后端「アカウントロック中（残り約 X 分）」；`catch APIError.server(403, let msg)` → 显账号停用提示。链路核实：后端 `auth.py` 423/403 的 detail 是 `{code,message}` dict → iOS `DetailError.extractMessage` 已支持取 message。
- 本地 `loginFailCount` 保留作纯 UX 计数，锁定真值以后端 423 为准。

### §16.4 R-5 体調報告履歴接真数据（commit `e4078c5`）
`MyHealthView` 原整页 `ForEach(SEED.health)` 无 `#if DEMO`、无后端拉取 → 生产学生看到假人发烧 38 度记录当自己健康史。
- `RollCallReportsAPI.listMine()` 接后端已有的 `GET /rollcall/reports/mine`（缺口在 iOS 侧没 list 方法；后端不按 kind 过滤 → iOS 端 filter `kind=="health"`）。
- `MyHealthView` 改双轨（演示 `SEED.health` / 生产 `.task` 拉 `listMine()`）+ 三态（加载转圈 / 失败可重试 / 真空态），失败也不退回假病历。生产版后端 body 是自由文本（症状/体温/補足 拼成多行）原样显示 + 提交时刻。

## §17 [2026-06-11] app 图标换新 + 首页活动/巴士卡接真（M-1）

### §17.1 app 图标换成 Tomoshibi-icon-1（commit `31a40fc`）
`TomoshibiApp/AppIcon.icon` 内容换成 itsuki 6-09 做的新设计图标（青绿线性渐变 + logo 层 + translucency），`AppIcon-1024.png` 同步换成新 1024 图。替换旧红色玻璃火苗。文件名/路径不变 → pbxproj 无需改。双 scheme BUILD SUCCEEDED。（全项目图标统一：老师网页 logo 同日同步换；Android 自适应图标因需合成 logo+渐变层 + 本机无 ImageMagick + 另会话在改 Android，留作专项跟进。）

### §17.2 首页活动卡 + 巴士卡接后端（M-1，commit `fc57edb`）
`LifeTab` 首页「今週の活動」卡 + 巴士卡原直读 `SEED.events` / `SEED.busSchedule` 无 `#if DEMO` → 生产学生看到 2 个月前死假活动/巴士。修法照 `MyLandingView` / `BusListView` 范本：加 `loadedEvents`/`loadedBusRoutes` 两个 `@State`，`.task` 生产版（`#if !DEMO`）拉 `EventsAPI.listEvents`（今日起到次年底）+ `BusAPI.listRoutes`（经 `BusRouteMapper`）。`eventsCard` 用 `#if DEMO SEED.events #else loadedEvents`；`upcomingBus` 从 `loadedBusRoutes`（`SpecialBusRoute`）算今日未过/最近未来第一班，`UpcomingBus` 结构从 `BusLine` 改持 `SpecialBusRoute`，busCard 渲染字段相应改 `ub.route.scheduleAt`/`.direction`/`.date`/`.weekday`。拉失败显「0 件」/「予定なし」不退回假数据。〔同族遗留：`packageCard` 仍读 `SEED.packages`，未在本次范围。〕

## §18 [2026-06-11] 首次进入介绍页重做 + 公告 AI 翻译/总结 + AI 头像启用

> 起因：itsuki 要「新用户初次进入用最少文字页数快速建立对 app 的认知」（v1.0 一大批用户进来），且要在介绍页加一页 Apple Intelligence 功能。AC 角度：真正的用户设计从用户视角思考。过程中 CC 两次拦下「宣传 app 里不存在/不可用功能」的坑（详 raw `2026-06-11_iOS介绍页+AI功能`）。

### §18.1 介绍页（OnboardingView）重做 4 页 + 只显示一次（commit `fa05f17`）
- 原 3 页介绍（点呼/申请/生活）自 5-07「不每次启动都弹」拍板后变孤儿页（无任何活路由指向，谁都看不到）。本次重做并真正接回启动流。
- **方案 B「学生的一天」4 页**：① タッチで点呼（用「タッチで」泛指 — itsuki 拍板「ios app 跟卡无关」，不提卡也不提手机；v1.0 不支持手机签到）② 外泊も帰省もアプリから ③ 自分の記録をいつでも ④ AI でもっと便利に（一键翻译/总结公告 + AI 头像，带机种小字）。每页 1 图标 + 1 标题 + 副标题（或 AI 页 3 行功能 + 小字）。**副文案全部不带句号「。」**（itsuki 拍板）。
- **无「スキップ」按钮 — 所有人首次必须看完 4 页**（itsuki 拍板，6-11 看完初版后撤掉 skip）。
- **只显示一次**：`SplashView` 加 `@AppStorage("hasSeenOnboarding")`。无 token 且本机没看过 → `.onboarding`；`OnboardingView` 最后一页「始める」置标记 → `.replace(.login)`（新用户在登录页点「新規登録」进注册）。有 token 直接 home（老用户不弹），看过的人不再弹（解决 5-07「太烦」）。

### §18.2 公告详情页 AI 一键翻译 + 一键要約（commit `785c206`）
- `AnnouncementDetailView` 正文下加 AI 操作行 + 正文设 `.textSelection(.enabled)`。
- **翻訳**：`import Translation` + `.translationPresentation(isPresented:text:)` 弹系统翻译浮层。iOS 17.4+，**全机种**、设备端、不联网。用 `announcementTranslateOverlay` View 扩展包 `if #available(iOS 17.4)` 安全降级。
- **AI 要約**：`import FoundationModels` + `LanguageModelSession { 指令 } / respond(to:)` 调设备本地 3B 模型生成日文要点，结果 `.medium` sheet 展示。**iOS 26+ 且 Apple Intelligence 机种**（`SystemLanguageModel.default.availability == .available`）才显示按钮，封装在 `AnnouncementAI` enum（成员标 `@available(iOS 26.0)`）。

### §18.3 重新启用 AI 头像生成（Apple Image Playground，commit `c5ce9a0`）
- 注册第 1 步「AI で生成」按钮原被硬编码 `supportsImagePlayground = false` 禁用（怕 18.1+ 的 `@Environment(\.supportsImagePlayground)` 在低部署目标编译失败）。
- 本次启用：把 18.2 专属 API（`@Environment(\.supportsImagePlayground)` + `.imagePlaygroundSheet(isPresented:concept:onCompletion:)`）全部隔离进 `AIAvatarGenerateButton` 子视图（标 `@available(iOS 18.2)`），父视图只在 `if #available(iOS 18.2, *)` 分支挂它 → 部署目标 16.0 照常编译，旧机种/未开 Apple Intelligence 不显示。

### §18.4 机种门槛事实（写进 AI 页小字）
- **翻译**：Translation 框架，iOS 17.4+，全机种（不需要 Apple Intelligence）。
- **AI 要約**：FoundationModels，iOS 26+ 且 Apple Intelligence 机种（iPhone 15 Pro / Pro Max + 16 全系，A17 Pro 芯片以上）。
- **AI 头像**：Image Playground，iOS 18.2+ 且 Apple Intelligence 机种。
- 故 AI 页小字只声明「AI 要約とアバター生成は iPhone 15 Pro 以降（Apple Intelligence 対応機種）が必要」—— 翻译全机种可用不设限。
- 工具链：Xcode 26.5 + iOS 26.5 SDK，三框架（Translation/FoundationModels/ImagePlayground）全在 SDK 里，弱链接。正式版 + 演示版双 BUILD SUCCEEDED。

### §18.5 [2026-06-11] 老师公告主页入口补全（itsuki 发现孤儿页）+ 后端对齐核对
- **缺口**：itsuki 看主页发现没有「お知らせ（老师公告）」入口。CC 全 app grep 确认 `AnnouncementListView`（公告一覧）+ 详情页代码都在，但**没有任何地方导航到 `.homeAnnouncements`** —— 主页无卡、铃铛（通知中心 NotificationsView）也不连公告、唯一导航是「列表内卡片→详情」但列表本身打不开。= 老师在 teacher_web 发了公告，iOS 学生从任何地方都进不去（跟介绍页同类「页面做了没接入口」病）。讽刺的是 §18.2 的 AI 翻译/要約刚挂在这个谁都打不开的详情页上。
- **修复**：`LifeTab` 主页卡片列**首位**加 `announcementCard` → `router.go(.homeAnnouncements)`。megaphone 图标 + 未读角标（`app.announcementUnreadCount`，与铃铛同源）+ 副标题显最新公告标题（`app.announcements.first.title`）/ 兜底「未読 N 件」/「寮からのお知らせ」。生产版 `.task` 加 `try? await app.loadAnnouncementList()` 让卡显真实最新。
- **后端对齐核对（itsuki 要求）**：iOS ↔ backend `/api/v1/announcements` 全链路逐字段比对 = **完全对齐，零漂移**：① 接口路径（GET list/unread-count/{id}、POST {id}/replies、DELETE {id}/replies/{rid}）一字不差 ② `AnnouncementBrief` 10 字段（含 `body_summary`/`is_read`/`reply_count` snake_case 映射）③ `AnnouncementDetailOut` 9 字段 + replies ④ `AnnouncementReplyOut` 6 字段 ⑤ unread_count ⑥ scope（后端 Literal[all/male/female]、iOS String 兼容）。数据层不需改。
- 正式版 + 演示版双 BUILD SUCCEEDED。
- **连带修演示版「通信エラー」**：补入口后 itsuki 一点进列表就报通信错误 —— 孤儿页从没被打开过，所以演示版从来没人发现它的三个 load（list/detail/unread-count）**没有 `#if DEMO` 分支**，演示版直接连真后端（无网/无真令牌）必报错。修：`SEED.swift` 加 3 条假公告（含全文 + 回复）+ 三个 load 加 DEMO 分支走 SEED + 主页 `.task` 改无条件拉（已 demo-aware）。这属编译期数据切换（生产版不含），非「上线前必删 scaffold」。

## §19 [2026-06-13] 特別運行便一覧：只显示特別便 + 日语汉字 運航→運行 统一（commit `57c8398`）

> 起因：itsuki 截图反馈三点 —— ① 这页只该显示特別運行便、不显示通学便 ② 每行徽章该用全称「特別運行便」不是缩写「特別便」 ③ 标题该是「特別運行便」。

### §19.1 只显示特別運行便、删通学便筛选
- `BusListView.filtered` 改成只保留 `kind == .dormSpecial`（寮生特別運行便），平日通学便（`dailyCommute`）不再显示。
- 删掉顶部「すべて」「特別便」「通学便」三选项类型筛选条（`tabs` + `kindFilter` state + 横向 chip ScrollView 全删）—— 只剩一类后筛选已无意义。保留下方「空港送迎便のみ」开关（提交帰国届选机场班次时用）。
- 每行徽章 `BusKind.dormSpecial.label`「特別便」→「特別運行便」（全称）。

### §19.2 日语汉字 運航 → 運行 统一（itsuki 直觉纠对了代码错字）
- itsuki 反馈写的是「運行」，但界面标题原本写「運航」。查证：**運航** 专给船 / 飞机用、**運行** 才是巴士 / 电车（按时刻表跑的车）的标准日语 —— 班车是巴士，itsuki 的「運行」才对，代码的「運航」是错字。
- 项目里「運行」本就是主流（SEED 假数据 `notice`、申請表「寮生特別運行」选项、出寮帰寮表单、`NetworkModels` / `BusAPI` 注释约 15 处），只有本班车界面的标题 + 路由名（共 6 处）落单用「運航」。
- 修：6 处「運航」全统一成「運行」—— `BusListStubs.swift`（label / 标题 / MARK / 枚举注释）+ `Route.swift`（`.busList` displayName + 注释）+ `MyPageStubs.swift`（2 处注释）+ `ApplyStubs.swift`（1 处注释）。
- ⚠️ 本设计档案早期章节（§12.5 标题 / §14.18 等）仍存历史「運航」写法，属当时记录，未回溯改。

### §19.3 验证
- 正式版 `TomoshibiApp` + 演示版 `TomoshibiAppDemo` 双 scheme（`iPhone 17 Pro`）**BUILD SUCCEEDED**。
- 改动只动注释 / 显示字符串 + 删筛选 UI，无字段 / 接口 / 数据层变化（后端 `/api/v1/bus/routes` 不动）。

---

## §20 上线签名 / 构建配置登记（⭐ 配置真值表 — 这类「外部账号/编号」值的登记位）

> 生效真值在 `03_dev/student_ios/v1/project.yml`（这里是人读的对照登记）。Team ID 不是密码、是半公开标识，进公开仓库属正常。

| 项 | 值 | 说明 |
|---|---|---|
| **苹果开发者 Team ID（团队编号）** | `DCQ2KT5ZA9` | itsuki 2026-06-11 提供。`project.yml` 的 `DEVELOPMENT_TEAM`。Archive/上架签名用 |
| 正式版 bundle id | `com.itsuki.tomoshibi` | App Store 上架的应用唯一身份号 |
| 演示版 bundle id | `com.itsuki.tomoshibi.demo` | 演示版独立 id，可与正式版同机共存 |
| 测试目标 bundle id | `com.itsuki.tomoshibi.tests` | 单元测试 bundle |
| 签名方式 | Automatic（自动） | Xcode 按 Team 拉/建描述文件 |
| 签名开关 | `CODE_SIGNING_ALLOWED/REQUIRED = YES` | 2026-06-11 开（原全程关）；Archive 需 Xcode 登录该开发者账号 |
| 最低系统 | iOS 16.0 | itsuki 2026-06-05 拍板 |

**⚠️ Archive 上架仍需 itsuki 在 Xcode 做**：① Xcode → Settings → Accounts 登录该开发者 Apple ID（CC 的 headless 构建拿不到登录态/描述文件）② 苹果后台为 `com.itsuki.tomoshibi` 开推送能力 + 生成 APNs 证书（若 v1.0 上推送）。CC 侧只负责把 project.yml 配好 + 模拟器构建验证不破。

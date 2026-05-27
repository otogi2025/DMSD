# Tomoshibi 学生 iOS App · 设计决策完整归档

> **作用**：itsuki 提过的所有 iOS 设计要求 + 自主决定 + 待决清单的完整归档。防遗忘 / 下次会话快速恢复 context / AC 素材 / Claude Design prompt 的 single source of truth。
> **建立**：2026-04-22 晚 by [Mac-demo-sprint]
> **最后更新**：2026-05-27（§实装进度速查表 5 个 🟡 全 ✅ — 5-27 深夜审查 + 早段 catch 修 + StayDetail 切真 API 全落地）。早些更新：2026-05-21 A-029 / 2026-05-03（§3.9.2 注册 flow 5→6 step + §3.12「登録コード入力」）/ 2026-05-02 §11.9 I1/I2 / 2026-04-22 晚 Round 1
> **同型档案对照**：`teacher_web/WEB_DESIGN_LOG.md`（老师 Web 的等价档）

## ⚠️ 实装进度速查表（2026-05-27 全 ✅ 化）

| 层 | 进度 | 说明 |
|---|---|---|
| 设计文档（本文） | ✅ ~95% | 989 行设计，主体 v2 已落 + 5-03 注册 flow 更新 |
| Network/Endpoints | ✅ | Auth / Applications / Study / Announcements / RollCall 全加（A-024 已修） |
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
| 2026-04-22 夜 · 19:10 | itsuki 拍板 **外泊申请提交期限规则**：出発日の属する週の水曜日 23:59 または 出発 48 時間前、いずれか早い方。iOS App 側は期限後の送信ブロック必須（UI：送信ボタン disabled + 説明「期限を過ぎました。寮監と直接相談してください」+ 寮監室への導線）。Web 側は既に `teacher_web/round3/src/components/applications.jsx` + `outstay-detail-modal.jsx` に実装済（`outstayDeadline()` helper / 列表の 期限 badge / 詳細 modal の §提出期限 section + 面談必要アラート + 説明 banner）· iOS Round 1/2 Prompt を書くときにこのルールを申請 flow step 2 or 3 に加えること |

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
- Community 全量（宿舍墙 / 点歌 / 遗失物 / 活动 / 巴士 / 建议）
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

**⚠ 権威源は `02_design/system_features.md §3`。ここは iOS 視点の抜粋 + App 固有の UI 仕様のみ。**

#### 3.9.1 編碼

`学年(2) + 組(2) + 番号(2)` = 6 桁、例 `060218` = 高 3 / B 組 / 18 番。

- 学年: 中 1=01, 中 2=02, 中 3=03, 高 1=04, 高 2=05, 高 3=06（6 年制中高一貫）
- 組: A=01, B=02（当校は B までしか存在しない）
- 番号: 01〜99（班里通し番号）

#### 3.9.2 注册 flow に追加 step

旧 4 step → **新 6 step**（2026-05-03 itsuki 拍板で **step 6 登録コード** を最終 step に追加 — App Store 公開対策 §3.12）:

| Step | 字段 |
|---|---|
| 1 基本情報 | 氏名 / 生日 / 性別 / アバター |
| **2 学年・組・番号** ⭐ 新設 | 学年 picker（中 1〜高 3） / 組 picker（A/B） / 番号 input（数字、01-99）→ 自動で 060218 生成表示 |
| 3 学生類別 | 一般寮生 / サッカー部 |
| 4 房间号 ⭐ 新設 field | 部屋番号 input（例 `M101` / `W203`、validation は §3.10 参照） |
| 5 連絡先 + パスワード | メール / 電話 / パスワード × 2 |
| **6 登録コード** ⭐ 新設（2026-05-03） | 教師発行の 6 桁数字コード input（§3.12 / 共用層 §7.16） |

**UI 規則**:
- Step 2 で学年・組・番号が 3 つとも入ると、下に「あなたの学号: `060218`」を 30pt cobalt で表示（プレビュー）
- 番号重複チェック（後端 `GET /accounts/check?student_no=XXXXXX`）→ 重複時は赤エラー「この番号は既に使用されています。班里最末番号 + 1 で入力してください」

#### 3.9.3 demo seed 更新

リュウ イヒ（itsuki 自身）:
- **旧**: 番号 `00`
- **新**: 学号 `060218`
- 生日 `2006-10-14` → 2026 年 4 月時点で高 3 に在学 → `grade_code=06` と整合 ✅

#### 3.9.4 マイページ 編集

「個人情報」section で学年 / 組 / 番号が編集可能（進級・転校対応）:
- 編集 button 押下 → modal「学年・組・番号を変更しますか？学号が変わります」
- 保存 → §3.11 改动履歴に自動記録 + 老师 Web に通知

---

### 3.10 房间号（2026-04-23 拍板）

**⚠ 権威源は `02_design/system_features.md §4`。**

#### 3.10.1 注册時

- 学生本人が手入力
- フォーマット: `[MW]\d{3}` を推奨だが、demo 段階では **任意文字列許可**（validation なし）
- 性別と `[MW]` の整合チェックは v1.1 で追加（demo 段階スキップ）

#### 3.10.2 マイページ 編集

- read-only / 編集可 の切替は「老师 一括分配 適用中か否か」で決まる
- **demo 段階**: 常に編集可（一括分配未実装のため）
- v1.1 以降: 一括分配 適用後は read-only + 「部屋変更は寮監へ相談してください」文言

#### 3.10.3 一括分配 受信（v1.1 将来機能）

- 老师 Web で `POST /room-assignments/batch` 実行 → 学生 App に silent push
- App 受信 → マイページ房间号 自動更新 + 通知「あなたの部屋が M101 → M205 に変更されました（2026-04-25 09:30 寮監による割当）」
- §3.11 改动履歴に自動記録（actor=teacher）

---

### 3.11 学生改动履歴（監査ログ、2026-04-23 拍板）

**⚠ 権威源は `02_design/system_features.md §5`。**

#### 3.11.1 原則

**学生が App 内で行う情報変更は全て老师 Web から閲覧可能。**

対象フィールド:
- 学号構成（grade_code / class_code / seat_no）
- 房间号（自己編集 + 老师 一括分配）
- メール / 電話 / アバター
- パスワード（変更事実のみ、ハッシュ非記録）
- 氏名（誤入力修正、要老师承認 ⏳ v1.1）

#### 3.11.2 マイページ「変更履歴」項目

- マイページ末尾に「変更履歴」一行 button 追加 → タップで履歴画面（時系列 list）
- 表示項目: `日時 / フィールド名（日本語）/ 旧値 → 新値 / 変更者（自分 / 寮監 / システム）`
- 期間フィルタ: 全期間 / 過去 30 日 / 過去 1 年
- 自分が変更した行のみ閲覧可（他学生の履歴は見えない）

#### 3.11.3 Web 側連携

老师 Web「学生アカウント管理」→ 学生詳細 modal「アクティビティ履歴」tab に時系列表示（WEB_DESIGN_LOG 参照）。

---

### 3.12 登録コード入力（2026-05-03 拍板、App Store 公開対策）

**⚠ 権威源は `02_design/system_features.md §7.16`。ここは iOS 視点の UI 仕様のみ。**

#### 3.12.1 動機

itsuki 2026-05-03 拍板。App Store 上架 = 全人類に配布チャネル開放。登録口にゲートを入れて「物理的に教師に接触できる人」だけが登録できるようにする。経緯詳細は `05_logs/raw/2026-05-03.md §11`。

#### 3.12.2 UI 仕様（iOS 専属）

- **配置**: 注册 flow の **最終 step（step 6）**（パスワード設定 step 5 の次）
- **タイトル**: 「登録コード」
- **説明文**: 「教師に発行された 6 桁の数字コードを入力してください」
- **入力 field**:
  - 6 桁数字専用 OTP 風 input（1 文字ずつ separated boxes 推奨、Apple の SMS 認証 UI 風）
  - キーボードは `numberPad`
  - autofill `oneTimeCode` は **使用しない**（OS が SMS から自動補完するのを防ぐ — このコードは SMS 経由ではないため）
- **submit ボタン**: 「登録を完了する」
  - 6 桁全部埋まるまで disable
- **エラー表示**:
  - 失敗時 → 入力 field を赤く揺らす（haptic feedback：error）+ 下に「コードが正しくないか、有効期限が切れています。教師に再発行を依頼してください。」
  - リトライは即可能（rate limit は backend 側で 5 回 / 分など）
- **戻る**: 戻るボタンで step 5 に戻れる（既入力データは保持）

#### 3.12.3 後段 flow

- submit 成功 → backend が `POST /accounts` を全 step データ + `registration_code` で受信 → コード検証 → DB に学生作成 → 永久 session 発行
- 成功画面 → §3.13 ⭐「ようこそ、{氏名}さん」+ アカウント番号 060218 表示
- 失敗（コード不正 / expire）→ field エラー（上記）

#### 3.12.4 ⚠️ Demo 段階の取扱

`05_logs/raw/2026-05-03.md §11` の itsuki 拍板 = v1.0 から実装。Demo 4-28 は既に終わったので **Demo skip 不要**。新入学シーズン（2026-04 想定）= v1.0 範囲。

実装スコープ:
- Step 6 view（OTP 風 6 桁 input）
- error state（field 赤揺れ + haptic）
- backend API integration（`POST /accounts` body に `registration_code` field 追加）

未実装（後送り v1.1+）:
- Touch ID / Face ID で「最近のコード」を保護して auto-fill — 不要（一度きりなので）
- QR コード経由でのコード入力（教師 Web で QR 表示 → 学生スキャン）— v1.1 検討
- 寮単位ごとに別コード（dorm_unit 別）— v1.1 検討

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

**双端同步**：上架版 fork（`~/dev/Tomoshibi-AppStore/ios/`）+ 主项目（`03_dev/student_ios/v1/`）同步改完 2026-05-07

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

**双端同步**：2026-05-22 主项目 v1 backport 完成（fork 已归档到 `99_archive/2026-05-22_tomoshibi_appstore_fork/`，主项目变唯一开发线）。改动落在 `MyPageStubs.swift` MySettingsView（state + accountDeletionSection + performDelete）+ `AuthAPI.swift` AccountsAPI.deleteMyAccount()。

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

### 5.1 全体構造（上 → 下）

```
PageHeader「マイページ」
├─ profileSection（紧凑：avatar 56pt + 氏名 + アカウント番号 + 寮室 Pill 一行）
├─ ⭐ 学習ステータス Card（学習対象学生のみ表示）
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

### 5.2 旧版（4-22 設計）vs 方案 B（5-03 拍板）

| 項目 | 旧版（8-grid） | 方案 B |
|---|---|---|
| profile | avatar 64 + name + account + 2 Pill 縦並び | avatar 56 + 紧凑横一列 |
| 学習履歴 | grid 第 9 格（学習対象のみ追加、最下） | 顶部第 2 ブロック Card 化（最显眼） |
| 点呼履歴 | grid 第 2 格（emoji + label） | Card 化 + 含本月统计 |
| 減点明細 | grid 第 3 格（emoji + 数字 badge） | Card 化 + 含点数 + 状态 Pill |
| 履歴 grid | 8-9 件 | 6 件（去掉点呼 / 減点 / 学習） |
| settings | 行事予定 + 特別運航便 + 通知設定 + About + ログアウト | 删特別運航便（5-03 搬到 Home busCard） |

### 5.3 重要性优先级

itsuki 拍板「マイページ で核心信息は概覧 + 詳細入口」モデル（参考 Apple Health / Activity）。viewing 順位:
1. 私は誰（profile）
2. 学習中? OK?（学習 Card）— 学習対象学生のみ
3. 点呼大丈夫?（点呼 Card）
4. 減点ライン大丈夫?（減点 Card）
5. その他履歴（grid 6 件）
6. 設定

### 5.4 統計データ算出（v1.0 demo）

- 学習ステータス: `app.studyState`（idle / upcoming / active / done）+ `app.studyCountdownSec`
- 点呼今月統計: `SEED.rollcall` を state 別 count（時間内 / 遅刻 / 欠席）
- 減点点数: `SEED.user.points`（5-03 = 4.5）+ 阈値判定（< 4 良好 / 4-7 罰掃 注意 / ≥ 8 禁足）— 阈値は §7.12 + RollCall_Spec.md と同じ

> **v1.1 拡張予定**: 学習履歴 statistics（出席率 / 異常回数）/ 点呼トレンド（先月比較）/ 減点 12 月推移 chart（旧版にあった、Card 内 mini chart で復活）。

### 5.5 実装ファイル

`03_dev/student_ios/v1/TomoshibiApp/Features/MyPage/MyPageStubs.swift` — `MyLandingView`（line 51〜）。

5-03 大改の実装ポイント:
- `blocks` 6 件に縮小（点呼 / 減点 / 学習 削除）
- `body` 5 ブロック構造（profile + 状态 Card 群 + 「履歴」header + grid + settings）
- 新 helper: `studyStatusCard` / `rollcallStatusCard` / `pointsStatusCard` / `landingCardBg` / `landingCardBorder` / `monthRollcallStats` / `statBlock` / `studyStateText` / `formatCountdown`
- `settingsSection` から「特別運航便」row 削除（Home busCard へ移設）

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
| §1.4 Home 子页 | 通知 / 快递 / 遗失物 / 点歌 / 宿舍墙 / 活动 / 巴士 / 匿名建议 | 18 |
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
| N8 | 注册激活 | 即激活（推翻 CLAUDE.md "面签" 规则 — §9 同步）|
| N9 | 长按返回时长 | 0.4 秒 |
| N10 | sheet 上顶部 bar | 不显示 |
| N11 | 非点呼时段点中央按钮 | 提示 + 允许演示扫描 |
| N12 | 点呼 sheet 动画源 | CSS 动画（HTML mockup 用）/ SwiftUI 原生 .glassEffect + Animation（实装）|
| N13 | "其他问题" form | 自由文本 + 类型 tag |
| N14 | Home 全寮统计 | 不显示 |
| N15 | 快递未领 badge | 红点 + 数字 |
| N16 | 宿舍墙身份 | **实名** |
| N17 | 点歌 source | Apple Music link paste |
| N18 | 暗色模式 | v1.0 不做 / v2 再做（2026-05-25 推翻） |
| N19 | 横屏 | 不支持 |
| N20 | Demo 切学生 | 砍（注册 flow 取代）|

---

## 9. 跨文档同步（ACTION REQUIRED · 需在本会话 / 下会话执行）

本次 iOS 讨论产生的**跨文档影响**：

| # | 改动 | 目标 | 状态 |
|---|---|---|---|
| 9.1 | `§账号规则` "面签激活" → "即激活" + 新增锁定升级策略 | `CLAUDE.md`（主指令档）| ✅ **2026-05-26 自动消除** — commit `d608846` CLAUDE.md 重写到 QTS 模式时整段被砍，不再含「面签激活/即激活/账号规则」字样 |
| 9.2 | 老师 Web 加"学生账号管理 / 密码重置"页 | `teacher_web/round3/src/components/accounts.jsx` | **✅ 2026-04-22 晚 [Code-Agent] 直接在 Round 3 里加完** — 番号/氏名/部屋/邮箱/电话/最终登录/状态 列表 + 详情 modal（プロフィール 编辑 + 密码重置 + ロック解除 + アクティビティ 时间线）。Shell 左 nav 加「学生アカウント管理」入口。seed 24 人（00 = リュウ イヒ，01-23 真实学生） |
| 9.3 | 老师 Web `/discipline` 加"被锁定学生通知"card | 同上 | 🔄 **2026-05-26 转 Web 端 TODO** — 见 `00_admin/TODO.md` §🆕 v1.0 后新功能候选 N-003。归属从 iOS 设计日志 §9 移到 Web 端 backlog（这条本来就是 Web 活，iOS 侧不动） |
| 9.4 | `sprint.md` / `scope_tier.md` 纳入"iOS App 注册 flow + 锁定策略" | `demo_4-28/sprint.md` + `scope_tier.md` | ✅ **2026-04-29 自动消除** — commit `d590159` demo_4-28 整段归档到 `99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/`，sprint.md / scope_tier.md 已不在活跃区，无需再同步 |

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
> **单 repo**（2026-05-06 退役独立 repo / 2026-05-21 C-012 清理）: Swift 实装直接在 `03_dev/student_ios/v1/TomoshibiApp/`，跟 backend / Android / Web / 点呼机 全在 DMSD 单 repo 里。原跨 repo 同步规则（`bin/sync-ios-refs.sh` / `Tomoshibi-iOS/refs/`）已废。
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

memory `project_demo_scaffolds_to_remove_before_v1.md` 真值。具体ファイル:

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

**学び（itsuki AC 素材化済 — raw/2026-05-03.md §11）**: GUI と底層 build setting の不整合に注意。Xcode は底層 setting を優先し GUI は読み取り表示のみ。

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

**AC 叙事**: `raw/2026-05-03.md §14` ⭐⭐⭐ #AC候選。`system_features.md §7.15.12` AC 叙事段に同内容落档。

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

### 13.4 詳細 view 内 一键日中翻訳（spec §7.15.5）

**Framework**: `import Translation` (iOS 17.4+ presentation, iOS 18+ programmatic)。

**動作**:
- ボタン押下 → `translationConfig` を `Locale.Language("ja") → Locale.Language("zh-Hans")` で設定
- `.translationTask(translationConfig) { session in ... }` modifier が自動再実行
- `session.translate(batch:)` でタイトル / 本文 / 全 reply を 1 回の batch で翻訳
- `clientIdentifier` で振り分け → `translatedTitle / translatedBody / translatedReplies[UUID]` cache
- `showOriginal = false` で表示切替（cache 命中時は再翻訳せず即時切替）
- 再押で `showOriginal = true` で原文に戻す（cache は破棄しない）

**UI**: `actionButtonsRow` 内 character.bubble icon + 「中国語に翻訳」⇄「原文に戻す」/「翻訳中…」。

**実装**: `AnnouncementDetailView.startTranslation() + runTranslation(session:)` + state 6 個。`AnnouncementReplyRow` に `overrideBody: String?` 追加して翻訳済本文を注入。

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

**END v2** — 5-04 老师公告 v1.0 完成（§13 新増）。

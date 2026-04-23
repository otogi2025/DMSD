# Tomoshibi 学生 iOS App · 设计决策完整归档

> **作用**：itsuki 提过的所有 iOS 设计要求 + 自主决定 + 待决清单的完整归档。防遗忘 / 下次会话快速恢复 context / AC 素材 / Claude Design prompt 的 single source of truth。
> **建立**：2026-04-22 晚 by [Mac-demo-sprint]
> **最后更新**：2026-04-22 晚（Q/N 全答 + Round 1 Prompt 落盘）
> **同型档案对照**：`teacher_web/WEB_DESIGN_LOG.md`（老师 Web 的等价档）

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

**⚠ 権威源は `02_design/system_features_v0.1.md §3`。ここは iOS 視点の抜粋 + App 固有の UI 仕様のみ。**

#### 3.9.1 編碼

`学年(2) + 組(2) + 番号(2)` = 6 桁、例 `060218` = 高 3 / B 組 / 18 番。

- 学年: 中 1=01, 中 2=02, 中 3=03, 高 1=04, 高 2=05, 高 3=06（6 年制中高一貫）
- 組: A=01, B=02（当校は B までしか存在しない）
- 番号: 01〜99（班里通し番号）

#### 3.9.2 注册 flow に追加 step

旧 4 step → **新 5 step**:

| Step | 字段 |
|---|---|
| 1 基本情報 | 氏名 / 生日 / 性別 / アバター |
| **2 学年・組・番号** ⭐ 新設 | 学年 picker（中 1〜高 3） / 組 picker（A/B） / 番号 input（数字、01-99）→ 自動で 060218 生成表示 |
| 3 学生類別 | 一般寮生 / サッカー部 |
| 4 房间号 ⭐ 新設 field | 部屋番号 input（例 `M101` / `W203`、validation は §3.10 参照） |
| 5 連絡先 + パスワード | メール / 電話 / パスワード × 2 |

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

**⚠ 権威源は `02_design/system_features_v0.1.md §4`。**

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

**⚠ 権威源は `02_design/system_features_v0.1.md §5`。**

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

## 5. 个人主页（マイページ）内容

深度 = "真的看点呼记录 + 点数 + 个人相关全部"。

- 个人情報（氏名 / 生日 / 性别 / 号码 / 邮箱 / 电话 / 寮分配 / 一般 or サッカー部 — 全 read-only）
- 点呼履歴 list + 详情（N20 → 砍 Demo 切学生；就是 00 号的履歴）
- 減点明細 + 12 月推移 chart
- 処分履歴（罚扫 / 禁足）
- 体調報告 履歴
- 申請履歴（跳 申し込み 或独立）
- 掃除提出 履歴（含评分）
- 快递领取 履歴
- 通知設定
- Tomoshibi について（版本 + AC 署名）
- ログアウト

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
- 暗色模式：**做**（N18 ✅ — iOS App Store 加分 + AC 评审加分 + iOS 26 Liquid Glass 在暗色下效果好）

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
| N18 | 暗色模式 | 做 |
| N19 | 横屏 | 不支持 |
| N20 | Demo 切学生 | 砍（注册 flow 取代）|

---

## 9. 跨文档同步（ACTION REQUIRED · 需在本会话 / 下会话执行）

本次 iOS 讨论产生的**跨文档影响**：

| # | 改动 | 目标 | 状态 |
|---|---|---|---|
| 9.1 | `§账号规则` "面签激活" → "即激活" + 新增锁定升级策略 | `CLAUDE.md`（主指令档）| ⏳ 本会话结束前 commit |
| 9.2 | 老师 Web 加"学生账号管理 / 密码重置"页 | `teacher_web/round3/src/components/accounts.jsx` | **✅ 2026-04-22 晚 [Code-Agent] 直接在 Round 3 里加完** — 番号/氏名/部屋/邮箱/电话/最终登录/状态 列表 + 详情 modal（プロフィール 编辑 + 密码重置 + ロック解除 + アクティビティ 时间线）。Shell 左 nav 加「学生アカウント管理」入口。seed 24 人（00 = リュウ イヒ，01-23 真实学生） |
| 9.3 | 老师 Web `/discipline` 加"被锁定学生通知"card | 同上 | ⏳ 同（未做）|
| 9.4 | `sprint.md` / `scope_tier.md` 纳入"iOS App 注册 flow + 锁定策略" | `demo_4-28/sprint.md` + `scope_tier.md` | ⏳ 本会话结束前评估 |

---

## 10. 下一步

1. ✅ `round1_handoff/Round1_Prompt.md` 已写
2. ⏳ itsuki 扫 Prompt → 找漏洞 / 微调
3. ⏳ itsuki 开 claude.ai Design project → 拖入 `round1_handoff/` 整个文件夹 → 贴 prompt → 让 Claude Design 先出 3 variations
4. ⏳ itsuki 选定 variation → Claude Design Phase B 输出全 73 页
5. ⏳ standalone HTML 下载到本目录 → 代码 agent 接入 SwiftUI

---

**END** — 本档随 iOS 设计新决策累积更新。下次重大变动时加一条"时间线"记录 + 对应 section。

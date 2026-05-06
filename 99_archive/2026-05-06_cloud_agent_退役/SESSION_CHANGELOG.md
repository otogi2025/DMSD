# iOS Swift App · Session Changelog

> 每个 CC 会话的改动清单。会话开始读这里 + `SHARED_DECISIONS.md`；会话结束前追加新条目。

---

## 2026-04-23 · iOS-Swift-CC（Claude · Opus 4.7）

### 大改动

**Flow / Navigation**：
- Splash → **RegisterStep1**（原来是 Onboarding）
- RootView 用 `.safeAreaInset` 挂 TopRollBar / BottomNav（ScrollView 自动避让，不再遮挡内容）
- GlobalOverlays 只剩 sheet / breadcrumb / toast

**Account 规则（跨会话共享，见 `DMSD/00_admin/跨会话_ios_共享决策.md`）**：
- account 6 桁：`年级码(2)+组码(2)+番号(2)` · 高3 B 18 → `060218`
- SEED.user 更新：account=`060218`, +`grade`/`classSuffix`/`seatNo` 字段
- User struct 所有字段改 `var`（支持升学改动）
- Login magic seed 兼容 `"00"` / `"060218"` / email

**Register Step1**：
- 顺序：アバター → 氏名 → 性別 → 生年月日 → **学年** → **組** → **出席番号**
- 6 年制年级 chips（中1 / 中2 / 中3 / 高1 / 高2 / 高3）
- 組 A/B（no C）
- 实时显示「アカウント番号 060218」
- 生年月日：wheel picker + ja_JP locale（不再是英文 Oct）
- 次へ 保存到 `SEED.user`

**Foundation atoms 对齐 HTML（JSX c281cafa / 8b866e02）**：
- PrimaryButton：fontSize 15→16 · semibold→bold · btnGradRadial (RadialGradient 35%/28%) · shadow rgba(31,107,116,0.24) y=4 · kerning 0.32 · contentShape（整体 hit-test）
- Field：label fontSize 12→13 · spacing 6→7
- TField：height 46→48 · bg hairSoft→pearl · focus border primary
- GhostButton / GhostButtonFull：contentShape 整区 hit-test

**UI**：
- Splash：自绘 teal 火焰 → `Image("TomoshibiFlame")` Asset（灰色火焰 Image #47）+ 白底 rounded card
- AppIcon：1024×1024 同灰火焰
- TopRollBar：idle 不显示（user 觉得浮着挡内容）· 圆角 capsule（原 `.rect` 无圆角）
- BottomNav：圆角胶囊 + `.glassEffect(.regular, in: .capsule)` 直接 modifier（不在 `.background` wrap，blur 更强）· マイページ icon moon.stars→person.fill · 贴底（removed 6pt padding）· contentShape fix tap 穿透
- HomeView：移除 58 / 108 pt Color.clear placeholder（safeAreaInset 接管）· 点数 Card pill 动态：idle=`来月より清掃対象` / active=`点呼中 · X:XX` / late=`遅刻` / done=`時間内にチェックイン`
- MyLanding：加 `PageHeader(level: 1)`（左上 Home icon → `.home`）

**StayForm（外泊申請）**：
- 本人連絡先：从 SEED.user 读（学年・組・番号・氏名・電話）· 删 WeChat 行
- 方法 §3：ChipGroup 改用 iOS 16+ `Layout` protocol 的 `FlowLayout`（修了往路/復路 label 跟 chip 混排 bug）
- 宿泊先 §4：RadioCard（日本人宅/留学生宅/ホテル/実家）**删掉** → TField 自填
- 食事 §5：每天 checkbox 表格 **删掉** → 開始日+朝/昼/夕 〜 終了日+朝/昼/夕 期间选择

**日文自然化**（user 反馈）：
- `来月清掃罰則予定` → `来月より清掃対象`
- `快递 · N 件待領` → `宅配便 · N 件未受取`
- `快递領取履歴` → `荷物受取履歴`
- `今日到着` → `本日到着`
- `父方の叔父` → `叔父 / 祖父母 / ホテル予約`
- 「点呼提醒」`2 桁番号` → `6 桁番号`

**RegisterStep3 邮箱 hint**：
- 加「学校のメールアドレスでも、ご自身のメールアドレスでも登録できます」

**RegisterStep2 点呼時間**（user 数据）：
- 一般寮生：`平日 朝 7:40 / 晩 22:00 · 土日 朝 8:50 / 晩 20:00`
- サッカー部：`平日 朝 7:10 / 晩 22:00 · 土日 朝 7:10 / 晩 20:00`（去掉「早朝練があるため」前缀）
- 标题「学生区分」→ 「点呼区分」

**RegisterDone 账号显示**：
- 硬编码 `"00"` → `SEED.user.account` 动态 · 字体 64pt→44pt（6 桁 fit）

### 文件变动（本会话）

```
TomoshibiApp/Assets.xcassets/                          新
  ├── Contents.json
  ├── AppIcon.appiconset/
  │   ├── Contents.json
  │   └── Icon-1024.png                                新 · 灰色火焰 resized 1024
  └── TomoshibiFlame.imageset/
      ├── Contents.json
      └── flame.png                                    新 · Image #47

TomoshibiApp/Features/Auth/AuthStubs.swift             major（Splash/Register1 新字段/Done 动态 account/Login seed 兼容）
TomoshibiApp/Features/Home/HomeStubs.swift             major（placeholder 删 + pill 状态机 + 日文修）
TomoshibiApp/Features/MyPage/MyPageStubs.swift         加 PageHeader L1 + 荷物受取履歴
TomoshibiApp/Features/Apply/ApplyStubs.swift           major（StayForm SEED.user + FlowLayout + 宿泊先/食事 重构）
TomoshibiApp/Foundation/Seed/SeedModels.swift          User 全 `var` + grade/classSuffix/seatNo
TomoshibiApp/Foundation/Seed/SEED.swift                060218 seed
TomoshibiApp/Foundation/Components/PrimaryButton.swift HTML-fidelity rewrite + contentShape
TomoshibiApp/Foundation/Components/Field.swift         HTML-fidelity (Field label 13/600, TField height 48 bg pearl focus state)
TomoshibiApp/Foundation/Components/BottomNav.swift     胶囊 .glassEffect 直接 modifier + person.fill
TomoshibiApp/Foundation/Components/TopRollBar.swift    圆角 capsule
TomoshibiApp/Root/RootView.swift                       safeAreaInset 架构
TomoshibiApp/Root/GlobalOverlays.swift                 只剩 sheet/breadcrumb/toast
```

### 追加（同日後半）

**AppIcon / Splash**：
- Splash 火焰：灰色 → 红色（`06_assets/icons/tomoshibi_flame_color.png` from `Tomoshibi-iro.png`）
- AppIcon 1024×1024 → 红火焰同图（resize + 去 alpha）
- 归档：`DMSD/06_assets/icons/tomoshibi_flame_color.png` + `tomoshibi_flame_mono.png`

**カレンダー 页重构**（user 要求 tap 日期看当日行事）：
- EventsView：移除 list/calendar tab 切换 · 改为**日历主视图 + tap 选日期 + 下方显示当日行事**
- 上半：月切换 ‹ › + 曜日 + 日期 grid（水 start · 空格占位）· 选中高亮 primary · 今日 primary outline · 有事 accent 圆点（未选中时）
- 下半：选中日 `4月23日（木）` + N 件 pill + Cards list（时刻 · タイトル · 📍 場所 · chev）· 无事 EmptyState
- Year 格式 `2,026` 逗号 bug 修了（`Text(verbatim:)`）
- 选中日圆点不重叠数字（`hasEvent && !isSelected`）

**SEED.events 扩展** 3 件 → 14 件：4/5 留4アクティビティ · 4/7 帰寮日 · 4/8 始業式 · 4/9 入学式 · 4/10 春期課題考査 · 4/11 みつ元気PJ · 4/23 新入生歓迎会 · 4/25 避難訓練 · 4/26 茶道部体験 · 4/29 GW · 5/6 GW後帰寮 · 5/16 みつ元気PJ · 5/23 音楽と青空市 · 5/31 英検

**巴士表日别分组**：
- `BusDaySchedule` 新 struct（date / weekday / label / notice? / lines）
- `SEED.busSchedule`：5 日程（4/29 / 5/6 / 5/16 / 5/23 / 5/31）含完整 lines
- BusView 重构：日别 card section + header 显示 `4/29 (水) · GW外泊` + 黄 notice 条 + 运行 Line list
- 底部备注「上記以外の日はスクールバスの運行はありません」

**巴士表归档**：`DMSD/02_design/bus_schedule_real.md` 完整日程真值 + 乘车原则 + 上海岡山便注意

**中文残留再修**：
- `宿舎墙` → `寮ウォール`（HomeStubs CommunityTab）
- `点歌 · 今週候補` → `リクエスト曲 · 今週候補`（HomeStubs CommunityTab）
- `宿舎墙、点歌、快递` → `寮ウォール、リクエスト曲、宅配`（AuthStubs Onboarding body）

**跨会话协作文档**：
- `DMSD/00_admin/跨会话_ios_共享决策.md`（§0 文件位置 · §1 账号规则 · §2 可变字段/change log · §3 进度 · §4 协作规则）· web-CC（Mac-demo-sprint）加 §5 指向长期权威 `02_design/system_features_v0.1.md`
- `DMSD/bin/sync-ios-refs.sh` 同步脚本 · web-CC 已更新路径为 `03_dev/student_ios/`
- `TomoshibiiOSApp/SHARED_DECISIONS.md` 指针
- `TomoshibiiOSApp/SESSION_CHANGELOG.md` 本文件（会话完整改动日志）

### 待做 TODO（传给下一个会话）

- [ ] **RegisterStep3 或 Step1 加 `room` 房间号 TField**（学生自填）
- [ ] **MyPage 個人情報編集 sheet / page** — 改 grade/classSuffix/seatNo/room
- [ ] **AppStore.changeLog: [ChangeLogEntry]** mock（每次改 account 相关字段 append 记录）
- [ ] MyPage / Home / Community 各页细节继续对齐 HTML（字号 / 间距 / 圆角 / 颜色）
- [ ] StayForm §7「西村 宏（父）」placeholder 改普通日本姓
- [ ] `.glassEffect` 各处一致性检查
- [ ] HomeView「次のバス便」智能化：读 `busSchedule` 找最近未来日程，当天无运行显示「次回 4/29(水) 07:30」

---

## 会话模板（复制这段用）

```
## YYYY-MM-DD · {role}

### 大改动
- ...

### 文件变动
- ...

### 待做 TODO
- [ ] ...
```

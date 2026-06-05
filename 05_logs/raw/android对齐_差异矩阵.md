# Android 学生 App 对齐 iOS — 差异矩阵（摸底）

> **产出时间**：2026-06-05
> **真值来源**：iOS（`03_dev/student_ios/v1/TomoshibiApp/`）+ 对齐规格 `00_admin/iOS_Android_对齐规格.md`
> **被测对象**：Android `03_dev/student_android/v1/`（Kotlin + Compose，早期演示桩）
> **怎么摸的**：8 个只读子代理并行，每个读一个功能模块的规格段 + 对应 Android 屏文件，判「有 / 半成品 / 缺」。地基 + 导航两块由主会话读规格第 1-2 章评估。
>
> **状态定义**：
> - **有** = 外观 + 功能基本对齐 iOS（很少，Android 是早期桩）
> - **半成品** = 有 UI 桩但缺功能（无网络层 / 假数据）或外观、文案偏差大
> - **缺** = Android 完全没有这个屏 / 组件
>
> **全局最大缺口**：Android **完全没有网络层**（没有任何联网代码，只有 `MockData.kt` 本地假数据）。几乎所有「半成品」屏的共同短板都是「无网络层 + 假数据」，逐行不再重复写，统一在收尾报告里作为一条总缺口。

---

## 0. 地基（设计系统 / 主题 / 共享组件）— 规格第 1 章

| 项 | iOS 源 | Android 文件 | 状态 | 关键差距 |
|---|---|---|---|---|
| 色板令牌 | `Theme/TTokens.swift` | `ui/theme/Color.kt` | 有 | 已 1:1 移植全部令牌，还多做暗色模式（先按亮色对齐） |
| 令牌容器 | `enum T` | `ui/theme/Tokens.kt` | 有 | `SuzuTokens` + `LocalSuzuTokens`，三渐变已建 |
| 字体规范 | `.system()` | `ui/theme/Type.kt` | 半成品 | 占位 SansSerif + RobotoMono，待接 Noto Sans JP（视觉差可接受） |
| 尺寸常量（圆角/间距） | `T.Radius` / `T.Space` | 无 | 缺 | 没有 `SuzuDim` 尺寸常量，各组件硬编码 dp |
| 中央共享组件库 | `Foundation/Components/*`（16 个原子） | 无 | 缺 | Card/Pill/Avatar/PrimaryButton/GhostButton/Field/TField/TArea/RadioCard/SectionHeader/EmptyState/Skeleton/Toggle/Toast/PageHeader 全散在各屏内联，无中央库 |
| 玻璃组件 | `LiquidGlass/*` | 无 | 缺 | GlassCard/GlassSheet/GlassBackdrop 缺，需统一降级方案 |

## 1. 导航 / 路由 / 骨架 — 规格第 2 章

| 项 | iOS 源 | Android 文件 | 状态 | 关键差距 |
|---|---|---|---|---|
| Route 枚举 | `Routing/Route.swift`（~60 case） | `nav/Routes.kt`（22 个） | 半成品 | 只 22 个 vs iOS ~60；缺 displayName / isApplyBranch / isMyBranch / hidesBottomNav 等判断属性 |
| 自研导航栈 | `Routing/RouterStore.swift` | 无（用系统 NavHost） | 缺 | iOS 自研栈（go/back/replace/jump），Android 用 Jetpack Navigation 系统栈，模型对不上 |
| 顶层渲染 | `Root/RootView.swift` | `nav/NavGraph.kt` | 半成品 | 用系统 NavHost，非「when(current) 单点路由表 + 上下栏挂载」 |
| 底部导航条 | `Components/BottomNav.swift` | `ui/components/BottomTabs.kt` | 半成品 | 中央点呼按钮已有桩，但 iOS 是「2 文字 tab + 中央凸起」，Android 是 5-tab，需改 |
| 顶部点呼条 | `Components/TopRollBar.swift` | `ui/components/TopRollBar.kt` | 缺 | Android 这个文件实装的是**减点卡**，不是规格的四态点呼状态条 |
| 全局浮层（sheet/面包屑/toast） | `Root/GlobalOverlays.swift` | 无 | 缺 | sheet 机制 / 面包屑 popup / toast 全缺 |
| PageHeader 头部 | `Components/PageHeader.swift` | 无 | 缺 | 子页统一头部（左键按 level 切 / 长按面包屑）缺 |

## 2. 登录 / 注册 / 账号 — 规格第 4 章

| 屏 | iOS 源 | Android 文件 | 状态 | 关键差距 |
|---|---|---|---|---|
| Splash 闪屏 | `Auth/AuthStubs §2.1` | `SplashScreen.kt` | 半成品 | 延迟 1.4s（iOS 2.2s），无真实令牌检测、分流靠 mock flag |
| Onboarding 3 页引导 | `§2.2` | `OnboardingScreen.kt` | 半成品 | 框架完整，SF Symbols 未换 Material 图标 |
| Register Step1 基本情報 | `§2.4` | `AccountScreen.kt Step1` | 半成品 | 缺头像选择、生年月日用 Dialog 非 wheel、预览样式差 |
| Register Step2 点呼区分 | `§2.5` | `AccountScreen.kt Step2` | 半成品 | radio 圆环样式偏差，无后端映射 |
| Register Step3 連絡先 | `§2.6` | `AccountScreen.kt Step3` | 半成品 | hint 文案不全（缺「認証メールは送信されません」） |
| Register Step4 パスワード | `§2.7` | `AccountScreen.kt Step4` | 半成品 | 样式微调，无后端发请求 |
| Register Step5 認証コード | `§2.8` | 无 | 缺 | 完全缺：6 位大字输入 / 倒计时重发 / 422 错误；Android 4 步后直跳 Welcome |
| Register Done 完成 | `§2.9` | `WelcomeScreen.kt` | 半成品 | 缺绿勾 spring 动画、账号大字应 44sp（现 14sp） |
| Login 登录 | `§2.10` | `LoginScreen.kt` | 半成品 | 缺番号/邮箱双 tab（仅邮箱）、无登录 API、无 401 锁定 |
| Lockout 锁定页 | `§2.11` | 无 | 缺 | 完全缺：失败阶梯（30s→1h→永久）、倒计时、升级警告 |
| PwReset 找回密码说明 | `§2.12` | 无 | 缺 | 完全缺（v1.0 入口已隐藏，但屏体应留备用） |

## 3. ホーム 主页 — 规格第 5 章

| 屏/卡 | iOS 源 | Android 文件 | 状态 | 关键差距 |
|---|---|---|---|---|
| 問候行（おかえり + 日付 + 铃铛 badge） | `HomeStubs` greetingRow | `HomeScreen.kt` | 半成品 | 缺 JST 日期行、铃铛按钮 44×44、未读 badge |
| 学年更新「待更新」横幅 | `HomeStubs` + `Route.renewStudentNo` | 无 | 缺 | needsRenewal 状态 + 横幅容器 + 更新按钮全缺 |
| 減点 amber 卡（idle 態） | `HomeStubs` idle case | `TopRollBar.kt` | 有 | 外观基本对齐；缺右上白色径向装饰圆斑；仅 idle 态 |
| 次のバス便卡 | `HomeStubs` LifeTab① | `HomeScreen.kt` + `MockData` | 半成品 | 假数据，缺「挑下一班」实时逻辑（JST） |
| 宅配便卡（待領 badge） | `HomeStubs` ② | `HomeScreen.kt` + `HomeCards.kt` | 半成品 | 假数据 count=1，缺按待領动态计数 |
| 今週の活動卡 | `HomeStubs` ③ | `HomeScreen.kt` EventsCard | 半成品 | 预览只 2 条硬编码，缺 14 条数据源 |
| リクエスト曲卡 | `HomeStubs` ④ | `HomeScreen.kt` + `MockData` | 半成品 | 3 条假数据，缺 8 条数据源 |
| 遺失物卡（3 列网格） | `HomeStubs` ⑤ | `HomeScreen.kt` LostFoundGrid | 有 | 外观基本对齐；缺完整数据源 |

## 4. 申し込み 列表 + 新規 — 规格第 6 章

| 屏 | iOS 源 | Android 文件 | 状态 | 关键差距 |
|---|---|---|---|---|
| 申し込み一覧（列表） | `Apply/ApplyStubs ApplyListView` | `ApplicationsScreen.kt` | 半成品 | 类型表用日语 key、只 10 个缺 5；卡缺左侧类型图标块 + 底部日期区；tab 选中配色错（黑底应深青）；FAB 圆形应圆角方；状态徽章缺 3 种 |
| 新規申請（种类选择） | `Apply/ApplyStubs ApplyNewView` | `ApplicationsScreen.kt` ApplyKindGrid | 半成品 | 现状是底部抽屉应为独立全屏页；类型缺 5 个（行事企画/冷蔵庫/物品所持等）；无图标显首字；路由用日语 key |

## 5. 各申請表单 — 规格第 7 章

| 屏/组件 | iOS 源 | Android 文件 | 状态 | 关键差距 |
|---|---|---|---|---|
| 表单共用原子层（Field/TField/TArea/DateField/TimeField/RadioCard/ChipGroup） | `Apply/ApplyFormSupport.swift` | 无 | 缺 | 完全无通用组件库；现 ApplyNewScreen 内硬编码 |
| 表单分派器（ApplyFormDispatcher 按 kind 路由） | `Apply/*` | 无 | 缺 | 无 dispatcher，只一个通用 ApplyNewScreen |
| StayForm 出寮届（外泊/帰省/帰国三合一） | `Apply/ApplyStubs StayForm` | 无 | 缺 | 完全无；8 段区块 + 三 kind 显隐 + 复杂校验 + 3 种 Body |
| StudyAbsenceForm 学習欠席届 | `Apply/StudyAbsenceForm` | 无 | 缺 | 完全无；前/后/両方单选 + 日期 ±14 天 + 理由校验 |
| StudyOnlineForm オンライン学習（含文件上传） | `Apply/StudyOnlineForm` | 无 | 缺 | 完全无；周课表 + 契約書文件 + 两步 multipart 提交 |
| ContractFilePicker 契約書选择 | `Components/ContractFilePicker.swift` | 无 | 缺 | 完全无；拍照/相册/PDF + HEIC→JPEG + 10MB 拦 |
| GenericApplyForm 通用桩（外出/修繕/代理受取/来訪者/帰る） | `Apply/ApplyStubs` | `ApplyNewScreen.kt`（部分） | 半成品 | 残缺：缺修繕专属字段、タクシー开关联动、各类型特定字段 |
| ApplyPreview 确认页 | `Apply/*` | 无 | 缺 | 完全无；只读键值卡 + 两按钮 |
| ApplyDone 完成页 | `Apply/*` | 无 | 缺 | 完全无；居中勾 + 大标题 + 预想审查时间卡 |
| ApplyDetail 详细（审查时间线） | `Apply/ApplyStubs ApplyDetailView` | `ApplicationDetailScreen.kt` | 半成品 | 有 UI（申請者/内容/承認链/撤回）但全 MockData、时间戳写死 |
| RenewStudentNoSheet 番号再設定弹窗 | `Apply/*` | 无 | 缺 | 完全无；学年/组 chip + 番号键盘 + 实时预览 + 422 toast |
| 日期/時刻/時区基础设施（JST 固定） | `Apply/ApplyFormSupport` | `ApplyNewScreen.kt` DatePicker | 半成品 | DatePicker 用 UTC 未绑 Asia/Tokyo，可能偏一天 |

## 6. マイページ 个人页 — 规格第 8 章

| 屏 | iOS 源 | Android 文件 | 状态 | 关键差距 |
|---|---|---|---|---|
| マイページ着陸 MyLanding | `MyPage/MyPageStubs MyLandingView` | `MyPageScreen.kt` | 半成品 | 结构错：缺 3 状态卡（学習/点呼/減点）+ 日程卡；宫格少 2 多 2；假数据 |
| 個人情報 MyInfo | `MyPageStubs MyInfoView` | 无 | 缺 | 完全无；10 行信息表卡 + 编辑 + 变更履歴 |
| 連絡先・部屋編集 MyInfoEdit | `MyInfoEditView` | 无 | 缺 | 完全无；read-only 段 + 3 输入字段 + 保存 |
| 点呼履歴 MyRollcall | `MyRollcallView` | 无 | 缺 | 完全无；月份筛选 + 按日分组 + 6 列信息 |
| 点呼セッション詳細 MyRollcallDetail | `MyRollcallDetailView` | 无 | 缺 | 完全无；日期场次卡 + 2 列键值网格 |
| 減点明細 MyPoints | `MyPointsView` | （见第 9 章 DeductionScreen） | 半成品 | 见减点章 |
| 減点グラフ MyPointsChart | `MyPointsChartView` | 无 | 缺 | 完全无；12 月折线图 |
| 処分履歴 MyDiscipline | `MyDisciplineView` | 无 | 缺 | 完全无；空状态屏 |
| 体調報告履歴 MyHealth | `MyHealthView` | 无 | 缺 | 完全无；卡列表 |
| 掃除提出履歴 MyClean | `MyCleanView` | 无 | 缺 | 完全无；卡列表 + 状态 Pill + 退回评语盒 |
| 荷物受取履歴 MyPackages | `MyPackagesView` | 无 | 缺 | 完全无；卡列表 + 待領/領済 Pill |
| 学習履歴 MyStudy | `MyStudyView` | 无 | 缺 | 完全无；非对象/对象两分支 |
| 通知設定 MySettings | `MySettingsView` | `SettingsScreen.kt` | 半成品 | 现是通用設定屏（主题/字号等），非规格的「通知設定」（5 开关 + Push + 账号削除）；文案结构都不同 |
| Tomoshibi について MyAbout | `MyAboutView` | 无 | 缺 | 完全无；logo + 版本号 + AC 署名卡 |
| ログアウト弹窗 LogoutSheet | `MyPageStubs LogoutSheet` | `MyPageScreen.kt` | 半成品 | 文案错（应「次回起動時はアカウント番号と…」） |

## 7. 減点明細 + 趋势图 — 规格第 9 章

| 屏 | iOS 源 | Android 文件 | 状态 | 关键差距 |
|---|---|---|---|---|
| 入口卡 PointsStatusCard（着陸页内） | `MyPointsView pointsStatusCard` | 无 | 缺 | MyPage 着陸页无减点卡，应新增可点卡 |
| 減点明細 MyPoints（05-A） | `MyPointsView` | `DeductionScreen.kt` | 半成品 | 架构有但偏差：大数字应读 user.points、琥珀渐变上界色错、明细需接后端 |
| 減点グラフ MyPointsChart（05-B） | `MyPointsChartView` | 无 | 缺 | 完全无；Canvas 12 点折线 + 网格 + 阈值线 4/8 |

## 8. 杂项（バス / 宅配 / 曲 / カレンダー / 通知）— 规格第 10 章

| 屏 | iOS 源 | Android 文件 | 状态 | 关键差距 |
|---|---|---|---|---|
| 特別運航便 BusList | `BusList/BusListStubs` | `BusScreen.kt`（旧版） | 缺(实质) | 无日别分组/筛选/空港 banner/次便高亮；完全不是规格的 BusListView |
| 宅配一覧（待領/領済 tab） | `Community/CommunityStubs` | `DeliveryScreen.kt` | 半成品 | 无 segmented tab，假数据，中日文案混 |
| 宅配詳細 | `CommunityStubs` | 无 | 缺 | 完全无，无详情跳转 |
| リクエスト曲一覧 | `CommunityStubs` | `MusicScreen.kt` | 半成品 | 缺 hint banner，投票机制与规格不符（iOS 已废） |
| 曲を投稿 | `CommunityStubs AddRequest` | `MusicScreen.kt` Dialog | 半成品 | 缺 Apple Music URL 字段 + 投稿理由 + 封禁 banner |
| 曲詳細 | `CommunityStubs` | 无 | 缺 | 完全无，无路由跳转 |
| 曲を通報する（弹窗） | `CommunityStubs` | `MusicScreen.kt` Sheet | 半成品 | 通報理由 4 radio 缺（现 3 个不符），缺其他详细 textarea |
| 行事予定（月历） | `Schedule/ScheduleStubs` | `ScheduleScreen.kt` | 半成品 | 无月历网格（iOS 7 列日历），无今日判定，假数据 |
| 活動詳細 | `ScheduleStubs` | 无 | 缺 | 完全无，无详情跳转 |
| 通知中心 | `Community/Notifications` | `NotificationsScreen.kt` | 半成品 | 筛选第 5 项文案错，无 Pill tone 映射 |
| 通知詳細 | 同上 | `NotifDetailScreen.kt` | 半成品 | 无返信 UI（公告未实装），送信元写死 |
| お知らせ（公告一覧） | `AnnouncementsAPI` | 无 | 缺 | 完全无；接真后端 GET /announcements |
| お知らせ詳細（+ 回复） | 同上 | 无 | 缺 | 完全无；回复输入 + POST replies |

## 9. 点呼 / NFC / 状态条 — 规格第 11 章

| 屏/组件 | iOS 源 | Android 文件 | 状态 | 关键差距 |
|---|---|---|---|---|
| TopRollBar 四态状态条 | `Components/TopRollBar.swift` | 无（同名文件实装减点卡） | 缺 | Android TopRollBar.kt 是减点卡，非 idle/active/absent/done 四态点呼条 |
| RollcallSheet NFC 扫描弹窗（4 步状态机） | `Rollcall*` | `RollCallSheet.kt` | 半成品 | 只 idle 步，缺 scanning/success/fail 三步动画 |
| 中央点呼 FAB | `BottomNav.swift` | `BottomTabs.kt` | 半成品 | 62dp 圆/rollGrad/Shield 对齐，缺点击中等震动反馈 |
| RollCallScreen 点呼履历 | `Rollcall*` | `RollCallScreen.kt` | 有 | 列表/状态标签/时间戳符合预期 |
| StudyCheckinSheet 晚自习 2 次签到 | `Rollcall*` | 无 | 缺 | 完全无；主页 amber 卡进，2 次 tap 流程 |
| FeedbackSheet 反馈三选一 | `Rollcall*` | 无 | 缺 | 完全无；点 TopRollBar 弹，3 选项卡（体調/欠席/その他） |

---

## 统计

| 状态 | 屏/组件数 |
|---|---|
| 有 | 4（减点 amber 卡 / 遺失物卡 / RollCallScreen / 色板令牌） |
| 半成品 | ~32（多数共同短板：无网络层 + 假数据 + 文案/配色/布局偏差） |
| 缺 | ~41（完全没有，需从零搭；含整个网络层 + 共享组件库 + 自研导航栈 + 大量 L2 子页） |
| **合计（含子卡片/组件/重复）** | **77 行**，去重后约 60 个真实功能屏 |

> 注：「77」含模块间少量重复（如「申し込み一覧」在第 4、5 章各列一次；「LifeTab 卡」= 主页第 3 章的卡，被杂项章重复列）+ 子卡片/组件级行。去重后真实功能屏约 60 个。

## 三个全局结构性缺口（不是单屏问题，是地基）

1. **网络层 = 零**。没有任何联网代码，整套要从零建（HTTP 客户端 + 错误处理 + 日期适配 + token 存储 + 10 组端点 + ~40 数据类）。几乎所有「半成品」屏的根因。
2. **共享组件库 = 零**。iOS 16 个原子组件 + 玻璃组件全无中央库，各屏内联重写，导致外观漂移。
3. **自研导航栈 = 零**。Android 用系统 NavHost（22 路由）vs iOS 自研栈（~60 路由 + 面包屑 + 全局浮层），骨架模型对不上。

## 防作弊核心（后端未写，遇到只记 TODO，不动）

点呼相关屏（RollcallSheet / StudyCheckinSheet）的真实 NFC 签到链路依赖防作弊核心后端（nonce / ECDSA 签名 / 设备注册 / 卡→学生映射），后端一行没写。Android 侧这些屏只能做 UI + 动画，真实联网签到记 TODO。

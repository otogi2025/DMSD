# iOS 上线缺口修复 — GOAL 施工图（详细规格）

> 本文件是给「另一个 Claude Code 会话用 `/goal` 自主跑」的施工图。该会话开工前**先 Read 本文件全段**再动手。
> 起因：itsuki 2026-06-08 问「iOS 距正式版还差什么」→ 6 维度子代理审 2.2 万行 + CC 自验 → 缺口分三档进 `00_admin/TODO.md` §📱。本 goal 做其中「代码能做、且能用编译验证」的部分。
> 工作目录：`03_dev/student_ios/v1/`（iOS 学生 app，系统名 Tomoshibi）。

---

## §0 硬约束（违反任一条 = 本轮白做）

1. **只改 iOS**（`03_dev/student_ios/v1/` 下）。不碰 Android（`03_dev/student_android/`）、不碰后端（`03_dev/backend/`）、不碰老师网页。
2. **保留所有 `#if DEMO` 演示分支**。演示版（scheme `TomoshibiAppDemo`，编译时定义 `DEMO` 宏）继续用假数据 `SEED.*`；只改正式版（`#else` / 非 DEMO）分支。`#if DEMO` 是编译开关：`DEMO` 这个宏定义了走演示分支、没定义走生产分支。
3. **代码注释 100% 中文**；界面给用户看的文字（UI 字符串）保持日语，日语词在注释里出现要用「」括起来。这是项目中文铁律，保存时有 hook 扫描。
4. **每改完一个功能 commit 一个**：显式列文件名（`git add <具体文件>`，不准 `git add -A`/`git add .`）；commit 前先 `git diff --cached` 核对只有自己改的文件（多会话共用暂存区，别带走别会话的改动）；**不写 `Co-Authored-By`**；**不 push**；**不打 tag**。
5. **不动签名相关设置**：`project.yml` 里 `DEVELOPMENT_TEAM`（苹果团队编号）保持空、`CODE_SIGNING_ALLOWED/REQUIRED` 保持 `NO`。理由：itsuki 还没办苹果开发者账号、没团队编号；且本 goal 靠「模拟器编译通过」验证，模拟器是不签名构建，强开签名会让验证手段失效。签名翻 YES 是 itsuki 拿到账号后的活，不在本 goal。

---

## §1 必读背景

### 1.1 演示 / 生产双轨架构
- 演示版 scheme `TomoshibiAppDemo`（定义 `DEMO` 宏）→ `#if DEMO` 分支走 `SEED.*` 假数据，给宿舍管理员演示用。
- 正式版 scheme `TomoshibiApp`（不定义 `DEMO`）→ `#else` 分支调真后端 / 真功能。
- 网络地址：调试运行（DEBUG，Xcode 直接 Run）= `http://localhost:8000`；上架打包（RELEASE，Archive）= `https://api.tomoshibi.cc`（见 `APIClient.swift:13-17`）。

### 1.2 ⭐ 点呼签到的真实架构（2026-06-02 itsuki 拍板「架构反转」，权威文档 `02_design/flow_design.md §3`）
**手机不联网，手机把学生身份数据用 NFC 写进墙上 ST25DV16K 芯片的 Mailbox（邮箱，256 字节临时缓存区），点呼机（树莓派）被动读走、再由点呼机发后端、后端验证。**

旧方案（已作废，别按旧的做）：手机读贴纸拿一次性随机码 nonce → 手机自己 POST 后端。现有 `RollCallAPI.swift:14-19` 的注释还停在旧方案（写「app 拿 nonce → POST」），**那段注释过时**，本 goal 要把它纠正。

`flow_design.md §3`（66-113 行）的端到端流程：
1. 学生开 app、点「签到」按钮。
2. app 唤起 iOS NFC 写入会话（`CoreNFC`），提示「点呼機にタッチしてください」（请碰一下点呼机）。
3. app 把身份数据写进 ST25DV 的 Mailbox 邮箱。数据 = `student_id`（v1.0 只要这个；v1.1 可选加本机私钥签名防造假学号）。
4. **手机全程不联网，开飞行模式也能完成这一步。**
5. ST25DV 被写入 → 点呼机收到硬件中断 → 读走数据 → 发后端。
6. app 本地显示「点呼機に送信しました」（已发给点呼机），**不等后端结果**（手机不联网，也等不到）——`flow_design.md §3` 步骤 19 的「本地物理确认」做法 A。

### 1.3 本功能验收范围 = 「代码写好 + 双 scheme 编译过」
- 本 goal 只要求把 CoreNFC 写入层按 §4 真写出来、功能写完整、能编译、数据格式落文档、演示版保留假动作。
- **不要求跑真机 NFC**：模拟器本来就跑不了 NFC（`NFCReaderSession.readingAvailable` 在模拟器恒为 false），真机联调由 itsuki 在硬件 + 点呼机读取侧驱动到位后另做，不在本 goal 范围。
- ISO15693 自定义命令的确切命令字节用具名常量 + `// TODO[硬件]: 对照 ST25DV16K datasheet 核实` 标注（芯片手册不在仓库），结构搭对即可，联调时坐实。

---

## §2 验证方式（每条都要在对话里贴真实输出，小模型才能判定完成）

每轮先重新生成工程再双版本编译（工具 `xcodegen` 从 `project.yml` 生成 `.xcodeproj`，新加文件必须靠它进工程）：

```
cd 03_dev/student_ios/v1
xcodegen generate
xcodebuild -scheme TomoshibiApp     -destination 'platform=iOS Simulator,name=iPhone 17 Pro' build
xcodebuild -scheme TomoshibiAppDemo -destination 'platform=iOS Simulator,name=iPhone 17 Pro' build
```

两条都要出现 `** BUILD SUCCEEDED **`。
- ⚠️ 编译警告里若有日语注释告警（中文铁律 hook），按铁律修。
- ⚠️ 若某次改动（尤其 §3.3 entitlements 接线）让模拟器不签名构建挂了：把那一处改动回退，留 `// TODO[签名]: ...` 说明，**别在同一个错上耗轮次**（见 §5 刹车）。

---

## §3 工作清单（每轮挑没做完的往下做，做完一个 commit 一个）

### 🔴 阻塞档

#### ① 手机点呼签到 — CoreNFC 写 ST25DV Mailbox（核心，详细规格见 §4）
- 现状（已 grep 核实）：签到按钮走 `Features/Home/HomeStubs.swift:1483` 的 `simulate()`，只调 `AppStore.swift:526` 的 `recordCheckin()`（纯本地改状态、现编时刻、5 秒复位），不发任何地方；`simulate()` 外层**没有** `#if DEMO`，演示版正式版跑同一段假逻辑。学習签到 `HomeStubs.swift:1828` 的 `simulate()` 同样。
- 要改成：演示版（`#if DEMO`）保留现在的假动作；正式版（`#else`）改成调 §4 写好的 NFC 写入层，把 `student_id` 写进 ST25DV Mailbox，成功后本地显示「点呼機に送信しました」、不等后端。学習签到同样处理。
- 验收：① `grep -rn "import CoreNFC"` 命中新建的 NFC 文件；② `simulate()` 两处都出现 `#if DEMO`/`#else` 分叉；③ 双 scheme BUILD SUCCEEDED；④ 数据格式注释跟 `flow_design.md §3` 一致。

#### ② app 图标对不上
- 现状：`TomoshibiApp/Assets.xcassets` 里只有 `TomoshibiFlame.imageset`、没有 `AppIcon` 条目；但构建设置 `ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon`（`project.pbxproj:631/724/825`）指向它。真图标是散放的 `TomoshibiApp/AppIcon-1024.png`（已确认 1024×1024）。
- 要改成：在 `Assets.xcassets` 里新建 `AppIcon.appiconset`，放进 `AppIcon-1024.png` 当单尺寸图标（Xcode 14+ 支持单尺寸 1024 图标集），写好 `Contents.json`。
- 验收：`Assets.xcassets/AppIcon.appiconset/Contents.json` 存在且引用 1024 图；双 scheme BUILD SUCCEEDED。

#### ③ 推送 entitlements 没接进构建 + NFC 用途说明
- 现状：`TomoshibiApp/TomoshibiApp.entitlements`（声明 app 要用推送 + NFC 读取的配置文件，已含 `aps-environment` 推送 + `com.apple.developer.nfc.readersession.formats` NFC 格式 [NDEF, TAG]）存在，但 `project.pbxproj` 里没有 `CODE_SIGN_ENTITLEMENTS` 设置把它接上（grep 零命中）。NFC 写入还需要 Info.plist 的用途说明字符串，现在没有。
- 要改成：在 `project.yml` 的 `TomoshibiApp` target `settings.base` 里加：
  - `CODE_SIGN_ENTITLEMENTS: TomoshibiApp/TomoshibiApp.entitlements`
  - `INFOPLIST_KEY_NFCReaderUsageDescription: "点呼の出席を点呼機に送信するために NFC を使用します"`（NFC 用途说明，碰一下时系统弹的提示）
- 验收：`grep CODE_SIGN_ENTITLEMENTS` 在生成后的 `project.pbxproj` 命中；双 scheme BUILD SUCCEEDED。⚠️ 若接 entitlements 让不签名模拟器构建挂了 → 回退 `CODE_SIGN_ENTITLEMENTS` 这一行、留 `// TODO[签名]` 说明（NFC 用途字符串保留），别耗轮次。

### 🟡 重要档（都是代码改，验收 = 双 scheme BUILD SUCCEEDED + 对应改动 grep 得到）

#### ④ 6 个列表加载失败显示成「假的空列表」
- 现状：`AppStore.swift` 的 `loadCleaningHistory`(968-977) / `loadMyProfile`(1027-1042) / `loadSongs`(986-995) / `loadLostFound`(1003-1013) / `loadMyPackages` / `loadAnnouncementUnreadCount` 的 catch 块空着（错误全静默吞）；界面 `MyPageStubs.swift:1444`(減点なし)/`1959`(掃除)、`CommunityStubs.swift:930`(遗失物)/`1043`(点歌) 只有空态、没加载中 / 失败态。网断时扣分页把「有 5 个扣分」显示成「減点なし（零扣分）」。
- 要改成：给这几个列表加「加载中 / 加载失败 / 真没数据才显空」三态。最简做法：在 `AppStore` 给每个列表加一个加载状态枚举（idle/loading/failed/loaded），界面照已有正确写法 `ScheduleStubs.swift:54-65` 补两段 UI（加载中转圈 `ProgressView`、失败显「読み込みに失敗しました」+ 再読み込み按钮）。优先减点明细 + 点呼履历两个敏感页。
- 验收：减点 / 点呼 / 扫除 / 点歌 / 遗失物界面出现失败态文案「読み込みに失敗しました」；双 scheme BUILD SUCCEEDED。

#### ⑤ 登录令牌过期后不自动跳回登录页
- 现状：`RootView.swift:45-111` 纯按路由切界面，没有任何监听 `app.authToken`（登录令牌）变 nil 就跳登录的全局机制（grep `onChange` 跟 auth 无关）。令牌在静默加载里过期后 app 假死在空白壳里。
- 要改成：在 `RootView` 或 app 入口加全局 `onChange(of: app.authToken)`，变 nil 时 `router.replace(.login)`，统一踢回登录页。
- 验收：grep 到 `onChange(of:` 监听 `authToken` 并跳 `.login`；双 scheme BUILD SUCCEEDED。

#### ⑥ 离线 / 拉资料失败时首页显示假学生「リュウ イヒ 4.5点」
- 现状：`AppStore.swift:144-146` `displayUser = currentUser ?? SEED.user`，正式版登录后没拉到本人资料时回退成演示假人（`SEED.user`，姓名「リュウ イヒ」/ 4.5 点 / 迟到 5 欠席 2）。首页 amber 卡 `HomeStubs.swift:556/571-575` 就显这套假数字。
- 要改成：正式版（`#if !DEMO`）`currentUser` 为 nil 时返回一个空白占位 `User`（姓名 / 房号 / 数值显「—」），不回退 `SEED.user`；只有演示版才回退假人。
- 验收：`displayUser` 出现 `#if DEMO`/`#else` 或 `isAuthenticated` 判断、生产分支不返回 `SEED.user`；双 scheme BUILD SUCCEEDED。

#### ⑦ 删掉正式版无条件显假数据的死入口
- 现状：① 旧巴士页 `CommunityStubs.swift:1749` `BusView` 无条件读 `SEED.busSchedule`/`SEED.busNotice`（无 `#if DEMO` 无登录判断），由死路由 `RootView.swift:77` `.homeBus` + `Route.swift:37` 可达，首页已不用它；② 「我的页」`MyPageStubs.swift:204-211` 的 `upcomingEvents` 无条件读 `SEED.events`，被 `scheduleCard`(241/249) 渲染。
- 要改成：① 删 `BusView` + `.homeBus` 路由枚举 + `RootView` 对应 case（首页已改走带登录判断的 `BusListView`）；② 「我的页」行事预定卡数据源 `SEED.events` 用 `#if DEMO` 守卫：演示读 SEED、生产读 `EventsAPI.listEvents` 拉到的列表（参考 `ScheduleView` 已有调用），拉不到显空态「当面の予定はありません」。
- 验收：`grep BusView` / `grep "case homeBus"` 零命中（已删）；`MyPageStubs.swift` 的 `SEED.events` 引用在 `#if DEMO` 内；双 scheme BUILD SUCCEEDED。

#### ⑧ 隐私清单「营养标签」据实补声明
- 现状：`TomoshibiApp/PrivacyInfo.xcprivacy`（苹果要的隐私自述文件）里 `NSPrivacyCollectedDataTypes`（声明收集哪些用户数据）是空数组；但 app 实际收账号（姓名 / 联络方式）+ 上传契約書照片（`StudyAPI.swift:58-66`）。空声明跟实际矛盾，会被苹果审核打回。
- 要改成：在 `NSPrivacyCollectedDataTypes` 据实补：联系信息（姓名 / 电话邮箱）、用户内容（契約書照片）、标识符（账号），用途标「App 功能」、`NSPrivacyCollectedDataTypeLinked` 据实、`NSPrivacyCollectedDataTypeTracking` 填 false。按苹果隐私清单官方键名格式写。
- 验收：`NSPrivacyCollectedDataTypes` 非空、含上述类型；plist 格式合法（`plutil -lint TomoshibiApp/PrivacyInfo.xcprivacy` 通过）。

#### ⑨ 暗色模式开关是「死控件」
- 现状：设置页 `MyPageStubs.swift:2106-2123` 有暗色开关写进 `app.isDark`，但入口 `TomoshibiApp.swift:28` `.preferredColorScheme(.light)` 钉死亮色、无视它（注释 26 行自承 N18 未实装）。拨了没反应。
- 要改成（取省事方案）：把 `MyPageStubs.swift` 那段暗色开关 UI 整段删 / 隐藏（别给用户假开关）。真做暗色是 N18，留 v1.1。
- 验收：设置页不再有「ダークモード」开关；双 scheme BUILD SUCCEEDED。

#### ⑩ 加密合规标志没声明
- 现状：grep `ITSAppUsesNonExemptEncryption` 全工程零命中，每次上传苹果都卡一道「用没用特殊加密」手填问询。
- 要改成：`project.yml` 的 `TomoshibiApp` `settings.base` 加 `INFOPLIST_KEY_ITSAppUsesNonExemptEncryption: "NO"`（app 只用标准 HTTPS，填否对）。
- 验收：grep 命中；双 scheme BUILD SUCCEEDED。

#### ⑪ 通知 5 开关旁加「接通后生效」说明（小改）
- 现状：设置页 `MyPageStubs.swift:2058-2065` 5 个通知开关（点呼 / 申请 / 包裹 / 活动 / 扣分）存了用户意愿但发送侧不读（注释自承 push 未接通）。
- 要改成：这组开关下方加一行小字说明「通知が有効になってから反映されます」（通知接通后生效），免得用户以为关了就不收。
- 验收：该说明文案出现在设置页；双 scheme BUILD SUCCEEDED。

---

## §4 手机点呼签到 — CoreNFC 写 ST25DV Mailbox 详细规格

### 4.1 新建 NFC 写入层
新建 `Foundation/Network/NFC/ST25DVWriter.swift`（目录没有就建）。职责：把 `student_id` 通过 CoreNFC 写进 ST25DV16K 的 Mailbox 邮箱。要点：

- `import CoreNFC`
- 类型 `final class ST25DVWriter: NSObject` 实现 `NFCTagReaderSessionDelegate`（标签读写会话代理）。
- 对外提供一个 async 方法，签名建议：
  ```
  @MainActor func writeCheckin(studentId: UUID) async throws
  ```
  内部用 `withCheckedThrowingContinuation` 把代理回调包成 async。
- 会话：`NFCTagReaderSession(pollingOption: .iso15693, delegate: self, queue: nil)`（ST25DV 是 NFC Type 5 / ISO15693 标签）。`session.alertMessage = "点呼機にタッチしてください"`。
- 可用性守卫：方法开头 `guard NFCReaderSession.readingAvailable else { throw ST25DVError.unavailable }`（模拟器 / 不支持 NFC 的机型走这条，调用侧给友好提示）。
- 检测到标签 `didDetect tags:`：取第一个 `case .iso15693(let tag)`，`session.connect(to:)` 后写 Mailbox。
- **写 Mailbox 用 ISO15693 自定义命令**（`tag.customCommand(requestFlags:customCommandCode:customRequestParameters:)` 或 `sendRequest`）：
  - ST25DV 厂商代码 `0x02`（ST）。
  - 写 Mailbox（Write Message / Write Mailbox）的自定义命令码 + 参数字节 **用具名常量定义**，且每个都标 `// TODO[硬件]: 对照 ST25DV16K datasheet 核实命令字节（Write Mailbox / Fast Transfer Mode）`。没硬件没手册不要瞎填具体值能跑就行——结构搭对、常量留 TODO。
- 错误类型 `enum ST25DVError: Error { case unavailable, writeFailed, ... }`。

### 4.2 写入的数据格式（落文档，跟点呼机将来读取侧对齐）
Mailbox 256 字节，v1.0 payload 紧凑二进制：
- 第 1 字节：格式版本号 `0x01`。
- 第 2 字节：类型（`0x01`=点呼签到 / `0x02`=学習签到），让点呼机区分两种签到。
- 接 16 字节：`student_id`（UUID 的 16 字节原始值，`uuid` 属性）。
- v1.1 可选：再接私钥签名（v1.0 不做，注释标 v1.1）。

在 `ST25DVWriter.swift` 顶部用注释把这个格式写清楚，注明「跟 `02_design/flow_design.md §3` + 将来 `03_dev/rollcall_device/src/nfc/st25dv.py` 对齐；点呼机读取侧尚未实装，本格式为提案，硬件到货后双方对齐定稿」。

### 4.3 接到签到按钮
- `Features/Home/HomeStubs.swift` 点呼 `simulate()`（1483）+ 学習 `simulate()`（1828）：
  ```
  #if DEMO
      // 原来的假动作（保留）：app.recordCheckin() 等
  #else
      // 正式版：真写 ST25DV
      do {
          try await ST25DVWriter().writeCheckin(studentId: app.myStudentId)  // 点呼传类型 0x01 / 学習 0x02
          // 本地物理确认（做法 A）：不等后端
          app.recordCheckin()           // 复用本地状态更新让卡变绿、显「点呼機に送信しました」
      } catch ST25DVError.unavailable {
          // 模拟器 / 不支持 NFC：给提示「この端末は NFC 非対応です」
      } catch {
          // 写入失败：弹错，别假装成功
      }
  #endif
  ```
  （`app.myStudentId` 见 `AppStore.swift:136`，登录后 `loadMe` 填。为 nil 时先引导登录 / 提示。）
- `recordCheckin()` 里「现编签到时刻 + 5 秒复位」那段属于演示性质，正式版本地只需把卡显示成「已发送」即可；按做法 A 不依赖这个时刻当权威（权威时刻是点呼机盖的）。能不动就保留它当本地 UI 反馈，注释说明「本地 UI 反馈，非权威；权威判定在点呼机 + 后端」。

### 4.4 纠正过时注释
- `RollCallAPI.swift:14-19` 注释把旧方案（「app 拿 nonce → POST」）改成架构反转后的说明：手机改写 ST25DV、不再 POST 签到；`RollCallAPI.checkin` 这个 POST 方法 v1.0 学生端不再用（保留代码 + 注释标「架构反转后学生端弃用，可能给老师代点 / 路径 A 补录用，勿删」），别让后来人以为还要调它。

### 4.5 验收 = 代码 + 编译
代码写完 + 功能完整 + 双 scheme BUILD SUCCEEDED + 格式落文档 + 演示版保留假动作 = 完成。真机 NFC 联调不在本 goal（itsuki 硬件到位后另做）。

---

## §5 不做的事 + 刹车 + 完成条件

### 不做（超范围，别碰）
- 后端部署、苹果开发者账号 / 签名翻 YES、App Store Connect 后台元数据 —— 都是 itsuki 外部活。
- v1.1 项：离线缓存 / 本地化多语言 / 无障碍 / 崩溃上报 / 强制更新 / 下拉刷新 / 超时调整 / 启动屏品牌化 / iPad 适配 / 补单元测试 / 翻译老 Stub 日语注释（这条可选，行有余力再做，别为它耗轮次）。

### 刹车（防失控烧钱）
- 同一个错连续 3 轮没解决 → 停下，报告卡在哪。
- 总轮次到 30 轮 → 停下。
- entitlements 接线 / 图标 / NFC 这类「可能因环境验不了」的，挂了就回退 + 留 TODO，别死磕。

### 完成条件（小模型据此判定，要在对话里贴齐这些原始输出）
1. `xcodegen generate` 成功 + `xcodebuild -scheme TomoshibiApp ... build` 贴出 `** BUILD SUCCEEDED **`。
2. `xcodebuild -scheme TomoshibiAppDemo ... build` 贴出 `** BUILD SUCCEEDED **`。
3. `git log --oneline -15` 显示 §3 各功能的 commit（每功能一个、文件名显式、无 Co-Authored-By、未 push）。
4. 报告逐条对 §3 的 ①~⑪ 说「做了 / 跳过 + 原因」。

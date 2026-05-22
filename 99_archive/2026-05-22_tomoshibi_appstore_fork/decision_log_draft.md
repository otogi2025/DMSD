# decision_log 待加章节 draft（itsuki 自粘到 05_logs/decision_log.md）

> 本文件是 CC 起草的 draft，**itsuki 自己粘到 `05_logs/decision_log.md`**（CC 不直写决策日志主文件 — 这是 AC 协作的硬底线）。
> 粘完后这个 draft 文件可以删，或者归档到 99_archive/。

---

## 2026-05-07 — App Store 上架方向 3 个核心决策反转

### 决策 1：G2 决策（v1.0 三端齐发）打破，提前 iOS 单独上 App Store

**背景**：
- 4-19 G2 拍板「v1.0 = iOS + Android + NFC 卡 一次上线」，逻辑是不分阶段、避免半成品
- 5-07 itsuki 拍板「现在就推 iOS 上 App Store 公开发布」（v0.8.0 期间）
- iOS 单独推 App Store 上架，Android + NFC 卡留在 v1.0 / v1.1 之后

**理由（itsuki 拍板时给）**：
- AC 叙事「真实上架的产品」⭐⭐⭐⭐⭐ 比「演示用 prototype」强得多
- 上架 1.0.0 + 后续 1.1.0 加 NFC 是合理迭代路径，不破坏 v1.0 用户体验
- 等 NFC 卡到货 + Android 同步可能拖到秋季，错过最有效的 AC 素材产出窗口

**代价 + 接受**：
- v1.0 用户拿不到完整功能（NFC 不可用 / 无 Android 端） — 接受，因为目标用户群是「先体验 → 后续升级」
- 4-19 决策的「不分阶段」原则被打破 — 接受，因为外部条件变化（实体卡 supply chain 不可控）

**how to apply**：
- 上架版 fork 在 `~/dev/Tomoshibi-AppStore/`（DMSD 外，不污染主项目 git）
- 主项目 v1/ 继续 Android 同步开发 + NFC 卡到货后 v1.1.0
- AC 叙事：5-04 → 5-07 决策反转写成「条件变化触发的判断调整」

---

### 决策 2：B4「这次不开 NFC」反转 → 完整保留 NFC 功能

**背景**：
- 上架 plan 初版 B4 推荐「这次不开 NFC（实体卡未到货 + 审核员无法测试 + 1.0.0 占坑）」
- itsuki 拍板「NFC 完整保留 — 跟正式版一模一样，可以正常碰。卡到了再匹配」

**理由（itsuki 给）**：
- 1.0.0 没 NFC 是「半成品」，1.1.0 加回会破坏 1.0.0 已上架用户的预期
- 任意 NFC tag 触发都能展示完整 UX 流程（即使非授权卡走 backend 验签失败的正常 error）
- 给审核员看到 NFC capability 完整 + UX 流程完整，比「不开 NFC」展示价值更高

**how to apply**：
- iOS 加 entitlements `com.apple.developer.nfc.readersession.formats` (NDEF + TAG)
- Info.plist 加 `NFCReaderUsageDescription`（日语用途说明）
- itsuki 在 Apple Developer Portal 注册 App ID 时**必须勾 Near Field Communication Tag Reading** capability
- Reviewer Notes 写明「専用カード未配布、任意 tag で UI 確認可」

---

### 决策 3：私域策略放弃 → 按通用产品上架

**背景**：
- 上架 plan 初版预计 Apple 4.2.1（私域 / Demo app）reject 风险高（限定特定宿舍学生使用）
- 初版策略：在 Reviewer Notes 主动声明「限定校内分发」+ 备 Unlisted App 方案 B
- itsuki 拍板「我不说，Apple 怎么知道？我就默认它是公开的，可以给全球所有地方都可以想用就用的。宿舍的点呼系统不就好了？」

**理由（itsuki 拍板时给）**：
- Apple 4.2.1 reject 触发条件需要 metadata 主动暴露「私域限定」字眼。不主动说就不容易触发
- 「宿舍点呼数字化」语调是通用 SaaS 产品（不绑定特定学校），叙事可以泛用
- 注册码门保护 = 「为了保护学生隐私（部屋番号等）」，不是「拒绝外部用户」

**how to apply**：
- App 描述写**通用宿舍管理产品语调**（不写特定学校 / 校名）
- Reviewer Notes 解释「注册码门是为隐私保护」（不是限定群体）
- 不申请 Unlisted App
- 备方案：万一 4.2.1 reject，再加 Unlisted 申请

---

### 实装总结（5-07 当天 CC 完成的代码改动）

- ✅ iOS + backend 物理 fork 双份 → `~/dev/Tomoshibi-AppStore/{ios,backend}/`（DMSD 外）
- ✅ project.yml 11 处改动（Bundle ID 去 .demo / Marketing 1.0.0 / iOS 18 / Team ID 落地 / signing 拆 configs / NFC entitlements）
- ✅ APIClient.swift `#if DEBUG` 切 prod URL
- ✅ PrivacyInfo.xcprivacy 新建（4 个 reason code + Tracking false）
- ✅ TomoshibiApp.entitlements 新建（NFC NDEF + TAG）
- ✅ 账号删除（iOS MyPage UI + alert + backend DELETE /accounts/me + AuditLog）
- ✅ SplashView 启动跳转改造（双端：fork + 主项目）+ system_features.md §7.17 + IOS_DESIGN_LOG §3.13
- ✅ backend seed.py 改造（admin + reviewer 学生 + reviewer 注册码 999999）
- ✅ VPS 部署配置（Dockerfile + docker-compose + Caddyfile + .env.example + DEPLOY.md）
- ✅ App Store METADATA.md（描述 / 关键词 / Reviewer Notes 双语）
- ✅ privacy_policy.md（GH Pages 部署用）
- ✅ RegisterStep4 password 默认值 `#if DEMO` 包裹（Release 空字符串）

### itsuki 待启动的并行任务

- 🔴 ASC 撞名检索（Tomoshibi / ともしび / 灯火）
- 🔴 Apple Developer Portal 注册 App ID `com.itsuki.tomoshibi` + 勾 NFC capability
- 🔴 日本 VPS 注册（Vultr Tokyo / Sakura / Conoha）+ 域名买（推荐 Cloudflare）
- 🔴 GitHub Pages 部署 privacy_policy.html + support.html

### 时间线预期

- Day 1-2: CC 代码改动 ✅ 已完成
- Day 3-7: itsuki VPS 部署 + DNS / 域名等候
- Day 6-8: itsuki 截图 + ASC 元数据填写
- Day 9: itsuki Xcode Archive + Validate + Upload
- Day 9: itsuki 提交审核
- Day 10-12: Apple 审核（24-72h）
- Day 12-14: Reject 应对（基线假设 1 次） + 修 + 重提
- Day 14-18: 上架

最快 14-18 天上架（现实预期 3-4 周含 1 次 reject + 学校生活）。

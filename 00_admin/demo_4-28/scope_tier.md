# Demo 4-28 Scope Tier 清单  <!-- VERSION_OK -->

> **作用**: Tier 1/2/3 分层完整清单。代码 agent 直接读这个做事。
> **权威**: 本文件是 demo 功能范围的唯一真值。`sprint.md §2` 只放摘要，详情看这里。
> **最后更新**: 2026-04-22（**砍点呼机硬件** — 详见本文 §0.1）

---

## 0. 总原则

| Tier | 含义 | Demo Day 表现 |
|---|---|---|
| **Tier 1** | 流程脚本里要真演示，必须端到端跑通 | itsuki 真 tap / 老师真点 / 系统真响应 |
| **Tier 2** | Web 菜单存在 + UI skeleton + mock 数据 | 老师点开能看到页面，itsuki 口头讲"这里将来做什么" |
| **Tier 3** | demo 当天**完全不出现**（砍）| Demo 后按管理员反馈再决定做不做、何时做 |

**管理员视角**: 左侧菜单 7 大类齐全 + 核心点呼流程真跑 → 感受到"系统完整" + "技术可行"。

### 0.1 重大 scope 调整（2026-04-22）：砍点呼机硬件

**itsuki 拍板**：
- **Pi 3A+ / PN532 / 喇叭 / 外壳 不下单**（原 sprint.md §0.5 采购全部推翻，hardware_design.md §4.1 同步砍）
- **NTAG215 卡也不必买** — demo 只演 itsuki 一人签到，用她手里已有的 NFC 卡（银行卡 / Suica / PASMO / 学生证）即可
- **现场流程**：iPhone 碰 itsuki 自己的 NFC 卡 → iOS Shortcuts Automation 触发 → POST 后端 → WebSocket 推 iPad → iPad Safari **页面 リュウイヒ 座位变绿 + iPad 扬声器 TTS 播报 "リュウイヒ"**
- **原"点呼机喇叭播报"降级**：语音从 Pi 移到 iPad（Web Speech API）/ Mac（`say -v Kyoko` 命令）

**为什么砍**（AC 叙事 🌟）：
- 7 天 deadline + 零基础 → PN532 I²C 驱动 + 线材接线 + Pi 烧 SD + TTS 配置是硬件最大不确定性
- 砍硬件 = demo 成功率从 60% 拉到 95%
- 不影响架构说服力：demo 讲"上线版会有专用点呼机"，给管理员看 hardware_design 文档的硬件选型过程，比现场跑一个不稳定的 Pi 更专业
- 原创设计"语音播报防作弊"从硬件层移到软件层：iPad 发声同样达到"大家都能听到签到人名字"的效果，防作弊叙事不变

**影响哪些条目**：
- §1.5 **点呼机语音喊名** → 改为 "iPad / Mac 语音喊名"（见下方修订）
- §1.4 **硬件替代** → ST25DV fallback 简化（卡贴桌面而非点呼机）
- §4 **代码 agent 入口** → 删除 `03_dev/demo_4-28/device/` 任务
- `sprint.md §0.5` §3 时间表 / `hardware_design §4` 采购 / `CLAUDE.md` 项目信息段 — 已同步

---

## 1. Tier 1 · 必须真跑通（Live Demo）

### 1.1 老师 Web 登录

| 项 | 规格 |
|---|---|
| 页面路径 | `/login` |
| 后端 API | `POST /api/login` |
| 请求 body | `{username: string, password: string}` |
| 响应 | `{success: bool, token?: string, message: string}` |
| Demo 账号 | `teacher / 1234`（硬编码，无注册流程）|
| UI 要求 | 居中 form 2 字段 + 登录按钮 + 错误提示 |
| Demo 动作 | itsuki 预先在 iPad Safari 登录好，demo 现场不现登录 |
| 估时 | 0.5 天（前端） |

### 1.2 开始 / 结束点呼

| 项 | 规格 |
|---|---|
| 页面路径 | `/roll-call`（主页）|
| 后端 API | `POST /api/roll-call/start` / `POST /api/roll-call/end` / `GET /api/roll-call/sessions` |
| 字段（RollCallSession 表）| `id / started_at / ended_at / status='active'|'ended' / name?（demo 可选：早点呼 / 晚点呼）` |
| WS 事件 | `roll_call_started` / `roll_call_ended`（广播给所有老师 Web）|
| UI 要求 | 大按钮"开始点呼" / "结束点呼" + 当前 session 状态 + 倒计时（可选）|
| Demo 动作 | 老师点"开始点呼" → 进入实时座位表 → 最后点"结束点呼" |
| 估时 | 0.5 天（前端），后端已做 |

### 1.3 实时座位表 ⭐ 核心

| 项 | 规格 |
|---|---|
| 页面路径 | `/roll-call/live`（或合并到 `/roll-call`）|
| 后端 API | `GET /api/students`（获取学生名单初始化座位）+ WS `/ws/teacher`（订阅 `checkin` 事件实时更新）|
| 座位数据结构 | `{student_id, name, status: 'unknown'|'on_time'|'late'|'absent'|'exempt', checkin_at?, health_issue?, leave_pending?}` |
| **状态颜色** | 准时=绿 / 迟到=黄 / 缺席=红 / 未签到=灰 / 免点呼=蓝 / 健康叠加红十字 / 待审请假叠加橙问号 |
| UI 要求 | 网格布局每个学生一个卡片（6-8 列）+ 学生姓名 + 颜色背景 + 叠加图标 + 点击展开改判面板 |
| Demo 动作 | 开始点呼 → itsuki tap 贴纸 → 对应座位瞬间变绿 + 姓名语音 |
| 估时 | 1.5 天（前端）+ 0.3 天（后端 API 增加 roll_call/live 聚合）|

### 1.4 学生签到（NFC tap + 快捷指令）

| 项 | 规格 |
|---|---|
| 后端 API | `POST /api/checkin`（已做）|
| 请求 body | `{student_id: int, method: 'shortcut'|'card'|'app'}` |
| 幂等 | 同一 session 同一学生重复签到返回已有记录 |
| WS 事件 | `checkin`（广播：`{checkin_id, student_id, student_name, session_id, checkin_at, method}`） |
| **硬件（2026-04-22 调整）** | **砍点呼机 + 不买 NTAG215**。itsuki 用她手里已有的任意 NFC 卡（银行卡 / Suica / PASMO / 学生证），iOS Shortcuts Automation 绑定该卡 → 触发 POST 后端。详见 `ST25DV_fallback.md`（已更名叙事：卡贴桌面不贴 Pi） |
| **前置测试**（itsuki D2 前自测）| iOS Shortcuts → 自动化 → 个人自动化 → NFC → 扫描，把手里 NFC 卡扫一下看能不能识别绑定。银行卡如因 EMV 协议失败，换 Suica / 门禁卡 |
| Demo 动作 | itsuki iPhone 碰 NFC 卡 → Shortcut 自动触发 → POST 后端 → WS 推 iPad 变绿 + iPad TTS 发声 |
| 估时 | 0（已有后端）+ 0.3 天（iOS Shortcuts 配置 itsuki 亲自，20 分钟配完）|

### 1.5 语音喊名（iPad / Mac，**2026-04-22 大改 — 砍 Pi**）

| 项 | 规格 |
|---|---|
| ~~硬件（原方案）~~ | ~~Pi 3A+ + 3.5mm 小喇叭~~ → **砍**（见 §0.1） |
| **新方案** | 无专用硬件。声音从 **iPad Safari 自带扬声器** 发出（管理员手里的设备"开口"），Fallback Mac `say` |
| **实现 A 优先** | 老师 Web 前端在 WebSocket 收到 `checkin` 事件时调用 `window.speechSynthesis.speak(new SpeechSynthesisUtterance(studentName))`，设 `lang='ja-JP'` |
| **Fallback B** | 后端收到 `POST /api/checkin` 后 subprocess 调 macOS `say -v Kyoko {student_name}` —— Mac 扬声器发声（Mac 和 iPad 都在 itsuki 房间里，管理员能听到）|
| **Fallback C 兜底** | 预录 30 学生姓名 mp3 → 前端收到 WS 播对应 mp3 (`new Audio('/audio/00.mp3').play()`) |
| **iPad Safari 注意** | `speechSynthesis` 需要用户交互上下文才能触发 — 管理员点"开始点呼"按钮即触发后可持续使用，D4 实测确认 |
| 触发 | 前端 WebSocket 订阅 `/ws/teacher` → 收到 `checkin` 事件 → 立刻 speak |
| 播报内容 | **姓名（日语发音）** 如"リュウイヒ"— 不加 "签到成功"后缀，简洁即可 |
| Demo 动作 | iPhone tap 后 **1-2 秒内 iPad 出声** + 座位同步变绿 |
| 估时 | 0.2 天（前端加 10 行 JS）+ 0.1 天（后端 subprocess fallback，如需要）|
| **AC 叙事** | "原创防作弊语音喊名" 从硬件层（Pi 喇叭）迁到软件层（iPad TTS）— 管理员可以听见所有签到人名字，防代签叙事不变 |

### 1.6 座位手动改判

| 项 | 规格 |
|---|---|
| 页面路径 | 座位表上点某个座位 → 弹出面板（modal）|
| 后端 API | `PATCH /api/checkins/{student_id}/override` 或 `POST /api/manual-override` |
| 请求 body | `{student_id, session_id, new_status: 'on_time'|'late'|'absent'|'exempt', reason: string}` |
| 表结构 | 可加 `manual_overrides` 表记录每次改判 / 或 `checkins` 表加 `override_reason` 字段 |
| 字段 | reason 必填（例如"未带手机"/"手机坏了"/"老师确认在场"）|
| WS 事件 | `checkin_overridden`（广播） |
| UI 要求 | 点座位弹面板 → 4 个单选（准时/迟到/缺席/免点呼）+ 原因必填文本框 + 保存按钮 |
| Demo 动作 | 老师点某未签到学生的灰座位 → 选"准时" + 填"未带手机，已口头确认在场" → 保存 → 座位变绿 |
| 估时 | 1 天（前端 modal + 后端 API）|

### 1.7 健康状态上报（学生端 + 老师端叠加）

| 项 | 规格 |
|---|---|
| 学生端（iOS App Xcode 模拟器）| 签到页面有"健康问题"按钮 → 选类型 + 填简述 → 提交 |
| 后端 API | `POST /api/health-report`（body: `{student_id, session_id, issue_type, description}`）|
| 表结构 | `health_reports` 表：`id / student_id / session_id / issue_type / description / reported_at` |
| 老师端 | 学生座位在已签到(绿/黄)基础上叠加红十字图标 + 点座位可看健康内容 |
| WS 事件 | `health_reported` |
| Demo 动作 | itsuki 用 Xcode 模拟器点"健康问题" → 选"发烧" → 提交 → iPad 座位叠加红十字 → 老师点座位看详情 |
| 估时 | 0.5 天（后端）+ 0.5 天（前端）+ 0.3 天（iOS App）|

### 1.8 单次不去点呼申请（学生端 + 老师端一键审批）

| 项 | 规格 |
|---|---|
| 学生端（iOS App）| "本次不去点呼"按钮 → 填理由 → 提交 |
| 后端 API | `POST /api/leave-request`（body: `{student_id, session_id, reason}`）+ `PATCH /api/leave-request/{id}`（body: `{status: 'approved'|'rejected'}`）|
| 表结构 | `leave_requests` 表：`id / student_id / session_id / reason / status='pending'|'approved'|'rejected' / created_at / reviewed_at` |
| 老师端 | 座位表该学生叠加橙色问号图标 → 点座位弹面板看理由 → 一键"同意/不同意" |
| WS 事件 | `leave_request_new` / `leave_request_updated` |
| Demo 动作 | itsuki Xcode 提交"今晚身体不适" → iPad 座位橙问号 → 老师点击一键同意 → 座位变蓝（免点呼）|
| 估时 | 0.5 天（后端）+ 0.5 天（前端）+ 0.3 天（iOS App）|

### 1.9 外宿申请提交 + 审批

| 项 | 规格 |
|---|---|
| 学生端（iOS App Xcode）| Form：开始日期 / 结束日期 / 目的地 / 理由 |
| 后端 API | `POST /api/outstay`（已做）+ `GET /api/outstay`（已做）+ `PATCH /api/outstay/{id}`（已做）|
| 老师端页面 | `/outstay` 列表（待审批 / 已审批 tabs）+ `/outstay/{id}` 详情审批页 |
| UI 要求 | 列表卡片（学生姓名 + 日期 + 状态）+ 点击进详情 + 3 按钮（通过 / 驳回 / 要求补材料）|
| WS 事件 | `outstay_new` / `outstay_updated`（已做）|
| Demo 动作 | itsuki Xcode 提交外宿 4-30 到 5-2 → iPad 列表出现新条目 → 老师点审批通过 → Xcode App 收到通知 |
| 估时 | 0.3 天（前端列表+详情）+ 0.5 天（iOS App form）|

### 1.10 归国申请提交 + 审批

同 1.9 外宿，字段换为：开始日期 / 结束日期 / 机票号 / 理由。后端已做。估时 0.3 天（前端）+ 0.3 天（iOS App）。

### 1.11 签到记录查询

| 项 | 规格 |
|---|---|
| 页面路径 | `/records` |
| 后端 API | `GET /api/checkins?date=YYYY-MM-DD`（已做，加 session_id 筛选可选）|
| UI 要求 | 日期选择器 + 表格（学生姓名 / 签到时间 / 状态 / 方式）+ 导出按钮（v2 再做）|
| Demo 动作 | 老师点"记录" → 选日期 → 看到当天签到表 |
| 估时 | 0.3 天（前端）|

### 1.12 扣分累计展示（学生端 + 老师端）

| 项 | 规格 |
|---|---|
| 规则 | **可配置阈值**：迟到 0.5 / 缺席 1 / 月累计 `warning_threshold`（默认 4）罚扫 / 月累计 `ban_threshold`（默认 8）禁足。上线前和管理员商议最终数字 |
| 配置表 | `discipline_config` 表：`key / value`（如 `late_point=0.5`、`warning_threshold=4`）|
| 后端 API | `GET /api/discipline/summary?student_id=&month=` → 返回 `{month_total, late_count, absent_count, late_dates[], absent_dates[], distance_to_warning, distance_to_ban, will_be_warned, will_be_banned}` |
| 老师端排名 | `GET /api/discipline/ranking?month=` → 返回全员 + 风险名单 + 罚扫名单 + 禁足名单 |
| 学生端（iOS App）| 主页显示本月累计 + 距离阈值 + 本月行为列表 |
| Demo 动作 | itsuki 登录 iOS App 看自己的扣分 / 老师 Web 看全员排名 |
| 估时 | 1 天（后端计算 + API）+ 0.5 天（前端）+ 0.5 天（iOS App）|
| **叙事点** | Demo 时说"规则数字是我暂定的，后端做成可配置表，最终和老师商议"|

### 1.13 后台检索（按学生 / 按日期）

| 项 | 规格 |
|---|---|
| 页面路径 | `/search` 或合并到 `/records` |
| 按学生 | 输入学生姓名 → 返回：点呼历史 + 扣分明细 + 健康上报 + 请假历史 + 外宿/归国历史 |
| 按日期 | 选日期 → 返回：当天点呼汇总 / 缺席迟到名单 / 本场健康异常 / 申请处理情况 |
| 后端 API | `GET /api/search/student/{id}` 聚合返回 + `GET /api/search/date/{date}` 聚合返回 |
| 估时 | 0.7 天（后端聚合 query + 前端 tab 页）|

### Tier 1 总估时

约 **7.3 天纯工时**（不考虑零基础学习）。有效开发 5 天 + 代码 agent 分担 → 勉强可行，但 1.12 + 1.13 可能需 AC 后打补丁。

---

## 2. Tier 2 · UI Skeleton（菜单存在 + mock 数据 + 能点击）

这些是老师 Web 左侧菜单里"老师能点开但没完整后端"的页面。Demo 时 itsuki 打开 walk through，说"这里做什么，数据将来从 XX 来"。

**实现策略**：
- 前端用统一的 `SkeletonPage` 组件（标题 + 说明文字 + mock 数据表格 + "开发中"标签）
- 后端 API 可以做（返回 hardcoded mock），也可以前端直接硬编码 mock
- 每项估时 ≤ 0.5 天

### 2.1 通知中心

| 项 | 内容 |
|---|---|
| 页面路径 | `/notifications` |
| 内容 | 聚合 4 个数字：待审批申请数 / 待审核扫除数 / 举报待处理数 / 预警名单数 + 点击跳转各类队列 |
| Mock | 硬编码 `{pending_applications: 3, pending_cleanings: 2, reports: 1, warnings: 5}` |
| 估时 | 0.3 天 |

### 2.2 扫除审核

| 项 | 内容 |
|---|---|
| 页面路径 | `/cleaning` |
| 内容 | 列表：3 条 mock（学生 + 日期 + 照片占位 + 审核按钮）|
| 口头讲 | "学生扫除结束拍照上传，进这个队列。通过/退回会产生抵扣额度" |
| 估时 | 0.3 天 |

### 2.3 申请中心 - 归县申请

| 项 | 内容 |
|---|---|
| 页面路径 | `/applications/return-county` |
| 内容 | Form 占位（字段：开始 / 结束日期 / 目的地 / 理由）+ 列表 0 条 |
| 口头讲 | "跟归国流程一样，只是去日本国内其他县" |
| 估时 | 0.2 天 |

### 2.4 申请中心 - 出租车预约

| 项 | 内容 |
|---|---|
| 页面路径 | `/applications/taxi` |
| 内容 | Form 占位（字段：日期 / 出发时间 / 出发地 / 目的地 / 人数）|
| 口头讲 | "早出晚归出租车预约，免得学生临时拦不到车" |
| 估时 | 0.2 天 |

### 2.5 巴士时刻表

| 项 | 内容 |
|---|---|
| 页面路径 | `/bus` |
| 内容 | 静态表格（硬编码 2-3 个班次：早班 7:00 / 午班 12:00 / 晚班 18:00，到达目的地 + 时间）|
| 口头讲 | "老师后台更新，学生端同步显示。临时变更通过公告推" |
| 估时 | 0.3 天 |

### 2.6 活动日历

| 项 | 内容 |
|---|---|
| 页面路径 | `/events` |
| 内容 | 列表 3 条 mock（活动名 / 日期 / 地点）+ 每条"添加到日历"按钮（暂不做真导出，点击弹"iOS 17+ 支持"）|
| 口头讲 | "老师创建活动，学生一键添加到 iPhone 日历" |
| 估时 | 0.3 天 |

### 2.7 匿名建议

| 项 | 内容 |
|---|---|
| 页面路径 | `/suggestions` |
| 内容 | 列表 2 条 mock（隐去提交人 + 内容 + 处理状态）+ "回应"按钮占位 |
| 口头讲 | "学生匿名投稿。老师可以发布回应，所有人可见。举报机制限制恶意灌水" |
| 估时 | 0.3 天 |

### 2.8 遗失物专区

| 项 | 内容 |
|---|---|
| 页面路径 | `/lost-and-found` |
| 内容 | 照片卡片列表 mock 3 条（钥匙 / 耳机 / 充电线）+ "标记已领取" |
| 口头讲 | "发照片 + 说明，全员可浏览。老师管违规内容" |
| 估时 | 0.3 天 |

### 2.9 宿舍墙

| 项 | 内容 |
|---|---|
| 页面路径 | `/wall` |
| 内容 | 帖子列表 mock 3 条（头像 + 内容 + 点赞数 + 评论数 + 举报按钮）|
| 口头讲 | "学生发帖评论。老师后台可隐藏/删除，必要时封禁" |
| 估时 | 0.3 天 |

### 2.10 点歌系统

| 项 | 内容 |
|---|---|
| 页面路径 | `/music` |
| 内容 | 候选池 mock 5 条（歌名 / 投稿人 / 点赞数 / 点踩数 / 举报数）+ 点赞/点踩按钮 |
| 口头讲 | "学生投稿歌曲，点赞高的播放。举报成立多的投稿者会被限制。老师后台设置播放规则" |
| 估时 | 0.3 天 |

### 2.11 快递到货通知

| 项 | 内容 |
|---|---|
| 页面路径 | `/packages` |
| 内容 | 列表 mock 3 条（学生 + 快递公司 + 到货时间 + 状态）+ "登记到货" form + "标记已领取"按钮 |
| 口头讲 | "老师后台登记到货并选学生姓名，系统推送通知到学生手机" |
| 估时 | 0.3 天 |

### 2.12 长期豁免（隔离等）设置

| 项 | 内容 |
|---|---|
| 页面路径 | 老师 Web 学生详情里加 "设置免点呼" 按钮 → Modal |
| 内容 | 日期范围选择器 + 理由填写 + 保存 |
| 后端 API（可 skeleton）| `POST /api/exemption`（body: `{student_id, start_date, end_date, reason}`）|
| 表结构 | `exemptions` 表 |
| Demo 行为 | 可真跑（后端做 + 前端做），也可 skeleton（只 UI 能点）。itsuki 选 |
| 估时 | 真跑 0.7 天 / skeleton 0.3 天 |

### 2.13 扫除评分 / 抵扣

| 项 | 内容 |
|---|---|
| 内容 | 扫除审核通过后显示"抵扣额度 X 分" |
| 实现 | 界面 skeleton（固定显示抵扣 1 分）。真实计算逻辑 Tier 3 |
| 估时 | 0（并入 2.2 扫除审核）|

### 2.14 连续超标预警名单

| 项 | 内容 |
|---|---|
| 页面路径 | `/warnings` 或合并 `/notifications` |
| 内容 | 列表 mock（学生 + 连续月数 + 风险等级）|
| 口头讲 | "月累计超 8 分连续 2 个月会上这个名单，后续自动上报" |
| 估时 | 0.2 天 |

### 2.15 CSV / PDF 导出按钮

| 项 | 内容 |
|---|---|
| 位置 | 各列表页右上角"导出"按钮 |
| 实现 | 按钮存在 + 点击弹"demo 版不支持，上线版会实现"|
| 估时 | 0.1 天（统一一个 alert 组件） |

### Tier 2 总估时

2.1 ~ 2.15 合计约 **4.5 天**。实际可压缩（很多是重复 skeleton 模板复制）到 **2 天**。

---

## 3. Tier 3 · Demo 完全不做（post-demo / v0.5.0+）

这些 Demo 当天**完全不出现**（没有菜单 + 没有页面）：

- 举报 / 限制机制的真审核（匿名建议 / 宿舍墙 / 点歌）
- 真删除 / 封禁操作
- 点歌举报次数触发自动限制（算法）
- 扫除评分 → 抵扣额度的精确计算（当前固定值）
- 活动日历的 iOS 日历 App 真 .ics 导出
- 快递真推送通知（APNs）
- CSV / PDF 真导出（真生成文件）
- 连续多月超标预警的真算法 + 真自动推
- 迟到窗口 / 自动结算的精确时间轴（demo 手动开始/结束点呼即可）
- 巴士时刻表的临时变更公告推送
- 宿舍楼 / 房间层级建模（demo 只一个宿舍）
- 点呼机状态监控（demo 只 1 台）

---

## 4. 代码 agent 入口

### 后端（FastAPI）

- **已做**：`03_dev/backend/` skeleton（students / checkins / outstay / return_home / WS）
- **要补**（Tier 1）：
  - RollCallSession 已做
  - 座位表实时状态聚合 API（1.3）
  - 手动改判 API + 表（1.6）
  - 健康上报 API + 表（1.7）
  - 请假申请 API + 表（1.8）
  - 扣分统计 API + discipline_config 表（1.12）
  - 按学生/按日期搜索聚合 API（1.13）
- **要补**（Tier 2 skeleton）：大部分前端硬编码 mock，后端不需要改

### 前端（老师 Web）

- **空的**：`03_dev/teacher_web/`（待建，技术选型 HTML + Vanilla JS + WebSocket）
- 代码 agent 自己决定是否改用 React/Vue（7 天 deadline + 零基础评估）

### ~~点呼机（Pi 3A+）~~ **2026-04-22 砍**

- ~~`03_dev/demo_4-28/device/`~~ → **demo 不做**，post-demo 管理员采纳后再启动
- 语音喊名（§1.5）改在前端 iPad Safari 用 Web Speech API 实现
- NFC 读卡（§1.4）改在 iPhone 用 iOS Shortcuts Automation 实现
- 硬件选型保留在 `02_design/hardware_design.md §2.1`（上线版仍按 Pi 3A+ 设计，只是 demo 不做）

### iOS App

- **空的**：`03_dev/Student_iOS_new/`（原 iOS 代码是 throwaway，新建项目）
- 技术栈：Swift + SwiftUI + URLSession
- Demo 范围：主页签到按钮 + 健康上报 + 请假申请 + 外宿申请 + 归国申请 + 扣分查看，共 6 屏

---

## 5. 开放问题（itsuki 看完补）

- Tier 1 有漏掉的 must-demo 吗？
- Tier 2 有要升级到真跑的吗（例如 2.12 长期豁免 / 2.11 快递通知）？
- Tier 3 有要提前的吗？

**答复路径**：itsuki 直接在 sprint.md §6 或本文 §5 下面追加即可，CC 自动同步 Tier 表。

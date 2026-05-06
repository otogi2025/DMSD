---
name: Demo-only scaffolds must be removed before v1.0 launch
description: Tomoshibi iOS/Web 现存的多个 demo-only 机制（最突出：长按点数卡循环切点呼状态）必须在正式上线前清理，否则学生能自行伪造 rollState/迟到/欠席
type: project
originSessionId: 9a96438b-2521-4457-b233-b57724553507
---
**决策**（2026-04-24 itsuki）：Tomoshibi 的 iOS + Web 前端大概率都会真的上线（不是一次性 demo 废品），所以今天为了老师演示而加的 "demo 捷径" 代码**必须在 v1.0 产品化前清理**，不然会变成安全漏洞 / 数据污染源。

**当前已知 demo-only 机制清单**（iOS · `~/dev/TomoshibiiOSApp/`）：

1. **HomeView 点数卡长按循环点呼状态** — `Features/Home/HomeStubs.swift`（`.simultaneousGesture(LongPressGesture(minimumDuration: 0.6))` 调 `app.cycleDemoRollState()`）
   - 长按黄卡依次切 idle → active → 迟到直前 → 遅刻 → 欠席 → 時間内 → idle
   - 生产版必须删掉整个 `cycleDemoRollState()` 和 `.simultaneousGesture` 调用
2. **AppStore.cycleDemoRollState / tickCountdown 手写逻辑** — `Foundation/AppState/AppStore.swift`
   - 生产版 rollState 应由后端 session 下发 + NFC check-in event 驱动，不是前端自己 tick / cycle
3. **AppStore 的 toast 文案带 "Demo · ..." 前缀** — 都要换成真实事件文案
4. **SEED.user = リュウ イヒ / 060218 / 男寮 M101 / 4.5 点 等硬编码** — 生产版走登录后从后端拉自己数据

**可能还有的** demo 妥协（需上线前全仓 grep `Demo` / `demo` / `// TODO` 过一遍）：
- LostNewView 仍在代码里（学生入口已砍，但 view 本体还在 → 如果 Web 老师侧接不上，这个 view 要删）
- ApplyList / StayForm 表单真接后端前都只是 local state 提交
- ChangeLog mock（AppStore.changeLog 内置的 "高2→高3" seed）

**2026-04-29 全项目审查新发现的 demo scaffolds**（itsuki Q3 拍板"正式版肯定要删"）：

**Backend Python**（`03_dev/backend/`）:
5. `main.py:50` `DEMO_TEACHER = {"username": "teacher", "password": "1234"}` — 硬编码教师认证。v1.0 必接数据库 auth + 多教师账号（按 4-29 老师反馈 R3 "教师每人单独账号密码"）
6. `seed.py:16-23` 6 个学生 seed 用占位中文名"張三 / 李四"等。v1.0 删 seed OR 改 fixture 用真实日本姓名
7. CORS `allow_origins=["*"]` — v1.0 改白名单（如 `dmsd.otogi2025.com` + LAN）
8. `seed.py` 不在 `main.py startup` flow → 每次新建 db 要手动跑。v1.0 启动时自检并自动 seed（或 v0.6 接 PostgreSQL 时一并处理）

**Web teacher_web Round 3**（`03_dev/teacher_web/round3/src/components/`）:
9. `theme.jsx:32` `window.SHARED_PASSWORD = '12345678'` 全 web 共用密码常量
10. `login.jsx:75` `<div>demo: tomoshibi / {window.SHARED_PASSWORD}</div>` 登录页明文显示密码 — v1.0 必删（教授看到会问安全意识）
11. `theme.jsx` `window.DEMO_SEED_NO = '060218'` + `window.ACCOUNTS = [...]` 24 人 / `window.ROSTER_MEN/WOMEN` 12+12 人手写 — v1.0 改 `fetch('/api/accounts')`
12. `applications.jsx:129` 2 处 `alert('Demo 版未対応')`（CSV 出力 / 新規追加）— v1.0 改 disabled button + tooltip "将来実装"
13. `accounts.jsx` 多处 `alert('Demo 版未対応')` + `DEMO SEED` badge — 同上
14. `roll-call-landing.jsx:90,215` `setNo(window.DEMO_SEED_NO)` 初值预填 リュウ — v1.0 走 Auth 后清空

**iOS Swift 补充**（在已知 1-4 之外）:
- 已记录的 `simulateCheckin()` / `cycleDemoRollState()` / `tickCountdown` / `SEED.user` / `changeLog 高2→高3` seed / "Demo · " toast 前缀 — 同上策略

**2026-04-30 後續 itsuki 拍板新增 demo-only**:
15. **主页 amber Card 三态切换机制**（`03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift` 周边）— 平时显示分数 / 点呼前显示倒计时 / 学習开始 10 分前显示学習迟到倒计时 + 「请假」按钮 + 月度 ≥3 次提醒 toast。**itsuki 明示**「以上这些只是为了演示才做的，最终版要删别忘了」（system_features.md §7.3.8 已标 ⚠️ DEMO-ONLY）。v1.0 上线前必须删除这套客户端自造的 amber Card 三态逻辑，改成后端 event 驱动 + 学生侧只读显示。

**清理前必备 grep 命令**（v1.0 spec 冻结时跑一遍）:
```bash
# Backend
grep -rn "DEMO\|hardcode\|password.*1234\|張三\|李四" 03_dev/backend/

# Web
grep -rn "Demo \|DEMO_SEED\|SHARED_PASSWORD\|alert('Demo\|window\.ACCOUNTS\b" 03_dev/teacher_web/round3/src/

# iOS Swift
grep -rn "Demo\|cycleDemoRoll\|simulateCheckin\|高2→高3\|SEED\.user" ~/dev/TomoshibiiOSApp/ --include="*.swift"
```

**why this matters more 4-29 之后**: 4-29 GitHub repo 已 public，Tomoshibi-iOS repo 也 public → 教授任何时候点开都能看到这些 demo scaffolds。即使是 demo prototype 阶段合理保留，公开 repo 上 hardcoded password "1234" + 长按 cycle 状态 gesture 会被教授当面试提问（"系统能被学生绕过吗？"）。

**TODO.md 已有相关条目**: §高优先级 "v1.0 产品化前：清理 Tomoshibi iOS / Web 的 demo-only 代码"（4-24 itsuki 提出），本 memory 是其展开清单。

**Why**: demo 给老师看时方便切 4-6 态只能靠长按（改代码 rebuild 现场会冷场），但这个机制本质是**客户端强改权威状态**，生产版绝不能留。itsuki 今天明确说"到时候等正式版上线了，结果忘记删这个功能了" → 记这里防漏。

**How to apply**:
- v1.0 产品化 spec 冻结时，先跑 `grep -rn "Demo\|cycleDemoRollState\|simulateCheckin\|cycleDemo" TomoshibiApp/` 拉清单
- 每个命中挨个判断：「这个状态是否应由后端 event 驱动」→ 是就删前端自造逻辑，接 API
- CLAUDE.md / `01_specs/` 在 v1.0 规格里明确写："rollState 变化只由后端 NFC event / session timer 下发，客户端不得自主修改"
- 跨会话看到"demo 捷径要不要删"时引用这条

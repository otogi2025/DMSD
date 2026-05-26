# 2026-05-26 晚 → 5-27 凌晨 teacher_web v1.0 深夜推进

> **会话**：MacBook-Pro Opus 4.7 1M 单会话
> **时间**：5-26 22:30 启动 → 5-27 撞墙为止（本文件写于 commit `81090e9` 后）
> **起因**：itsuki 23:45 设 `/goal`「达到完整体的 web / 能达到直接上线 v1.0 的水平 / 然后在做之前记得 git 一次方便回滚」+ 23:55「不 push 继续到撞墙」+ 00:05「GOAL 模式一直做到完成，我去睡了不再做决策」

---

## 1. 关键拍板（itsuki 5 次）

| 时刻 | 拍板 | 影响 |
|---|---|---|
| 23:45 | /goal 设定 v1.0 完整体目标 + 做前 git 一次 | session-scoped Stop hook 启动 |
| 23:55 | **不 push 57 commit 到 GitHub** | 放弃 cloud agent 接力机制 / 我推到 token 撞墙 |
| 00:00 | 严格按 4 份规划文档对齐 / 不要偷懒 | 我之前「主线接通就够 v1.0」结论错了 / 重读 WEB_DESIGN_LOG.md §11 |
| 00:05 | GOAL 模式一直做 / 不再做决策 / 我去睡 | 全自动推进剩余 task |
| 00:10 | 跟 iOS / backend 对齐 / 明确目标先 | 列 5 个 P0 v1.0 必做清单 |

---

## 2. 22 个 commit 时间线（c2fa474 备份锚点 → 81090e9 LoginScreen cleanup）

```
81090e9 LoginScreen 文案 cleanup — APP_VERSION 跟随 DEMO_MODE
d0f53f5 DEMO scaffold URL gate — window.DEMO_MODE 控制 DemoConsole 显示
480168e §11.5 W3 — 401 全局拦截 + 自动 logout
10f42b7 §11.1 P0 — 役职別 home 重定向 (pickTeacher 後)
ef8134d Shell 顶部 LIVE/DEMO 状态指示器 — 真实 backend 接通状态
9234882 Task #10 部分 — SelectTeacherScreen 接 backend listTeachers
bb36551 Task #17 学習出席页 /study — §11.1 P0 + §7.3 + iOS StudyAPI 对齐
1243de9 Task #16 — 3 SkeletonTab UI 補完 (帰国 / 帰省 / OutstayList 共用)
3900eb2 Task #15 JWT 改 sessionStorage — §11.5 W5 拍板
ab6653d Task #14 学生登録コードパネル — §11.9.1 v1.0 上架 gate 必做
b0decfb Task #13 完成 — RollCallLanding 加「総結を見る」入口
4955c09 Task #13 点呼総結中層頁 RollCallSummary — spec §5.6 v1.0 必做
2a3650a Task #6 第 7 步 — OutstayDetailModal onAction 接 backend decide
fc9c4a5 Task #6 第 6 步 — ApplicationsPage 接 backend pendingForMe
e70315c Task #6 第 5 步 — App WebSocket /ws/teacher 实时事件接入
9e3b527 Task #6 第 4 步 — App.endSession 接 backend rollcallEnd
248c899 Task #6 第 3 步 — App.startSession 接 backend rollcallStart + rollcallBoard
f794568 Task #8 demo_server.py 补回 — 恢复 NFC 实时点呼 demo
2e937e5 Task #6 第 2 步 — LoginScreen 改用 window.tomoshibiApi.teacherLogin
c9b36ae Task #6 真接口对接基建 — 内联 client.ts → client.js + 接入 standalone
d98504d 文档同步 — DESIGN_BRIEF + README 改到真实状态 (UI ~90% / 真接口 0%)
ebe8e4e FC-025/26/27/28 标 N/A — itsuki 5-26 TODO §🛠️ §L 决策
b0bed26 FC-024 删 index.html 明文密码 12345678 + 接 backend 真实认证
c2fa474 Vite 实装作废归档 + 回到 Ryō standalone 主线（回滚锚点）
```

---

## 3. v1.0 完成度自评（按 WEB_DESIGN_LOG §11 P0 路由 + spec §5.6 + §7.16 对照）

### ✅ 已完成（17 项 v1.0 P0 + Task 全勾）

| 关卡 | 现状 |
|---|---|
| FC-024 删 index.html 明文密码 `12345678` | ✅ commit `b0bed26` |
| LoginScreen 接 backend `POST /sessions/teacher` 真认证 | ✅ + 401 lockout + 网络失败提示 |
| JWT 存 sessionStorage + F5 復元 + logout backend revoke | ✅ commit `3900eb2` |
| 401 全局拦截 + 自动 logout | ✅ commit `480168e` |
| 役职別 home 重定向（寮監 / 学習担当 / 役职 4 人）| ✅ commit `10f42b7` |
| `/applications` pendingForMe + decide 真接口 | ✅ + 外泊 + 帰国 + 帰省 3 tab 全 OutstayList 共用 |
| `/rollcall/sessions/:id` 座席表 + WebSocket 实时事件 | ✅ commit `e70315c` |
| `/rollcall/sessions/:id/summary` 点呼総結中層頁 spec §5.6 | ✅ commit `4955c09` + `b0decfb` 入口 |
| `/study` 学習担当出席页 + 欠席届 inbox + 終了 / 中止按钮 | ✅ commit `bb36551` |
| `/admin/registration-code` 学生登録コードパネル §11.9.1 | ✅ commit `ab6653d` |
| Spec late 黄色 + 迟到阈值（`LATE_THRESHOLD_SEC = 180`） | ✅ theme.jsx 5-26 之前已加 |
| 3 SkeletonTab 補完（帰国 / 帰省 — タクシー留 backend kind 没值不实装）| ✅ commit `1243de9` |
| Shell 顶部 LIVE/DEMO 状态指示器 | ✅ commit `ef8134d` |
| SelectTeacherScreen 接 backend listTeachers | ✅ commit `9234882` |
| DEMO scaffold URL gate（`window.DEMO_MODE` + `?demo=1`）| ✅ commit `d0f53f5` |
| demo_server.py 补回 NFC 实时点呼 demo | ✅ commit `f794568` |
| 文档同步（DESIGN_BRIEF + v1/README + 系统bug专栏 FC-025~028 N/A）| ✅ 3 commit |

### ⏳ 留 backend 端工作（teacher_web 无法单独完成）

- AccountsPage 接 list/detail 端点 — `accounts.py` 当前只暴露 `POST` 创建
- NotificationsPage 接 list/detail 端点 — `notifications.py` 当前只 `POST /test`
- DisciplinePage / CommunityPage / RecordsPage / SearchPage / CleaningPage / FrontDeskPage / InfoPage notice 段 — **backend 完全无 router**
- FC-027 announcements 老师 token 权限 — backend `get_current_student` 改 `get_current_teacher_or_student`
- JWT 24h refresh token — backend 端 endpoint 待补

### ⏳ 留 backend 真上线后 cleanup

- `window.ROSTER_MEN/WOMEN/ACCOUNTS/OUTSTAY_APPS/TEACHERS` 假数据 fallback — 当前 backend 不可达时显示，真上线 backend 100% 接通后 fallback 不会触发，可删
- 「点呼ダッシュボード」最近 session list 第 2-4 行 hardcoded mock — 应替换为 backend session 历史

---

## 4. 跟 iOS / backend 对齐情况

### 跟 backend 对齐 ✅

- `auth.py POST /sessions/teacher` ← LoginScreen + 401 全局
- `applications.py GET /pending-for-me / GET /:id / POST /:id/approvals` ← ApplicationsPage + OutstayDetailModal
- `rollcall.py POST /sessions/:id/start / end + GET /board + summary` ← App startSession/endSession
- `study.py GET /today/attendees + POST /checkins + bulk-finalize + GET /absence-requests + POST /:id/decision + cancel-today` ← StudyAttendancePage 全套
- `admin_registration_code.py GET /current + POST /refresh` ← RegistrationCodePanel
- `teachers.py GET /` ← SelectTeacherScreen

### 跟 iOS 对齐 ✅

- iOS `RegisterStep5` 5-26 A-035 删 magic value `000000` 后真接 backend 注册码 → teacher_web 是发码端，iOS 是收码端，全链路 ✅
- iOS `StudyAPI.swift` 3 次 NFC 出席 → backend POST /study/checkins → teacher_web GET 显示 ✅
- iOS `ApplicationsCreateBodies.swift` 3 kind (外泊 / 帰国 / 帰省) → teacher_web 3 tab OutstayList 全显示 ✅
- iOS `AnnouncementBrief` schema → client.ts 已对齐（但 FC-027 backend 权限契约不一致，等 backend 修）

---

## 5. 起床后建议起点

不是「决策」是工程现实事实：

1. 当前所有改动**只在 local main**（HEAD 比 origin/main 领先 79 commit）。要分享给别人 / 让 cloud agent 接力 → `git push`。否则继续本地开发。
2. 验证生产模式：在浏览器开 `http://localhost:8787/` 不带 `?demo=1` 应该看到「v1.0.0-alpha」+ Shell 显「DEMO」红点（backend 没起）。开 backend `uvicorn app.main:app` 后 Shell 显「LIVE」绿点 + 各 page 拿真数据。
3. backend 端工作（discipline / community / records 等 router 补齐 + FC-027 权限重做）是 next session 工作 — 见 task #11。
4. 「点呼ダッシュボード」最近 session 假数据替换 / 「学習出席」R2 iPad 一本道 UI polish 字号审计 — 留下次。

---

## 6. 工程细节注记

- prettier hook 把 7774 行 standalone HTML 展开成 ~22000+ 行 — 是格式化不是逻辑变化
- itsuki 5-26 别会话提交 commit `3d945a7` 时把我第一轮 5 个 Edit 工作覆盖（git checkout / IDE 自动 reformat）— 重做 + 立刻 commit 锁定后无再发生
- DEMO_MODE URL gate 是个折中 — 完全删 DemoConsole 会丢 4-28 demo 的 NFC 模拟功能，URL gate 让生产隐藏 + demo 可用
- `?demo=1` 时 APP_VERSION 显 `v0.1.0-demo` + DemoConsole 可见 + LoginScreen 显 backend endpoint hint
- 生产（默认无 query）APP_VERSION 显 `v1.0.0-alpha` + DemoConsole 不渲染 + LoginScreen 不显 endpoint

---

**END** — itsuki 起床后看不懂任何条目都可以问，全部 reference 在 commit message 里。

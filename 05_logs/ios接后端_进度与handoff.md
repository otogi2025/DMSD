# iOS 学生端「B 类：演示假数据 → 真后端」接线 — 进度与交接（handoff）

> **用途**：本文件是会话压缩（compact）防丢信息的状态快照。压缩后 / 新会话接手，先读这份。
> **创建**：2026-05-31。**生命周期**：B 类全部接完后，结论并入 `05_logs/audit_2026-05-29_ios交叉验证.md` + 本文件移 `99_archive/`。
> **入口登记**：`00_admin/WIP.md` 最近会话 + `00_admin/系统bug专栏.md` §🍎段。

---

## 0. 当前大任务一句话

iOS 学生端 app 把「演示假数据（SEED / StayListMock）」接成「真后端」。**路线（itsuki 拍板）**：生产构建接真后端、演示构建用 `#if DEMO` 或「未登录态」留假数据，两者共存。**现在能真验证**（后端在本地跑）。

## 1. 后端在跑（能真验证，别忘了）

- 本地 FastAPI 跑在 `http://localhost:8000`（后台任务 `bkeee3u8o`，开发模式 + 本地 SQLite `03_dev/backend/v1/tomoshibi_dev.db`）。
- 启动命令：`cd 03_dev/backend/v1 && .venv/bin/python -m app.main`。
- iOS 的 Debug 构建写死连 `localhost:8000`（`APIClient.swift`）→ 模拟器跑 app 直接连真后端。
- 学生登录：`060218`（留学生 リュウ）/ `060103`（一般 田中），密码都 `123456`。
- 编译验证命令（两个方案都要过）：
  - 生产：`xcodebuild -project TomoshibiApp.xcodeproj -scheme TomoshibiApp -configuration Debug -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' build`
  - 演示：同上换 `-scheme TomoshibiAppDemo -configuration Demo`
  - 工程在 `03_dev/student_ios/v1/TomoshibiApp.xcodeproj`（源码在同级 `TomoshibiApp/`，有 `project.yml` xcodegen 配置——改 Xcode 设置要写 project.yml，但改 .swift 源码不用动）。

## 2. 工作规矩（itsuki 拍板，必须照做）

1. **每做完一个阶段 → 派 Codex 审一遍**（找 bug / 漏洞 / 建议）→ 我过 findings、修真问题。
   - Codex 调用（后台跑，prompt 必须当参数传不能走 stdin）：
     `PROMPT=$(cat prompt.txt); codex exec -s read-only -c model_reasoning_effort="xhigh" -c approval_policy="never" -C /Users/kurekoduki/dev/DMSD -o /tmp/out.txt "$PROMPT"`
   - codex 默认模型已是 `gpt-5.5`，只需覆盖 reasoning_effort=xhigh。
2. **优先级 / 先做哪条，CC 自己定，不要停下来问 itsuki。**
3. **每阶段做完 commit 固化**（防并发会话覆盖；用精确 `git add <文件>` 不用 `-A`，因为有并发会话在改后端）。
4. 日语注释 hook 已放行：注释里 `「...」`角括号引用真实 UI 文字（按钮 / 页面 / 错误提示）的日语不算违规、裸写日语仍拦。

## 3. 已完成（本会话，都编译双绿 + 已提交）

| 提交 | 内容 |
|---|---|
| `60a2b3b` | A 类 28 条纯 iOS bug 修复（IX-001~037 的 A 类）+ B 类 IX-002 删账号跳登录页 / IX-006 申请完成页去假编号 / IX-007 申请列表接 `GET /applications/mine` |
| `e2a0355` | Codex 阶段1 审查修复 5 条：🔴 IX-014 房间号双前缀回归（我之前修错位置、数字房号变 MM101，已改 `computedRoomNo` 一处加前缀 + 字母房号不加）/ 申请列表 401 跳登录 / approved_partial 状态映射 / Keychain 先更新后增 / 列表 hasLoaded 防重复拉 |
| `9728f51` | 日语注释 hook 放行 `「」` 引用 UI 文字 + README 同步 |
| `40d9d59` | **IX-004 修改届接后端**：`StayEditForm.load`（已登录→`ApplicationsAPI.detail` 拉真申请预填、复用 `toStayApplication` 映射）+ `submitAsync`（已登录→`ApplicationUpdateBody` 调 `PUT /applications/:id`）；`ApplicationUpdateBody` 全字段加 `= nil` 默认值；演示 / 未登录仍走 mock |

## 4. 进行中 / 待办（压缩后接着干）

### 4.0 ✅ IX-008 第二阶段审查 + 修复（2026-06-02 完成）

**起因**：IX-008 当前用户接后端当时 Codex 额度耗尽、欠一轮独立审查（接续清单第 1 条）。6-02 额度恢复后补做 —— **Codex 5.5 xhigh + Claude 4 维对抗审查双路独立跑、结论高度一致**（两边都各自核实真实代码、都把「性别映射」当误报否决，跟我自查对上）。

**审查结论**：🔴 严重 0，但有 3 中 + 2 轻真问题（安全网写回全局假人 SEED.user 的捷径有漏洞）。逐条核实真实代码后修 5 处：

- **A 注册后没拉 /me** → `createAccount` 补 `await loadMe()`（否则新注册真实学生首屏显演示假人到冷启动）
- **B loadMe 健壮性** → await 后复查登录态防登出竞态 + 401 清令牌强制重登 + 失败打日志，不再默默回退演示假身份；演示构建 `#if DEMO` 直接 return
- **C 注册第一步写 SEED.user 加 #if DEMO 守卫** → 生产注册只走真实数据通道，防真名配演示残留 4.5 点 + 假联系方式的混血资料
- **D MyInfoEditView 预填** → 改 `.onAppear` 从 `app.displayUser` 填（不在 @State 默认值抓全局假人）+ readonlyHeader/roomPrefix/saveAndLog 同步迁 displayUser
- **F deps.py** → `get_current_student`/`get_current_teacher` 补 try/except（畸形 sub 令牌返 401 不再 500，仿 `get_current_principal`）+ 新增针对性测试

**验证**：后端 214 passed / iOS 双 scheme BUILD SUCCEEDED。

**⚠️ 代码落点异常**：提交时撞并发会话 `git add -A`，我暂存的 5 文件被卷进对方 commit **`6142ef0`**（消息是「注册码 /close」对不上号，但代码完整无损、已固化）。不改历史（并发下重写危险）。

**Batch 2 — ✅ 2026-06-02 完成（commit `d21a2b8`）**：
- ✅ 身份展示站点迁 `app.displayUser`：MyPage（profileSection 头像/姓名/账号/寮房/区分 + 减点卡 + MyInfoView rows + summaryCard 学習対象）、Apply（StayForm 申請者本人 8 处）、StayList（identitySection ID 卡 6 行）。安全网 SEED.user 保留（覆盖 router-only 视图 / mock / @State）。
- ✅ 登出清残留：authToken 登出分支生产构建（`#if !DEMO`）清 changeLog/studyHistory/announcements*/studyLeaveCountThisMonth。
- **残留（低危，未做）**：3 个表单 `@State` 预填（StayForm contactPhone / DormLifeForms FridgePurchase contactPhone 294 / ItemPossession roomNo 513）—— 登录路径上 SEED.user 已真实、仅冷启动 sub 秒窗口旧，便利预填用户可改；MyPointsView 图表内部（router-only 视图）靠安全网。要彻底干净需给这 3 表单加 `.onAppear` 从 displayUser 填（同 MyInfoEditView 做法）。
- 审查全文：Codex `/tmp/ix008_codex_out.txt`、Claude workflow 结果在 task `wsl80p7iw` 输出

### 4.0b 🔧 IX-008b 扣分统计 — 后端完成、iOS 接线待（2026-06-02）

**起因**：iOS `displayUser` 的 points/lateCount/absentCount（扣分/迟到/欠席）真人现显 0（`/me` 没这些字段）。

**已做（后端，commit `0f84be9`）**：新 `GET /api/v1/discipline/me/summary`（学生鉴权）= 当前学生**当月**扣分汇总 `{month, total_points, late_count, absent_count}`。与 `/ranking` 同口径（当月 + 排除已撤销）；`total_points`=当月全来源之和、`late/absent` 只数点呼 `rollcall_late`/`rollcall_absent`。**扣分按当月算**（照系统已有约定 — ranking 就是按月聚合 + 阈值按月判，不是新拍板）。+4 测试。后端 217 passed。

**iOS 接线 — ✅ 2026-06-02 完成（commit `d21a2b8`）**：
- `AuthAPI.swift` 加 `DisciplineAPI.mySummary()` + `MyDisciplineSummaryOut` Decodable
- `AppStore.loadMe` 拉到 /me 后再拉 summary，填 currentUser 的 points/lateCount/absentCount（真人现显真实当月统计，不再全 0）
- iOS 双 scheme BUILD SUCCEEDED。**IX-008b 全做完（后端 + iOS）。**

### 4.1 Codex 阶段2(IX-004) 审查 — 已回，2 条已修（提交 `6cca9fc`），剩 5 条待处理（原文 `/tmp/codex_stage2_out.txt`）

**✅ 已修（`6cca9fc`）**：🔴 destination 写错字段（加载从 `stay_locations.first.name` 读、原提交写 `dest_cities` = 覆盖错位置 → 改发 `stay_locations` + 改了才发）；🟠 `isSubmitting` 没拦连点（加 `guard !isSubmitting`）。

**✅ 全部已修（提交 `5a8be64`，后端 pytest 196 passed + 新增 3 针对性测试 + iOS 双 scheme BUILD SUCCEEDED）**：
- 🔴 **amend_reason 修改理由丢失** → 后端 `schemas.py` ApplicationUpdateIn 加 `amend_reason` 字段、`applications.py` update_application 把它 pop 出来写进 audit payload（不覆盖申请 reason）、iOS `submitAsync` 发送、audit mapper `detailText` 优先显示 amend_reason 让履历看得到。
- 🔴 **后端改完没重置 `status=pending`** → `applications.py` 链重建块后加 `app.status = "pending"`。新测试 `test_update_resets_status_to_pending` 验证 approved_partial 改完回 pending。
- 🟠 **日期/方法无条件发 → 误拒** → `submitAsync` 改成跟 initFields 基准值比对、只发真改过的（leave_date != original.leaveDate 才发 等）。
- 🟠 **returned 能编辑但后端拒** → `applications.py:370` 允许列表加 `returned`。新测试 `test_update_returned_application_allowed` 验证不 409 + 回 pending。
- 🟡 audit 文案 → iOS mapper `translateAction` 加 `application.update` → "修改届を提出"。
- 💡 `ApplicationUpdateBody` nil=不发、无法表达「清空成 null」→ 仍是将来字段允许清空时要定的协议（本次未做，记着）。

> **Codex 阶段3 审查**（审 `5a8be64`）已回 → 又修 3 条真问题（提交 `0ee5546`，后端 pytest 199 + iOS 双绿）：
> - 🟠 无实质修改也重置审批链（空 body / 只填理由 / 传相同值）→ 改成只有真改了业务字段才重置链 + 重发邮件，否则 422 `NO_CHANGES`；出寮日校验也只校验真改了的。
> - 🟠 `GET /{id}/audit` 老师越权（任何老师读任意申请履历，payload 现含 amend_reason）→ 照抄详情端点 `_teacher_can_view` 按担当寮范围限制。
> - 🟡 amend_reason 纯空白绕过 → 后端 strip 规整、iOS 改 `.whitespacesAndNewlines`。
> - 测试从 3 个加到 6 个（加 no-op 422 / audit 越权 403 / 跨寮老师可读 200 + reason 不覆盖 / 链全 pending 断言）。
>
> **独立缺口（非本次 bug，记着）**：`returned`（老师退回）状态目前**没有真实业务路径产出** —— 老师审批端点 `decide_approval` 的 `_recompute_application_status` 只产出 rejected/approved/approved_partial/pending，没实装「老师退回让学生改」动作（spec §7.2.4-5 要求）。我加的「returned 可编辑」前向兼容、保留。**要做完整闭环需后端 + teacher_web 加「差戻 / 退回」决策**（独立功能，归 TODO）。
>
> **Codex 阶段4 收敛复审**（审 `0ee5546`）已回 → 🔴 无、又修 2 条（提交 `5b97b45`，pytest 201）：
> - 🟠 `changed` 比较 flight 等 datetime 字段：请求带时区、SQLite 读回丢时区 → 同一时刻误判成改了仍重置链。加 `_norm` 统一成 JST aware 再比（复用 rollcall `_as_jst_aware` 同款）。
> - 🟡 改了字段但没填修改理由 → 后端 422 `AMEND_REASON_REQUIRED`（iOS 已强制、后端兜底）。
> - 测试加到 18 个（+ 没填理由 422 / 传相同值 no-op 且已承认行不被清）。
>
> **Codex 阶段5 收敛确认**（审 `5b97b45`）已回：**「收敛 — 无新增严重/中问题，IX-004 修改届可关闭。」** 🔴🟠🟡💡 全无，复核 `_norm` 没误伤 date/time、422 位置合理、前几轮修复没回退。
>
> ✅✅ **IX-004 修改届接后端 — 关闭**（5 轮 Codex 对抗复审收敛；提交链 `40d9d59` → `5a8be64` → `0ee5546` → `5b97b45`；文档 `a49daf9`）。
>
> **测试基建偶发隐患**（记着、非本次 bug）：`tests/conftest.py` 用单个文件型 SQLite + 每测试清表，多连接并发偶尔清表失败、级联崩一批（全量有时假报 60+ errors，单文件重跑就过）。根治要换「每测试事务回滚」隔离。

### 4.2 B 类剩余（按此顺序接着接）
- **IX-007 详情页 `ApplyDetailView`**：stay/holiday/return/returncountry 走 `StayDetailView`（已接后端 ✅）；但 `otherDetailBody`（修繕/来訪/代理受取等）那支仍读 `SEED` + 编造步骤时间，未接。
- **IX-009 通知**：`AppStore.allNotifications` 拼 `SEED.notifications`（生产泄漏）。`AnnouncementsAPI`（公告）+ `front_desk`（包裹）后端已有，聚合做真通知源。
- **IX-034 请假计数**：`AppStore` 请假次数只在内存累加、不按月清零。后端 `study.py` 有 `/absence-requests`，可数当月。
- ✅✅ **IX-008 用户资料 — 全部完成**（身份 §4.0/§14.8 + 二审 5 修复 §4.0 + 扣分统计 IX-008b §4.0b + Batch 2 站点迁移）。详见 §4.0 / §4.0b。**低危残留**：3 个表单 `@State` 预填（StayForm contactPhone `ApplyStubs.swift:432` / FridgePurchaseForm contactPhone `DormLifeForms.swift:294` / ItemPossessionForm roomNo `DormLifeForms.swift:513`）—— 登录路径已真实、仅冷启动 sub 秒窗口旧；要彻底干净给 3 表单加 `.onAppear { 从 app.displayUser 填 }`（同 `MyInfoEditView.loadCurrentInfo` 做法）。MyPointsView 减点图表（router-only 视图）靠安全网 SEED.user。

### 4.2bis 还没接的（IX-008 外 — 下次主推这些）
- **IX-007 详情页 `ApplyDetailView` 的 `otherDetailBody`**（修繕/来訪/代理受取等）仍读 `SEED` + 编造步骤时间，未接后端。
- **IX-009 通知**：`AppStore.allNotifications` 拼 `SEED.notifications`（生产泄漏假数据）。后端 `AnnouncementsAPI`（公告）+ `front_desk`（包裹）已有，聚合成真通知源。
- **IX-034 请假计数**：`AppStore` 请假次数只在内存累加、不按月清零。后端 `study.py` 有 `/absence-requests`，可数当月。
- **Codex 阶段1 第4条（低）**：`APIClient.decodeISO8601Date` 只解析带时区 ISO8601，后端若返无时区日期会解码失败 —— 待真后端有日期数据时验证，真无时区就加 fallback formatter。
- **老师「退回(returned)」动作**（接续 #3）：后端 `_recompute_application_status` 产不出 `returned`，spec §7.2.4-5 的「差戻」没实装。**要 itsuki 先拍板设计**（后端 + teacher_web）。
- **学習対象 is_study_target 后端字段**（接续 #4）：跟并发会话的「晚自习 UI / tier」决策缠在一起，暂不动。
- **Codex 阶段1 第4条（低）**：`APIClient.decodeISO8601Date` 只解析带时区的 ISO8601，后端若返回无时区日期会解码失败。**待真后端有日期数据时验证**（公告列表对测试学生为空、当时没法证实）；真无时区就加无时区 fallback formatter。

### 4.3 复验
- 房间号修复后建议跑一遍注册：确认数字房号 `101`→发后端 `M101`、字母房号 `A5`→`A5`（不再 `MM101` / `MA5`）。

## 5. 关键参照
- **37 条审查全清单**：`05_logs/audit_2026-05-29_ios交叉验证.md`（IX-001~037，CC workflow 27 + codex 13 交叉验证）。
- **bug 追踪入口**：`00_admin/系统bug专栏.md` §🍎 iOS 交叉验证段。
- **B 类「假数据→真后端」分组 + 后端接口现状**（哪些接口已就绪）见本文件 §4.2。

## 6. 风险 / 注意
- **并发会话在改后端**（`announcements.py` / `discipline.py` / `study.py` 一直在变）。我只碰 iOS。提交前 `git status` 确认、精确 `git add` 我自己的文件、绝不 `git add -A`。
- iOS 改动会触发一堆 PostToolUse hook 提醒（project-overview 同步 / 联动 / 日语注释 / demo-scaffold）——多数非阻塞，按需处理。
- B 类只能编译验证 + itsuki 手动跑模拟器验证；真机端到端联调需后端在线（现已在线）。

---

## 7. 2026-06-02 过夜自动修复 GOAL（itsuki 睡觉 · 无人值守）

### 7.0 运行模式（itsuki 拍板）
- **绝不问 itsuki**。遇到必须他拍板的 → 跳过 + 记 §7.3 待决策清单 → 继续做下一件能做的。
- 每阶段做完更新本文件（防上下文被自动摘要后丢状态）。
- 灾难级不可逆操作（删库 / `git reset --hard` / `git push --force` / 任何 push）一律跳过留给 itsuki。本地 commit 可以。
- 每阶段：Codex 5.5 xhigh 审 → 逐条核实真实代码再修 → 双端编译 / pytest 验证 → 精确 `git add <文件>` commit（不 `-A`、不 push）。

### 7.1 ✅ IX-034 请假计数按月 — 代码已提交 `e0c150c`（待修 Codex 4 点）
**已做**：后端 `GET /api/v1/study/absence-requests/me/summary`（当月 target_date 全状态计数，schemas `MyAbsenceSummaryOut`）+ iOS `StudyAPI.myAbsenceSummary()` + `loadMe` 拉真实当月数 + 3 测试。后端 220 passed / iOS 双 scheme BUILD SUCCEEDED。
**口径决定（itsuki 自定）**：按 target_date 算当月 / 数全部状态（含 rejected，匹配「提交即 +1」）/ 不加硬上限。
**Codex 审出 4 点待修（下一步先做这个）**：
1. 🟠 `submitStudyLeave`（AppStore.swift:541）成功后无条件 `+=1`，但表单能选今天到 +14 天、可能跨到下月 → 5 月底提交 6 月的，iOS 把「本月」+1 但后端不计入。改：只有 targetDate 属于 JST 当月才 +1。
2. 🟠 `loadMe`（AppStore.swift:152/166）竞态 guard 只查 `isAuthenticated`、没确认同一令牌 → A 登出 B 立刻登录时旧任务可能把 A 数据写进 B。改：进 loadMe 捕获 `let tokenAtStart = authToken`，每次 await 后 / 写回前 `guard authToken == tokenAtStart`。
3. 🟡 `test_study.py` 用 `date.today()` 而端点用 `_now_jst()` → 非 JST 机器月末边界 flaky；缺 12 月跨年 + 精确边界。改：monkeypatch `study._now_jst` 固定到 2026-12-31 23:xx JST 补边界断言。
4. 🟡 `ApplyStubs.swift:1061 formatYMD` 没固定 Asia/Tokyo、用设备默认时区 → target_date 口径可能偏。改：给 DateFormatter 指定 JST（注意是共用 helper，影响多个表单，确认范围）。
- 💡（不修）：study.py:580 `len(rows)` 可换 `select(func.count())`，但要加 func import、收益低，跳过。
- Codex 原文：`/tmp/ix034_codex_out.txt`。

### 7.2 ✅ 今晚修完的（带 commit 哈希）

**IX-034 请假计数按月 — ✅✅ 关闭（7 commit + 6 轮 Codex 对抗复审，pass6 终判「IX-034 收敛可关闭」）**
- `e0c150c` 主体（端点 `GET /absence-requests/me/summary` + iOS loadMe 拉真实当月数 + 3 测试）
- `7a9922c` 修 Codex 第 1 轮 4 点：① submitStudyLeave 只在 targetDate 属 JST 当月才 +1（跨月提交不再误加本月）② loadMe 捕获 tokenAtStart 每 await 后比对令牌 ③ test_study monkeypatch `study._now_jst` 固定日期去 flaky + 新增 12 月跨年边界测试 ④ ApplyStubs `formatYMD`/`parseYMD` 成对固定 Asia/Tokyo
- `7fecd21` 修 Codex 第 2 轮 3 点：① loadMe 的 catch 401 也比对令牌（A 旧请求迟到的 401 不误清 B 令牌）② StayList 编辑流程自有的 `parseYMD`/`formatYMD` 也固定 JST（上轮只改了 StayForm 新建那对、漏了编辑那对）③ 加 `absenceCountRevision` 代次守卫（在途旧 loadMe summary 不再覆盖刚提交请假的乐观 +1）
- `508c9b1` 修 Codex 第 2 轮 2 点：① submitStudyLeave 乐观 +1 后再拉 canonical 当月数收敛（token+代次双守卫）防启动 local=0 只 +1 偏低 ② StayList 编辑页两个 DatePicker 加 JST 时区环境 + formatYMDJa 固定 JST
- `2dff6b7` 修 Codex 第 3 轮 1 点：submitStudyLeave 进入即捕获 tokenAtStart、提交 await 后 guard，防提交在途登出/切用户写错状态（同 commit 含 IX-009 收敛）
- `6c58799` 修 Codex 第 4 轮 1 点：submitStudyLeave canonical await 后 + toast 前抛 CancellationError、调用方静默捕获（防第二个 await 期间登出把完成提示写别人 UI）
- `30032ea` 修 Codex 第 5 轮 1 点：submitStudyLeave 第一道 guard（submit await 后）也抛 CancellationError（async throws 里普通 return = 调用方视为成功仍导航完成页）
- **Codex pass6 终判「IX-034 收敛可关闭」**：所有跨 await 状态写入 + 完成页导航点全被令牌守卫覆盖
- 验证：后端 221 passed / iOS 双 scheme BUILD SUCCEEDED
- 待补：IOS_DESIGN_LOG §14.10 一行；`StudyOnlineForm.swift` 的 `ApplyFormDate.formatYMD`（オンライン自習表单 period_from/to）同款没固定 JST 的隐患（另一 helper / 另一表单，记着）

**IX-009 通知不泄漏假数据 — ✅✅ 关闭（3 commit，Codex pass5 终判「IX-009 收敛可关闭」）**
- `7e4a180` SEED.notifications 声明圈进 `#if DEMO`（5 条假通知物理上不进生产二进制）+ `allNotifications` 分构建（演示用 SEED fixture / 生产 = push + `announcementNotifications` 真公告映射、未読=公告未読驱动铃铛 badge）+ 新增 `announcementNotifications`/`notifTimeLabel`(JST)/`refreshNotificationSources` + `NotificationsView .task` 进入拉真公告
- `2dff6b7` 修 Codex 2 个 🟠：① badge 首屏不准 → 生产 `unreadNotificationCount` 用 `push 未読 + announcementUnreadCount`，loadMe 登录/启动即拉公告未読数 ② `loadAnnouncementList`/`loadAnnouncementUnreadCount` 加令牌守卫，登出/切用户不写回旧用户公告
- `6c58799` 补全公告 4 方法令牌守卫：`loadAnnouncementDetail` / `postAnnouncementReply` 也加 token-at-entry 守卫（详情缓存 / 列表已读 / 回复缓存不串号）
- 推迟（§7.3）：审批结果 / 包裹通知聚合 + 通知 id 下标身份 + push/公告时间排序

**IX-007 申请详情页生产不读 SEED — ✅（Option A）**
- `457077f` `ApplyDetailView.body` 分构建：生产显式只 `StayDetailView(id)`（后端只支持出寮届系），演示保留 SEED 路由讲叙事。修掉「item 落 SEED.applications[0] 巧合 + otherDetailBody 读 SEED」的脆弱/潜伏泄漏。iOS 双绿。
- Option B（真做修繕/来訪/代理受取功能）→ 推迟（§7.3）

**5-30 审查 🟡 批（Stage 4）— 部分做完，多数推迟**
- ✅ `13f5a01` iOS 4 个安全生产 bug：ios-home-05（首页日期写死 4/22→JST 今天 `homeGreetingDateLabel`）/ ios-home-10（公告回复失败静默→toast）/ iosmypage-11（「快递」→「荷物」）/ ios-staylist-05（audit 拉失败静默→toast）。iosmypage-12（删号跳登录）查证已被 IX-002 修。
- ✅ `797d16f` 文档 sysfeat-05（category ENUM→TEXT 对齐后端现实）/ sysfeat-06（flow_design 时间窗加注是 session 动态非 hardcode）。sysfeat-10（19:30→19:40）查证已对齐。
- ✅ migtest-05/06/07/10 查证前序会话已修（代码注释直接引用 migtest-ID，只是 TODO 复选框没勾）。
- ⏸ 后端 migration 批 + 其余 demo 耦合/潜伏 iOS bug → §7.3。

### 7.3 ⏸️ 待 itsuki 决策清单（跳过的，醒来一次性看）
- **IX-007 其它类申请（修繕/来訪/代理受取）v1.0 上不上线**：后端零实装。今晚已按 Option A 做完（生产不读 SEED、`457077f`）。**Option B = 真做这功能**（后端建表 + 5 端联动）仍待你拍板上不上线；不做的话生产就是「这几类申请提交不了 / 不存在」，需求侧确认。
- **IX-009 通知 — 已接公告，3 项推迟**：
  - **通知卡 id 用 `-(idx+1)` 下标身份**：公告插入/重排时同一公告会换 id、SwiftUI 卡片身份跳（轻微视觉）。彻底修要把 `NotificationItem.id` 从 Int 改成 String（`announcement-<uuid>` / `push-N` / `seed-N`）—— touch push id 生成 + SEED + 整个通知子系统，单列。
  - **push + 公告按来源拼接、非时间全局排序**：真 push 接通后旧 push 会永远压在新公告上方。要给 NotificationItem 加 createdAt + sourceKind 统一时间倒序（push 未持久前影响有限）。
  - **审批结果 + 包裹通知聚合**（今晚只接了真公告，这两个源推迟）：
  - **审批结果当通知**：申请列表（`/applications/mine`）没在 AppStore 缓存（各视图按需拉），且后端对「你的申请被批了」无已读/未读状态，且 `/applications/mine` 返回全部历史（把每条历史审批当常驻通知卡语义不对）—— 要做需先给 AppStore 加申请缓存 + 定通知语义（哪些状态算 / 已读态本地存还是后端加 / 去重），属产品决策。
  - **包裹通知**：要后端新建 `GET /front-desk/mine`（学生端查自己包裹）。后端零实装。
  - 通知中心的 type 过滤标签里「申請」「宅配」标签生产暂时为空（诚实 — 还没真数据源），公告走「すべて」标签显示。
- **5-30 审查后端 migration 批（全推迟 — 改 DB 约束有风险 / 多 PostgreSQL 专属 SQLite 测不了 / 多 schema 设计决策，过夜不盲改 schema）**：
  - rollcall-05（点呼幂等并发双写 → 要 PG 部分唯一索引 `(session_id, student_id) WHERE idempotency_key IS NULL`，SQLite 测试库验不了）
  - models-entry-06（RollCallEvent.base_status CHECK 含 'init' 但从不写入 → 收紧 CHECK = migration）
  - models-entry-08（Application.receipt_submitted/is_long_vacation nullable=True+default=False 三态混乱 → nullable=False 需 backfill + 查无代码依赖 null）
  - models-entry-10（StudentRegistrationCode 缺「同时只一个有效码」DB 保证 → PG 部分唯一索引）
  - models-entry-12（扣分用 Float → 4/8 分阈值边界可能误判；实测典型分值是 2 的幂分数 float 精确、换 Numeric 要定精度）
  - models-entry-05（AnnouncementReply.author_id 跨表无外键 → 是多态引用、加单一 FK 不成立，架构题）
  - models-entry-07（AuditLog append-only 无 ORM/DB 强制 → 要 PG 触发器或 SQLAlchemy event 阻止 UPDATE/DELETE，机制选型）
  - models-entry-11（create_all 只 dev 调、staging 启动即失败 → ops，staging 还没起）/ models-entry-13（Student.is_demo 靠每处查询主动过滤 → 要审计所有列表/统计端点，策略题）
  - migtest-08（历史迁移硬编码 999999 痕迹 → 不改历史迁移）/ migtest-09（applications.bus_route_id 悬空外键 = 半成品巴士功能）/ migtest-01（测试不跑 alembic = 测试基建改、有破坏全套风险）/ migtest-04（审批链补测 = 新写测试、量大）
- **5-30 审查其余 iOS bug（demo 耦合 / 潜伏 / 要接后端，留 TODO §🟡）**：ios-community-04/06/07/08/09/11/12（掲示板 SEED 耦合演示数据 + 数组下标当 id 潜伏，且掲示板上不上线本身待定）/ ios-home-07（兜底 21:02 罕触发）/08（联系人写死田中先生内線101 — 该从后端/配置来、产品题）/ iosmypage-07/08/09（月度统计/详情/总分 SEED 假数据 — 接后端 territory）/ ios-schedule-04（firstIndex??0 潜伏，events 接后端才暴露）/ ios-staylist-06（mock chain 未登录预览）/07（actor_type 粗暴 — 接后端真履历）/ ios-auth-09（splash 只验 token 存在）。多数是「功能上不上线 + 接没接后端」决策，不是无脑安全修。
- **Stage 5 ⚪ 未核实（iosmypage-01~12 + ios-schedule）**：5-30 workflow 子代理没返回；本次抽查 iosmypage-07/08/09/11/12 已分类（11/12 处理、07/08/09 接后端推迟），其余下次补核实。
- **老师「退回(returned)」动作** / **学習対象 is_study_target 后端字段** / **5-30 审查 🔵 段** / **spec 冻结区文档** / **版本号 bump** / **系统bug专栏 131 条 🟡 段（安全硬化/spec 文档/大工程，多要拍板）**：全跳过。
- （后续每跳过一条往这里加）

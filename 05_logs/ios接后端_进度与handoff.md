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

**剩余（Batch 2 — 这次审查发现但本阶段未做，下次接）**：
- 🟡 其余身份展示站点仍直读 SEED.user（MyPage profileSection 头像/姓名/账号/寮房 153-170、减点卡 294、summaryCard 学習対象 1970、StayList ID 卡 1324-1329、Apply me* 402-428、DormLifeForms @State 294/513）→ 统一迁 `app.displayUser`，废掉「写回全局 SEED.user」安全网
- 🟡 登出只清 SEED.user，没清 changeLog/announcements 等用户绑定 @Published → 抽 `resetUserState()`（跨账号隐私残留）
- 审查全文：Codex `/tmp/ix008_codex_out.txt`、Claude workflow 结果在 task `wsl80p7iw` 输出

### 4.0b 🔧 IX-008b 扣分统计 — 后端完成、iOS 接线待（2026-06-02）

**起因**：iOS `displayUser` 的 points/lateCount/absentCount（扣分/迟到/欠席）真人现显 0（`/me` 没这些字段）。

**已做（后端，commit `0f84be9`）**：新 `GET /api/v1/discipline/me/summary`（学生鉴权）= 当前学生**当月**扣分汇总 `{month, total_points, late_count, absent_count}`。与 `/ranking` 同口径（当月 + 排除已撤销）；`total_points`=当月全来源之和、`late/absent` 只数点呼 `rollcall_late`/`rollcall_absent`。**扣分按当月算**（照系统已有约定 — ranking 就是按月聚合 + 阈值按月判，不是新拍板）。+4 测试。后端 217 passed。

**待做（iOS，等 iOS 文件腾出再接）**：
- `AuthAPI.swift` 加 `DisciplineAPI.mySummary()`（GET /discipline/me/summary）+ `MyDisciplineSummaryOut` Decodable
- `AppStore.loadMe` 拉到基本资料后再拉一次 summary，把 points/lateCount/absentCount 填进 currentUser（现在 mapMeToUser 填 0）
- 注意：iOS User.points 是 Double、后端 total_points 是 float，对得上

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
- **IX-008 用户资料（最大一块，要先动后端）**：**实测 73 处** `SEED.user`（不是之前估的 25）散在 **7 文件**：`HomeStubs / MyPageStubs / ApplyStubs / DormLifeForms / AuthStubs / StayListStubs / AppStore`。**后端缺口**：登录只返回 `TokenOut`（无用户信息）、无学生 `/me` 接口（`student_profile.py` 只有 `GET /students/{id}/profile` 需 id）。**模板已确认**：老师端 `teachers.py:182` 有 `GET /teachers/me`（`get_current_teacher` 依赖取令牌 → `TeacherOut`），照仿。需：① 后端加 `GET /students/me`（仿老师端 + 新 `StudentMeOut` schema）；② iOS `AppStore` 存 `currentUser` + 登录/启动时拉一次；③ 73 处 `SEED.user` 改读 `currentUser`（演示 `#if DEMO` 留 SEED）。第 ③ 步 73 处适合 **workflow 并行铺**（按 7 文件分代理）。登录令牌 JWT 已带 student id + name + dorm_unit + is_overseas。
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

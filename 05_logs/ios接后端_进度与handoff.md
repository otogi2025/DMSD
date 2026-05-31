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

### 4.1 立刻要做（压缩后第一件事）
- **读 Codex 阶段2（IX-004）审查结果**：后台任务 `bq4miqzsp`，输出 `/tmp/codex_stage2_out.txt`。过 findings、修真问题、再提交。

### 4.2 B 类剩余（按此顺序接着接）
- **IX-007 详情页 `ApplyDetailView`**：stay/holiday/return/returncountry 走 `StayDetailView`（已接后端 ✅）；但 `otherDetailBody`（修繕/来訪/代理受取等）那支仍读 `SEED` + 编造步骤时间，未接。
- **IX-009 通知**：`AppStore.allNotifications` 拼 `SEED.notifications`（生产泄漏）。`AnnouncementsAPI`（公告）+ `front_desk`（包裹）后端已有，聚合做真通知源。
- **IX-034 请假计数**：`AppStore` 请假次数只在内存累加、不按月清零。后端 `study.py` 有 `/absence-requests`，可数当月。
- **IX-008 用户资料（最大一块，要先动后端）**：25 处 `SEED.user`（Home/MyPage/Apply/DormLifeForms）显示假用户。**后端缺口**：登录只返回 `TokenOut`（无用户信息）、无学生 `/me` 接口（`student_profile.py` 只有 `GET /students/{id}/profile` 需 id；老师端有 `GET /me` 可仿）。需：① 后端加 `GET /students/me`（仿老师端，从令牌取学生）；② iOS `AppStore` 存 `currentUser`；③ 25 处 `SEED.user` 改读 `currentUser`（演示 `#if DEMO` 留 SEED）。登录令牌 JWT 里已带 student id + name + dorm_unit + is_overseas（可临时用）。
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

# itsuki 2026-05-31 决策批 — 自审清单（Codex 用量耗尽，CC 自审替代）

> **背景**：Codex（每阶段代码审查工具）用量到上限（约今晚 23:57 恢复）。itsuki 拍板：能做的全做、Codex 用不了就别等、把要审的写成清单 CC 自己过一遍。
> **待办**：Codex 额度恢复后，对本批 commit（`ef1c910` + 文档批）补跑一轮终审确认收敛。
> **全量 pytest**：213 passed（清库后 `cd 03_dev/backend/v1 && rm -f test_tomoshibi.db* && .venv/bin/python -m pytest -q`）。

---

## 1. 扣分值 + 改判重算（rollcall.py，commit ef1c910）

| 审查点 | 自审结论 |
|---|---|
| 迟到/缺席分值改 0.5/1.0 是否对 | ✅ 对齐 system_features §862 冻结值（2026-04-30 itsuki 拍板）。旧 1.0/2.0 是 drift。规格本来就是 0.5/1。 |
| `_apply_override_demerit` 重算逻辑对不对 | ✅ 撤本场该生所有未撤销 rollcall_late/absent + 按 to_status 重记一条。逐转移核对：present→late=0.5、present→absent=1.0、absent→late（撤 1.0 记 0.5=0.5）、late→present（撤 0.5 记 0=0）、→exempt_range（不在表=0）全对。 |
| 多步改判 bug 修没修 | ✅ present→absent→late 现在 = 0.5（旧实现负 delta 全撤 = 0，少扣）。回归测试 `test_multistep_override_recomputes_demerit` 锁死。 |
| 会不会误伤别的扣分 | ✅ 只撤 rollcall_late/rollcall_absent；cleaning_failed / manual / study 扣分不碰。 |
| 删了 _OVERRIDE_DEMERIT_MAP 有没有残留引用 | ✅ grep 0 残留（384/803 注释已改）。 |
| ruff 删 import / 语法 | ✅ 没加新 import；9 模块 import 成功；213 passed。 |

## 2. 密码下限 6→8（schemas.py，commit ef1c910）

| 审查点 | 自审结论 |
|---|---|
| 改对地方了吗 | ✅ 只改「设密码」两处：TeacherRegisterIn（老师注册）、StudentAccountCreateIn（学生建号）。TeacherCreateIn 本来就 8。 |
| 登录处为什么不改 | ✅ StudentLoginIn / TeacherLoginIn 不动 —— 登录只是去验密码、不该卡长度。改了会把 `test_security_fixes` 的「wrong!!」(7 位错误密码) 挡成 422、破坏锁定测试。 |
| 有没有漏的密码路径 | ✅ 密码重置 `POST /accounts/{id}/password-reset` 服务端生成 16 位临时密码（已 ≥8，无需改）。全仓 4 处密码字段已覆盖。 |

## 3. 注册码 TTL 30 + 手动关闭（admin_registration_code.py，commit ef1c910）

| 审查点 | 自审结论 |
|---|---|
| TTL 5→30 | ✅ `REGISTRATION_CODE_TTL_MINUTES = 30`。测试断言同步改 30*60。 |
| close 端点对不对 | ✅ 作废现存 active 非审核员码 + 写 audit + 幂等（无 active 也安全）+ 审核员永久码不动。返回 204。 |
| 「一次性」需求 | ✅ 拒绝（itsuki 拍板）。规格 §7.16.2 规则 5 本来就写「コード再利用可」，跟 finding 矛盾，finding 错。 |
| 测试 | ✅ `test_close_invalidates_current`（关闭后 current=null）+ `test_close_requires_admin_role`（学生 403）。 |

## 4. 晚自习 3 次签到→2 次（规格 + 文档，文档批）

| 审查点 | 自审结论 |
|---|---|
| 规格改对 | ✅ §7.3.3 tap 列表 3→2（删中场）+ §7.3.4 異常描述去中场 + 特征矩阵「碰 2 次」。 |
| 后端要不要改 | ✅ 后端 create_checkin 是「每天一条签到」，没有三次（开始/中场/结束）逻辑——3→2 纯规格 + 前端事，后端无改。 |
| iOS/Android 前端 | ⏳ 待做（StudyCheckinSheet「3 回タップ」UI + recordStudyTap）。**并发会话正在改 iOS，避让，未动。** |

## 5. 文档同步（文档批）

| 审查点 | 自审结论 |
|---|---|
| 注册码 30/close 同步进规格 | ✅ §7.16.2 规则 4 + line 184 + API 矩阵 307。 |
| 扣分 + 注册码记设计日志 | ✅ BACKEND_DESIGN_LOG 进度表加 3 行。 |
| 真名/学号错注释 | ✅ teacher_web index.html 两处「itsuki 本人/060218 itsuki 本人」改成「架空サンプル、実在の学籍番号ではない」。 |

## 6. 还没做 / 待确认（留给 itsuki + 后续）

- **tier 等级**：未动。itsuki 没给具体数值。自审发现 tier 实为「月累计 ≥4 罚扫 / ≥8 禁足」的阈值（§862），不是单条事件标签——「迟到/缺席不同 tier」需 itsuki 定具体含义。**等 itsuki。**
- **IOS_DESIGN_LOG.md:199**「itsuki 本人」错注释：iOS 会话territory，避让未改。
- **晚自习 2 次签到 iOS/Android UI**：并发会话territory，待做。
- **Codex 终审**：额度恢复后补一轮。

---

## 7. itsuki「都坐好」批（iOS 晚自习 2 次签到 + tier 月累计 + 注释，commit a3eceda）

| 审查点 | 自审结论 |
|---|---|
| iOS 晚自习 3→2 删 .mid 后能编译 | ✅ **xcodebuild BUILD SUCCEEDED**。StudyTap 枚举删 .mid + 6 个 switch（stepLabel/stepNumber/timeWindow/successTitle/nextTapAfterRecord/短标签 extension）去 .mid 分支 + stepNumber end 3→2 + 进度点去中场 + demoSeed 删 2 条 mid。 |
| iOS 出席状态判定逻辑 | ✅ start+end→绿 / 只 start→进行中 / 只 end→异常 / done 且 0 tap→缺席。覆盖全。 |
| iOS UI 文本 3→2 | ✅ 「/ 2 回目」「全 2 回 タップ済み」「1 日 2 回タップ」+ MyPage 说明删中场。 |
| Android tier 重算 | ✅ 按 §862 月累计：本月 0.5→...→4.5，前 5 条 <4 = 0、第 6-7 条 ≥4 = 4。tier 当前 Android UI **未被读取**（grep 0 处使用），纯 mock 数据改为自洽。⚠️ 本机无 SDK 不能 gradle 编译，未真编译验证（风险低：只改 Int 字面量 + 注释、无结构改动）。 |
| Android 晚自习 2 次 UI | ✅ 无需改 —— Android **未实装**晚自习签到 UI（grep 0 命中 study-tap；ScheduleScreen 的「中間試験」是期中考、无关）。 |
| 注释错改对 | ✅ IOS_DESIGN_LOG「リュウ イヒ（itsuki 本人）」→「demo seed 本体、架空サンプル」。 |

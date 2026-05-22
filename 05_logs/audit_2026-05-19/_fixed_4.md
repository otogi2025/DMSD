# Fix-Bot 4 修复报告 — effective_* 彻底删除

生成于：2026-05-21（itsuki 拍板 b1 现在删 — 推翻 Fix-Bot 2 的 (a) 保留补丁方案）

---

## 背景

- itsuki 真实意图（5-21 拍板）：点呼时间永远固定 / 迟到永远按 `scheduled_*` 算 / 老师提前按按钮只是附加功能不改窗口。
- `effective_*` 字段族（窗口平移概念）跟 itsuki 意图完全不符。
- Fix-Bot 2 之前选 (a) 保留只是技术债 — 这次彻底删干净。

---

## grep 扫描总览

仅统计「窗口平移类」字段（`effective_window_start_at` / `effective_on_time_end_at` / `effective_late_end_at` / `effective_auto_end_at` / `effective_group` / `applied_group`）。

**完全不动**：
- `class_teacher_assignment.effective_from` / `effective_to`（教师任期日期 — 跟窗口平移无关）
- `announcements.effective_from` / `effective_until`（公告生效日期 — 跟窗口平移无关）

### 实际引用分布（清理前）

| 端 | 文件 | 引用数 | 性质 |
|---|---|---|---|
| backend code | `app/models.py` | 1 | `applied_group` 字段定义 |
| backend code | `BACKEND_DESIGN_LOG.md` | 2 | SQL DDL + 注释 |
| backend migration | `7a15771bdc7b_add_study_rollcall_teacher_tables.py` | 1 | 历史 migration（不动，新 migration 来抹）|
| spec 主体 | `RollCall_Spec.md` | 14 | §3.3 / §5.5 / §6.4 / §6.5 / §7 / §8 / §10 / §13 / §15 / 历史段 |
| spec 字典 | `FIELD_REGISTRY.md` | 5 | §2.3（4 effective_*）+ §2.4（applied_group）|
| spec 字典 | `ENUM_REGISTRY.md` | 1 | session_event_source 注释 |
| spec 规约 | `API_CONVENTIONS.md` | 4 | §5 / §6 / §7 全用 effective_*  |
| 客户端（iOS / Android / Web / 点呼机） | — | **0** | 客户端未实装该字段 |
| flow_design / system_features / 5 端 DESIGN_LOG | — | **0** | 未引用 |
| backend schemas / routers / services / tests | — | **0** | 未实装 |

**总引用数：28 处**（清理前）。**清理后所有 active code 零引用**，剩下的是新 migration / regression test / 字典「字段已删除」注释。

---

## 已修

### 数据库层

| 文件 | 改动 |
|---|---|
| `03_dev/backend/v1/app/models.py` | 删 `RollCallEvent.applied_group` 字段定义，加 b1 决策注释 |
| `03_dev/backend/v1/alembic/versions/b9c0d1e2f3a4_remove_applied_group.py` | **新建迁移**（down_revision = `a8b9c0d1e2f3`），`upgrade()` 删列 / `downgrade()` 加回 nullable 列 — 完全可逆 |

### Backend code

| 文件 | 改动 |
|---|---|
| `03_dev/backend/BACKEND_DESIGN_LOG.md` | DDL 段删 `applied_group` 列定义；session 创建说明改「分组直接走 student `student_group`」 |
| `03_dev/backend/v1/app/schemas.py` | 零改动（schemas 从未引用 applied_group / effective_*）|
| `03_dev/backend/v1/app/routers/rollcall.py` | 零改动（routers 从未引用）|
| `03_dev/backend/v1/app/services/` | 零改动（未引用）|

### Spec / 字典

| 文件 | 改动 |
|---|---|
| `01_specs/rollcall/RollCall_Spec.md` | §3.3 `applied_group` → `student_group`；§5.5 自动结束注释；§6.4 改名 `effective_group` → `student_group`；§6.5 查表三元组用 `student_group`；§7 重写判定条件全用 `scheduled_*`，加 b1 决策注；§7 边界 `t > scheduled_late_end_at`；§7 配置缺失用 `student_group`；§8 `settle_at` 公式用 `scheduled_auto_end_at`；§10.1 删 effective_* 行 + settle 公式改 scheduled_*；§10.2 删 `applied_group` 字段；§10.4 改述「判定/结算/查表全用 scheduled_*」；§13 历史段加 b1 拍板注；§15 时间窗表查找用 `student_group` |
| `01_specs/rollcall/FIELD_REGISTRY.md` | §2.3 删 4 个 `effective_*_at` 字段；§2.4 删 `applied_group` 项；两处加「2026-05-21 b1 删除」备注 |
| `01_specs/rollcall/ENUM_REGISTRY.md` | §8 注释 `effective_auto_end_at` → `scheduled_auto_end_at`，顺便修 `scheduled_window_start` → `scheduled_window_start_at` |
| `01_specs/API_CONVENTIONS.md` | §5「scheduled 与 effective 规则」整段重写为「时间窗规则（窗口永远固定）」；§6 倒计时公式改用 `scheduled_late_end_at`；§7 settle 公式改用 `scheduled_auto_end_at` |

### 客户端

| 端 | 改动 |
|---|---|
| iOS `NetworkModels.swift` | 零（未引用） |
| Android `data/` | 零（未引用） |
| teacher_web `src/api/client.ts` | 零（未引用 — 注：另有 `effective_from/effective_until` 是公告生效日期，不在本任务范围）|
| rollcall_device `src/` | 零（未引用） |

### 测试

| 文件 | 改动 |
|---|---|
| `03_dev/backend/v1/tests/test_rollcall.py` | 加 `TestNoEffectiveWindowShift` regression class（2 tests）：①`test_rollcall_event_has_no_applied_group_column` — ORM model 不能再有该字段；②`test_rollcall_session_uses_scheduled_only` — 不能再加 effective_*_at，scheduled_*_at 4 字段必须存在 |

### 备份

`99_archive/2026-05-21_pre_fix/effective_removal/` 内：`RollCall_Spec.md.bak` / `FIELD_REGISTRY.md.bak` / `ENUM_REGISTRY.md.bak` / `API_CONVENTIONS.md.bak` / `models.py.bak` / `BACKEND_DESIGN_LOG.md.bak` / `7a15771bdc7b.py.bak` 共 7 文件。

---

## 待 itsuki 拍板（unfix）

| ID | 项 | 理由 |
|---|---|---|
| U-1 | `_legacy/pages-records-search-etc.jsx` 内 `effective_from/until`（公告生效日期）保留 | 不在本任务范围（任务定义的是窗口平移类 `effective_*`，公告生效日期是不同语义）— 但跨任务交叉确认建议下次审查 |
| U-2 | 历史 migration `7a15771bdc7b` 内 `sa.Column('applied_group', ...)` 保留 | alembic 铁律：已 applied 的 migration 不能改 — 新 migration `b9c0d1e2f3a4` 来抹掉它建的列，是正确 pattern |
| U-3 | project-overview SKILL.md 同步 | hook 多次提醒，但本任务硬约束不在范围内 — 留给 itsuki 收尾 / Bot 7 处理 |

---

## 关键问题 3 条

1. **`applied_group` 实际从未承载真实业务区分** — itsuki b1 决策意味着「学生分组永远 = student 当前 group」，故 event 层冗余存这个字段从来就没必要。删字段不丢任何有意义的历史信息（downgrade 时只能恢复 NULL，跟 b1 语义自洽）。

2. **4 个 `effective_*_at` 字段 spec 写了但 backend 从没实装** — `RollCallSession` ORM 一开始就只用 `scheduled_*_at`。本任务实际「物理删」的列只有 1 个（`applied_group`），其他都是 spec 层「概念删」。这反过来说明 Fix-Bot 2 当初选 (a) 保留时，技术债其实只有 spec 文档 + 1 个 DB 列 — 删干净比保留更省事。

3. **历史 migration 不能改 — 这是 alembic 设计意图** — `7a15771bdc7b` 里 applied_group 列定义保留没问题，因为 alembic 用 revision 链回放：新 migration `b9c0d1e2f3a4` 在它之后跑，物理 schema 最终是「无 applied_group」状态。如果以后部署到全新 DB，alembic 会按链跑：建 applied_group → 删 applied_group → 终态正确。

---

## 验证

- **Python 语法检查（ast.parse）**：models.py / b9c0d1e2f3a4_remove_applied_group.py / test_rollcall.py 全过 ✅
- **regression test pytest**：`TestNoEffectiveWindowShift::test_rollcall_event_has_no_applied_group_column PASSED` + `test_rollcall_session_uses_scheduled_only PASSED` ✅
- **全 test_rollcall.py 跑**：4 passed / 6 errors — 6 个 error 全是预先存在的 `target_date` fixture bug（跟本任务无关，是别的 Bot 改 ORM 时 fixture 没跟上）
- **iOS 编译过吗？**：未跑（任务无 iOS 客户端改动 — 客户端零引用，没必要跑）
- **alembic 链验证**：head = `b9c0d1e2f3a4`，down_revision = `a8b9c0d1e2f3`，链完整可回滚 ✅
- **全 repo 残留 grep**：active code（非注释 / 非 regression / 非「已删除」备注）零 `effective_*` 窗口平移引用 ✅

---

## 跨端字段对齐

清理后所有客户端跟 backend 都只用 `scheduled_window_start_at` / `scheduled_on_time_end_at` / `scheduled_late_end_at` / `scheduled_auto_end_at`，未引入新字段，未删除已对齐字段，跨端零破坏。

## 不动清单（按任务硬约束 6）

- `05_logs/audit_2026-05-19/` — 不动（本任务报告 `_fixed_4.md` 除外）
- `00_admin/系统bug专栏.md` — 不动
- `_master_issues.md` — 不动
- 其他 Bot 改过的不相关代码 — 不动
- `.claude/skills/project-overview/SKILL.md` — 不动（任务范围外，hook 多次提醒已记录到 U-3）

完成。

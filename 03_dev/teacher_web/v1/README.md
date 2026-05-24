# 03_dev/teacher_web/v1/

**老师 Web v1.0 正式版 — 实装中**（2026-05-22 校准 — Codex FC-030）。

## 当前进度

> **2026-05-02 起 v0.8 — 5 端代码层全启动后正式开工**

- ✅ **技术栈**：Vite + TypeScript + Zustand + React 18
- ✅ **API client**：`src/api/client.ts` — 接真 backend，含 auth / applications / announcements / teachers / students / rollcall 6 大模块
- ✅ **多 page 实装**：Login / Teachers / Applications / 学習管理 / Schedule 等
- ✅ **demo 接真后端**（5-03 起）
- ✅ **共用 design system**（Ryō / Cobalt / Noto Sans JP）从 demo 继承
- 🔄 **进行中**：5 角色权限分流 / 1·2 寮 vs 4 寮分别显示 / 邮件通知 / 事务室 PC 打印
- ⚠️ **仍是 demo 包**：`v1/src/index.html` 7700+ 行老 demo（含 SHARED_PASSWORD `12345678` 明文 — Codex FC-024/A-039 待清理）

## 设计权威

- 共用规则：`02_design/system_features.md`
- Web 専属设计：`../WEB_DESIGN_LOG.md`
- API 字段对齐：`01_specs/rollcall/FIELD_REGISTRY.md` + `backend/v1/app/schemas.py`

## 历史 — 4-30 立项条件

> 以下条件 4-30 立项时定的，现在状态见上：

- [x] `02_design/system_features.md` 重写（4-30 完成 357→830 行）
- [x] `RollCall_Spec.md` 5 处修订（4-29 完成）
- [ ] 「点呼総結」中层页设计（详见 `RollCall_Spec.md §5.6`）
- [ ] 共用功能完整：出寮届承认 / 行事予定編集 / 寮生特别运航便录入 / 学生数据查看 / 事案录入 / 指导履歴

## 已知问题（Codex 第二轮 audit）

详见 `00_admin/系统bug专栏.md §🤖 Codex 段`：
- [FC-024] 🔴 `v1/src/index.html` 仍有明文密码 + 学生模拟数据（需清理或归档）
- [FC-025] 🟡 `StayLocation` 字段形状跟后端不一致（`{date, location, contact}` vs `{kind, name, address, phone}`）
- [FC-026] 🟡 `StudyAbsenceRequestOut` 缺 `period` 字段
- [FC-027] 🟡 老师公告 client 跟后端权限不一致 + 无页面使用
- [FC-028] 🟡 老师邀请码权限前后端角色不一致（Web 3 角色 / 后端 4 角色含 学習担当）
- [FC-029] 🟡 `package.json` 没 test 脚本（当前只有 build 验证）

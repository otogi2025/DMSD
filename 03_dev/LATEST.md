# Tomoshibi HTML プロトタイプ — 歴史归档索引

> **2026-04-23 建立 / 2026-05-22 重写（Codex FC-037）** — 本文件原来是「最新 HTML 位置速查」。但 5-06 之后 5 端进入真代码层（iOS Swift / Android Compose / Web Vite+TS / Backend FastAPI / 点呼机 Pi Python），HTML プロトタイプ阶段已结束。
>
> ⚠️ **不要按本文件路径启 demo** — 路径已废，demo 全部归档。本文件只作历史追溯用。

---

## 🔴 当前状态（2026-05-22）

| 端 | 当前位置 | demo 归档位置 |
|---|---|---|
| 老师 Web | `03_dev/teacher_web/v1/src/index.html`（Ryō standalone HTML，5-26 起 Vite + TS 实装版整体废弃 + 5-27 凌晨接 backend client.js helper）| 5-21 demo 158 文件 → `99_archive/2026-05-21_teacher_web_demo_archived/`；5-26 Vite 实装 13 文件 → `99_archive/2026-05-26_teacher_web_vite实装作废/`|
| 学生 iOS | `03_dev/student_ios/v1/`（Swift + SwiftUI 真代码）| `03_dev/student_ios/demo/` 仍在原位（HTML プロトタイプ）|
| iOS App Store fork | — | `99_archive/2026-05-22_tomoshibi_appstore_fork/`（5-08 上架冲刺 fork，5-22 backport 后归档）|

---

## 历史路径（5-06 之前的开发模式）

> ⚠️ **以下路径全部已废 / 已归档**。仅作历史参考。

### 老师 Web（HTML プロトタイプ阶段，2026-04-22 ~ 2026-05-06）

- demo 起動：`cd 03_dev/teacher_web/demo && ./tomoshibi` → 现已归档
- 単一 HTML：`03_dev/teacher_web/demo/Tomoshibi_v3_single.html` → 现已归档
- 編集版：`demo/src/index.html`（双击 Safari 看 UI）→ 现已归档
- 設計 LOG：`03_dev/teacher_web/WEB_DESIGN_LOG.md`（✅ 仍活）
- **历史 demo 密码**：`12345678`（写在 `theme.jsx` 的 `window.SHARED_PASSWORD`）— ⚠️ **仅历史归档使用，不能用于 v1.0 正式版**

### 学生 iOS（HTML プロトタイプ阶段，~ 2026-05-06）

- HTML プロトタイプ：`03_dev/student_ios/demo/Tomoshibi_iOS_PhaseB_v2.html`
- JSX 解包源：`03_dev/student_ios/demo/phaseB_src/`
- QA 記録：`03_dev/student_ios/demo/QA_Round1_PhaseB.md`
- 設計 LOG：`03_dev/student_ios/IOS_DESIGN_LOG.md`（✅ 仍活）
- ~~Swift v1.0 実装别 repo `~/dev/TomoshibiiOSApp/`~~ → **2026-05-06 退役独立 repo 模式，全部代码移入 DMSD `03_dev/student_ios/v1/`**

---

## 历史模式废弃理由（2026-05-06 拍板）

1. **跨 repo 协作三件套**（cloud agent / 独立 repo / sync 脚本）维护成本太高
2. **5 端 monorepo** 在 DMSD 内统一管理，版本 / commit / issue tracker 单一来源
3. **HTML プロトタイプ** 作为设计冻结后的「视觉真值」用途已被 5 个端的 *_DESIGN_LOG.md 取代

详见：
- `99_archive/2026-05-06_cloud_agent_退役/`（退役决策 + 迁移记录）
- `99_archive/2026-04-29_pre_v1.0_cleanup/`（4-29 大整理产物）
- `CHANGELOG.md` v0.6 ~ v0.8 段

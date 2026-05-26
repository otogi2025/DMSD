# iOS v1 demo 完整快照（2026-05-26）

## 为什么有这个目录

itsuki 2026-05-26 拍板：「主推进只走干净 iOS app，有需要再单独包装成 demo」。

本目录 = 删 demo 后门**前**的完整状态备份，含全部演示用假数据 + 测试入口。

## 来源

复制自：`03_dev/student_ios/v1/TomoshibiApp/`（2026-05-26 当时状态）

## 内容（含 demo 后门）

| 文件 | 后门 |
|---|---|
| `Features/Auth/AuthStubs.swift` | A-035 注册流程 "000000" 万能验证码后门 |
| `Features/Home/HomeStubs.swift` | 点数卡长按 → `cycleDemoRollState()` 切点呼状态 |
| `Foundation/AppState/AppStore.swift` | `cycleDemoRollState()` / `tickCountdown()` / `simulateCheckin()` 前端自走逻辑 + `changeLog` 「高2→高3」假 seed |
| `Foundation/Seed/SEED.swift` | `SEED.user` 硬编码 リュウ イヒ / 060218 / 男寮 M101 / 4.5 点 |
| 全 app | 各处 `"Demo · ..."` 前缀 toast 文案 |

## 用法

未来要做演示版（教授 / 出愿用）：
1. 从本目录复制回 `03_dev/student_ios/v1/TomoshibiApp/` 临时位置
2. 或直接在本目录改 — 演示完归位

不要直接在本目录开发新功能 — 它是冻结快照。

## 联动文件

- `00_admin/TODO.md §989-997` v1.0 前 demo 清理清单
- `03_dev/student_ios/IOS_DESIGN_LOG.md §3.16` Demo 账号双用 + Reviewer 永久码
- `03_dev/student_ios/IOS_DESIGN_LOG.md §3.18`（即将新增）「demo 后门删除记录」

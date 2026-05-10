# Domain Docs

How the engineering skills should consume DMSD's domain documentation when exploring the codebase.

DMSD 是 5 端 monorepo，设计文档双层结构。**`CLAUDE.md` 是 single source**，本文件是给 skill 读的快照。

## DMSD Layout — Multi-context

| 层 | 路径 |
|---|---|
| 共用层（≥2 端涉及）| `02_design/system_features.md`（94KB single source）|
| iOS 専属 | `03_dev/student_ios/IOS_DESIGN_LOG.md` |
| Android 専属 | `03_dev/student_android/ANDROID_DESIGN_LOG.md` |
| Web 専属 | `03_dev/teacher_web/WEB_DESIGN_LOG.md` |
| 后端 専属 | `03_dev/backend/BACKEND_DESIGN_LOG.md` |
| 点呼机 専属 | `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md` |
| 物理硬件层 | `02_design/hardware_design.md` |
| 决策日志（替代 docs/adr/）| `05_logs/decision_log.md` |

完整规则见 `CLAUDE.md §设计文档双层` + `CLAUDE.md §文件连锁结构`。

## Before exploring, read these

- 共用层 `02_design/system_features.md` — 跨端工作前先读
- 工作的端的 `*_DESIGN_LOG.md`（按上面映射）
- `05_logs/decision_log.md` — 历史架构决策
- `CLAUDE.md` — 项目铁律 + 文件联动矩阵 + 中文铁律

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront.

## Use the glossary's vocabulary

DMSD 术语字典在 `01_specs/rollcall/`（字典三件套 + 主体）。用术语时按字典；不在字典里的是新概念，先跟 itsuki 确认（不要静默引入新术语）。

## Flag conflicts

如果输出跟 `05_logs/decision_log.md` 某条决策冲突，明确 surface（不要静默 override）：

> _跟 decision_log §X.Y 冲突 —— 但值得重新讨论，因为 ..._

## ADR equivalents

DMSD 不用 `docs/adr/`。等价物：

- `05_logs/decision_log.md` — 拍板决策（itsuki 写，CC 永不直写正文）
- `05_logs/raw/YYYY-MM-DD.md` — 当日 raw（CC 写）
- `05_logs/project_evolution.md` — 项目演化叙事（itsuki 写）
- `05_logs/learning_path.md` — 学习路径（itsuki 写）

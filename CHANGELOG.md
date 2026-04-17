# Changelog

> 版本号规则: [语义化版本 (SemVer)](https://semver.org/) — 主版本号.次版本号.修订号
>
> **说明**: 项目早期 spec 文件名里写的 "v1.0" 是指"规格文档的第一版",
> 不是项目的正式发布版本。项目的实际版本从 0.1.0 开始,
> 1.0.0 = 系统在宿舍正式上线运行。

---

## [0.1.1] - 2026-04-13

> **注**：本版本原标记为 0.2.0，但内容实质上仅为 **命名与元数据整理**（spec 文件实质内容未变），按 SemVer 规范应为 patch (0.1.1) 而非 minor bump。2026-04-17 审查时更正。

### Added
- `CHANGELOG.md` 版本记录文件
- 版本管理实践指南（放在 iCloud `00_通用指南/` — 通用文件,适用于所有项目）
- AC 入試 三层记录体系（raw / 候选 / 成品；详见 `00_admin/CLAUDE_CODE_记录指南.md` + iCloud `AC入试记录指南_v3.md`）
- `00_admin/WIP.md` 多会话协调文档

### Changed
- **spec 文件命名统一**: 所有 spec 文件从 "v1.0" 重命名为 "v0.1"，项目版本从 0.x.x 开始，1.0.0 = 宿舍正式上线
- 更新 `00_admin/executable_dev_checklist_v0.1.md`: 点呼主闭环增加硬件架构和分阶段说明
- 更新 `CLAUDE.md`: 反映分阶段策略和版本管理

### Notes
- 本版本是 **命名与元数据整理**，spec 文件实质内容无变化
- 4-12 的设计决策（NFC 硬件方案 / 分阶段策略 / 语音播报防作弊 / NFC vs 二维码）未写入 spec，记录在 `05_logs/decision_log.md`
- v0.2.0 将在 spec 实质重写完成后发布（当前进行中，见 `00_admin/TODO.md` 的"RollCall v0.1 spec 待修订事项"）

---

## [0.1.0] - 2026-02-12

### Added
- 规格文档冻结 (ENUM_REGISTRY, FIELD_REGISTRY, API_CONVENTIONS, ERROR_CODES)
- RollCall_Spec 点呼行为规格
- 可执行开发清单
- 冻结决策文档
- 项目目录结构建立

### Notes
- 这是项目的第一个正式版本基线
- 原始文件名使用 "v1.0",已在 0.2.0 中统一重命名为 "v0.1"

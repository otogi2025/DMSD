# Changelog

> 版本号规则: [语义化版本 (SemVer)](https://semver.org/) — 主版本号.次版本号.修订号
>
> **说明**: 项目早期 spec 文件名里写的 "v1.0" 是指"规格文档的第一版",
> 不是项目的正式发布版本。项目的实际版本从 0.1.0 开始,
> 1.0.0 = 系统在宿舍正式上线运行。

---

## [0.2.0] - 2026-04-12

### Added
- NFC 点呼机硬件架构设计: Raspberry Pi + PN532 NFC 模块 + 扬声器,贴墙安装
- 分阶段上线策略: Phase 1 (NFC 卡 + 后端) → Phase 2 (手机 App)
- 语音播报防作弊设计: 点呼机读卡后播报学生姓名,老师对照人脸
- NFC vs 二维码技术选型决策记录
- CHANGELOG.md 版本记录文件
- 版本管理实践指南 (放在 iCloud `00_通用指南/` — 通用文件,适用于所有项目)

### Changed
- **版本号体系重置**: 所有 spec 文件从 "v1.0" 重命名为 "v0.1",项目版本从 0.x.x 开始,1.0.0 = 宿舍正式上线
- 更新 `00_admin/executable_dev_checklist_v0.1.md`: 点呼主闭环增加硬件架构和分阶段说明
- 点呼机从"iPad/iPhone"改为"Raspberry Pi 专用设备"
- 更新 CLAUDE.md: 反映分阶段策略和版本管理

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

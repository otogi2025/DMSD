# 99_archive/ — 归档说明

> 不再活跃、但有 AC 叙事价值 / 历史证据价值、不舍得删的旧文件。
> 每项都注明"来源 / 是什么 / 为什么归档 / 有没有被转译到活跃区"。
>
> 最后更新：2026-05-27（4-17 以来累计 14 个新子目录归档：5-02 系列 × 4 / 5-03 icons / 5-04 文件结构指南 + 版本管理SOP / 5-06 cloud agent + migration / 5-12 深夜大整理 / 5-21 teacher_web demo / 5-21_pre_fix / 5-22 tomoshibi appstore fork / 5-26 teacher_web vite + ios v1 demo snapshot — 详细清单见 project-overview SKILL.md §7.2）。NFC_NFD 鬼影文件问题已 2026-04-10 解决（详见 `05_logs/problem_solving/2026-04-10_NFC_NFD_git_pull_failure.md`），该子目录作为跨平台 Unicode bug 的证据底稿保留。

---

## 目录清单

### 📁 `2025-12_早期GPT对话/`
- **是什么**：2025-12-19 23:11 JST 左右与 GPT 讨论 DMSD 初稿方案的对话三件套（`payload.json` / `prompt.txt` / `resp.json`）
- **为什么归档**：项目起源证据，pre-0.1 版本 `v0.0.1` ~ `v0.0.3` 的原始素材
- **活跃区对应**：`05_logs/raw/2025-12_NFC系统早期设计对话.md` 是整理后的 Markdown 版本

### 📁 `01_specs_Overview_原稿/`（新增于 2026-04-17 晚）
- **是什么**：`宿舍管理系统电子化总览.docx` + `数据库字段字典.docx`
- **来源**：原在 `01_specs/Overview/`，2-12 冻结 spec 前的早期 Word 草稿
- **为什么归档**：权威 spec 已经是 `01_specs/rollcall/*.md` + `FIELD_REGISTRY_v0.1.md`，这两份 docx 已被取代
- **保留原因**：itsuki 从 Word 起步到 Markdown 化的迭代证据

### 📁 `NFC_NFD_鬼影文件/`
- **是什么**：2026-04-10 debug 出来的跨平台 Unicode normalization 冲突文件（Mac NFC 编码 vs Linux NFD 编码导致 `git pull` 失败）
- **为什么归档**：problem_solving 的证据底稿
- **活跃区对应**：`05_logs/problem_solving/2026-04-10_NFC_NFD_git_pull_failure.md`

### 📄 `ファイル - 2026-02-17T00:18:58*.510Z`（14 个文件）
- **是什么**：2026-02-17 前后从 Google Drive / 其他来源导出的 GPT 对话文件（NFC 方案 / 扣分规则等早期讨论）
- **命名**：`.510Z` 后缀是导出时间戳的一部分（UTC），带编号 `(1)` ~ `(13)` 是批量导出序列
- **为什么归档**：2-12 spec 冻结前的决策证据；与活跃区 raw/ 可互为证据链
- **注意**：二进制，CC 在 Linux/Mac CLI 下无法直接读取内容

### 📄 `2026-03-08_Folder_Structure_Overview.pages`（2026-04-17 晚从 `00_admin/` 移入）
- **是什么**：最早期的目录结构构想文档（Pages 格式）
- **为什么归档**：`CLAUDE.md` 目录结构章节已是权威源；`00_admin/目录架构.md` 也已废弃删除。这份是更早的 .pages 原稿
- **历史：** 自 2026-03-08 初次 git commit 起就在 `00_admin/`，从未被引用

### 📄 `2026-04-12_executable_dev_checklist_v0.1.md`
- **是什么**：4-12 NFC 方案设计日更新过的开发清单
- **为什么归档**：2026-04-17 拆分成 TODO.md + spec 附录，原文件功能被取代
- **活跃区对应**：`00_admin/TODO.md` 吸收了其内容

### 📄 `learning_process_原始.pages`
- **是什么**：2026-02 月的学习笔记 Pages 原稿
- **活跃区对应**：内容抢救到 `05_logs/dev_log/2026-02-0[2348]_*.md`（4 篇）

### 📄 `progress_log_原始.pages` / `progress_log_备份版.pages`
- **是什么**：2026-02 月的周进度 Pages 原稿 + 备份
- **活跃区对应**：内容抢救到 weekly_review（已迁 iCloud AC 素材区）

### 📄 `需要学习的内容_原始.pages`
- **是什么**：2026-02 月的学习路线图 Pages 原稿
- **活跃区对应**：整合到 `05_logs/learning_path.md` 的 P0/P1/P2 章节

---

## 归档原则

1. **不直接删**：有 AC 叙事价值或证据链价值的 → 归档，不删
2. **原稿 + 活跃区并存**：活跃区用 Markdown（可 diff），原稿保留作"起源证据"
3. **二进制 only 的孤儿文件**（.pages / .docx / .510Z）→ 配一份 README 条目说明来源
4. **纯废稿**（被下一版完全取代，无历史价值）→ 直接 `git rm`，不进归档

---

## 清理 SLA

- 归档目录**不主动刷新**。只在活跃区有文件移入 / 有孤儿文件被发现时追加条目
- 如果某项证据已完全整合到活跃区（如 learning_process_原始.pages）且 1 年无人查阅 → 可进一步压缩（例如 zip）或考虑移到 iCloud 离线存档

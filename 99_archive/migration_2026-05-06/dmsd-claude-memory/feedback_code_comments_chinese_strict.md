---
name: 代码注释严格中文，禁止日语漂移
description: itsuki 2026-05-03 强调 — 代码注释只用中文，即使在做日语 UI 功能也必须中文，CC 多次违规需主动警觉
type: feedback
originSessionId: 91c5824c-61b8-49a4-8c62-8ff27def4ed0
---
**规则**：代码注释**只用中文**。UI 字符串（按钮 label / Section title 等用户能看到的）保持日语，但**注释一律中文**。

**Why**：
- 注释是给开发者（itsuki + CC + 未来代码 agent）看的，中文是 itsuki 的母语，最高效
- itsuki 在日本上学不代表他内部思考用日语 — 反而中文是他解析复杂逻辑的语言
- CLAUDE.md「语言规则」表已有「代码注释 | 中文」条款，但 CC 在做日语 UI 功能（注册流程 / 申请表单 / Image Playground 集成等）时**特别容易**漂移成日语注释 — 因为 UI 字符串都是日语，写代码时手感连贯就用日语写注释了
- 2026-05-03 在加 ImagePlayground import + RegisterStep1View 头像 AI 生成功能时，CC 写了大段日语注释（"端末本地で AI イラスト生成"、"AI 生成済み URL があればそれを表示"等），itsuki 当场要求改回中文 + 写进 CLAUDE.md

**How to apply**：
- 写注释前 conscious check："这是 UI 字符串还是注释？" — 注释 → 中文，UI → 日语
- 触发场景特别警觉：
  - 文件里 UI 文案都是日语时（AuthStubs.swift / ApplyStubs.swift 等）
  - 集成苹果系统功能时（ImagePlayground / FoundationModels 注释里别写日语）
  - 改后端 schema 里 study_absence 这种含日语 enum 值时（值本身是英文，注释中文）
- 已经写出日语注释 → 立即改中文，不要等 itsuki 提

**配合 memory**：
- `feedback_default_chinese_response.md` — 默认中文回答（对话层）
- `feedback_explain_terms_to_itsuki.md` — 大白话优先

**反例**（CC 之前写过的）：
- ❌ `// 端末本地で AI イラスト生成 (iOS 18.2+, Apple Intelligence 対応端末のみ)`
- ✅ `// 设备本地 AI 插画生成（iOS 18.2+，仅 Apple Intelligence 支持机型）`

- ❌ `// 非対応端末ではボタン自体非表示 → UX 一貫性`
- ✅ `// 不支持的机型按钮直接不显示 → UX 一致性`

**2026-05-04 第二次违规 incident**：
做学生注册码 + 老师公告 backend 4 个新文件（accounts.py / admin_registration_code.py / announcements.py / models.py + schemas.py 新加段 + 2 个 alembic migration），写了几十处日语注释（`# 5 分以内有効`、`# 既存 active を全部 invalidate`、`# 永続 session、login 同等`、`# 検証 logic` 等）。itsuki 第二次明确强调 + 要求加重 CLAUDE.md 规则。

**根本原因**：spec 文档（system_features.md §7.15-7.16 / BACKEND_DESIGN_LOG.md §4.10 + §5.x）大量用日语描述 → CC 抄 spec 时手感一连贯就日语写注释。**对策**：抄 spec 时要 conscious 翻译，**永远不要直接 copy 日语片段进注释**。

**2026-05-04 第三次违规 incident**（同会话稍后）：
更新 `02_design/system_features.md §7.15.11 / §7.16.5` 实装矩阵时，CC 用了日语写表格内容（"投稿 / 一覧 / 詳細 / 既読 / 返信 / 登録コード入力（登録最終 step）" 等）。itsuki 第三次强调"**规范文档也用中文写**" — CC 之前以为只有"代码注释要中文"，没意识到规范文档（设计文档 / WIP / TODO / spec / raw log）也算 "给 itsuki 看的内部内容"，应该用中文。

**新增覆盖范围**（CLAUDE.md §中文铁律 §2 已加）：
- `02_design/system_features.md` 等全部设计文档 — 新加 / 改写的章节、表格、bullet
- `03_dev/{backend,student_ios,teacher_web}/*_DESIGN_LOG.md` 全部
- `00_admin/` itsuki 看的全部文档（WIP / TODO / 同步点清单 / 文件结构指南）
- `05_logs/raw/*.md` AC 素材 dump
- `01_specs/` 全部 spec 文档

**边界（仍保持日语）**：UI 字符串 / 邮件文案 / push 文案 / spec 引用的固定 message / 教授看的产品介绍页 / itsuki 写给教授的志望理由书自己产物。

**关键认知**：itsuki 是 DMSD 项目所有规范文档的**唯一长期读者**（教授只在最后阶段看 PRD 类成品，且那部分 itsuki 自己用日语写）。中间过程文档用日语 = itsuki 读得慢 + 漏关键细节。

**触发警觉清单（CC 看到这些关键词在自己即将写的注释里就停下来翻译）**：
- 高频粒子词：の / を / が / は / で / に / へ
- 时态语尾：です / ます / である / だった / になる
- 高频功能词：処理 / 機能 / 設定 / 実装 / 検証 / 生成 / 取得 / 登録 / 削除 / 更新 / 表示 / 一覧 / 必須 / 任意 / 既存 / 新規
- 数量词：以内 / 以上 / 以下 / 程度 / 等 / など
- 因果连接：ため / ので / から / なので

→ 出现以上任一 = 立即翻译成中文。

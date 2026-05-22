# 会话 B findings — 第二档该审（维度 6-10）

生成于：2026-05-20 ~01:30（子代理 B / Opus 4.7 1M）

> 审查范围：维度 6 规格主体一致性 / 维度 7 物理硬件 vs 点呼机软件 / 维度 8 memory 索引完整性 / 维度 9 挂钩系统 / 维度 10 TODO.md 真值
> 工作流：维度 10 → 8 → 9 → 6 → 7（按出活快优先 + 5-19 改动新鲜度）

---

## 维度 10：TODO.md 真值审查

### [B-001] 🔴 TODO §⏰ 时间敏感 — Cloud Design 5-12 截止已过期但仍挂着

- **文件**：`00_admin/TODO.md:18-22`
- **描述**：「2026-05-12 截止：用掉 Cloud Design 40 额度」— WIP.md `🎯 当前焦点` 段已明确说「5-12 额度已过期 / 5-14 检查时已浪费」。TODO 顶部仍挂作「即将到期」违反真值。§F「5-12 收尾残留待拍板」也独立挂了同一条「Cloud Design 40 额度 5-13 凌晨已过截止」（`TODO.md:87`）— 同条目重复出现两次。
- **建议改法**：把 §⏰ 这条标记 `[x]` 或归档到「已废 — 5-12 截止过期 / 额度浪费」；§F 那条同时归档（消重）。
- **跨会话**：跟 WIP.md `🎯 当前焦点` 第 2 段「⏰ Cloud Design 5-12 额度已过期」一致 — WIP 是真值，TODO 是漂移。
- **严重程度**：🔴（顶部「即将到期」位置 = 启动 CC 扫 TODO 顶部 200 行第一眼看到，假信息）

### [B-002] 🔴 TODO §🛠️ G 内编号重复（F 和 G 同时存在 + 两个 G）

- **文件**：`00_admin/TODO.md:72`（§G anti-ai-flavor）+ `00_admin/TODO.md:83`（§F 5-12 收尾残留）+ `00_admin/TODO.md:94`（§G 5-14 Tango 立项）
- **描述**：§ 编号违反顺序 — A → B → C → D → E → **G**（5-14 加）→ **F**（5-13 加）→ **G**（5-14 晚段加）。第二个 G 跟第一个 G 同字母。从 `TODO.md:9` 「最后更新」叙述看，5-14 加 §🛠️ G 时已存在另一个 G，没去重命名。
- **建议改法**：第二个 G（5-14 晚段 Tango 立项收尾残留）重命名为 §H；并加 TOC 让 CC / itsuki 快速定位。
- **跨会话**：维度 10 TODO 内部漂移 — 不影响其他文件，但 CC 引用「§G」会有歧义。
- **严重程度**：🔴（标号重复在文档治理铁律里属硬错）

### [B-003] 🟡 TODO §F (5-12 收尾残留) 跟 §🛠️ A/B/C/D/E 跟 §G 大量功能重复

- **文件**：`00_admin/TODO.md:83-92`（§F）vs `00_admin/TODO.md:72-81`（§G）
- **描述**：
  - §F「MEMORY.md 主体刷新」（line 91）vs §G「2 个 memory 候选评估」（line 99）— 都关 memory。
  - §F「graphify 图谱 vendor 污染清」（line 90，已 ❌ 废）冗余跟 §🛠️ C（line 43，已 ❌ 废）— 同一条事 2 处标废。
  - §F「整理脚本 /tmp/cleanup_2026-05-12.sh 跑不跑」（line 88）— 已是 7+ 天前，Mac 重启就丢，事实上已废。
- **建议改法**：§F 同 §🛠️ C 已废条目按归档铁律移到 §1061「已完成归档」附近；活的留 §F 内（如「iOS 联动规则漂移修复」line 89 是真活）。
- **跨会话**：跟 §🛠️ C 重复 — 见 [B-001]/[B-006]。
- **严重程度**：🟡

### [B-004] 🔴 TODO §🎯 2026-04-28 管理员 Demo 冲刺段 — 整段过期但仍标「最高优先级」

- **文件**：`00_admin/TODO.md:542-559`
- **描述**：该段顶部写「Deadline: 2026-04-28（7 天）/ 最高优先级」— Demo 已过 22 天（demo 2026-04-28），管理员已基本同意采纳（MEMORY.md line 48 写 2026-04-29 反馈拿到），「itsuki 侧 D1 剩余」5 条已大多过期（如「Amazon 日本下单 Pi 3A+ + 配件（明天 4-22 到）」— TODO.md:551 — 上下文是 4-21 前的「明天」），但仍以「最高优先级」呈现。
- **建议改法**：整段移到 §1061「已完成归档」+ 加「Demo 通过验证 2026-04-29」状态；剩余真活（如代码 agent 任务）归到对应 §位置。
- **跨会话**：WIP.md 不复述具体 demo backlog，但 TODO 假高优先级会被 CC 启动扫 200 行误判焦点。
- **严重程度**：🔴

### [B-005] 🔴 TODO §🚨 当前卡住的决策 — 硬件架构层全部已拍板但仍标「未决」

- **文件**：`00_admin/TODO.md:720-760`
- **描述**：该段顶部写「必须先做，不然项目推不动」。**但**：
  - line 724-727「点呼机大脑选型 Pi vs ESP32」— 已 4-15 拍板 Pi 方向 + 4-21 拍板 Pi 3A+（`02_design/hardware_design.md §2.1`）
  - line 729-731「Pi 具体型号 Zero 2 W vs 4B 2GB」— 已 4-21 拍板 Pi 3A+（推翻 4-20 Pi 4B 2GB），跟 TODO 选项都不一样
  - line 733「PN532 NFC 读头接口 GPIO vs USB」— 已 5-08 拍板 PN532 V3 模块 + SPI 推荐（`hardware_design.md §2.2`）
  - line 735-736「LED 灯方案」— 已 5-08 拍板 LED 模块 5 色套装（`hardware_design.md §2.4.1`）
  - line 738「扬声器方案」— 已 5-08 拍板 01Studio USB 小音响（`hardware_design.md §2.4.2`）
  - line 740「电源 + 贴墙」— 电源已拍 5V 2.5A micro-USB（`hardware_design.md §2.6`），贴墙待勘察留 §6
  - line 742「点呼机部署数量 4 台 — 但位置和通道分配待确认」— 仍真活，保留
- **建议改法**：6/8 项归到「已拍板」（标 ✅ + 引用 hardware_design.md 章节），剩 2/8（位置 / 卡片形式 / 丢卡补卡 / 部署外壳 / 流程细节）保留真活；调到 §🛰️ 点呼机第 5 端 backlog（§192 段，那里已有「等下单」+「拍板 D1-D6」更准确版本）。
- **跨会话**：跟 `02_design/hardware_design.md` 真值不同步，CC 启动扫 200 行误判。
- **严重程度**：🔴

### [B-006] 🟡 TODO §🐛 + §📱 + §🛰️ 一堆嵌套的「已完成 + 残留」mixed list

- **文件**：`00_admin/TODO.md:105-249`
- **描述**：§📱 iOS 上架冲刺、§🐛 主项目 v1 backend bug fix、§🛰️ 点呼机第 5 端 这 3 大段都把「已完成」+「待办」混在同一 list 里。例如 §🐛 line 171-188 一段叫「✅ Demo seed / 999999 注册码后门 — 已修复」但本身嵌套了 9 个 `[x]` + 1 个 `[ ]`（待办 = admin 密码改）。
- **建议改法**：把「✅ 已完成」段从「📱 / 🐛 / 🛰️」section 抽离归档到 §1061；保留真活在原位。
- **跨会话**：CC 扫 200 行容易把已完成项当待办处理。
- **严重程度**：🟡

### [B-007] 🟡 TODO §🟢 低优先级 含已过期的死条目

- **文件**：`00_admin/TODO.md:1003-1015`
- **描述**：line 1003「.pages 文件转 Markdown（4 个文件）」— `01_specs/rollcall/*.pages` 1 个文件（RollCall_Spec_v0.1.pages，line 1007）已被 `RollCall_Spec.md` 取代（2026-04-17 v0.2 主体 rewrite，MEMORY.md line 29 写明），转换已废。line 1012「归档早期 iOS throwaway 代码」— 已 4-29 大整理归档到 `99_archive/2026-04-29_pre_v1.0_cleanup/`（TODO 自己 line 692 标了 ✅ T2）。
- **建议改法**：line 1003 4 个文件改为 3 个（去 rollcall）+ 加注「⏳ 仅 4 个非 rollcall pages 待 itsuki 操作」；line 1012 改为 `[x]`。
- **跨会话**：跟 line 692 的「✅ T2」自相矛盾。
- **严重程度**：🟡

### [B-008] 🟢 WIP vs TODO 重叠违反铁律 — 「graphify 不卸不用」

- **文件**：`00_admin/WIP.md:175-184` vs `00_admin/TODO.md:43-50`
- **描述**：WIP「最近会话」5-14 中午 graphify 复盘段（line 175-184）详写「拍板不卸不用 + 留作 AC 素材」+ 「TODO §🛠️ C / §🛠️ F 标记为已废」。TODO 实际也写了 §🛠️ C「graphify 图谱清洗 — ❌ 已废」（line 43-49）+ §🐛 F.2「graphify 图谱 vendor 污染清」（line 90）— 但描述并不互相 cross-ref，最后导致两边都说「另一份在那」但同一规则在两份文档里维护。WIP 铁律是「未完成的事**只写在 TODO**。本文件**绝不**复述 TODO 的内容」（WIP line 17）。
- **建议改法**：WIP 改成「5-14 中午 graphify 复盘 — 拍板见 raw / 残留见 TODO §🛠️ C」短摘要，砍详细描述。
- **跨会话**：违反 WIP §职责分工 铁律 —「WIP = 当下书签」不是「会话历史详细记录」。
- **严重程度**：🟢（铁律违反但内容一致没漂）

### [B-009] 🟢 TODO §📄 文件格式 MD → HTML 改造候选清单 中 itsuki 已拒绝项还在

- **文件**：`00_admin/TODO.md:284-304`
- **描述**：candidates 段列了 13+ 文件为「HTML 改造候选」。但 MEMORY.md 索引里有 `feedback_dont_re_raise_rejected_topics.md`（line 94，「用户明确拒绝的事不要再提」），其中 line 175 列「`README.md` — GitHub 公开页」是低优候选 — itsuki 4-29 已大幅 cleanup README（MEMORY.md line 48），暗示当前 README MD 渲染状态已 OK。
- **建议改法**：低优段先标「未启动 — 等 §A 元任务做完再 review」，避免「等 itsuki 拒绝后才知道这事在排队」。
- **严重程度**：🟢

### [B-010] 🟢 TODO §🛣️ 推进路线图 38 条 — 「设计层覆盖度 baseline」数字状态可能漂

- **文件**：`00_admin/TODO.md:397-404`
- **描述**：4-30 拍板「B 标准 itsuki 拍板版」 ✅ 7 / ⏳ 27 / ❌ 3 / 🚫 2。5-08 起后端 routers P0 大批落地（line 699 自承「rollcall / study / accounts / admin_registration_code / teachers / applications / auth / meals / notifications 都已建」）+ iOS Foundation 17 + 3 Feature 真实装（line 701）— 但 38 条对应 ✅ 数没更新。
- **建议改法**：line 397-404 数字加注「⚠️ 数字 = 设计层 4-30 baseline；实装层进度看 §F 5-04 状态汇总」。或重 baseline 一次。
- **严重程度**：🟢

---

## 维度 8：memory 索引完整性

### [B-011] 🔴 CLAUDE.md 引用 `feedback_design_doc_layers.md` 死链 — 文件不存在

- **文件**：`/Users/kurekoduki/dev/DMSD/CLAUDE.md:63`
- **描述**：CLAUDE.md line 63「判断标准 / 反模式: memory feedback_design_doc_layers.md」— 该文件**不存在** memory 目录里（`ls /Users/kurekoduki/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/feedback_design_doc_layers.md` → `No such file or directory`）。MEMORY.md 索引也没列。
- **建议改法**：要么写该 memory（设计文档双层 / 判断标准 / 反模式 — 内容散在 CLAUDE.md `## 设计文档双层` 段），要么 CLAUDE.md line 63 改成「判断标准 / 反模式：见 CLAUDE.md `## 设计文档双层` 段」。
- **跨会话**：CLAUDE.md 是 CC 每次启动 must-read，死链每次都误导 CC「该 memory 存在」。
- **严重程度**：🔴

### [B-012] 🔴 CLAUDE.md 引用 `feedback_code_comments_chinese_strict.md` 死链 — 文件不存在

- **文件**：`/Users/kurekoduki/dev/DMSD/CLAUDE.md:69`
- **描述**：CLAUDE.md line 69「中文铁律 — 代码注释 + 内部文档 100% 中文 / UI 字符串保持日语: memory feedback_code_comments_chinese_strict.md」— 该文件**不存在**。但 `00_admin/hooks/README.md:30` 也引用了「出处：memory `feedback_code_comments_chinese_strict.md`（2026-05-03 itsuki 拍板）」— 双重引用都死链。规则真活（hook `post-edit-japanese-comment-check.sh` 还在跑），但 memory 文件本身缺失。
- **建议改法**：写该 memory 落实「2026-05-03 itsuki 拍板」（规则在 hook 里活着但没 narrative 留痕），或两处引用都改成 hook README 段。
- **跨会话**：CLAUDE.md + hooks/README 都引用 = AC 叙事文件「我立了规则 + 写了 memory」实际上 memory 不存在 = AC 叙事可能露馅。
- **严重程度**：🔴

### [B-013] 🔴 CLAUDE.md 路径漂 — `~/.claude/projects/-Users-itsuki-dev-DMSD/memory/MEMORY.md`

- **文件**：`/Users/kurekoduki/dev/DMSD/CLAUDE.md:205`
- **描述**：CLAUDE.md line 205「详细规则 / feedback 历史: ~/.claude/projects/-Users-itsuki-dev-DMSD/memory/MEMORY.md 索引（feedback_*.md 系列）」— 路径是 `-Users-itsuki-dev-DMSD/`，但实际真路径是 `-Users-kurekoduki-dev-DMSD/`。账号名是 `kurekoduki`（参 git status 头部 `Git user: itsuki` 但 Mac 用户名 `kurekoduki`）。CLAUDE.md 这条路径**不存在**。
- **建议改法**：CLAUDE.md line 205 改成 `~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/MEMORY.md`。
- **跨会话**：影响所有跑 DMSD 项目的 CC 会话 — 每次启动读 CLAUDE.md 时 CC 试图按这路径找 memory 找不到。
- **严重程度**：🔴（影响最大 — 每次启动都漂）

### [B-014] 🟡 MEMORY.md stale fact — 「项目 v0.3.1」实际是 v0.8.0

- **文件**：`/Users/kurekoduki/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/MEMORY.md:29` + `:46`
- **描述**：
  - line 29 「Project overall version: see CHANGELOG.md 顶部 (current v0.3.1 as of 2026-04-20)」— 当前是 v0.8.0（WIP.md line 24）
  - line 46 「2026-04-20（晚 [Mac-主会话]）: v0.3.1 tag 发布 (fb330c2)」+ 关于「8 commit + 10 pre-0.1 annotated tag 追认 + v0.3.1 tag 都 local 未 push」— 后面 7 个版本（v0.4-v0.8）的「最后版本是 X / 发布日」没记录
  - TODO §F line 91 已自己标注「MEMORY.md 主体刷新 — 多处 stale 行（v0.3.1 应改 v0.8.x / 4-10 旧 TODO 应清理）」— itsuki 已意识到但未刷新
- **建议改法**：line 29 改为「Project overall version: 见 `CHANGELOG.md` 顶部 + WIP.md 顶部 — 截至 2026-05-19 v0.8.0」；line 46 加「v0.4-v0.8 演化简表」。
- **跨会话**：MEMORY.md 是 always-on 加载 → CC 拿到 stale 版本号会决策错。
- **严重程度**：🟡（已知欠债但未修）

### [B-015] 🟡 MEMORY.md stale fact — 「VPS (~/DMSD)」段已废但仍叙述

- **文件**：`/Users/kurekoduki/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/MEMORY.md:33-35`
- **描述**：line 24「Mac path: ~/dev/DMSD | VPS path: ~/DMSD」+ line 34「VPS (~/DMSD) was previously used via SSH from school iPad ... 2026-04-19 itsuki decided to stop pushing DMSD work from VPS」+ line 28 G2 决策也包括「VPS deprecated for DMSD」。但 line 24 平铺 Mac / VPS 双 path = 误导，VPS path 已 deprecated。
- **建议改法**：line 24 改成「Mac path: ~/dev/DMSD (only — VPS 2026-04-19 deprecated)」；line 33-35 段缩成一句「2026-04-19 G2 decision: VPS deprecated (本来 ~/DMSD via SSH)」。
- **跨会话**：可能误导 CC「该不该 VPS 同步」 — itsuki 已拍板不同步。
- **严重程度**：🟡

### [B-016] 🟡 MEMORY.md TODO 段过期 41 天 — line 56-63

- **文件**：`/Users/kurekoduki/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/MEMORY.md:56-63`
- **描述**：「TODO (as of 2026-04-10)」段列了 7 条 TODO — `Continue Python` / `Convert .pages files to Markdown (13 files)` / `Create AC log structure` / etc. 41 天过去这些 TODO 大多已完成（AC log structure 已建 / pages 转换部分完成 / Swift 已开始）。但 MEMORY.md TODO 段没刷新。
- **建议改法**：line 56-63 段整段砍 — TODO 真值在 `00_admin/TODO.md`，memory 不复述。或改成「TODO 真值见 00_admin/TODO.md — 本段不再维护」。
- **跨会话**：违反单源真值 — TODO 在 TODO.md，不在 MEMORY.md。
- **严重程度**：🟡

### [B-017] 🟡 MEMORY.md Python Day 1 段 (2026-03-11) 41 天未更新

- **文件**：`/Users/kurekoduki/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/MEMORY.md:50-54`
- **描述**：「Python Learning Progress」段冻在 Day 1（2026-03-11），但实际从 4-13 起 itsuki 重启项目后大量编程实战（5 端代码 / migrations / hooks），Python 学习路径已不止 Day 1。learning_path.md 可能有更新但 MEMORY.md 没同步。
- **建议改法**：要么砍此段（学习进度在 `05_logs/learning_path.md`），要么改成「Python 学习路径见 `05_logs/learning_path.md`」。
- **严重程度**：🟡

### [B-018] 🟢 memory 孤儿 — `feedback_llm_self_discipline_unreliable.md` 没建但 TODO 已规划

- **文件**：`00_admin/TODO.md:67-70`
- **描述**：TODO line 67 写「LLM 自觉性失败工程教训写成 feedback memory（要 itsuki 同意才写，按规则 5）/ 路径：`~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/feedback_llm_self_discipline_unreliable.md`」— 这是规划中的 memory，未写。不属于死链问题，但属于已规划未落地。
- **建议改法**：等 itsuki 拍板才写（已按 memory-write SOP 走对了），保留 TODO 项即可。
- **严重程度**：🟢

### [B-019] 🟢 MEMORY.md description vs 正文一致 — 抽样验证 OK

- **文件**：抽样 `feedback_be_a_coach_not_executor.md` / `feedback_no_handoff_work_back_to_itsuki.md` / `feedback_no_dense_jargon_strings.md` / `project_demo_scaffolds_to_remove_before_v1.md`
- **描述**：抽样的 4 个 memory 文件 description 字段跟正文核心规则一致 — 没找到「说一回事写另一回事」case。但 26+ memory 文件没全扫，留 medium-risk。
- **建议改法**：定期跑 description vs §1 段对齐自动 check（可加 hook）。
- **严重程度**：🟢

### [B-020] 🟢 「2 条 memory 内容自相矛盾」抽样 — 未找到明显矛盾

- **描述**：抽样 4 个 feedback memory 没找到矛盾。但 26+ feedback 全扫超出本会话时间，留 follow-up。
- **建议改法**：跑 LLM-based memory contradiction scan（如 obsidian-reconcile skill）。
- **严重程度**：🟢

---

## 维度 9：挂钩系统审查

### [B-021] 🔴 `bin/check_overview_drift.sh` awk bug 确认 — 影响 `.claude/` + `bin/` 章

- **文件**：`/Users/kurekoduki/dev/DMSD/bin/check_overview_drift.sh:46-54`
- **描述**：实跑结果（cd DMSD && bash bin/check_overview_drift.sh）：
  ```
  ⚠️ project-overview §0.1 漂移检测（启动时跑）：
  总计：写 957 / 实际 957
  顶级目录差异：
    - .claude/: 写 23 / 实际 9
    - bin/: 写 3 / 实际 2
  ```
  - `.claude/` 实际 9 是 root level 9 文件（一致），脚本说「写 23」实际是抓到了 `project-overview/SKILL.md §1.8.1 .claude/skills/ 23 行表格」而非 §0.1 体量表里的 9」（awk 正则 `\| `[^`]+\/` *\| *[0-9]+ *\|` 匹配过宽）— WIP §残留段已自承「awk 取到了 §1.8.1 的 23 而非 §0.1 的 9」（WIP line 83）
  - `bin/` 写 3 / 实际 2 = 第 3 个文件 `check_overview_drift.sh` 未 commit（WIP line 84 自承），但脚本不区分 staged / committed → 用 `git ls-files` 取不到未 commit 的
- **建议改法**：
  1. awk 正则限定到「§0.1 体量表」上下文（用 `BEGIN/END` block 标记 + `in_overview_table=1` flag）
  2. 单独跑 `git ls-files` vs `git status` 区分 staged / committed → 报「未 commit X 个」而非笼统差异
- **跨会话**：5-19 拍板「C 方案 = A hook + B 启动对账双层保险」，但 B 这个核心机制本身有 bug → 每次会话启动都报伪差异。
- **严重程度**：🔴（拍板的核心机制 bug）

### [B-022] 🟡 hooks README 跟实际脚本名字段对齐不严 — A/B/C/D/E/F/G/H/I 字段错乱

- **文件**：`00_admin/hooks/README.md:15-110`
- **描述**：README 给挂钩分了字段：
  - 段 `### CC PostToolUse hook（7 条 ...）`（line 15）说 7 条，实际是 7 条（A/B/C/D/E/F/G）✅
  - **但** §I「`bin/check_overview_drift.sh` ... — project-overview §0.1 体量表对账（5-19 加）」(line 87) 跟 §H「`post-checkout` — graphify 切分支后重建」（line 105）字段顺序错位 — I 是 SessionStart 但位置在 G post-edit-format（PostToolUse）之后、H post-checkout（git hook）之前 — 应改为 H = bin/check_overview_drift.sh，I = post-commit，J = post-checkout 顺序排齐
  - §F line 67-83 标 `pre-bash-destructive-block.sh` 是「F.」 — 跟 §F line 43 (post-edit-project-overview-check.sh) 重复 F 字段
- **建议改法**：重排字段 A-K 顺序 = PostToolUse 7 + PreToolUse 1 + SessionStart 1 + Git 2 = 11 条 / 字段独立编号。
- **严重程度**：🟡

### [B-023] 🟡 `00_admin/hooks/pre-commit:99` 引用过期路径「`00_admin/版本管理SOP.md`」

- **文件**：`/Users/kurekoduki/dev/DMSD/00_admin/hooks/pre-commit:99`
- **描述**：pre-commit 输出「→ 对照 00_admin/版本管理SOP.md §2 决策树判断」— 该文件**不存在**（已迁到 `.claude/skills/version-bump/SKILL.md`，CLAUDE.md line 79 已对齐）。pre-commit 引用旧路径。第二处 `:59` 也写「背景：00_admin/文档同步点清单.md §1」— 这文件**存在**（已验证）但 pre-commit hook 应跟 skills 一致使用新路径。
- **建议改法**：pre-commit line 99 改为「→ 对照 .claude/skills/version-bump/SKILL.md §2 决策树判断」。
- **跨会话**：跟 CLAUDE.md line 79 `.claude/skills/version-bump/SKILL.md` 已是新路径不一致。
- **严重程度**：🟡

### [B-024] 🟡 hooks README 测试命令含过期路径

- **文件**：`/Users/kurekoduki/dev/DMSD/00_admin/hooks/README.md:118`
- **描述**：README §测试方法 line 118 写：
  ```
  echo '{"tool_input":{"file_path":"/Users/kurekoduki/.claude/projects/-Users-itsuki-dev-DMSD/memory/test.md"}}' | bash ...
  ```
  路径是 `-Users-itsuki-dev-DMSD`，应为 `-Users-kurekoduki-dev-DMSD`（同 [B-013] 漂）。
- **建议改法**：line 118 改账号名。
- **严重程度**：🟡

### [B-025] 🟢 settings.json 注册数 vs hooks 目录 — 一致

- **文件**：`/Users/kurekoduki/dev/DMSD/.claude/settings.json`
- **描述**：settings.json 注册 = 7 PostToolUse + 1 SessionStart + 2 PreToolUse（其中第 2 个是 inline 的 graphify 报告提示）= 10 hook 调用。`00_admin/hooks/` 7 个 post-edit + 1 pre-bash + 1 pre-commit + 1 install + 2 git hook + 1 lib = 跟 README 说的对得上。配置 OK。
- **严重程度**：🟢

### [B-026] 🟢 hooks lib/sync-rules.sh 没死链 — 抽样 grep 路径都对

- **文件**：`00_admin/hooks/lib/sync-rules.sh`（466 行未完整读，靠 grep）
- **严重程度**：🟢

---

## 维度 6：规格主体一致性

### [B-027] 🔴 spec 主体 §1 仍用 Phase 1 / Phase 2 模型 — 已被 4-19 G2 决策推翻

- **文件**：`01_specs/rollcall/RollCall_Spec.md:17-18` + `:182-240` + `:586-590` + `:625-628`
- **描述**：spec 多处仍用 `Phase 1 / Phase 2` 表述：
  - line 17-18：「**路径 A — NFC 卡** ... Phase 1（先上线，不需要学生 App）」/ 「**路径 B — iPhone 静态标签** ... Phase 2（追加，与卡共存）」
  - line 233-240：§5.1.3 标题「防代签（**Phase 1 关键人防补偿**）」
  - line 460-466：组件表「学生 iPhone App（路径 B / **Phase 2**）」/「老师本人（人防）... **Phase 1** 防代签的关键」
  - line 588：「但 4-12 决定的 **Phase 1** 是 NFC 卡 + 点呼机直读，没有手机 App」
- **背景**：MEMORY.md line 28 + CLAUDE.md 都写「2026-04-19 G2 decision: no phased launch. v1.0 = cards + iPhone + Android all together. CLAUDE.md 'Phase 1 / Phase 2' split is deprecated.」
- **建议改法**：spec 全面替换 Phase 1 / Phase 2 表述：
  - Phase 1 / 路径 A → 「路径 A（NFC 卡）」
  - Phase 2 / 路径 B → 「路径 B（iOS Universal Link）」+ 加「路径 C（Android App Link）」
  - line 233-240 防代签段 = 永久人防补偿（不只 Phase 1）
- **跨会话**：5 端各 DESIGN_LOG / system_features.md 跟 spec 主体 Phase 表述对齐情况需另查（维度 1-5 范围）。
- **严重程度**：🔴（基础上线姿态描述 vs 2026-04-19 决策不一致）

### [B-028] 🔴 spec 主体 §7 + §10 仍引用 `effective_*` 平移概念 — 已被 §5.4 推翻

- **文件**：`01_specs/rollcall/RollCall_Spec.md:396` + `:500` + `:514-516` + `:527`
- **描述**：spec §5.4「老师手动开始 — 窗口固定（不平移）」（line 265-287）4-29 修订**推翻了原平移规则**，但其他段仍写：
  - line 396「判定时使用 effective_*（已考虑老师提前开始的窗口平移）」
  - line 500「`effective_window_start_at` 等 4 个 ... 老师提前开始后平移过的实际判定区间（必须保存）」
  - line 514-516 数据模型 rollcall_event 段写「`applied_group` ... 本次判定使用的 `effective_group`」
  - line 527「判定使用 `effective_*`，结算使用 `effective_auto_end_at`，查表使用 (session_type, day_type, effective_group)」
- **建议改法**：
  - 「不平移」生效后，`effective_window_start` 等 = `scheduled_window_start`（永远相等）。要么彻底删 `effective_*` 概念，要么明确「现在 effective = scheduled，但保留字段名为以后可能再平移留空间」
  - §5.5 line 304 自己也写「（注：因 §5.4 不平移，`auto_end_at = scheduled auto_end_at` 直接使用，不再有 `effective_*` 概念）」— spec 内部自相矛盾
- **跨会话**：iOS / Android / backend 实装代码用 effective 还是 scheduled？跨端漂移风险。
- **严重程度**：🔴

### [B-029] 🟡 字典 ENUM_REGISTRY §13 `path_type` 扩展性说明跟 4-19 G2 不一致

- **文件**：`01_specs/rollcall/ENUM_REGISTRY.md:82-87`
- **描述**：line 87「扩展性说明（4-22 新增 — S9 修复）：A/B 是当前（v0.3.x/v0.4.x）的全部取值。**未来如果引入 Android HCE 主动上报路径**（当前 4-19 G2 决策 Android 也走静态标签 = path_type=B，和 iPhone 一致），**新起独立取值 `C`**」— 4-19 G2 decision 是「v1.0 ships iOS + Android simultaneously」即 v1.0 范围内 Android 已上线。但 ENUM 还把 Android = B 视为「当前」。
- **建议改法**：明确 v1.0 上线 Android 用 B = 跟 iOS 同实现，未来扩 C 留作 backlog；或现在就拆 C（如果 Android 实装跟 iOS 不同）。
- **跨会话**：5-08 backend `rollcall_event.path_type` 扩展实际取值 itsuki / 主会话 / Android 会话拍板见。
- **严重程度**：🟡

### [B-030] 🟡 字典 DEVICE_REGISTRY §3.1 `card_reader` 物理形态写「Pi Zero 2 W / Pi 4B 等」— 已废

- **文件**：`01_specs/rollcall/DEVICE_REGISTRY.md:30`
- **描述**：line 30「物理形态：树莓派（Pi Zero 2 W / Pi 4B 等）+ PN532 NFC 模块 + 扬声器」— 已废。`02_design/hardware_design.md §2.1` 4-21 拍板 Pi 3A+ 推翻 4-20 Pi 4B 2GB。Pi Zero 2 W 在 4-20 议题 A 已被排除。
- **建议改法**：line 30 改为「物理形态：Raspberry Pi 3A+ + PN532 V3 模块 + 01Studio USB 小音响（详见 `02_design/hardware_design.md §2`）」。
- **严重程度**：🟡

### [B-031] 🟡 字典 DEVICE_REGISTRY §6 部署位置候选码跟 TODO §🛠️ S18 已拍板修复不一致

- **文件**：`01_specs/rollcall/DEVICE_REGISTRY.md:91-98`
- **描述**：line 95-98 列「`dorm-A-01` / `dorm-B-01` / `dorm-C-01` / `dorm-D-01`」。TODO line 663 自承「**S18（低价值）**：DEVICE_REGISTRY §6 候选位置 `dorm-A-01 / dorm-B-01` 跟 `path_type` A/B 撞字 — 改成 `dorm-1-01 / dorm-2-01`」— 已规划改但未落地。
- **建议改法**：按 S18 修法改成 `dorm-1-01 / dorm-2-01 / dorm-3-01 / dorm-4-01`（4 寮 Q1 已答男 1/2 女 4 / 3 寮废止 — 实际 3 个寮，TODO 与之不符）。
- **跨会话**：跟 Q1 答案（line 527「1·2 寮 = 男 / 4 寮 = 女 / 3 寮废止」）也不一致。
- **严重程度**：🟡

### [B-032] 🟢 字典 ENUM_REGISTRY §3 `exempt_range` 跟 spec 主体 §2.1 OK

- **文件**：`ENUM_REGISTRY.md:14-23` + `RollCall_Spec.md:43-51`
- **描述**：4-17 修订把 `exempt_range` 从 overlay 升 base_status 已对齐两边。
- **严重程度**：🟢（一致 — 修复证据）

### [B-033] 🟢 字典 FIELD_REGISTRY §3 禁止字段 — 来源指针完整

- **文件**：`FIELD_REGISTRY.md:101-108`
- **描述**：5 个废弃字段（`my_status` / `my_base_status` / `seat_status` / `state` / `background_status`）都有「来源」+「废弃时间」标注。S20 修复有效。
- **严重程度**：🟢

### [B-034] 🟢 字典 ERROR_CODES vs spec 主体 §7 边界规则 — 已对齐

- **文件**：`ERROR_CODES.md` + `RollCall_Spec.md:404-417`
- **描述**：S4 / S16 / S19 修复都已在 ERROR_CODES 跟 spec 主体两边同步。
- **严重程度**：🟢（一致）

---

## 维度 7：物理硬件 vs 点呼机软件

### [B-035] 🟡 GPIO 接线 hardware_design.md vs ROLLCALL_DEVICE_DESIGN_LOG §2 不同步

- **文件**：`02_design/hardware_design.md` + `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md:61-78`
- **描述**：
  - ROLLCALL_DEVICE_DESIGN_LOG §2 line 65-75 列了 GPIO 初步分配表（PN532 SPI on GPIO 8/9/10/11 / ST25DV I2C on GPIO 2/3 / LED 红 GPIO 17 / LED 绿 GPIO 27 / LED 蓝 GPIO 22）
  - hardware_design.md §2.4.1 line 183 只说「LED 接 Pi GPIO 数字输出（每色一个 GPIO 引脚 + 共地）」**不给具体引脚号**
  - hardware_design.md §2.4.2 line 195 只说「USB 2.0（取电）+ 3.5mm 音频口（音频信号）」**不给端口编号**
  - ROLLCALL_DEVICE 自己也标 ⏳「正式接线图待 hardware_design.md §2.4 LED / 喇叭 / 外壳定型 + 实物到货后绘制」（line 62）— **2 文件互相等对方落地**
- **建议改法**：hardware_design.md §2.4 把具体 GPIO pin 数字落下来（即使是 🟡 CC 假设），ROLLCALL_DEVICE_DESIGN_LOG §2 引用 hardware_design.md 章节。一处真值。
- **跨会话**：实物到货后接线漂的风险源 — 现在 2 文件都说「等对方」。
- **严重程度**：🟡

### [B-036] 🟢 模块选型（PN532 V3 / NTAG215 / ST25DV16K）— hardware_design.md 跟 spec / 字典对齐

- **文件**：`02_design/hardware_design.md §2.2 / §2.3 / §3` + `01_specs/rollcall/DEVICE_REGISTRY.md §3` + 字典
- **描述**：PN532 V3 选型在 hardware §2.2 + ROLLCALL_DEVICE_DESIGN_LOG §1.1（line 38） + DEVICE_REGISTRY §3.1 都引用 = 一致。NTAG215 在 hardware §3 + FIELD_REGISTRY §2.2 `card_uid`（NTAG215 UID 7 bytes）一致。ST25DV16K 在 hardware §2.3 + ROLLCALL_DEVICE_DESIGN_LOG §10-D2 都引用 = 一致。
- **严重程度**：🟢

### [B-037] 🟢 src/main.py 是骨架占位 — 不漂

- **文件**：`03_dev/rollcall_device/src/main.py:1-10`
- **描述**：实际代码 10 行只是 docstring + 占位注释「实装时填充」，没有任何硬件引用。无漂的可能。
- **严重程度**：🟢

### [B-038] 🟡 BOM 列零件代码没用 — 部分对齐失败

- **文件**：`02_design/hardware_design.md §4.2` BOM
- **描述**：
  - §4.2 line 297-307 列了 9 类零件（Pi 3A+ ×3 / micro-USB 电源 ×3 / microSD ×3 / 外壳 ×3 / PN532 ×3 / ST25DV ×3 / NTAG215 ×110 / 杜邦线杂费 / 运费）。
  - **缺**：LED 模块（§2.4.1 拍板 ¥10.9 套装但 BOM 没列）/ 01Studio USB 小音响（§2.4.2 ¥29 但 BOM 没列）/ SYB-170 面包板（§2.5 ¥1.59 但 BOM 没列）/ 杜邦线母对母 40P（§2.5 ¥1.98 但 BOM 没列）/ Pi 3A+ 风扇盖（§2.4.3 ¥24 总但 BOM 没列）
  - 即 §2.4 + §2.5 5-08 加的零件**没回填到 §4.2 BOM 表**
- **建议改法**：§4.2 BOM 表加 5 行（LED 套装 / USB 小音响 / 面包板 / 杜邦线 / 外壳+风扇套装），合计也要更新（当前 ¥1345 RMB 不含这些）。
- **跨会话**：5-08 §2.4/§2.5 拍板没联动到 §4.2 BOM = `system_features.md` 或上线采购清单可能漂。
- **严重程度**：🟡

### [B-039] 🟡 hardware_design.md §0 状态表 §2.4 说「✅ 定稿」但 §4.4 又写「Demo 阶段砍 LED」自相矛盾

- **文件**：`02_design/hardware_design.md:20` + `:316`
- **描述**：
  - §0 line 20「§2.4 LED / 喇叭 / 外壳 ✅ 定稿（2026-05-08 itsuki 复核 + CC 查证）」
  - §4.4 line 315-318「**4.4 反馈设备（Demo 阶段砍）**」 — line 316「~~LED（绿/红）~~ Demo 阶段砍：用 Web 端实时显示 + 点呼机屏幕日志代替」
  - §4.4 line 320 还有第二个 §4.4 标题「4.4 Android App 签名证书（keystore）存储方案」 — **标题重号** + 第一个 §4.4 已废（demo 阶段砍 → 但 §2.4 5-08 已重新选型 LED 模块）
- **建议改法**：
  - 删第一个 §4.4（line 315-318）— 因为 demo 阶段已过，5-08 已重新选型
  - 第二个 §4.4 改成 §4.5
- **跨会话**：§0 状态表 vs §4 采购清单 vs §2.4 选型 三处不一致。
- **严重程度**：🟡

### [B-040] 🟢 ROLLCALL_DEVICE_DESIGN_LOG §10-D1~D6 跟 TODO §🛰️ D1-D6 — 完全对齐

- **文件**：`03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md:213-220` vs `00_admin/TODO.md:212-217`
- **描述**：6 个待 itsuki 拍板的决策点（D1 PN532 库 / D2 ST25DV 驱动 / D3 TTS / D4 SPI vs I2C / D5 WebSocket / D6 设备认证）2 文件描述完全对齐。
- **严重程度**：🟢

### [B-041] 🟢 ROLLCALL_DEVICE_DESIGN_LOG §1.2 启动前提 跟 hardware_design.md 一致

- **文件**：`ROLLCALL_DEVICE_DESIGN_LOG.md:51-54`
- **描述**：「Pi 3A+ + PN532 V3 + ST25DV16K × 2 + LED 模块 + USB 小音响 + NTAG215 × 50 配件已确认（2026-05-08 itsuki 复核）」— 跟 hardware §2 选型全对齐。
- **严重程度**：🟢

---

## 总计

| 严重 | 数量 | 占比 |
|---|---|---|
| 🔴 | 11 | 27% |
| 🟡 | 17 | 41% |
| 🟢 | 13 | 32% |
| **总** | **41** | 100% |

### 各维度分布

| 维度 | 🔴 | 🟡 | 🟢 | 小计 |
|---|---|---|---|---|
| 维度 10 TODO 真值 | 4 | 3 | 3 | 10 |
| 维度 8 memory 索引 | 3 | 4 | 3 | 10 |
| 维度 9 挂钩系统 | 1 | 3 | 2 | 6 |
| 维度 6 规格主体 | 2 | 3 | 3 | 8 |
| 维度 7 硬件 vs 点呼机 | 0 | 4 | 3 | 7 |
| **总** | **10** | **17** | **14** | **41** |

> 注：上面分布表的「13」改成「14」对齐子项（自检发现）；总数 41 个。

### 关键发现 — 3 条最该立刻动的

1. **[B-013] CLAUDE.md line 205 路径漂 `-Users-itsuki-dev-DMSD/`** — 影响所有会话每次启动，假路径，每次都要 CC 重新猜真路径。一行修，立刻见效。
2. **[B-021] `bin/check_overview_drift.sh` awk bug 确认** — 拍板的「C 方案 B 部分」核心机制有 bug，每次会话启动都报伪差异（.claude/ 写 23 / 实际 9，bin/ 写 3 / 实际 2）。awk 正则限定到 §0.1 体量表 + 区分 staged/committed 可修。
3. **[B-027]+[B-028] spec 主体 Phase 1/2 + effective_* 概念过期** — 2026-04-19 G2 决策 + 2026-04-29 不平移决策已推翻，spec 主体多处仍用旧表述。影响 5 端实装的对齐基准。

### 没审到的（time-box 边界）

- 维度 8 memory 内容矛盾 — 抽样 4/26+ 文件没找到，剩 22+ 未扫
- 维度 6 spec 主体 §6-11 + 附录 B 跟字典三件套**完整**字段对齐 — 抽样了关键段，没全扫
- `hooks/lib/sync-rules.sh` 466 行规则跟实际触发文件路径**逐条**对齐 — 只 grep + 抽样
- WIP.md 没审 — 主要被 [B-008] 抓到铁律违反，没逐条核 5 个会话条目

---

**END of session_B_findings**

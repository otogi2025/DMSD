# Fix-Bot 2 — 01_specs/ + 02_design/ 修复记录

生成于：2026-05-21（B 子代理 — 规格与设计文档修复，与 Fix-Bot 1 / Fix-Bot 3 并行）

> **范围**：B-027 / B-028 / B-029 / B-030 / B-031 / B-035 / B-038 / B-039 / C-010（合并 B-027）/ C-011 / C-020 / C-022
>
> **硬约束遵守**：不 commit / 不 push / 不动 03_dev/ 与 00_admin/ / 不动 flow_design.md:71（主会话已修）/ 不动主会话保留 A-010 A-028 / 大改前已备份。

---

## ✅ 已修

### B-027 + C-010：spec 主体 Phase 1 / Phase 2 全面替换（最大改动）

**文件**：`01_specs/rollcall/RollCall_Spec.md`

**改动**：
1. **顶部副标题**：标题去 v0.1 后缀（同 C-020 合并）→ `# RollCall Spec（点呼仕様）`；副标题加版本流叙事 + 加「上线姿态（2026-04-19 G2 决策）」段 — 明确 v1.0 一次上线 A 卡 / B iOS / C Android，不再分 Phase 1/2。
2. **§1 概述「双路径并存」→「三路径并存」**：表里新增「路径 C — Android App Link」一行；流程描述「路径 A 或路径 B」→「路径 A / B / C 任一」；「Phase 1 防代签关键人防补偿」→「永久人防补偿」。
3. **§5.1.1 标题**：「路径 A — NFC 卡（Phase 1 主推）」→「路径 A — NFC 卡」。
4. **§5.1.2 标题**：「路径 B — iPhone 静态标签（Phase 2 追加）」→「路径 B — iOS Universal Link（与路径 A 共存，v1.0 同时上线）」+ 顶部注：路径 C Android App Link 实现同型，复用 `path_type=B`。
5. **§5.1.3 标题**：「防代签（Phase 1 关键人防补偿）」→「防代签（永久人防补偿）」+ 正文「Phase 1 硬约束」→「永久硬约束」+「Phase 2 路径 B」→「路径 B / C」。
6. **§9 组件表**：「学生 iPhone App（路径 B / Phase 2）」改成两行 — 「学生 iOS App（路径 B）」+ 新增「学生 Android App（路径 C）」明确实现同型 `path_type=B` 复用；「老师本人（人防）」段去 Phase 1 字样 → 「永久硬约束」。
7. **附录 A.1**：「Phase 1 与 spec 的脱节」改写为「早期 spec 与上线姿态的脱节（历史，已 4-19 G2 + 4-17 v0.2 双重解决）」，正文重写澄清这是 4-12 临时方案被 4-17 / 4-19 双重收口。
8. **附录 A.7**：「Phase 2 路径 B 设计」→「路径 B 设计」。
9. **附录 B 顶部排序说明**：「🔴 Phase 1 开工前必须解决」→「🔴 v1.0 开工前必须解决」。
10. **附录 B.1 建议段**：「Phase 1 NFC 卡方案靠老师监督」→「路径 A NFC 卡方案靠老师监督（永久硬约束）」+「Phase 2 加 iPhone」→「路径 B / C」。
11. **附录 B.2-B.18 散落改动**：「Phase 1 影响」「Phase 1 用 NFC 卡」「Phase 2 用 App」「Phase 1 没有学生 App」「Phase 1 点呼机断网」「Phase 1 / Phase 2 重试逻辑」全部改成「路径 A / 路径 B / 路径 C」表述；「Phase 1 开工前定」→「v1.0 开工前定」。
12. **附录 D 收口表**：A.1 / B.1 / B.11 三行文本去掉「Phase 1 / Phase 2」措辞，改成「早期 vs 上线姿态脱节（历史问题）」/「永久硬约束」/「无 App 学生」。

---

### B-028：spec §7 + §10 effective_* 概念解决

**文件**：`01_specs/rollcall/RollCall_Spec.md`

**选 (b) 保留字段名**（迁移成本低，符合建议）：
- §7 顶部「判定时使用 effective_*（已考虑老师提前开始的窗口平移）」改为说明：「**2026-04-29 修订**：因 §5.4 改为窗口固定（不平移），`effective_*` 现在恒等于 `scheduled_*`。字段命名保留是为了数据模型字段稳定（未来若再引入平移规则可不动 schema）」。
- §10.1 `effective_window_start_at` 字段说明：「老师提前开始后平移过的实际判定区间」→「实际判定区间。**2026-04-29 修订**：因 §5.4 不平移，当前 `effective_* = scheduled_*`（字段名保留以备未来扩展）」。
- §10.4 字段一致性约束：「判定使用 effective_*，结算使用 effective_auto_end_at」→ 加注「（=scheduled_*，§5.4 不平移）」。

---

### B-029：ENUM_REGISTRY §13 path_type 扩展性说明 vs 4-19 G2 一致

**文件**：`01_specs/rollcall/ENUM_REGISTRY.md`

**改动**：path_type 扩展性说明段重写：
- B 描述：「iPhone 路径」→「手机路径：iPhone / Android 读静态标签 → 手机自己发后端」
- 扩展性说明：明确 v1.0 范围 A/B 两值，Android 实现同型复用 path_type=B（NDEF 被动读 + 本机签名 + 自发后端）；未来若引入 Android HCE 主动上报路径新增 `C`，TODO §🛠️ 暂留 C 占位不实装。

---

### B-030：DEVICE_REGISTRY §3.1 物理形态过期

**文件**：`01_specs/rollcall/DEVICE_REGISTRY.md`

**改动**：`card_reader` 物理形态描述：「树莓派（Pi Zero 2 W / Pi 4B 等）+ PN532 NFC 模块 + 扬声器」→「Raspberry Pi 3A+ + PN532 V3 NFC 模块 + 01Studio USB 小音响（详见 `02_design/hardware_design.md §2`）」— 跟 4-21 拍板 Pi 3A+ + 5-08 模块定稿对齐。

---

### B-031：DEVICE_REGISTRY §6 部署位置候选码

**文件**：`01_specs/rollcall/DEVICE_REGISTRY.md`

**改动**：候选清单从 4 个减到 3 个（3 寮已废止），按寮号编号避免跟 `path_type` A/B 撞字：
- `dorm-A-01 / dorm-B-01 / dorm-C-01 / dorm-D-01` → `dorm-1-01 / dorm-2-01 / dorm-4-01`
- 加注：3 寮已废止 — 候选清单不列。如果未来重启 3 寮，再补 `dorm-3-01`。
- §6 标题：「4 台部署」→「多台部署（Q1 拍板：3 寮使用 = 1 寮男 / 2 寮男 / 4 寮女；3 寮废止）」。

---

### B-035：hardware_design.md §2.4.1 LED 落具体 GPIO pin 数字

**文件**：`02_design/hardware_design.md`

**改动**：§2.4.1 LED 接 Pi 行：「GPIO 数字输出（每色一个 GPIO 引脚 + 共地）」→「**红 = GPIO 17 / 绿 = GPIO 27 / 蓝 = GPIO 22 / 白 = GPIO 23** + 共地（pin 6 / pin 9 任一 GND）」。
- 注脚解释：从 ROLLCALL_DEVICE_DESIGN_LOG §2 已写的初步分配（红 17 / 绿 27 / 蓝 22）落到本文档作单一真值；白色 = GPIO 23（不冲突 PN532 SPI 占的 8/9/10/11 + ST25DV I2C 占的 2/3）。
- §2.4.2 喇叭接 Pi 行：「USB 2.0 + 3.5mm 音频口」→「USB 2.0 任一空闲口 + Pi 3A+ 内置 3.5mm 模拟音频口」更明确接口位置。

> 注：ROLLCALL_DEVICE_DESIGN_LOG 端改引用 hardware_design 章节，归 Fix-Bot 1 处理（已在 prompt 提到）。

---

### B-038：hardware_design.md §4.2 BOM 表加 5 行

**文件**：`02_design/hardware_design.md`

**改动**：§4.2 部署扩容 BOM 表：
- 顶部加注「2026-05-21 修订（B-038 修复）」说明
- 新增 5 行：LED 模块 5 色套装 ¥11×3 / 01Studio USB 小音响 ¥29×3 / SYB-170 面包板 ¥2×3 / 杜邦线母对母 40P ¥2×3 / Pi 3A+ 透明外壳 + 风扇盖 ¥24×3（原 Pi 3A+ 外壳改成"透明外壳 + 风扇盖"）
- PN532 NFC 单价从 ¥30 改成 ¥27（贴 §2.2 定稿 ¥26.7）
- 杂费从 ¥50 砍到 ¥30（避免重复）
- 合计 ¥1345 → ¥1475 RMB

---

### B-039：hardware_design.md §4.4 标题重号 + 砍过期段

**文件**：`02_design/hardware_design.md`

**改动**：
- 第一个 §4.4「反馈设备（Demo 阶段砍）」改成 `~~反馈设备（Demo 阶段砍）~~（已废 — 2026-05-08 §2.4 重新选型）` + 注「采购口径以 §4.2 BOM + §2.4 为准。本段保留作历史记录」— 不删，保留原 demo 阶段决策痕迹但明确已被推翻。
- 第二个 §4.4「Android App 签名证书 keystore」改成 §4.5（消除重号）。

> §0 状态表 §4.4 行未改 — 已写「🔴 Demo 阶段全部推翻 / 部署扩容仍按原计划」语义上符合现状，不需要变。

---

### C-010：合并到 B-027 已处理

`01_specs/rollcall/RollCall_Spec.md` 上面所有 Phase 1/2 替换已覆盖 C-010 描述的全部行（line 17-18, 26, 182, 203, 233, 460, 466, 586-590, 653-665, 678-679, 693, 706）。

---

### C-011：system_features.md 跨 repo 同步规则全删

**文件**：`02_design/system_features.md`

**改动**：
- §1.1「为什么有这份文档」段改写：从 2 端布局（iOS 独立 repo / Web demo+v1）→ 5 端布局（iOS / Android / Web / 后端 / 点呼机 全在 DMSD 内 v1/ 下）。
- §1.2「跨会话同步规则」表全部重写：删除 `bin/sync-ios-refs.sh` / `Tomoshibi-iOS/STATUS.md` 反向同步等独立 repo 规则；新增 Android、点呼机两端的同步动作；加历史注脚（2026-05-06 退役独立 repo 落地引用 `99_archive/2026-05-06_cloud_agent_退役/`）。
- §1.3「sync-ios-refs.sh 的作用」整段删除（脚本已退役）。

---

### C-020：RollCall_Spec.md 标题去 v0.1 后缀 + 副标题版本流叙事

**文件**：`01_specs/rollcall/RollCall_Spec.md`

合并到 B-027 第 1 项一起处理。标题 `# RollCall Spec v0.1（点呼仕様）` → `# RollCall Spec（点呼仕様）`；副标题加版本流：v0.1 (2026-02-12 初版) → v0.2 (2026-04-17 主体改写) → 当前 = spec 主体 + 4-17 决策 + 4-29 38 条增量。

---

### C-022：system_features.md 顶部时间戳过时

**文件**：`02_design/system_features.md`

**改动**：顶部「最后更新: 2026-05-03」→「最后更新: 2026-05-21 — 加最近改动概要」+ 一句版本流概要（注册码 iOS/Android 实装 / 老师公告 4 端实装 / 字段对齐多轮 / 点呼机第 5 端加入）。

---

## ⏳ 待 itsuki 拍板

无 — 本批 12 条 finding 均按建议改法落地。

## ❌ 跳过

| Finding | 原因 |
|---|---|
| A-010 / A-028 | 主会话保留（v1.0 决策性 — NFC ECDSA 实装）|
| B-027 中 `flow_design.md:71` Pi 4B → Pi 3A+ | 主会话已修，本 Bot 不重复 |
| ROLLCALL_DEVICE_DESIGN_LOG 引用 hardware_design § GPIO 章节 | 03_dev/ 范围 — 归 Fix-Bot 1 |
| 03_dev/student_*/DESIGN_LOG.md 跨 repo 字段 | 03_dev/ 范围 — 归 Fix-Bot 1（C-012 不在本 Bot 范围）|

## 文件改动统计

| 文件 | 改动段数 | 性质 |
|---|---|---|
| `01_specs/rollcall/RollCall_Spec.md` | 19 段 | spec 主体 Phase 1/2 全替换 + effective_* + 标题去 v0.1 |
| `01_specs/rollcall/ENUM_REGISTRY.md` | 1 段 | path_type §13 v1.0 vs 未来扩展明确 |
| `01_specs/rollcall/DEVICE_REGISTRY.md` | 2 段 | §3.1 物理形态 + §6 部署位置候选码 |
| `02_design/hardware_design.md` | 4 段 | §2.4.1 GPIO + §2.4.2 接口 + §4.2 BOM + §4.4 重号砍 |
| `02_design/system_features.md` | 3 段 | 顶部时间戳 + §1.1 5 端布局 + §1.2 跨端同步规则重写（§1.3 删）|

**总计**：5 个文件 / 29 处段落改动。

## 备份位置

`99_archive/2026-05-21_pre_fix/` 含 5 个文件的修改前快照（RollCall_Spec.md / ENUM_REGISTRY.md / DEVICE_REGISTRY.md / hardware_design.md / system_features.md）。

## hook 提醒说明

整批改动过程中 PostToolUse hook 频繁触发：
- `post-edit-project-overview-check.sh` — RollCall_Spec / ENUM_REGISTRY / DEVICE_REGISTRY 因 project-overview 行体量数字未变而报「路径找不到」（脚本误报，文件路径其实在），需 Bot 3 联动 project-overview 表行数刷一遍才能消。
- `post-edit-sync-check.sh` — system_features 改动触发 5 端 DESIGN_LOG 联动提醒（属 Fix-Bot 1 范围，本 Bot 不动）。
- `post-edit-version-hardcode-check.sh` — RollCall_Spec 顶部 + hardware_design BOM 含版本号，提示已确认无硬编码 bump。

未触发实质错误。本 Bot 不修 hook 自身（B-021 awk bug 等归 Bot 3）。

# 当前工作状态 (Work In Progress)

> **这个文件是给 Claude Code 看的。**
>
> - **会话开始时**: 先读这个文件,知道"做到哪了、谁在做什么、哪些文件我不能碰"
> - **会话结束前**: 更新这个文件(移任务状态、登记完成、更新时间戳)
> - **多个会话并行时**: 通过这个文件互相协调,避免冲突
>
> 和其他文件的区别:
> - `progress_overview.md` = 长期章节目录(稳定,每次会话结束更新一次)
> - `TODO.md` = itsuki 自己的完整待办清单(所有该做没做的事)
> - 本文件(WIP.md) = 当下的书签 + 多会话协调(谁占用哪些文件,避免冲突)

---

**最后更新**: 2026-04-17 18:09 by [Mac-主会话 (CC-Opus-4.7)]
**当前总版本**: v0.3.0（AC 入试记录指南：v3.1） — v0.2 修订进行中

---

## 🎯 当前焦点

**Phase 1 + Phase 2 的架构设计基本完成**(2026-04-15 会话),现在进入硬件型号收尾 + 文档补完阶段。

**架构层已确定**:
- **核心原则**: 点呼机只搬运数据,业务判断全在后端(thin client / thick server)
- **Phase 1(卡方案)**: 卡 → 点呼机(读 UID)→ 后端(查表 + 判断)→ 返回姓名 → 点呼机播报
- **Phase 2(加 iPhone,卡仍保留)**: iPhone 读点呼机外贴的静态 NFC 标签拿到 device_id → iPhone 自己通过 WiFi/4G 发 `{student_id, device_id, ts, 签名}` 给后端 → 后端判断 → 通过 WebSocket 推回点呼机播报。**不走"手机伪装 NFC 卡"路径**(iOS 第三方 App 无 Secure Element 权限)。
- **硬件大脑方向**: A(Raspberry Pi),经重新对比 ESP32 后再次确认。

**剩下的硬件收尾**:
1. 宿舍点呼位置网络情况(itsuki 要去问老师)—— 影响最终型号
2. 型号最终选择:Pi Zero 2 W (¥100 RMB) vs Pi 4 2GB (¥300 RMB) vs 其他 —— 认知更新后已不需要 4GB 高配

**新发现的项目债**:
- v0.1 spec **完全没写点呼机契约**(spec 冻结于 2026-02-12,NFC 硬件是 4-12 才加的设计)—— 要补一份设备端 API 契约文档
- Android 版 Phase 2 方案还没细化(HCE 机制和 iOS 不同)

**下一个大动作**: 补点呼机 spec → 硬件收尾型号定 → 采购 → Phase 1 代码(后端骨架 + 点呼机读卡)。

**4-17 18:00 启动**: itsuki 二轮审查发现 7 个结构性问题（CHANGELOG 名不副实 / spec 主体 Phase 视角错 / 4 台是幽灵 / device_id 裸字段 / progress_overview 过时等），拍板 5 个硬决策（Q1 `exempt_range` = base / Q2 spec 主体改写双路径 / Q3 = **4 台** / Q4 物理布局 TBD / Q5 = revert 到 v0.1.1）。spec 修订工作分 3 个 commit 推进（详见下面"进行中任务 A"）。

---

## 🔄 进行中的任务

### 任务 A: RollCall v0.1 spec 修订（来自 2026-04-17 二轮审查）

- **认领者**: [Mac-主会话 (CC-Opus-4.7)]
- **开始时间**: 2026-04-17 18:00
- **为什么做**: 4-17 itsuki 二轮审查发现 16 项文档/字典内部冲突 + 5 个外人视角担忧（详见 raw/2026-04-17.md 17:56 dump）；之前 25 项漏洞 + 这些都要系统性修订
- **涉及的文件/目录**（其他会话不要动）:
  - `01_specs/rollcall/RollCall_Spec_v0.1.md`
  - `01_specs/rollcall/FIELD_REGISTRY_v0.1.md`
  - `01_specs/rollcall/ENUM_REGISTRY_v0.1.md`
  - `01_specs/rollcall/ERROR_CODES_v0.1.md`
  - `01_specs/rollcall/DEVICE_REGISTRY_v0.1.md`（新建）
  - `CHANGELOG.md`
  - `CLAUDE.md`
  - `WIP.md`
  - `00_admin/progress_overview.md`
- **执行计划（3 commit）**:
  - **commit 1（元数据）**: CHANGELOG 0.2.0→0.1.1 + CLAUDE.md "规格 v0.2" 措辞修正 + raw dump + WIP 更新 ← **进行中**
  - **commit 2（spec 修订）**: RollCall_Spec 主体 rewrite (双路径) + ENUM/FIELD 修 + ERROR_CODES 补 + DEVICE_REGISTRY 新建
  - **commit 3（硬件落实）**: spec §3.2 A/B → A/B/C/D + progress_overview 起草更新
- **已完成**:
  - [x] CHANGELOG.md revert 0.2.0 → 0.1.1（commit `8706fed`）
  - [x] CLAUDE.md "规格 v0.2 已更新" 措辞修正
  - [x] WIP.md 顶部 + 焦点 + 进行中任务更新
  - [x] raw/2026-04-17.md 18:00 dump 追加
  - [x] **commit 1 已 push 准备**（`8706fed` — 7 files / +1220 / -34）
- **当前停在**: 进入 commit 2（spec 主体 rewrite + 字典三件套修订 + DEVICE_REGISTRY 新建）
- **下一步**: 重写 RollCall_Spec_v0.1.md 主体为双路径并存 + 修字典 + 补错误码 + 新建 DEVICE_REGISTRY

---

## ✅ 最近完成(24-48 小时内)

### 2026-04-17

- **[Mac-主会话]** 把 `RollCall_Spec_v0.1.pages` 数字化为 Markdown（`01_specs/rollcall/RollCall_Spec_v0.1.md`），顺便反向审查 spec 漏洞 7+18=**25 项**（附录 A + B，5 项 🔴 为 Phase 1 阻塞项）
- **[Mac-主会话]** **iCloud AC 目录结构大重构**：两个冗余 "筑波大学 AC入試 準備" 合并；按编号分类（00_指南 / 01_官网资料 / 02_分析与调研 / 03_素材_候选 / 04_素材_成品 / 05_产出 / 99_archive）；扁平版过期文件进 `99_archive/_deprecated_4-14扁平版snapshot/`（建议 4-24 前眼检后删）
- **[Mac-主会话]** **AC 素材第 2 层首次批量填充**：CC 经 itsuki 明确授权，从 `05_logs/raw/` 5 个历史文件挑出 10 条候选 + 候选索引，搬进 iCloud `03_素材_候选/`（常规流程仍是 itsuki 月度做）
- **[Mac-主会话]** **CC 权限边界更新**（`DMSD/CLAUDE.md`）：CC 可读 iCloud AC 目录；写 03/04 需当场授权；永不写 05_产出
- **[Mac-主会话]** **AC 入试记录指南 v3.0 → v3.1**：§1 目录图、§11 起步清单修订为当前真实状态（版本号 bump = AC 记录触发）
- **[Mac-主会话]** 清理 `iCloud/04_Dev/Projects/AC_DMSD/` 老镜像：提取 8 个早期 .pages/.pdf 到 `99_archive/早期手写材料/`，镜像壳标 `_deprecated_AC_DMSD_旧镜像_至2026-04-24`

### 2026-04-15

- **[Mac-主会话]** 重新打开 A(RPi)/B(ESP32) 全维度对比,确认方向 A;推翻 4-12 "已决定 RPi" 的伪决策
- **[Mac-主会话]** 确立核心架构原则:"点呼机只搬运数据,业务判断全在后端"(由 itsuki 主动提出,反驳 AI 的过度配置建议)
- **[Mac-主会话]** 识别 iOS 平台第三方 App 无 NFC HCE / Secure Element 权限的根本限制;学习 Apple Pay 背后机制
- **[Mac-主会话]** 推翻 "手机发 UID 和卡统一" 的初期设计,重设 Phase 2 为双路径共存(卡走 RFID,iPhone 读静态贴纸 + 自己联网发后端,后端 WS 推回点呼机播报)
- **[Mac-主会话]** 发现 spec gap:v0.1 spec 完全没写点呼机契约,记入项目债

### 2026-04-13

- **[Mac-主会话]** 版本号体系重置 v1.0 → v0.1 (commit `3b01345`)
- **[Mac-主会话]** 建立 AC 入試完整记录体系 (commit `e637034`)
- **[Mac-主会话]** 目录结构整理 + 历史内容抢救 (commit `e346dca`)
- **[Mac-主会话]** 2026-04-12 NFC 方案设计日 dev_log (commit `43c73ec`)
- **[Mac-主会话]** 添加 WIP.md 会话状态文档 + CLAUDE.md 新会话读取指令 (commit `91a4294`)
- **[Mac-主会话]** 建立 ac_入試准备/ 子文件夹 + 提升"边做边学"到方法论层 (commit `d89b435`)
- **[Mac-主会话]** 归档 NFC/NFD 鬼影文件到 99_archive/ (commit `666faf8`)
- **[Mac-主会话]** 保存 2025-12 早期 NFC 系统设计对话为 raw 素材(~3100 行,待后续整理)

### 2026-04-12

- **[Mac-会话]** NFC 架构决策(Raspberry Pi + 分阶段 + 播报防作弊)
- **[Mac-会话]** 更新 executable_dev_checklist_v0.1

### 2026-04-10

- **[Mac-会话]** 解决 NFC/NFD git pull 失败
- **[Mac-会话]** 建立 AI 协作机制 + 一个月空白反思

---

## 📋 开放任务

**完整待办清单已迁移到 `00_admin/TODO.md`**(itsuki 自己维护的主清单)。

本文件只保留 **多会话协调相关** 的任务信息——即:有文件边界冲突风险、需要认领的任务。

查看所有待办 → `00_admin/TODO.md`

### 📌 需要会话认领的任务(有文件边界风险)

*(当前无。将来当多个会话同时开工时,从 TODO.md 拉任务到这里并标注认领者+涉及文件。)*

---

## 🚧 阻塞项

*(当前无阻塞项)*

---

## 🔒 多会话协调规则

### 会话认领流程

1. **开始任务前**: 把任务从 "开放任务" 移到 "进行中",登记认领者和开始时间
2. **做的过程中**: 更新 "已完成" 子列表 + "当前停在"
3. **完成后**: 把任务移到 "最近完成",写上 commit hash(如有)
4. **放弃 / 暂停时**: 把任务写清楚停在哪,移回 "开放任务" 或保留在 "进行中" 标注为暂停

### 会话标识(建议命名)

用 `[设备-主题]` 格式,例如:
- `[Mac-主会话]` — Mac 上的主会话
- `[Mac-后端]` — Mac 上专门做后端的
- `[Mac-设备]` — Mac 上专门做 Raspberry Pi 代码
- `[VPS-后端]` — VPS 上的后端会话
- `[iPad-文档]` — iPad 上做文档整理

### 避免冲突的硬规则

1. **每个"进行中"任务必须标出"涉及的文件/目录"**
2. **其他会话不能动正在被认领的文件**
3. **共享文件**(大家都会改的,如 `CLAUDE.md`, `WIP.md`, `progress_overview.md`, `CHANGELOG.md`): 一次只能有一个会话修改,改完立刻 commit + push
4. **改 `WIP.md` 本身时**: 先 pull,改完立刻 push,避免和其他会话撞
5. **git conflict 了怎么办**: 停下来,先问 itsuki,不要自己猜合并

### 关键文件边界(将来会用到)

| 目录 | 归谁管 |
|------|-------|
| `03_dev/backend/` | 后端会话 |
| `03_dev/device/` | 设备会话(Raspberry Pi) |
| `03_dev/Student_iOS_new/` | iOS 会话 |
| `03_dev/teacher_web/` | 老师端会话 |
| `01_specs/` | 一次只允许一个会话改(规格冻结区) |
| `00_admin/` | 主会话管理 |
| `05_logs/dev_log/` | 各会话写自己今天的,文件名不撞就好 |
| `05_logs/raw/` | 同上 |

---

## 📝 给新会话的上下文(关键信息)

新会话读完 `CLAUDE.md` 和本文件应该知道:

1. **当前版本**: v0.3.0（v0.2 修订进行中） — 项目还在规格和设计阶段,未开始写代码。CHANGELOG 已于 4-17 晚重建为细粒度（pre-0.1 追认 6 条 + 2-02 至今每个实质节点一条）
2. **分阶段策略**: Phase 1 = NFC 卡 + 后端 + Raspberry Pi 点呼机(不需要学生 App)|  Phase 2 = 加手机 App
3. **防作弊核心**: 语音播报(原创设计,详见 `05_logs/decision_log.md`)
4. **版本体系**: 0.x.x = 开发中,1.0.0 = 宿舍正式上线
5. **记录体系**: CC 侧见 `00_admin/CLAUDE_CODE_记录指南.md`；方法论总章（`AC入试记录指南_v3.md`）在 iCloud，CC 不读
6. **文件地图**: `00_admin/目录架构.md`
7. **itsuki 的偏好**: 给选项用 A/B/C 不用甲乙丙;决策她拍板;不盲从 AI

---

## 🕘 更新日志(本文件自己的)

- 2026-04-13 17:30 — [Mac-主会话] 初次创建 WIP.md
- 2026-04-13 晚 — [Mac-主会话] 开放任务迁移到 `TODO.md`;WIP 聚焦多会话协调;更新当前焦点(NFC 硬件选型中)
- 2026-04-13 深夜 — [Mac-主会话] 补充今天的完成清单(commit 91a4294/d89b435/666faf8 + 2025-12 raw)
- 2026-04-15 晚 — [Mac-主会话] 刷新当前焦点(Phase 1+2 架构敲定,进入硬件收尾+spec 补完阶段);登记 4-15 完成清单;记入两项新项目债(点呼机 spec、Android Phase 2 方案)
- 2026-04-17 18:00 — [Mac-主会话] 启动 RollCall v0.1 spec 修订(3 commit 计划);版本号 v0.3.0 revert 到 v0.1.1 patch（命名整理而已，spec 内容未变）;新增"进行中任务 A"
- 2026-04-17 18:09 — [Mac-主会话] CHANGELOG 细粒度重建：pre-0.1 追认 6 条 2025-12 方案级迭代（HCE→tag→SDM/SUN→v2→v2.1→v2.1加固版，来源 itsuki 贴出的早期 ChatGPT log）+ 2-02 至今每个实质节点一条 patch，当前 = v0.3.0

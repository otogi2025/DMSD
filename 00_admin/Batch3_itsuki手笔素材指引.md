# Batch 3 — itsuki 手笔区素材指引

> **这是什么**：按 CLAUDE.md §AC 记录协作 → 目录边界 规则，`decision_log.md` / `project_evolution.md` / `learning_path.md` 是 **itsuki 手笔区，CC 不动正文**。本文件是 CC 整理的"**ready-to-paste draft**"，itsuki 审完直接复制粘贴到对应文件即可。
>
> **对应 backlog 条目**：D1 / D2 / D3 / D4
>
> **CC 不做**：不 Edit / Write 以上三个文件的正文
> **CC 做了**：下面四节里的每一条都是按这三个文件的**现有格式**起的 draft，可**直接粘贴**
>
> **最后更新**: 2026-04-20
> **工作量**：itsuki 审 + 复制粘贴约 30-45 分钟

---

## 目录

- [§1 decision_log.md 新增 9 条（D2）](#1-decision_logmd-新增-9-条d2)
- [§2 project_evolution.md 新增 5 次转折（D1）](#2-project_evolutionmd-新增-5-次转折d1)
- [§3 learning_path.md Python Day 2 坦诚（D3）](#3-learning_pathmd-python-day-2-坦诚d3)
- [§4 learning_path.md PostgreSQL 选型补答（D4）](#4-learning_pathmd-postgresql-选型补答d4)

---

## §1 decision_log.md 新增 9 条（D2）

**粘贴位置**：`05_logs/decision_log.md` 最顶上的 `## 决策记录（倒序）` 下面、`## 2026-04-15 — 点呼机架构原则` 上面。**倒序排列 = 最新的在最上面**。

> **注**：以下 draft 的 "为什么改" 和 "影响" 部分 CC 已尽量写全，但**"事后回看"全部留 (几个月后补填)**，因为这本来就是 itsuki 将来补的。
>
> **有"[itsuki 补]"标注的地方 = CC 不确定的点，itsuki 粘贴前自己确认一下**。

---

### Draft 1（粘贴到 decision_log 顶部）

```markdown
## 2026-04-20 — 点呼机硬件型号最终拍板：Pi 4B 2GB × 4 台

**之前的决策**（4-15 遗留）: 方向 A（Raspberry Pi）确认，但具体型号留白 — Pi Zero 2 W (¥100) / Pi 4B 2GB (¥300) / Pi 4B 4GB (¥541) 三款候选
**新的决策**: Pi 4B 2GB × 4 台（¥1200 人民币 ≈ ¥24000 日元）
**为什么改**:
1. 4-20 追问"为什么要树莓派？" 澄清 thin client ≠ no client —— NFC 被动芯片必须有一个中间设备搬运数据，这个设备的存在由物理限制决定
2. Pi Zero 2 W GPIO 需要焊接 → 一个人开发学习成本高
3. Pi 4B 4GB 过度配置（点呼机只搬运数据，不需要大内存）
4. Pi 4B 2GB 是"刚好够用"的平衡点：Python 完整生态 / GPIO 直插不焊接 / 扬声器 + ST25DV 动态写入都跑得起
**影响**: 硬件采购可以定稿（配合 4-20 的 ST25DV16K × 4 一起下单）；4 台总硬件成本约 ¥24000 日元
**相关**: `05_logs/raw/2026-04-20.md §16:30`
**事后回看**: (几个月后补填)

---
```

### Draft 2

```markdown
## 2026-04-20 — 路径 B NFC 贴纸：静态 → 动态 ST25DV16K（应对 URL 复制漏洞）

**之前的决策**（4-15 设计）: 路径 B 用被动 NFC 标签，仅供 iPhone 读取拿 device_id；签名 + nonce 防代签在 App 端
**新的决策**: 改用**动态 NFC 标签 ST25DV16K**（I²C 可写入），点呼机每 10 秒通过 I²C 刷新贴纸里的 URL（含时效 10 秒的一次性 nonce）
**为什么改**:
1. 我发现漏洞：学生可以用 NFC Tools App 读真贴纸 → 拿到静态 URL 文本 → 复制到自己的空白 NTAG215 贴纸上 → 在宿舍房间 tap 假贴纸也能完成"签到"（App 依然走合法的签名 + nonce 流程，后端没法分辨）
2. 根因：**静态 URL 等于可复制的字符串，"知道 URL" ≠ "到场"**
3. 签名 + nonce 防御只能防跨设备代签，防不住同设备 + 假贴纸
4. AI 推荐的"A + C"组合（BSSID 校验 + 老师人防兜底）我没采纳——**我要设计上 100% 防死，不接受"防 90% 剩 10% 靠人兜底"**
**影响**:
- 贴纸从"完全被动"升级为"半主动"（贴纸内容由点呼机动态刷新）
- 点呼机代码多了"I²C 刷新 NDEF"的职责
- thin client 原则仍然成立——点呼机不做**业务判断**，只做"搬运 + 维护贴纸内容"
- 硬件采购加 ST25DV16K × 4 + Qwiic 转杜邦线 × 4（中国购买 ¥140 人民币 ≈ ¥2800 日元）
- spec §5.1.2 需要修订（记入 v0.4.0）
**相关**: `05_logs/raw/2026-04-20.md §15:30 + §16:00`
**事后回看**: (几个月后补填)

---
```

### Draft 3

```markdown
## 2026-04-20 — iPhone 路径技术方案：BTR + Universal Link + AASA（"碰一下就签到"）

**之前的决策**（spec v0.1 原定）: iPhone 走 Core NFC，用户打开 App → 按按钮 → tap（7 步）
**新的决策**: Background Tag Reading（BTR）+ Universal Link + AASA —— 学生拿出手机 tap 贴纸 → iOS 自动唤 DMSD App 到签到页（2 步）
**为什么改**:
1. 点呼时段短（拥堵时间 1-2 分钟过 ~120 人），前台读的 7 步 × 120 人 × 每天 2 场 = 1200 步/天的体验差
2. BTR 技术已成熟（iOS 11+），要求贴纸写 NDEF URL + App 配置 Associated Domains + 域名 HTTPS 托管 AASA 文件
3. 域名选项 A/B/C 里选 A（注册正式域名如 `dmsd.otogi2025.com`，一年几百日元），不选 B GitHub Pages（域名不美观）、不选 C Let's Encrypt 子域（复杂）
**影响**:
- 后端要绑正式 HTTPS 域名
- iPhone App 要实现 Universal Link handler
- iOS 老机型（7/8/X）BTR 只在锁屏触发，主屏不响应 → 需要学生培训 + App 主屏放"手动 tap"兜底按钮
- 低电量模式会禁用 BTR → fallback 必须有
**相关**: `05_logs/raw/2026-04-20.md §15:00`
**事后回看**: (几个月后补填)

---
```

### Draft 4

```markdown
## 2026-04-19 — 文档同步机制：单源真值 + 同步清单 + pre-commit hook（A+B+C 三件套）

**之前的决策**: 无（共享信息如版本号、目录结构散在多个文件里各自维护）
**新的决策**: 建立三层防漂移机制
- **A. 单源真值**: 每个共享概念只在一处存（版本号在 CHANGELOG；目录结构在 CLAUDE.md；5 AC 核心问题在 CLAUDE.md），其他文件用指针引用。详见 `00_admin/文档同步点清单.md`
- **B. CLAUDE.md 会话结束前 CC 扫描规则**: 声明性文件检查 + 时间戳新鲜度扫描 + 新同步点发现
- **C. git pre-commit hook**: 自动拦截声明性文件（CLAUDE.md / WIP / TODO / progress_overview）里的硬编码版本号，不一致拒绝 commit
**为什么改**:
1. 我发现迭代了几个版本后多个文件还写着过期版本号（"迭代到 v0.3 了但有些文件还写 v0.1 / v0.2 / 'v0.2 修订进行中'"）
2. 症状是"版本号漂移"，但病根是**"同一信息多处存储 → 必然漂移"**
3. CC 给 3 档方案（A / A+B / A+B+C），我选最彻底的 A+B+C —— 不想再出这类问题
**影响**:
- 6 条 backlog 条目一次性闭合（D22 / D23 / D24 / D25 / L11 + D19）
- 新机器 clone 后要跑 `bash 00_admin/hooks/install.sh` 一次（Mac / VPS 各跑）
- 以后任何新"声明性文件"要同步加进 `文档同步点清单.md` + hook 配置
**相关**: `05_logs/raw/2026-04-19.md §21:30`；`00_admin/2026-04-19_项目审查_backlog.md §M1`
**事后回看**: (几个月后补填)

---
```

### Draft 5

```markdown
## 2026-04-19 — G2 决策：取消 Phase 1 / Phase 2 分阶段，v1.0 一次上（iOS + Android + 卡）

**之前的决策**（4-12 原决定）: Phase 1 = 卡 + 后端（最快上线），Phase 2 = 加手机 App（iOS + Android）
**新的决策**: 取消分阶段，v1.0 直接 iOS + Android + 卡 完整版一次上线。开发内部按 M1→M5 里程碑推进（兜底：做不完至少 M1+M2 可 demo）
**为什么改**:
1. [itsuki 补：你当时的原话 / 直觉理由]
2. 分阶段的好处（Phase 1 最快上线）在实际 AC 进度下意义不大 —— 到 2027-04 有 12 个月，完整做比两阶段 churn 更高效
3. 三路径（卡 / iPhone / Android）从设计上就是共存的，没必要人为切分成两个 release
**影响**:
- CLAUDE.md 里 "Phase 1 / Phase 2" 表述统一替换为 "v1.0 完整版 + M1-M5 里程碑"
- 原 executable_dev_checklist 按 Phase 1 / 2 划分的任务表需要重新组织（按 M 划分）
- 兜底规则：时间不够时至少 M1（spec 闭环）+ M2（点呼机 + 后端基础）可做 demo
**相关**: `05_logs/raw/2026-04-19.md`（整份）；`00_admin/WIP.md §架构层（4-19 重大转向）`
**事后回看**: (几个月后补填)

---
```

### Draft 6

```markdown
## 2026-04-17 — spec 主体 rewrite（v0.3.0）：双路径并存 + thin client + 4 台协调 + 改判时限矩阵

**之前的决策**（2026-02-12 冻结的 v0.1）: spec 主体以"单设备 + 学生持手机 App" 为默认架构，双路径是附加分支
**新的决策**: spec 主体重写为"双路径并存"（路径 A 卡 / 路径 B 手机）作为架构核心；thin client 原则 / 4 台点呼机协调 / 改判时限矩阵等写入主体
**为什么改**:
1. 4-15 确立的"thin client"和"iOS 平台限制 → 双路径"是主体架构级别的事，spec 主体必须反映
2. v0.1 spec 没写点呼机契约（spec gap，4-15 发现），这次主体 rewrite 是还项目债
3. 主体 681 → 958 行（+277），附录 B 从 18 项扩到 25 项
**影响**:
- 项目版本 v0.1.3 → v0.3.0（minor bump，spec 范围实质扩大）
- 4 个字典（ENUM / FIELD / ERROR_CODES / DEVICE_REGISTRY）配合联动修订
- 附录 D 盘点：13 项 ✅ / 10 项 🔄 待拍（留 v0.4.0）
**相关**: `05_logs/raw/2026-04-17.md`；`CHANGELOG.md v0.3.0`
**事后回看**: (几个月后补填)

---
```

### Draft 7

```markdown
## 2026-04-17 — Q1-Q5 硬决策（spec 层 5 个长期悬置问题一次性拍板）

**之前的决策**: 无（5 个问题从 v0.1 开始悬置，每次遇到都绕开）
**新的决策**: 5 个一次性拍板
- **Q1**: `exempt_range`（免点呼时段）从 overlay 类型升为 base_status 类型 —— 免点呼是"基础状态"不是"叠加标记"
- **Q2**: [itsuki 补 —— 5 个 Q 具体内容可能要查 raw/2026-04-17.md]
- **Q3**: [itsuki 补]
- **Q4**: [itsuki 补]
- **Q5**: [itsuki 补]
**为什么改**:
1. 悬置越久，spec 主体越难 rewrite —— 这些 Q 是依赖链的底层
2. CC 在 spec rewrite 过程中把这 5 个 Q 并列提出，我一次性决策避免来回
**影响**: 字典三件套跟着改（overlay 分两类 / ENUM 新增 5 值 / FIELD 新增 6 字段 / ERROR_CODES 新增 5 码）
**相关**: `05_logs/raw/2026-04-17.md`；`01_specs/rollcall/RollCall_Spec_v0.1.md` 附录
**事后回看**: (几个月后补填)

---
```

### Draft 8

```markdown
## 2026-04-17 — 字典三件套（ENUM / FIELD / ERROR_CODES）+ DEVICE_REGISTRY 新建：单源真值架构

**之前的决策**: 枚举值、字段、错误码散在 spec 主体里重复定义
**新的决策**: 四个独立文件作为单源真值，spec 主体只引用不重复
- `ENUM_REGISTRY_v0.1.md` — 所有枚举值
- `FIELD_REGISTRY_v0.1.md` — 所有字段
- `ERROR_CODES_v0.1.md` — 所有错误码
- `DEVICE_REGISTRY_v0.1.md` — 点呼机设备台账（新建，对应 4 台点呼机协调）
**为什么改**:
1. 单源真值是防漂移的架构做法（相关：4-19 建立的 A+B+C 文档同步机制）
2. 代码开工时前后端直接引用字典，不用从 spec 主体挖
**影响**: 项目版本 v0.1.3 → v0.2.0（minor bump，新 spec 范围）
**相关**: `CHANGELOG.md v0.2.0`
**事后回看**: (几个月后补填)

---
```

### Draft 9

```markdown
## 2026-04-17 — base_status 从 overlay 升 base（spec 建模层重构，Q1 决策的落地）

**之前的决策**: `exempt_range`（免点呼时段）属于 overlay_badges（叠加标记）
**新的决策**: 升级为 base_status 的独立取值（和 present / absent / late 同级）
**为什么改**:
1. overlay 是"在 base 之上的装饰"，但 exempt_range 改变的是"系统对这个时段的判定逻辑"，不是装饰
2. 建模上，"base + overlay 是正交两层"的假设被打破 —— exempt_range 违反了这个正交性
3. 升为 base 后 spec §2.4 的底色优先级从"优先级表"简化为"单一 base 取值"，逻辑更清晰
**影响**:
- ENUM base_status 从 3 值（present/absent/late）扩到 4 值（+ exempt_range）
- overlay_badges 分两类（纯装饰型 vs 改底色型）显式声明
- UI 层"exempt_range 和 present 同为绿色"的视觉区分问题遗留（backlog S5，待解）
**相关**: 同上 Q1
**事后回看**: (几个月后补填)

---
```

---

## §2 project_evolution.md 新增 5 次转折（D1）

**粘贴位置**：`05_logs/project_evolution.md` 的 `## 现在的状态（2026-04-13）` 之前。**重要**：原文 `## 现在的状态（2026-04-13）` 整段需要重写为 `## 现在的状态（2026-04-20）`，内容对齐 progress_overview。

> **注**：project_evolution 是**叙事段落**（有时间线 + 因果链），不是像 decision_log 那样的结构化条目。下面 5 个 draft 按 project_evolution 现有的"触发事件 / 为什么是转折 / 做了什么 / 意义"结构写。

---

### Draft 1（第五次重大转折）

```markdown
## 第五次重大转折 — 2026-04-15: 反驳 AI 过度配置 + 核心架构原则确立

**触发事件**: 讨论点呼机硬件型号时 AI 推荐 Raspberry Pi 4B 4GB（¥541 RMB），我直觉"太贵"，反问"为什么要这么高配置"。

**为什么这是转折**: 这是项目第一次**我主动反驳 AI 的建议**，回到第一性原理重新论证。从"接受 AI 的合理默认"升级到"质疑 AI 的合理默认"。

**做了什么**:
1. 发现 spec 里 grep "点呼机" 零匹配 —— 根本没写过点呼机职责，AI 因此自由加配
2. 确立核心架构原则：**"点呼机只搬运数据，业务判断全在后端"**（thin client / thick server）
3. 硬件配置大幅降级 —— 从 Pi 4B 4GB 降到 Pi Zero 2 W / Pi 4B 2GB 候选
4. 同日确立 Phase 2 双路径设计（iPhone 读点呼机外贴的静态 NFC 贴纸，自己联网发后端；卡继续走 RFID → 后端）—— 承认 iOS 平台限制，不强求协议统一
5. 发现 spec v0.1 完全没写点呼机契约（spec gap，记为项目债）

**这次转折的意义**:
- 从"被动接受 AI 建议"到"主动反驳 + 独立判断"
- 架构原则从 ad-hoc 拍板升级为显式写出可反复引用的"thin client / thick server"
- 项目第一次承认"有些限制（iOS SE / HCE 权限）改变不了，只能设计绕过"

**事后回看**: (几个月后补填)

---
```

### Draft 2（第六次重大转折）

```markdown
## 第六次重大转折 — 2026-04-17: spec 主体 rewrite + Q1-Q5 硬决策 + 字典体系重构

**触发事件**: 4-15 发现 spec gap 后，意识到 v0.1 spec 的架构已经跟不上 4-12 / 4-15 的决策进度。spec 主体需要一次大 rewrite。

**为什么这是转折**: 之前的转折都是"在旧 spec 上补"，这一天是**旧 spec 上层架构的正式升级**。不是在老房子里加家具，是在老地基上盖新楼。

**做了什么**:
1. **字典三件套 + DEVICE_REGISTRY 四件套**：单源真值架构，spec 主体只引用不重复
2. **Q1-Q5 硬决策**：5 个悬置已久的建模问题（base_status vs overlay 分层 / 其他 4 个）一次性拍板
3. **spec 主体 rewrite**：双路径并存 / thin client / 4 台协调 / 改判时限矩阵 全进主体；681 → 958 行
4. **CHANGELOG 细粒度化 + pre-0.1 追认 6 条**：把"讨论了十几种方案才写第一版文档"的历史补进版本历史
5. **项目版本号 v0.1.3 → v0.2.0 → v0.3.0 连跳两个 minor**：对应字典重构（v0.2.0）+ spec 主体 rewrite（v0.3.0）

**这次转折的意义**:
- spec 层从"设计中"进入"主体稳定"阶段 —— 之后的修改主要是细节 / 补遗，不是架构级变更
- 单源真值架构第一次在项目里落地，为 4-19 的文档同步机制铺了路
- 版本号第一次承担"阶段里程碑"的语义作用（之前更像"commit 汇总"）

**事后回看**: (几个月后补填)

---
```

### Draft 3（第七次重大转折）

```markdown
## 第七次重大转折 — 2026-04-19: G2 决策 + 文档同步机制 + 项目审查 backlog

**触发事件**: 会话开场 itsuki "之前的决定全砍了，从 0 开始"，CC 连续跳步 3 次被纠正，重新确立"先流程后硬件"方法论。

**为什么这是转折**: 这一天做了**三件都是"方法论级别"的事**，不是单一决策。影响到项目之后 6+ 个月的协作方式。

**做了什么**:
1. **G2 决策**：取消 Phase 1 / Phase 2 分阶段，v1.0 直接 iOS + Android + 卡 完整版一次上线（开发内部 M1→M5 里程碑）
2. **卡完整生命周期 + App 账号规则定稿**：空白 NTAG215 + 自贴名字便签 / 一设备一账号 / 丢卡新绑定 / 毕业回收复用
3. **记录指南 §3.4 新增"记录详细度要求"**：5 模块 + 篇幅指引 + 失败模式清单。raw 每条 500-2000 字目标（之前 100-300 字"决策快照"被识别为"简略等于没记录"）
4. **文档同步机制 A+B+C**：从"版本号漂移"症状识别系统病根"多源必然漂移"，选最彻底方案（单源真值 + 同步清单 + pre-commit hook）
5. **项目审查 backlog**：87 条漏洞（D30 + S20 + A13 + T13 + L11）+ Tier 0-4 版本路线图（v0.3.1 → v0.6.0）

**这次转折的意义**:
- **方法论层**：从"做项目"升级到"建立做项目的方式"（见 4-13 第四次转折的延续，但这次更深）
- **工程层**：文档同步机制是第一次用"工程手段"（hook）而不是"纪律手段"解决一致性问题
- **元层**：87 条漏洞清单是对项目至今所有产出的一次全盘审视 —— 展示出"自省 + 改进"的能力
- **协作层**：CC 跳步 3 次被纠正记入详细 log，展示"不盲从 AI"的延续性（和 4-15 反驳过度配置同模式）

**事后回看**: (几个月后补填)

---
```

### Draft 4（第八次重大转折）

```markdown
## 第八次重大转折 — 2026-04-20: iPhone 路径落地 + 发现 URL 复制漏洞 + 动态 NFC 贴纸

**触发事件**: 按 4-19 WIP 留的 5 议题顺序推进，第一个是"iPhone tap 贴纸技术细节"。从议题 A（BTR 方案）进到议题 B（动态贴纸），在过程中发现漏洞。

**为什么这是转折**: 这一天是**"方案介绍 → 找漏洞 → 升级方案"的典型学习循环**。短短半天在 AI 介绍的方案里主动发现攻击面，推翻 AI 推荐的省事组合，选了贵但彻底的方案。

**做了什么**:
1. **iPhone BTR 方案拍板**：Background Tag Reading + Universal Link + AASA，学生 tap 贴纸自动唤 App（2 步 vs 前台读的 7 步）+ 正式域名投资
2. **URL 复制漏洞发现**：CC 讲完方案时我追问"学生把 URL 复制了岂不是到处都能碰一下签到"—— CC 之前完全没提这层，是 gap
3. **方案 A/B/C/D 对比**：CC 推荐 A（BSSID）+ C（人防）省事组合，**我选最贵彻底的 B（动态 NFC 贴纸 ST25DV16K）**—— 不接受"设计上漏 10% 靠人兜底"
4. **硬件最终型号拍板**：追问"为什么需要树莓派"后澄清"thin client ≠ no client"，拍板 Pi 4B 2GB × 4 台（¥1200 RMB）
5. **跨境供应链**：ST25DV 中国 ¥25/个 × 4 = ¥100 + 空运日本 ¥40-60，比日本本地便宜 10 倍

**这次转折的意义**:
- **原创思维循环的再次出现**：和 4-12 "播报防作弊"同一模式 —— 观察 → 找漏洞 → 推导方案（但这次是从 AI 的方案里找漏洞，更高阶）
- **"愿意为正确付代价"确立为设计原则**：方案 B 贵且复杂，但不妥协
- **"AI 推理 vs 主角决策"的典型错位**：AI 优化"最短路径"（A+C 省事），主角守"设计原则完整性"（必须 100% 到场验证）

**事后回看**: (几个月后补填)

---
```

### Draft 5（替换"现在的状态（2026-04-13）"整段）

```markdown
## 现在的状态（2026-04-20）

**项目阶段**:
- 规格设计: ✅ 完成（v0.1 冻结，v0.2/v0.3 迭代）
- 架构决策: ✅ 主体完成（4-12/4-15/4-17/4-19/4-20 五次迭代）
- 硬件采购: ⬜ 待下单（型号已敲定）
- 编程学习: 🔄 Python Day 2+ 延后（spec 主导期合理状态）
- 实际开发: ⬜ 未开始

**记录体系**:
- ✅ dev_log（8 篇，itsuki 手写）
- ✅ problem_solving（4 篇）
- ✅ decision_log（7 + 9 = 16 条，补完 v0.3.1 后）
- ✅ reflection（已迁 iCloud）
- ✅ raw（5+ 份，含 2025-12 早期对话）
- ✅ learning_path + project_evolution（本次转折更新中）
- ✅ 文档同步机制 A+B+C（4-19 新立）
- ✅ 项目审查 backlog（4-19 新立，87 条）
- ⬜ interview_log（待开始）
- ⬜ monthly_review（月底做）

**下一个重大转折会是什么**:
- 第一台点呼机硬件到手 + 能读第一张 NFC 卡（M2 里程碑，预计 5-6 月）
- 第一个后端 API 跑通（M2-M3，预计 6-7 月）
- 第一个 iPhone / Android 能 tap 贴纸自动唤 App（M4，预计 7-8 月）
- v1.0 全系统联调完成（M5，预计 9-10 月）
- 宿舍正式上线 = v1.0.0（预计 AC 提交后，2026-11 月左右）

---
```

---

## §3 learning_path.md Python Day 2 坦诚（D3）

**粘贴位置**: `05_logs/learning_path.md` 找到 "即将要学 → Python 进阶（第 2-5 天）" 那段，**整段替换**。

```markdown
### Python 进阶 — Day 2+ 主动延后

**现状（2026-04-20）**: Python Day 1 学于 2026-03-11，Day 2+ 至今 40 天未续。

**坦诚说明为什么延后（这不是"懒"，是主动选择）**:

1. **3-11 到 4-20 期间项目处于 spec / 架构主导期** —— 真实工程需求没到位之前，单独学 Python 驱动力不够（4-10 回归日"边做边学"哲学的直接体现）
2. **期间的认知产出主要发生在架构层**：4-12 NFC 架构 / 4-15 thin client + 双路径 / 4-17 spec rewrite / 4-19 G2 + 文档同步机制 / 4-20 BTR + 动态贴纸 —— 这些都比"学 Python for 循环"优先级高
3. **续学时机判断**：等 M1 里程碑（spec 完全定稿）完成 + M2 开工前约 1-2 周启动，那时 Python 代码有真实目的（点呼机 I²C 刷新 / HTTP 发后端 / pyttsx3 播报 ≈ 20 行代码/台）

**AC 视角**:
这段"延后"在 AC 面试里正是可讲的素材 —— **展示"学习驱动力来自真实问题"而不是"按教程进度"**。和 4-10 回归日反思里"单独学 Python 学不下去"的认知一脉相承。不是瑕疵，是方法论一致性的证据。

**下一步**（等 M2 开工前启动）:
- [ ] Python Day 2: for 循环、list
- [ ] Python Day 3: while 循环、dict
- [ ] Python Day 4: 函数（function）
- [ ] Python Day 5: 类（class）
```

---

## §4 learning_path.md PostgreSQL 选型补答（D4）

**粘贴位置**: `05_logs/learning_path.md` 找到 "为什么选 PostgreSQL 不是 MySQL/SQLite: (未想好，学的时候再回答)" 那段，**整段替换**。

```markdown
### 为什么选 PostgreSQL（不是 MySQL / SQLite）

[itsuki 补：以下是 CC 整理的选型素材，最终措辞由你拍板]

**核心理由**（按重要度排序）:

1. **我需要的是"认真的关系型数据库"，但不需要 MySQL 的互联网大规模场景特性**
   - DMSD 是一个宿舍内部系统，用户数几百，不需要分库分表 / 主从复制 / 读写分离这些 MySQL 生态的强项
   - PostgreSQL 对"中小规模 + 正确性优先"场景更友好 —— 严格的数据类型、约束检查、事务保证

2. **SQLite 不行的原因**: 虽然文件型数据库轻量，但 DMSD 有多客户端（4 台点呼机 + 老师 iPad + 学生手机）并发写入，SQLite 的 writer lock 模型会卡

3. **PostgreSQL 对 spec 里的数据模型友好**:
   - spec 里 `base_status` 是枚举 → PostgreSQL 原生 `ENUM` 类型（MySQL 也有但没 PG 严格）
   - `audit_log` 审计场景 → PostgreSQL 的 JSONB 字段能直接存审计元数据（不用额外表）
   - `idempotency_key` 唯一约束 + partial index → PostgreSQL 支持更完整
   - 将来如果要加时序数据（考勤统计 / 扣分历史），PostgreSQL 的时间函数和窗口函数更强

4. **学习曲线和中文资料**: PostgreSQL 中文文档相对 MySQL 少一些，但官方英文文档非常完整（比 MySQL 更系统）；且 PG 的"标准 SQL 兼容性"更好 —— 学它等于学 SQL 本身，将来转 MySQL / Oracle / SQL Server 迁移成本低

5. **和 FastAPI + SQLAlchemy 的搭配**: 业界推荐组合，生态成熟；PG 的 asyncpg 驱动是 Python 异步场景的标配

**什么时候会改变这个决策**:
- 发现某个功能 PostgreSQL 做不到但 MySQL 能做（目前不知道是什么场景）
- 数据量爆发到需要水平扩展（DMSD 全宿舍才几百人，不会）
- 团队来了个 MySQL 专家不愿学 PG（DMSD 就我一个人，不适用）

**面试可用表达**:
> "我选 PostgreSQL 不是因为它最流行，是因为它最匹配 DMSD 这个'小规模 + 正确性优先 + 数据模型偏复杂（枚举 / JSONB / 时序）' 的场景。MySQL 的强项（超大规模互联网场景的分库分表）我用不上，而 PostgreSQL 对 spec 里已经定义的字段类型支持更严格，可以让代码在数据层就挡住类型错误。"
```

---

## 💡 itsuki 粘贴工作流建议

1. **开一个 terminal**：`cd ~/dev/DMSD` + `code 05_logs/decision_log.md` + `code 05_logs/project_evolution.md` + `code 05_logs/learning_path.md`
2. **逐 draft 复制**：每个 draft 用三反引号围住，复制中间内容（不含围栏）
3. **粘贴后**：
   - decision_log: 粘在 "## 决策记录（倒序）" 下面（最新在最上面）
   - project_evolution: 按时间倒序 OR 正序（跟现有文件保持一致 —— 原文是**正序**）
   - learning_path: 替换原对应段落
4. **每粘一个 draft 后** 回本文件来打 x：在对应 Draft 标题下加一行 `<!-- ✅ 已粘贴 YYYY-MM-DD -->`
5. **全部粘完**：
   - 把 `00_admin/2026-04-19_项目审查_backlog.md` 里 D1 / D2 / D3 / D4 打 ✅
   - 然后告诉 CC，CC 会更新 backlog + 触发 v0.3.2 patch
   - 可选：删除本文件 `00_admin/Batch3_itsuki手笔素材指引.md`（已完成使命）

---

**END** — 本文件是 v0.3.1 → v0.3.2 之间的临时辅助文件，不算项目正式产出。

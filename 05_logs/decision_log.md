# 决策变更记录

> 记录项目的版本级/方向性重大决策。
> 单文件追加式,最新的决策放最上面。
> 面试前快速调取决策脉络用。

---

## 格式模板

```markdown
## YYYY-MM-DD — [决策简述]

**之前的决策**: ...
**新的决策**: ...
**为什么改**:
1. ...
2. ...
**这个改动影响了什么**: ...
**事后回看**(几个月后补填): 这个决定对吗?
```

---

## 决策记录(倒序)

## 2026-05-26 — 指令文档不写时间戳 / 历史标记 + DMSD CLAUDE.md 247→190 行重写到 QTS 模式

**之前的决策**(隐性 / 长期): CC 在 CLAUDE.md / SKILL.md / 文档同步点等指令文档里习惯加「2026-05-XX 拍板 / 上线 / 新加 / B-XXX 死链修复」类时间戳 / 历史标记 — 以为是「可追溯 + 有上下文」，itsuki 反复看到反感累积
**新的决策**:
1. **铁律立项**：指令文档（CLAUDE.md / SKILL.md / `.claude/agents/*.md` / `docs/agents/*.md`）正文不写时间戳 / 历史标记 — 历史归 git log / `05_logs/decision_log.md` / raw / CHANGELOG
2. **写到 memory**：新建 `~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/feedback_no_timestamps_in_instruction_docs.md`（跨会话坚持）
3. **DMSD CLAUDE.md 重写**：247→190 行（A 砍 120 行历史/复制版段 + B 搬 35 行到 dmsd-startup §4 + D 补 70 行参考 QTS 模式 — Skills 继承段 / Hooks 继承段 / 全项目中枢联动 / 沟通规则简版 / Git 段）
4. WIP 顶部「最后更新」+「最近会话」段时间戳是例外（协调用，本来就是日志性质）
**为什么改**:
1. itsuki 5-26 列 DMSD CLAUDE.md 内容时看到「🆕 5-26 新加（5 行）」标记，反应：「像这种 xxx 新加，**完全没必要写到 claude.md 里啊，只是浪费时间**」
2. 设计哲学（itsuki 隐性长期，5-26 第一次明示）：指令文档 ≠ 日志 — 指令文档是当下指引（长期可读 / 不被历史污染），历史归专门的日志文件
3. QTS CLAUDE.md（itsuki 自己整理的）给 DMSD 缺的良好模式：Skills 继承段 / Hooks 继承段 / 全项目中枢联动段（结构清晰 / 不混历史）
4. CC 长期翻车（写时间戳 = 潜意识把指令当日志用） — 累积 → itsuki 正式拍板立铁律
**这个改动影响了什么**:
- DMSD CLAUDE.md 247→190 行（砍 57 行 + 加 QTS 模式新段）
- DMSD CLAUDE.md 增加 Skills 继承段 + Hooks 继承段 + 全项目中枢联动段 + 沟通规则简版 + Git 段
- 6 个项目 CLAUDE.md 顶部加沟通铁律段「不主动用英语名词」
- dmsd-startup SKILL.md §4 新增「按需触发的事」段（搬 CLAUDE.md L132-150 原内容）
- project-overview SKILL.md §1.7 dmsd-startup 描述加「+ §4 按需触发的事」
- memory 新增 `feedback_no_timestamps_in_instruction_docs.md`
- 未来所有 CLAUDE.md / SKILL.md 改动都按此铁律 — 不加时间戳尾巴 / 历史段 / bug 编号
**相关**: `05_logs/raw/2026-05-26_dmsd-startup+CLAUDE.md大改.md` 阶段 6-9
**事后回看**(几个月后补填):

---

## 2026-05-26 — 启动 SOP 集中化 — dmsd-startup skill 立项 + 全局 coord-check 退役（DMSD 项目下静默）

**之前的决策**(2026-05-25 + 早些): DMSD 启动逻辑散在 3 处 — 全局 `~/.claude/hooks/session-start-coord-check.sh`（多会话协同检测） + 全局 `~/.claude/hooks/session-start-env-diff.sh`（环境清单对账）+ DMSD `bin/check_overview_drift.sh`（project-overview 漂移检测，SessionStart hook）+ DMSD `CLAUDE.md` 第 106-111 行「会话开始: 读 WIP.md」段
**新的决策**:
1. DMSD 新建 `~/dev/DMSD/.claude/skills/dmsd-startup/SKILL.md` — §2 5 件启动必做事（多会话协同注册 / project-overview 漂移检测 / ac-radar startup_check / 读 WIP / 报告状态）+ §4 按需触发的事（找文件 / TODO / WIP-TODO 铁律 / 文件联动）
2. 全局 `session-start-coord-check.sh` 在 DMSD 项目下 `exit 0` 静默退出 — 由 dmsd-startup §2 Step 1 接管
3. 全局 `session-start-env-diff.sh` 不动 — 留全局自动跑（覆盖所有项目）
4. 每个项目以后独立做自己的启动 skill（QTS / tango / SC26 等先不做，按需后续）
**为什么改**:
1. itsuki 反问「这不应该做成 skill 吗？sesion start env diff 和 start coor 不都是应该集合到启动 skill 里吗？」— CC 第一方案「挂钩不动 + skill 抽段」被推翻，itsuki 想要的不是「挂钩 + skill 互补」是「全集中到一个 skill」
2. 散在 3 处 = 容易漏，集中到 skill = 一站式入口 + CC 启动后读一次拿到完整 SOP
3. 设计哲学：单一职责 + 单一入口 over 多层冗余 + 互补
4. env-diff 留全局是因为它是「跨项目通用对账」（全局工具差异），不属于「项目特定启动逻辑」 — 职责本来就在全局层
**这个改动影响了什么**:
- DMSD `.claude/skills/` 多 1 个 skill（7→8）
- DMSD CLAUDE.md 顶部加「⭐⭐⭐ dmsd-startup 强制加载」段（5 行核心 + 简化的会话开始段）
- `~/.claude/hooks/session-start-coord-check.sh` DMSD 项目下静默退出
- 未来其他 5 项目（QTS / tango / SC26 / practice / cc-project-template）都要做自己的启动 skill
- 长期：每项目启动 skill 内容会因项目差异而不同（DMSD 有 5 端联动 / QTS 有 DECISIONS.md / tango 单端 web 等）
**相关**: `05_logs/raw/2026-05-26_dmsd-startup+CLAUDE.md大改.md` 阶段 4-5
**事后回看**(几个月后补填):

---

## 2026-05-26 — destructive-bash 行为约定立项（CC 看到 WARN 自己停下想，不阻断不批准）

**之前的决策**(2026-05-12): `pre-bash-destructive-block.sh` 从 exit 2 阻断改成 warn 模式（注入 ⚠️ destructive-bash-WARN 文字提醒，不阻断命令）
**新的决策**: 在全局 `~/.claude/CLAUDE.md` 加 CC 行为约定段。CC 看到 WARN 后：(1) 自己停下来想一遍这命令真有必要吗 (2) 没必要 → 不跑 + 跟 itsuki 说一句「本来要跑 X 反思后跳过」(3) 有必要 → 直接跑不专门征求同意 (4) 灾难级（rm -rf 到 repo / rm .git / git push --force 到 main）即使有必要也要先确认
**为什么改**:
1. 5-12 改成 warn 后 itsuki 感觉「hook 没在工作」— warn 模式靠 CC 自觉，CC 看到警告但下意识继续跑命令 → 从外部看就是「命令照跑 / hook 等于没」
2. CC 提 A 全阻断 / B 加规则 / C 灾难级分档 + 可恢复级 warn 三方案 — itsuki 选 B 简化版「不要分档，不要征求同意，只要让 CC 多一次反思窗口」
3. 这不是技术决策是设计哲学 — 工具不必非「拦」或「批」，可以是「提醒反思」第三态
**这个改动影响了什么**:
- 全局 `~/.claude/CLAUDE.md` 加 `## destructive-bash-WARN 看到之后怎么办` 段（5 行行为约定）
- `pre-bash-destructive-block.sh` 脚本本体不变（已经是 warn 模式 + 8 个 pattern）
- 沟通规则隐性立铁律 — 工具警告不是用来阻断 CC，是用来给 CC 反思空间
**相关**: `05_logs/raw/2026-05-26_dmsd-startup+CLAUDE.md大改.md` 阶段 1
**事后回看**(几个月后补填):

---

## 2026-05-22 — 撤回中国海运渠道，改日本本地买点呼机配件

**之前的决策**(2026-05-08): 11 件配件淘宝集中下单 ¥381 RMB 海运到日本（含 Pi 3A+ / PN532 V3 红板 / ST25DV16K × 2 / NTAG215 × 50 / LED 5 色套装 / USB 小音响 / 面包板 / 杜邦线 / 电源 / 透明壳 + 风扇）
**新的决策**: 被海关查扣的不要了。以后所有点呼机配件改在日本本地买（Amazon.jp / 秋月電子 / スイッチサイエンス / 千石電商 / Yahoo Auction / メルカリ）
**为什么改**:
1. 5-12 到 5-16 之间这批配件走中国海运被海关查扣全没。原因是为省运费打成一个包裹寄出 → 不清楚是哪 1-2 件触发查扣，但所有件连带没收（打包 = 单点故障 / single point of failure）
2. 长期维护视角：日本本地买 = 本地有备件 + 退换货走日本邮政 = 以后某个配件坏了维护方便
3. 风险跟件数非线性 — 一件出事全没。下次拆寄 + 本地买 = 真省，不只是规避海关
**这个改动影响了什么**:
- 原 ¥381 RMB 淘宝清单 + 「下单」「收货清点」2 任务作废
- 预算重估：日本本地价 vs 中国海运价，预计贵 1.5~2 倍但消除海关风险 + 提速到货
- 硬件设计文档 `02_design/hardware_design.md` §2 全部型号 / 价格 / 渠道字段要重写（日本重新选型后）
- 点呼机设计文档 `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md §1.2` 加海关事件 + 改日本买
- 未来从中国寄任何件都要拆成 2-3 包分批寄
**相关**: `05_logs/raw/2026-05-22.md`（深度 AC 素材 + 模式 1+2+6 三维度拆解）+ `.claude/skills/session-wrap/SKILL.md §5.5.15`（同日立项 decision-draft 子节 — 第一次实测产出就是这条）
**事后回看**(几个月后补填):

---

## 2026-04-15 — 点呼机架构原则: "只搬运数据,业务判断全在后端"

**之前的决策**: 无(职责边界模糊,spec 里根本没写过点呼机职责)
**新的决策**: 点呼机只做 4 件事 — 读 NFC、发 HTTP、听 WebSocket 接收推送、播报 + 亮灯。**不做任何业务判断**(迟到/缺席/窗口内外,一律后端决定)
**为什么改**:
1. AI 推 Pi 4B 4GB ¥541 RMB,我直觉"太贵",反问"为什么要这么高配置",回到第一性原理
2. 发现 spec 里 grep 点呼机零匹配 — 没有职责声明,AI 就会自由加配
3. 职责最简化 → 配置需求最小化 → Pi Zero 2 W 级别就够用
4. thin client / thick server 是成熟架构原则,改规则时只改后端一处,设备越蠢越安全
**影响**:
- 硬件配置大幅降级(Pi 4B 4GB → Pi Zero 2 W / Pi 4B 2GB 候选)
- 点呼机代码极简化(估计 < 100 行 Python)
- 所有未来"给点呼机加功能"的诱惑都要被这个原则挡回去
**相关**: `problem_solving/2026-04-15_AI过度配置诊断.md`
**事后回看**: (几个月后补填)

---

## 2026-04-15 — Phase 2 架构: iPhone 读静态标签 + 卡共存的双路径,不走 HCE

**之前的决策**(4-12 原始设想): "学生拿手机碰一下点呼机,点呼机收到手机传来的信息" — 默认手机和卡走同一个协议(都发 UID 给点呼机)
**新的决策**: 双路径共存,**协议不强求统一**
- **路径 A(卡)**: 卡 → 点呼机读 UID → HTTP 发后端 → 后端判断 → 返回 → 播报
- **路径 B(iPhone)**: iPhone 读点呼机外贴的**静态** NFC 标签(拿 device_id)→ iPhone 自己用 WiFi/4G 发 `{student_id, device_id, ts, 签名}` 给后端 → 后端判断 → 后端通过 WebSocket 推回点呼机 → 播报
**为什么改**:
1. 我原本的"卡和手机都只发 UID"统一模型撞上 iOS 平台限制 — 第三方 App 不能访问 Secure Element / HCE,**不能伪装 NFC 卡发任意 UID**
2. 追问"自动贩卖机碰一碰怎么做的",挖到 Apple Pay 背后是 SE + 一次性 token,不是普通 App 能碰的基础设施
3. 承认平台差异,用两条不同技术路径实现同样的用户体验,比强求统一协议更现实
**影响**:
- 点呼机外壳要多贴一张静态 NFC 标签(~¥2/张)
- 后端要加 WebSocket 推送机制给点呼机发播报指令
- iPhone App 要实现 Core NFC 读标签 + 签名逻辑
- Android 方案要单独设计(HCE 机制和 iOS 不同),记为项目债
- **Phase 1 卡设计不需要推翻**,Phase 2 是"加",不是"改" — 分阶段策略的复利
**相关**: `problem_solving/2026-04-15_iOS限制下的UID统一模型重构.md`
**事后回看**: (几个月后补填)

---

## 2026-04-15 — 点呼机大脑: 经 A(RPi)/B(ESP32) 全维度重新对比后,确认方向 A

**之前的决策**(4-12 记录的): 点呼机 = Raspberry Pi + PN532 NFC + 扬声器
**新的决策**: 方向仍是 A(Raspberry Pi),**但这次是经过完整 A/B 对比后由 itsuki 主动拍板,不是默认继承 AI 建议**
**为什么改(过程而非结论)**:
1. 4-12 的"已决定 RPi" 是 AI 建议 itsuki 没反对,不是主动决策
2. 今天重开对比:SBC vs MCU 本质差异、离线能力、语音播报、扩展性、AC 叙事
3. 基于 itsuki 的三个判断(宿舍网络稳、不需要屏幕、想练 Python+Linux 这条线),确认 A
4. **具体型号未定** — Pi Zero 2 W (¥100) vs Pi 4B 2GB (¥300) 还在候选,等宿舍网络情况细节再拍
**影响**: 方向没变,但这次是"被论证过的决策"而不是"默认接受的建议"
**事后回看**: (几个月后补填)

---

## 2026-04-10 — 学习方法: 从"先学完再做"改为"边做边学 + AI 辅助"

**之前的决策**: 按传统路径先把 Python 学完、Swift 学完、数据库学完,再开始做 DMSD
**新的决策**: 边做边学 — 遇到需要什么再学什么,AI 作为即时家教
**为什么改**:
1. 传统路径在 AI 时代过时了 — AI 可以即时解释任何概念,不需要"预先学完"这个前提
2. 没有真实问题驱动的学习,记不住也用不上;有问题驱动就有动力
3. AC 入試 评委更喜欢"带着真实问题边学边做"的故事,比"系统学完后按部就班"强
4. 一个月空白期证明了"先学再做"对我不可行(学着学着就放弃了)

**但识别出一个陷阱**: 纯粹"让 AI 写我不懂的代码" = vibe coding,这是作弊。
**对应的三条铁律**:
- 每行代码能解释
- 先猜后跑(先预测 AI 写的代码会怎么执行,再跑验证)
- 写 dev_log

**这个改动影响了什么**:
- 学习路径: 详见 `learning_path.md`
- AI 协作规则: 详见 `CLAUDE.md` + `feedback_be_a_coach_not_executor`
- 整个项目节奏: 不再"先憋几个月再开始",而是从现在起边做边学

**事后回看**: (几个月后补填)

---

## 2026-04-13 — 版本号体系重置: v1.0 spec → v0.1

**之前的决策**: 2026-02-12 冻结 spec 文件时用了 "v1.0" 命名(11 个文件)
**新的决策**: 所有 spec 文件重命名为 "v0.1";项目版本从 0.x.x 开始;v1.0.0 = 宿舍正式上线
**为什么改**:
1. 学了 SemVer 规范后意识到 "v1.0" 代表"第一次正式发布",连代码都没写不能叫 1.0
2. 趁文件少立刻纠正,以后文件多了改起来成本高
3. 错误的版本号会让所有后续版本的意义都不对
**影响**: 11 个 spec 文件重命名 + 所有交叉引用更新 + 建立 CHANGELOG + 写版本管理指南

---

## 2026-04-12 — 点呼机硬件: 从 iPad 改为 Raspberry Pi

**之前的决策**: (AI 一开始假设)点呼机 = iPad
**新的决策**: 点呼机 = Raspberry Pi + PN532 NFC 模块 + 扬声器,贴墙安装
**为什么改**:
1. iPad 不适合固定在墙上,也太贵(~¥50,000+ 一台)
2. Raspberry Pi 方案 ~¥13,500/台,便宜 80%
3. Raspberry Pi 跑 Python,和后端同一种语言,学习曲线低
4. 自己组装硬件对 AC 入試 展示动手能力 + 成本意识
**影响**: 后端接口设计、设备端代码语言、硬件采购清单

---

## 2026-04-12 — 分阶段上线策略

**之前的决策**: v1.0 一次性包括后端 + iOS 学生 App
**新的决策**:
- Phase 1: NFC 卡 + 后端 + 点呼机 (不需要学生 App,最快上线)
- Phase 2: 加手机 App(iOS + Android),和卡共存
**为什么改**:
1. 用卡可以绕过"学生手机 iOS/Android 不统一"的问题
2. 学校另一位老师在做二维码方案,我需要尽快上线
3. Phase 2 不替换 Phase 1,向后兼容
**影响**: 开发量砍掉近一半,上线速度大幅提升

---

## 2026-04-12 — 点呼防作弊: 语音播报设计

**之前的决策**: 无(设计空白)
**新的决策**: 学生碰卡后系统播报学生姓名,老师对照人脸
**为什么改**:
1. 发现任何打卡系统都有共同弱点:技术只能验证设备,验证不了人
2. 二维码可截图、NFC 卡可让朋友带、手机可借给朋友 — 都绕不开"代签"
3. 播报 + 老师看脸 = 攻击者必须本人到场,技术 + 人的组合
**影响**: 点呼机必须有扬声器,Phase 1 的核心差异化功能

---

## 2026-04-12 — NFC vs 二维码

**之前的决策**: 已决定 NFC,但没明确理由
**新的决策**: 继续 NFC,理由充分化
**为什么改**:
1. 二维码可以截图发给不在场的同学(致命漏洞)
2. 点呼的本质是"确认人在场",不是"确认有人扫了码"
3. NFC 的 4cm 距离限制从根本上消除了这个漏洞
**影响**: 技术选型定稿,写进 dev_log 和 spec

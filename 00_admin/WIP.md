# 当前工作状态 (Work In Progress)

<!-- 滚动规则：最后更新段只留最近 5 次会话，老条目收尾时移 99_archive -->
**最后更新**: 2026-06-10（最近 5 次会话，每条一行；完整历史原文 → `99_archive/2026-06-10_WIP历史段归档.md`）

- **2026-06-10 WIP/TODO 瘦身重组**——按交接件 `WIP_TODO瘦身_交接_2026-06-10.md` 把 TODO.md 重排成 §A 上线必做 / §B 不挡上线 / §C 长尾存疑 / §D 等拍板 四层（571 条未完成只搬家未改写、前后计数一致，整段已完成移 `TODO_完成归档.md`）+ 本段瘦身到 5 条。**未 push**。
- **2026-06-10 iOS 全量审查 + 前后端对齐（额度中断收口）**——26 代理审 22543 行，确认 138 / 推翻 8 / 未验证 86，最大发现「点呼显示链 iOS 端整条是假的」；结果入 TODO §A/§B，原始数据存 raw json。**未 push**。
- **2026-06-10 点呼机设计档案「硬件待下单」文档漂移修复**——6-04 下单状态漏同步 `ROLLCALL_DEVICE_DESIGN_LOG.md` 两段，本次补成「✅ 已下单」。详见 raw/dev_log `2026-06-10`。**未 push**。
- **2026-06-09 版本号重排 + 多代理深度审查**——按「一个 bug 一个补丁号」重排 95 个 commit 补 32 个标签、当前 v0.19.3；29 子代理审出 19 条确认入 TODO 不当场修。详见 raw `2026-06-09_版本号重排+深度审查.md`。**未 push**。 <!-- VERSION_OK -->
- **2026-06-09 iOS 上线缺口 11 功能实装 + codex 4 轮对抗复审收敛**——11 功能各单独 commit、双 scheme 编译过、ST25DVWriter NFC 取消竞态挖到 0 阻塞 0 重大，13 commit 本地。详见 raw/dev_log `2026-06-09`。**未 push**。

> **本文件 = Claude Code 的「当下书签 + 多会话协调」清单。短小为美。**
>
> **职责分工（重要 — 别再重叠）**:
>
> | 文件 | 内容 | 给谁看 |
> |---|---|---|
> | **WIP.md（本文件）** | 当下书签 + 最近 5 次会话 1-2 行总结 + 多会话占用 + 阻塞项 | CC（每次会话开始读全文）|
> | **TODO.md** | **所有未完成事项的完整 backlog**（真值）| itsuki + CC（每次会话开始扫顶部 200 行）|
> | ~~progress_overview.md~~ | 2026-06-10 退役归档 — 进度叙事归 CHANGELOG 全版本一览 + PROJECT_GUIDE §8.5 | — |
> | **CHANGELOG.md** | 已发布版本编年史 | 全部读者 |
> | **commit history** | 每次改动的细节 | git log 可查 |
>
> **铁律**：未完成的事**只写在 TODO.md**。本文件**绝不**复述 TODO 的内容。
>
> - **会话开始**: CC 走 `.claude/skills/dmsd-startup/SKILL.md` §2 — 5 件必做事（多会话协同注册 / project-overview 漂移检测 / ac-radar startup_check / 读 WIP / 报告状态）。**TODO + git status 启动不主动跑**（TODO 等 itsuki 主动问，git status 留收尾 §5.5.9）
> - **会话结束**: CC 更新「最近会话」+「多会话占用」；新增的 backlog **写到 TODO.md** 不写这里

---

**当前版本**: v0.19.3 <!-- VERSION_OK -->（2026-06-09 把 v0.15.0 之后 95 个 commit 按「一个 bug 一个补丁号 / 连续 feat 批次合成次版本号」重排补打 32 个标签 v0.15.1~v0.19.3；远程 origin 最后 push 停在 v0.8.0 故重排安全；详见 CHANGELOG 顶部「2026-06-09 重排说明」）
**版本 bump 流程**: `.claude/skills/version-bump/SKILL.md`（itsuki 说「迭代/bump/发版本/打 tag」自动触发；CC 有否决权 — 即使 itsuki 说要 bump 但 §2 决策树不命中可以拒绝）

---

## 🎯 当前焦点

> **⭐⭐⭐ 沟通规则 cc-comm-rules v0.6.0（5-14 晚撤回 v0.5.0）** — 新会话必读 → `raw/2026-05-14.md §K` + 全局挂钩 `~/.claude/skills/cc-comm-rules/SKILL.md` <!-- VERSION_OK -->
> **v0.6.0 撤回 v0.5.0「英文自由用」** — 回归 v0.4.1「概念术语强制中文 + 技术事实保留英文」+ 新加 §2.3.1「术语后必带中文效果描述」。起因：v0.5.0 早段拍板当晚实测翻车（must 模式 / action 模式 / modified / 残 / 误判拒答 看不懂）。术语表 180+ 词条**保留**作 AC 学习材料，但 v0.6.0 后**不再自动加词**。<!-- VERSION_OK -->
> **配套新挂钩**：`anti-ai-flavor` 全局挂钩（CC 说话别像 AI、像真人聊天 — 气质层）— 6 类痛点 A-F（A 缺上下文 / B 复杂条件句 / C 网络黑话 / D 术语裸露 / E 字面化 / F 客套腔）按反感程度排序，always-on。详见 `~/.claude/skills/anti-ai-flavor/SKILL.md`<!-- VERSION_OK -->
> v0.1-v0.4「约束 CC 输出」思路全部作废。<!-- VERSION_OK -->
> **删的**：`pre-write-memory-block.sh` hook（itsuki 原话「我从来没有说过要拦截持久记忆」）。
> **新的**：`pre-bash-destructive-block.sh` 推全局 `~/.claude/hooks/`（原 DMSD 项目级保留）— 8 个原 pattern 不变，warn 模式不变，覆盖范围扩到所有项目。
> **备份**：5-14 改的 3 处旧版存 `~/.claude/_archive_2026-05-14/`（含 README 回滚命令）。
> **未来 propose**：把 `~/.claude/` 做成 git 仓库（永久解决全局配置无历史问题）— 等 itsuki 拍板。

> **⏰ Cloud Design 5-12 额度已过期** — 5-14 检查时已浪费。下次额度重置时间未知。

**当前版本之后的阶段**（版本号见 `CHANGELOG.md` 顶部） — 5 端代码层启动完毕（iOS + Android + Web + Backend + 点呼机），下一步重点：
1. 老师公告 4 端实装（iOS + Android + Web + Backend — 不含点呼机）— spec 已落 `system_features.md §7.15`
2. 学生注册码 v1.0 实装（4 端 spec 已就位 2026-05-03 上午别会话 — 不含点呼机）
3. ~~文档欠债：`progress_overview.md` 章节级里程碑刷新~~（2026-06-10 以退役方式解决 — 归档进 99_archive，待办已提取 TODO §N+）

→ 完整 backlog 看 `TODO.md`。

---

## 📜 最近会话（最多保留 5 条，老的删 — 详细历史看 commit log + raw/）

### 2026-06-10 WIP/TODO 瘦身重组（交接任务执行）by [Fable 5]

- 接手交接件 `WIP_TODO瘦身_交接_2026-06-10.md`：TODO.md 2220 行重排成 §A 上线必做(102) / §B 不挡上线(199) / §C 长尾存疑(230) / §D 等拍板(40) 四层，整段已完成移 `TODO_完成归档.md`；WIP 顶部 1.26 万字历史段剪切 `99_archive/2026-06-10_WIP历史段归档.md`。
- 脚本断言 2220 行全覆盖 + 未完成 571 条前后对账一条不丢。跟交接件两处出入已明示：零散 ✅ 条目留原位当证据 / §A 102 条超「几十条」预估不硬砍。
- 4 commit（`b429940`/`cc62fa2`/`475d9c2`/`fc58de1`）未 push。raw `2026-06-10_WIP_TODO瘦身.md` + dev_log 同名。

### 2026-06-10 iOS 全量审查 + 前后端对齐 — 额度中断收口 by [Fable 5 · ultracode]

- itsuki 要「审查所有 iOS 代码 + 前端后端对齐」（全量 22543 行，区别于 6-09 增量审查）。26 个一线代理（13 审查分片 + 13 对齐域）+ 对抗验证（重大 3 票多数决）。
- **额度两次撞限**（250 代理后挂、续跑又静默断），itsuki 喊停 → CC 停工作流**零代理本地收口**：脚本解析工作流日志收割 233 条发现 + 160 个验证裁决配对合并。
- 结果入 `TODO.md §🔍 2026-06-10`：确认 138 / 推翻 8（误报率 5%）/ **86 条未验证**（含 22 重大，工作流缓存在可续跑）→ 合并后 84 条待办。按 6-09 拍板**只记录未修**。
- 最大发现：**点呼显示链 iOS 端整条是假的**（签到永远「時間内」、弹窗永远「点呼時間外」、详情时刻写死）。另亲自 grep 核实「{ok,data} 响应包络两侧代码都不存在」= 心智模型 §3 + API_CONVENTIONS 文档漂移，已挂心智模型 §6 未决。
- commit `71d9200`（TODO + 原始数据 json）+ 收尾 commit，未 push。raw `2026-06-10_iOS全量审查.md`。

### 2026-06-10 点呼机设计档案「硬件待下单」文档漂移修复 by [Opus 4.8 1M]

- itsuki 发现 `ROLLCALL_DEVICE_DESIGN_LOG.md`（点呼机软件设计档案）还写「硬件待下单 ⏳」，要 CC 诊断根因。
- 查 git 历史定位：6-04「硬件下单总检查」提交 `8b5c081` 把下单状态写进 `hardware_design.md` + 采购清单网页，但对点呼机软件档案只改了一行 LED 接线，进度表 + §1.2 启动前提两段没同步——「改 A 漏联动 B」文档漂移。
- 核实秋月電子三家全下单后，把两处改成「✅ 已下单」。判断不需联动其他架构链文件（只是采购进度）。本地 commit 未 push。AC：问题发现 + 诊断真因。raw `2026-06-10.md`。

### 2026-06-09 版本号重排 + 多代理深度审查 by [Opus 4.8 1M · xhigh]

- itsuki 要「审查 v0.15.0 之后的活 + 重排版本号」。**三轮纠正 CC**：① 别把 bug 跟功能打包成一个版本号 ② 审查找的 bug 丢 TODO、别当场修（「我什么时候让你找 bug 了」）③ 一个 bug 一个补丁号、别算一起（「每个版本号都能对得齐就行」）。<!-- VERSION_OK -->
- **版本号重排**：按「一个 bug 一个补丁号（第三位）/ 连续 feat 批次合成次版本号（第二位）」重排 v0.15.0 之后 95 个 commit → 新建 **32 个 tag v0.15.1~v0.19.3**（4 minor + 28 patch），**当前 v0.19.3**。未改代码、未动 commit。远程停 v0.8.0 故重排安全。<!-- VERSION_OK -->
- **多代理深度审查**：6 维度并行 + 对抗验证 v0.15.0..HEAD + 3 未提交改动（29 子代理）→ raise 23 确认 19（0 阻塞 / 2 重大 / 12 次要 / 5 小），全部写进 `TODO.md` §🔍，按 itsuki 拍板**不在本次修**。<!-- VERSION_OK -->
- 验证：后端 pytest 373 全过 + iOS 正式版/演示版双 BUILD SUCCEEDED。commit `b6a0b79`（版本重排文档）+ 收尾 commit，**未 push**。
- AC：模式 5（认知改变 — itsuki 推导出 SemVer 正确用法）+ 模式 1（纠正 AI）双顶级。详见 raw `2026-06-09_版本号重排+深度审查.md` + decision_log。

### 2026-06-09 iOS 上线缺口 11 功能实装 + codex 4 轮对抗复审收敛 by [Opus 4.8 1M · ultracode · /goal]

- itsuki 6-08 让 6 维度子代理审 iOS 2.2 万行列缺口（TODO §📱），本会话做其中「代码能做 + 编译验证」的 11 个。`/goal` 因正文超 4000 字符没挂上，itsuki「继续」让 CC 按施工图自主跑。
- 11 功能各单独 commit、正式版+演示版双 scheme BUILD SUCCEEDED：① 手机 NFC 签到（新建 `ST25DVWriter.swift` 用 CoreNFC 写 ST25DV Mailbox，2026-06-02 架构反转方案，命令字节占位 TODO[硬件]）/ ② `.icon` 图标保留验证（不建 appiconset）/ ③ entitlements+NFC说明 / ④ 6 列表三态 / ⑤ 令牌过期跳登录 / ⑥ 离线不显假学生 / ⑦ 删巴士死页+events接后端 / ⑧ 隐私清单据实补 / ⑨ 删暗色死控件 / ⑩ 加密标志 / ⑪ 通知说明。
- **codex 4 轮对抗复审**（gpt-5 + high，非预期 gpt-5.5 + xhigh）逐层挖 `ST25DVWriter` NFC 取消竞态：一轮 2 阻塞+4 重大+1 次要 → 二/三轮 M-1 越挖越深（cancel 空操作 → 创建 session 前空窗）→ 四轮核实死锁判断 + 报 0 阻塞 0 重大收敛。CC 不盲信（指出 codex 高估了「B-2 双重 resume 崩溃」，单线程本不崩只是跨线程没锁）+ 修完自己 xcodebuild 双 scheme 验。
- 13 commit 全本地**未 push**。AC：模式 2（多 AI 对抗复审）⭐顶级 + 不盲信 AI + Swift 6 并发实战。raw/dev_log `2026-06-09`。

## 🤝 多会话占用（避免冲突）

*当前无并行会话占用任何文件。*

> 如启动多会话并行：在此列出谁正在改哪些文件 + 开始时间，其他会话避让。改完登记完成移走。

---

## 🚧 阻塞项

*当前无阻塞项。*

> 阻塞项 = 等 itsuki 答复才能推进的硬卡点（如 Q1/Q2 字段对齐拍板）。无阻塞时本节为空。

---

## 🔒 多会话协调规则

### 会话标识（建议命名）

`[设备-主题]` 格式：`[Mac-主会话]` / `[Mac-mini-Opus 4.7]` / `[Mac-后端]` / `[Mac-iOS]` / `[Mac-Android]` / `[Mac-Web]` / `[Code-Agent]`。

### 避免冲突的硬规则

1. 每个「占用」任务必须标出涉及文件 / 目录
2. 其他会话不能动正在被占用的文件
3. **共享文件**（`CLAUDE.md` / `WIP.md` / `CHANGELOG.md` / `TODO.md`）：一次只能一个会话改，改完立刻 commit + push
4. 改 `WIP.md` 本身：先 pull，改完立刻 push
5. git conflict：停下来问 itsuki，不自己猜合并

### 关键文件边界

| 目录 | 归谁管 |
|------|-------|
| `03_dev/backend/` | 后端会话 |
| `03_dev/student_ios/` | iOS 会话 |
| `03_dev/teacher_web/` | Web 会话 |
| `03_dev/rollcall_device/` | 点呼机会话（Pi）|
| `01_specs/` | 一次只允许一个会话改（规格冻结区）|
| `00_admin/` | 主会话管理 |
| `05_logs/raw/` | 各会话写自己今天的，文件名不撞 |

---

## 📝 给新会话的上下文（关键信息）

读完 `CLAUDE.md` + 本文件 + `TODO.md` 顶部应该知道：

1. **当前版本**：见上方 + `CHANGELOG.md` 顶部
2. **上线姿态**（4-19 G2 决策）：取消分阶段；v1.0 直接 iOS + Android + 卡 一次上线
3. **防作弊核心**：动态 NFC 贴纸 ST25DV16K（10 秒 nonce）+ ECDSA 签名 + 老师监督 + 语音播报（原创设计 → `05_logs/decision_log.md`）
4. **版本体系**：0.x.x = 开发中，1.0.0 = 宿舍正式上线
5. **记录体系**：CC 侧 `00_admin/CLAUDE_CODE_记录指南.md`；总章 `AC入试记录指南_v3.md` 在 iCloud（CC 不读）
6. **文件地图**：`CLAUDE.md §目录结构` + `.claude/skills/project-overview/SKILL.md`（5-04 起替代已归档的 `00_admin/文件结构指南.md`）
7. **文档一致性**：声明性文件不写硬编码版本号，见 `CLAUDE.md §文档一致性规则`
8. **itsuki 偏好**：选项用 A/B/C 不用甲乙丙 / α β γ；决策他拍板；不盲从 AI

---

## 🕘 本文件自己的更新日志

- **2026-05-04 上午** — 加 2026-05-04 会话条目（A+B 文件联动工具建设）
- **2026-05-04** — 🔧 **大改 by [Mac-mini-Opus 4.7]**：itsuki 指出 WIP 跟 TODO 重叠 → 拍板方案 A → 砍「🔄 进行中的任务」section（218 行，跟 TODO 重叠）+ 砍「✅ 最近完成」长尾历史（170 行，commit history 已记录）+ 头部「最后更新」长串历史压缩到「最近会话」5 条 → 全文 600 → ~160 行；分工规则写明铁律「未完成的事只写在 TODO」；CC 启动流程加「扫 TODO 顶部 200 行」。备份 `/tmp/WIP_backup_2026-05-04.md`
- **2026-05-10** — 加 ac-radar 上线条目（共 6 条超 5 条上限）→ 砍 5-04 晚 iOS bug 修复条目（详见 raw/2026-05-04_iOS_bug修复.md）
- 更早历史 — 见 `git log -- 00_admin/WIP.md`

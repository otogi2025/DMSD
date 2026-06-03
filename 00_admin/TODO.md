# DMSD 待办清单

> **这个文件是给 itsuki 看的**,用来跟踪所有该做但还没做的事。
>
> - 和 `WIP.md` 的区别: WIP 是给 Claude 看的"当下在做什么 + 多会话协调",TODO 是给 itsuki 看的"还没做的所有事"
> - 和 `progress_overview.md` 的区别: progress_overview 是稳定的章节目录,TODO 是可以频繁增删的任务池
> - 完成的任务: 在 checkbox 前打 x,隔段时间(每周或每月)批量移到"已完成归档"

**最后更新**: 2026-06-03（**§📱 iOS 上架冲刺段重新校准** — 实测线上后端 `api.tomoshibi.cc` 在线但跑 5-08 骨架版（40 接口 / 本地 61）；itsuki 确认 3 事实：首次上架（5-08 卡 Validate 没提交）+ 开发者账号续费中 + 谷歌云服务器自付费在跑；拍板**公开上架** + 工作流「后端本地做完再一次性部署」+ 三阶段路线；今天 v1.0 功能范围：IX-007 不进 v1.0 往后堆 / 老师退回(差戻) v1.0 必做 / 学習対象字段要做 / 通知子系统完整方案（5 内容源 + push + 设置可关闭））。早些 2026-06-02（点呼机 ST25DV **架构反转**落地 — §R 加「🔄 架构反转后续」4 条（防代刷随反转简化（CC 初判「阻塞」被纠正：手机不联网→旧 nonce 多余）/ 连带 4 文件待简化 / 🟠后端三选一跟老师谈 / 人脸归 v2.0）+ §R 学习任务标进展（跟 Gemini 系统学过一轮）+ 作废「nonce 时间窗回填」任务（反转后 116 天伪问题消失）。详 decision_log + raw `2026-06-02`）。早些 2026-05-31（teacher_web v1.0 + 后端经 codex 5 轮复审收敛 0 blocker/major → 加 §🌐 follow-up 段 5 条：设计文档同步 / NFC 防代刷立项 / push 真投递 / 上线 ops / 低优先清理。详见 raw `2026-05-31_teacher_web_v1.0全实装+codex5轮收敛.md`）。早些 2026-05-30（全项目第二轮审查 — 多代理 workflow + Codex 复核 + 3 补审 → 175 条；§🐞 系统 Bug 专栏段加「2026-05-30 审查 backlog」8 条大工程；修 11 处小 bug commit `6cc5c07`；与 itsuki `/goal` 并行施工会话协调 + 收尾流程改进 session-wrap §7.6.7）。早些 2026-05-29（CC 扫项目推荐自动化 → 加 §🔌「上线时配置」段记 #7 连本地库 / #9 连线上库 / #10 Sentry，等上线提醒；建 Dependabot 依赖监控 + pre-commit 密钥扫描）。早些 2026-05-28 凌晨（跨夜会话 — 主体在 5-27 晚段-3：老师实名账户登录改造 + codex 5.5 xhigh 审查；§🚀-G 加 codex 剩余 4 项 itsuki 决策 / 大工程 + §🚀-D `/community` 行去「匿名建議」字眼跟 spec §7.14 拍板对齐）。早些 5-27 晚段-1 — anti-ai-flavor 双层防御立项会话加 §🛠️ §P 新段 5 条 — iOS 推进延后 / 环境清单 md↔html 同步 / Stop hook 首次实战观察 / 翻车案例库 v1.1 核对 / 5 铁律没升 8 类。起因：itsuki 启动 iOS → CC 报告状态翻车 3 处 → itsuki 主动提「立 hook 强制扫 + 白名单」方向 → 工程实装 3 新文件 + 2 改文件全在 ~/.claude/ 全局目录）。早些 5-27 早段（全项目审查会话加 §🛠️ §N 新段 8 条「全项目审查 backlog」+ 直接修 6 处 Vite 决策漂移 + 物理清 7 个 .DS_Store + git mv `student_ios/_archived_DESIGN_BRIEF_Round1_context.md` 到 99_archive；起因：itsuki 启动「全项目审查 — 每个文件 / 文件关联 / 关联 skill / 内容审查 / project-overview 检查全跑」强调「不要偷懒 + 扫整个项目所有文件 + 不要给我留问题 + 所有问题加 TODO 里」）。早些 5-27 深夜（14 件 TODO 小活批量清：6 件本来就闭合 TODO 没刷状态 / 7 件真做 / 2 件挂起等拍板。详见 WIP.md 顶部「最后更新」概要）。早些 2026-05-26 晚段-4（§🛠️ 加 §L 新段「teacher_web Vite 废弃 + Ryō polish 回滚残留」5 条 — 写 demo_server.py 恢复 NFC 实时点呼 / 系统bug专栏 FC-025/26/27/28 标 N/A / 未来 polish 候选方向 4 个 / WEB_DESIGN_LOG §7+§10 复核 / DESIGN_BRIEF §3-§8 复核；同时改 §🚧 主会话保留 6 条 A-039（vite 验证 N/A → Ryō standalone 直接验证）+ 改 line 888 ✅ S15 标反转（Vite 实装废弃）+ §K「WIP 加本会话条目」标 ✅ 完成；起因：itsuki 启动 teacher_web 推进 + 看到 Vite 实装版怒怼「不是我的 web」拍板「垃圾归档用 B」+ frontend-design polish 试做后整体不喜欢一句「回滚」全退）。早些 5-26 晚段-2（§🛠️ 加 §K 新段「启动 SOP 集中化 + CLAUDE.md 重写残留」5 条 — 全局环境清单同步 / ~/.claude/ git repo propose 强化 / 其他 5 项目启动 skill / sync-check bin-script 警告 / WIP 加本会话条目；起因：dmsd-startup skill 立项 + DMSD CLAUDE.md 247→190 行重写到 QTS 模式 + 6 项目 CLAUDE.md 加沟通铁律「不主动用英语名词」+ destructive-bash 行为约定 + CLAUDE.md 文档观转变（时间戳冗余禁止））。早些 5-25 晚段（§🛠️ J 加 2 条新待办 — 触发词「翻车」首次实战测试 + inbox 累到 3-5 条后写「整理 inbox」SOP；起因：anti-ai-flavor skill 加第 3 触发词「翻车」单字 + 新建 `~/.claude/skills/anti-ai-flavor/inbox.md` — itsuki 收尾中途立项自我迭代机制）；早些更新：2026-05-25（5-25 drift 修 + session-coord 三层保险会话加 §📊 project-overview 历史欠债 2 条 + §🐚 shell 工具链 quirk 1 条 + §🛠️ J 首次创建 6 条）；2026-05-24 5-22 修漏洞会话补 §🎯 D1-D5 + §📁 / §💾 标 ✅ + 加未 push 37 commit；5-22 §🛰️ 点呼机段配件采购方向反转 — 5-12~16 中国海关查扣 → itsuki 拍板撤回中国海运 → 日本本地买 / 原 11 件淘宝清单 + 2 任务作废 / 加 6 条新待办；2026-05-21 加 §🐞 系统 Bug 专栏入口 131 条 / 清 §⏰ Cloud Design 5-12 过期项；2026-05-14 §🛠️ G + H；2026-05-13 §🛠️ E + F；2026-05-11 §📄；2026-05-08 §📱 + §🛰️ + §🐛<!-- VERSION_OK -->
**当前版本**: 见 `CHANGELOG.md` 顶部 · 单源真值，见 `00_admin/文档同步点清单.md`

> **2026-04-17 归档说明**：`executable_dev_checklist.md` 已归档到 `99_archive/2026-04-12_executable_dev_checklist.md`（内容已过期，功能被本 TODO.md 吸收）。

---

## 🎓 AC 升学素材整理 + 升学文件夹结构完善（🔴 高优先 — 2026-06-03 itsuki 拍板加）

> itsuki 要做两件事：① 把已堆的 AC 入试素材整理一遍 ② 把 iCloud 升学文件夹结构理顺。
> 当前素材分布：ac-radar skill `SKILL.md` §二「四级流水线」是规则；实际文件在 iCloud `.../升学/.../筑波大学 AC入試 準備/06_radar_inbox/` 下（普通区 `ac_scratchpad_*.md` 一堆 + 高权重区 `_priority_itsuki主动提报/` 现有 4 个 md：5-27 注册默认值 / 6-03 点呼机硬件 / 6-03 Codex 增量 / 6-03 iOS 动画黑屏）。

- [ ] **统一两个真目录** — `iCloud/.../升学/` 下有两个真目录（不是别名）：`AC/` 和 `大学入試/`，各有一份 `筑波大学 AC入試 準備/`。AC 收集箱（`06_radar_inbox/`）写在 `大学入試/` 下，会话存档（daily-archive 脚本）写在 `AC/` 下，两套配置不一致、将来容易写串。三选一：(a) 统一到 `AC/` 改 session-wrap 路径 (b) 统一到 `大学入試/` 改脚本 (c) 确认一个是废弃残留直接删。**（吸收下方「🛠️ Skill/Hook 工具后续」段原第 2 子段 + §🏁 收尾里 daily-archive 目录树不统一两条待拍板 backlog）**
- [ ] **整理收集箱积压** — 普通区从 5-10 到 6-03 攒了十几个 `ac_scratchpad_*.md`，还没往右搬到 `03_素材_候选/`。itsuki 择期挑哪些值得留。
- [ ] **完善文件夹结构** — 四级流水线（`06_radar_inbox/` → `03_素材_候选/` → `04_素材_成品/` → `05_产出/`）是否够用、要不要再细分类、高权重区 `_priority_itsuki主动提报/` 怎么跟普通区长期共存 —— itsuki 定方向，CC 执行。

---

## 🌐 teacher_web v1.0 收敛后 follow-up（2026-05-31 加）

> teacher_web + 后端经 codex 5 轮复审收敛 0 blocker/major（后端 193 测试）。详见 `05_logs/teacher_web_v1.0_W8审查findings.md` + raw `2026-05-31_teacher_web_v1.0全实装+codex5轮收敛.md`。剩这些非阻塞 follow-up：

- [ ] **设计文档同步** — 6 新模块（events/bus/guidance/incidents/student_profile/student_promote）+ push 没进 `BACKEND_DESIGN_LOG.md` / `system_features.md` / `WEB_DESIGN_LOG.md`，要补
- [ ] **NFC 防代刷后端立项** — 计划已写 `02_design/NFC防代刷_后端立项施工计划.md`（细化 §🐞 A-010）；后端可独立先做 nonce 表+端点+ECDSA 验签+卡绑定表（6 步），硬件/iOS 联调等贴纸到货 + iOS 加签名字段
- [ ] **push 推送真投递** — 后端只有骨架，真投递要 APNs/FCM 凭证 + iOS/Android 集成（client 上报 device token + 处理推送）
- [ ] **上线 ops** — 按 `04_ops/teacher_web_v1.0_上线部署清单.md` 设环境变量 + 建表 + seed + serve
- [ ] 低优先：index.html 残留死注释（提及已删的 ROSTER/TEACHERS 名字）+ `client.ts` 跟 `client.js` 漂移的历史死文件清理

---

## 🐞 系统 Bug 专栏（v1.0 上线前 — 5-20 审查作战产出）

> **131 条 bug 详细管理见**：[`00_admin/系统bug专栏.md`](系统bug专栏.md)
> - 🔴 阻塞上线：43 条（v1.0 前必修）
> - 🟡 该修：58 条
> - 🟢 优化 / 信息：30 条
>
> **来源**：3 子代理并行审 15+ 维度（2026-05-19 启动 / 2026-05-20 凌晨 cron 自动 fire / 5-21 itsuki 拍板专栏化管理）
> **完整 findings**：`05_logs/audit_2026-05-19/session_{A,B,C}_findings.md` + `_master_issues.md`
>
> **TOP 5 最紧急**（详见专栏）：
> 1. 🔴🔴🔴 [A-039] teacher_web 老师密码全员明文（public repo 已暴露）
> 2. 🔴 [B-013/C-001] CLAUDE.md 路径错位（每次会话受影响 — 一行修）
> 3. 🔴 [A-010] backend NFC 防代刷一行未实装（v1.0 上线最大隐患）
> 4. 🔴 [A-001~005] backend auth 5 处漏洞集中爆发
> 5. 🔴 [C-007~009] README + progress_overview 严重过期

> **🆕 2026-05-30 第二轮全项目审查**（多代理 workflow + Codex 复核 + 3 补审 → 175 条）：
> - ✅ 已修 11 处（iOS 安全 2 + 后端崩溃/校验/越权 + 文档死链；本会话 commit `6cc5c07` + 并行 /goal 会话 `d9e65f1`）
> - ✅ **2026-05-31 续修**：角色名用字 + 三端隐私清理 + Android 4 小 bug + 后端 4 小 bug + 实时广播架构(rollcall-06/applchain-12) + Codex 反馈批，每阶段派 Codex 5.5 xhigh 审。
> - ✅ **2026-06-02 itsuki 决策批 + Codex 双轮终审收敛**：扣分值 0.5/1.0 + 改判按当前状态重算 / 密码后端 8 位 / 注册码 30 分自动失效+手动关闭（拒绝「一次性」）/ 晚自习 3→2 次签到 / tier 月累计≥4 罚扫 ≥8 禁足 / demo 假学号注释改架空サンプル。后端 commit `ef1c910`+`6142ef0`、iOS+Android `a3eceda`。
> - ⏳ **iOS 晚自习 2 次签到收尾 gap（本会话已改在磁盘、未提交）**：`MyPageStubs.swift` 3 处 `count==3`→`StudyTap.allCases.count` + `AppStore.swift` `studyAttendance` 的 `.done` 分支提前判异常。**跟并发会话 ix-008b 接线挤同文件、未从我这边 commit**（怕卷走对方半成品）→ 等那窗口提交 ix-008b 时一并带上，之后 `xcodebuild` 验证一次。
> - 🔴 **未修大工程 backlog**（v1.0 上线，几天–几周实装，非「修 bug」能解决）：
>   1. NFC 防代刷全栈（card_uid↔学生绑定 + 10秒 nonce + ECDSA 签名 + 点呼机 src 实装）— 后端 + iOS + Android + 点呼机**全空**
>   2. Android 整个无网络层 → 接后端要从零写
>   3. iOS 点呼 / 6 类申请接后端（RollCallAPI 死代码 + ApplyPreview 假提交，只弹 toast 不发后端）
>   4. 删账号 `DELETE /accounts/me`（苹果强制 + iOS 已调用；/goal `admin_accounts.py` 可能在做账号管理）
>   5. 后端写接口寮越权校验（/goal 正逐个修：discipline / dorm_unit 已修，rollcall/cleaning/front_desk/applications/study 待确认）
>   6. 学生登录失败锁定（auth-account-03）— 注册码「一次性」(auth-account-04) itsuki 06-02 拍板**拒绝**、改 30 分+手动关闭已实装，本条只剩登录锁定
>   7. spec 冻结区文档过期（DEVICE_REGISTRY 旧型号 RPi 4B / ENUM 缺 manual / RollCall_Spec 路径 C / ERROR_CODES 状态码）— 规格冻结区需 itsuki 解冻后改
>   8. progress_overview 严重过期（VPS 架构图 / GitHub 写成私有 / 独立 repo 残留 — 跟 §16 上面 C-007~009 同源）

#### 🔢 版本号 bump（itsuki 06-02 批准、待并发会话安静后做）

- [x] ~~走 `.claude/skills/version-bump` SOP~~ ✅ 2026-06-03 做了核心（commit `48e7c97` + `e91e768`）：回溯补 6 个标签 v0.8.1~v0.12.0（按 SemVer：每段有真新功能=次版本号 / 纯修复或工具链=修订号）+ CHANGELOG 6 条目 + WIP 当前版本→最新 + 三端客户端版本号统一。**没等并发会话停手** — 它改的是 iOS/点呼机/file-linkage，跟 CHANGELOG/WIP/客户端版本号文件不重叠，没撞。剩 `README.md` / `index.html` 版本号改动跟并发会话叠在工作树，待整理一起 commit + push。<!-- VERSION_OK -->
- [ ] **CC 后续小活（6-03 收尾留）**：`version-bump` skill（§0.2 / §4 第 3 项 / §13）把 `00_admin/版本演变一览.md` 列为「每次 bump 必改铁律文件」，但该文件实际不存在，`CHANGELOG.md` 已承担版本编年史职责。下次 bump 前把 skill 这几处改成指向 CHANGELOG 或删掉，免得再绊一下。

#### 🟡 2026-05-30 审查「能直接改、还没排到」的小 bug（可 xcodebuild / pytest 验证 — 从已删 handoff 并入 2026-06-02）

> 原 `05_logs/audit_2026-05-30/` 三个文件（findings.md 175 条 / 修复进度交接.md / itsuki决策批_自审清单.md）已并入本段并删除，完整 175 条原文可从 git 历史取回。下面只列还没做的。

- [ ] **iOS 小 bug**（能编译验证、安全）：ios-community-04（死字段 up/down）/06（数组下标当 id）/07（fallback 首条）/08（日历写死 4-5 月）/09（写死假内容）/11（认领无核验）/12（死方法）；ios-home-05（日期写死 4/22）/07（时间写死 21:02）/08（联系人写死）/10（公告回复静默失败）；iosmypage-07（月度未过滤）/08（详情假数据）/09（总分写死）/11（中文「快递」）/12（删号后视图栈）；ios-auth-09（splash 只验 token 存在）；ios-staylist-05（audit 静默吞）/06（mock chain 造假）/07（actor_type 粗暴）；ios-schedule-04（firstIndex??0）
- [ ] **老师网页**：teacherweb-05（client.ts 死代码删）、teacherweb-09（WebSocket 令牌走 URL 不安全 — 需后端鉴权配合，中等）
- [ ] **后端要 migration（改 DB 约束，中等）**：models-entry-05/06/07/08/10/11/12/13（外键 / CHECK 约束 / server_default / append-only 防改 / Float 阈值）；rollcall-05 残余（点呼手动/NFC 无幂等键并发双写 → 需 PostgreSQL 部分唯一索引 `(session_id, student_id) WHERE idempotency_key IS NULL`）
- [ ] **迁移与测试**：migtest-01（测试不跑 alembic）/04（审批链没测）/05（永真断言）/06/07（断言恒真）/08/09/10
- [ ] **文档**：sysfeat-05（category 用 ENUM 还是 Text）/06（时间窗硬编码）/10（旧时刻 19:30）
- [ ] **Codex 补测试建议**：broadcast_sync + run_coroutine_threadsafe 新路径补回归测试 / `POST /teachers` valid+invalid email API 测试 + teacher_web 前端兼容 422 detail list / WebSocket dorm_unit=2 广播过滤补回归测试

> **2026-06-02 过夜 GOAL 进度**：✅ iOS 安全批 4 个已修（ios-home-05 首页日期 / ios-home-10 公告回复失败 toast / iosmypage-11 快递→荷物 / ios-staylist-05 audit 失败 toast，commit `13f5a01`；iosmypage-12 早被 IX-002 修）。✅ 文档 sysfeat-05/06 已修（`797d16f`），sysfeat-10 查证已对齐。✅ migtest-05/06/07/10 查证前序会话已修（代码注释引用 migtest-ID）。⏸ **后端 migration 批（models-entry-05~13 + rollcall-05）+ 其余 demo 耦合/潜伏 iOS bug 全推迟** —— schema 改约束有风险 / 多 PG 专属 SQLite 测不了 / 多要拍板（接后端 + 功能上不上线），理由逐条见 `05_logs/ios接后端_进度与handoff.md` §7.3。

#### 🔵 2026-05-30 审查「需 itsuki 拍板」（部分本批已决，剩下面这些 — 从已删 handoff 并入）

- [ ] **体調報告履歴 + 掃除提出履歴**两屏 Android 没实装（androidrest-05，入口跳首页）→ v1.0 要不要做？不做就删入口。（itsuki 06-02 倾向暂不做）
- [ ] **注册密码下限 Android 端对齐**：后端已改 8 位，Android 界面/代码（android-base-07 / androidrest-07）待对齐成 8 位
- [ ] **git 历史**里旧邮箱/手机号要不要重写清除（BFG / filter-repo）？建议不做：提交身份邮箱本就公开、当前源码已清、代价大
- 已决（不用做）：リュウイヒ + 学号 060218 保留当本地 demo + 注释已改「架空サンプル」/ 注册码 30 分+手动关闭（拒绝一次性、6 桁熵 itsuki 接受）/ sysfeat-02/04/09/11（flow_design 签到模型 / URL 域名 / 注册码限流 / audit log v1.1）暂不做

#### ⚪ 2026-05-30 审查「未核实」（下次补核实再判 — 从已删 handoff 并入）

- [ ] **iosmypage-01~12 + ios-schedule 全部** — 第一次核实 workflow 这两单元子代理没返回，状态未知，下次要补核实再分类

---

## 🔌 上线时配置（CC 自动化推荐 — 等后端真上线 / 真用起来再做）

> 2026-05-29 CC 扫项目推荐自动化时，itsuki 选了几个"连数据库 / 上线监控"类工具。
> 它们现在建不了或没意义（服务器 / 线上数据库还不存在），统一记在这，等上线时配。
> itsuki 原话："上线我大概率会忘，现在记下来，到时你提醒我。"
>
> **触发提醒**：itsuki 说"要上线 / 部署后端 / 买服务器"时，CC 主动翻出本段逐条问。

- [ ] **连本地数据库（SQLite MCP）** — 等后端真用起来、本地库有真实数据后加。让 CC 能直接查 `03_dev/backend/v1/tomoshibi_dev.db`（现在只有 2 个练习学生，加了没意义）。装法：`claude mcp add tomoshibi-db --scope local -- uvx mcp-server-sqlite --db-path <库路径>`
- [ ] **连线上数据库（PostgreSQL MCP）** — 后端部署到服务器、有真 PostgreSQL 后加。让 CC 能直接查线上数据。
- [ ] **上线后崩溃监控（Sentry）** — App 上线后加。需先注册 Sentry 账号拿一个连接串（DSN = 一串地址 + 密钥），再在后端 + 客户端接入，程序崩了自动报给 itsuki。

---

## 🆕 v1.0 后新功能候选（2026-05-21 itsuki 提）

> 这一段记 itsuki 想加但**当前不在 v1.0 上线必做范围**的功能。每条带场景 + 设计点 + 完成定义。等设计层评估完再决定 v1.0 加 / 推到 v1.1。

### N-001 — Web「开始点呼」按钮自动状态切换

- **场景**：老师忘按开始点呼
- **行为**：距固定开始时间还有 3 分钟时，Web 上「开始点呼」按钮自动变「点击查看点呼」（或后端自动开点呼场次让学生能 tap）
- **设计点**：
  - 前端定时器轮询「下一个点呼场次开始时间」
  - 后端可能要加 `auto_started_at` 字段区分手动 / 自动
  - UI 状态机：未到 → 即将开始（< 3 min）→ 进行中 → 已结束
- **完成定义**：老师即使忘按，到固定时间点呼也能正常进行 + 老师能事后看进度

### N-002 — 规则外特殊点呼（一次性）

- **场景**：突击点呼 / 特殊日子（运动会前夜 / 紧急集合）
- **行为**：老师能开启「自选窗口时间 + 自选迟到判定时间」的临时点呼
- **设计点**：
  - `rollcall_session` 表加 `is_custom: bool` 字段
  - `is_custom=true` 时窗口时间走自定义字段（不走每日固定 schedule）
  - 老师 UI 加「特殊点呼」入口（独立于每日点呼）
- **完成定义**：老师能临时点一次特殊点呼，学生收到通知 + 能按时刷

### N-003 — 老师 Web `/discipline` 加「被锁定学生通知」card（2026-05-26 从 iOS §9.3 转过来）

- **来源**：原 `03_dev/student_ios/IOS_DESIGN_LOG.md §9.3` 跨文档同步条 — 标 ⏳ 未做，5-26 复查归类为 Web 端工作（iOS 侧不动），从 iOS §9 转到 Web TODO
- **场景**：学生因连续误操作 / 密码错误被系统锁定 → 老师在 `/discipline` 页面看不到，无法主动联系学生 / 解锁
- **行为**：`/discipline` 页面加一个 card 列出「当前被锁定的学生」（番号 / 氏名 / 锁定时间 / 锁定原因 / 锁定升级阶段 1-6），点击进详情走「アカウント解除」流程（已有，在 `accounts.jsx` 详情 modal 里）
- **设计点**：
  - 后端要有「列出当前被锁定学生」endpoint（可能复用现有 `accounts.jsx` 用的 status 字段过滤 `status=locked`）
  - card 位置：`/discipline` 页面顶部 banner 区，跟「今日违规清单」card 并列
  - 锁定升级阶段（IOS_DESIGN_LOG §3.5 §3.6 6 阶段定义）要在 card 上显示
- **完成定义**：老师打开 `/discipline` 一眼看到「现在有几个学生被锁了 / 分别是谁 / 锁多久了」+ 一键跳到解锁流程

### N-004 — 出租车预约（タクシー予約）4 端实装（2026-06-03 itsuki 提）

> **✅ 2026-06-03 大部分实装 + codex 5.5 xhigh 审查通过**：后端（`applications.taxi_reservation_time` + migration `a7b8c9d0e1f2` + 223 测试绿含 2 taxi）/ iOS（`StayForm` 外泊·帰省·帰国 提交 + 详情显示 + 外出 UI 桩，双 scheme BUILD SUCCEEDED）/ 老师网页（「タクシー」tab 实装 + 详情字段 + badge 防漏看，check_jsx 0 错）三端**前后端对齐完成**。codex 审出 1 阻塞（migration 编号撞既有 events，已换 `a7b8c9d0e1f2` + `alembic heads` 验证单 head）+ 3 建议（帰国教师详情误显行先都市 / 修改届 taxi 名义 / tab sub 共享）**全部已修**。
> **剩待办**：① Android ⏳（Compose 骨架未接后端，待接后端时一起做，详见 `ANDROID_DESIGN_LOG.md §10`）；② **修改届改/取消 taxi**：现 create-only（新建填、改不了），改/取消需三态语义「未设置=不改 / 字符串=改 / null=取消」+ `StayEditForm` 加 taxi UI（codex 6-03 指出）。下面是原始设计记录。

- **场景**：学生外出 / 外泊要坐出租车去车站等地，希望在手机上直接预约，老师能提前知道并安排车
- **行为**：
  - 学生 iOS / Android：在「外出」申请 + 「外泊」出寮届表单里能勾选「预约出租车」，填**想坐车的时间**（只填时间，跟申请本身的日期 / 回寮时刻无关）
  - 老师 teacher_web：后台能看到所有出租车预约（谁 / 几点 / 去哪）
  - 防老师漏看：老师**主页**醒目显示待处理的出租车预约（思路同 N-003 锁定学生 card）
- **设计点**：
  - 后端要决定怎么存：① applications 表加字段（如 `taxi_reserved: bool` + `taxi_time: time`）还是 ② 单独建一张出租车预约表。**注意现状**：外出（outing）走 `GenericApplyForm`，现在是纯演示桩**根本没接后端**（后端 `schemas.py` 的申请类型 `Literal["帰省","外泊","帰国"]` 只认三种过夜外出，不认当日外出）；外泊（stay）走 `StayForm` 已接后端。所以这功能落地前，外出本身要先接后端
  - 跨「外出 + 外泊」两种申请类型都要支持
  - 老师主页加一个出租车预约提醒 card
  - 通知（可选）：预约成功 / 老师确认后通知学生，跟通知子系统整合
  - 关联：外出申请的「出行方式（交通手段，UI 上是「電車 / バス / 車 / 徒歩 / その他」）」itsuki 6-03 确认**保留**；出租车预约是独立于出行方式的附加功能
- **完成定义**：学生在外出 / 外泊申请里能预约出租车并选时间 → 老师后台 + 主页都看得到 → 4 端（iOS / Android / teacher_web / 后端）字段对齐

---

## 🔧 下次会话接续清单（2026-05-21 — 这次会话 compact 前的状态）

> **2026-05-31 iOS 接后端会话留**（IX-004 修改届 ✅ 关闭 / IX-008 当前用户 ✅ 身份接完）：
> - [x] ~~**IX-008 Codex 独立审查待补**~~ ✅ 2026-06-02 完成 — Codex 5.5 xhigh + Claude 4 维对抗审查双路独立跑、结论一致（🔴0 / 🟠3 / 🟡2）。修 5 处：注册补 loadMe / loadMe 健壮性(401清令牌+登出竞态+#if DEMO) / 注册第一步加 #if DEMO 守卫 / MyInfoEdit 预填迁 displayUser / deps.py 畸形 sub 返 401。后端 214 / iOS 双绿。**代码撞并发 git add -A 卷进 commit `6142ef0`**（消息对不上号但代码完整）。详见 handoff §4.0。
> - [x] ~~**IX-008 Batch 2 — 剩余身份站点迁 displayUser**~~ ✅ 2026-06-02（`d21a2b8`）— MyPage/Apply/StayList 身份展示站点迁 `app.displayUser` + 登出 `#if !DEMO` 清 changeLog/announcements 等。**残留低危**：3 表单 @State 预填（contactPhone/roomNo，登录路径已真实、仅冷启动窗口旧）+ MyPointsView 图表（router-only 靠安全网）→ 彻底干净需给 3 表单加 `.onAppear` 从 displayUser 填。详见 handoff §4.0 Batch 2。
> - [x] ~~**IX-008b 扣分统计接入**~~ ✅ 2026-06-02 全做完 — 后端 `GET /discipline/me/summary`（`0f84be9`）+ iOS `DisciplineAPI.mySummary` + loadMe 填 currentUser 统计（`d21a2b8`）。真人现显真实当月扣分/迟到/欠席（按当月算）。详见 handoff §4.0b。
> - [x] ~~**IX-034 请假计数按月接入**~~ ✅ 2026-06-02 代码提交 `e0c150c` — 后端 `GET /study/absence-requests/me/summary`（当月 target_date 全状态计数）+ iOS loadMe 拉真实当月数替代内存累加 + 3 测试。后端 220 / iOS 双绿。**Codex 5.5 xhigh 审出 4 点待修**（跨月仍 +1 / loadMe 令牌竞态 / 测试时区 / formatYMD）→ 过夜 GOAL 第一件事修。详见 handoff §7.1。
> - [ ] **IX-009 通知 + IX-007 详情页**（B 类接后端剩余）→ 过夜 GOAL 自动推。IX-009 聚合公告+审批（包裹要后端新建 `GET /front-desk/mine` 跳过）；IX-007 走 Option A 降级 DEMO（其它类后端零实装）。详见 handoff §4.2bis + §7。
> - 🌙 **2026-06-02 过夜无人值守 GOAL 运行中**（itsuki 睡觉）：修能自动修的 bug + 接后端，遇要决策的跳过记 handoff §7.3。运行规则 + 修完/待决策清单见 handoff §7。
> - [ ] **老师「退回(returned)」动作未实装** — 后端 `decide_approval` 的 `_recompute_application_status` 只产 rejected/approved/approved_partial/pending，**产不出 `returned`**（spec §7.2.4-5 要的「老师退回让学生改」没做）。我已让修改届允许编辑 returned（前向兼容），但要真闭环需后端+teacher_web 加「差戻」决策。
> - [ ] **学習対象 is_study_target 后端字段** — IX-008 iOS isStudyTarget 默认 false（老师后台手动设的才是）。但 `/me` 没返这 flag，将来老师能在后台设时 `/me` 要带上（StudentProfileBasic 加 is_study_target）。
> - 详细进度：`05_logs/ios接后端_进度与handoff.md`

> 本次会话：4 会话审查作战 — Claude 3 子代理后台跑找 131 条 findings + 主会话修 10 条 + Fix-Bot 1/2/3 修 67 条 + Fix-Bot 4 effective_* 删后台跑中。

### 🔥 紧急 — 下次会话立刻看

- [x] ~~**Bot 1 闯祸 — 30+ iOS 编译错误**~~ ✅ 2026-05-22 验证是 SourceKit（编辑器单文件检查器）误报 — 真实 `xcodebuild` 编译全过。详见 `raw/2026-05-22_iOS_fork融合.md` §21:45

### ⏳ Fix-Bot 4 后台跑中

- [ ] **Fix-Bot 4 effective_* 字段彻底删** — 5-21 itsuki 拍板 (b1) 现在删
  - 任务 ID：`a7992274892f10ae5`
  - 范围：5 端代码 + spec + 字典 + alembic 迁移 + 测试
  - 完成后看：`05_logs/audit_2026-05-19/_fixed_4.md`

### 🤖 Codex 第二轮 audit

- [ ] **itsuki 用 `00_admin/codex_audit_prompt.md` 喂 codex 跑全量审查**
  - prompt 已写好（含 27 必读文件 + 17 审查维度 + Claude 漏的 4 类重点）
  - 输出：`05_logs/audit_2026-05-21_codex/session_codex_findings.md`
- [ ] codex 跑完后跟 Claude 131 条对照（重复 / 独立 / Claude 漏 — 分类）

### 📋 系统 Bug 专栏状态更新

- [ ] **系统bug专栏.md 77 条已修标 ✅** — 主会话 10 + Bot 1 33 + Bot 2 12 + Bot 3 22
  - 当前文件这些条还是 ⏳ 待修 — 状态字段没更新
  - 修完时填 commit hash（commit 后）

### 🚧 主会话保留 6 条（架构决策）

- [ ] **A-001~005** backend 鉴权 5 处漏洞集中处理（需要 itsuki 设计层拍板）
- [ ] **A-010 / A-028** NFC ECDSA 防代刷实装（v1.0 决策性 — 二选一 完整实装 / 砍降级 v1.1）
- [ ] **A-002** HS256 → RS256 迁移（架构层）
- [ ] **A-035** iOS Auth magic value "000000" 注册流程后门（怕误删，需要 itsuki 拍板）
- [ ] **A-039** teacher_web v1/src/index.html 7774 行 standalone HTML — 含明文密码 `12345678` v1.0 上线前必删（**5-26 修订**：vite 整体废弃，「vite 验证」N/A；现在改成 Ryō standalone 直接验证 — 改完密码用 `./tomoshibi start` 浏览器 reload 看）

### ⚠️ Bot 3 跳过的待决策 5 条

- [ ] **C-035/036** 跨项目 DMSD 残留（Bot 3 判断「合法历史」— itsuki 拍板是否复核）
- [ ] **C-037** cc-project-template 6 skill 工程量大 — Bot 3 只清 1 个，剩 5 个跳过
- [ ] **B-018** `feedback_llm_self_discipline_unreliable.md` memory 写（需要 itsuki 同意才写）
- [ ] **C-031/033** raw 5 月各文件缺「## AC 信号」双写段（等 itsuki 拍板要不要补）
- [ ] **C-028/C-029** decision_log + project_evolution 4-15 后空白（itsuki 自写铁律 — CC 起草 draft 等粘贴）

### 📁 文件加 project-overview 引用

- [x] ~~**`00_admin/系统bug专栏.md`** 加进 `project-overview/SKILL.md`~~ ✅ 2026-05-22 完成（§1.2 已加 + 含 Codex 段说明）
- [x] ~~**`00_admin/codex_audit_prompt.md`** 加进 `project-overview/SKILL.md`~~ ✅ 2026-05-22 完成（§1.2 已加）

### 📊 project-overview 历史欠债（2026-05-25 加）

- [ ] **§6.2 raw 标题数漂**：§0.1 体量表写 raw 50+5（含 5-24/5-25），但 §6.2 章节标题还停在「48 文件」+ 描述写「5-16 ~ 5-21 4 个新增 raw 未 commit」— 至少 4 个 raw 没列进章节本体（5-22 / 5-22-iOS / 5-24 / 5-25）。下次 project-overview 大整理时校准 §6.2 标题 + 描述

### 🐚 shell 工具链 quirk（2026-05-25 加）

- [ ] **`git ls-files` 中文文件名 NFC/NFD 怪行为**：本会话调查 drift 漂移时发现 `git ls-files | wc -l` = 1122 / `sort -u` 后 1120 / `sort | uniq -c` 显示 6 个 path count 2 / `grep -c "^<path>$"` 显示该 path 只 1 次 — git index 实际每个 path 只 1 份（`git ls-files --stage` 验证），是 shell `uniq` 在中文文件名 Unicode normalization（NFC/NFD）上的怪行为，不是 git 真重复。**当前不动 git 状态**（避免改坏仓库 + 不是真问题），记备查。如果以后想根因，可以查 git 仓库的 NFC/NFD 设置 + macOS HFS+ filename encoding 历史。本会话已修脚本侧口径（删 `sort -u` 统一成 `sort | uniq -c`）规避脚本误报

### 💾 commit + push

- [x] ~~**77 条修 + Fix-Bot 4 effective_* 删 + 5-21 hook 修** 全部未 commit~~ ✅ 2026-05-22 完成（5 commit 落地：`8e584b9` / `29fc7e6` / `3f65331` / `7120c53` + 多个修漏洞会话 + iOS 会话 + 点呼机会话 commit）
- [x] ~~itsuki 拍板 commit 时机~~ ✅ 5-22 拍板「全都做」commit 一波
- [ ] **当前累积未 push commit：37 个**（origin/main ahead 37）— 全局铁律：CC 不自动 push，**等 itsuki 说「推一下」**
- [ ] 全局铁律：CC 不自动 commit / push

### 🎯 5-22 修漏洞会话留 — 等 itsuki 拍板 5 大决策（2026-05-22 加）

> 本会话「继续修项目漏洞」做了 12 件文档 / 工程治理修。剩 5 件大决策必须 itsuki 拍板才能推：

#### D1. spec 改了要不要 bump 版本号
- `RollCall_Spec.md` + `API_CONVENTIONS.md` 改了 FC-017（旧 `/api/v1/checkin` → `/api/v1/rollcall/sessions/{session_id}/checkins`），按 `version-bump skill §10 4 问` 算实质改动
- 选项：(a) bump v0.8.1 / (b) 攒一波别的改动再 bump v0.9.0 / (c) 跟下次 backend FC-* 修一起 bump <!-- VERSION_OK -->

#### D2. C3 `system_features.md` 引用废 repo `Tomoshibi-iOS`（[C-011]）
- `02_design/system_features.md:47,59,61,67,70,75` 6 处引用 `~/dev/TomoshibiiOSApp/`（5-06 已退役独立 repo 模式）
- 留下次会话单做（system_features 别会话频繁改避免冲突）

#### D3. D 段 `cc-project-template` 跨项目 DMSD 残留（[C-037] / [FC-036]）
- `~/dev/cc-project-template/.claude/skills/` 6 skill 共 45+ 处 DMSD / Tomoshibi / itsuki / 筑波 AC 内容
- 工作量：30-60 分钟跨项目修，需先 `cd ~/dev/cc-project-template/`
- 选项：(a) 5-22 接着做 / (b) 排进下次专项会话 / (c) Tango 真用模板时再修

#### D4. Codex 段大决策（之前留的 4 个）— 影响 v1.0 上线范围
- **[FC-010]** App Store 要求的账号删除 → 进 v1.0 还是 v1.0.1？<!-- VERSION_OK -->
- **[FC-016]** NFC ECDSA + nonce → v1.0 (a) 完整实装 / (b) 砍降级 v1.1 <!-- VERSION_OK -->
- **[FC-005~015]** backend 代码层修法（pytest 收集失败 / `timedelta` 缺导入 / 学生 checkin endpoint 权限 / `minute-5` 整点崩溃）→ 等 backend 会话还是 itsuki 自修
- **[FC-011 续]** `config.py` 的 `_FORBIDDEN_JWT_SECRETS` 集合扩展（防止 `.env.example` 长字符串复制后绕过）— 算 backend 代码层

#### ~~D5. Bot 1 iOS 烂摊子复盘~~ ✅ 2026-05-25 复查完
- 5-22 iOS 会话已修主体（`46f779c` backport + `84e2490` 删 magic value "000000" + `f2a6730` 字段对齐 + `6aaa928` demo scaffold 删）
- ✅ **2026-05-25 Bot 1 复查会话**：全量 diff 备份 fork vs 主项目 v1（两边各 42 个 Swift 文件 / 9 差异文件 / 3 fork 独有上架文件）— **没遗留误删的真功能**。4 处删除全在 `project_demo_scaffolds_to_remove_before_v1.md` 清单内 Bot 1 删对了（A-030/033/037/038）；剩下都是 swiftformat 格式整理 / 5-22 后主项目新加（A-019/036 + FC-020 + RollCallAPI）。详见 `raw/2026-05-25.md`

---

## ⏰ 时间敏感 — 即将到期

*（暂无 — 5-21 清理）*

- [x] ~~**2026-05-12 截止**：用掉 Cloud Design 40 额度~~
  - **2026-05-21 归档**：截止已过期 9 天，额度已浪费（5-13 凌晨刷新）— B-001 修复

---

## 🛠️ Skill / Hook / 工具后续（2026-05-11 晚加）

### 联动系统 sync-rules.sh 3 个预先存在问题（2026-06-03 codex 审查发现）
> 6-03 补联动盲点后派 codex GPT-5.5 xhigh 审查揪出，都不是本次改出来的、超范围当时没修，记这等处理。

- [ ] **D1 `_check_demo_scaffold` 返回值反转**（真 bug）— `sync-rules.sh` 函数 return 0=没触发 / 1=触发，但调用处 line 314 `if 函数; then count++` 在返回 0 时才计数 → 触发警告反而不计数。警告文字照印（echo 在 return 前）但内部计数错；triggered_count 当退出码可能被 commit 拦截用到，改前要查清谁用这退出码、乱改有风险。修法: 调用处加 `!` 取反。2026-06-03 创建 / CC 已验证确实反了。
- [ ] **D2 Rule 6 design-doc 死路径** — trigger 引用的 `02_design/teacher_requirements.md` 已不存在（ls 确认）。不影响另两个文件匹配，但死引用留着误导。修法: trigger 删 `|teacher_requirements`，SKILL.md Rule 7 同步改。2026-06-03 创建 / 最简单的一个。
- [ ] **D3 must 必查清单路径无锚定** — 各 must 规则第 3 参数里的 pattern 普遍没 `^...$`，`grep -qE` 理论上会误匹配含同名片段的别的路径。实际 pattern 都挺具体、概率低。修法: 逐条加锚定 + 回归测试（工作量稍大）。2026-06-03 创建 / 低优先。

### iOS 申请详情 2 个预先存在小隐患（2026-06-03 codex 审查发现）
> 6-03 演示数据 + 出寮届表单改动后派 codex GPT-5.5 xhigh 审查揪出，不是本次改出来的、属可选没修，记这等处理。

- [ ] **ApplyDetailView 未知 id fallback 到 `SEED.applications[0]`**（`ApplyStubs.swift:1995`）— 详情查找找不到 id 时退回第一条假数据，未知 / 旧 id 会被第一条掩盖（显示成别人的申请），且未来 SEED 为空会数组越界。修法: 改成 optional「找不到」分支显示空状态。演示阶段 SEED 有 3 条不崩、低优先。
- [ ] **StayDetailView 移动方式 label 总是「帰省方法」**（`StayListStubs.swift:980`）— 外泊 / 帰国时也显示「帰省方法」语义不准。修法: 按 kind 显示「帰省方法」/「出寮方法」。纯文案、可选。

### iCloud AC 素材分散在两个根目录（2026-05-30 加，等 itsuki 拍板）
> ⬆️ 2026-06-03 升级为高优先 — 已并入顶部「🎓 AC 升学素材整理 + 升学文件夹结构完善」段统一处理。本条保留详细背景。
- 现象: `02_学习与知识/升学/` 下有两个不同目录（inode 不同，**不是别名是两个真目录**）：`AC/` 和 `大学入試/`，下面各有一份 `筑波大学 AC入試 準備/`
- 分散情况: AC inbox（`06_radar_inbox/`）写在 `大学入試/` 下；jsonl 原文 + 会话总结（daily-archive 脚本写）写在 `AC/` 下
- 影响: ① AC 素材分两处，itsuki 后期整理要看两个地方 ② `session-wrap` SKILL.md §5.5.1.B 写 inbox 路径用 `大学入試/`，但 `daily-archive-cp.sh` 脚本用 `AC/` — 两套配置不一致，将来容易写串
- 选项: (a) 统一到 `AC/`（脚本在用的活跃根）改 session-wrap 路径 (b) 统一到 `大学入試/` 改脚本 (c) 确认其中一个是废弃残留直接删
- 决策: 2026-05-30 创建 / 待 itsuki 拍板
- 出处: `raw/2026-05-29_session-coord自动化.md` 收尾时发现

> 今晚装了 cc-comm-rules（CC 沟通规则 skill — 解决 itsuki 反复怒怼 CC 沟通失职）+ 3 个 hook + graphify 全套。下面是装完之后还没做的。

### A. 试用 cc-comm-rules + 收集反馈

- [ ] **试用 cc-comm-rules 1-2 周** — 看 4 个规则真用起来效果如何（详见 `~/.claude/skills/cc-comm-rules/SKILL.md`）
- [ ] **如果某条规则没解决问题** → 跟 itsuki 讨论调整（不要单方面改）
- [ ] **如果 hook 误报多** → 调整 `user-prompt-comm-priority.sh` 的怒怼词清单

### B. 同步环境清单 HTML

- [ ] **更新 `~/.claude/我的环境.html`** — 加 cc-comm-rules skill + 3 个新 hook
  - 加在 §4 全局 Skills 表（cc-comm-rules 那行）
  - 加在 §3 全局 Hooks 表（从 1 个 PostCompact 扩到 4 个 hook）
  - 验证方式：下次 CC 会话启动时 `session-start-env-diff.sh` hook 应该不再报 diff（因为 HTML 已同步）

### C. graphify 图谱清洗 — ❌ 已废（2026-05-14 中午拍板）

- [x] ~~**重跑 `/graphify --update`** 用 `.graphifyignore` 清掉 vendor 污染~~
  - **5-14 中午 graphify 实测复盘拍板「不卸不用 + 留作 AC 素材」** — CLAUDE.md / WIP / project-overview / file-linkage 4 个现有 skill 已精确解决 DMSD 真实问题（字段对齐 / 改 A 必改 B / 文件功能），graphify 反而冗余
  - 拍板"不用"了 → 不必清污染
  - 配置 / hook / 图谱目录 / 全局 CLI 全保留当 AC 素材
  - 详细 → `05_logs/raw/2026-05-14.md §I`

### D. push 累积 commits

- [ ] **11+ commits 未 push 到 GitHub** — 等 itsuki 拍板说"推一下"才推
  - 当前 commit 已含：今晚 cc-comm-rules + 3 hook + graphify 全套 + raw §D §E + WIP + TODO 改动
  - 按 itsuki 全局铁律：CC 不自动 push

### E. 沟通规则文件 v0.4.0 + v0.4.1 后续（2026-05-13 凌晨加） <!-- VERSION_OK -->

> 5-13 凌晨沟通规则文件迭代到 v0.4.1（根本方向调整 + DMSD 归类修正）。下面是升级后还没做的。详见 `05_logs/raw/2026-05-12_修补批量+comm规则加严.md §I`。 <!-- VERSION_OK -->

- [ ] **试用 v0.4.0 切分规则 1-2 周** — 看「概念强制中文 + 技术事实保留英文」真用起来效果如何 <!-- VERSION_OK -->
- [ ] **如果某类切分有边界争议** → 跟 itsuki 讨论 v0.4.2 调整（不单方面改） <!-- VERSION_OK -->
- [ ] **跨会话规则传播限制** — Claude Code 当前无技术机制让运行中的会话即时收到沟通规则文件升级
  - 现状：另一深度审查会话（5-13 同时跑）按旧规则给 itsuki 英语，已踩坑
  - 应对：要么关掉重开那个会话，要么 itsuki 手动贴 v0.4.1 切分给那个会话 <!-- VERSION_OK -->
  - 长期：等 Anthropic 官方加「skill 文件改动 → 运行中会话热加载」自动触发协议（目前没有，可能未来加）
- [ ] **LLM 自觉性失败工程教训写成 feedback memory**（要 itsuki 同意才写，按规则 5）
  - 路径：`~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/feedback_llm_self_discipline_unreliable.md`
  - 内容：v0.1-v0.3 同方向加严失败 3 次后才接受"改方向"的教训
  - 核心：LLM 自觉性 = 工程不可靠组件；同方向加严 N 次失败 → 应该改方向；机制层切分 > 靠 LLM 判断

### G. anti-ai-flavor + cc-comm-rules v0.6.0 后续（2026-05-14 晚加） <!-- VERSION_OK -->

> **2026-05-21 注（B-002 修）**：本段 §G（5-14 晚加） + 下方 §F（5-13 凌晨加）顺序倒置,但字母不重复;§H（5-14 晚段 Tango）紧接 §G 编号唯一。原 finding 建议「第二个 G→H」实际看文件已是 H,本次只确认编号唯一。<!-- VERSION_OK -->

> 5-14 晚段-2 会话新建 `anti-ai-flavor` 全局挂钩 + cc-comm-rules 撤回 v0.5.0 到 v0.6.0。下次会话继续优化（itsuki 原话「下次接着继续更新优化」）。<!-- VERSION_OK -->

- [ ] **anti-ai-flavor 8 个测试用例 subagent 对比未跑** — itsuki 选 C 跳过，下次会话真实使用中观察问题。位置：`~/.claude/skills/anti-ai-flavor/evals/evals.json`（8 用例 A-F 各 1 + 综合 1）。要不要跑 + 何时跑 itsuki 拍板
- [ ] **网络黑话黑名单持续补** — 现一级 7 词（刀 / 硬度 / 锁死 / 兜底 / 收窄 / 稳稳 / 说拧了）+ 二级扩展 5 类。下次见新黑话追加 `~/.claude/skills/anti-ai-flavor/references/jargon-blacklist.md` 末尾
- [x] ~~**术语表.html 现有 modified 状态决定**~~ ✅ **2026-05-22 标 ✅** — 5-14 已 commit 进 git（commit `8e35338` docs(wip+todo+raw+vocab): 5-14 晚段-2 anti-ai-flavor 立项 + 5-16 工程边角清理）。当前不是 modified。180+ 词条已上线作 AC 日语学习材料。<!-- VERSION_OK -->
- [ ] **`~/.claude/我的环境.html` 重新生成** — 清单美化派生版（5-11 晚生成）。现 md 加了 anti-ai-flavor + cc-comm-rules v0.6.0 标注，html 未同步。要不要重新生成 itsuki 决定 <!-- VERSION_OK -->
- [ ] **WIP 已 8 条超 "最多 5 条" 上限清理** — 下次清理 5-11 段 4 条老条目（详细历史在 commit log + raw）。或者 itsuki 拍板"放宽到 8 条"也行
- [ ] **CC 写 anti-ai-flavor 时自己也犯 F+A 类的元层教训写 feedback memory？** — 反讽性证据：写规则时自己也违反规则。是否值得写一条 `feedback_cc_skips_interview_step.md` 提醒"用 skill-creator / skill-with-process-steps 类挂钩时机械逐步走，不跳第一步"。itsuki 拍板

### I. session-wrap §7.5.7 TODO 双向刷新规则（2026-05-24 加）

> **背景**：5-22 修漏洞会话收尾时 CC 把「留 itsuki 拍板 5 大决策」只写收尾报告里没 Edit TODO 落地。itsuki 5-24 怒怼「他妈的这些你记录到 todo 里面了没 / 要我的收尾 skill 每次都能把剩下没做完的放到 todo 里面，然后把做完的从 todo 里面去掉。要能做到这样，帮我改好」→ 拍板细化 §7.5.1 项 7 = 强制规则。

- [x] ~~**改 session-wrap skill §7.5.1 项 7**~~ ✅ **2026-05-24 完成** — 项 7 改成「双向刷新强制规则」+ 加 §7.5.7 详细机械 5 步（A 列任务 / B grep TODO / C 标 ✅ / D 加新条目 / E 报告引用真实行号）
- [x] ~~**§7.5.7.4 出处段写本次怒怼背景**~~ ✅ **2026-05-24 完成** — 直接引 itsuki 原话作为 skill 历史证据
- [ ] **试用 §7.5.7 1-2 周** — 下次会话收尾跑 §7.5.1 项 7 时按机械 5 步走，看是否真不再「报告写了就算」/ 「漏洞条目都在 系统bug专栏」类回避
- [ ] **如果反模式仍出现** → 加 hook 强制兜底（PostToolUse 监测「收尾」关键词 + 报告里是否真有「TODO.md:行号」引用 → 没有就报警），不再靠 LLM 自觉
- [ ] **跨项目同步** — SC26 / Tango 收尾 skill 是否也加 §7.5.7（如果它们有 TODO 类文件）— itsuki 拍板

### F. 5-12 收尾残留待拍板（2026-05-13 凌晨加 — 2026-05-21 大整理 / B-003 修）

> 5-12 修补类批量会话末尾留下 7 件，5-21 audit 后归档大部分（已废 / 跟 §⏰ 重复 / 已 Bot 修）。

**真活（剩 1 条）**：
- [x] ~~**iOS 联动规则 1 + 2 严重漂移修复**~~ ✅ **2026-05-26 验证全对齐**。条目描述过时 — 5-08 后 backend 只有 2 commit 改 schemas/models (`3f65331` Fix-Bot 4 effective_* / `852563c` 999999 注册码后门)。5-21 Fix-Bot 1 已加 `path_hint` 字段。5-22 iOS 会话 `46f779c` backport 完成。5-24 FC-020 加 `bus_route_id` / FC-021 改 `room_no` max 8。5-26 全量比对 iOS NetworkModels / Endpoints vs backend schemas.py — 所有 学生 iOS 用到的 12 个 schema 字段全一致。

**已归档（B-003 修移到 §1061 同义 — 见各自处理点）**：
- [x] ~~**Cloud Design 40 额度 5-13 凌晨已过截止**~~ — 已在 §⏰ 段处理（B-001）
- [x] ~~**整理脚本 `/tmp/cleanup_2026-05-12.sh` 跑不跑**~~ — Mac 重启即丢,事实上已废
- [x] ~~**graphify 图谱 vendor 污染清**~~ — ❌ 已废（2026-05-14 中午拍板「不卸不用」，详见 §C）
- [x] ~~**MEMORY.md 主体刷新**~~ — 2026-05-21 Fix-Bot 3 已修（B-014/015/016/017）
- [x] ~~**`.claude/skills/file-linkage/SKILL.md` §1 标题「18 条」漂移**~~ — 已被 commit 859693e 修过

### H. 2026-05-14 晚段 Tango 立项 + 收尾残留（2026-05-14 晚段加）

<!-- 5-21 重命名：原 §G（第二个 G）→ §H — B-002 修复（编号唯一化） -->

- [ ] **DMSD 累积 commit 未 push** — 21 条 ahead origin/main（含本次 `97923a5` Tango 立项 raw + 早段 `16dd939` 沟通规则 v0.5.0 + 5-13 接力 + 5-12 修补批量 + 5-11 系列）— 等 itsuki 拍板 push 时机 <!-- VERSION_OK -->
- [ ] **`06_assets/术语表.html` modified 别会话残留** — 5-14 早段 session #4 CC 加的 7 个 CC 协作词（staging / silent-skip / silent-exit / exit-code / scope / regex / override）没 commit。v0.6.0 撤回 v0.5.0 后这些词的去留 itsuki 拍板：要么补 commit 进 5-14 早段，要么 discard <!-- VERSION_OK -->
- [ ] **ac-radar 中央 inbox 5-14 未写** — 本次 session-wrap 没并行加载 ac-radar skill。下次 itsuki 收尾时主动调 ac-radar flush 把 5-14 全量素材（早段沟通规则 + 晚段 Tango 立项 + 晚段-2 anti-ai-flavor）补到 iCloud `06_radar_inbox/ac_scratchpad_2026-05-14.md`
- [ ] **2 个 memory 候选评估** — (a) "vibe coding 不能按手工搓估时" → CC 估时方式根本错（可能 feedback memory）/ (b) "cc-project-template 治理框架首次实战" → 可能 project memory。按 memory-write skill SOP 走（查重 + frontmatter + MEMORY.md 索引）
- [ ] **Tango GitHub repo + push** — `gh repo create otogi2025/tango --public --source=. --push`（本地 `~/dev/tango/` 已 2 个 commit `addbfde` + `0467ed6` 等推送）
- [ ] **Tango 6 skill 共 197 处 DMSD 残留** — 9 条 G1-G9 治理 TODO 在 `~/dev/tango/00_admin/TODO.md` 里，边开发 Tango Phase 1 边清

---

### J. anti-ai-flavor HOW_TO_TALK + 跨项目 session-wrap 同步残留（2026-05-25 晚段加）

- [ ] **SC26 `session-wrap/SKILL.md` §7.5.5 line 720 旧漂移修** — 写"6 项核对表"实际 8 项（5-16 加 project-overview 项时漏改 / 5-25 又加项 8 没顺手修）
- [ ] **Tango `session-wrap/SKILL.md` 未来装 §7.5 强制清单段** — 5-14 立项漏装。当前项 8 嵌在 §5.5 里作为临时方案。装好后把项 1-8 迁移过去
- [ ] **CC 自治进化机制 propose** — itsuki 5-25 提「不同项目的 cc 可以自己进化自己的收尾 skill」 — 现在是人工跨项目同步（DMSD → SC26 → Tango），未来要每个项目 CC 自己根据项目特点判断该加什么项。要 propose 架构方案：可能用 skill 模板 + 跨项目 diff 机制
- [ ] **触发词「单词白名单」首次触发后建 `~/.claude/skills/anti-ai-flavor/whitelist.md`** — 5-25 拍板设计，文件未建（等 itsuki 第一次说「单词白名单」时 CC 建）
- [ ] **触发词「说人话」首次实战测试** — 5-25 拍板「说人话」=「重写上一条」，未真用过
- [ ] **触发词「翻车」首次实战测试**（**5-25 晚段第三轮升级新加**）— 5-25 拍板「翻车」单字触发 → CC 把上一条回复按 5 字段（原文 / 6 类归类 / 违反铁律 / 根因 / 修正版）写到 `~/.claude/skills/anti-ai-flavor/inbox.md` 末尾。等下次 CC 翻车 itsuki 喊一声看机制能不能跑通
- [ ] **inbox 累到 3-5 条后写「整理 inbox」SOP**（**5-25 晚段第三轮升级新加**）— 批量合并到 `references/翻车案例库.md` 的流程还没定。需要的字段：合并触发词 / 重新编号规则（案例库已有 #1-#20）/ 合并完移到「已整理归档」区不直接删 / 合并时 CC 是否要主动重写修正版
- [ ] **anti-ai-flavor 场景模板 5-8 补齐** — `HOW_TO_TALK.md` 现在只定了场景 1-4（做完事 / 卡住 / 简单 yes-no / 复杂解释），场景 5（发现新东西要解释）/ 6（2-3 种做法让拍板）/ 7（主动提醒踩坑）/ 8（反驳 itsuki）还是占位 — 下次会话继续走

### K. 启动 SOP 集中化 + CLAUDE.md 重写残留（2026-05-26 晚段-2 加）

- [ ] **全局环境清单 `~/.claude/我的环境.md` + `.html` 同步本会话新建 / 改动** — 本会话新建 `~/dev/DMSD/.claude/skills/dmsd-startup/SKILL.md`（DMSD 项目专属 skill）+ 改 `~/.claude/hooks/session-start-coord-check.sh`（DMSD 项目下静默退出）+ 改 `~/.claude/CLAUDE.md`（加沟通铁律段 + destructive-bash 行为约定段）— 收尾 §7.5 项 11 触发但本会话没补做（等下次会话 / 或本次最后补）
- [ ] **~/.claude/ 做成 git 仓库 propose**（**5-14 立的 / 5-26 再次强化**）— 本会话改了 `~/.claude/CLAUDE.md` + `~/.claude/hooks/session-start-coord-check.sh` 都没法 git 备份。永久解决全局配置无历史问题。需要 itsuki 拍板初始化策略（git init / .gitignore 哪些 / hook 自动 commit 还是手动）
- [ ] **其他 5 项目（QTS / tango / SC26 / practice / cc-project-template）独立启动 skill 都没做** — itsuki 5-26 拍板「先只做 DMSD 完整版」，其他项目按需后续做。开新项目工作时 propose 加项目级启动 skill
- [ ] **sync-check 警告 `bin/check_overview_drift.sh` 联动文件未改** — 别会话改了脚本本体但 CLAUDE.md / 文档同步点清单 / hooks README 没提到。本会话不动（不是本会话改的）。要拍板：(a) 别会话补 (b) CC 下次会话主动补 (c) 改 sync-rules.sh 让 bin/check_overview_drift.sh 自动豁免
- [x] ~~**WIP.md「最近会话」段加本会话条目** — 本次会话主题（启动 SOP 集中化 + CLAUDE.md 大改）跟晚段「iOS Bot 1 复查 + 全项目中枢注册」是 5-26 不同会话不同主题，应该单独加一条到「最近会话」段（最多 5 条上限）~~ ✅ 2026-05-26 晚段-2 收尾完成（commit `771ef59`）

### L. teacher_web Vite 废弃 + Ryō polish 回滚残留（2026-05-26 晚段-4 加）

- [ ] **写 `v1/demo_server.py`** — 恢复 NFC iPhone 快捷指令实时点呼 demo 功能。提供 3 个端点：GET `/api/server-info`（返回 LAN IP + port，给浏览器 auto-detect）/ POST `/checkin?no=XX`（接 iPhone 快捷指令，存 event with seq）/ GET `/events/latest`（浏览器 1 秒 poll，返回最新 event）。当前 `./tomoshibi start` 跑的是 `python3 -m http.server` 只做静态，NFC 实时点呼断了。预估工作量 50 行 Python（aiohttp 或 stdlib http.server 都行）
- [x] ~~**系统bug专栏 FC-025/26/27/28 标 N/A** — `00_admin/系统bug专栏.md` 里 4 条 Codex 第二轮 audit 发现的字段对齐 / 权限 / package 问题，全部是针对 Vite + TS 实装版的。Vite 整体废了 → 这 4 条 N/A 不再有效~~ ✅ **2026-05-27 闭合** — 专栏 line 940/947/954/961 4 条 FC-025/26/27/28 全部已标「✅ N/A」（注「`client.ts` 没归档，Task #6 真接口对接时本条要重开」）
- [ ] **未来设计层 polish 候选方向**（如果再起意优化 Ryō）— 4 个候选：
  - (a) 单页大改造（B 改成具体一页换风格，不动整体）
  - (b) 字体单独换不动颜色（risk 最低）
  - (c) 找 itsuki 喜欢的具体参照系 web（让他先指）
  - (d) 跟 itsuki 一起看几个真实日本教育系统 UI（不同风格）后再选方向
- [x] ~~**WEB_DESIGN_LOG §7 参考资料索引 / §10 下次会话 quick-start 复核**~~ ✅ **2026-05-27 闭合** — §7 改成指向 `v1/src/_legacy/` + `v1/src/api/client.ts` + 历史归档目录 / §10 重写 quick-start 反映 Vite 废弃 + standalone 主线 + 加 `v1/开发模式跑.command` + `./tomoshibi start` + rebuild.command 当前路径
- [x] ~~**DESIGN_BRIEF.md §3-§8 复核**~~ ✅ **2026-05-27 闭合** — DESIGN_BRIEF 文件顶部时间戳「2026-05-26 大调整」+ §3 实装范围 / §4 未实装 / §5 关卡清单 / §6 真接口对接路线 D0-D6 全部已反映 5-26 后事实（5-26 当天写）

### M. AC 学习内容清单扩充 4 章实装残留（2026-05-27 收尾加）

> **背景**：5-25 晚 itsuki 让 CC 起草 `06_assets/学习内容清单.html` v0.1.0 9 章后看完不满足深度 + 主动要求扩充「专业类知识 + 项目底层运转逻辑」。<!-- VERSION_OK --> CC 在回复里列了 4 章新增大纲（第 9-12 章）等 itsuki 拍板，但 itsuki 直接说「收尾」没继续讨论 → 4 章扩充未实装到 HTML，变悬挂任务。深度 AC 素材见 `05_logs/raw/2026-05-25_AC学习清单起草.md`。

- [ ] **实装第 9 章 — 项目底层运转逻辑** — 5 节（操作系统基础 / 网络底层 TCP-IP DNS TLS / 编译解释字节码 / 数据库底层 B 树事务并发 / 异步深度）/ 约 15+ 条目 / 每条 item-card 格式带「是什么 + DMSD 关联 + AC 故事价值」3 角度
- [ ] **实装第 10 章 — 计算机科学基础（情報科学類 1-2 年级共通课预习）** — 8 节（离散数学 / 线性代数 / 微积分 / 概率统计 / 算法数据结构 / 计算机体系结构 / 形式语言自动机 / 面向对象理论）/ 约 25+ 条目 / **AC 最强用途** = 评委问「入学后想学什么」能答到具体科目级别
- [ ] **实装第 11 章 — 信息安全深度（CTF / SecHack365 方向预习）** — 4 节（密码学基础 / 椭圆曲线 ECDSA / 网络安全攻防 SQL 注入 XSS CSRF 中间人 / CTF 5 大类）/ 约 18+ 条目 / 跟 DMSD NFC 防作弊 3 层直接对接
- [ ] **实装第 12 章 — 软件工程** — 7 节（版本控制理论 / 测试 TDD / 设计模式 / 重构 / CI-CD / 可观测性 / 文档驱动开发）/ 约 15+ 条目
- [ ] **HTML 整体调整** — 9 章 → 13 章，原第 9 章「推荐学习顺序」往后挪到第 13 章 + 阶段 A/B/C 加入新 4 章的优先级 + 排序
- [ ] **等 itsuki 拍板** — 上面 4 章是否全要 / 哪几节砍 / 顺序调整（信息安全章是否前置到第 9 章因为跟 DMSD 防作弊直接相关）/ 还要加什么新方向（AI / ML / IoT 等 itsuki 可能想要）

### N. 全项目审查残留（2026-05-27 早段加 — itsuki「全项目审查 + 不要偷懒」会话产出）

> **背景**：5-27 早段 itsuki 启动「全项目审查 — 每个文件 / 文件关联 / 关联 skill / 内容审查 / project-overview 检查全跑一遍 + 主目录无编号文件分析 + 各文件夹莫名其妙的文件 + 不要偷懒 + 扫整个项目所有文件 + 不要给我留问题 / 所有问题加 TODO」。CC 一次过扫 1189 文件 + grep 决策关键词 + 比对 SKILL.md §0.1 + 读关键文件 → 直接修 6 处 Vite 决策漂移 + 物理清 7 个 .DS_Store + git mv `student_ios/_archived_DESIGN_BRIEF_Round1_context.md` → 99_archive。详细审查报告 `05_logs/raw/2026-05-27_全项目审查.md`。本段记 CC 修不了的 8 条 backlog。

- [ ] **99_archive/ 顶层 21 个散件归档**（命名 + 子目录结构 itsuki 拍板）— 14 个 `ファイル - 2026-02-17T00:18:58 (1-13).510Z`（Google Drive 早期残件）+ 5 个 .pages 历史原稿（`需要学习的内容_原始.pages` / `learning_process_原始.pages` / `progress_log_原始.pages` / `progress_log_备份版.pages` / `2026-03-08_Folder_Structure_Overview.pages`）+ `2026-04-12_executable_dev_checklist_v0.1.md` 早期 checklist → 建议塞进 `99_archive/2026-02-17_早期文件残件/` 子目录（命名 / 是否分两个子目录 itsuki 决定）
- [ ] **01_specs/ 4 个 .pages 历史归档**（CC 读不了，要 itsuki Mac 上 Pages.app 操作）— `API_Contract_v0.1.pages` / `IA_UI_v0.1.pages` / `Overview_of_Features_v0.1.pages` / `RollCall_Spec_v0.1.pages` / `rollcall/DMSDv0.1验收脚本.pages`（共 5 个，都已被 .md 取代）→ 建议归档到 `99_archive/2026-02-12_v0.1_spec_pages原稿/`
- [ ] **`00_admin/2026-04-19_项目审查_backlog.md` 物理归档**（已大量 close，project-overview SKILL.md §1.2 已标 📦 但物理位置还在 00_admin/）→ git mv 到 `99_archive/2026-04-19_项目审查_backlog/`
- [ ] **跑 `graphify update .` 刷知识图谱**（5-26 vite 废弃 + 物理删 node_modules 81MB 后没刷 → `graphify-out/GRAPH_REPORT.md` Community Hubs 段 vendor React/Babel runtime 重复出现 36 次，因为索引基于 5-26 之前快照）
- [ ] **`backend/demo/` 目录处置**（5-21 后 backend demo 阶段结束，是否归档 / 删 / 留 — itsuki 拍板）
- [ ] **`progress_overview.md` 4-17 后大改**（章节级里程碑刷新到 5-27 当下 — 阶段 3-7 状态 / v0.4-v0.8 + 5-27 凌晨 + 早段累积推进 / 加 v0.8 之后 28+ commit 累积表）— 列入文档欠债 WIP 当前焦点 #3
- [ ] **v0.8 之后累积 28+ commit 未 bump，5-27 干完是否 bump v0.9**（走 version-bump skill 决策树 — CC 有否决权但 itsuki 启动「迭代 / bump / 发版本 / 打 tag」才进入流程）
- [ ] **加「决策状态扫描 hook」长期 propose**（识别「Vite + TS」/「Phase 1 / Phase 2」/「demo 阶段」等敏感关键词，跟 decision_log 实际状态对比 — 防本次发现的「Vite 5-26 已废，但 4 处当前状态描述没刷」类漂移再发生）
- [ ] **WIP「最近会话」砍老条目维持 5 条上限**（本次审查发现实际有 14 条会话条目 — 别会话累积加新条目时没砍最老 / itsuki 决定砍 line 244+ 9 条还是保留全历史）

### O. 中枢档案污染修 + 双写铁律 + hook 残留（2026-05-27 早段-3 加）

> **背景**：5-27 早段-3 itsuki 发现别会话写中枢 `项目档案/DMSD.md` 末尾「更新日志」混入 AC 模式分析（「模式 5 顶级 / AC 价值 ⭐⭐⭐⭐⭐」）→ CC 排查 3 档案污染（DMSD.md / Tango.md / QTS.md）+ 1 个漏写（5-27 三段会话 AC 素材没进 06_radar_inbox）+ 立 3 层防御（中枢 CLAUDE.md 铁律 / session-wrap SKILL.md §5.5.1.A 去向表 + 强制双写 / 全局 PostToolUse hook 扫 AC 关键词）。详细见 WIP 早段-3 段。

- [ ] **anti-ai-flavor inbox 累计 5 条 — 到 itsuki 之前定的「3-5 条后写整理 inbox SOP」阈值**（已经命中阈值上限 — 下次会话或 itsuki 主动喊「整理 inbox」时合并 #001-#005 到 `~/.claude/skills/anti-ai-flavor/references/翻车案例库.md`，写「整理 SOP」流程文档）
- [ ] **中枢档案铁律落地 — 各项目 CLAUDE.md 加指针让各项目 CC 知道这条规则**（Tango / QTS / 大学入試父项目 CLAUDE.md 三个项目 CC 启动时还不知道有这条铁律 → 加一段「中枢档案铁律 — 参考 全项目中枢/CLAUDE.md §中枢档案铁律」指针。DMSD CLAUDE.md 已在 §「全项目中枢联动」段引用 — 验证是否要补具体铁律内容还是只给指针）
- [ ] **全局 `~/.claude/` 不在 git → settings.json + hook 新建无历史记录** — 5-14 + 5-26 已立 propose「~/.claude/ 做成 git 仓库」，本次会话新建 1 hook + 改 settings.json 又一次案例 → 等 itsuki 拍板
- [ ] **hook 长期 false positive 监控** — `post-edit-zhongshu-ac-pollution-check.sh` 关键词清单 `模式 [0-9]+ 顶级|AC 价值[^点]|⭐⭐⭐|关联度评估` 可能误伤元描述（本次会话已遇 1 次 — QTS.md 写「关联度评估全砍」被 hook 命中误判，已改措辞规避）→ 累 3-5 次 false positive 后看是否要扩展白名单 / 路径排除
- [ ] **WIP「最近会话」9 条超 5 条上限**（本会话加早段-3 → 9 条；§N 第 9 条已立 backlog 砍 5-25 晚段-2 / 5-25 晚段 / 5-26 / 5-26 晚段-2 / 5-26 晚段-3 中老的 4 条；本会话 CC 没擅自砍 — itsuki 决定砍哪 4 条）

### P. anti-ai-flavor 双层防御立项残留（2026-05-27 晚段加）

> **背景**：5-27 晚段 itsuki 启动 iOS 推进 → CC 报告状态翻车 3 处（`deadline` / `clarify` / `diff` 英语裸露 + 病句 + 编造数据）→ itsuki 怒怼追问根因「为什么 CC 总是会自己莫名其妙用英语」→ CC 摊牌 3 层根因 + Claude Code hook 体系无 PostResponse 类硬约束 → itsuki **主动提**「立 hook 强制扫 + 白名单」方向（独立提出 detective control 思路）→ CC 给 A/B/C 三方案 → itsuki 拍板 A+B → 工程实装 3 新文件 + 2 改文件（53 词白名单 + Stop hook 事后扫 + UserPromptSubmit 白名单注入）。详见 raw `2026-05-27_anti-ai-flavor双层防御立项.md`。

- [ ] **iOS app 推进延后** — 本会话原主题被沟通基础设施修复完全占用，iOS 一行没碰。下次会话或现在切回 iOS（可选方向：TODO §D 2 处工程债务 catch 降级 / 老师公告 iOS 端实装 / 学生注册码 iOS 端实装）
- [ ] **环境清单 `.md` vs `.html` 漂移** — `~/.claude/我的环境.md` 2026-05-27 08:22 之后没动，`.html` 19:50 + 本会话晚段都改了。两者 sync 一道（itsuki 决定要不要现在做还是下次）
- [ ] **Stop hook 首次实战观察** — 本会话收尾结束后 Stop hook 首次跑，观察：① 误报多不多（`anti-ai-flavor-precheck.sh` 这种 hook 文件名是不是该加白名单第 6 类）② inbox 自动追加格式是否清晰 ③ 跑超时（10s timeout）会不会成问题
- [ ] **翻车案例库 v1.1 状态核对** — inbox.md 注释说「#001-#007 整体合并到 references/翻车案例库.md #21-#27」，但本会话 CC 没读案例库本身核对。下次会话核对案例库 v1.1 是否真有 #21-#27 + 跟 inbox 5 字段对得上
- [ ] **anti-ai-flavor 5 铁律没升 8 类** — anti-ai-flavor hook 自检 6 类→8 类升级了，但 5 铁律（起因 / 改哪+这是啥 / 改的内容 / 每对象 / 下一步）描述没动。是不是该加 6+7 铁律对应 G+H 自指失败 + 编造数据？等下次会话或 itsuki 拍板

### Q. 整理 inbox 第一次实战 + 6 类升 8 类残留（2026-05-27 晚段-2 加）

> **背景**：5-27 晚段-2 itsuki「启动」后 4 件小事自决 → CC 翻车 5 词全裸（`untracked` / `working tree` / `commit` / `repo` / `propose`）→ inbox #006 → itsuki「整理 inbox」第一次实战触发 → 合并 inbox #001-#007 到 `~/.claude/skills/anti-ai-flavor/references/翻车案例库.md` v1.1 #21-#27 + 加根本问题 5「自指失败」+ 类 J/K + 触发词 2→4 → itsuki「升级」→ 6 类升 8 类全链路 7 文件联动改 → drift 修第二轮（H 类铁律当场实战验证）→ 1194 ✅。详见 raw `2026-05-27_整理inbox+8类升级.md`（commit `6fa42ad` 已入库）。

- [ ] **daily-archive 跟 ac-radar 目录树不统一** — daily-archive 脚本 cp 路径写 `升学/AC/筑波大学.../03_素材_候选/`，ac-radar 写的 inbox 在 `升学/大学入試/筑波大学.../06_radar_inbox/`。同项目两套目录树会不会未来 itsuki 整理素材时找不到？等下次拍板要不要统一
- [ ] **anti-ai-flavor inbox.md 「已整理归档」7 条物理保留** — 5-27 整理时 7 条用 HTML 注释包住放在「已收集案例」段下面（按案例库「不直接删万一合并出错可恢复」铁律）。下次整理时按案例库 §九「整理 inbox」SOP 把它们再往下挪到「已整理归档」段下面 + 附新整理日期注释（机制可行性等下次整理验证）
- [ ] **G+H 新模式 memory 同步** — 本会话 anti-ai-flavor 主体加了 G「自指失败」+ H「编造数据」两个新类，但 memory `feedback_anti_ai_flavor_翻车案例.md` 索引段还没更新指向案例库 v1.1。下次会话或 memory-write skill 触发时同步
- [ ] **`~/.claude/` 全局目录不在 git 跟踪** — 本会话改了 5 处 `~/.claude/` 文件（SKILL.md / hook / CLAUDE.md / HOW_TO_TALK.md / 案例库 / inbox / 我的环境.html）全没 git 历史。5-14 / 5-26 / 5-27 已立 propose「把 `~/.claude/` 做成 git 仓库」三次未拍板，等 itsuki 决定
- [ ] **WIP「最近会话」累积 9 条远超 5 上限** — 本会话加完 9 条，§P 段说「9 条已超」上次没砍。等 itsuki 拍板砍哪 4 条（候选：5-26 / 5-26 晚段-2 / 5-26 晚段-3 / 5-27 早段-3 中老的几条）

### R. 点呼机构造 + 工作原理学习（2026-05-27 硬件采购会话加）

> **背景**：5-27 itsuki 推进点呼机配件采购时，Codex「ST25DV 116 天磨穿」警告 → itsuki 重算发现 Codex 假设「7×24 每 10 秒刷」不符合真实点呼时间窗 → 抓出设计文档 §2.3 漏写时间窗限定。itsuki 意识到自己对点呼机各部件怎么协作、ST25DV 怎么工作还没吃透 → 立学习任务。

- [~] **系统学一遍点呼机构造 + 工作原理** — 🔄 **2026-06-02 跟 Gemini 系统学过一轮，大头吃透**（6 部件 / 路径 A+B 数据流 / SPI+I²C 区别 / Mailbox 机制 / 信号冲突物理隔离 / thin client 边缘-中心分工，详 raw `2026-06-02`）。③ ST25DV 原理因架构反转更新为「手机写 Mailbox、树莓派 I²C 读」，旧 nonce 刷新作废。剩**实操层**（开机初始化 ST25DV / 真接线 / 写 Python）等硬件到货再学。① 6 部件（Pi 主板 / PN532 读卡器 / ST25DV 贴纸 / LED / 风扇 / USB 喇叭）② 路径 A（NFC 卡）+ B（手机碰）数据流 ④ thin client 点呼机/后端分工。材料：`hardware_design.md` + `ROLLCALL_DEVICE_DESIGN_LOG.md` + `flow_design.md`。AC 价值：硬件理解是面试可挂的工程深度
- [x] ~~**`hardware_design.md` §2.3 回填 nonce 刷新时间窗限定**~~ ❌ **2026-06-02 作废** — 架构反转后点呼机不再每 10 秒刷 nonce（手机改「写」方），「116 天磨穿」前提整个消失，本任务无意义。详 decision_log 2026-06-02 条
- [ ] **NTAG424 DNA 正式部署替代 NTAG215** — 路径 A 学生卡演示用 NTAG215（UID 可克隆），正式部署 4 台时换 NTAG424 DNA（AES-128 + SUN 防克隆）。新增预算约 2-4 万日元（100+ 张 × 200-400 日元）。等部署阶段做

#### 🔄 架构反转后续（2026-06-02 itsuki 拍板 ST25DV 手机「读」→「写」）

> **背景**：itsuki 找 Gemini 学点呼机原理时发现旧方案矛盾 → 拍板架构反转（手机写 ST25DV、树莓派被动收）。`hardware_design.md §2.3` + decision_log 已改。反转后防代刷其实**简化**（CC 初判「断链」被 itsuki 当场纠正 — 手机不联网，详 raw §9）+ 连带文件待简化 + 后端选址，列待办：

- [ ] **防代刷随架构反转简化（非阻塞 — CC 初判「断链阻塞」被 itsuki 当场纠正，详 raw §9）** — 手机不联网、只点呼机连后端 → 旧 nonce+URL（防手机远程 POST 代签）在新架构多余、可砍。代刷只剩「到现场」一条路 → 靠「播报 + 老师看脸」（4-12 既定）+ v2.0 人脸。真正要做：① **点呼机↔后端 HTTPS + 设备密钥认证**（本来就要做，防重放属这层、点呼机参与）② 可选：手机写的数据带签名防造假学号（优先级低，到场被看脸防，v1.1 议）。后端 A-010 的 nonce+ECDSA 范围据此重评（大概率大幅简化）
- [ ] **连带 4 文件同步**（等防代刷新方案定后改）— `flow_design.md`（签到时序图 + 防御数学全是旧方案）/ `NFC防代刷_后端立项施工计划.md`（整个后端 nonce+ECDSA 计划按旧架构）/ `system_features.md`（nonce rate limit）/ `ROLLCALL_DEVICE_DESIGN_LOG.md`（§范围写「动态贴纸 nonce 写入」）
- [ ] **🟠 后端服务器三选一（要跟老师讨论）** — 宿舍现有一台摄像头专用服务器、无点呼系统专用服务器。三选一：A 自己动手组一台 / B 租 VPS（云服务器）/ C 跟摄像头系统共用一台。决定后端部署位置（影响点呼机↔后端走外网几十 ms 还是局域网几 ms → 影响延迟账本）
- [ ] **人脸识别正式归 v2.0** — 24H 实时 1:1 人脸比对（防借手机代刷）。需服务器算力（最好显卡）+ 隐私处理 + 光照调优，独立大工程。v1.0 先把 NFC 双路径做扎实，不拖累上线

#### 🔍 2026-06-03 Codex 跨 AI 审查补充的技术风险（itsuki 主动调 Codex 5.5 xhigh 审点呼机对话挖出）

> **背景**：itsuki 把点呼机 Gemini 对话完整上下文交给 Codex（gpt-5.5，最高思考档 xhigh）独立审，挖我们漏的技术风险。Codex 不知道项目已有 ECDSA + nonce 设计，却独立推出同方案 → 反向验证该设计必要。CC 已逐条核实成立、非错前提。下面每条标注跟现有条目的关系，避免重复理解。

- [ ] **⚠️ 重估优先级：手机发射明文 student_id 会被复制 / 重放** — Codex 指出手机若只把明文学号写进 ST25DV，逆向 app / 抓包 / 借号即可代签。现有条目（457）把「手机写的数据带签名」列为「② 可选 / 优先级低 / v1.1 议」，Codex 认为应是核心必做（点呼机出一次性随机数 nonce → 手机用设备绑定密钥签名 → 写回，否则旧数据可重放）。**待 itsuki 重估**：v1.0 必做还是 v1.1。跟 A-010 / 457 的范围重评合并考虑
- [ ] **手机离线 → 凭证吊销难题** — 手机不联网就无法实时确认账号是否被封禁 / 设备换绑 / 令牌（token）吊销。需短期凭证 + 过期时间 + 同步策略（毕业生 / 被锁学生的手机离线时还能不能签到）。现有条目未覆盖
- [ ] **学生卡 UID 可能被克隆** — 若只读 NFC 卡 UID（卡的唯一编号）当身份，低成本卡的 UID 不是强认证、可克隆。要确认学校卡类型；面试可能被问「为什么 UID 不当密码用」。现有条目未覆盖
- [ ] **ST25DV Mailbox 高并发竞争** — 单缓冲（Mailbox 是 ST25DV 里那 256 字节的临时收件区）在卡点连刷下可能：后写覆盖前写 / 半包读取 / GPO 中断丢失 / 树莓派清空时手机还在写。需加序号 + 校验码（CRC）+ busy 检查 + 确认重试（ACK）+ 实测。比现有 rollcall-05 的幂等键并发更底层（在硬件层）
- [ ] **双入口业务层幂等去重** — PN532（卡）和 ST25DV（手机）双路径 + 网络超时重试 → 同一学生可能重复提交。后端要用 `session_id + student_id` 幂等去重。部分覆盖现有 rollcall-05，但要补「双入口同时提交」这种情况
- [ ] **延迟要看 p95 / p99 不能只看平均** — 80 人卡点真正的拥堵来自偶发 2 秒的尾部延迟（p95/p99 = 第 95/99 百分位延迟，即最慢那 5% / 1% 的体验），不是平均值。上线前实测做延迟分布图，不只单次秒表。现有条目未覆盖
- [ ] **NTP 不可用 + 无 RTC 的时间风险** — 树莓派没有电池实时时钟（RTC），断电重启时间会错乱；NTP（网络对时）被墙 / 断网 / 被伪造都影响迟到判定。校时发生「时间跳变」会让签到时间倒退或前进。方案：用单调时钟记事件先后顺序 + 最近一次可信校时换算成真实时间 + pending 标记 + 人工复核。现有条目未覆盖（itsuki 主文件已记 NTP 学到，但没记 NTP 失效的风险）
- [ ] **离线降级要防作弊** — 服务器断了还允许本地暂存签到，攻击者可故意断网制造「宽松模式」。离线记录标 pending + 签名会话令牌 + 不可篡改日志 + 恢复后复核。现有条目未覆盖
- [ ] **老师网页「开始点呼」是高权限动作** — 要防跨站请求伪造（CSRF，骗已登录老师的浏览器替攻击者发请求）+ 账号盗用 + 重放「开始」命令 + 学生伪造 WebSocket 指令。点呼机↔服务器要设备身份认证（部分覆盖 459，补 CSRF / 重放面）
- [ ] **点呼机物理安全** — 机器放在学生能碰到的地方，SD 卡 / 配置 / API 令牌 / 音频缓存 / USB 口 / 网线都可能被物理攻击。需外壳防拆 + 最小权限令牌 + 日志审计。现有条目未覆盖
- [ ] **本地播报会泄露信息（枚举攻击）** — 攻击者乱发学号、听机器念不念名字，就能枚举出有效学生；红绿灯 / 语音也暴露迟到缺席状态。失败反馈要泛化 + 加速率限制。现有条目未覆盖

#### 📋 2026-06-03 第二次 Codex 审补充（审「5 文档修改一致性」，区别于上面审 Gemini 对话那次）

> CC 改完 5 文档（手机读→写架构反转追平）后派 codex 5.5 xhigh 复审文档一致性。**已做**：flow_design / ROLLCALL_DEVICE_DESIGN_LOG / 项目心智模型 / hardware_design / BACKEND §9.1 五文档架构反转追平 + A 组 9 处文档矛盾修复（6-03）。下面是 codex 挖出、需后续做的：

- [ ] **后端 `rollcall_events` 加 `swipe_time` 字段** — 现在是 `checked_in_at = now()`（后端收到时刻），但新架构判迟到要用点呼机打的接触时刻 → schema 缺字段，判定链断。后端实装时加
- [ ] **幂等重设计避坑** — codex 建议 `(session_id, student_id)` 唯一防重复，但 `rollcall_events` 是只追加表、老师改判要写第二条 `teacher_override` → 简单唯一约束会挡掉改判记录。要按「同一次签到 / 同一来源」去重，不是「一个学生一条」。跟上面 470 那条合并设计
- [ ] **iOS/Android 写 ST25DV Mailbox 真机 spike（试做验证）** — 要 ISO15693 自定义命令（`RF_PUT_MSG` / Fast Transfer Mode 快速传输模式），不是普通 NDEF 写。两平台真机验证通过再冻结协议（跟 itsuki「写码前找懂 iOS NFC 的人确认」是同一件事）
- [ ] **采集线程 GPO 别被 PN532 阻塞挤掉** — 单线程里先 `pn532.read_card(0.5s)` 再查 GPO，PN532 堵着时可能漏 ST25DV 中断 → 用独立 GPIO 回调 + 线程安全队列。跟上面 469 那条合并
- [ ] **下游残留文件（458 之外补全清单）** — 仍有旧「读 URL / nonce」描述：`system_features.md §7.4.2` / `RollCall_Spec.md §5.1.2` / `ENUM_REGISTRY.md`（`iphone_tag`/`hybrid` 语义）/ `DEVICE_REGISTRY.md §3.2` / `API_CONVENTIONS.md §4 §10`（`server_now` 基准）/ 点呼机 `README.md` + `src/main.py`

#### 🔥 下单前必确认（2026-05-28 采购会话 — 优先级高，下单前逐条核对）

> **背景**：5-28 itsuki「今晚把点呼机硬件全买好」→ CC 用 WebFetch 把 itsuki 发的采购链接逐个抓取确认 → 揪出链接和需求对不上的几处。清单做成 `03_dev/rollcall_device/点呼机采购清单.html`（浏览器可视化 + 可点链接 + 折叠截图）。以下是下单前必须 itsuki 拍板/改的：

- [ ] **🔴 风扇换 5V** — itsuki 发的风扇链接 Amazon `B0DYV31FJZ` 抓出来是「JYUDAUFU 30×10mm **DC 12V** 4 个装」。Pi 3A+ 只有 5V，12V 风扇转不动。别买这个，重找 5V 30mm 风扇
- [ ] **🟠 喇叭二选一** — 截图是 HONKYOB ¥1,980，但链接 `B0G64JFMNR` 抓出来是 Apqfw HM5002 另一款。两个都是 USB 小喇叭功能差不多，确认买哪个，别两个都下
- [ ] **蓝色 LED 补链接** — itsuki 发的秋月 8 个链接里漏了蓝色 LED（截图有），补 `g101321`（¥180 / 10 个入）
- [ ] **杜邦线去重** — 买了两种母对母：`g103475`（15cm 10 本）+ `g115868`（20cm 40P 连排），功能重叠留一种够（都便宜，都留也行）
- [ ] **PN532 链接核对** — `B0C7Q1PX3R`（应是 PN532 读卡器 ¥1,190）WebFetch 抓取时服务器一直报 500 错误，没确认成，下单前 itsuki 点进去自己核对是不是 PN532
- [ ] **ST25DV 数量 4 还是 5** — 截图选了 4，hardware_design.md §4.6 定的是 5（4 部署 + 1 备用）。库存仅剩 8，今晚下单
- [ ] **Mac 有没有 SD 卡槽** — 没有就要补一个 microSD 读卡器，否则系统写不进卡、Pi 开不了机
- [ ] **下单后改文档** — 方案从「Qwiic 免焊」改成「焊 2.54mm 排针」，要把 `02_design/hardware_design.md`（删 ¥3,090 Qwiic 套件 + 补 ¥749 排针套装）和 `03_dev/rollcall_device/点呼机接线说明.md` §3（Qwiic→焊排针）同步改掉

### S. IOS_DESIGN_LOG §11 技术实装层日语中文化（2026-05-28 加）

> **背景**：5-28 itsuki 让 CC 把 `IOS_DESIGN_LOG.md` 里的日语改中文（中文铁律：内部文档 100% 中文 / 界面字符串保留日语）。CC 已改完 §1 时间线 + §3 注册全段 + §5 个人主页（设计说明性质，已中文化）；§4 / §3.14 等章节日语几乎全是界面文案按原则保留。§11 技术实装层约 180 行日语（混 Swift 代码注释 + 后端 API 名 + 技术术语笔记），itsuki 拍板先 commit 已改的、§11 单独加 TODO。

- [ ] **`IOS_DESIGN_LOG.md` §11 技术实装层日语 → 中文** — 涉及 §11.1 P0 范围表 / §11.2 技术栈表 / §11.4 全局约束（通知 / オフライン / セキュリティ / アクセシビリティ 等子标题 + 内容）/ §11.5 状态管理代码块注释 / §11.6 功能别 API 映射表 / §11.7 共通组件 / §11.8 测试配信 / §11.9 待决清单。原则：纯说明叙述 + Swift 代码注释改中文，界面错误文案（「アカウントが無効です」等学生真看到的）保留日语。约 180 行，判断细碎，留整块时间做

### T. 宿舍申請实物表 v1.0 实装（2026-05-28 加 — itsuki 提供「届け類.pdf」9 种实物表）

> **背景**：itsuki 5-28 提供宿舍真实纸质申请表「届け類.pdf」(朝日塾中等教育学校 寮)9 种扫描件。CC + codex 双读核对一致, 6 个待拍板点 itsuki 全拍板, 已落 `02_design/system_features.md` §7.2(出寮届補完)/ §7.3.5(学習在线申请)/ §7.21(4 种全新申請)/ §8(数据模型)。itsuki 拍板「都进 v1.0」。iOS 侧映射已写 `IOS_DESIGN_LOG.md` §14。以下是 5 端实装 backlog。

**后端 backend** — ✅ **2026-05-28 全部完成**（commit `c6ccee0`，codex gpt-5.5 xhigh 实装 + CC 审查：70 测试通过 + 干净空库迁移全链路验证）：
- [x] ~~`applications` 表加 6 字段：contact_phone / companion / dest_cities / receipt_submitted / is_long_vacation / meal_note（§8.2 補完）~~ ✅
- [x] ~~`approver_role` + `teachers.role` ENUM 加「校長」（帰国届最终许可、§7.2.2；itsuki 5-28 拍板 A「实物有校长就要校长」）~~ ✅
- [x] ~~帰国届 chain：担任 → 国際交流部長 → 寮務課長 → 寮務部長 → 管理係 → **校長**（様式3-1）~~ ✅ `approval_chain.py`
- [x] ~~帰省 chain 4 人不分日本人 / 留学生 + 外泊日本人 4 人含寮務部長（修旧 3 人）~~ ✅
- [x] ~~新表 `study_online_requests`（在线学习申请、类型 A、§8.3）~~ ✅
- [x] ~~新表 §8.7 4 张：dorm_event_proposals / dorm_schedule_changes / fridge_purchase_requests / item_possession_requests~~ ✅
- [x] ~~Alembic 迁移 `d2e3f4a5b6c7`（新字段 + 5 新表 + ENUM 加校長）~~ ✅
- [x] ~~各表 router + schema + API（新路由 `study_online.py` + `dorm_life.py` + main.py 注册）~~ ✅
- [ ] **待向老师确认（非阻塞）**：日本人帰国 / 通常时帰国是否有别的实物表（目前只有留学生・長期休暇 様式3-1）→ `approval_chain.py` 里 `("帰国", False)` 仍是暂定值

**✅ 学生端 iPhone iOS — 实装完成（2026-05-28，codex gpt-5.5 xhigh 干活 + CC 审查 + 独立 xcodebuild 验证全过）**（§14 映射）：
- [x] ~~出寮届 ApplyForm 扩展：帰省 is_long_vacation 选择 + 新字段 + 食事日本人 / 留学生分支 + 命名班车（西口便等）~~ ✅
- [x] ~~帰国届 ApplyForm（飛行機字段 + 校長 chain 显示）~~ ✅ 含修复 `ApprovalRole` 枚举缺「校長」bug（之前会错显示成「管理係」）
- [x] ~~学習在线申请 view（类型 A：期间 + 周时间表月~金 + 契约书凭证 + 3 天前提交）~~ ✅ 新建 `StudyOnlineForm.swift`
- [x] ~~行事企画 ApplyForm + 列表~~ ✅ 新建 `DormLifeForms.swift`
- [x] ~~冷蔵庫購入 view（A:47L 1万 / B:85L 2万 二选一）~~ ✅
- [x] ~~物品所持 ApplyForm~~ ✅
- [x] ~~各申請界面接 backend 新接口~~ ✅ 新建 `StudyOnlineAPI`(在 StudyAPI.swift) + `DormLifeAPI.swift`
- [x] ~~在线学习 / 冷蔵庫 / 物品所持「我的提交列表」~~ ✅ 第二轮补（行事企画第一轮已做）
- [ ] 日課変更：iOS 学生端**不做**（责任者 / 老师提交、归 Web）— 设计如此，不是漏
- [ ] **iOS 6 新界面逐屏运行点查** — CC 只验证了编译通过 + app 启动不崩，没逐屏点（macOS 没装模拟器自动点击工具 + 后端没起）。**itsuki 用演示版手动走一遍确认能填能提交**

**演示版（demo build）修复 — 2026-05-28 同会话（codex 跑 xcodegen 引入的回归 + itsuki 演示需求）**：
- [x] ~~Demo 编译配置回归修复~~ ✅ codex 第一轮 `xcodegen generate` 擦掉了手动配的 Demo 配置 → 写进 `project.yml`（Debug/Release/Demo + DEMO 开关 + 两个 scheme），永久 regen-safe
- [x] ~~demo 和正式版区分~~ ✅ 独立 bundle id（`com.itsuki.tomoshibi` / `.demo`）+ 显示名（Tomoshibi / Tomoshibi Demo），可同时装
- [x] ~~demo 房间号默认 A5~~ ✅ `SEED.user.room`
- [x] ~~demo 注册第五步认证码预填 + 直接进~~ ✅ `#if DEMO` 包（只演示版有，正式版无 → 顺带解决 A-035「000000 后门是生产漏洞」）
- [ ] **A-035 可关闭**（§🚧 A-035）：「000000 注册后门」担忧已解决 — 现在 bypass 只在 `#if DEMO`、生产版不含。下次清 A-035 时确认关闭

**Android — 暂不走（itsuki 5-28 拍板待 iPhone 后再说）**：
- [ ] 参考 iOS §14 + iPhone 实装完成版镜像实装（出寮届扩展 / 帰国届 / 学習在线 / 行事企画 / 冷蔵庫 / 物品所持）

**老师 Web teacher_web — 暂不走（itsuki 5-28 拍板待 iPhone 后再说）**：
- [ ] 各申請的审批 / 处理界面（含 4 种新表单）
- [ ] 学習欠席届**一人审查**界面（学習担当 / 晚自习监督老师、§7.3.5 拍板、不做多角色链）
- [ ] 冷蔵庫購入采购流程（注文担当 / 請求担当 / 本人签收）
- [ ] 日課変更审批（国際交流部長 + 寮担当）

**设计文档同步**：
- [ ] BACKEND_DESIGN_LOG 同步申請实物補完
- [ ] ANDROID_DESIGN_LOG 同步（参考 iOS §14）
- [ ] WEB_DESIGN_LOG 同步老师审批 / 处理
- [x] ~~IOS_DESIGN_LOG §14~~ ✅ 2026-05-28 已写

**待向老师确认（非阻塞）**：
- [ ] 日本人帰国 / 通常时帰国是否有别的实物表（目前只有留学生・長期休暇 様式3-1）

## 🚀 teacher_web v1.0「直接上线」backlog（2026-05-27 审查产出 — 优先级最高）

> **背景**：5-27 晚段-2 itsuki 让 CC 对 teacher_web 做审查 — 目标「让网站达到可以直接上线的水平」。CC 扫了 `WEB_DESIGN_LOG.md` / `DESIGN_BRIEF.md` / `system_features.md` / `v1/src/` 实际目录后**诚实结论**：**目前没到「直接上线」水平**。UI 90% ✅ + Login 真接 backend 1/16 ✅ + 其他 15 个 page 全部假数据 ⏳。本段集中列「要达到直接上线还差什么」。
>
> **5-27 backend 状态**：5-27 醒后会话 CC 大批修 backend（8 commits / 9 处 bug + 实装 spec §11.4 改判扣分联动 + spec §7.5 自动扣分 + WebSocket + alembic c1d2e3f4 3 张表 + 8 个新 P0/P1 endpoint）→ **backend 接入就绪，只剩 frontend 调用**。详见 `05_logs/raw/2026-05-27_teacher_web_v1.0_深夜推进.md §9`。

### 🚀-A 5-27 审查已修 drift（CC 自己做掉，不需要决策 — 已闭合）

- [x] ~~**`WEB_DESIGN_LOG.md` §1 速查表 4 处 drift 校准**~~ ✅ 2026-05-27 闭合 — (1) `index.html` 7774 → **24041 行**（5-26 polish + 之后多次推进累积）/ (2) `_legacy/*.jsx` 路径错 → 实际 `components/_legacy/*.jsx`（14 个 jsx 名单全列）/ (3) `demo_server.py` 「死链 / 失效」描述错 → 实际文件真存在 142 行 + `tomoshibi` CLI 调它正常 / (4) A-039 明文密码 🔴 未修 → 实际 5-26 commit `b0bed26` 已删 ✅
- [x] ~~**`DESIGN_BRIEF.md` §1 + §2 文件清单 drift 校准**~~ ✅ 2026-05-27 闭合 — `index.html` 行数刷 / `components/_legacy/` 路径修 / `demo_server.py` 加进文件清单 / `client.js` + `client.ts` 两个都列出
- [x] ~~**`BACKEND_DESIGN_LOG.md` §12 改订履历加 5-27 实装行**~~ ✅ 2026-05-27 闭合 — 9 处实装入档（spec §11.4 改判扣分 / WebSocket / 自动扣分 / R4 helper / 3 张新表 / 权限收窄等）
- [x] ~~**`project-overview/SKILL.md` §3.3 backend/v1/app/ 核心加 `ws_manager.py`**~~ ✅ 2026-05-27 闭合 — 9 → 10 文件 + `deps.py` 加 R4 helper 注记 + `models.py` 表数 13 → 21+

### 🚀-B 真后端对接 — 15 个 page（最大阻塞 — 直接上线必做）

> 当前只有 Login（`/login` LoginScreen `b0bed26` 5-26 已接 `POST /api/v1/sessions/teacher`）真接 backend。其他 15 个 page 全部读 `window.ROSTER_MEN/WOMEN/ACCOUNTS/OUTSTAY_APPS` 等假数据。**backend 已就绪**（5-27 实装完），frontend 接入只剩调用。

#### B-1 优先级 P0（核心 use case — 没接 = 等于没上线）

- [x] ~~**`/login/select-teacher` SelectTeacher**~~ ✅ 2026-05-27 凌晨闭合 — commit `9234882` 接 `client.js listTeachers()`
- [x] ~~**`/roll-call/live` LiveRollCall 接 backend**~~ ✅ 2026-05-27 凌晨闭合 — commit `248c899`（startSession 接 board）/ `9e3b527`（endSession 接 backend）/ `e70315c`（WebSocket 实时事件接入 onMessage 处理）
- [x] ~~**`/roll-call` landing 7 天趋势图 + 4 session 类型**~~ ✅ 2026-05-27 凌晨闭合 — commit `35873c2` RecordsPage + landing 共用 `rollcallSessionsHistory` helper
- [x] ~~**`/applications` 申请センター list + 承認**~~ ✅ 2026-05-27 凌晨闭合 — commit `fc9c4a5` ApplicationsPage 接 `pendingForMe`
- [x] ~~**`outstay-detail-modal.jsx` 申请详情**~~ ✅ 2026-05-27 凌晨闭合 — commit `2a3650a` OutstayDetailModal `onAction` 接 backend `decide`

#### B-2 优先级 P1（次要核心 — 接 backend 已就绪）

- [x] ~~**`/discipline` 扣分排名**~~ ✅ 2026-05-27 凌晨闭合 — commit `bd3dc25` 接 `getDisciplineRanking` + commit `0c5da45` client.js 加 3 helper
- [x] ~~**`/cleaning` 清掃**~~ ✅ 2026-05-27 凌晨闭合 — commit `8e7aa5c` CleaningPage 接 `listCleaning`
- [x] ~~**`/front-desk` 宅配 + 忘れ物**~~ ✅ 2026-05-27 凌晨闭合 — commit `8e7aa5c` FrontDeskPage 接 `listFrontDesk`
- [ ] **`override-modal.jsx` 手动调整** — `PATCH /api/v1/rollcall/events/{id}`（5-27 backend 实装 spec §11.4 改判扣分联动 commit `69e840b`，frontend override-modal 未接 client.js — 改完会自动触发 backend 扣分逻辑）
- [x] ~~**学生登録コードパネル**~~ ✅ 2026-05-27 凌晨闭合 — commit `ab6653d` Task #14 RegistrationCodePanel + §11.9.1 6 桁 mono + 倒计时 + 寮務 gate
- [x] ~~**`/records` 签到历史**~~ ✅ 2026-05-27 凌晨闭合 — 同 `/roll-call` landing commit `35873c2`
- [ ] **shell topbar 全局搜索** — `window.ROSTER_ALL` → `client.js searchStudents(q)` → 接 backend 搜索（backend `GET /accounts` list endpoint 暂未实装，归 §🚀-B-3 P2 范围）

#### B-3 优先级 P2（backend 未实装 — 强做 = 假接通 = 不诚实）

> itsuki 5-27 拍板「假接通 = 不诚实」— 这些 backend P2 endpoint 没实装前 frontend **不强做**。等 backend 这部分实装到 v1.1 / v1.2。

- [ ] **`/notifications` 通知聚合** — backend P2 endpoint 未实装，frontend 保持假数据状态显示「未来接 backend」
- [ ] **`/community` 寮掲示板 + リクエスト曲 + 忘れ物 + 宅配** — backend P2 endpoint 未实装（5-27 砍「匿名建議」tab，system_features §7.14 4-29 拍板）
- [ ] **`/info` 寮内通知 + 行事カレンダー** — backend P2 endpoint 未实装（部分老师公告走 announcements 已有，但 InfoPage UI 不止公告）
- [ ] **`/accounts` 学生账号管理 list** — backend `GET /accounts` list 未实装（POST /accounts 注册有了，但 list 没了）
- [ ] **バス時刻** — backend P3 endpoint 未实装

### 🚀-C 缺失 UI（3 个 SkeletonTab + 老师公告发布页）

- [x] ~~**`/applications/return` 帰国 申请页**~~ ✅ 2026-05-27 凌晨闭合 — commit `1243de9` Task #16 3 SkeletonTab UI 補完
- [x] ~~**`/applications/home` 帰省 申请页**~~ ✅ 同上
- [x] ~~**`/applications/taxi` タクシー 申请页**~~ ✅ 同上
- [ ] **老师公告**「发布页 UI」** — backend 5 端点全有（5-27 client.js 也补 4 helper），但 frontend 没**发布编辑器** UI（A-026 已补 type 但 UI 不在范围）

### 🚀-D 协议 / 体验细节

- [ ] **WebSocket 重连机制 + 「再接続中」banner** — spec §11.8 要求 frontend 断线自动重连 + 状态指示器，当前 `client.js openTeacherWS` 只 `console.error`，UI 没 banner
- [ ] **启动入口梳理（2026-05-28 部分变更）** — 原 `开发模式跑.command`（调 `python3 -m http.server`）已归档到 `99_archive/2026-05-28_开发模式跑_被启动全套脚本替代/`。现在两个入口用途不同：双击 = 项目根 `启动老师网站.command`（起后端 8000 + 前端 8787，**正式登录用**）/ CLI = `tomoshibi` → `python3 demo_server.py`（**NFC 实时点呼演示用**）。如要统一 NFC 演示行为再定
- [ ] **spec §11.3 改判时限矩阵** — PATCH /events/{id} 没校验 7 天 / 30 天 / 月结后只读 — 5-27 backend 没实装 / frontend 没限制 UI

### 🚀-E 直接上线 = 还差什么（一句话总结 — 给 itsuki 起床看）

| 维度 | 现状 | 缺什么 |
|---|---|---|
| UI 完成度 | 90% ✅ | 3 个 SkeletonTab + 老师公告发布页 UI |
| 真后端对接 | 1/16（Login）✅ | 15 个 page 调 client.js（backend 已就绪）|
| WebSocket 实时 | backend 实装 ✅ / frontend 接入 ⏳ | LiveRollCall 接 `openTeacherWS()` + 重连 banner |
| spec 一致性 | §11.4 改判扣分 ✅ / §7.5 自动扣分 ✅ | §11.3 时限矩阵（backend + frontend 都没做）|
| 启动脚本 | 双入口行为不一致 ⏳ | 统一到 `demo_server.py` |
| Demo 兜底 | NFC 实时 demo 失效（启动脚本不调 demo_server.py）⏳ | 修启动脚本（30 秒事）|
| **总结评估** | 🟡 alpha（demo 给管理员看可以）| 🔴 离「学生 / 老师真用」还差 15 个 page 真接 backend |

→ 估工作量：B-1 / B-2 加起来 12 个 page 真接 backend ≈ 1 个 page 平均 1-2 小时（HTML inline 写 fetch 调用 + 替换 `window.*` 假数据）= 12-24 小时；B-3 + C + D 跳过或 v1.1 做 = 0 小时（不做）；上线最快路径 = **12-24 小时纯接入工作 + 测试 1-2 小时**。

### 🚀-F 5-27 早段醒后审查 backlog（真留待办 — itsuki 起床看）

> **背景**：5-27 早段 itsuki 启动「审查我做的事到底做好了没」+「不需要决策的直接修 / 决策的加 TODO 跳过 / 收尾后直接关会话」→ CC 自查 5 维度全过（alembic ✅ / 13 router 注册 ✅ / 61 endpoint import 通过 ✅ / Student.is_demo 字段已加 ✅ / client.js 32 helper 跟 backend 路径 100% 对齐 ✅）+ 5 处日语注释中文化收尾。下面是醒后审查后剩余的真待办（itsuki 决策范畴 / production 推进需要的 step）。

- [ ] **production DB 跑 `alembic upgrade head` 应用 c1d2e3f4** — 开发环境已 upgrade ✅（5-27 凌晨验证），但 itsuki 真上线前要在 production 环境跑同样命令（3 张新表 demerit_event / cleaning_assignment / front_desk_item）
- [ ] **`override-modal.jsx` 手动调整接 backend `PATCH /events/{id}`** — backend §11.4 改判扣分联动已实装（5-27 commit `69e840b`），frontend override-modal 还在用假 onAction，需补一个 client.js call（约 1 小时）
- [ ] **shell topbar 全局搜索 — 等 backend GET /accounts list endpoint 实装**（P2 范围 / 待 itsuki 决定字段）
- [ ] **backend P2 工作 — CommunityPost + Notice 字段决策**：
  - CommunityPost 匿名 author_id 字段怎么处理（NULL / 哈希 / 单独表）
  - Notice vs Announcement 是合并成一个 model 还是分开（spec §7.13 vs §7.15）
  - 没决策不能继续 frontend NotificationsPage / CommunityPage / InfoPage 真接 backend
- [ ] **93 commit 未 push origin/main** — itsuki 5-26 23:55 拍板「不 push 到 GitHub / 继续到撞墙」执行中，等 itsuki 拍板何时 push（建议 v1.0 alpha 验证完一次 push）
- [ ] **review `01_specs/teacher_web_v1.0_backend_models_propose.md` 229 行 propose 文档** — 5-27 凌晨 CC 替默认决策的字段方案（DemeritEvent source_type 6 类 / CleaningAssignment area 8 类日文 / FrontDeskItem kind 2 类 / 阈值 4 + 8 hardcode）— itsuki 看完决定推翻 CC 默认或追加
- [ ] **`/notifications` + `/community` + `/info` + `/accounts` 4 page 等 backend P2 endpoint 实装后再接** — 这 4 个 page 当前显示「未来接 backend」假数据状态符合「假接通 = 不诚实」原则
- [ ] **WebSocket 重连机制 + 「再接続中」banner**（spec §11.8）— backend `/ws/teacher` 已实装 5-27 commit `436f316`，frontend `client.js openTeacherWS` 只 `console.error` 没 UI banner — 1-2 小时工作量
- [ ] **spec §11.3 改判时限矩阵**（7 天 / 30 天 / 月结后只读）— backend PATCH /events/{id} 没校验 / frontend 没限制 UI — 等 itsuki 起床拍板字段定义

### 🚀-G 5-27 实名账户登录 — codex 5.5 xhigh 审查剩余项（P0 + 关键 P1/P2 已在 commit 中修，下面是仍未处理的）

> **背景**：5-27 itsuki 拍板「教师登录改实名账户 + 加教师管理页」+「砍匿名建議」+「做完让 codex 5.5 xhigh 审查」。3 commit 落地（`b9f237c` backend + `b444aad` frontend + `1904b18` 设计档案），codex 审查出 3 🔴 + 7 🟡 + 3 🟢。**🔴 全修 + 关键 🟡 + 🟢 #11 #12 #13 已修**，下面是剩余 itsuki 决策 / 工作量大的项。

- [ ] **codex 审查 #4：`GET /api/v1/teachers/public` 暴露 `last_login_at`** — 让无认证爬虫能枚举账户活跃状态。UX 用途 = LoginScreen 卡片显示「N 分前にログイン」给老师辨认上次是谁用。trade-off：保留（UX 友好）vs 砍（安全更严）。itsuki 决策
- [ ] **codex 审查 #6：`DELETE /api/v1/teachers/{id}` hard delete 不考虑外键引用** — `models.py:315-316 / 655-667 / 726-727` 多张表外键引用 `teachers.id`（指导履历 / 公告作者 / 学生注册码生成人）。生产环境删时会报 constraint error 或留 orphan 记录。建议改 soft delete `status="deleted"` + 所有 list query 加 `WHERE status='active'` filter
- [ ] **codex 审查 #7：`TeacherCreateIn` 字段校验弱** — `email` 用 `str` 不是 `EmailStr` / `login_id` 没格式校验（半角英数限制？）。当前依赖 backend DB UNIQUE constraint 拦重复，但格式错误（"abc 全角" / "test@invalid"）只在 DB 层报错。建议 schemas.py 加 `EmailStr` + `login_id: str = Field(pattern=r"^[a-z0-9_]+$")`
- [ ] **codex 审查 #10：`client.js` error 包装统一化** — 当前 `request()` 抛扁平化错误（`{status, body}`），但前端模态框（TeachersAdminCreateModal 等）读 `e.body.detail.message` — backend 返 `{detail: {code, message}}` 才匹配。HTTPException 直接 raise 时 FastAPI 自动套 `{detail: ...}` ✅，但有些路径返 flat string `detail: "msg"` 时前端拿不到 — 需统一 backend 错误格式 + 改 client.js 错误抽取 logic
- [ ] **codex 审查 #13 已处理但残留可能**：扫 `WEB_DESIGN_LOG.md` 历史 round notes 里其他匿名建議 / community 相关旧描述（5-27 修了 349 + 458 两行 + tab 描述行，其他历史段如 §1-§4 Round notes 没动）— 等 v1.1 整理 WEB_DESIGN_LOG 历史段时一并清

## 📱 iOS 上架冲刺 — 剩余事项（2026-05-08 状态）

> **2026-06-03 重新校准（itsuki + Opus 4.8 会话）** — 本段 5-08 状态已半年，实测 + itsuki 确认校准：
>
> **现状核实**：线上 `api.tomoshibi.cc` 实测在线（HTTP 200 / 0.66s），但跑的是 5-08 骨架版（`0.1.0-v1-skeleton` / 40 接口）；本地开发版 61 接口 —— 这半年功能（实物申请表 / 老师实名登录 / 扣分统计 / 请假计数 / 今天定的老师退回 / 学習対象 / 通知）线上都没部署。测 `/me`、`discipline/me/summary`、`absence-requests/me/summary` 线上全 404。
>
> **itsuki 确认 3 事实**：① 5-08 卡在 Validate 就停了，**app 从没真正提交过苹果审核**（这次=首次上架）② 苹果开发者账号还在续费有效 ③ 谷歌云服务器 itsuki 在付费维护、知道它在跑。
>
> **分发方式拍板**：**公开上架 App Store**（不是 TestFlight 内部分发）。配套建议：app 加「无注册码停在登录页」，外人下载也进不去（防审核质疑「外人下载没用」+ 防滥用）。
>
> **工作流拍板（itsuki）**：后端先在本地做完所有功能，最后再一次性部署到服务器（不边做边传 — 每次部署有风险 + 审核期线上必须稳）。
>
> **三阶段路线**：
> 1. **本地做完功能**（当前阶段）：iOS B 类接后端剩余（老师退回 / 学習対象 / 通知子系统）+ 对应后端 + 低风险 bug + 能直接修的 bug。
> 2. **后端一次性部署**：本地 SQLite → 线上 PostgreSQL（踩 §🐛 段 3 个部署坑）+ 完整后端传上 `api.tomoshibi.cc`。
> 3. **iOS 提交审核**：填 `DEVELOPMENT_TEAM`（现空）+ 开真机签名（现 `CODE_SIGNING_ALLOWED:NO`）+ 补 Info.plist `NFCReaderUsageDescription` + 降 deploymentTarget（现 iOS 26 偏高）+ Archive → Validate → Upload + 截图/元数据/隐私声明 + Submit。
>
> **今天（6-03）拍板的 v1.0 功能范围**：
> - ✅ **IX-007 其它类申请（修繕/来訪/代理受取）不进 v1.0** —— 后端零实装、太麻烦，往后堆。今晚已按 Option A 做完「生产不读假数据」(`457077f`)；Option B（真做这功能：后端建表 + 5 端联动）推迟。
> - 🔴 **老师「退回(差戻)」动作 v1.0 必做** —— 后端 `_recompute_application_status` 现产不出 `returned` 状态 + teacher_web 加退回决策按钮 + iOS 已前向兼容（"returned 可编辑"已埋好）。spec §7.2.4-5 要求。
> - 🔴 **学習対象 is_study_target 后端字段要做**（之前跟晚自习 UI / tier 决策缠一起，6-03 拍板做）。
> - 🔴 **通知子系统 v1.0 完整方案**（IX-009 扩展）：
>   - 内容源 5 类：公告 ✅已接 / 审批结果 / 包裹到了 / 扣分迟到 / 签到提醒
>   - 送达：app 内通知列表 + push 推送
>   - **通知设置页：每类通知用户可单独关闭**（苹果审核合规必需 — push 必须可拒绝）
>   - push 要 APNs（苹果推送服务）证书 + 后端推送服务 = 5-08 没碰过的新大块
>
> **2026-05-21 注（B-006 修）**：本段 + 下方 §🐛 + §🛰️ 都把「✅ 已完成」+「待办」混在同一 list 里 — CC 扫 200 行容易误判已完成项当待办处理。**已完成项已用 `[x] ~~strikethrough~~` 标识 / 待办用 `[ ]`** — 看 checkbox 状态判断。

> **会话状态**：5-07 启动「上线 iOS 到 App Store」目标 → 5-08 完成 backend 部署到 GCP VPS（asia-northeast1）+ DNS（api.tomoshibi.cc）+ GH Pages（privacy / support）+ Apple Developer Portal App ID + ASC App「Tomoshibi · 灯火」+ Xcode 编译。**5-08 21:30 卡在 Validate App** 失败（CFBundleShortVersionString empty）— 已修 fork project.yml 用 MARKETING_VERSION 写法 + 让 itsuki 在 Xcode General tab 直接填 Version 1.0.0 / Build 1，待重新 Archive。
>
> **凭证**（Apple Reviewer Notes 用，**5-08 修复后版**）：reviewer 学号 `999999` / 密码 `Tomoshibi-Reviewer-2026!`（is_demo=True 学生）+ admin login_id `admin` / 密码 env `ADMIN_INITIAL_PASSWORD`（fallback `ChangeMe-2026-05` 仅 dev 兜底）。`999999` 注册码改为 `is_reviewer=True` 永久标志，但**Reviewer Notes 不写注册码**（防 OCR 泄漏）。强密码 POSTGRES_PASSWORD / JWT_SECRET 在 VPS .env（不在 git 里）。详见 `system_features.md §7.20`。

### A. 今晚冲提交剩余步骤（itsuki 操作）

- [ ] Xcode General tab 填 Version: `1.0.0` / Build: `1`（修 Validate 失败的 CFBundle empty bug）
- [ ] Product → Archive 重新跑
- [ ] Validate App 通过
- [ ] Distribute App → App Store Connect → Upload
- [ ] 等 ASC processing build 完成（10-30 min）
- [ ] Simulator 截图（iPhone 16 Pro Max）至少 3-4 张（Login / Home / 申请列表 / MyPage）
- [ ] ASC 元数据填表（fork METADATA.md 复制粘贴）
- [ ] ASC App Privacy 数据声明（METADATA.md §5 对照表填）
- [ ] App Icon 1024 PNG 上传 ASC（fork 内 `~/dev/Tomoshibi-AppStore/ios/TomoshibiApp/AppIcon-1024.png`，CC 5-07 用 swift Cocoa 合成 1024×1024 无 alpha 红渐变 + 火焰）
- [ ] Reviewer Notes 双语填（METADATA.md §6 完整复制）
- [ ] Submit for Review

### B. v1.0.0 上架审核**通过当天立刻**做 <!-- VERSION_OK -->

- [ ] **admin 密码立刻改强密码** — env `ADMIN_INITIAL_PASSWORD` 设强密码 + web 后台改账号密码（1Password 生成）
- [ ] **删 VPS prod DB 旧 reviewer 学生 060199**（5-08 fork seed 创建的，新 prod seed 用 999999 学号，旧行需手动清理）：
  ```sql
  DELETE FROM accounts WHERE student_id IN (SELECT id FROM students WHERE grade_code='06' AND class_code='01' AND seat_no='99');
  DELETE FROM students WHERE grade_code='06' AND class_code='01' AND seat_no='99';
  ```

### C. ✅ Reviewer demo 5 个设计缺陷 — 已修复 <!-- VERSION_OK -->

5-08 21:35 主 CC review 戳穿 5 个 bug → itsuki 拍板「修干净再提交」→ v1.0.1 修理项全部提前在 v1.0.0 修完。详见 §🐛 `Demo seed / 999999 注册码后门 — 已修复` ledger。 <!-- VERSION_OK -->

### D. 工程债务延后修

- [ ] **Fork backend 4 文件合回主项目**（5-08 拍板，落实 5-06「single source」）：把 `~/dev/Tomoshibi-AppStore/backend/` 的 `Caddyfile` / `Dockerfile` / `docker-compose.yml` / `DEPLOY.md` 移到 `03_dev/backend/v1/`，删整个 fork 目录。VPS 改为 rsync 主项目 v1 → VPS。需要先把 5-08 fork 跟主项目剩余差异合并（看 `diff -r` 输出）
- [x] ~~**iOS fork 处置**（`~/dev/Tomoshibi-AppStore/ios/`）~~ ✅ 2026-05-27 闭合 — 5-22 已整体归档到 `99_archive/2026-05-22_tomoshibi_appstore_fork/`，原路径删除。diff 归档 vs 主项目：fork 独有文件 0 个，所有改动（含账号删除 UI）已同步主项目
- [ ] 反向 rsync VPS migration patch → Mac fork（VPS CC 在 `b2c3d4e5f6a7_align_application_schema.py` 改成 dialect-aware，Mac fork 还是 buggy 版本，下次 rsync 会回退）：
  ```bash
  rsync -avz \
    itsuki@34.85.74.70:~/tomoshibi-backend/alembic/versions/b2c3d4e5f6a7_align_application_schema.py \
    ~/dev/Tomoshibi-AppStore/backend/alembic/versions/b2c3d4e5f6a7_align_application_schema.py
  ```
- [ ] UptimeRobot 配 https://api.tomoshibi.cc/healthz 5 分钟监控（Apple 审核期 24-72h 必须 100% 在线，挂 5 分钟以上 reject 风险）
- [ ] 主项目 v1 backend `app/main.py:70` 加 production guard 防 create_all（跟 §🐛 v1 backend bug fix #2 配套，防止未来 v1 部署 prod 又踩坑）
- [ ] **iOS `StayListStubs.swift:475` catch 降级到 mock 假数据问题** — 当前 `ApplicationsAPI.listMine()` 失败时降级到 `StayListMock.all`（注释说「避免空 view 影响调试」），但 v1.0 上线后用户看到假数据。修法：catch 改区分 `APIError.unauthorized` → 用 mock（未登录态兜底，符合 line 458 A-037 注释意图）/ 其他错误 → 显示错误提示 + 空 view 不降级。**审查发现于 2026-05-27 深夜 iOS 审查会话**
- [ ] **iOS `MyPageStubs.swift:1637` catch 暴露 `error.localizedDescription` 给用户** — `deleteError = "通信失败 — \(error.localizedDescription)"` 会把 Swift / URLSession 的英文技术错误（如 "The data couldn't be read..."）直接给学生看。修法：catch 改区分 `APIError.network` / `.server` / 其他 → 显示日语友好提示。**审查发现于 2026-05-27 深夜 iOS 审查会话**

### E. 跨端同步遗留（不阻塞今晚）

- [x] ~~iOS 端账号删除（账号删除 UI + DELETE /accounts/me）~~ ✅ 2026-05-27 闭合 — 主项目 `AuthAPI.swift:52 AccountsAPI.deleteMyAccount()` + `MyPageStubs.swift:1632` 界面 + 调用全装好。5-22 归档 fork 时已同步完成
- [ ] 主项目 v1 alembic/env.py 加 DATABASE_URL env override（已在 §🐛 v1 backend bug fix 跟踪）

---

## 🐛 主项目 v1 backend bug fix（2026-05-08 上架版部署时发现）

> **背景**：5-08 把 fork 的 backend（`~/dev/Tomoshibi-AppStore/backend/`）部署到 GCP VPS production Postgres 时，连续踩到 3 个隐藏 bug。**上架版 fork 已修，主项目 v1 同源代码也有同样 bug**。当前不影响 v1 dev（dev 用 SQLite 走的是 buggy 路径但表现正常），但**未来 v1 真要部署到 prod Postgres 会一一踩到**。建议下次有空时单独 commit 修这 3 个 bug，保持 v1 跟 fork 同步。

- [ ] **Bug 1: `alembic/env.py` 不读 env DATABASE_URL** — alembic 默认读 `alembic.ini:89` 硬编码 SQLite URL，env.py 不会自动 fallback 到环境变量。**修法**：env.py 在 `config = context.config` 之后加 4 行
  ```python
  if os.environ.get("DATABASE_URL"):
      config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
  ```
  fork 已修：`~/dev/Tomoshibi-AppStore/backend/alembic/env.py`
- [ ] **Bug 2: `docker-compose.yml` 不传 `APP_ENV`** — v1 当前没 docker-compose.yml（fork 才加的），所以暂时不会踩。**未来 v1 加 docker 部署时**：api service 必须显式传 `APP_ENV: ${APP_ENV:-production}`，否则 `app/config.py:21` 默认 `"dev"` → `app/main.py:70` 跑 `create_all()` 绕过 alembic
- [ ] **Bug 3: `alembic/versions/b2c3d4e5f6a7_align_application_schema.py` 用 SQLite-only 的 `batch_alter_table(recreate='always')`** — Postgres 部署时强制 DROP + 重建 applications 表，包括 drop applications_pkey，但 application_approvals 外键依赖它 → migration 失败。**修法**：让 upgrade/downgrade 根据 `op.get_bind().dialect.name` 分支（SQLite 保留 batch / Postgres 用普通 op.xxx）。**5-08 fork 修法待 VPS CC 落地后同步，那边方案确定后填**

### ✅ Demo seed / 999999 注册码后门 — 已修复（2026-05-08 同日重做完毕）

> **背景**：5-08 上架冲刺时 fork 直接塞 `999999` 永久码进 prod DB（`expires_at=2030`），主 CC review 戳穿 5 个 bug。itsuki 拍板「修干净再提交」→ 全部 v1.0.1 修理项提前在 v1.0.0 修完。详细 raw → `05_logs/raw/2026-05-08.md`。 <!-- VERSION_OK -->

**5-08 已完成清单**（commit 待 push）：
- [x] Schema 加 `students.is_demo` + `student_registration_codes.is_reviewer`（migration `f6a7b8c9d0e1`，含 `UPDATE invalidated_at=NOW() WHERE code='999999'` 把 fork 塞进 VPS prod DB 的旧行作废）
- [x] `/refresh` 加 `is_reviewer=False` 过滤 — reviewer 码不被作废
- [x] `/current` 加 `is_reviewer=False` 过滤 — 老师面板不可见（防泄漏）
- [x] `_generate_code` random 范围 `[0, 999998]` — `999999` reserved
- [x] Admin 学生列表 3 处加 `is_demo=False` 过滤（rollcall.session_board / rollcall._settle_absent / applications.list_pending_for_me）
- [x] `seed.py` 双源合并 — `APP_ENV=dev|production` env 切换；Mac fork `~/dev/Tomoshibi-AppStore/backend/` 待删（5-06 single source 拍板落实，见 §G）
- [x] Reviewer 凭证升级 — 学号 `999999`（grade=99/class=99/seat=99）/ 密码 `Tomoshibi-Reviewer-2026!` / 注册码 `999999` `is_reviewer=True` 永久
- [x] admin 默认密码移到 env `ADMIN_INITIAL_PASSWORD`（fallback 仅 dev 兜底，prod 必须设 env）
- [x] 5 个新 pytest case（test_demo_reviewer.py），全套 42 passed
- [x] system_features §7.20 + §7.16 例外条款 / BACKEND_DESIGN_LOG §5.x.4 / IOS_DESIGN_LOG §3.16 同步

**上架审核通过当天**剩余动作：
- [ ] admin 密码立刻 web 后台改强密码（1Password 生成 + 不进 git）

---

## 🛰️ 点呼机第 5 端 backlog（2026-05-08 itsuki 拍板「点呼机当第 5 端」）

> **背景**：2026-05-08 itsuki 拍板把点呼机当第 5 端,跟 backend / iOS / Android / teacher_web 4 端对称管理。同日完成:配件型号定型(PN532 V3 / LED 模块 / 01Studio 小音响 / Pi 3A+ 透明壳 / 面包板杜邦线)+ `03_dev/rollcall_device/` 骨架建成 + `ROLLCALL_DEVICE_DESIGN_LOG.md` 11 章纲建成 + 联动机制 12→18 条规则升级（5 端反向规则 + 端→共用层）+ `bus_schedule_real.md` 从 02_design 挪到 06_assets。
>
> **当前状态**：骨架阶段 ⏳。代码 0 行,等 itsuki 拍板 D1-D6（见 ROLLCALL_DEVICE_DESIGN_LOG §10）+ 配件实物到货后开始实装。
>
> **优先级**：P2 — backend v1 上线后再启动（点呼机依赖 backend API）。在此之前可以先买配件 + 装 Pi OS + 学 GPIO 基础。

### 配件采购（2026-05-22 撤回中国海运渠道 → 日本本地买）

> **2026-05-22 方向反转**：5-12~16 之间原计划那批 11 件配件走中国海运被海关查扣全没（原因：为省运费打成一个包裹，某 1-2 件触发查扣 → 全部连带没收）。itsuki 拍板：被拦的不要了，改日本本地买。理由：(1) 避免再被查扣；(2) 配件坏了维护方便（本地有备件 + 退换货走日本邮政）。
>
> 详细 AC 素材见 `05_logs/raw/2026-05-22.md`；决策日志草稿待新能力模块 `decision-log-write` 产出后由 itsuki 粘到 `05_logs/decision_log.md`。
>
> 原淘宝清单（¥381 RMB）+「下单」「收货清点」2 条任务作废。

- [ ] **重新选型 6 类硬件（日本本地能买的型号）** — Pi 3A+（或 Pi 4 / 5 升级）/ PN532 V3 红板 / ST25DV16K I²C 模块 × 2 / NTAG215 × 50 / LED 5 色 + 杜邦线 + 面包板 / USB 小音响 + 透明外壳 + 风扇 + 5V 电源
- [ ] **渠道调研** — Amazon.jp / 秋月電子（akizukidenshi.com）/ スイッチサイエンス（switch-science.com）/ 千石電商 / Yahoo Auction（旧物）/ メルカリ（旧物）
- [ ] **预算重估** — 日本本地价 vs 原中国海运价 + 海关风险溢价（预计贵 1.5~2 倍但消除海关风险 + 提速到货）
- [ ] **更新 `02_design/hardware_design.md` §2** — 全部型号 / 价格 / 渠道字段（日本重新选型出结果后改）
- [ ] **更新 `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md §1.2`** — 加 5-12~16 海关事件 + 改日本买（本会话内做）
- [ ] **拆寄不打包寄**（5-22 教训）— 如果将来还要从中国寄某些件，拆成 2-3 包分批寄，避免再触发「一件查扣全没」

### 拍板 6 个软件层决策（D1-D6,详见 ROLLCALL_DEVICE_DESIGN_LOG §10）

- [ ] **D1**：PN532 用什么 Python 库 — `nfcpy`(社区) / `Adafruit-PN532`(轻量) / 二选一
- [ ] **D2**：ST25DV16K 驱动方案 — (a) 自写底层 I²C 寄存器读写 / (b) port Arduino C++ 库到 Python / (c) 用 C 写 daemon, Python 调 — **真挑战,1-2 周学习成本**
- [ ] **D3**：日语 TTS 方案 — `pyttsx3` 离线 / Google Cloud TTS 联网 / 预录音频文件
- [ ] **D4**：PN532 接 Pi 用 SPI 还是 I²C — SPI 稳但占 GPIO 多 / I²C 占 GPIO 少但 Pi 上不稳
- [ ] **D5**：是否用 WebSocket 接收老师端推送 — HTTP 轮询 / WebSocket
- [ ] **D6**：设备认证方式 — 设备 ID + 密钥 / JWT

### 实装顺序（D1-D6 拍板后,按这个顺序 1 周一个里程碑）

- [ ] **M1**：Pi 装 Raspberry Pi OS Lite 64-bit + SSH + 静态 IP
- [ ] **M2**：写 `nfc/pn532.py` — 读 NTAG215 卡 UID（开发期手动测）
- [ ] **M3**：写 `led/led.py` — GPIO 状态机（蓝/绿/红/白）
- [ ] **M4**：写 `api/client.py` — POST `/checkin` 调 backend（mock 阶段）
- [ ] **M5**：串 `main.py` 主循环（IDLE → SUBMITTING → SUCCESS / FAIL → IDLE）
- [ ] **M6**：写 `nfc/st25dv.py` — 自写 I²C 驱动（D2 拍板后,**真挑战段**,1-2 周）
- [ ] **M7**：写 `audio/player.py` — 日语播报（D3 拍板后）
- [ ] **M8**：写 systemd unit + 开机自启 + 故障重启
- [ ] **M9**：部署到真宿舍点呼一次（M1 demo）

### 物理 + 部署待办

- [ ] 宿舍现场勘察 — 点呼机贴在哪面墙 / 距离 WiFi AP / 电源线长度（见 `hardware_design.md §6`,等 itsuki 问老师）
- [ ] 部署 SOP 写到 `03_dev/rollcall_device/docs/部署SOP.md`（M9 时一边做一边写,做下次部署的真值）
- [ ] 跟管理员谈「断网时点呼机怎么办」(故障恢复策略,影响 ROLLCALL_DEVICE_DESIGN_LOG §6)

### 同步 / 联动

- [x] **2026-05-08 完成**：建 `03_dev/rollcall_device/` 骨架（README + DESIGN_LOG + requirements.txt + src/main.py + 4 个空模块包 + config + docs 占位）
- [x] **2026-05-08 完成**：联动机制 12→18 条规则升级（加 5 端反向 + 端→共用层）+ Rule 3 system-features 加 ANDROID + ROLLCALL_DEVICE
- [x] **2026-05-08 完成**：CLAUDE.md「设计文档双层」从「3 端」补到「5 端 + 物理硬件层」+「文件连锁结构」加反向规则 6 条 + 目录结构加 rollcall_device
- [x] **2026-05-08 完成**：file-linkage / project-overview / 同步点清单 / hooks README 全部同步到 18 条规则
- [x] **2026-05-08 完成**：`02_design/hardware_design.md` §2.2 / §2.4 / §2.5 占位回填 + §0 状态表全 ✅ + §2.3 「Pi 4B」漂移修成 Pi 3A+
- [x] **2026-05-08 完成**：`02_design/bus_schedule_real.md` 挪到 `06_assets/`（数据,不是设计）

---

## 🛠️ Meta / CC 协作改进（2026-05-07 itsuki 拍板）

- [ ] **做一个「教学类 Skill」** — 暂名 `.claude/skills/teach-as-you-go/SKILL.md`
  - **背景**：CC 给 itsuki 操作指南时容易直接丢「点这里 / 输这个」，没解释「这是什么 / 为什么必须做 / 为什么这样选不那样选」。itsuki 是零基础学习者，每个操作都是学习机会，不解释 = 偷懒。
  - **触发场景**：itsuki 第一次接触某个工具 / Apple Developer Portal / Xcode 操作 / 命令行 / 第三方服务（Vultr / Cloudflare / GitHub Pages / SSH 等）→ CC 必须**当下解释**：
    1. 这是什么（概念）
    2. 为什么必须做（不做的后果 / 跳过的代价）
    3. 为什么这样选不那样选（多选项时给对照表）
    4. 操作背后的工作流程（如「为什么签名要先在网页声明 capability」这种黑盒链路）
  - **反触发**（不要触发）：itsuki 已经做过 N 次的操作（git commit / Xcode Cmd+B 等）— 不重复啰嗦
  - **触发实例（2026-05-07 教训）**：上架流程让 itsuki 在 Apple Developer Portal 勾「NFC Tag Reading」时 CC 只丢指令，没解释「Capability 是什么」「为什么不勾其他」「Push Notifications 为什么不勾」。itsuki 当下纠正「我需要你的解释，我需要你教我，我现在边做边学习，你不能偷懒」CC 才补讲。
  - **写法**：仿照 `.claude/skills/session-wrap/` / `.claude/skills/version-bump/` 结构
  - **验收**：下次 itsuki 第一次接触 SSH / Caddy / Docker 这类工具时，CC 主动解释（不等 itsuki 催）

---

## 📄 文件格式：MD → HTML 改造候选清单（2026-05-11 拍板分层）

> **背景**：2026-05-11 itsuki 读了 Thariq Shihipar（Anthropic）的「Why HTML」文章 → 讨论后拍板**混层方案**：CC 工具链主导的文件（启动 parse / hook grep / sync 规则 / git diff review）保 MD；**人是最终读者**（教授 / 招生官 / 老师 / 宿舍管理员）的文件候选 HTML。已有 `00_admin/术语表.html`（5-11 首个 HTML 文件）作为试水。
>
> **方针 — 不强制双写**：保持 MD 单源真值（DMSD 整套 sync 机制依赖 MD）。itsuki 自己偶尔需要看某个 MD 的 HTML 版时**让 CC 临时 pandoc 渲染**，永不入 git：
>
> ```bash
> pandoc <MD_PATH> -o /tmp/$(basename <MD_PATH> .md).html -s --metadata title="<标题>"
> open /tmp/$(basename <MD_PATH> .md).html
> ```
>
> **走真改造（纯 HTML 或双写）的门槛**：3 条全满足 — (1) 教授 / 招生官 / 老师是主要读者，**不是** CC 协作内部；(2) HTML 表达力真比 MD 强很多（SVG / 倒计时 / 时间轴 / 交互）；(3) 改频率低（一旦改了能容忍同步成本）。

### A. 元任务（先做这条再考虑下面）

- [ ] **itsuki 查看已有的 HTML skill** — itsuki 说「我有 HTML skill」。先确认这个 skill 干什么 / 跟 Anthropic 官方 `frontend-design` skill 关系 / 是否能直接复用做下面的改造 / 是否需要写新 skill。决定后再启动下面的改造任务。

### B. 候选 HTML 改造文件（**未启动 — 等 §A 元任务做完再 review**，B-009 修）

> 2026-05-21 注：候选清单 13+ 文件,但 §A 元任务（itsuki 查 HTML skill）未做完前不启动任何改造。低优项不主动催。

**高优 — AC 出愿强相关**：

- [ ] `00_admin/v0.3.0_AC叙事.md` ~ `v0.8.0_AC叙事.md` 7 个 — 教授 / 招生官读项目演化主线
- [ ] `00_admin/原创设计_语音播报防作弊.md` — ⭐ AC 最强素材之一，自动贩卖机灵感→代刷观察→工程方案完整链
- [ ] `00_admin/AC_志望動機_素材.md` — Q1-Q8 留白等 itsuki 自填，HTML 可做填空交互式编辑
- [ ] `00_admin/AC_提交_checklist.md` — 5-10 月 6 个 gate 倒计时 + 月度 review，HTML 强（倒计时 + 进度条）
- [ ] `00_admin/面试准备_索引.md` — 6 大类 42+ 题，HTML 可做交互式题库
- [ ] `05_logs/decision_log.md` — 6 条版本级决策，HTML 强（时间轴 + 决策卡片）
- [ ] `05_logs/learning_path.md` — 学习路径，HTML 强（知识树）
- [ ] `05_logs/project_evolution.md` — 4 次重大转折，HTML 强（折线图）
- [ ] `05_logs/problem_solving/` 4 文件 — 现象→假设→验证→结论结构化展示

**中优 — 设计可视化 / 老师面试展示**：

- [ ] `02_design/hardware_design.md` — Pi 3A+ 选型 + GPIO 接线 + BOM，HTML 强（SVG 接线图 + 模块比较表）
- [ ] `02_design/flow_design.md` — 路径 A 卡 / 路径 B iOS / Android 流程，HTML 强（SVG 序列图）

**低优 — 对外公开页 / 双向边缘**：

- [ ] `README.md` — GitHub 公开页（GitHub MD 渲染已不错），可选单独做 `index.html` 给招生官
- [ ] `CHANGELOG.md` — 18 tag 时间轴可视化（CC 仍 parse MD 单源）

### C. 已是 HTML 文件清单

- `00_admin/术语表.html`（2026-05-11 建）— 180+ 词 AC 面试术语学习工具（主动回忆 + 间隔重复 + localStorage 进度）

### D. 反向规则 — 永不 HTML 化（CC 工具链强制 MD）

- `CLAUDE.md` / `WIP.md` / `TODO.md` / `文档同步点清单.md` / `.claude/skills/project-overview/SKILL.md` — CC 启动 parse + 维护 grep
- 5 端 `*_DESIGN_LOG.md` + `system_features.md` + `01_specs/` 字典 — CC sync 主导（hook + sync-rules.sh 依赖 MD grep）
- `05_logs/raw/` 全部 — git diff review 主导，HTML diff 噪音爆炸（Thariq 自己承认是最大缺点）
- `00_admin/hooks/` + `.claude/skills/` — 脚本 + skill 定义，跟 HTML 无关
- `memory/`（`~/.claude/...`）— CC 自己读
- `99_archive/` — 归档参考，不主动读

---

## 🛣️ 推进路线图 — 38 条三轨并行（2026-04-30 启动）

> **背景**: v0.6.0 close（4-29 晚）已铺设计层骨架 — `02_design/system_features.md §7` 14 子节覆盖 38 条 + R1-R4 硬约束锁定 + 12 Q 全答。下一步 = **3 轨并行**推到「代码 agent 可接手」状态。 <!-- VERSION_OK -->
>
> **多会话认领** 见 `00_admin/WIP.md §🔄 进行中的任务`。

### 三轨分工

| 轨道 | 内容 | 主写文件 | 估时 |
|---|---|---|---|
| **A · 状态盘点** | 38 条逐条对照设计文档 → 标 ✅⏳🔧 + 覆盖度 baseline | `00_admin/TODO.md` 顶部 38 条 | 1 会话 |
| **B · §9 + Q12 拍板** | 8 条待拍板事项 + Q12 矛盾 → itsuki 拍板 → 落地 | `02_design/system_features.md §9` + 拍板结论落地 §3/§6/§7 | 1 会话 |
| **C · 实装包拆分** | P0 核心模块需求 brief，给 code agent 用 | `03_dev/{backend,teacher_web,student_ios}/REQUIREMENTS.md`（新建）| 2-3 会话 |

### 文件边界（避免多会话撞）

- A 写 `TODO.md` 38 条状态 / B 写 `system_features.md §9` / C 新建 `03_dev/*/REQUIREMENTS.md`
- 三方都**只读**对方主写文件 → 互不冲突
- 例外 1: B 拍板后产生新事实 → A 会话**回头**把对应条 ⏳ 改成 ✅（依赖，不是并行冲突）
- 例外 2: C 起草中发现 §7 子节设计缺口 → 同会话补 §7（B 只动 §9，§7 子节是 C 的可写区）

### C 内部优先级

- **P0 核心**: 出寮届提交（#1-9 · 学生 iOS）+ 点呼/学習（#14-20 · iPad Web）
- **P1 闭环**: 役職承認（#10-13）+ 出寮者一覧（#22-27）
- **P2 后台**: 寮務部教師（#28-33）+ 食堂 Excel（#7）
- **P3 支线**: 巴士+行事 master 编辑（#8 #9 #11 #12）+ 音楽リクエスト（#37）

### 完成定义

3 轨全 done = 38 条状态层「设计 ✅ + 实装 brief 就位」→ 启动 **v0.7.0** 实装会话（code agent 接手）。

### 📦 轨道 C 完成后的 evidence 待补 + 实装阻塞（2026-04-30）

> **轨道 C close 状态**: P0 实装 brief 全部落地（backend `BACKEND_DESIGN_LOG.md` 新建 + iOS / Web `_DESIGN_LOG.md` §11 实装清单 append）。**当日决策**: D1 SendGrid / D4 实物表为准 / D5+I6+D10 注册即用 / W1 TS+Vite 升级 / D2-D9 + I1-I8 + W2-W8 一次过 / D11 单独表 / D12 ENUM 加管理係 — **全 25+ 条决策清完**。

**残 evidence 待 itsuki 补**：

- [ ] **帰省 实物表照片** ×2（一般学生 / 留学生）— 下次见老师拿原表拍 → backend D4 「帰省 chain」从 ⏳ 暫定 → ✅
- [ ] **帰国 实物表照片** ×2（一般学生 / 留学生）— 同上 → backend D4 「帰国 chain」从 ⏳ 暫定 → ✅
- [ ] **担任 名簿 seed 数据**（哪个老师担任哪个学年 × 組）— v1.0 上线前 itsuki 跟老师确认 → `class_teacher_assignment` 表初期データ导入

**外泊届 chain 已 ✅**（2026-04-30 实物表 evidence 入手）— code agent 实装这部分不被这件事阻塞。

**code agent 接手时不被阻塞的模块**: 学生注册 / login / 学習出席 / 点呼 / 邮件通知 framework / 数据库 schema / 全部 API endpoints。
**唯一被阻塞的**: 帰省・帰国届の承认 chain 生成函数（外泊已可写、帰省・帰国は実物表 evidence 入るまで暫定で実装可、入った時点で chain 設定値だけ調整）。

---

## 🎯 4-28 demo 后老师反馈 backlog（2026-04-29 受领，最高优先级）

> **背景**: 4-28 demo 给老师看后，4-29 老师通过 LINE 发来完整需求清单（5 大角色 + 订正 + itsuki 补足 = 38 条）。
>
> **必读硬约束 4 条** — 与现有设计直接冲突 / UX 根本约束:
> - **R1**: 通知 = 邮件固定（push 不可。理由 = "残る"）
> - **R2**: 老龄寮監 UX = 不能条件分歧、一本道操作
> - **R3**: 教师每人单独账号密码
> - **R4**: 1・2 寮 / 4 寮 分别显示

### 📊 设计层覆盖度 baseline（轨道 A 盘点 · 2026-04-30 · ✅ B 标准 itsuki 拍板版）

> ⚠️ **数字 = 设计层 4-30 baseline**（B-010 修 2026-05-21）；实装层进度（5-04 起 backend / iOS / Android 大批落地）看 §F 状态汇总 + `00_admin/progress_overview.md §阶段 6/7`。下方 ✅/⏳/❌/🚫 数字未刷新（5-08 起后端 routers + iOS Foundation + Android 22 屏 实装让 ✅ 实际更多）。
>
> ⚠️ **历史**: 4-30 第一版 baseline 用了 CC 自定义的宽松标准（"列入 system_features.md = ✅"）→ ✅ 34/39。**itsuki 4-30 指出"什么时候完成了这些设计? 自作主张"** → 撤销旧版 → 拍板用下面的 **B 标准**重做(本节)。
>
> **38 条对照源**: `02_design/system_features.md §7` 14 子节 + `01_specs/rollcall/RollCall_Spec.md §5-§10` + `03_dev/student_ios/IOS_DESIGN_LOG.md` + `03_dev/teacher_web/WEB_DESIGN_LOG.md` + round3 demo 实装

#### ✅ 标准定义（B 标准 · 大白话）

| 标 | 中文含义 | 必须满足条件 |
|---|---|---|
| **✅ 设计完成** | "code agent(写代码的 AI)拿到这条就能直接动手" | UI 画过(iPhone 屏幕 / Web 页面图能看到) **+** 字段都列了(每个 input / 表 column 名+类型) **+** API 形状定了(请求 URL+参数+返回结构) — **3 项全满足** |
| **⏳ 设计部分** | "有进度但还差几样" | 3 项中有 1-2 项 ok(比如字段定了但 UI 没画 / 或 UI 占位但 API 没写)|
| **❌ 几乎没碰** | "只有名字 / 完全没碰" | 3 项一个都没满足(只有"提到这功能存在")|
| **🚫 已砍** | "决定不做" | itsuki 4-29 拍板砍 |

> **备注**: checkbox `- [ ]` = 实装层(代码层) / emoji 前缀 = 设计层。代码全 0% → 实装层全部 `[ ]`。

#### 数字（B 标准）

| 标 | 数量 | 编号 |
|---|---|---|
| **✅ 设计完成** | **7 / 39** | #16, #17, #18, #19, #20, #37, #38 |
| **⏳ 设计部分** | **27 / 39** | #1-#15(除 #16-#20 外的 #1-#15)+ #22-#27 + #29 + #31-#34 + #39 |
| **❌ 几乎没碰** | **3 / 39** | #21, #28, #30 |
| **🚫 已砍** | **2 / 39** | #35, #36 |
| **🔧 待实装** | 37 / 39 | 除已砍外全部 → 轨道 C 起草需求 brief |

#### ✅ 7 条详情(为什么算 ✅ — 3 项都满足)

| # | 条目 | UI(画过)| 字段(列了)| API(定了)| Demo |
|---|---|---|---|---|---|
| **#16** | 当天夜点呼出席者列表 | iPad live-roll-call.jsx | rollcall_session + rollcall_event 字段表 | RollCall_Spec.md §6 派生算法(组+时间窗) | round3 demo |
| **#17** | 数夜点呼出席人数 + 保存时刻名字 | 同上 | rollcall_event append-only 表 | POST /checkin | round3 demo |
| **#18** | 当天朝点呼出席者列表 | 同上 | 同 #16 | 同 #16 | round3 demo |
| **#19** | 数朝点呼出席人数 + 保存 | 同上 | 同 #17 | 同 #17 | round3 demo |
| **#20** | 自动判定迟到 / 缺席(后续可手动改)| live-roll-call.jsx 黄色高亮 | RollCall §5.4-5.5 时刻表 + §7 判定逻辑 | PATCH /checkins/:id | round3 demo |
| **#37** | 音乐 リクエスト(请求)曲管理 | round3 demo Web (男女寮 tab + 提交順 + 承认/拒否)| songs 表(待写但概念清晰)| GET /songs?dorm= + PATCH /songs/:id/state | round3 demo |
| **#38** | 食事 from/to(从几号到几号不要餐)明确 | round3 demo Web 修订 | system_features §7.2.1 字段表标了 from/to | apply 表 meals_skip_from / meals_skip_to | round3 demo |

#### ❌ 3 条详情(几乎没碰 — 大白话讲清楚)

| # | 条目 | 现状(讲人话)| 缺什么 |
|---|---|---|---|
| **#21** | 老龄(年纪大的)寮監 UX 一本道(线性流程不分岔) | 4-29 我们一起定了 R2(Rule 2 = 第 2 条硬约束)规则:**"老师年纪大,iPad 操作要简单不分岔"**。**但 iPad 上具体每个页面长什么样、按钮放哪、和现在 demo 比要砍哪些选择项 — 全是空白** | iPad 老师页面所有 UI |
| **#28** | 寮务管理员追加 / 删除 学生 | system_features.md §7.1(账号那一节)只列了"学生自己注册",**没有"管理员代录入新生 / 学生离寮删除"这一行** — 整个功能没写 | UI + 字段 + API 全空 |
| **#30** | 教师当天代录出寮届 | §7.2 #3(出寮届那一节)提了"教师当天录入是例外",**但具体录入界面长什么样、谁能录、和学生本人提交差在哪 — 没写** | 教师代录 UI + 是否需另一签批 |

#### 🔍 设计权威源速查(每条编号对应文档位置)

| # 编号 | 主题(中文)| 设计权威 |
|---|---|---|
| #1-#13 | 出寮届(申请书)提交 + 役职(职务)承认 | `system_features.md §7.2` |
| #7 | 食堂食数 Excel 导出 | `§7.2 #7` + `§7.7` |
| #8, #11 | 巴士特别便(寮特殊巴士)| `§7.6` |
| #9, #12 | 行事予定(学校日程表)| `§7.5` |
| #14, #15, #20(学習部分)| 学習(晚自习)| `§7.3` |
| #16-#19, #20(点呼部分)| 点呼(朝/夜)| `§7.4` + `RollCall_Spec.md §5.6 §6 §7 §8 §10.2` |
| #21 | 老龄一本道(线性流程不分岔)UX | `§2 R2`(只锁定原则)/ ❌ iPad 具体 UI 全空 |
| #22-#27 | 出寮者一覧(出门学生列表)● 事務室 PC | `§7.8` + `§2 R4` |
| #28 | 寮务追加 / 删除学生 | ❌ 缺(`§7.1` 仅自助注册)|
| #29 | 学習对象寮生(被列入晚自习名单的学生)| `§7.3`(中学全员 / 高中手动名单)|
| #30 | 教师当天代录 | `§7.2 #3` 仅原则 / ❌ 具体 UI 未详 |
| #31, #33 | 学生指导履历 / 事案(事件)录入 | `§7.9` |
| #32 | 学生个人数据 aggregated(汇总)view | `§7.10` |
| #34 / R1 | 通知=邮件固定(R1 = Rule 1 = 第 1 条硬约束)| `§2 R1` + `§7.13` |
| #35, #36 | 学生发帖+社区+匿名建议 | `§7.14` 砍 |
| #37 | 音乐 リクエスト(请求)曲 | `§7.11` |
| #38 | 食事 from/to(从几号到几号不要餐)明确 | `§7.2.1` |
| #39 / R3 | 教师每人单独账号(R3 = Rule 3 = 第 3 条硬约束)| `§2 R3` + `§7.1` |

> **术语小词典**(给 itsuki 复习用):
> - **R1-R4** = 我们 4-29 拍板的 4 条硬约束(R = Rule 规则)。R1=邮件通知 / R2=老龄一本道 / R3=教师单独账号 / R4=1·2 寮和 4 寮分别表示
> - **Q1-Q12** = 我们 4-29 列给老师的 12 个阻塞问题(Q = Question)。已答 11 个 / Q12 矛盾保留
> - **#1-#39** = 老师 4-29 LINE 给的 38 条要件(#34 之后 4 条砍/留是 itsuki 补足,所以总共 39 行)
> - **D / V1 / V1.1+** = Demo (4-28) / v1.0 上线版 / 未来扩展
> - **system_features.md** = 整个系统的功能清单(iOS + Web + 后端 共用真值)
> - **RollCall_Spec.md** = 点呼(roll call)的详细规格

---

### 〇 学生用 出寮届提交

- [ ] **⏳ 1.** 学生只能提交自己的届，不能代别人填
- [ ] **⏳ 2.** 三种届的字段
  - 帰省: 出寮日 / 帰省方法 / 出寮时刻 / 帰寮日 / 帰寮方法 / 帰寮时刻
  - 外泊: 帰省字段 + 外泊地点（可多个）+ 不要食事的时间段
  - 帰国: 外泊字段 + 出发机场 / 起飞时刻 / 到达机场 / 到达时刻
- [ ] **⏳ 3.** 出寮日只能选明天以后（不能选今天）
- [ ] **⏳ 4.** 不需要填的字段不显示（动态非表示）
- [ ] **⏳ 5.** 提交后给提交者展示承认状态:
  - 帰省: 寮務部長 + 寮務課長 承认
  - 外泊: 上面两个 +（留学生）国際交流部長 + 国際交流課長
  - 帰国: 同外泊
- [ ] **⏳ 6.** 提交时给上述役职发**邮件**通知（订正后 = 邮件固定，→ R1）
- [ ] **⏳ 7.** 给食堂员工通知食数（从食事不要时间段算每天朝/昼/夕份数 → Google Sheets，不需共享）
- [ ] **⏳ 8.** 显示寮生特别运航便一覧（选帰省方法时能从列表里选更好。**杭田未实装**）
- [ ] **⏳ 9.** 显示行事予定

### 〇 役职 出寮届承认

- [ ] **⏳ 10.** 看出寮届，给许可/不许可
- [ ] **⏳ 11.** 寮生特别运航便的录入 + 编辑
- [ ] **⏳ 12.** 行事予定表的修改（编辑）
- [ ] **⏳ 13.** 给出寮届提交者发评论（**杭田这个功能弱**）

### ★ 寮監・学习担当 点呼/学习用（iPad）

- [ ] **⏳ 14.** 当天夜学习出席者列表（出寮届 + 学习欠席届 + 学习对象寮生 自动算出）
- [ ] **⏳ 15.** 数夜学习出席人数，保存时刻和名字
- [ ] **✅ 16.** 当天夜点呼出席者列表（从出寮届算）
- [ ] **✅ 17.** 数夜点呼出席人数，保存时刻和名字
- [ ] **✅ 18.** 当天朝点呼出席者列表
- [ ] **✅ 19.** 数朝点呼出席人数，保存时刻和名字
- [ ] **✅ 20.** 根据时刻判断学习・朝点呼・夜点呼的迟到/缺席（之后可手动改）
- [ ] **❌ 21.** 老龄寮監 UX 极限简化（→ R2）

### ● 寮監确认用 出寮者一覧（事务室 PC）

- [ ] **⏳ 22.** 在事务室 PC 上看
- [ ] **⏳ 23.** 能打印
- [ ] **⏳ 24.** 不能编辑（防误删）
- [ ] **⏳ 25.** 1・2 寮 和 4 寮 分开显示（→ R4）
- [ ] **⏳ 26.** 出寮届录入后 1 小时内反映
- [ ] **⏳ 27.** 形式 = Excel / Sheets / 独自 UI 都行

### 〇 寮務部教师确认用

- [ ] **❌ 28.** 寮生的追加 / 删除
- [ ] **⏳ 29.** 修改学习对象寮生
- [ ] **❌ 30.** 出寮届一览阅览 + 录入（教师可当天录入）
- [ ] **⏳ 31.** 学生指导历录入
- [ ] **⏳ 32.** 学生个人数据显示（出寮届履历 / 学习迟到欠席履历 / 朝点呼履历 / 夜点呼履历 / 指导履历 / 其他）
- [ ] **⏳ 33.** 事案录入（文中学生名 tap 跳转该学生数据。**杭田未实装**）

### 老师订正

- [ ] **⏳ 34.** 通知 = 邮件固定（push 不可。理由 = "残る"=会留下记录，→ R1）

### itsuki 补足（4-29 拍板砍/留 4 条）

- [ ] **🚫 35.** 学生发帖功能 + 社区功能整体 — **砍**（4-29 拍板）
- [ ] **🚫 36.** 匿名建议提交 — **砍**（4-29 拍板）
- [ ] **✅ 37.** 音乐功能 — **留**（4-29 显式保留 · 既存 round3 リクエスト曲管理ワークフロー継続）
- [ ] **✅ 38.** 外宿申请的"不要食事时间段" = from/to 明确
- [ ] **⏳ 39.** 每个老师单独账号密码（→ R3）

### 阻塞推进的 Q（要先问老师 — 12 个 · 4-29 已答 11 个）

- [x] **✅ Q1** (阻塞 #25 寮单位): 1/2/4 寮的物理关系？性别 / 栋 / 楼层？3 寮哪去了？ — **答**: 1·2 寮 = 男 / 4 寮 = 女 / 3 寮废止;物理关系 ⏳ 老师追问待
- [x] **✅ Q2** (阻塞 #14-#15 #29 学習): "学習" = 晚自习？时间？对象学年？"学习对象寮生"选定基准？ — **答**: 中学生全员自动 / 高中开学考+期末考不合格者手动 → 期末后 reset
- [x] **✅ Q3** (阻塞 #14): 学习欠席届 = 纸提交？App？提交期限？谁批？ — **答**: App 提交,19:40 学習开始前,专任老师承认
- [x] **✅ Q4** (阻塞 #39): 役职账号 = 各 1 名固定 / 多人？换人怎么交接？ — **答**: 各 1 名,退出 → 下个人登录
- [x] **✅ Q5** (阻塞 #21 #39): 寮監 = 几人？换班？iPad 共用 / 个人别登录？ — **答**: 几名未定,iPad 共用,退出登录切换
- [x] **✅ Q6** (阻塞 #22-#23): 事务室 PC 现有环境（OS / 浏览器 / 打印机）？ — **答**: 職員室 PC + 事務室 PC + 寮管室 iPad + 食堂 iPad
- [x] **✅ Q7** (阻塞 #7): 食堂 Sheets 模板 / 写入权限拿法？ — **答**: Excel 导出(不要餐食学生 + 期间)
- [x] **✅ Q8** (阻塞 #8 #11): 特别运航便 = 学校包车？master 谁管？频度？ — **答**: 学校固定便 + 寮特殊便(市内・空港),学生选
- [x] **✅ Q9** (阻塞 #12): 行事予定 = 现有 calendar？iCal/Google Calendar 连携可？ — **答**: 现有不够,要加强
- [x] **✅ Q10** (阻塞 #39): 教师密码重置怎么运营？ — **答**: 项目负责老师经手
- [x] **✅ Q11** (阻塞 #5): 留学生 flag 怎么设？数据源 = 学校 master？ — **答**: 注册时自己选
- [ ] **⚠️ Q12** (全体参考): 杭田既存 UI 能给我们看吗？ — **矛盾保留**: itsuki "没参考价值" / 老师"基本上什么都给看" → 轨道 B 拍板

---

## ✅ 2026-04-28 管理员 Demo 冲刺（已通过 — 2026-05-21 归档 / B-004 修）

**状态**：Demo 通过验证 2026-04-29（管理员当面口头同意采纳）。整段已归档,详细见 `99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/`。

- [x] ~~Amazon 日本下单 Pi 3A+ + 配件~~ — 已下单（4-22 到货）
- [x] ~~淘宝下单 ST25DV16K~~ — 已下单
- [x] ~~代码 agent 分配任务（前端 / 后端 / iOS / Pi 4 个模块）~~ — 5-02 起 5 端代码层全启动取代 demo agent 分工
- [x] ~~管理员反馈整理到 `05_logs/raw/2026-04-28.md`~~ — 4-29 raw 已记录管理员同意采纳
- [x] ~~根据反馈决定路线~~ — 4-29 拍板：推进 v1.0,系统进入实装阶段 → MEMORY.md `Key Dates` 4-29 段

---

## 📌 2026-04-29 项目审查 — 内容整理待拍板(CC agent 找的,等 itsuki 决定)

> **背景**:4-29 itsuki 让 CC 排查项目"内容重复/部分章节重复/关键事实点散到多处"。CC 派 agent 扫两遍,处理了 3 类(扣分阈值漂移/CLAUDE.md 长段硬编码/demo_4-28 路径),剩下 3 条等 itsuki 拍板。
>
> **完整 39 条 finding 清单** → CC 本地 plan 文件 `~/.claude/plans/bug-ac-parallel-pumpkin.md`(含严重度分类+验证方法+不动的边界)

- [x] ~~**CLAUDE.md vs CLAUDE_CODE_记录指南.md 完全重复 5 核心问题 + 触发清单**~~ — 2026-05-04 闭合：彻底重构方案 — `CLAUDE_CODE_记录指南.md` git rm，整体迁入 `.claude/skills/ac-record/SKILL.md`（v4 + 我自主修订 7 项）。CLAUDE.md 只保留 5 条硬底线 + 触发关键词指针。

- [ ] **DESIGN_BRIEF.md vs WEB_DESIGN_LOG.md(`03_dev/teacher_web/` 内)Round 历史 + 颜色 tokens 重复**
  - 现状:DESIGN_BRIEF 是"当前设计快照",WEB_DESIGN_LOG 是"完整设计 log"。但 DESIGN_BRIEF 里的颜色值和 Round 1-3 时间线在 LOG 也写了一遍
  - 选项 a:DESIGN_BRIEF 关于颜色/Round 历史的段改为 "见 WEB_DESIGN_LOG.md §3/§1 时间线" 指针
  - 选项 b:保留分散(DESIGN_BRIEF 简版给新人快速 onboard,LOG 是详档)

- [ ] **`Batch3_itsuki手笔素材指引.md` 5 块 draft 90% 没粘进对应文件**
  - 内容:4-20 CC 起草 5 块给 itsuki 复制粘贴用的 draft:
    - decision_log 新增 9 条决策
    - project_evolution 5 次转折
    - learning_path Python Day 2 主动延后坦诚
    - learning_path PostgreSQL 选型理由
  - 现状:4-29 检查发现 90% 还没粘到 `05_logs/decision_log.md` / `project_evolution.md` / `learning_path.md`
  - 选项 a:itsuki 抽 30-45 分钟把 draft 粘进对应文件 → 粘完后删 Batch3
  - 选项 b:决定不补了 → 直接归档 Batch3 到 99_archive/
  - 选项 c:暂搁置 → Batch3 继续放着等以后

- [x] ~~**CLAUDE.md 4-step vs IOS_DESIGN_LOG 5-step 矛盾(同时存在)**~~ ✅ **2026-05-26 闭合 — 选 a（5 步是真值）**
  - **真值证据（iOS 代码）**：`03_dev/student_ios/v1/TomoshibiApp/Features/Auth/AuthStubs.swift` line 478 注释「注册进度 · 5 步（Step5 = 认证代码，5-04 加 RegisterStep5 时把硬编码 4 改成 5）」+ 5 个 `RegisterStepN.swift` view 完整存在 + `Foundation/Routing/Route.swift` line 79-84 定义 `registerStep1`~`registerStep5` + `registerDone`
  - **矛盾已自动消失**：2026-05-26 commit `d608846` CLAUDE.md 重写到 QTS 模式时砍掉所有注册流程具体描述段，grep「4-step / 5-step / 多步注册 / 注册.*步」全空
  - **不需要回滚 IOS_DESIGN_LOG §3.9.2**：跟代码一致
  - **不需要回写 CLAUDE.md「5-step」描述**：QTS 模式后 CLAUDE.md 不放这种实装细节，由 IOS_DESIGN_LOG §3.9 单独权威

---

## 📋 旧审查 backlog + 5-01 全文件审查 未结余项（2026-05-04 收敛 — 单源真值）

> **背景**：4-19 项目审查 87 条 + 5-01 全 repo 文件状态评审 = 两次大盘点。**5-04 itsuki 拍板：以后不再分散文档**，未做事项一律写在本 section。
>
> **历史快照（不再单独维护，仅作证据链）**：
> - `00_admin/2026-04-19_项目审查_backlog.md` — 完整 87 条 + 已闭合证据链
> - `00_admin/漏洞_剩余清单_2026-04-21.md` — 4-21 中间精简版
> - `00_admin/项目文件总览.md`（原 `2026-05-01_全文件审查.md` 5-04 改名升级为系统级单源真值）— 606 文件逐个状态 + AC top 10。**新会话首选入口**
>
> **图例**：D = 文档一致性 / S = spec 内部漏洞 / A = AC 视角 / T = 技术债 / L = 小细节 / M = meta
> **标号沿用 backlog 原 ID**（D1-D30 / S1-S20 / A1-A13 / T1-T13 / L1-L11 / M1-M2）方便溯源。

### A. itsuki 自己粘 / 自己改 / 自己拍板（CC 不能代做）

#### A.1 一次性粘贴 11 条历史欠债（30-60 分钟，性价比最高）

把 4-20 起就准备好的 4 份草稿粘到长期记录文件里（CC 永不直写 decision_log / project_evolution / learning_path 正文）：

- [ ] 一次性合并 Batch3 + progress_overview_draft
  - 把 `00_admin/Batch3_itsuki手笔素材指引.md` 4 段草稿粘到 `05_logs/decision_log.md` / `05_logs/project_evolution.md` / `05_logs/learning_path.md`
  - 把 `00_admin/progress_overview_draft_2026-04-20.md` 整体替换 `00_admin/progress_overview.md`

闭合：D1（project_evolution 4-13 后停滞 / 遗漏 5 次重大转折）/ D2（decision_log 9 条决策没进）/ D3（learning_path Python Day 2 状态过期 41 天）/ D4（PostgreSQL 选型理由 `(未想好)` 占位符）/ D7（progress §阶段 0.6 4-13 停）/ D8（技术学习时间线缺 4-15/4-17/4-19/4-20 6 条）/ D9（关键决策索引缺 10 条）/ D10（问题解决索引缺 4 条）/ D11（占位符数字 4 vs 5 不一致）/ D12（仓库结构地图含已归档的 executable_dev_checklist）/ D13（progress 和 CLAUDE.md 目录结构不同步）

#### A.2 itsuki 手改正文 5 条（CC 永不直写）

- [ ] **D5** `project_evolution.md` 起点章节有死引用 — 路径 `ac_入試准备/项目起源_真实观察.md` 是 iCloud 迁移前的旧路径
- [ ] **D6** `project_evolution.md` "现在的状态(4-13)" 记录体系数字全过期（dev_log 写 2 实际 8 / problem_solving 写 1 实际 4 / decision_log 写 5 实际 7+ / raw 写 3 实际 5+）
- [ ] **D28** `project_evolution.md` 起点章节（2-12 冻结）只说"为什么冻结"，没有第二次转折（4-10 回归日）那种三层分析。AC 视角：起点反而该最完整
- [ ] **D29** `decision_log.md` 6 处"事后回看（几个月后补填）"占位符全空 — 是 AC #4 自己認識的黄金素材
- [ ] **D30** `dev_log/2026-04-10_回归日.md` 占位符数字 — Explore 数 5 / TODO 数 4，off-by-one

#### A.3 业务 / 技术拍板 5 条（不定就堵着）

- [ ] **S5（颜色区分）🔴**：`exempt_range`（免点呼）颜色 = 绿色 = 跟 `present`（准时）一样，UI 上无法视觉区分。加 icon / 边框 / 文字 / 叠加符号 哪个？
- [ ] **S6（追溯申请）🔴**：spec §11.3 改判 >30 天 "走「追溯申请」独立流程（v0.3 设计）" — 但 v0.3 已发布"独立流程"没设计。选 A：v0.4 单独设计 §11.5 / 选 B：spec 改"追溯申请推迟到 v0.5，v0.4 只处理 ≤30 天"
- [ ] **S8（X 分钟）🟡**：spec §5.3 `auto_end_at = on_time_end + X 分钟`，X 待定（候选 3 / 5 / 10 / 15 / 30）。阻塞结算代码
- [ ] **S17（overlay 元数据）🟡**：overlay 分两类（纯装饰型 vs 改底色型）目前只在 ENUM §4 + spec §2.2 文字描述。改 ENUM 加 `overlay_type` 字段 还是保持文字够用？v0.7.0 UI 开工前评估
- [ ] **L8（URL 命名）🟢**：`API_CONVENTIONS.md §8` 已列 3 方案对比，待拍板：A `/api/v1/student/...`（RESTful + 版本 + 角色）/ B `/student/...` + Header / C `/api/v1/...`（角色靠 token）。拍板后连改 spec §5.1 + §2

#### A.4 24 个看不懂的文件 = 删 / 留 拍板（节省约 13 MB）

- [ ] `01_specs/*.pages` 4 个：`API_Contract_v0.1` / `IA_UI_v0.1` / `Overview_of_Features_v0.1` / `rollcall/DMSDv0.1验收脚本` — `.md` 替代品都已建（**T1**）
- [ ] `01_specs/rollcall/RollCall_Spec_v0.1.pages` 1 个 — 已被 `RollCall_Spec.md` 取代
- [ ] `99_archive/01_specs_Overview_原稿/` 下 2 个 .docx — 都已被 .md 取代
- [ ] `99_archive/` 根 5 个 .pages（learning_process / progress_log × 2 / 需要学习 / Folder_Structure_Overview）— 都已被 .md 抢救
- [ ] `99_archive/` 根 14 个 `.510Z` 早期 GPT 对话 PDF dump — 已整理到 `raw/2025-12_NFC系统早期设计对话.md`（**T11**）
- [ ] `99_archive/NFC_NFD_鬼影文件/` 5 个副本 — 问题已解决可删 / 保留则 README 补 1 句（**L4**）

#### A.5 v1.0 上线前必做（不能跳）

- [ ] **`06_assets/real_samples/bus_notice_2026-03-22_特別運行便.md` 学生实名脱敏** — GitHub 现在公开 + 含真名
- [x] ~~**iOS 3 个空壳 view 决定命运**：`Schedule` / `StayList` / `BusList`~~ ✅ 2026-05-25 Bot 1 复查会话验证：3 个 view 都不是空壳，全在用。`ScheduleView` 是行事予定月历（`SEED.events`）/ `BusListView` 是寮生特别便一覧（HomeStubs `.busList` 跳转目标）/ `StayListView` 5-21 A-037 改成调真后端 `ApplicationsAPI.listMine()`。TODO 原描述「已并入 Home / Apply / Community Bus card」过期。
- [ ] **`00_admin/AC_志望動機_素材.md` Q1-Q8 itsuki 自己起草**（185 行框架 17 个小节占位 / 内容待填 — AC 5 核心问题 #5 志望動機，repo 内最大空白）

### B. CC 可独立做（每条 < 30 分钟，下次开会话「做 B 类」即可）

- [x] ~~改名 `03_dev/student_ios/DESIGN_BRIEF.md` → `_archived_DESIGN_BRIEF_Round1_context.md`（IOS_DESIGN_LOG 已全覆盖）~~ ✅ **2026-05-26 闭合** — 2026-05-13 commit `81842f4`「整理 14 文件 — 管理文档归位 + 老文件归档 + iOS 改名」已完成，归档文件存在 `03_dev/student_ios/_archived_DESIGN_BRIEF_Round1_context.md`
- [x] ~~改名 `03_dev/student_ios/demo/Round2_Prompt_C3.md` → `_archived_Round2_Prompt_draft.md`（C3 已 resolve）~~ ✅ **2026-05-26 闭合** — 同上 commit `81842f4` 已完成，归档文件存在 `03_dev/student_ios/demo/_archived_Round2_Prompt_draft.md`
- [x] ~~删 `99_archive/2026-04-15_old_demo/.DS_Store`（误进 git）~~ ✅ **2026-05-27 删**（不在 git track 范围 — 物理 rm 即可）
- [x] ~~删 3 个已过期的 admin 文件：~~ ✅ **2026-05-27 闭合** — 3 文件均已被挪到 `99_archive/2026-05-12_深夜大整理/`（commit history 可查）：
  - `00_admin/v0.4.0_S系列spec漏洞优先级分析.md`（已被「漏洞_剩余清单」吸收）
  - `00_admin/T2_iOS归档_dryrun评估.md`（已执行）
  - `00_admin/跨会话_ios_共享决策.md`（iOS 工程已独立 repo）
- [ ] backend `03_dev/backend/v1/app/models.py` 13 张表 docstring 各标 P0 / P1 / P2 — **2026-05-27 复核**：当前表数已从 13 → 21（5-22 加 demerit/cleaning/front_desk + 5-03 加 announcement/announcement_reads/announcement_replies/student_registration_codes + 5-08 加 teacher_invitations），P0/P1/P2 分级标准也没拍板 → 挂起等 itsuki 决定分级口径再做
- [x] ~~更新 `99_archive/README.md` 时间戳 + 鬼影文件解决说明~~ ✅ **2026-05-27 闭合** — 时间戳改到 2026-05-27，加 14 个新子目录说明 + 鬼影文件已 4-10 解决证据链
<!-- 2026-05-21 Fix-Bot 3 删: 「更新 00_admin/文件结构指南.md」— 该文件已 5-04 归档,被 `.claude/skills/project-overview/SKILL.md` 取代,无需再补 v0.6/v0.7/v0.8 AC 叙事 (project-overview skill 已覆盖) -->
- [x] ~~**S18（低价值）**：`DEVICE_REGISTRY §6` 候选位置 `dorm-A-01 / dorm-B-01` 跟 `path_type` A/B 撞字 — 改成 `dorm-1-01 / dorm-2-01`。真部署 4 台时顺手做也行~~ ✅ **2026-05-27 闭合** — `DEVICE_REGISTRY.md §6` 已是 `dorm-1-01 / dorm-2-01 / dorm-4-01`，2026-05-21 B-031 commit 已落地（line 90 有「**2026-05-21 修订（B-031 修复）**：候选码改为按寮号编号」证据）
- [ ] **后端补漏**：`routers/applications.py` 加 `POST /{id}/approvals`（役职审批 #10-#13）+ `DELETE /{id}`（D3 撤回）+ `services/email.py` 补 retry 3 次循环
- [x] ~~**N18 暗色模式实装 待拍板**~~ ✅ 2026-05-25 itsuki 拍板 B：v1.0 不做 / v2 再做。`IOS_DESIGN_LOG.md §6.5` + §8.2 N18 行已更新。`TomoshibiApp.swift:22 .preferredColorScheme(.light)` 保留作 v1.0 强制 light 防黑闪。
- [ ] **5-04 iOS bug 修复联动残留**：
  - [x] ~~（1）pbxproj 备份 `/tmp/pbxproj_backup_before_icon_move` 验证后清理~~ ✅ **2026-05-26 闭合** — macOS 重启自动清空 `/tmp`，文件已不存在
  - [ ] （2）启动 git status 残留垃圾（`.bak` × 2 / `Root/File.txt`）等 itsuki 拍板删
  - [x] ~~（3）iOS sync 脚本本机不通（找不到 `~/dev/TomoshibiiOSApp`）— 是否 clone 独立 repo / 或改脚本路径~~ ✅ **2026-05-26 闭合** — 2026-05-06 退役独立 repo 模式，`sync-ios-refs.sh` 已归档到 `99_archive/2026-05-06_cloud_agent_退役/`，独立 repo 目录 `~/dev/TomoshibiiOSApp` 不再需要

### C. AC 提交前长期任务（4 条）

- [ ] **A7** `05_logs/learning_path.md` P0-P2 学习路线图 itsuki 自己用自己的话重写（不是 AI 协助整理 — 教授会问"为什么这样分级"）
- [ ] **A8** `05_logs/decision_log.md` 每条加"AI 参与 vs itsuki 拍板"标签（教授会问"这是你的想法还是 AI 的"）
- [ ] **A10** `05_logs/raw/2026-04-17.md` 775 行提炼成 200 行 `dev_log/2026-04-17_spec大审查.md` 成品版（教授不会翻 775 行）
- [ ] **L5** `01_specs/rollcall/RollCall_Spec.md` 1009 行拆主体 + 附录两份（接近 Markdown 单文件可读上限）

### D. CC 不可写（外部，itsuki 自己改）

- [ ] **M2** iCloud `00_通用指南/版本管理实践指南.md` §5 / §7 / §12 更新 — CC 无 iCloud 写权限。要改：§12 规划表过期（实际 0.2 字典 / 0.3 spec rewrite，跟指南写的不一样）/ §5 补"0.x 阶段 spec 实质变动可触发 minor bump"/ §7 补"版本号前缀式 vs Conventional Commits 何时用哪种"

### E. 接受现状不修（记录在此防再被提）

- ⚪ **L2** CHANGELOG v0.1.1 列 7 个裸 commit hash — rebase / squash 会失效但不 rebase 就 OK
- ⚪ **L3** commit `8706fed refactor:` 标签语义错（应是 chore/docs）— 改需 rebase 不建议
- ⚪ **L4** `99_archive/NFC_NFD_鬼影文件/` 日文方引号 + 副本后缀 — 不动，这堆文件本身就是 2026-04-10 跨平台 Unicode bug 的证据
- ⚪ **L7** ENUM §14 "前后端代码直接拷贝本文件取值" — 面向未来规则，等代码时引用
- ⚪ **L9** `v0.1_冻结决策.md §5` 实施要求 — 同上面向未来
- ⚪ **D27** `progress_overview` 和 `learning_path` 大段重复（Python / NFC / Git / SemVer）— 等 Batch3 粘完后看是否还需结构决策
- ⚪ **T5** GitHub Actions CI — 纯 spec 阶段不需要，v0.6.0+ 写代码后再考虑

### F. 5-04 状态汇总（已闭合 / 已推进）

**5-04 同步打勾到 backlog 4 条**（实际已在大整理 / 后端推进中完成）：
- ✅ **T2** 旧 iOS Phase 2 throwaway — 4-29 大整理已归档到 `99_archive/2026-04-29_pre_v1.0_cleanup/`
- ✅ **T7** 数据库 migration — 用 Alembic 取代手写 .sql，最新 `c3d4e5f6a7b8_add_study_absence_period.py`（5-03）
- ✅ **T12** README + LICENSE — 4-20 都建（T12 与 A1 / T6 重复条目）
- ✅ **S15** CLAUDE.md §目录结构 — M1 之后已对齐当前事实（`backend / teacher_web / student_ios`）
- ✅ **D17 / D18**（5-04 关闭）— D17 itsuki 私事不追踪 / D18 已完成归档段定位下降，CHANGELOG / git log 已是事实主线

**5-01 后大幅推进（仅记录状态，无新行动）**：
- ✅ 后端 routers P0 大批落地 — `rollcall.py` / `study.py` / `accounts.py` / `admin_registration_code.py` / `teachers.py` / `applications.py` / `auth.py` / `meals.py` / `notifications.py` 都已建
- ✅ ~~teacher_web v1 真改造已启动 — 5-01 时是 demo 100% MD5 镜像，5-02 起 TS+Vite+Zustand 已落地~~ **5-26 反转**：Vite + TS + Zustand 实装版整体废弃归档到 `99_archive/2026-05-26_teacher_web_vite实装作废/`，回归 Ryō standalone 主线（itsuki 拍板「Vite 实装版垃圾归档，用 B」— 详见 decision_log 顶部 + raw `2026-05-26_teacher_web_vite废弃+polish回滚.md`）
- ✅ iOS 三端架构成熟 — Foundation 17 文件冻结 + Auth / Home / Community 3 个 Feature 真实装 + Apply / MyPage Stubs 已存在待 v2

### 数字汇总（2026-05-04）

| 类 | 待办 | 备注 |
|---|---|---|
| A.1 一次性粘贴 | 11 条闭合 | itsuki 1 小时清完 |
| A.2 itsuki 改正文 | 5 条 | 散在 decision_log / project_evolution / dev_log |
| A.3 业务/技术拍板 | 5 条 | 5×5 分钟 |
| A.4 不可读文件去留 | 6 类约 24 文件 | 一次拍板 |
| A.5 v1.0 必做 | 3 条 | 含 AC_志望動機 itsuki 自写 |
| B CC 独立小事 | 9 条 | 总 < 4 小时 |
| C AC 长期 | 4 条 | 大改造 |
| D 外部 | 1 条 | iCloud 指南 |
| E 接受现状 | 7 条 | 不修 |
| **真实工作量** | **~25 条 itsuki + 9 条 CC** | itsuki 约 2 小时 + CC 约 4 小时 |

---

## 🚨 当前卡住的决策(必须先做,不然项目推不动)

### 硬件架构层 — 2026-05-21 大整理（B-005 修：6/8 项已拍板 → 归到「已拍板」+ 引用 hardware_design.md）

**✅ 已拍板（迁到归档段）**：

- [x] ~~**点呼机"大脑"选型**: Raspberry Pi(A) vs ESP32(B)~~ — 2026-04-15 拍板 A 方向 / 2026-04-21 拍板 Pi 3A+ 具体型号（推翻 4-20 Pi 4B 2GB），详 `02_design/hardware_design.md §2.1`
- [x] ~~**Pi 具体型号**: Zero 2 W vs 4B 2GB~~ — 2026-04-21 拍板 Pi 3A+，详 `02_design/hardware_design.md §2.1`
- [x] ~~**PN532 NFC 读头接口**: GPIO vs USB~~ — 2026-05-08 拍板 PN532 V3 模块 + SPI 推荐，详 `02_design/hardware_design.md §2.2`
- [x] ~~**LED 灯方案**~~ — 2026-05-08 拍板 LED 模块 5 色套装 ¥10.9，详 `02_design/hardware_design.md §2.4.1`
- [x] ~~**扬声器方案**~~ — 2026-05-08 拍板 01Studio USB 小音响 ¥29，详 `02_design/hardware_design.md §2.4.2`
- [x] ~~**电源与贴墙方式**~~ — 电源 2026-05-08 拍 5V 2.5A micro-USB，详 `02_design/hardware_design.md §2.6`

**仍卡住（真活）**：

- [ ] **点呼机部署数量 4 台 位置和通道分配** — 4 台已定，但**实际部署位置（4 寮哪几个入口）+ 网络通道分配待确认**。等宿舍勘察 + 跟管理员协商
- [ ] **贴墙安装方式** — 双面胶 / 螺丝 / 支架，等位置勘察才定（电源已定 micro-USB）

- [ ] **卡片形式**
  - A: 空白 NTAG215 + 贴纸打印学号/名字(¥7/张,业余但便宜)
  - B: 定制印刷卡带学校 logo(¥15-30/张,正式但贵)
  - C: 空白卡 + 只贴学号(隐私保护,但学生自己难识别)

- [ ] **UID → 学生绑定流程**
  - A: 管理员用后台系统一张张绑定(灵活,补办也用同流程)
  - B: 厂家提供 UID 清单,管理员对名单分发(快但易乱)

- [ ] **丢卡 / 补卡流程**
  - 补卡收费吗?多少?
  - 挂失到补发之间怎么点呼?(临时签?)
  - 旧 UID 如何作废?

- [ ] **点呼机外壳方案**: 3D 打印 / 亚克力盒 / 木盒 / 买现成

- [ ] **点呼流程细节**(未决完):播报内容格式("张三 准时" vs 仅姓名);失败场景的声音/灯区分;离线策略;快速重复碰卡判重;点呼窗口由谁定义;老师怎么看缺席列表(Phase 1 无学生 App)

### 现实世界调研(靠 itsuki 去问 / 去查)

- [ ] **问老师: 宿舍点呼位置的网络情况**
  - 有网口(RJ45)吗?
  - 学校 WiFi 覆盖到吗?稳定吗?
  - 能让自己的设备连校园 WiFi 吗?(有些学校限制)
  - ⚠️ 这个不问清楚,大脑选型和整个架构都定不下来

- [ ] **查 1688 / 淘宝: NTAG215 空白卡批发价**
  - 120 张的单价
  - 运费到日本多少
  - 是否能接受定制印刷(logo + 学号)

- [ ] **问学校: 有没有 makerspace / 3D 打印机**(决定外壳方案)

- [ ] **确认宿舍实际点呼流程现状**: 现在是怎么点呼的?老师怎么做?

---

## 📋 RollCall v0.1 spec 待修订事项(来自 2026-04-17 审查)

> 25 项问题(附录 A 7 项 + 附录 B 18 项),详见 `01_specs/rollcall/RollCall_Spec.md` 附录。
> 每项的完成方式:在 v0.2 spec 整理时改进文档,并对应到代码实现。

### 🔴 Phase 1 开工前必须解决(5 项)

- [ ] **B.1 代签 / 替考问题完全没防范** — NFC 卡固有弱点;spec 需明文记录"老师在场监督"作为补偿手段
- [ ] **B.2 4 台点呼机的协调没定义** — 学生属于哪台?碰错算不算?session 是 1 台一场还是 4 台同一场?
- [ ] **B.3 重复签到 / 双签的处理没定义** — 学生意外双碰怎么响应?(建议:silently ignore + 记日志)
- [ ] **B.4 未注册卡(陌生 UID)的响应没定义** — 后端错误码 + 点呼机灯/声音 + 是否记审计
- [ ] **B.5 学生 → session 的归属没定义** — session 谁创建?学生属于哪些 session?新入寮/退寮/转学怎么处理?

### 🟡 强烈建议 Phase 1 解决(6 项)

- [ ] **B.6 老师"延后按开始钮"的场景未明确** — 系统已自动开始后,老师按按钮怎么办?(建议返回 `ALREADY_RUNNING`)
- [ ] **B.7 "学生比老师先到"的 UX 没定义** — 点呼机灯/声音怎么响应 `NOT_STARTED`?需要"等待中"区分于"失败"
- [ ] **B.8 离线策略** — 点呼机断网时:拒绝 / 缓存等网恢复 / 触发降级模式?
- [ ] **B.9 改判后的纪律分扣减未闭环 + §11.3 修改时间窗** — 自动扣分联动 + 角色×时间二维矩阵(7天/30天/只读 + 月结冻结)
- [ ] **B.11 「申请审批」流程 + Phase 1 无 App 的根本问题**(2026-04-17 从 🟢 升 🟡) — 谁发起?Phase 1 没 App 怎么提交?审批时限?撤回?反馈通知?v0.2 §8.3 增补

### 🟢 后续完善(8 项)

- [ ] **B.10 "免"状态学生意外回来碰卡** — 允许签到覆盖 / 忽略 / 双状态显示?
- [ ] **B.12 `schedule_mode` 默认值未定** — 建议默认 `split`
- [ ] **B.13 节假日表的来源未定** — 建议从内閣府 CSV 自动预填,老师只补学校特殊休日
- [ ] **B.14 `health_flag` 红十字的生命周期** — 谁加?何时清?
- [ ] **B.15 `evidence` 字段的格式** — 文本 / 图片 / URL?多个证据怎么处理?
- [ ] **B.16 "本场来自点位 A 或 B" 的含义未明** — 物理位置(4 台机器) vs 路径类型(卡 / iPhone)?
- [ ] **B.17 WebSocket 协议未定义** — 消息格式 / 心跳 / 重连策略
- [ ] **B.18 幂等键未明确** — 候选:`(student_id, session_id)` / 加 `client_request_id` / 用 `card_uid + 时间桶`

### 📝 整理时发现的小问题(6 项,附录 A)

- [ ] **A.1 Phase 1(NFC 卡)vs spec 假设(手机 App 触碰)脱节** — v0.2 spec 时解决
- [ ] **A.2 早点呼祝休日足球部时间(7:20)和平日相同** — 是否手滑?待确认
- [ ] **A.3 `auto_end_at = on_time_end + X 分钟` 的 X 未定值** — 候选 5/10/15/30
- [ ] **A.4 老师"提前开始"窗口平移规则可能反直觉** — 提前按 → 准时截止也提前,是不是想要的?
- [ ] **A.5 日文打字错误(CC 已修正)** — 待 itsuki 确认 CC 修正无误
- [ ] **A.6 颜色优先级前后两套写法不一致(CC 已采用详细版)** — 待 itsuki 确认采用对了

> 注:附录 A.7 (点呼机外贴 NFC 标签描述与 4-15 设计一致) 不是问题,已 ✅。

---

## 🔴 高优先级(开发相关)

- [ ] **v1.0 产品化前：清理 Tomoshibi iOS / Web 的 demo-only 代码**（2026-04-24 itsuki 提出 / 2026-05-26 itsuki 拍板做法 B「主推进只走干净 iOS app + 备份一份单独 demo」）
  - 背景：4-28 演示用的 iOS + Web 两个前端，itsuki 决定演示通过后直接拿去产品化（不重写）
  - 但为了演示方便加了 **客户端自造状态** 的 demo 捷径，正式上线前必须删干净，否则变成安全漏洞（学生能自己伪造点呼状态）
  - iOS 进度（2026-05-26 推进）：
    - [x] ~~`Features/Home/HomeStubs.swift` 点数卡 LongPressGesture~~ ✅ 5-21（A-030 / A-033）
    - [x] ~~`AppStore.swift` `cycleDemoRollState()` + `simulateCheckin()`~~ ✅ 5-21（A-030 / A-033）。`tickCountdown()` 不算 demo（active 状态合法倒计时逻辑，生产版仍需要），保留。
    - [x] ~~A-035 注册流程 "000000" 万能验证码后门~~ ✅ 5-24 (`84e2490`)
    - [x] ~~A-038 `seedDemoAnnouncements()` 141 行公告假数据池~~ ✅ 5-21
    - [x] ~~`AppStore.swift` 5 处裸 fallback / DEMO-ONLY-SCAFFOLD~~ ✅ 5-26：`computedRoomNo` "M205" / `createAccount` 7 字段 `.isEmpty ? "新入生"/"07"/"01"/"05"/"demo1234"` / 公告 list / detail / reply 3 处 catch 分支删
    - [x] ~~AppStore.changeLog "高2→高3" seed~~ ✅ 5-26 验证已在 `#if DEMO` 包内（line 136-140），按做法 B 保留
    - [x] ~~各种 `"Demo · ..."` 前缀 toast 文案~~ ✅ 5-26 验证 4 处全在 `#if DEMO` 包内（line 395-406 `cycleDemoStudyState()`），按做法 B 保留
    - [ ] **SEED.user 硬编码 + 全 226 行假数据池整文件包 `#if DEMO`** — 5-26 评估：SEED 被 132 处代码引用（9 个 Stubs 文件 + AppStore），直接包会编译报错。要先把每个界面改成「真接后端拉数据 + loading / empty / error 状态」。**延期到 backend 真上线后做**（数周级架构重构）
    - [x] ~~5-26 demo 快照备份~~ ✅ `99_archive/2026-05-26_ios_v1_demo_snapshot/`（含 README 说明用途 + 41 swift 文件 / 1.1M）
  - Web（teacher_web/round3）：同类 demo seed / mock state（需 grep 清单 — iOS 推进时未处理）
  - 权威备忘：`memory/project_demo_scaffolds_to_remove_before_v1.md`
  - 执行时机：v1.0 spec 冻结前，或接真后端那一刻（两者取早）

- [ ] **补点呼机契约 spec**(v0.2 spec gap)
  - Phase 1 代码开工前必须写
  - 至少含:`POST /api/v1/checkin` 请求/响应格式、WebSocket 消息协议、点呼机职责边界("只搬运,不判断")
  - 版本策略待定:原目录改 vs 开 `01_specs/v0.2/`

- [ ] **review 今天的 dev_log,可能修改**

---

## 🟡 中优先级(学习 / 推进)

- [ ] **Python 第 2 天: for 循环 + 列表**
  - 地点: `~/dev/practice/`(不在 DMSD 仓库)
  - 题目尽量和 DMSD 相关(点呼、扣分、签到)

- [ ] **Python 继续: dict + 函数**(Day 2 之后)

- [ ] **把 AC 叙事内容粘到 Mac 备忘录**
  - 之前从 progress_overview 抽出来的那段

- [ ] 🔴 **项目文件大整理 — 散 / 多 / 复杂 / 功能重复**（2026-05-04 itsuki 提，明天/后天做）
  - 现状痛点（itsuki 自己说的）：
    1. 太散 — 元层文件散布在 00_admin/ 多个文件
    2. 太多 — 项目文件总览列了 600+ 文件
    3. 太复杂 — 同一类信息在多处出现
    4. 功能重复 — 比如 SOP / 文档同步点清单 / 项目文件总览 都涉及版本号联动
  - 整理方向：
    - 哪些可以合并？哪些可以归档？
    - 哪些应该升级为 skill / hook（已有 ac-record + version-bump 2 个 skill 可参考）
    - 哪些是历史快照可以挪 99_archive？

- [ ] 🔴 **项目文件总览 + 文件联动 — 拆成 2 个 skill 架构**（2026-05-04 itsuki 第 6 次纠正 CC 设计盲点）

  **演化历史**：
  - v1（CC 提）：联动规则放 CLAUDE.md → itsuki 戳穿"token 浪费"
  - v2（CC 改）：联动 + 总览融合到一个文件 → itsuki 戳穿"每次改文件都读完整文件浪费 token"
  - **v3（itsuki 拍板）**：拆成 2 个独立 skill，各司其职

  **3 层最终架构**：
  ```
  ┌─ Skill: file-linkage ── 短，专一（~50 行联动矩阵）
  │  触发：CC 改文件后 / itsuki 说「我改了 X 要查什么 / 联动检查」
  │  物理位置：新建 00_admin/联动矩阵.md（itsuki 直接打开方便）
  │  SKILL.md 是指针 → Read 联动矩阵.md
  │
  ├─ Skill: project-overview ── 长，详细（文件清单+内容概要）
  │  触发：itsuki 说「X 文件干嘛 / 找文件 / 项目里有什么 X 类文件」
  │  物理位置：保留 00_admin/项目文件总览.md（itsuki 直接打开方便）
  │  SKILL.md 是指针 → Read 项目文件总览.md
  │
  └─ CC PostToolUse Hook ── 确定性脚本（不进 context）
     CC 调 Write/Edit 后立刻跑 sync-rules.sh → 报告联动漏改
  ```

  **「指针 skill」设计**（itsuki 拍板）：
  - SKILL.md 主体只写「触发条件 + Read XX 文件」指令
  - 物理内容保留在 00_admin/（itsuki 习惯打开方便）
  - 优点：物理 single source / itsuki 查询习惯不变 / CC 按需触发
  - 缺点：CC 多一次 Read 调用（可忽略）

  **子任务**（按依赖顺序）：
  1. 新建 `00_admin/联动矩阵.md`（从 CLAUDE.md「文件连锁结构」+ `hooks/lib/sync-rules.sh` + `文档同步点清单 §11` 提炼，~50 行）
  2. 创建 `.claude/skills/file-linkage/SKILL.md`（指针 → 联动矩阵.md）
  3. 项目文件总览补"大概内容"列（每个文件 1-2 句具体写了什么）
  4. 创建 `.claude/skills/project-overview/SKILL.md`（指针 → 项目文件总览.md）
  5. CC PostToolUse hook 落地（settings.json 配 + 复用 sync-rules.sh）— 跟「日语注释拦截 hook」一起做
  6. CLAUDE.md「文件连锁结构」段瘦到 ~5 行指针「→ file-linkage skill / project-overview skill / hook」
  7. 文档同步点清单 §11 内容挪走（如重叠）
  8. 项目文件大整理（散 / 多 / 复杂 / 重复）

  **token 账**：
  - 现状：CLAUDE.md「文件连锁结构」~15 行 = 占启动开销
  - v1 方案（CC 错）：CLAUDE.md +80 行 / +2k 永久 token
  - **v3 方案**：CLAUDE.md -10 行 / 联动矩阵 skill ~50 行按需 / 总览 skill 按需 — 启动开销-200 token，按需加载只加载需要的那块

  - 工作量预估：大（~5-8 小时）

  - **CC 失误演化**（itsuki 连环戳穿 — 全是 AC 素材）：
    - 第 1 次：CC 提"指针文件"多余
    - 第 2 次：CC 提"未完全理解"自我贬低
    - 第 3 次：CC 关键词触发不实用（itsuki 不说那些词）
    - 第 4 次：CC 联动规则塞 CLAUDE.md（token 浪费）
    - 第 5 次：CC 总览+联动融合（每次改文件都读全文浪费）
    - 第 6 次：（如果还有错）—— itsuki 持续做 CC 的 design coach
  - itsuki 要求：「我对项目文件总览的要求就是可以让我就在这一个文件里面就了解整个项目所有的文件都是干嘛的，某个文件是干嘛的，某个文件里面有什么，大概有什么内容，然后某个文件改了之后要跟另外一个文件联动之类的」
  - 升级后必含 4 类信息：
    1. **文件是干嘛的**（已有 — "作用"列）
    2. **大概内容**（部分有 — 要补全到每个文件 1-2 句"具体写了什么"）
    3. **联动规则**（**新增** — 改了 A 必查 B；融合到每个文件条目"联动"列 + 末尾「联动矩阵」section 双层）
    4. **状态 / AC 价值**（已有）
  - 同步机制：每次新建/删除/改/移动文件 → 项目文件总览 必须当场更新

  **⭐ 文件联动的 3 层架构（itsuki 5-04 拍板，CC 之前误判塞 CLAUDE.md，被 itsuki 纠正后改方案）**：

  ```
  ┌─ Skill 形态联动规则手册 ── 按需触发（不占启动 token）
  │  itsuki 主动调 / 关键词「联动检查 / 我改了 X 要查什么」
  │  内容：联动矩阵全文 + 反向索引 + sync-rules.sh 人类可读版
  │
  ├─ CC PostToolUse Hook ── 行为触发实时拦截（不进 context）
  │  CC 调 Write/Edit 工具瞬间 → 自动跑 sync-rules.sh → 立刻报告漏改
  │  比 git pre-commit 早一步（CC 中途没 commit 也能拦）
  │
  └─ CLAUDE.md ── 永远在线但只 5 行指针
     - 改文件 → CC PostToolUse hook 自动报联动
     - 主动查 → 调 skill 或翻项目文件总览
  ```

  - **替代后果**：
    - `CLAUDE.md「文件连锁结构」段` ~15 行 → ~5 行指针（省 ~200 token 永久开销）
    - `00_admin/文档同步点清单.md §11 文件联动规则` 挪到 skill / 项目文件总览
    - `00_admin/hooks/lib/sync-rules.sh` 保持代码化（hook 自动跑）— 但内容人类可读版搬到项目文件总览末尾「联动矩阵」section

  - **同时要做（关联子任务）**：
    1. 创建新 skill `.claude/skills/file-linkage/SKILL.md`（联动规则手册 — 触发关键词「联动 / 改了 X 要查什么 / 联动检查」）
    2. 加 CC PostToolUse hook（settings.json 配置 + 复用 sync-rules.sh）— 跟「日语注释拦截」hook 一起做
    3. 项目文件总览补"大概内容" + 加"联动"列 + 末尾「联动矩阵」section
    4. CLAUDE.md「文件连锁结构」段瘦身到 ~5 行指针

  - 工作量预估：大（~5-8 小时）— 比单独整理总览多了 skill + hook 落地

  - **CC 失误案例（这次会话）**：CC 一开始判断「联动规则放 CLAUDE.md 永远在线」 → itsuki 立刻戳穿「token 太多」+ 提出「skill + 行为触发 hook」方案 → CC 承认错误，改方案。这是 itsuki 第 5 次戳穿 CC 设计盲点（前 4 次：指针文件 / 未完全理解 / 关键词触发 / 项目文件总览不该融合 → 这次是要融合）。

### 🆕 unknown unknowns 工程实践体检清单（2026-05-04 CC 主动诊断 — 等 itsuki 回来再做）

> 背景：5-04 晚 itsuki 戳穿 CC coach 失职后，CC 系统扫描 DMSD 还有哪些业界标准实践他可能没用过。详细 dump 见 `05_logs/raw/2026-05-04.md §X.5`。
>
> **判断原则**：每条都要先问"对 DMSD 当前有没有真用得上"，不为了堆技术栈而装。

**🔴 大概率没用 / 应该试**（投产比高，半天内能装上）：
- [ ] **GitHub Actions（CI/CD）** — 单人也能用，每次 push 自动跑 pytest，挂了立刻邮件通知。3-5 行 yaml。**好处**：每次推代码不会因为漏跑测试爆掉。
- [ ] **Linter / Formatter** — `ruff` (Python) / `swiftlint` (Swift) / `prettier` (TS/Web) 自动检查代码风格。**好处**：不靠你眼睛 + 团队风格统一。
- [ ] **Type checker** — `mypy` (Python) 静态查类型错误，bug 在跑代码前就发现。Swift 自带，TypeScript 自带。
- [ ] **API 文档自动化** — FastAPI 自带 `/docs` 路由（你已经有但可能没意识到 / 没充分用）。打开 `http://localhost:8000/docs` 就是交互式 API 文档，不用手写。
- [ ] **`.env` + python-dotenv** — 把 DB 密码 / API key 从代码里拿出来，**防止 commit 进 git**。配 `.gitignore` 排除 `.env`。

**🟠 单人项目可以延后但要知道**（v1.0 上线相关时再装）：
- [ ] **GitHub Issues** — 替代 TODO.md（多人时必须，单人也能用 label 分类）。可以晚点，本 TODO.md 暂时够用。
- [ ] **Sentry** — 生产环境错误自动收集（v1.0 上线前装），错误来了自动邮件 + 看堆栈。
- [ ] **Docker** — 部署时保证环境一致（v1.0 部署到 VPS / 教师端 Pi 时会用上），「在我电脑能跑」的反义词。
- [ ] **结构化日志（structlog）** — 比 `print()` 强，能查询 / 过滤 / JSON 格式存档。

**⚪ 暂时跳过**（DMSD 用不到 / 太重）：
- Performance profiling / A/B testing / 监控大盘 / Kubernetes 等

**学习路径建议**（如果要做）：
1. 先 `.env`（30 分钟，风险最高 — 别 commit 密码进 git）
2. 后 `ruff` + `swiftlint`（1 小时，立刻看到效果）
3. 后 `mypy`（半天，需要给已有代码加类型 hints）
4. 后 GitHub Actions（30 分钟 yaml + 把上面 3 个串进去）
5. v1.0 上线前再做 Sentry + Docker

---

## 🟢 低优先级(整理 / 维护)

- [x] **git push 今天(4-13)的 4 个 commit 到 GitHub** ~~2026-04-19 打 x：已完成（后续又 push 了 v0.2.0/v0.3.0 双 tag）。backlog D14~~
  - `3b01345` 版本号重置 v1.0 → v0.1 <!-- VERSION_OK -->
  - `e637034` 建立 AC 入試完整记录体系
  - `e346dca` 目录结构整理 + 历史内容抢救
  - `43c73ec` 2026-04-12 NFC 方案设计日 dev_log

- [ ] **.pages 文件转 Markdown**(3 个非 rollcall 文件 — B-007 修)
  - `01_specs/API_Contract_v0.1.pages`
  - `01_specs/IA_UI_v0.1.pages`
  - `01_specs/Overview_of_Features_v0.1.pages`
  - ~~`01_specs/rollcall/*.pages`~~ — 已废,已被 `RollCall_Spec.md` 取代（2026-04-17 v0.2 主体 rewrite）

- [ ] **清理 `01_specs/临时PDF/` 下的"のコピー"副本**(5 个文件)
  - git status 里一直挂着

- [x] ~~**归档早期 iOS throwaway 代码**~~ — 已 2026-04-29 大整理归档到 `99_archive/2026-04-29_pre_v1.0_cleanup/`（line 714 §T2 已标 ✅，重复条目 B-007 修）

- [x] **给空目录建 README 或 .gitkeep 或删除** ~~2026-04-19 打 x：这些目录根本不在 git 里（git 不 track 空目录），本地 find 也没列出来 → 该 TODO 条目虚，无需处理。backlog D16~~
  - `02_design/`, `04_ops/`, `06_assets/`, `07_release/`

- [x] **建 `.gitignore`** ~~2026-04-19 打 x：.gitignore 已存在（4-13 前），该 TODO 条目过期。backlog D15~~
  - 至少忽略 .pages 临时副本、macOS 的 .DS_Store 等

- [ ] **建 `README.md`**(项目根目录,GitHub 首页)
  - 项目是什么 + 现在到哪了 + 技术栈

---

## 🔵 中远期(还早,不用现在做)

- [ ] **VPS 安装 PostgreSQL**
- [ ] **搭建 FastAPI 后端骨架**(`03_dev/backend/`)
- [ ] **采购 NFC 卡**(120 张,等决策定了)
- [ ] **采购点呼机硬件**(等大脑选型定了)
- [ ] **学 Swift / SwiftUI 基础**(Phase 2 学生 App 才用到)
- [ ] **学 C/C++ + Arduino / ESP-IDF**(如果选 ESP32 路线)

- [ ] **搭建宿舍综合官网** `dmsd.otogi2025.com`（或同类域名）
  - 承载：APK 下载 + 学生首次安装引导 / AASA 文件（iOS Universal Link）/ assetlinks.json（Android App Links）/ 未来的学生端通知公告 / 老师端管理网站入口 / 校外联系方式
  - 来源：2026-04-20 议题 B-8，itsuki 自己的想法——把"APK 分发页"扩展为"完整宿舍官网"
  - 时机：议题 E 后 / v0.5.0 左右，不急

- [ ] **keystore 备份（Android App 签名证书）**
  - 方案（2026-04-20 议题 B 定稿）：**本地 Mac 主存 + 后端服务器加密压缩包（跨人传承）+ 密码纸质笔记本**（毕业转交接手人）+ 年度校验
  - 不存 iCloud（个人账号不可传承）
  - 时机：开始打包 Android App 时（M3-M4 里程碑），不早于 v0.6.0

- [ ] **异常行为检测（风控）** — 议题 D-2 推迟 M3+
  - 5 分钟内 >5 次失败签到 → 标记审计
  - 同 session 跨点呼机异常切换
  - 签到时间集中异常
  - 时机：v0.6.0+（有用户数据后再做）

- [ ] **毕业交接包设计** — 议题 B keystore 传承考虑触发
  - keystore 转交
  - 域名 DNS 转让
  - 服务器管理员账号移交
  - GitHub repo transfer ownership
  - 交接 checklist + README
  - 时机：2028-01（毕业前 2 个月）

---

## ✅ 已完成归档(最近 1 个月)

### 2026-04-13
- [x] 版本号体系重置 v1.0 → v0.1 (commit `3b01345`)
- [x] 建立 AC 入試完整记录体系 (commit `e637034`)
- [x] 目录结构整理 + 历史内容抢救 (commit `e346dca`)
- [x] 2026-04-12 NFC 方案设计日 dev_log (commit `43c73ec`)

### 2026-04-12
- [x] NFC 架构决策(Raspberry Pi 方向 + 分阶段 + 播报防作弊)
- [x] 更新 executable_dev_checklist_v0.1

### 2026-04-10
- [x] 解决 NFC/NFD git pull 失败问题
- [x] 建立 AI 协作机制
- [x] 一个月空白反思

### 2026-03-11
- [x] Python Day 1: 变量、数据类型、print、if/elif/else

### 2026-03-10
- [x] Git 基础学习,GitHub 仓库创建,项目初始化

### 2026-02-12
- [x] v0.1 规格冻结

---

## 📝 维护说明

- **新增待办**: 随时往上面加,分好优先级
- **完成待办**: 在 checkbox 打 x,保留在原位置
- **归档**: 每周或每月一次,把打 x 的移到"已完成归档"
- **重排优先级**: 想到什么就调整,不用和 Claude 商量
- **不确定放哪里**: 先扔到底部,之后再分类

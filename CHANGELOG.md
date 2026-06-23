# Changelog

> **最后更新**: 2026-06-18（**v0.24.9 ~ v0.27.0 — 上线前全量审查修复 campaign（5 端 bug/日语/校验/对齐）+ C42/C43 出寮届撤回·差戻重提 4 端 + 后端 PostgreSQL 部署修复 + 老师网页 demo 登录分权限组与版本号构建自动注入 + 后端寮过滤改登录选寮·临时账户到期；v0.24.8 之后多会话并行 51 commit 回溯切 3 patch + 3 minor + 补打先前漏建的 v0.24.8 tag，三端客户端版本号同步 0.27.0，当前版本 v0.27.0**）。早些：2026-06-16（**v0.24.8 — iOS 日语 UI 自然度全量审查施工：以真实宿舍《2026年度生徒寮のしおり》为基准全量复审，13 代理并行改 16+ 文件 149 处（晩自習→夜学習 74 / 退回→差し戻し / 学籍番号→アカウント番号 / 保証人→保護者 / 認証コード→登録コード / 罰則清掃词序 / 半角排版），双 scheme BUILD SUCCEEDED，commit `a0e7d9a`，patch、三端客户端版本号攒未动，当前版本 v0.24.8**。早些：**v0.24.7 — iOS 登录切标签不清空字段（patch，1 commit `74e0618`）**。早些：**v0.24.0~v0.24.6 — 多会话 22 commit 回溯切版本（1 minor + 6 patch），v0.24.6**：后端安全/并发硬化 minor v0.24.0（DemeritEvent 唯一约束+迁移 / slowapi 限速 / 审批行锁串行化 / 上传流式防 OOM / 鉴权对齐权限组 + 测试补全）+ iOS 假数据泄漏·401·时区全链 JST patch v0.24.1~3 + teacher_web 代録入口 patch v0.24.4 + 演示账号放开 patch v0.24.5（知情决策、回退 6-08 隔离）+ iOS 日语母语复审 patch v0.24.6。7 个 annotated tag 已建（指向各历史 commit、日期回填）。三端客户端版本号本批未同步 — 回溯切版本撞并发会话占用工作树（两次冲掉本次编辑），避让、待串行后补（记 TODO §B）。详见下方各版本段 + 「2026-06-15 回溯切版本说明」banner）。早些更新：2026-06-15（**v0.23.11 — 选学生统一组件 StudentPicker + 快递件数 item_count 跨三端，当前版本 v0.23.11**：6-14 拍板设计、6-15 凭设计文档实装。后端加 item_count 字段+迁移 `0dee708c484e` + 新增 `GET /discipline/students`（C_DEMERIT，扣分搜学生，不复用前台接口因权限簇不同）；老师网页 `shared.tsx` 新建共用 `StudentPicker`（single/multi + searchApi prop）接三处 + 宅配弹窗件数步进器+房号自动+备注可选+删配送業者 + 扣分页新增搜学生入口；iOS 显示件数。后端 392 passed + 网页 tsc+build + iOS 双 scheme BUILD SUCCEEDED。单功能簇 patch、三端客户端版本号可攒未动。3 commit `b946489`/`affeac2`/`0261228` 未 push）。早些更新：2026-06-14（**v0.23.10 — iOS 上线前审查 Tier2/Tier3 修复批，当前版本 v0.23.10**：工作流（12 agent 并行分析 + 对抗核验）重定位漂移行号、CC 逐簇落地 6 簇 86 处：A=JST 时区选择性 10 处（生日 date-only / 全局 dateEncodingStrategy 经核验未碰）+ B=枚举仅安全收 Bool?→Bool（其余 5 项改 enum 会多文件连锁+改运行时行为、UI 已有守卫，记 TODO）+ C=日语「明显」措辞自然化 30 + D=其他 bug 11（toast 代次令牌 / 点呼详情 O(n)→单次解析 / 月历切月智能复位 / 头像取消即复位 / 锁定计时器迟到 Task 守卫 / 健康履历吞 401 改清登录态 / 未读 badge 同源 / Keychain 写失败降级日志不再 DEBUG 崩）+ E=漏洞中低纵深 6（Keychain 访问级别 WhenUnlocked / baseURL 环境变量仅 DEBUG / 4 处 print 仅 DEBUG）+ F=Tier3 润色 26 + 小 bug 3（班车 Date(JST) 比较 / 登录切 tab 清字段 / ApplyKindMapper 死键修复）。双 scheme（E 簇加 Release 档验 #else 分支）全绿，6 commit，patch、三端客户端版本号攒未动；命名故事 AC 叙事 + 称呼归属 + 演示姓名汉字 3 项搁置待 itsuki）。早些更新：2026-06-14（**v0.23.9 — iOS 上线前审查 Tier1 修复批，当前版本 v0.23.9**：第2簇防抖 8 表单 + 第3簇 NFC 生产不再本地伪置 done（recordCheckin 整段包 #if DEMO、状态全由后端 my_checked_in_at 驱动，消除被每秒覆盖的竞态）+ 默认日期改未来 + 第4簇中危漏洞 4 类（合同下载走统一 APIClient / 16 处错误文案不暴露内部 / PDF 先验大小防内存崩 / 上传不吞 401）+ codex 复审两轮收敛（补强 422 口径 + PDF 预检限 PDF）。双 scheme BUILD SUCCEEDED，5 commit，patch、三端客户端版本号攒未动）。早些更新：2026-06-14（**v0.23.8 — iOS+Android 班车「特別運行便」一覧只显示特別便 + 運航→運行 汉字统一，当前版本 v0.23.8**：itsuki 截图反馈，两端班车页只显示寮生特別運行便（隐藏平日通学便）+ 删「すべて/特別便/通学便」类型筛选条（留空港开关）+ 徽章用全称「特別運行便」；itsuki 凭母语级日语直觉纠对代码错字「運航」（专指船/飞机）→ 巴士标准「運行」，全项目 13+ 处简繁運航/运航统一成運行/运行；共用规格 §7.6.2 同步。iOS 双 scheme + Android assembleDebug 通过，5 commit。单功能簇 patch，三端客户端版本号可攒未动）。早些更新：2026-06-13（**v0.23.7 — 公告补 is_demo 隔离 + 对齐 iOS 演示公告，当前版本 v0.23.7**：`Announcement` 加 is_demo 字段+索引+迁移 `a2b3c4d5e6f7`；6 端点按 is_demo 隔离（演示老师/学生只看演示公告、碰真实公告返 404），解除演示老师禁发/禁回复改成 demo 沙盒内可操作；seed 种 6 条演示公告（固定 UUID 对齐 iOS SEED.swift）；根治 BACKEND_DESIGN_LOG §7.5.1 记的 v1.1 公告读侧隔离债。公告+demo 26 测试全绿（专属库避多会话并发污染）。单功能簇 patch，三端客户端版本号可攒未动）。早些更新：2026-06-13（**v0.23.6 — 后端启动 schema 落后自检，当前版本 v0.23.6**：`main.py` lifespan 加 `_warn_if_db_schema_outdated()`，dev 启动比对库 alembic 版本 vs head，落后打 WARNING（`current=None` 全新库静默不误报）。背景：teachers/public 500 根因是本地 dev 库缺 6-12 alembic 迁移 `f1a2b3c4d5e6`（`teachers.permission_group` 列）。pytest 371 passed）。早些更新：2026-06-12（**v0.23.5 — iOS 公告翻訳重做（原地翻译），当前版本 v0.23.5**：把公告翻译从弹系统浮层改成正文原地翻成母语（`TranslationSession` 程序化接口 iOS18+）+ 语言选择窗 英/简中/泰/越 + 默认语言记忆 + 「通知設定」升级综合「設定」页；`@preconcurrency` 解决 Swift6 完全并发「sending session」报错。双 scheme BUILD SUCCEEDED。单功能簇 patch，三端客户端版本号 patch 可攒未动）。早些更新：2026-06-12（**v0.23.4 — 老师权限分级 codex 审查四项修复，当前版本 v0.23.4**：4 个补丁（F1~F5 中 4 个被采纳）经 codex 二次审查 + CC 独立核实前提后修复，pytest 371 passed 全程保持，复审收敛 blocker 0 / major 0）。早些更新：2026-06-11 深夜（**v0.23.0 — iOS 体验功能批次 + 首批单元测试 + 管理基建搭车，当前版本 v0.23.0**：收尾「版本当场结账」新机制首战 — v0.22.3 之后 28 commit 一次结清。驱动者 = iOS 功能批次（介绍页重做 4 页 / 公告 AI 翻译+要約 / 图标换 Tomoshibi-icon-1 / 首页活动+巴士卡接真 M-1 / AI 头像启用）+ iOS 首批 7 条单元测试（点呼时间窗状态机，test target 从零建立）；管理基建（老师网页 CI / 后端 142 接口总表 / 文件清单生成器 / raw 迁 iCloud / 启动收尾流程改版）按规矩不驱动版本号、随段记录。三端客户端版本号同步 0.23.0）。早些更新：2026-06-11（**插空细分 + 新段补标 — v0.3.3~v0.14.8 共 70 个补丁插空 + v0.20.0~v0.22.3 新打，当前版本 v0.22.3**：按「一个 bug 一个补丁号」给老段号位空隙里的 70 个 fix commit 逐个补打补丁标签（已 push 的 67 个旧标签与 commit 全部未动、历史未重写，新标签日期回填 commit 当天）；3 个号位死区内 13 个 fix 在对应版本段「死区注记」逐条列出；v0.19.3 之后 76 个 commit 按同标准切 3 minor + 3 patch。详见下方「2026-06-11 插空细分说明」banner）。早些更新：2026-06-09（**v0.15.1 ~ v0.19.3 重排补打 32 个标签** — v0.15.0 之后 95 个 commit（6-05~6-09、全本地未 push）按 itsuki 拍板「一个 bug 一个补丁号 / 连续 feat 批次合成次版本号」重排，当前版本 **v0.19.3**；远程 origin 最后 push 停在 v0.8.0 故重排安全；详见下方「2026-06-09 重排说明」banner + 各版本段。深度审查 19 条 findings 记 `00_admin/TODO.md` §🔍 不在本次修）。早些更新：2026-06-05（**v0.12.1 patch + v0.13.0 ~ v0.15.0 三连 minor** — 6-03/6-04/6-05 三天 80 commit 按真实 commit 顺序切：v0.12.1（6-03 纯修复段：删寮ウォール收尾 + iOS 既存 bug + 点呼机文档）/ v0.13.0 出租车予約 4 端 + 文件联动 / v0.14.0 杭田 6-04 需求批 + 外出申請 + 契約書 / v0.15.0 老师网页迁 Vite + Android 对齐 + 学年更新 + Resend，**当前版本 v0.15.0**；三端客户端版本号同步到 0.15.0）。早些更新：2026-06-03（**v0.8.1 ~ v0.12.0 回溯补标** — 5-11 ~ 6-02 一个多月连续施工的 236 commit 一次性按语义化版本（SemVer）规范回溯补 6 个版本标签 + CHANGELOG 条目；详见下方各版本段顶部「回溯补标说明」banner）。早些更新：2026-05-02 晚（**v0.8.0 close** — 5 端代码层全启动（含点呼机骨架）：Android Compose bootstrap + 10 屏 / iOS 网络层完整建设 + AppStore 切真后端 / teacher_web v1 TS+Vite+Zustand 升级 + 5 page / backend rollcall+study+teachers routers + Alembic 框架 / iOS↔backend 字段对齐 F1-F5+Q1）。早些更新：v0.7.0 close（三轨 A+B+C 同日完成 38 条老师反馈 + 实物表 evidence 推翻 LINE 文字推测 + 沟通规则 #6 + SOP §8.5 版本路线图）；v0.6.0 close（老师 4-29 LINE 38 条受领 + RollCall_Spec 5 处时序修订 + system_features 中文骨架大重写）；v0.4.0 + v0.5.0 双 minor 闭合；**版本管理 SOP 建立**
>
> **2026-05-19 注**: v0.8 之后累积 15+ commit 实质推进（5-04 文件联动工具 / 5-08 硬件全定稿 / 5-10 ac-radar / 5-11 cc-comm-rules + graphify / 5-13 文件大整理 / 5-14 anti-ai-flavor / 5-16 跨项目大修 / 5-19 project-overview 大改造 + 防漂 C 方案 / 5-20+ 131 条 bug findings 修复），未到 bump 触发线，详见 WIP + progress_overview。
>
> 版本号规则：[语义化版本 (SemVer)](https://semver.org/) — 主版本号.次版本号.修订号
>
> **本项目约定**：
> - `v0.x.y` = 开发阶段，`0.x` 本意就是"不稳定，什么都能改"
> - `v1.0.0` = 系统在宿舍正式上线运行（对外第一次兼容性承诺）
> - spec 实质内容未变的版本 bump = patch（`0.0.y` / `0.x.y`），只有"新范围进来"才 minor bump
>
> **pre-0.1 的追认**：下方 `0.0.x` 系列是在 2026-04-17 回溯 chat log 后补标的。
> 原始迭代发生在 ChatGPT 对话里，未进入 git（见 `05_logs/raw/2025-12_NFC系统早期设计对话.md` 节选）。
> 打这些标签的目的：让"讨论了十几种方案才写第一版文档"这件事有可追溯的证据链。
>
> **2026-04-20 更新**：10 个 pre-0.1 annotated tag（`v0.0.1` - `v0.0.10`）已追认打在 initial commit `3baa168` 上，每个 tag message 里写了对应版本的核心内容 + 指向 CHANGELOG / raw 的指针。`git tag -l | sort -V` 可以看到完整版本历史。

---

## 全版本一览（v0.0.1 → v0.27.0）

> 一行一个版本快速定位，技术细节见下方对应 `## [x.y.z]` 段。
> **版本号单一真值 = 本文件（CHANGELOG.md）**。

| 版本 | 日期 | 一句话 |
|---|---|---|
| v0.0.1~0.0.6 | ~2025-12 | 史前方案推翻：手机当卡 → 二维码 → 静态 ID 不可信 → 设备签名+一次性码 |
| v0.0.7~0.0.10 | 2026-02-02~08 | 从纯讨论过渡到建目录、准备进 Git |
| v0.1.0 | 2026-02-12 | spec 规格冻结（8 验收场景 + 扣分阈值）|
| v0.1.1 | 2026-04-13 | 错命名的 v1.0 全改回 v0.1 + 建 CHANGELOG |
| v0.1.2 | 2026-04-15 | 架构原则：点呼机「只搬运数据、判断全在后端」|
| v0.1.3 | 2026-04-17 | spec 从 .pages 转 .md |
| v0.2.0 | 2026-04-17 | 字典层单源真值 |
| v0.3.0 | 2026-04-17 | spec 主体重写（681 → 958 行）|
| v0.3.1 | 2026-04-20 | AC 文档层 + 文档同步机制 |
| v0.3.2 | 2026-04-20 | 推翻 4-19 两条架构决策 |
| v0.3.3~0.3.6 | 2026-04-21~22 | 补丁 ×4：spec S 系列漏洞闭合三批 + API_CONVENTIONS 48→240 行（6-11 插空补标）|
| v0.4.0 | 2026-04-22 | 系统命名 Tomoshibi + spec 漏洞批量闭合 |
| v0.5.0 | 2026-04-29 | Demo 4-28 冲刺落地 |
| v0.5.1 | 2026-04-29 | 补丁 ×1：恢复误删的 teacher_requirements.md（6-11 插空补标）|
| v0.6.0 | 2026-04-29 | 老师 38 条需求受领 + 设计大重写 |
| v0.6.1~0.6.2 | 2026-04-30 | 补丁 ×2：国際交流課長 役职補正 + 描述同步（6-11 插空补标）|
| v0.7.0 | 2026-04-30 | 三轨并行消化 38 条 |
| v0.7.1~0.7.2 | 2026-05-02 | 补丁 ×2：后端 meals_skip 序列化 / iOS ApplicationStatus 补枚举（6-11 插空补标）|
| v0.8.0 | 2026-05-02 | 五端代码全启动 |
| v0.8.1 | 2026-05-16 | 注册码+公告 4 端 + 点呼机第 5 端 + 工具链（期间 7 个 fix 见该段死区注记）|
| v0.8.2 | 2026-05-24 | iOS 上架版融合 + 删后门（期间 4 个 fix 见该段死区注记）|
| v0.8.3~0.8.8 | 2026-05-26~27 | 补丁 ×6：FC-024 明文密码 / FC-027 公告权限 / import 崩溃 ×2 / iOS 债务 / codex 审查批（6-11 插空补标）|
| v0.9.0 | 2026-05-27 | 老师网页真接口全实装 |
| v0.9.1~0.9.5 | 2026-05-28 | 补丁 ×5：iOS catch / 注册码转数字 / 登录页收口 / seed 时区 / 房间号双前缀（6-11 插空补标）|
| v0.10.0 | 2026-05-28 | 申请实物表数字化 + 116 天伪问题 |
| v0.10.1~0.10.12 | 2026-05-30 | 补丁 ×12：teacher_web v1.0 W8 修复链 — 后端 7 bug / 安全加固 / 寮边界 R4 / codex 4 轮（6-11 插空补标）|
| v0.11.0 | 2026-05-30 | 老师网页六大模块 + 项目心智模型 |
| v0.11.1~0.11.30 | 2026-05-31~06-02 | 补丁 ×30：隐私清理 / 三端小 bug 批 / IX 系列接后端 codex 多轮收敛链（6-11 插空补标）|
| v0.12.0 | 2026-06-02 | iOS 全面接真后端 IX 系列 + ST25DV 架构反转 |
| v0.12.1 | 2026-06-03 | 纯修复 patch（期间 2 个 fix 见该段死区注记）|
| v0.13.0 | 2026-06-03 | 出租车予約 4 端 |
| v0.14.0 | 2026-06-04 | 杭田老师需求大批 + 外出申請 |
| v0.14.1~0.14.8 | 2026-06-05 | 补丁 ×8：Vite 迁移审查修复 / roster 并发 / renewal 寮边界 / revision 撞号（6-11 插空补标）|
| v0.15.0 | 2026-06-05 | 老师网页迁 Vite + 学年更新 |
| v0.15.1~0.15.2 | 2026-06-05 | 补丁 ×2：iOS 通知持久化 / 申請详情防越界 |
| v0.16.0 | 2026-06-05 | 学生包裹查询接口 + iOS 外出/契約書 + APNs 推送骨架 |
| v0.16.1~0.16.11 | 2026-06-05~06 | 补丁 ×11：推送幂等 / 打扫去ロビー / 日语母语级 / 鉴权 / 宅配 / **时区根治** / iOS 包裹接后端 等 |
| v0.17.0 | 2026-06-07 | 前台男女寮过滤+接口 + 后端 6 自查接口 + iOS 8 界面接真后端 + 演示账号隔离起步 |
| v0.17.1~0.17.12 | 2026-06-07~08 | 补丁 ×12：演示隔离 + iOS 接线 codex 多轮复审修，一轮一个补丁号 |
| v0.18.0 | 2026-06-08 | 演示账号默认启用 + 删 DEMO 水印 + 11 全局端点隔离补齐 |
| v0.19.0 | 2026-06-08 | iOS 上线缺口 11 功能（含**手机 NFC 签到** ST25DV）|
| v0.19.1~0.19.3 | 2026-06-09 | 补丁 ×3：iOS NFC codex 三轮复审修 |
| v0.20.0 | 2026-06-09 | Android 8 屏接真后端批 + v1.0/1.1/1.2 范围冻结规格 |
| v0.21.0 | 2026-06-10 | 清扫/罚扫功能全 5 端删除 |
| v0.22.0 | 2026-06-11 | iOS 点呼显示链接真后端 R-1/R-2 + 后端 /rollcall/me/today |
| v0.22.1~0.22.3 | 2026-06-11 | 补丁 ×3：R-3 防连点 / R-4 登录锁定真值 / R-5 体調履歴接真 |
| v0.23.0 | 2026-06-11 | iOS 体验功能批次（介绍页/AI 翻译要約/新图标/首页接真/AI 头像）+ 首批 7 条单元测试 + 管理基建搭车（CI/接口总表/文件清单/raw 迁 iCloud）|
| v0.23.1 | 2026-06-12 | 补丁：F2 renewal-start 端点漏挂权限闸（codex 审查）|
| v0.23.2 | 2026-06-12 | 补丁：F1 admin_accounts 3 端点补寮边界（codex 审查）|
| v0.23.3 | 2026-06-12 | 补丁：F4 delete_teacher 最后管理员保护集合错误（codex 审查）|
| v0.23.4 | 2026-06-12 | 补丁：F5 学習担当 fallback 组错误（codex 审查）|
| v0.23.5 | 2026-06-12 | 补丁：iOS 公告翻訳重做（原地翻译 + 4 语言选择 + 默认语言 + 设置页升级）|
| v0.23.6 | 2026-06-13 | 补丁：后端启动 schema 落后自检（`_warn_if_db_schema_outdated`，dev 启动比对 alembic head 打 WARNING）|
| v0.23.7 | 2026-06-13 | 补丁：公告补 is_demo 隔离 + 对齐 iOS 演示公告 |
| v0.23.8 | 2026-06-14 | 补丁：iOS+Android 班车「特別運行便」一覧只显示特別便 + 運航→運行 汉字统一 |
| v0.23.9 | 2026-06-14 | 补丁：iOS 上线前审查 Tier1 修复批（日语残留+防抖 8 表单+NFC 生产不伪置 done+中危漏洞 4 类+codex 复审） |
| v0.23.10 | 2026-06-14 | 补丁：iOS 上线前审查 Tier2/Tier3 修复批（JST 时区选择性 10 + 枚举 Bool 收紧 + 日语明显 30 + 其他 bug 11 + 漏洞中低纵深 6 + Tier3 润色 26+小bug3）+ 同区间并行（多会话补记）：注册码对全权限组+演示账号放开 `aa1ee98` |
| v0.23.11 | 2026-06-15 | 补丁：选学生统一组件 StudentPicker + 快递件数 item_count 跨三端（后端加字段+迁移+扣分搜学生接口 / 老师网页共用组件接三处+件数步进器 / iOS 显示件数）|
| v0.24.0 | 2026-06-15 | minor：后端安全/并发硬化（DemeritEvent 唯一约束+迁移 / slowapi 限速 / 审批行锁 / 上传流式防 OOM / 鉴权对齐 effective_group + 测试补全）|
| v0.24.1 | 2026-06-15 | 补丁：iOS 生产假数据泄漏（#if DEMO 守卫）+ 401 集中处理 |
| v0.24.2 | 2026-06-15 | 补丁：iOS 时区全链 JST 统一（DatePicker 4 文件 + Calendar.current 6 处 + 格式化全链）+ 隐私清单 APNs + 减点口径 |
| v0.24.3 | 2026-06-15 | 补丁：iOS 时区修复 codex 三轮复审补强 |
| v0.24.4 | 2026-06-15 | 补丁：teacher_web 代録入口调整 + 学生账号按钮文案 |
| v0.24.5 | 2026-06-15 | 补丁：演示账号放开 4 处 assert_not_demo_teacher（知情决策，遗留风险见 decision_log）|
| v0.24.6 | 2026-06-15 | 补丁：iOS 日语 UI 字符串母语者全量复审 10 处修正 |
| v0.24.7 | 2026-06-15 | 补丁：iOS 登录页切番号/メール标签不再清空对方输入框 |
| v0.24.8 | 2026-06-16 | 补丁：iOS 日语 UI 自然度全量审查施工 — 以宿舍《生徒寮のしおり》为基准 16+ 文件 149 处 |
| v0.24.9 | 2026-06-17 | 补丁：上线前全量审查修复·第一波（5 端 bug/日语自然度/校验/对齐 + 后端契約書 magic bytes 校验 + 2 寮 A 前缀房号注册修复 + codex 复审）|
| v0.25.0 | 2026-06-17 | minor：C42/C43 出寮届撤回·差戻重提 4 端实装 + C20 在线学习者夜学習缺席豁免 + teacher_web/iOS 审查深水批（多会话深夜并行）|
| v0.25.1 | 2026-06-18 | 补丁：iOS 主页「下次罚扫」小卡简化（只显示日期时间、去地点、不可点）|
| v0.25.2 | 2026-06-18 | 补丁：后端迁移 d2e3 batch recreate=always→auto，修生产 PostgreSQL 部署崩 |
| v0.26.0 | 2026-06-18 | minor：老师网页 demo 登录分权限组（每组 demo 老师 + op 账号 + 系统管理者入口）+ 版本号构建时从 CHANGELOG 自动注入 |
| **v0.27.0** | **2026-06-18** | **minor：后端寮过滤改登录时选寮重开 + 临时账户到期机制（后端+老师网页 3 端）← 当前版本** |
| v1.0.0 | 目标 2026 底~2027 初 | 宿舍正式上线 |

---

> **【2026-06-11 插空细分 + 新段补标说明 · v0.3.3 ~ v0.14.8（70 补丁）+ v0.20.0 ~ v0.22.3】** 按 itsuki 拍板「一个 bug 一个补丁号」两步补齐：① 老段（v0.3.2 ~ v0.15.0）号位空隙里的 70 个 `fix` commit 逐个补打补丁标签（v0.3.3~0.3.6 / v0.5.1 / v0.6.1~0.6.2 / v0.7.1~0.7.2 / v0.8.3~0.8.8 / v0.9.1~0.9.5 / v0.10.1~0.10.12 / v0.11.1~0.11.30 / v0.14.1~0.14.8）—— **已 push 的 67 个旧标签一个未动、commit 未动、历史未重写**，新标签日期回填 commit 当天；3 个号位死区（v0.8.0→v0.8.1→v0.8.2、v0.12.0→v0.12.1）内 13 个 fix 无空号可插，在对应版本段「死区注记」逐条列出。② v0.19.3 之后 76 个 commit 按同标准切 3 minor + 3 patch（v0.20.0 ~ v0.22.3，当前版本）。v0.3.2 以前的早期 commit 未用 feat/fix 前缀，不做机械细分。管理体系类 fix/feat（收尾流程 / hooks / 联动规则）按 version-bump 决策树第 7-9 条不驱动版本号。

> **【2026-06-15 回溯切版本说明 · v0.24.0 ~ v0.24.6】** v0.23.11 之后多会话累积 22 个 commit（后端硬化批 / iOS 时区与假数据修复批 / teacher_web 调整 / 演示账号放开 / iOS 日语复审），单一会话无法在产生时即时结账。按「version-bump §2 决策树 + 一个 bug 一个补丁号 + 连续新基建/feat 批合成 minor」回溯切为 1 个 minor（v0.24.0 后端，命中迁移 schema 变更 + 新基建限速阈值）+ 6 个 patch。7 个 annotated tag 已建、日期回填各段末 commit 当天，commit 与历史均未改写（v0.23.11 起所有 commit 未 push，回溯安全）。⚠️ 三端客户端版本号本应在 minor 处同步至 0.24.6，但回溯切版本期间并发会话正占用工作树并两次冲掉本次编辑，故避让、客户端版本号暂攒未动（待工作树串行后补同步，已记 TODO §B）。

> **【2026-06-18 回溯切版本说明 · v0.24.9 ~ v0.27.0】** v0.24.8 之后多会话累积 51 个 commit（6-16~6-18：上线前全量审查修复 campaign 跨 5 端 + C42/C43 出寮届撤回·差戻重提新功能 + 后端 PostgreSQL 部署修复 + 老师网页 demo 登录与版本号机制 + 后端寮过滤改登录选寮·临时账户到期），多会话并行无法在产生时即时结账。按 version-bump §2 决策树 +「连续 feat 批合成 minor / bug 修复批 patch」回溯切为 3 patch（v0.24.9 / v0.25.1 / v0.25.2）+ 3 minor（v0.25.0 / v0.26.0 / v0.27.0）。同时补打先前漏建的 **v0.24.8 tag**（release commit `423b07c` 已存在但当时未打 tag）。7 个 annotated tag 日期回填各段末 commit 当天，commit 与历史均未改写（v0.24.8 之后所有 commit 未 push，回溯安全）。深夜批（v0.25.0）因 teacher_web 审查修复、C42/C43 feat、iOS 审查批由多会话并行交错提交，无法线性拆分，合并为单一 minor 如实记录。三端客户端版本号本批同步至 0.27.0（iOS `project.yml` / Android `build.gradle.kts`；老师网页自 v0.26.0 起构建时从本文件自动注入、无需手改）。⚠️ 本次结账时另一会话仍在并行提交功能 commit（结账前 HEAD 从 `fcab4ee` 推进到 `4eb503a`），本批以结账时刻 HEAD=`4eb503a` 为界，之后新提交留待下次结账。

## [0.27.0] - 2026-06-18（后端寮过滤改登录时选寮 + 临时账户到期机制）

> 起因：老师登录后的寮（宿舍栋）过滤原先固定在账号属性上，改为登录时选择寮并据此重开会话；同时为临时调入的老师账号加到期机制。后端 + 老师网页 + 设计文档同批（由并行会话提交 `4c4df64` / `f7ecca4` / `4eb503a`）。

### Added
- 后端 `teachers.expires_at` 字段 + 迁移 `d1e2f3a4b5c6_add_teacher_expires_at`：临时账户到期后登录被拒。
- 老师网页登录密码屏「选寮」步骤 + 临时账户创建表单（`TeachersAdminPage`）。

### Changed
- 寮过滤逻辑从账号固定属性改为登录时选寮、按所选寮重开会话（`deps.py` / `auth.py`）。
- 老师网页登录卡片移除寮徽章（改为登录时选）。
- `system_features.md` 3 处寮过滤注记 + 后端/网页设计日志同步。

### Notes
- 后端 199 行新测试 `test_temp_account_and_dorm_select.py` 覆盖临时账户到期 + 选寮。
- openapi 接口总表重导 + schema 快照测试为该并行会话后续收尾项，本次结账时尚未提交（不在本批 push 范围）。

## [0.26.0] - 2026-06-18（老师网页 demo 登录分权限组 + 版本号构建自动注入）

> 起因：① demo 演示登录原先单一 demo 老师，改为每个权限组一个 demo 老师 + 运维（op）单独账号 + 系统管理者登录入口，便于按角色演示。② 老师网页版本号长期手改易漂移，改为构建时从 CHANGELOG 顶部自动注入。

### Added
- 老师网页每权限组一个 demo 老师 + op 单独账号 + 系统管理者登录入口（commit `fcab4ee`）。
- `vite.config.ts` 构建/启动时读 CHANGELOG 顶部版本号注入全局常量 `__APP_VERSION__`，`theme.ts` 直接用（commit `22aa548`）。

### Changed
- 老师网页版本号自此「跟着 CHANGELOG 走」——发版只需重新构建网页即同步，对应 version-bump §4 第 8b 项（治第 8 项 patch 漂移）。

## [0.25.2] - 2026-06-18（后端迁移修复 — 修生产 PostgreSQL 部署崩）

> 起因：后端完整版首次部署到生产 PostgreSQL 时迁移崩溃。根因：`batch_alter_table(recreate="always")` 是 SQLite 专用（强制整表重建），在 PG 上重建带外键依赖的表时需先删主键、被外键挡住。

### Fixed
- 迁移 `d2e3` 的 `recreate="always"` → `"auto"`（6 处）：PG 走原地 ALTER、SQLite 仍重建，两边都对（commit `a7e2ad8`）。

### Notes
- 仍有 3 处 `recreate="always"` 为潜在风险（仅全新建库才触发，不影响现状），记 TODO，需 PG 副本验 base→head 后再逐个改，勿无脑 sed 全改。

## [0.25.1] - 2026-06-18（iOS 主页「下次罚扫」小卡简化）

### Changed
- iOS 主页「下次罚扫」小卡只显示日期时间，去掉地点、改为不可点击（commit `97483cf`）。IOS_DESIGN_LOG §31 同步。

## [0.25.0] - 2026-06-17（C42/C43 出寮届撤回·差戻重提 4 端 + C20 夜学習豁免 + 审查深水批）

> 6-17 深夜多会话并行批。包含一项跨 4 端新功能（C42/C43）、一项业务规则修正（C20）、以及 teacher_web / iOS 上线前审查的深水区修复。因多会话交错提交无法线性拆分，合并为单一 minor 如实记录。

### Added
- **C42/C43 出寮届撤回 + 差戻（差し戻し，退回重办）重提 + 行事企画重提**：后端端点（commit `06e2461`）+ Android 学生端 UI（`f131ade`）+ iOS 学生端 UI（`552da64`）+ teacher_web 差戻按钮整链（`fd6ad80`）。

### Changed
- **C20 在线学习承認者夜学習缺席豁免**：经承認的在线学习者夜学習不误判缺席、不扣 1.5 分（commit `ddaea9d`）。
- 個人情報 U1 编辑按钮文案对齐实际可改项（学年/组/番号归老师控制，commit `c7eaa62`）。

### Fixed
- teacher_web 审查深水批：后端并发竞态 + 晚自习逻辑 + 校验上限 + 健壮性 + 演示隔离 + 历史统计 + 锁定过滤 + 权限闸 + 前端申请/点呼改判核心 + 权限组接线（TW-001 ~ TW-126 数十项，commits `adc4758` / `092a725` / `4f885aa` / `e17a5fd` / `871d5e0` / `a7e5c11` / `a2ac02b` / `36c82a1` / `70ddefc` / `c8619be`）。
- iOS 审查批：登出清推送残留 + 注册半登录兜底重拉 + 密码长度三方对齐 + 移除写真死按钮 + 生年月日(0歳)兜底 + 点呼详情空态 + 面包屑重复路由 + PageHeader 长按双触发 + 移除下書き假动作 + 食事不要期間上限 + 申请列表失败错误态 + OutingOut datetime 对齐后端（commits `4eea1d8` / `23b9b10` / `d427cb0` / `ef45f0f` / `57cf9e0` / `e9785dd` / `32fa291`）。
- iOS 启动页 logo 更新为最新蓝火苗图标（commit `788ec63`）。

### Notes
- `1da5419` chore：iOS weak-link FoundationModels/Translation 防旧系统崩 + 清理散落文件。
- 设计文档同步：backend C42/C43/C20 变更履历 + 各端 Q3 v1.1 候补死代码登记 + IOS_DESIGN_LOG §30。

## [0.24.9] - 2026-06-17（上线前全量审查修复·第一波 5 端）

> 起因：v1.0 上线前对 5 端做全量审查（找 bug / 日语自然度 / 校验 / 跨端对齐 / 死代码）并修复第一波。

### Fixed
- 后端：2 寮 A 前缀房号注册被 422 拒绝修复 + 契約書上传加文件头 magic bytes 二次校验 + 下载 nosniff + 数据完整性/鉴权/中文漏出/并发批 + codex 复审 2 项（commits `8724772` / `7c18251` / `4e71a38` / `49e7a9e`）。
- iOS：审查代码修复批（2 寮注册 iOS 半 + 日期钳制 + 前后端对齐 + 次要 bug）+ 日语自然度修复批 + 全量审查 14 条（死文件/日语/校验/版本机制）（commits `9be4da1` / `34bb7ff` / `b3ce454`）。
- 老师网页：检索结果寮表示修正（dormLabel 收 dorm_unit 数字恒判女子寮，TW-004）+ parseJst 时间解析修期限徽章恒「期限内」（TW-002）+ 全量审查（bug/死代码/日语/对齐）+ codex 复审（startSession 清零 nfcSeq）（commits `fd04244` / `b6c6fcb` / `481aa4d` / `7ad35e9`）。
- Android：全量审查（中文漏出/日语统一/对齐/死代码，commit `040e8b8`）。

### Notes
- 文档对齐代码现实：開示申請残留清理 + WS/nav/分页示例修正（commit `9fb6930`）+ ANDROID_DESIGN_LOG §12 同步（`2648c09`）。
- 区间含 v0.24.8 CHANGELOG 文档补记 commit `3112995`（teacher_web 晩自習→夜学習同批落档），属 v0.24.8 文档尾、不单独成版本。

## [0.24.8] - 2026-06-16（iOS 日语 UI 自然度全量审查施工 — 以宿舍《生徒寮のしおり》为基准）

> 起因：itsuki 要求把整个 iOS app 的**所有日语** UI 再做一遍自然度审查，并第一次把**真实宿舍手册**《2026年度生徒寮のしおり》当对照基准（不是凭 AI / 直觉语感）。审查 + 施工图在前一会话产出（94 条确认），本会话施工落地。区别于 v0.24.6（仅凭语感扫出 10 处）。

### Changed
- **晩自習 → 夜学習**（决定 1，74 处）：app 全用「晩自習」但手册一律「夜学習」，连 app 自己的演示公告都写「夜学習」（自相矛盾）。本次仅 iOS；英文代号 `study`/`studyAbsence` 不动、接口契约零变化。**其余 3 端（后端用户文本 / 安卓 / spec）待全端统一，记 TODO §B；老师网页本版已含 ↓。**
- **老师网页 晩自習 → 夜学習（同批，commit `76fe434`）**：teacher_web 7 文件 25 处显示文字 + 注释，与上面 iOS 同向、同一日语审查批次（compact 后 itsuki「开干」执行）。后端角色 key `学習担当` 不动（roleLabel 显示成「夜学習担当」）；`permissions.ts` 权限组钥匙「一般宿管+晚自习」+ LoginScreen 同名标签缠后端比对值 + 一般宿管中文未决，留另一捆未动。`晩点呼→夜点呼`(5 处) 仍未做，记 TODO §B。`npm run build` ✓。
- **学籍番号 → アカウント番号**（决定 3）：按 app 自己体系，未采手册「生徒番号」。
- **罰則清掃 保留命名**（决定 2）：不用手册「環境整備」覆盖产品名，只统一被写反的词序「清掃罰則」→「罰則清掃」。
- 用词对齐手册：晩点呼→夜点呼 / 保証人→保護者 / 認証コード→登録コード（注册流程）/ 食事申告→申し込み / 予想経費→概算経費 / 学生納付金→寮費 / お問い合わせ→申し出て 等。
- 排版（仅日语 UI 串内，中文注释标点不动）：半角「·」→全角「・」、中文逗号「，」→「、」、半角「...」→「…」、名词数字间去半角空格。

### Fixed
- 中文漏出硬伤：`HomeStubs` `Text("請假")` → 欠席届；罚扫状态 `退回`（SEED / MyPage）→ `差し戻し`。
- SEED 点呼履历 `["朝","晩"]`→`["朝","夜"]` 时同步改 `specials` 字典查找 key（否则两天「欠席」特殊态静默失效）。

### Notes
- 工作流 13 代理分文件并行施工 149 处 + 主会话 grep 全树复验 + 亲自双 scheme 编译。共 16+ 个 swift 文件。
- 主会话不盲从施工图：`AppStore:1505` 把「寮務課長」误改「寮務部長」已回退（`寮務課長` 是 app 审批链真实独立角色、对后端 `approver_role` 契约，非しおり笔误；該命名是否按手册调留 itsuki 通盘拍板，同「減点→指導」性质）。施工图漏列的同类占位由 grep 补全（認証コード AuthStubs 3 处 / 清掃罰則词序 MyPage 2 处 / 晩点呼生产映射 MyPage:1077）。
- 双 scheme（`TomoshibiApp` + `TomoshibiAppDemo`）BUILD SUCCEEDED（iPhone 17 Pro）。commit `a0e7d9a`，patch，三端客户端版本号攒未动。详见 IOS_DESIGN_LOG §27。

## [0.24.7] - 2026-06-15（iOS 登录页切标签不清空对方字段）

### Fixed
- `LoginView`（`AuthStubs.swift`）切「番号 / メール」标签时不再清空对方输入框。原代码 `email = ""` / `acc = ""` 无任何功能作用：邮箱 mode 直接弹「メールでのログインは現在ご利用いただけません」不读 email 字段；导致 demo 演示版预填「060217 / demo@example.com」切来回一次双双消失。生产版也受益：切标签不再丢用户已填内容。

### Notes
- 双 scheme（`TomoshibiApp` + `TomoshibiAppDemo`）BUILD SUCCEEDED。1 commit `74e0618`，patch，三端客户端版本号攒未动。

## [0.24.6] - 2026-06-15（iOS 日语 UI 文字母语者全量复审 — 10 处自然度修正）

> 起因：itsuki 问「所有日语都自然了吗」。此前审查仅覆盖被标记字符串，未做从头逐条母语者普查。

### Changed
- iOS 学生端 28 个含假名文件、793 条日语 UI 字符串母语者全量复审（工作流：16 初审 → 去重 → 对抗终审），10 条确认修正 / 22 条误报驳回。
- 修正含：`請假`（中文漏出）→ `欠席届`；`次は…を…に`（无谓语悬空）→ `次回：…`；`前半節/後半節`（生造词）→ `前半/後半`；`予想審査時間` → `審査時間の目安`；`拾得場所`（兼落とし物语义反）→ `場所`；外泊「地点」→「滞在先/場所」；`希望所持理由` → `所持理由`；邮箱登录 toast 补不可用前提；演示申请 `駅前·タクシー予約` → `駅前·買い物` 等。

### Notes
- 双 scheme（`TomoshibiApp` + `TomoshibiAppDemo`）BUILD SUCCEEDED；`IOS_DESIGN_LOG.md` §24 同步。2 commit `4455be3` / `2b07115`。
- 误报反向确认：上批 `判定の変更はされていません` 经终审背书自然、`電波を確認してください` 判微妙语感未改。

## [0.24.5] - 2026-06-15（演示账号放开 — 拆 4 处 assert_not_demo_teacher）

> itsuki 6-15 拍板：演示账号也能用「教員アカウント管理」全功能（接 6-14 注册码同款知情决定）。版本号按改动范围（拆 4 守卫）定为 patch，安全分量由本段文字承载。

### Changed
- 后端 `teachers.py` 删招待発行/列老师/建老师/删老师 4 处 `assert_not_demo_teacher`（权限组矩阵不动，仍 op/寮管理者 MANAGE）；`TeachersAdminPage.tsx` 误导红字改中性文案；`BACKEND_DESIGN_LOG §3.8` / `teacher_permission_v1 §5` 同步。

### Notes
- 知情遗留风险（itsuki 明示勿自动修回）：演示账号可枚举真实老师 login_id/email、高权限组可增删真实老师；回退 6-08 演示隔离加固 `49176ff`。后端 409 passed / npm build 通过。1 commit `939bcc2`。

## [0.24.4] - 2026-06-15（teacher_web 代録入口调整 + 学生账号按钮文案）

### Changed
- 代録（代学生提交出寮届，低频）从 `Shell.tsx` 左侧导航「点呼業務」组移除，入口改到「申請」页标题区右侧按钮；路由与页面保留。
- 学生账号「＋ 新規追加（iOS から）」按钮去掉「iOS から」标注（点击说明不变）。

### Notes
- README 项目起点时间线补全（2025-12 起点）随段记录。2 commit `d103f2c` / `7e4e36a`（+ `90bea61` docs）。

## [0.24.3] - 2026-06-15（iOS 时区全链 JST 统一 + 隐私清单 + 减点口径）

> codex 多轮复审驱动：非 JST 设备上日期「输入 → 运算 → 格式化」全链偏移的系统性修复。

### Fixed
- 申请类时刻日期（出寮/帰寮/飞机/学習欠席/生日）`DatePicker` 输入端 + `parseHM/formatHM` + `dateRange` + `held_at` 合成全部固定 `Asia/Tokyo`；主动 grep 全 iOS 6 处 `Calendar.current` 统一 `tokyoCalendar`。至此全 iOS 日期链 JST 一致。
- 行事行生产版隐藏误导箭头（点击 guard 静默失效）；减点明细加区头「減点履歴（全期間）」与今月合計区分。

### Changed
- `PrivacyInfo.xcprivacy` 补 APNs Device ID 类别（Linked，关联 student_id），防上架驳回。

### Notes
- 双 scheme BUILD SUCCEEDED。5 commit `bab9872`/`1543cc6`/`85a738d`/`6b07a2f`/`5ee17f3`。

## [0.24.2] - 2026-06-15（iOS 401 令牌过期集中处理）

### Fixed
- `AppStore` 加 `handleIfUnauthorized`（带 loadMe 同款竞态守卫），4 个 load（包裹/曲目/失物/档案）catch 先调它：401 清令牌跳登录，消除「取得に失敗」死循环；非 401 保持原失败态。

### Notes
- 1 commit `167a4bf`。

## [0.24.1] - 2026-06-15（iOS 生产版假数据泄漏修复）

### Fixed
- Home 包裹卡 `pendingPkg` 加 `#if DEMO` 守卫：生产读 `app.packages`、demo 读 SEED。
- 注册完成页改读 `app.displayUser`（不再读 `SEED.user`），loadMe 失败显占位「—」而非演示假人。

### Notes
- 1 commit `1208b42`。

## [0.24.0] - 2026-06-15（后端安全 / 并发硬化批 — codex 复审 Q1–Q4）

> minor：命中迁移（schema 变更）+ 新基建（限速）阈值。v0.23.11 之后后端并发安全系统性硬化，含数据库约束、限速、行锁串行化、流式上传、鉴权对齐与测试补全。

### Added
- `DemeritEvent` 唯一约束 `(student_id, source_type, source_event_id)` + 迁移 `0e1f2a3b4c5d`，根除并发重复扣分。
- 限速基建 `ratelimit.py`（注册 10/h、学生登录 20/min、老师 10/min，按环境 enabled）+ slowapi 依赖。
- 后端测试 `test_discipline_curfew.py`（8 分外出禁止门槛/撤销/curfew_count）+ `test_study_finalize_demerit.py`（缺席扣分链/source_event_id/幂等/日期边界/demo 隔离），补 I1/I2 零测试缺口。
- 提交幂等 `Idempotency-Key`；全局异常处理器（未捕获异常统一 500 不泄堆栈）。

### Fixed
- 审批链并发原子化：`decide_approval` 条件更新 `UPDATE…WHERE decision IS NULL` + `expire` 重读审批链 + `with_for_update()` 行锁彻底串行化，根除两角色并发审批卡 `approved_partial`、补终态/撤回守卫与停用账号校验。
- 缺席扣分「缺席 → 出席 → 再缺席」漏扣（先查含软删 → 复活/INSERT）；改判扣分 + bulk_finalize 三处 `IntegrityError` 配 savepoint 容忍。
- 通知 mark_read 并发包 savepoint 防撞 `uq_notif_read`；契约书上传改 64KB 分块流式 + `.tmp`+`os.replace` 原子替换，防 OOM/截断毁旧合同。
- 档案鉴权由旧职位集改 `effective_group + has_permission(C_GUIDANCE)`，对齐权限组体系。

### Changed
- Dockerfile gunicorn `-w2` → `-w1`（WS 连接表单进程，上 Redis 前方案）；docker-compose 补 env 透传 + DEPLOY.md。

### Notes
- 后端全量 pytest 通过（codex 复审两轮收敛；Q3 强一致幂等表降级记 v1.1 TODO）。9 commit `e332881`(docs)→`bd0d968`/`790cc62`/`f23d634`/`67579d5`/`064356a`(test)/`a60f51e`/`9b34ea0`/`7ef0cf4`。
- 三端客户端版本号暂攒未动（回溯切版本撞并发会话占用，避让待补，记 TODO §B）。

---

## [0.23.11] - 2026-06-15（选学生统一组件 StudentPicker + 快递件数 item_count 跨三端）

> 起因：itsuki 6-14 截图反馈老师网页前台「宅配通知を追加」弹窗选学生不好用，拍板「选学生做成可复用组件、别处统一用 + 件数动后端」。6-14 brainstorming 出设计，本会话（6-15）compact 后凭设计文档跨三端实装。

### Added
- 后端 `FrontDeskItem.item_count`（宅配件数，Integer 默认 1，migration `0dee708c484e`，`server_default="1"` 回填历史行）；`FrontDeskItemOut`/`FrontDeskItemCreateIn` 同步加字段（默认 1、`ge=1`）。
- 后端 `GET /api/v1/discipline/students`（扣分页搜学生用，`C_DEMERIT` 权限，复用 `FrontDeskStudentBrief` 最小字段 + 同款 demo/寮过滤）。**刻意不复用** front-desk 的 `GET /students`：权限簇不一致（前台·宅配 vs 扣分管理），能扣分的寮監未必有前台权限。
- 老师网页共用组件 `StudentPicker`（`shared.tsx`，`mode` 单选/多选 + `searchApi` prop 适配三个权限不同接口 + `autoOpen` 打开即列表），接三处：前台快递弹窗（单选）/ 事件记录（多选，替换本地 `StudentMultiSelect`）/ 扣分页新增「任意の学生に手動加算」入口（保留排行榜行旧入口）。

### Changed
- 老师网页宅配弹窗：件数改步进器（−/数字/＋）选 `item_count`、部屋番号选学生后自动带出只读、备注改可选、删「配送業者」字段；列表行显示「N件 + 可选备注」。
- 后端 `FrontDeskItemCreateIn.description` 由必填 `min_length=1` 改 `Optional`，按 `kind` 区分必填性（宅配可空→落库存空串、失物招领仍必填，新增 `_lost_and_found_requires_description` validator）。
- iOS `AppStore.FrontDeskItemBrief` 加 `itemCount`（CodingKey `item_count`），通知中心宅配标题带件数「荷物が届いています（N件）」+ 宅配詳細页加件数行 + 空备注卡片标题回退「荷物 N件」。

### Notes
- 验证：后端全量 **392 passed**（+8 测试：item_count 默认/传值/`ge=1`、宅配 description 可空/失物必填、扣分搜学生 200/q 筛/学生令牌拒）；老师网页 `tsc --noEmit && vite build` 通过；iOS `TomoshibiApp`+`TomoshibiAppDemo` 双 scheme BUILD SUCCEEDED；`sync-check.sh` 全过 + 三端 `item_count` 字段对齐。
- Android 快递端读 `MockData.DEFAULT_DELIVERY` 假数据、未接后端，本次不涉及（接后端时再带 item_count，已记 TODO 远期）。
- 3 commit：`b946489`(后端) / `affeac2`(老师网页) / `0261228`(iOS)。单功能簇 patch，三端客户端版本号可攒未动。
- 遗留：三个搜学生接口无真分页（演示无碍、真实名册导入前补），已记 `admin/TODO.md` §B。

---

## [0.23.10] - 2026-06-14（iOS 上线前审查 Tier2/Tier3 修复批：JST 选择性 + 枚举 + 日语 + bug + 漏洞纵深 + 润色）

> 起因：6-13 审查分层后，Tier1（必改）已在 v0.23.9 落地，本段是 Tier2（重要）+ Tier3（润色）一次做完。用工作流（12 agent：6 簇并行「深度分析→对抗核验」流水线）重定位被 Tier1 改漂的行号、出精确 old_string/new_string 并核验硬规则/误报，CC 再逐簇 Edit 落地 + 双 scheme 真编译 + 按簇 commit（codex 编不了 iOS，落地与验证必须 CC 自己做）。

### Fixed
- **A·JST 时区选择性（10 处）**：公告展示/回复时间、首页班车·活动「今天」判断、点呼本地记录(DEMO)、学习打卡历史、本月点呼统计口径、违纪图表月份分桶各单点加 `Asia/Tokyo`；归国航班时间用 Tokyo 历合成（错在 `Calendar.current` 合成那刻，只改输出 formatter 没用）。**生日 `birthdayString`（date-only）与全局 `dateEncodingStrategy` 经核验未碰**（加 JST 会把生日算到前一天）。
- **C·日语「明显」措辞（30 处）**：机翻腔/外国人写法→自然日语 —— 取消→取り消し(6)、救済可能→判定を見直せます、失敗。もう一度→読み取りに失敗しました、願→申請、改判→判定の変更、永久→ロック中、予想問題点→想定される問題点と対応策 等。仅改 UI 日语字面、中文注释不动。
- **D·其他确认 bug（11 处）**：toast 代次令牌防连续 toast 互踢、点呼详情 O(n) 查找改单次解析、月历切月 `selectedDay` 智能复位、AI 头像取消即复位 loading（不等 5.5 秒）、登录锁定计时器 `invalidate` 后迟到 Task 守卫、健康履历吞 401 改清登录态、未读 badge 列表已加载时改用列表自身条数、Keychain 写失败降级日志不再 DEBUG `assertionFailure` 崩。
- **E·漏洞中/低纵深（6 处）**：Keychain 访问级别 `AfterFirstUnlock`→`WhenUnlockedThisDeviceOnly`、`baseURL` 环境变量覆盖仅 DEBUG 生效（Release 二进制固定生产地址）、4 处生产 `print(error)` 包进 `#if DEBUG`（loadMe/loadTodayRollcall/外泊审计/APNs）。
- **F·Tier3 润色（26 措辞 + 3 小 bug）**：日语建议级（去翻译腔あなたは/敬体统一/差戻→差し戻し/补句点·全角括号）；班车候选改 `Date(JST)` 解析比较不靠字典序(#5)、登录切 tab 清隐藏字段(#8)、`ApplyKindMapper` key `study_absence`→`studyAbsence` 修死键(#22，POST 时 encode 不再回退原值发错给后端)。

### Notes
- **B·枚举收紧**：分析+对抗核验两轮均判定 meal/path_hint/period/post_type/product 改 enum 会引发 `@State`/`Binding`/`decode` 多文件连锁 + 改运行时行为（如空串照发），且 UI 已有守卫，价值<风险 —— 只做安全的 `receipt_submitted`/`is_long_vacation` `Bool?`→`Bool`，其余记 TODO。
- 验证：每簇双 scheme `xcodebuild` 均 `BUILD SUCCEEDED`；E 簇因引入 `#if DEBUG/#else` 另跑 Release 档验 `#else` 分支编译。
- 6 commit：`4fe5565`(A) / `dff7063`(B) / `a1ef0e4`(C) / `aa047fa`(D) / `fd4b5bd`(E) / `6f3765a`(F)。
- 单批审查修复 patch，三端客户端版本号可攒未动。
- 搁置待 itsuki（3 项）：命名故事「日本で留学する私」措辞（AC 叙事归 itsuki）、变更不可字段称呼「先生 vs 寮監」（谁负责改学生资料=项目语义）、演示申請者姓名汉字写法（agent 自造无出处，本批只改了 号→番 单位）。

### 同区间并行（多会话，CHANGELOG 补记）
- **注册码功能对所有权限组 + 演示账号放开**（commit `aa1ee98`）：老师网页「学生登録コード」原对申請承認専用组只读、且演示账号被 `assert_not_demo_teacher` 一律挡。itsuki 拍板放开 —— `permissions.py` C_REG_CODE 矩阵全 MANAGE + 删 `admin_registration_code.py` 4 处演示闸（回退 2026-06-08 codex 加固 `49176ff`），所有权限组 + 演示账号均可完整读写真实注册码。诊断纠正前端红字「仅三职位」过时误报。后端全量 384 passed + 网页 build ✓。
- 归账说明：`aa1ee98` 提交于 v0.23.10 release（`341c3a3`）之前、是其 git 祖先，拓扑上已被 v0.23.10 包含；多会话并发致原 v0.23.10 条目只认领 iOS 审查、漏写本项，此处补记（故不另 bump v0.23.11）。决策详情 + 遗留风险（未来审查勿当 bug 修回）见 `logs/decisions/decision_log.md` 同日。

---

## [0.23.9] - 2026-06-14（iOS 上线前审查 Tier1 修复批：日语残留 + 防抖 + NFC 竞态 + 中危漏洞）

> 起因：6-13 对 iOS 学生端做的 4 维度全量审查（176 条 + codex 复核）分层后，把 Tier1 必改项分 4 簇执行。本段是第 2~4 簇 + codex 复审补强（第 1 簇日语残留已在 `ef9c65c` 落地）。

### Fixed
- **防重复提交（防抖，8 表单）**：失物/点歌投稿、宿舍行事企画/冷蔵庫購入/物品所持願、出寮届、学習欠席届、連絡先・部屋編集保存各加 `isSubmitting` 守卫（首个 `await` 前主线程同步置位 + `defer` 复位 + 按钮 disabled 叠加），消除手快连点重复 POST。
- **生产 NFC 点呼竞态**：`recordCheckin()`（本地伪置 rollState=.done/「時間内」）+ `autoDismissDoneTask` 整段包进 `#if DEMO`，删 HomeStubs 生产分支调用。原来生产写卡后本地置 done 会被每秒 `refreshRollStateFromSessions`（后端 `my_checked_in_at` 仍 nil）覆盖回受付中/欠席、体验像签到失败；改后生产只显「写卡成功」绿勾、点呼状态全由后端驱动（顺 v1.0 姿态：真权威判定在点呼机+后端）。顺带消灭 demo 常量 `rollCountdownSec=180` 泄漏进生产。
- **通用申请默认日期**：GenericApplyForm 的 date/endDate 从硬编码过去日 2026-04-25/26 改 `StayForm.tomorrow`/后天 + DateField `minDate` 钳住，来訪者不再把过去日当来訪日提交。
- **合同下载第二网络栈（中危）**：从 `URLSession.shared` 自建栈改走统一 `APIClient`（新增 `download(path:)`，复用 baseURL+鉴权+同一 session，将来加证书绑定/禁 Release 环境变量能覆盖到），`URLSession.shared` 全仓清零。
- **错误信息暴露内部（中危，16 处）**：生产兜底 `app.showToast(error.localizedDescription)` 全换 `APIErrorPresenter.userMessage(for:fallback:)`，不再泄漏后端原始 message/字段名/路径（审查点名约 5 处，grep 全仓实挖 16 处）。
- **大 PDF 内存（中危）**：合同 PDF 选取先用 `resourceValues(.fileSizeKey)` 验大小、超 10MB 直接拒，不再整包读进内存才校验（图片仍走压缩路径、不误挡能压小的大图）。
- **上传吞 401（Tier1）**：在线学习第二步上传契約書的内层 catch 加 `APIError.unauthorized` 分支，401 时清 token + 跳登录、不再吞成「添付失败」误进完成页。

### Notes
- codex（gpt-5.5 / xhigh，显式传 `--model`/`--effort`）只读复审两轮收敛（0 blocker / 0 major）：采纳 2 条（`download` 补 `case 422` 口径对齐 / PDF 预检限 `.pdf` 修图片回归），缓议 1 条（`StayForm.tomorrow` JST 口径 → 归 Tier2）。
- 验证：每簇正式版 `TomoshibiApp` + 演示版 `TomoshibiAppDemo` 双 scheme `xcodebuild` 均 `BUILD SUCCEEDED`。
- 5 commit：`be155a5`（防抖）/ `ec03fed`（NFC 竞态+默认日期）/ `7f4065a`（中危漏洞 4 类）/ `5efe4ba`（codex 补强）+ 第 1 簇 `ef9c65c`（日语残留，前一会话）。
- 单功能簇 patch，三端客户端版本号可攒未动。Tier2/Tier3 待 itsuki 拍板。

---

## [0.23.8] - 2026-06-14（修订：iOS+Android 班车「特別運行便」一覧只显示特別便 + 運航→運行 汉字统一）

> 起因：itsuki 截图反馈 iOS 班车页三点，拍板 iOS + Android + 共用规格全同步。

### Changed
- **班车一覧只显示寮生特別運行便**：iOS `BusListView.filtered` / Android `BusListScreen` 的可见列表过滤改成只留 `dorm_special`，平日通学便（`daily_commute`）不再显示（通常日校车靠页脚弱字另查）
- **删类型筛选条**：两端「すべて / 特別便 / 通学便」3 胶囊筛选 + 相关 state / 组件 / 孤儿 import 全删，只保留「空港送迎便のみ」开关
- **徽章用全称**：每行徽章「特別便」→「特別運行便」
- **共用规格 `system_features.md §7.6.2`** 班车一覧行为描述同步更新（只显示特別運行便 / 删类型 filter）

### Fixed
- **運航 → 運行 汉字纠错**：itsuki 凭母语级日语直觉打的「運行」纠对了代码里一直没人发现的错字 ——「運航」专给船 / 飞机、巴士的标准日语是「運行」（项目里「運行」本就是主流约 15 处，只班车界面落单 6 处）。全项目 13+ 处简繁「運航 / 运航」统一成「運行 / 运行」：iOS（`BusListStubs`/`Route`/`MyPageStubs`/`ApplyStubs`）+ Android（`BusListScreen`/`Routes`/`Models`/`MockData` 含 2 处公告假数据 UI 串）+ `system_features.md`（5 处）+ `BACKEND_DESIGN_LOG.md`。`IOS_DESIGN_LOG.md` 历史章节 6 处刻意保留作历史记录（§19.4 声明）

### Notes
- 验证：iOS 正式版 + 演示版双 scheme `BUILD SUCCEEDED`；Android `./gradlew assembleDebug` `BUILD SUCCESSFUL`
- 5 commit（`57c8398` iOS 代码 / `875c10a` IOS_DESIGN_LOG §19 / `c1b59b7` iOS 文件头补漏 / `79f702c` Android 代码 / `5102da4` 规格+后端·Android 设计档案）
- 单功能簇 patch，三端客户端版本号可攒未动

---

## [0.23.7] - 2026-06-13（公告补 is_demo 隔离 + 对齐 iOS 演示公告）

### Added
- `Announcement.is_demo` 字段 + `idx_announcement_is_demo` 索引（迁移 `a2b3c4d5e6f7`），与 students/teachers.is_demo 三表对称
- seed 演示数据种 6 条宿舍公告（固定 UUID 对齐 iOS SEED.swift，挂演示老师名下 is_demo=True）

### Changed
- 公告 6 端点按 is_demo 隔离：list/unread-count/detail 演示老师/学生只看演示公告、真实侧只看真实公告，碰对方公告返 404
- 解除演示老师禁发/禁回复公告的一刀切限制 → 演示老师在演示沙盒内发的公告 is_demo=teacher.is_demo
- test_demo_teacher 3 测试更新为新隔离语义（403→404 / 能发但隔离）

### Fixed
- 根治 BACKEND_DESIGN_LOG §7.5.1 记录的 v1.1 公告读侧 demo 隔离漏洞（演示老师能偷看真实老师广播）

### Notes
- iOS / 老师网页零改动（is_demo 不进 client schema，靠后端隔离自动受益）
- 公告 + 演示隔离 26 测试全绿（专属测试库避多会话并发污染）；既有 12 个 dorm 过滤测试 failed 与本次无关（baseline 对比证实，记 TODO）
- 单功能簇 patch，三端客户端版本号 patch 可攒未动
- commit: `859419a`(代码) + `8ae7803`(设计文档)

## [0.23.6] - 2026-06-13（修订：后端启动 schema 落后自检）

### Added
- **`_warn_if_db_schema_outdated()` 启动自检**（`app/main.py`）：dev 启动时比对库当前 alembic 版本 vs `ScriptDirectory.get_heads()`，落后则 `logger.warning` 醒目提示（含 `alembic upgrade head` 命令）。`current=None`（全新 `create_all` 库）静默不误报，不污染 pytest。背景：本地 `tomoshibi_dev.db` 缺 migration `f1a2b3c4d5e6`（`teachers.permission_group` 列）导致 `GET /teachers/public` 500（2026-06-13 真事故）。

---

## [0.23.5] - 2026-06-12（功能：iOS 公告翻訳重做 — 原地翻译）

### Changed
- **公告翻訳从「系统浮层」改成「正文原地翻译」**：旧 `.translationPresentation` 弹系统浮层 → 新 `TranslationSession` 程序化接口（iOS 18.0+）把正文整段替换成译文 +「原文に戻す」可切回。
- **点翻訳先弹语言选择窗**：4 语言 English / 简体中文(zh-Hans) / ไทย / Tiếng Việt（宿舍留学生主要母语）；可勾「次回からこの言語に翻訳する」存默认（`@AppStorage("translate_default_lang")`），设默认后下次直接翻不弹窗。
- **「通知設定」页升级为综合「設定」页**：新增「お知らせの翻訳」section 改默认语言（含「毎回選択する」回到每次弹窗）。

### Fixed（技术）
- `@preconcurrency import Translation` 解决 Swift 6 完全并发下 translationTask 闭包（继承 MainActor 隔离）调 nonisolated `translate`、而 `TranslationSession` 非 Sendable 导致的「sending session」数据竞争编译错。

### 说明
- 文件：`HomeStubs.swift` + `MyPageStubs.swift`，双 scheme BUILD SUCCEEDED（iPhone 17 Pro / iOS 26.5 SDK）。commit `94ee3b4`。
- 单功能簇 patch；三端客户端版本号 patch 可攒、本次未动（iOS 实装；Android 公告同类隐患待对齐 → TODO §B）。
- 新功能「老师单独给学生发私信」拍板要做、版本待定（TODO §B），不在本版。

## [0.23.4] - 2026-06-12（修订：F5 学習担当 fallback 组错误）

> **修订号**：codex 审查发现 `ROLE_DEFAULT_GROUP["学習担当"]` 错误映射到 `申請承認専用`（无操作权），itsuki 拍板改为 `一般宿管+晚自习`。alembic 迁移回填同步；`gakushu_promote` 测试夹具显式设 `permission_group="申請承認専用"` 防 fallback 依赖。commit `2087587`。

## [0.23.3] - 2026-06-12（修订：F4 delete_teacher 管理员保护集合错误）

> **修订号**：`TEACHER_ADMIN_ROLES = {"寮務部長", "寮務課長", "寮監"}` 集合成员错误（寮監 = VIEW 组被误含；校長 = MANAGE 组被遗漏）。新增 `_has_teacher_account_admin(teacher)` 函数按 `effective_group` 正确判断；删老师保护逻辑改用 Python 侧遍历计数。commit `b217453`。

## [0.23.2] - 2026-06-12（修订：F1 admin_accounts 3 端点补寮边界）

> **修订号**：`GET /students`、`password-reset`、`unlock-account` 三端点在权限分级后缺寮边界过滤。新增 `_assert_student_in_dorm` helper；`list_students` 加 `dorm_units_for_teacher` 过滤；`password_reset`/`unlock_account` 拿学生后立即校验寮归属。commits `718cced`。codex 报 14 个端点，CC 独立 git diff 核实只有 3 个是本次权限分级引入的缺口，其余 11 个是历史预存在问题（F1-遗留）。

## [0.23.1] - 2026-06-12（修订：F2 renewal-start 漏挂权限闸）

> **修订号**：`student_promote.py` 的 `/renewal-start` 端点仍用旧 `require_teacher_roles(*_ADMIN_ROLES)` 未迁移。改挂 `require_permission(C_STUDENT_ACCOUNT, MANAGE)`，删 `_ADMIN_ROLES` 常量。commit `4cb86b1`。

## [0.23.0] - 2026-06-11

> **为什么 bump**：v0.22.3 之后累积 28 commit，含完整 iOS 功能批次（决策树 #4 prototype 大幅扩展）→ minor。本段是「版本结账并入收尾」新机制（收尾核对表第 13 项）的首次实战 — 当场结清、不再攒标签。

### Added
- iOS：首次进入介绍页重做（4 页 / 只显示一次）`fa05f17` / 公告详情页 AI 一键翻译 + 一键要約 `785c206` / AI 头像生成重新启用（Apple Image Playground）`c5ce9a0`
- iOS：**首批单元测试** — `TomoshibiAppTests` 测试目标从零建立 + 点呼时间窗状态机 7 条（Swift Testing，注入时刻测 `decideRollState`），`xcodebuild test` 7/7 passed `8f237cf` `99a2999`
- 管理基建（不驱动版本号，随段记录）：老师网页 CI `ci.yml` / 后端 142 接口总表 `bin/export_openapi.sh` + `openapi_snapshot.json` / 文件清单生成器 `bin/generate_file_inventory.py` + `文件批注.tsv` 双轨 / pre-commit 版本演变一览拦截升级为阻塞 `25c4345`

### Changed
- iOS / 老师网页：app 图标与 logo 换 Tomoshibi-icon-1 新青绿渐变设计 `31a40fc` `4201a2f`
- 三端客户端版本号 0.22.3 → 0.23.0（version-bump §4 第 8 处联动）
- raw（AC 素材详细叙事）107 文件迁出仓库 → iCloud 素材池；启动 / 收尾流程改版（核对表 14 项、session-coord 停用、真值指针化 Rule 27）

### Fixed
- iOS：首页活动卡 + 巴士卡接后端真数据，生产不再显 SEED 假数据（M-1）`fc57edb`
- ruff 删 import 坑机制性堵死（挂钩 `--unfixable F401`）`caef9d3`

## [0.22.3] - 2026-06-11（修订：R-5 体調履歴接真）

> **修订号**：体調報告履歴接后端真数据，生产版不再显假病历。commit `e4078c5`。

## [0.22.2] - 2026-06-11（修订：R-4 登录锁定后端真值）

> **修订号**：登录锁定以后端为真值 — 接 423/403。commit `7841f5a`。

## [0.22.1] - 2026-06-11（修订：R-3 点呼弹窗防连点）

> **修订号**：三个点呼上报弹窗加提交中守卫防连点。commit `d3d0439`。

## [0.22.0] - 2026-06-11（iOS 点呼显示链接真后端 R-1/R-2）

> **为什么次版本号**：点呼显示链从整条假数据变真 —— 后端新建学生端 `GET /rollcall/me/today`（今日本人寮场次 + 四时间窗 + 我的判定），iOS AppStore 时间窗状态机真实驱动 rollState + 签到判定，点呼履历详情显真实场次窗口（消除写死「時間外/時間内」与 07:00/21:00）。对应 commit 段 `d076a51`..`9f92d00`。

## [0.21.0] - 2026-06-10（清扫/罚扫功能全 5 端删除）

> **为什么次版本号**：itsuki 拍板砍清扫/罚扫功能，按「拍板砍功能必须当场删代码」铁律全 5 端删除 + 揭示版残留 tab 删 + codex 2 轮收敛。commit `e15ae95`。

## [0.20.0] - 2026-06-09（Android 8 屏接真后端批）

> **为什么次版本号**：Android 从假数据迈向真后端的第一大批。对应 commit 段 `234cbaa`..`d210844`。

### Added（新功能）
- LoadState 三态基础设施（加载/失败/空）供各屏复用 + 登录接真 AuthAPI + 令牌持久化 DataStore + 启动自动登录
- 公告列表 / 各类申請一覧（行事企画/在线学习/冷蔵庫/物品所持）/ 巴士便 / 行事予定 / 出寮届申請+履歴 全接后端 + 三态
- v1.0 隐藏点呼签到入口（中央按钮改近日开放提示，NFC 签到属 v1.1）

### Notes
- 本段附带规格治理批 `769b95c`：v1.0/1.1/1.2 范围冻结规格三件套 + v1.0 验收脚本 + API 文档按实装同步

> **【2026-06-09 重排说明 · v0.15.1 ~ v0.19.3】** 以下 32 个版本是 v0.15.0 之后 95 个 commit（6-05~6-09、全本地未 push）按 itsuki 拍板的「一个 bug 一个补丁号、新功能批次才升次版本号」重排补打的标签 + 条目。**未改任何代码、未动任何已有 commit、未重写历史** —— 只在对应历史 commit 上打 annotated tag。判断依据：**每个 `fix` commit 各给一个修订号（patch），连续的 `feat` 批次合成一个次版本号（minor）**。远程 origin 最后 push 停在 v0.8.0，v0.8.1 起全本地，故重排安全。深度审查（多代理 6 维度 + 对抗验证）找到的 19 条 findings 记在 `00_admin/TODO.md` §🔍，不在本次重排里修。

## [0.19.3] - 2026-06-09（修订：iOS NFC codex 复审第三轮）

> **修订号**：ST25DVWriter 原子取消守护 —— 手机 NFC 签到 session 取消竞态最深层修复。commit `c2e052f`。

## [0.19.2] - 2026-06-09（修订：iOS NFC codex 复审第二轮）

> **修订号**：M-1 残留 —— loadMe 等待期间取消的拦截。commit `0193b89`。

## [0.19.1] - 2026-06-09（修订：iOS NFC codex 复审第一轮）

> **修订号**：手机 NFC 签到首轮复审，修 2 阻塞 + 4 重大 + 1 次要。commit `0841ad7`。

## [0.19.0] - 2026-06-08（iOS 上线缺口 11 功能）

> **为什么次版本号**：iOS 上架就绪一批新功能。对应 commit 段 `15b0ce5`..`4d4b5b5`（含中途修 `fd186ef` 令牌过期跳登录）。

### Added（新功能）
- **手机点呼签到** —— 新建 ST25DVWriter，用 CoreNFC 写 ST25DV Mailbox（2026-06-02 架构反转方案，手机写邮箱不联网）
- 6 个列表加载失败显三态（防把网络错误画成「なし」）+ 行事予定卡接真后端
- project.yml 补 NFC / 加密 / entitlements 上架声明 + 隐私清单据实补数据收集

### Changed / Removed
- 删巴士死页 BusView + .homeBus 路由 + 删暗色模式死控件开关
- 离线/拉资料失败生产版不回退假学生 + 通知设定页加「接通后生效」说明

## [0.18.0] - 2026-06-08（演示账号默认启用 + 全局端点隔离收尾）

> **为什么次版本号**：演示账号从 opt-in 默认关改默认启用（B）+ 删右下 DEMO 水印（A）+ 11 处全局端点（表本身无 is_demo 列的：公告回复/前台失物/点歌/遗失物社区等）补演示隔离守卫。codex 3 轮复审收敛。commit `15b0ce5`。

## [0.17.12] - 2026-06-08（修订：iOS 接线清缓办）

> **修订号**：清掉 codex 缓办的 4 项（首页/落地页假数据 + 外出守卫 + 查表大小写）。commit `72f3101`。

## [0.17.11] - 2026-06-08（修订：演示隔离 codex 第 5 轮）

> **修订号**：补账号管理漏洞（teachers/注册码/担任分支）。commit `49176ff`。

## [0.17.10] - 2026-06-07（修订：演示隔离 codex 第 4 轮）

> **修订号**：补 8 个 major（incidents/outings/study_online/study/dorm_life）。commit `16a1420`。

## [0.17.9] - 2026-06-07（修订：演示隔离 incidents + WebSocket）

> **修订号**：补事案 incidents + WebSocket 推送隔离（之前误判架构、实为能解决）。commit `683791f`。

## [0.17.8] - 2026-06-07（修订：演示隔离 rollcall/guidance/applications）

> **修订号**：补 codex 第 3 轮指出的 rollcall/guidance/applications 漏网。commit `545d04c`。

## [0.17.7] - 2026-06-07（修订：演示账号写隔离）

> **修订号**：写隔离 blocker 1/2 + 10 文件写越界（演示老师不能写真实数据）。commit `7e53748`。

## [0.17.6] - 2026-06-07（修订：演示隔离补 2 处列表泄漏）

> **修订号**：补 codex 复审逮到的 2 处遗漏列表泄漏。commit `d1c94b6`。

## [0.17.5] - 2026-06-07（修订：演示隔离第二批读取端点）

> **修订号**：8 个老师读取端点补 demo_scope（读泄漏）。commit `52bd71d`。

## [0.17.4] - 2026-06-07（修订：iOS 接线 codex 第三轮）

> **修订号**：双 await 流补第二令牌守卫 + resolve 按钮复位。commit `cb412f9`。

## [0.17.3] - 2026-06-07（修订：演示隔离 cleaning/misc 读泄漏）

> **修订号**：补 cleaning/misc 读泄漏 + 演示学生房号规范。commit `8dc3863`。

## [0.17.2] - 2026-06-07（修订：iOS 接线 codex 第二轮）

> **修订号**：9 处提交/更新流补令牌守卫。commit `b6bdc00`。

## [0.17.1] - 2026-06-07（修订：iOS 接线 codex 第一轮）

> **修订号**：4 处修复（owner 大小写/冷启动 profile/必填/空状态）。commit `219fa1e`。

## [0.17.0] - 2026-06-07（前台过滤 + 后端 6 功能 + iOS 8 接线 + 演示账号隔离起步）

> **为什么次版本号**：iOS 全面接真后端 + 后端演示账号隔离起步一批新功能。对应 commit 段 `0652e2b`..`3d5e6b0`。

### Added（新功能）
- 后端：前台列表男女寮过滤 + 寮監挑学生接口 + 6 个学生自查/上报/社区/杂项接口 + teachers 加 is_demo 列演示账号隔离（演示老师只看演示数据）
- iOS：8 个学生界面（扫除历史/个人信息/体调欠席/点歌/遗失物/修繕来訪代理/点呼历史/减点明细）生产分支接真后端，演示分支保留假数据

## [0.16.11] - 2026-06-06（修订：iOS 包裹接后端）

> **修订号**：包裹一览/履历/详情接真后端 + 假数据 #if DEMO 守卫。commit `25c700f`。

## [0.16.10] - 2026-06-06（修订：后端时区根治）

> **修订号**：后端时间统一存世界时、读出日本时间（+09:00）—— 新增 TZDateTime 自定义类型，替换 88 个 datetime 字段。修的是旧代码已发版的时间存储行为，按 SemVer 属修订号。commit `521d999`。

## [0.16.9] - 2026-06-06（修订：老师网页宿舍名 + 状态日语）

> **修订号**：宿舍名统一男子寮/女子寮 + 改判状态值日语化 + 删 AC 署名页脚。commit `44c2c5d`。

## [0.16.8] - 2026-06-06（修订：前台宅配空串归一）

> **修订号**：宅配 student_id 空串/纯空白归一成 None。commit `594b3ff`。

## [0.16.7] - 2026-06-06（修订：前台宅配必填收件学生）

> **修订号**：宅配登记强制带收件学生 student_id。commit `86304c2`。

## [0.16.6] - 2026-06-06（修订：iOS 冷启动令牌同步）

> **修订号**：冷启动恢复令牌时显式同步 APIClient.token。commit `85ea0f8`。

## [0.16.5] - 2026-06-05（修订：老师网页日语母语级）

> **修订号**：22 文件界面日语母语级修正 + 3 轮 codex 复审收敛。commit `e2962d0`。

## [0.16.4] - 2026-06-05（修订：iOS 包裹通知 id 偏移）

> **修订号**：包裹通知 id 偏移量调整避开理论碰撞。commit `78d39f8`。

## [0.16.3] - 2026-06-05（修订：后端推送补 import）

> **修订号**：补 IntegrityError import（codex 逮到 ruff 删了 import）。commit `4b713f9`。

## [0.16.2] - 2026-06-05（修订：后端打扫区域去ロビー）

> **修订号**：打扫区域 CHECK 约束去掉「ロビー」选项。commit `e563aec`。

## [0.16.1] - 2026-06-05（修订：后端 device-token 幂等）

> **修订号**：device-token 并发注册兜成幂等。commit `9f49f1d`。

## [0.16.0] - 2026-06-05（学生包裹查询接口 + iOS 外出/契約書 + APNs 推送骨架）

> **为什么次版本号**：一批新功能。对应 commit 段 `163ff51`..`6076579`。

### Added（新功能）
- 后端：学生端 GET /front-desk/mine 包裹查询接口 + 7 测试
- iOS：外出申請接 outings 后端 + 契約書补传/查看（A1-A3）
- iOS：APNs 推送骨架 + 包裹通知接后端 + datetime 解码兜底

## [0.15.2] - 2026-06-05（修订：iOS 申請详情防越界）

> **修订号**：详情页移动方式标签按种类区分 + 申请详情防 SEED 越界。commit `baba8a5`。

## [0.15.1] - 2026-06-05（修订：iOS 通知开关持久化）

> **修订号**：通知开关 @State→@AppStorage 本地持久化。commit `58f91e8`。

## [0.15.0] - 2026-06-05（老师网页迁 Vite + Android 对齐 iOS + 学年更新完成）

> **为什么次版本号**：多个真新功能 —— 学年更新/学生自设番号 5 端完成 + 老师网页 HTML→React/TS/Vite 迁移 + Android 对齐 iOS 43/60 屏 + 邮件 Resend。对应 commit 段 6-05（45 commit），末端 `3ac00bc`。

### Added（新功能）
- 学年更新 / 学生自设番号：后端开闸+自设+进度+老师单件改 + iOS 番号再設定按钮/弹窗 + 老师网页开闸/分组列表/进度横幅/兜底单件改 + 4/1 提醒横幅
- 老师网页从 HTML 单文件迁到 React 18 + TypeScript + Vite（界面 100% 冻结原样搬，26 组件；chrome 实测 17 页全渲染 + 27 接口 200 + 真数据通）
- student_android 对齐 iOS 7 波 ≈43/60 屏（マイページ全家桶 / 申請表单群 / 点歌 3 屏 / 行事予定 / 通知中心 / 点呼 NFC 状态条 / 学習签到 Sheet 等）
- 邮件 SendGrid → Resend 迁移（dev 无密钥不真发 + pytest）

### Changed
- `启动老师网站.command` 切到 build dist + 后端托管 dist；旧 HTML 单文件版整组归档到 `99_archive/2026-06-05_teacher_web_html单文件版归档/`

### Fixed
- 后端 dev 库 alembic revision 撞号修复（needs_renewal 误用 `b2c3d4e5f6a7` → 改唯一号 `f8a9b0c1d2e3` + 重建库）
- 老师网页 Vite 迁移三路审查收敛（地基 workflow 19 + 终审 workflow 8 + codex 3）
- 后端 pytest 311 全过

### Notes
- 老师网页仅剩 itsuki 肉眼签收 + push；RollCallLanding 统计卡是原样照搬的 demo 数据（带「DEMO」标记），接不接真后端待 itsuki 决策

---

## [0.14.8] - 2026-06-05（修订：插空补标 — backend）

> **修订号**：fix(backend): needs_renewal 迁移 revision 撞号修复(b2c3d4e5f6a7→f8a9b0c1d2e3)。commit `e5073e5`。

## [0.14.7] - 2026-06-05（修订：插空补标 — teacher_web）

> **修订号**：fix(teacher_web): Vite迁移阶段5 终审 part2(codex 3类型缝,CC核实后端路由全属实)。commit `8783073`。

## [0.14.6] - 2026-06-05（修订：插空补标 — teacher_web）

> **修订号**：fix(teacher_web): Vite迁移阶段5 终审修复 part1(workflow 8条裁决)。commit `86b9b18`。

## [0.14.5] - 2026-06-05（修订：插空补标 — renewal）

> **修订号**：fix(renewal): codex 审出 R4 寮边界 4 处 + needs_renewal 开闸检查。commit `9f87c8b`。

## [0.14.4] - 2026-06-05（修订：插空补标 — teacher_web）

> **修订号**：fix(teacher_web): Vite迁移阶段2审查修复 — types.ts 对齐后端 schemas.py。commit `3c5d7e4`。

## [0.14.3] - 2026-06-05（修订：插空补标 — web+backend）

> **修订号**：fix(web+backend): 既存错误提示路径修复 + 出寮届同日时刻后端兜底。commit `40de4e3`。

## [0.14.2] - 2026-06-05（修订：插空补标 — applications）

> **修订号**：fix(applications): 代録表单审查修复（自审 + workflow + Codex 三路）。commit `f3a846e`。

## [0.14.1] - 2026-06-05（修订：插空补标 — study）

> **修订号**：fix(study): roster 加入并发 race 防 500（自审中危发现）。commit `f08ca45`。

## [0.14.0] - 2026-06-04（杭田 6-04 教师需求大批 + 外出申請 + オンライン学習契約書）

> **为什么次版本号**：杭田老师 6-04 一批新功能横跨 5 端 + 新建外出申請（outings）功能 + 在线学习契約書上传。对应 commit 段 6-04（23 commit），末端 `04d738f`。

### Added（新功能）
- 外出申請（outings）：新建 outings 表 + 6 接口 + 単一先生確認流程（后端 + iOS）
- オンライン学習申請 契約書文件上传（后端 + iOS + 老师网页）
- 杭田 6-04 需求批：出寮者一覧只读页（网页 + 后端 `GET /applications/active`）/ 审批加学生评论框 / 审批结果给提出者本人发邮件 / 个人データ点呼履历朝夜分开 / 事案涉及学生姓名可点跳个人档案 / 行事予定接真后端 `GET /events` / 点呼 live 板预标出寮願生 exempt_range / 学習対象名簿增删 / 食数表导出入口 / 代録出寮届当日补录（后端）
- 寮生特別運行时刻表接真后端 + dev 种子巴士数据
- iOS 个人ページ精致化 + 巴士时刻表入口

### Changed
- 删除匿名建議功能（iOS + Android）+ 遗失物场所文案修正

### Notes
- 点呼机离线 → 老师手动接管设计（5 文档对齐）+ codex-review skill 立项

---

## [0.13.0] - 2026-06-03（出租车予約 4 端 + 文件联动系统扩展）

> **为什么次版本号**：出租车予約跨 4 端新功能（有真新功能即 minor）。对应 commit `4959168`（文件联动）..`b23f62c`（出租车），末端 `b23f62c`。

### Added（新功能）
- 出租车予約「タクシー予約」4 端（iOS / Android / 老师网页 / 后端）+ 出寮届表单字段对齐宿舍实物样本
- 文件联动系统补 4 类盲点（规则 19→23 条）+ codex 审查修复

### Notes
- 删寮ウォール收尾 / iOS 既存 bug 修复 / 点呼机架构文档对齐 已归入下方 **v0.12.1**（纯修复段，无新功能）

---

## [0.12.1] - 2026-06-03（删寮ウォール收尾 + iOS 既存 bug 修复 + 点呼机架构文档对齐）

> **为什么修订号（patch）**：本段**无新功能**，只有删除已决定的寮ウォール残留代码 + 修既存 iOS bug + 点呼机架构文档对齐 + 客户端版本号统一 —— 修旧代码、不加新东西即 patch。对应 commit `48e7c97`..`f85b3a9`，末端 `f85b3a9`。（patch 必须排在它修复的版本 v0.12.0 之后、下一个 minor v0.13.0 之前，本段正好满足。）

### Changed
- 删除寮ウォール（学生掲示板）残留代码 —— 落实 4-29 拍板（iOS struct 18→15 + 残留注释中文化）
- 三端客户端版本号统一到 0.12.0

### Fixed
- iOS 表单既存 bug：日期初值固定 JST + 表单冷启动竞态补填 + 预填迁 displayUser

### Notes
- 点呼机架构反转（手机读 → 写）5 文档对齐 + codex 复审 A 组 9 处一致性修复

### 死区注记（2026-06-11 插空细分）
- v0.12.0 与本段之间号位被占，期间 2 个 fix 无法补打独立补丁标签，逐条列此：
  - `5b36518` 06-03 fix(ios): 低风险残留清理 — 表单预填迁 displayUser + 在线自习日期固定 JST
  - `5971054` 06-03 fix(ios): Codex 审查加固 — 日期初值 JST + 表单冷启动竞态补填

---

> **【2026-06-03 回溯补标说明 · v0.8.1 ~ v0.12.0】** 以下 6 个版本是 5-11 ~ 6-02 一个多月连续施工、当时未及时 bump，于 2026-06-03 一次性按语义化版本（SemVer）规范回溯补打的标签 + 补写的条目。**未改任何代码、未动任何已有 commit、未重写历史** —— 只在各段末端 commit 上打 annotated tag（标签时间对齐对应 commit）。判断依据：**每段含真新功能即次版本号（minor），纯修复 / 开发工具链即修订号（patch）**。终点 v0.12.0，守住「v1.0 = 宿舍正式上线」的承诺。

## [0.12.0] - 2026-06-02（iOS 全面接真后端 IX 系列 + findings 收敛）

> **为什么次版本号**：8 个 feat 是 iOS 多个功能从假数据切到真后端 + itsuki 5-31 决策批新业务规则。虽同时修 30 个 bug（Codex 多轮复审收敛打磨），但「有真新功能」即触发 minor，修 bug 多不降级。对应 commit 段 5-31 ~ 6-02（73 commit），末端 `70f91b0`。

### Added（新功能）
- iOS 当前用户接真后端 IX-008：后端 `GET /students/me` + iOS 登录拉 /me 替换 SEED 假数据
- iOS 当月扣分汇总 IX-008b：后端 `GET /discipline/me/summary` + iOS 接线
- iOS 学習欠席当月计数 IX-034：后端 `GET /absence-requests/me/summary` + iOS StudyAPI
- iOS IX-004 修改届 / IX-009 通知 / IX-007 申请详情页 接真后端
- 晚自习 2 次签到 + 纪律 tier 月累计（iOS + Android）
- itsuki 5-31 决策批：扣分值 / 重算规则 + 密码 8 位 + 注册码 30 分钟有效 + 手动关闭

### Fixed（30 条，节选）
- PII 隐私清理：三端硬编码真实邮箱 / 手机号清除 + admin 邮箱改环境变量
- 「寮務一般教師」角色名全链路 25 处统一（简体 → 日语）
- Android 小 bug 批：静默吞异常 / 版本号 / 邮箱正则 / JSON 注入
- IX 系列 Codex 多轮收敛：令牌竞态 / 跨月计数 / 时区边界 / 改判扣分回退
- 后端 pytest 从 193 增至 220 全过

### Notes
- iOS 防代刷「三缺口」分析被 itsuki「手机不联网」架构常识推翻（ST25DV 改写架构待重设计）

---

## [0.11.30] - 2026-06-02（修订：插空补标 — ios）

> **修订号**：fix(ios): 5-30 审查 🟡 批 — 4 个安全生产 bug。commit `13f5a01`。

## [0.11.29] - 2026-06-02（修订：插空补标 — ios）

> **修订号**：fix(ios): IX-034 收敛最后一点 — 第一道令牌守卫也抛 CancellationError。commit `30032ea`。

## [0.11.28] - 2026-06-02（修订：插空补标 — ios）

> **修订号**：fix(ios): IX-034 + IX-009 Codex 第4轮收敛（令牌竞态边角）。commit `6c58799`。

## [0.11.27] - 2026-06-02（修订：插空补标 — ios）

> **修订号**：fix(ios): IX-034 第3轮 + IX-009 收敛（Codex pass3）。commit `2dff6b7`。

## [0.11.26] - 2026-06-02（修订：插空补标 — ios）

> **修订号**：fix(ios): IX-007 申请详情页生产不读 SEED（Option A）。commit `457077f`。

## [0.11.25] - 2026-06-02（修订：插空补标 — ios）

> **修订号**：fix(ios): IX-034 Codex 第2轮收敛补 2 点。commit `508c9b1`。

## [0.11.24] - 2026-06-02（修订：插空补标 — ios）

> **修订号**：fix(ios): IX-009 通知不再泄漏 SEED 假数据，生产聚合真公告。commit `7e4a180`。

## [0.11.23] - 2026-06-02（修订：插空补标 — ios）

> **修订号**：fix(ios): IX-034 Codex 收敛复审补 3 点。commit `7fecd21`。

## [0.11.22] - 2026-06-02（修订：插空补标 — ios+backend）

> **修订号**：fix(ios+backend): IX-034 收尾修 Codex 4 点（跨月计数 / loadMe 令牌竞态 / 测试时区边界 / formatYMD JST）。commit `7a9922c`。

## [0.11.21] - 2026-06-02（修订：插空补标 — backend）

> **修订号**：fix(backend): 注册码 /close 加 expires_at>now 过滤 + 改单行更新（Codex P3 + 修我引入的 TypeError）。commit `6142ef0`。

## [0.11.20] - 2026-05-31（修订：插空补标 — ix-008）

> **修订号**：fix(ix-008): 登出清当前用户 + SEED.user 复位 — 防真实用户数据残留。commit `97d0180`。

## [0.11.19] - 2026-05-31（修订：插空补标 — backend）

> **修订号**：fix(backend): rollcall 改判按 Codex 5.5 审查修 2 真问题 + 补回归测试 — 205 passed。commit `3059fe8`。

## [0.11.18] - 2026-05-31（修订：插空补标 — ix-004）

> **修订号**：fix(ix-004): codex 阶段4 复审修 2 条 — flight 时间归一化 + 修改理由后端必填。commit `5b97b45`。

## [0.11.17] - 2026-05-31（修订：插空补标 — backend）

> **修订号**：fix(backend): findings 后端纯代码批 11 条修复 — 全量 pytest 199 passed。commit `68a619f`。

## [0.11.16] - 2026-05-31（修订：插空补标 — ix-004）

> **修订号**：fix(ix-004): codex 阶段3 审查修 3 条 — 修改届防滥用 + audit 越权 + 空白绕过。commit `0ee5546`。

## [0.11.15] - 2026-05-31（修订：插空补标 — ix-004）

> **修订号**：fix(ix-004): codex 阶段2 剩余 5 条收口 — 修改届接后端完善。commit `5a8be64`。

## [0.11.14] - 2026-05-31（修订：插空补标 — backend）

> **修订号**：fix(backend): WS 寮过滤漏推 dorm_unit=2 给男寮老师 — rollcall-02/03 修对（Codex 5.5 发现）。commit `2e4bd43`。

## [0.11.13] - 2026-05-31（修订：插空补标 — ios）

> **修订号**：fix(ios): codex 阶段2(IX-004) 审查修 2 条。commit `6cca9fc`。

## [0.11.12] - 2026-05-31（修订：插空补标 — ios）

> **修订号**：fix(ios): IX-004 修改届接后端(加载+提交)。commit `40d9d59`。

## [0.11.11] - 2026-05-31（修订：插空补标 — backend）

> **修订号**：fix(backend): TeacherCreateIn email 改 EmailStr — models-entry-09（后端批漏提交补上）。commit `7e13365`。

## [0.11.10] - 2026-05-31（修订：插空补标 — backend）

> **修订号**：fix(backend): 补回 main.py 漏的 import asyncio — 修复 8b1d1da 启动崩溃。commit `9fa41a9`。

## [0.11.9] - 2026-05-31（修订：插空补标 — android）

> **修订号**：fix(android): FeedbackScreen 连点防空提交 — 快照改早返回（Codex 5.5 审查反馈）。commit `5aca68b`。

## [0.11.8] - 2026-05-31（修订：插空补标 — backend）

> **修订号**：fix(backend): Codex 后端批审查反馈修正 — pytest 193 全过。commit `8b1d1da`。

## [0.11.7] - 2026-05-31（修订：插空补标 — android）

> **修订号**：fix(android): FeedbackScreen 提交竞态 — 协程前快照值（Codex 5.5 审查反馈）。commit `2e07d58`。

## [0.11.6] - 2026-05-31（修订：插空补标 — backend）

> **修订号**：fix(backend): findings 后端小 bug 批 4 条 — pytest 193 全过。commit `1e12fa2`。

## [0.11.5] - 2026-05-31（修订：插空补标 — ios）

> **修订号**：fix(ios): codex 阶段1审查修复 4 处。commit `e2a0355`。

## [0.11.4] - 2026-05-31（修订：插空补标 — android）

> **修订号**：fix(android): 小 bug 批 — 静默吞异常/版本号/邮箱正则/JSON 注入。commit `c19a5d7`。

## [0.11.3] - 2026-05-31（修订：插空补标 — seed）

> **修订号**：fix(seed): admin 邮箱改环境变量 ADMIN_EMAIL — 修正隐私清理误伤。commit `017e121`。

## [0.11.2] - 2026-05-31（修订：插空补标 — pii）

> **修订号**：fix(pii): 清三端硬编码的真实邮箱/手机号 — 隐私泄露。commit `96eb249`。

## [0.11.1] - 2026-05-31（修订：插空补标 — role）

> **修订号**：fix(role): 「寮務一般教师」简体师→日语師 — 全链路 25 处统一。commit `9a15aba`。

## [0.11.0] - 2026-05-30（teacher_web v1.0 完整施工 — 6 大模块）

> **为什么次版本号**：8 个 feat 是老师网页 6 大模块从零建（每个含后端建表 + 迁移 + 接口 + 网页 UI）。对应 commit 段 5-29 ~ 5-30（30 commit，12 fix 是同期收敛），末端 `9f3e336`。

### Added（新功能）
- 学生账号管理（后端 + 网页，W5）
- 6 大模块：行事予定 / 巴士时刻表 / 指導履歴 / 事案录入 / 学生个人档案聚合 / 学号一括进级
- push 推送通知后端骨架
- 网页前端 FE1-FE4：上述模块 UI + ROSTER 假名单全重接真后端

### Changed
- W6 删 demo 脚手架 + 生产 API 配置 + seed 密钥 fail-fast + 启动环境守卫

### Fixed
- W8 修复批 + Codex 4 轮复审收敛（含寮边界 R4 系统性补齐 / StaticFiles import blocker）
- 全项目审查 175 条 findings 落地

### Notes
- 新建项目心智模型 skill（AI 开局必读骨架）+ session-coord 自动化 + Dependabot

---

## [0.10.12] - 2026-05-30（修订：插空补标 — backend）

> **修订号**：fix(backend): v1.0 W8 codex 第4轮 — 系统性补齐寮边界(R4)。commit `57ce922`。

## [0.10.11] - 2026-05-30（修订：插空补标 — backend）

> **修订号**：fix(backend): v1.0 W8 codex 第3轮修复 — 2 个收敛阻塞。commit `74eaf47`。

## [0.10.10] - 2026-05-30（修订：插空补标 — backend）

> **修订号**：fix(backend): v1.0 W8 codex 第2轮修复 — 3 个收敛阻塞。commit `9c2fbab`。

## [0.10.9] - 2026-05-30（修订：插空补标 — teacher_web）

> **修订号**：fix(teacher_web): v1.0 W8 codex 前端修复 — 假帖/UUID校验/删敏感假数据。commit `7de2503`。

## [0.10.8] - 2026-05-30（修订：插空补标 — backend）

> **修订号**：fix(backend): v1.0 W8 codex 复审修复 — 含 StaticFiles import blocker。commit `75d6f03`。

## [0.10.7] - 2026-05-30（修订：插空补标 — backend）

> **修订号**：fix(backend): v1.0 W8 修复 B8 — 寮边界校验(R4)。commit `8899bbf`。

## [0.10.6] - 2026-05-30（修订：插空补标 — teacher_web）

> **修订号**：fix(teacher_web): v1.0 W8 前端修复 A1+A5 — teacher.role + dorm_unit。commit `a32084c`。

## [0.10.5] - 2026-05-30（修订：插空补标 — audit-2026-05-30）

> **修订号**：fix(audit-2026-05-30): 全项目审查修复 — iOS 安全 2 处 + 后端日期校验 + gitignore + 文档死链。commit `6cc5c07`。

## [0.10.4] - 2026-05-30（修订：插空补标 — backend）

> **修订号**：fix(backend): v1.0 W8 修复第3批 — 生产部署配置。commit `d4a9108`。

## [0.10.3] - 2026-05-30（修订：插空补标 — backend）

> **修订号**：fix(backend): v1.0 W8 修复第2批 — 后端安全加固。commit `e56684d`。

## [0.10.2] - 2026-05-30（修订：插空补标 — backend）

> **修订号**：fix(backend): v1.0 W8 修复第1批 — W7 新模块 bug。commit `0e72e09`。

## [0.10.1] - 2026-05-30（修订：插空补标 — teacher_web）

> **修订号**：fix(teacher_web): v1.0 上线施工 W1-W3 — 修后端 7 bug + 三边对齐 + 网页接后端。commit `d9e65f1`。

## [0.10.0] - 2026-05-28（宿舍申请表全链路 + iOS 申請界面 + 点呼机硬件定稿）

> **为什么次版本号**：2 个 feat 但都是大块新功能——申请表后端全链路 + iOS 6 个申請界面同时落地。对应 commit 段 5-28（20 commit），末端 `afaec36`。

### Added（新功能）
- 后端宿舍申请表 5-28 规范实装：出寮届補完 + 校長审批链 + 5 张新表（study_online / dorm_event / schedule / fridge / item）+ alembic d2e3f4a5b6c7
- iOS 6 个申請界面：在线学习 / 行事企画 / 冷蔵庫 / 物品所持 等 + 校長链修 + demo / 正式版分离

### Changed
- 点呼机日本本地选型回填 hardware_design + 采购清单 HTML + 接线文档
- web 登录账号砍到 1 个（新股 / 寮務部長）+ seed 教师数 9 → 1

### Notes
- ST25DV「116 天磨穿」被 itsuki 常识推翻（点呼非全天刷，伪问题留痕）

---

## [0.9.5] - 2026-05-28（修订：插空补标 — ios）

> **修订号**：fix(ios): demo 注册房间号默认 A5 + 修房间号双前缀。commit `6d945df`。

## [0.9.4] - 2026-05-28（修订：插空补标 — seed）

> **修订号**：fix(seed): 注释教师数 9→1 + today_jst 改用 ZoneInfo Asia/Tokyo（codex 审查修）。commit `344b550`。

## [0.9.3] - 2026-05-28（修订：插空补标 — web+seed）

> **修订号**：fix(web+seed): 登录页账号砍到 1 个(新股/寮務部長) + 返回按钮改为显眼样式。commit `01d0654`。

## [0.9.2] - 2026-05-28（修订：插空补标 — ios）

> **修订号**：fix(ios): 注册页 demo 默认空 + 送后端转数字码修真 bug + 设计文档部分中文化。commit `0ccd19d`。

## [0.9.1] - 2026-05-28（修订：插空补标 — ios）

> **修订号**：fix(ios): TODO §D 2 处 catch 修 + StayDetail 切真 API + codex 审查全装 6 项。commit `7f579c1`。

## [0.9.0] - 2026-05-27（teacher_web 老师网页 v1.0 真接口全实装）

> **为什么次版本号**：38 个 feat 压倒性新功能——老师网页从「纯 UI / 0 真接口」做到「全接后端」。对应 commit 段 5-26 ~ 5-27（75 commit），末端 `aba0659`。

### Added（新功能）
- 老师网页 Task #6 点呼全流程接后端（start / end / board / WebSocket 实时事件）
- 申请审批 / 学習出席页 /study / 公告 / 学生登録码面板 / 役职別 home 重定向
- 实名账户登录改造（取代共用密码）+ 教师创建 / 删除管理页
- 后端：DemeritEvent / Cleaning / FrontDesk model + router + alembic c1d2e3f4 三张新表
- 后端：WebSocket /ws/teacher 4 处 broadcast + 自动扣分（spec §7.5）+ 改判扣分联动（§11.4）

### Changed
- JWT 改 sessionStorage + 401 全局拦截自动 logout + LIVE/DEMO 状态指示器

### Fixed
- FC-024 删 index.html 明文密码 12345678，接真实认证
- codex 5.5 xhigh 审查修 3 个阻塞（timedelta import / 越权 / 最后一个 admin lockout）

### Notes
- 新建 dmsd-startup skill + 重写 DMSD CLAUDE.md（247 → 190 行）

---

## [0.8.8] - 2026-05-27（修订：插空补标 — audit）

> **修订号**：fix(audit): codex 5.5 xhigh 审查修 — 3 🔴 + 关键 🟡/🟢 全修 + 剩余加 TODO。commit `aba0659`。

## [0.8.7] - 2026-05-27（修订：插空补标 — ios）

> **修订号**：fix(ios): TODO §D 2 条工程债务修复 — StayList 假数据降级 + MyPage localizedDescription 暴露。commit `92d8408`。

## [0.8.6] - 2026-05-27（修订：插空补标 — backend）

> **修订号**：fix(backend): models.py 补 Float import — 修 DemeritEvent NameError。commit `b4d40d6`。

## [0.8.5] - 2026-05-27（修订：插空补标 — backend）

> **修订号**：fix(backend): cleaning + discipline 补 dorm_units_for_teacher import。commit `ddf3880`。

## [0.8.4] - 2026-05-27（修订：插空补标 — backend）

> **修订号**：fix(backend): FC-027 announcements 权限改造 — 老师 token 能调 list/detail。commit `46a1014`。

## [0.8.3] - 2026-05-26（修订：插空补标 — teacher_web）

> **修订号**：fix(teacher_web): FC-024 删 index.html 明文密码 12345678 + 接 backend 真实认证。commit `b0bed26`。

## [0.8.2] - 2026-05-24（iOS 上架版融合 + 安全审查修复）

> **为什么修订号**：3 个 feat 是 iOS 上架准备性质（融合上架 fork + 网络层基建 + 删后门），无面向用户的产品大功能。对应 commit 段 5-22 ~ 5-24（15 commit），末端 `6a1b4aa`。

### Added
- iOS App Store 上架版 fork backport 回主项目 v1
- 新建 RollCallAPI 网络层 + swiftformat 整理

### Fixed
- 删 demo scaffold 与 magic value "000000" 注册后门（A-024 / 030 / 033 / 035 / 038）
- NetworkModels 字段对齐 backend（FC-020 / 021）+ spec 死链修复（FC-017）
- Fix-Bot effective_* 多端同步 + Codex 第二轮 audit 修 5 处 FC-*

### 死区注记（2026-06-11 插空细分）
- v0.8.1 与本段之间号位被占，期间 4 个 fix 无法补打独立补丁标签，逐条列此：
  - `3f65331` 05-22 fix(backend+spec+android+web+rollcall_device): Fix-Bot 4 effective_* + 多端同步
  - `f2a6730` 05-24 fix(ios): FC-020/021 NetworkModels 字段对齐 backend
  - `5681584` 05-24 fix(spec): FC-017 RollCall_Spec 修旧 /api/v1/checkin 死链 endpoint
  - `e1a4d51` 05-24 fix(spec): FC-017 API_CONVENTIONS 同步真实 endpoint 路径

---

## [0.8.1] - 2026-05-16（开发支撑体系 + 沟通规则 + 文档治理）

> **为什么修订号**：5 个 feat 全是开发工具链 / 协作机制（不是 Tomoshibi 产品功能），产品 5 端代码未动。对应 commit 段 5-11 ~ 5-16（23 commit），末端 `8e35338`。

### Added
- graphify 知识图谱全套上线
- cc-comm-rules 沟通规则 skill + 3 hook
- anti-ai-flavor 反 AI 味 skill 立项
- project-overview 同步 hook + session-wrap 收尾自查清单

### Changed
- destructive bash hook 从 block 改 warn（不阻断，只提醒）

### Fixed
- 5-12 深度审查发现的 spec 死链 + 致命缺口修复

### 死区注记（2026-06-11 插空细分）
- v0.8.0 与本段之间号位被占，期间 7 个 fix 无法补打独立补丁标签，逐条列此：
  - `af257d9` 05-03 fix(icons): 启动屏火焰也换成 clean 版（漏掉的资产）
  - `65bbc3c` 05-03 fix(ios): RegisterStep5 加 demo bypass — backend 没开时也能进 App
  - `f034075` 05-03 fix(meta): 5-03 收尾 — 协作模型规则跟齐治理 commit
  - `d27fe41` 05-04 fix(skill): 删除「未完全理解明标」机制 — itsuki 拒绝自我贬低进 git
  - `5e2e29e` 05-04 fix(skill): 主要工作模式从「关键词触发」换成「收尾全量扫描」
  - `e05a451` 05-04 fix(ios): 5 Stubs 重做 — 删 9 处 placeholder + iOS 26 Text 插值 + 暗夜强制 light
  - `859693e` 05-13 fix(specs+hooks+skill): 5-12 深度审查发现的死链 + 致命缺口修复

---

## [0.8.0] - 2026-05-02 晚（5 端代码层全启动 — Android bootstrap + iOS 网络层 + teacher_web v1 + backend 全功能 routers + iOS↔backend 字段对齐 + 点呼机骨架）

> **为什么 minor bump**（对照版本管理 SOP §2 决策树）：本版本是 v0.7.0「设计 → brief」全闭环之后第一个进入「**brief → 实装代码**」阶段的里程碑。31 commit 累积横跨 5 端：
> - **#4 03_dev/ 大幅扩展**（强命中）→
>   - **Android**：从零搭建 Compose 工程（commit `889d65c` Round 1 prompt + `536abce` bootstrap）— `03_dev/student_android/v1/compose-drafts/` 新建 21 个 .kt 文件 + 10 屏 UI（Login/Home/Apply/MyPage/Schedule/Bus/Study/Music/Notifications/NfcScreen 等）+ MainActivity / NavGraph / AppStore / MockData / Theme + ANDROID_DESIGN_LOG.md 新建
>   - **iOS 网络层**：`Foundation/Network/` 完整建设（commit `a992b4f` `624fea1` `cf5c9fa` `d698148` `b8b2f50` `2c2c34f` `0ffa68f` `0c3ff96` `5c8cf9f` 9 commit）— NetworkModels.swift（6 Codable struct）+ Endpoints/ 4 module + KeychainService（JWT 持久化）+ APIClient 错误解码修正 + AppStore 切真 API（login + applications submit/list/detail/update + study absence-requests）
>   - **iOS↔backend 字段对齐**（commit `4be8121` + `40f82ee`）— F1-F5+Q1 7 处失配修复（kind 日文映射 / stay_locations 对象数组 / meals_skip 形状 / 砍 student_id / 加 reason 字段 / status 加 returned）+ Alembic migration `b2c3d4e5f6a7`
>   - **iOS 学生侧完全体**（commit `747a179` `512424d`）— P0×3（Music 入口加 LifeTab / 出寮届修改届完整表单 + audit log 履歴 tab + chain 重置 / 学習 NFC 3 次碰）+ P1×2（マイページ MyInfoEdit 修订 spec §6 / 注册留学生 chip + 锁定升级 30s→1m→5m→30m→1h→永久）+ P2×1（push listener mock 4 trigger）+ ⭐⭐ リクエスト曲投诉系统拍板（5/10/15 自动封禁）→ system_features §7.11.2 落地
>   - **iOS UI 调整 6 件**（commit `c720065`）— Auth/Home/Apply/MyPage UI 调整 + AppStore + BottomNav + BUILD.md
>   - **teacher_web v1 启动**（commit `98315f1`）— TS + Vite + Zustand 升级 + 5 page 起手 + 旧 jsx 归档 _legacy/
>   - **teacher_web demo 接真后端**（commit `bd39760`）— demo_server.py 加 /api/v1/ 代理 + JWT 真实认证 + 学習管理全屏会话（StudyLanding + LiveStudySession + 3-tap NFC + 相位条 + デモコンソール）
>   - **backend 全功能 routers**（commit `151d863`）— rollcall.py + study.py + teachers.py 新建 + models 扩展 + Alembic 框架建立
> - **#5 改了 CLAUDE.md 元规则**（命中）→
>   - 加设计文档双层结构规则（commit `4687611`）
>   - §对话规则 §7 加强 — 主动诊断 unknown unknowns 话术模板（commit `3891f3c`）
>
> **31 commit 跨 v0.7.0 → v0.8.0**（5-01 → 5-02）：详见下方 Added / Changed / Notes 分类。
>
> **特殊里程碑**：v0.8.0 是项目第一次「三端 app + 后端 + 文档 五条线同时推进」的版本（5-08 后加点呼机层成 5 端 monorepo）。v0.7.0 把「老师 38 条」消化成 brief，v0.8.0 开始把这些 brief 写成代码。

### Added — 三端代码层全启动

**Android（从零搭建）**：
- `03_dev/student_android/v1/compose-drafts/` 工程框架（21 个 .kt 文件）
- 10 屏 Compose UI：Login / Home / Apply / MyPage / Settings / Schedule / Bus / Study / Music / Notifications / NfcScreen / Account / ApplicationDetail / Deduction / Delivery / Feedback / LostFound 等
- AppStore（全局状态）+ NavGraph + Routes + MockData + 共通组件（BottomTabs / SuzuIcons）
- ANDROID_DESIGN_LOG.md 新建 + SETUP_INSTRUCTIONS.md
- 实装方针拍板：CC 主导逐屏对译 Compose（不派 sub agent）

**iOS 网络层**（`03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/`）：
- `NetworkModels.swift` — StudentBrief / ApprovalStepOut / ApplicationOut / AuditLogOut / StudyAbsenceRequestOut / AnyJSON（跟 backend Pydantic byte-perfect 对齐）
- `Endpoints/AuthAPI.swift` — loginStudent
- `Endpoints/ApplicationsAPI.swift` — create / listMine / detail / update / audit
- `Endpoints/ApplicationsCreateBodies.swift` — KisheiCreateBody / GaihakuCreateBody / KikokuCreateBody / StayLocationBody / MealSkipBody / ApplicationUpdateBody（discriminated union 3 typed body）
- `Endpoints/StudyAPI.swift` — submitAbsenceRequest
- `KeychainService.swift` — JWT 持久化 wrapper（save/load/delete、kSecAttrAccessibleAfterFirstUnlock）

**iOS 学生侧完全体**（`Features/`）：
- 出寮届修改届完整表单 + audit log 履歴 tab + chain 重置流程
- 学習 NFC 3 次碰 + マイページ 学習履歴
- マイページ MyInfoEdit 学号/姓名 read-only / 邮箱/电话/房间号可改
- 注册流程：留学生 chip + 锁定升级 6 段（30s→1m→5m→30m→1h→永久）
- push listener mock 4 trigger（学習批 / 学習拒 / 名单加入 / 修改届再批）
- リクエスト曲投诉系统（SongReportSheet 4 理由 + 投诉 button + 投稿封禁 banner）

**backend 全功能 routers**（`03_dev/backend/v1/app/routers/`）：
- `rollcall.py` — 7 endpoint（today/sessions / sessions/start / end / checkins / board / summary / events PATCH）
- `study.py` — 8 endpoint（today/attendees / checkins / bulk-finalize / checkins PATCH / absence-requests POST / GET / decision / cancel-today）
- `teachers.py` — 4 endpoint（invitations / register / list / me）
- Alembic 框架建立 + migration `b2c3d4e5f6a7`（meals_skip 形状改 + reason 加 + status 加 returned）

**teacher_web v1**（`03_dev/teacher_web/v1/`）：
- TS + Vite + Zustand 升级（替代旧 React + JSX 单文件 demo 模式）
- 5 page 起手（spec D 范围）
- 旧 jsx 归档到 `_legacy/`

**teacher_web demo 接真后端**（`03_dev/teacher_web/demo/`）：
- demo_server.py 加 `/api/v1/` urllib 反向代理
- 登录改 JWT 真实认证（POST /sessions/teacher）
- 学習管理全屏会话（StudyLanding + LiveStudySession + 3-tap NFC + 相位条 + デモコンソール）
- backend 加 TeacherTokenOut schema + seed.py 补 StudyRoster + 今日 RollCallSession

### Changed — iOS↔backend 字段对齐 F1-F5+Q1

**backend 改动**（commit `4be8121` + `40f82ee`）：
- `Application.reason` 列追加（F5）
- `meals_skip_from/to` 削除 → `meals_skip JSON [{date,meal}]` 追加（F3）
- status CHECK 加 `returned`（Q1）
- Alembic migration `b2c3d4e5f6a7` 实行 + DB 更新确认
- `meals.py` range 判定 → entry 直接 lookup 重写
- `meals_skip JSON serialize` 修复（commit `40f82ee`）

**iOS 改动**（commit `4be8121`）：
- `APIClient` / `APIError` 新建（F7 基盘）
- `ApplyKindMapper` 新建（stay↔外泊 等 4 桁日文映射）
- `StayForm.submit()` 砍 student_id（F4）
- `stay_locations` 改 [{kind,name}] 对象数组（F2）
- `meals_skip` 改 [{date,meal}] 列表 + `expandMealsSkip` helper（F3）
- `AppStore.authToken` 加（APIClient 同期）
- `ApplicationStatus.cancelled` → `withdrawn` 统一（Q1）
- `approved_partial` enum case 追加（5-02 commit `d698148`、补漏 backend 6 値）

**iOS 切真 API**（5-02、本会话 commit `b8b2f50` `2c2c34f` `0ffa68f`）：
- `LoginView.tryLogin` async + AuthAPI.loginStudent 接続 + 401 走锁定升级
- `StayForm.submit` 按 kind dispatch 到 3 typed body + ApplicationsAPI.create
- `AppStore.submitStudyLeave` async throws + StudyAPI.submitAbsenceRequest
- `StayListView/Detail/Edit` 全切真 API + .task { await load() } pattern + .refreshable 下拉刷新
- 加 ApplicationOut.toStayApplication() converter + AuditLogOut.toAuditLogEntry() converter

**APIClient 错误解码修正**（commit `a992b4f`）：
- `DetailError.detail: String` → `DetailError.extractMessage(from:)` 双形态解码
- 修复 `{"detail":{"code","message"}}` ネスト形态被 fallback 失精度的 bug

### Fixed

- iOS 学習欠席届 mock 计数器在 backend 失败时也 +1 → 改成成功后才更新（commit `2c2c34f`）
- iOS submit() 各错误未分类 → 加 401/422/network/其他 4 类 catch（多 commit）
- IOS_DESIGN_LOG.md 文件头时间戳 4-22 → 5-02 同步（commit `5c8cf9f`）

### Notes — 元规则升级

**CLAUDE.md 改动**：
- §设计文档双层结构规则新建（commit `4687611`）— 共用层 / iOS+Web+後端専属层 4 層分層 + 改的順序（共用層先改→専属層引用）+ 反模式拦截
- §对话规则 §7 加强（commit `3891f3c`）— 主动诊断 unknown unknowns（覆盖技术 / AC / 学习 / 自我管理 4 类、话术「你现在做的是 X、业界标准是 Y、原因是 Z」、强度 B-C、禁用「良好实践」抽象话术）

**memory 更新**：
- `feedback_proactive_diagnose_unknown_unknowns.md` 新建（详细版 4 类覆盖 / 强度分档 / 正反例 ❌✅ / 反模式 5 条）
- MEMORY.md ⚡ FOUNDATIONAL RULE 块加索引

**核心 AC 金句**（raw/2026-05-02 §4 ⭐）：「提醒我学习扩展我的思维这个很重要」 — itsuki 在七问澄清中说出，对应自我推荐书「AI と協働姿勢」+ 面试问题 #4「学到了什么」。

**31 commit 归入本版本**：
- `889d65c` Android Round 1 prompt 落盘
- `536abce` Android bootstrap Compose 工程框架 + 10 屏
- `c720065` iOS Auth/Home/Apply/MyPage UI 调整
- `747a179` iOS 学生侧完全体（P0×3 + P1×2 + P2×1 + 反馈 6 件 + 投诉系统拍板）
- `512424d` 4-30 後續 决策落地（学習 NFC 化 + 出寮届修改届 + 教师权限）
- `0aeaae9` 三端对齐审计 dump + 失配清单 F1-F15 + 方案 ABC（阻塞 Q1/Q2）
- `4687611` CLAUDE.md 加设计文档双层结构规则
- `54cb4e8` 全 repo 606 文件审查 + 状态分类
- `151d863` backend rollcall/study/teachers routers + Alembic 框架
- `98315f1` teacher_web-v1 TS+Vite+Zustand 升级
- `bd39760` teacher_web-demo 接真实后端 + 学習管理実装
- `54dd01d` backend F1-F7 + Q1-Q2 字段对齐 handoff 文档
- `4be8121` iOS↔backend 字段对齐 F1-F5/Q1/F7
- `3891f3c` CLAUDE.md §对话规则 §7 加强
- `654a731` 5-02 会话 — iOS↔backend 対齐收尾记录
- `40f82ee` backend meals_skip JSON serialize 修复
- `debcb07` 5-02 收尾 — 设备迁移前 raw 追加 + handoff 归档
- `23a5e1f` Mac mini setup checklist
- `c844bbd` 5-02 raw 目录补 §5 + §6 链接
- `a992b4f` iOS NetworkModels + APIClient 错误解码修正（本会话）
- `624fea1` iOS Endpoints/ 4 module（本会话）
- `cf5c9fa` iOS KeychainService + AppStore 永続化（本会话）
- `d698148` iOS ApplicationStatus 加 approved_partial + 注释中文化（本会话）
- `b8b2f50` iOS LoginView 切 AuthAPI（本会话）
- `2c2c34f` iOS StayForm + StudyAbsence 切真 API（本会话）
- `0ffa68f` iOS StayListView/Detail/Edit 切真 API（本会话）
- `0c3ff96` iOS 网络层会话收尾文档（本会话）
- `5c8cf9f` IOS_DESIGN_LOG 文件头时间戳同步（本会话）
- 加上 release commit + 别会话若干微调

---

## [0.7.2] - 2026-05-02（修订：插空补标 — ios）

> **修订号**：fix(ios): ApplicationStatus 加 approved_partial + 注释统一中文。commit `d698148`。

## [0.7.1] - 2026-05-02（修订：插空补标 — backend-v1）

> **修订号**：fix(backend-v1): meals_skip JSON serialize 修复 + tests 用新 schema。commit `40f82ee`。

## [0.7.0] - 2026-04-30 晚（三轨 A+B+C 同日完成 — 38 条 B 标准 baseline + §9 8 条拍板 + 实装包拆分 + 实物表 evidence 推翻）

> **为什么 minor bump**（对照版本管理 SOP §2 决策树）：本版本三轨 A+B+C 同日落地 38 条老师反馈的"设计 → 拍板 → 实装 brief"全闭环：
> - **#1 改了 spec 业务规则主体** → `02_design/system_features.md` 8 处章节修订（§3.3 寮物理关系事实记录 / §3.4 账号运用 4-30 修订 / §4.2 学号生命周期 / §5 房间号 M/A/W 编码新建 / §6 改动履历字段重分类 / §7.1+§7.10+§7.13 矩阵+通知 / §7.3 晚自习 7 tab+双视图 大扩充 / §7.2.2 外泊届承认 chain 实物表修订 / §8.1+§8.6 数据模型 + disclosure_requests 表新建 + §9 全 close + §10 改订历史 +1 行）
> - **#4 03_dev/ 大幅扩展** → `BACKEND_DESIGN_LOG.md` 新建（对称 iOS / Web 既存 LOG）+ iOS LOG §11 v1.0 实装清单 append + Web LOG §11 v1.0 实装清单 append
> - **#5 改了 CLAUDE.md 元规则** → §对话规则 第 6 条沟通规则升级（代号/日语/英文缩写第一次出现要翻译）
>
> **5 commit 归入本版本**：`604bc9b` 轨道A baseline / `4272fc7` 轨道B §9 拍板 / `f25255b` SOP §8.5 路线图 / `6f508d4` 轨道B-followup / `184c0c6` 轨道C 实装包拆分

### Added — 三轨并行机制 + 39 条 B 标准 baseline + 实装包

**轨道 A：38 条逐条状态盘点（`604bc9b`）**:
- `00_admin/TODO.md §📊 设计层覆盖度 baseline` 新建 — B 标准（UI 画过 + 字段都列了 + API 形状定了 三项全 = ✅）
- 38 条 + itsuki 补足 1 条 = 39 条 emoji 前缀逐条标注：✅ 7 / ⏳ 27 / ❌ 3（#21 老龄宿管老师 iPad UI / #28 寮务追加删除学生 / #30 教师当天代录）/ 🚫 2（#35 学生发帖 / #36 匿名建议）
- Q1-Q11 标 ✅ 完成 + Q12 标 ⚠️ 杭田 UI 矛盾保留 → 轨道 B 处理
- §🛣️ 推进路线图 — 三轨 A/B/C 总览 + 文件锁定边界 + C 内部优先级 P0-P3
- 末尾"术语小词典"（R1-R4 / Q1-Q12 / #1-#39 / D-V1-V1.1+ / system_features / RollCall_Spec）

**轨道 B：system_features §9 8 条 (a)-(h) + Q12 全 close（`4272fc7`）**:
- (a) 罚则数值 → hardcode 常量 + 不上线前确认（§7.12 注解，YAGNI 不做 admin UI）
- (b) 学号变更 → 学生 read-only / 老师 Web 全权（首次注册除外）（§4.2 + §6 + §7.1 拆 2 行 + §7.13 通知反向）
- (c) 房间号 → 个室 model + M/A/W 前缀编码（§5.0 编码规则新建：M???=1 寮男 / A?-A??=2 寮男 / W???=4 寮女 / 3 寮废止 + §5.1 backend regex 校验 + §8.1 CHECK 约束）
- (d) 指导履历 → C 案 默认不显示 + 学生申请开示（§7.10 拆 4 行 + §7.13 通知 +2 + §8.6 disclosure_requests 表新建 8 字段）
- (e) 寮監账号 → close 寮監几人 + 任意浏览器登录 + 前台禁止自助注册（§3.4 重写 "iPad 共用" → "登录设备不限定" + §7.1 +2 行：寮監账号管理 + 首个 bootstrap）
- (f) 晚自习名单 → C 案 + 7 tab + 双视图 + 学期前邮件提醒（§7.3 大扩充 UX 详细规格 + 矩阵 5 行）
- (g) 寮物理关系 → close + 事实记录（§3.3 表加列 + 1+2 寮紧邻 + 全活动合并）
- (h) + Q12 杭田 UI → close 不存在矛盾（老师允许 + itsuki 拒绝可同时成立 → §9 (h) 删除）
- §10 改订历史 +1 行

**轨道 C：实装包拆分 + 25+ 条决策（`184c0c6`）**:
- `03_dev/backend/BACKEND_DESIGN_LOG.md` **新建** — backend 専属設計 + v1.0 实装清单（对称 iOS / Web 既存 LOG）
- `03_dev/student_ios/IOS_DESIGN_LOG.md §11` **append** — v1.0 实装清单
- `03_dev/teacher_web/WEB_DESIGN_LOG.md §11` **append** — v1.0 实装清单
- 当日 25+ 决策清完：D1 SendGrid（自建 SMTP deliverability 劝退）/ D2-D9 一次过按 CC 推荐 / D11 担任单独表 `class_teacher_assignment` / D12 ENUM 加管理係 / W1 升级 TS+Vite+Zustand / I1-I10 + W2-W8 一次过
- `00_admin/文件结构指南.md` + `CLAUDE.md` 加 BACKEND_DESIGN_LOG 指针
- `00_admin/TODO.md §📦 轨道 C` section 加 evidence 缺口（帰省 / 帰国 实物表 ×4 + 担任名簿 seed）

**SOP §8.5 版本路线图（`f25255b`）**:
- 新章节 — v0.7→v0.8 后端 → v0.9 Android → v0.10 iOS+Web 升级 → v1.0 联调上线 + 关键依赖图 + 4 条风险点 + 维护规则
- 前提（itsuki 4-30 明示）：iOS / Web 前端 demo 改改可用 / Android + 后端从 0 写
- §12 Onboarding 表加 1 行：用户问"下一个版本是什么" → 读 §8.5

### Changed — `system_features.md §7.2.2` 实物表修订（⭐⭐⭐ AC 候选）

**实物表 evidence 推翻老师 LINE 文字推测**：itsuki 给 2 张实物外泊届表，CC 之前 chain 推测全推翻：
- 担任 + 管理係 必有（LINE 漏写）
- 国際交流課長 在外泊届 chain 上不出现（**注**：役职存在，但外泊届实物表上无印欄；帰国届等他届可能仍涉及。教训：「印欄不存在」≠「役职不存在」— `6914e72` 補正）
- 一般外泊 = 3 人（CC 推 2 人）
- 留学生外泊 = 5 人（CC 推 4 人）
- → §7.2.2 修订 + backend D4 ✅ + I11 / W9 实装 brief 调整

→ AC 候选：信息源选择 lesson — chat 文字 vs 物理事实（raw §7.2 ⭐⭐⭐）

### Notes — 沟通规则 #6 + 多会话治理升级

- **CLAUDE.md §对话规则 第 6 条新增**（`604bc9b`）：项目内部代号（R1-R4 / Q1-Q12 / G2 / Phase / Tier / #1-#39 等）/ 日语词（寮監 / 寮務 / 一本道 / 帰省 等）/ 英文缩写（UX / API / NFC 等）第一次出现都要给中文意思 / 全名展开 / 大白话解释。对话和文档都适用。memory `feedback_explain_terms_to_itsuki.md` 详细规则 + 术语对照表。
  - itsuki 原话："我需要你用我可以看懂的语言跟我对话给我介绍" + "看你说的话很费脑子"
- **CC mistake list 自审**：(1) baseline 第一版用错标准（CC 自定义"列入 system_features.md = ✅" → ✅ 34/39，被 itsuki 推翻 → B 标准重做 → ✅ 7/39）(2) #21 老龄一本道 UX 一句话堆 4 个术语没翻译 (3) 起手按字面新建 3 REQUIREMENTS.md 违反单源真值原则（轨道 C） — 三处 mistake 都被 itsuki 当场纠正
- **多会话治理实战验证**：A → `00_admin/TODO.md` / B → `02_design/system_features.md §9` / C → `03_dev/{backend,iOS,Web}/REQUIREMENTS.md`（后改名 LOG append） — 三方文件主写区不重合，5 commit 0 冲突
- **#21 老龄宿管老师 iPad UI / #30 教师当天代录** 仍 ❌ baseline — B/C 范围外，留 v0.7.x patch 单议题处理
- **AC §6-§8 候选 dump**（`raw/2026-04-30.md`）：§6 § 符号偏好 ⭐⭐ / §7.2 实物表 evidence 推翻 ⭐⭐⭐ / §8 Apple Developer 年费购入 ⭐⭐

---

## [0.6.2] - 2026-04-30（修订：插空补标 — v0.7.0-docs）

> **修订号**：fix(v0.7.0-docs): 国際交流課長 描述同步 itsuki 補正 6914e72 — 「印欄不存在」≠「役职不存在」。commit `e669642`。

## [0.6.1] - 2026-04-30（修订：插空补标 — approval-chain）

> **修订号**：fix(approval-chain): 国際交流課長 役职保留 — itsuki 補正。commit `6914e72`。

## [0.6.0] - 2026-04-29 晚（老师 4-29 LINE 38 条受领 + spec 主体修订 + 设计大重写 + demo/v1 分离）

> **为什么 minor bump**（对照版本管理 SOP §2 决策树）：本版本完成 4-28 demo 通过老师认可后的全套响应：
> - **#1 改了 spec 业务规则主体** → RollCall_Spec.md 5 处时序修订（§4.2 老师时刻表 + §5.2 流程 + §5.4 窗口固定不平移 + §5.5 自动开始时点 + §5.6 「点呼総結」中层页 + 附录 A.4 close）
> - **#3 改了 02_design 设计文档** → system_features.md 357 → 830 行 大重写（中文骨架 + R1-R4 硬约束 + 14 子节功能矩阵）
> - **#4 03_dev/ 大幅重组** → backend/teacher_web/student_ios 各自分 demo/v1，210+ 文件 rename
>
> **2 commit 归入本版本**：`0d1da76`（cleanup checkpoint — 4-29 19:45 itsuki 自做）+ 本 release commit（4-29 晚）

### Added — 4-28 demo 后的需求收纳 + 长期治理基建

**老师需求受领 + 整理**（`00_admin/TODO.md` + `02_design/system_features.md` + APPENDIX A）:
- 老师 4-29 LINE 38 条产品要件 + 1 条订正（通知 = 邮件）
- itsuki 4 条砍/留（学生发帖/社区/匿名 砍 + 音乐 留）
- 12 个待问 Q（Q1-Q12 已答其中关键 11 个）
- 4 条硬约束 R1-R4（邮件 / 一本道 / 教师单独账号 / 1·2 寮 vs 4 寮 分别）

**RollCall_Spec.md 时序规则全面修订**（5 处）:
- §4.2 老师侧时刻表 — 加列"应开始(-5min)"+"兜底自动开启(-3min)"+ 注明"未签到不自动变黄"
- §5.2 流程 — 从 3 步扩到 5 步，明确"老师按结束 → 跳总结页"
- §5.4 老师手动开始 — **改写**：推翻原"窗口平移"规则 → 窗口固定 + 边界 4 行表
- §5.5 自动开始 — 时点从 `window_start` 改到 `on_time_end - 3min`
- §5.6 「点呼総結」中层页 — **新增**：4 区块（缺席 / 迟到 / 特殊要求 / 外宿自动跳过）+ "回主页"按钮 + 主页保留入口
- 附录 A.4 ✅ CLOSED

**system_features.md 中文骨架大重写**（357 → 830 行）:
- 文档头删掉文件级 v0.x 版本号（违反单源真值原则，git 是单源）
- §2 必读硬约束 R1-R4 顶部新章
- §3 5 角色体系 + 设备分布（職員室 / 事務室 / 寮管室 iPad / 食堂 iPad）
- §7 功能矩阵 14 子节覆盖老师 38 条（出寮届 / 学習 / 点呼 / 行事 / 巴士 / 食堂 / 出寮者一覧 / 指导履历 / 个人数据 / 砍掉功能 等）
- §8 数据模型扩充（applications / study / events / bus / meals / teachers + R4 一致性 CHECK）
- APPENDIX A 老师 LINE 原文（evidence 保留日语原文）

### Changed — 03_dev demo/v1 分离

- `03_dev/backend/` → `backend/{demo,v1}/`（10 文件挪到 demo/，新建顶层 README + v1/README 占位）
- `03_dev/teacher_web/round3/` → `teacher_web/demo/`（157 文件整体 rename + 新建 v1/README 占位）
- `03_dev/student_ios/designs/` → `student_ios/demo/`（4 文件 rename + 新建 v1/README 指向 ~/dev/TomoshibiiOSApp/）
- `bin/sync-ios-refs.sh` 路径修正 designs → demo
- `03_dev/LATEST.md` + `00_admin/文件结构指南.md` 同步反映新路径

### Notes — itsuki 拍板的治理决策

- **demo 锁定不动 / 正式版从 demo 复制需要的部分**（4-29 拍板）→ 防止 demo 临时性代码污染长期维护
- **三层档案分层**（共用真值 system_features / iOS 専属 LOG / Web 専属 LOG）
- **CC 触发清单加一条**「档案体系 / 文件管理规范 元思考」→ 让 CC 主动识别同类元决策（CLAUDE.md + CLAUDE_CODE_记录指南.md 同步加）
- **AC §13 ⭐⭐⭐ 长期治理思维**（~2000 字方法论级 dump in `05_logs/raw/2026-04-29.md`）

---

## [0.5.1] - 2026-04-29（修订：插空补标）

> **修订号**：fix: 恢复误删的 02_design/teacher_requirements.md。commit `dda3541`。

## [0.5.0] - 2026-04-29（Demo 4-28 sprint 落地 + 跨会话同步机制 + 学号 6 桁体系）

> **为什么 minor bump**（对照版本管理 SOP §2 决策树）：本版本完成 demo-4-28 sprint 全套（D1-D2-D3 + demo-day fix + web 收尾），属于 03_dev/ prototype 大幅扩展（条件 4 minor 触发）+ 学号 6 桁体系是业务规则改动（条件 1 minor 触发）+ 跨会话同步规则 A+B+C 是新决策机制（条件 5 patch 触发，叠加上面 = minor）。
>
> **6 commit 归入本版本**：`d517cef` / `78aa611` / `57bc394` / `da959ef` / `0c8362c` / `9aedd36`（4-22 18:31 → 4-29 13:06）。
>
> **首次执行版本管理 SOP** — 本版本 close 是 SOP 建立后的第一次实践，CHANGELOG / WIP 头部 / 版本演变一览 / vX.Y.Z_AC叙事 / raw 当日 dump / git tag 6 处联动同步。

### Added — Demo 4-28 sprint 全面落地

**Web Round 3 完整 prototype**（`03_dev/teacher_web/round3/`）:
- 12 组件 + 3 vendor + 130 字体（base64 inline）+ 32 MB single-file U 盘版
- 学生アカウント管理页面（`accounts.jsx` + ACCOUNTS seed 24 人 + Shell nav + modal 2 tab）
- login / dashboard / live 座席表 / override modal / roll-call landing
- カレンダー仿 iOS（月グリッド + 选择日列表 + ＋追加 modal 复用 ModalShell）
- リクエスト曲管理（男女寮分け + 提出順 + 承認/拒否 workflow + #番号 寮×朝/晩 4 組合別自動採番）
- 主页ショートカット URL 自动检测 LAN IP（demo_server.py /api/server-info + manual fallback）
- 男寮新教员（新股 / 小林 / 難波 + 姓后先生统一）+ applications.jsx 承認 workflow

**iOS Round 1 落盘**（`03_dev/student_ios/`）:
- `IOS_DESIGN_LOG.md`（303 行，决策归档）+ `Round1_Prompt.md`（878 行，73 画面 Phase A+B 一次出）+ 4 参考图
- 3 按钮 nav + Home omnibus + 中央点呼 sheet（iOS 26 Liquid Glass）+ 注册 4-step + 锁定升级 5 阶段 + 长按 breadcrumb
- Phase B v2 HTML（Tomoshibi_iOS_PhaseB_v2.html，QA 修 C1+C2）
- 推翻 Xcode 壳方案 → Demo 当天 Safari 直开（itsuki 拍板，CC 30 行 SwiftUI 工程废弃）

**学号 6 桁体系**（D3 拍板）:
- 学年 × 組 × 番号、中高一貫 6 年制、A=01/B=02
- リュウ イヒ demo seed: 00 → **060218**（高3 B 18）
- DEMO_SEED_NO=060218 单源 + sid-based 判定 + accounts.jsx 番号列 70→130px

**跨会话同步机制 A+B+C**（D3 建立）:
- `02_design/system_features.md` 新建 = iOS+Web+後端共用真值（"単一真値"）
- `bin/sync-ios-refs.sh` 建立（DMSD → Tomoshibi-iOS/refs/ 物理コピー）
- CLAUDE.md §跨 repo 同步规则（明文 ルール）
- 解决问题：Tomoshibi iOS Swift 实装在独立 repo（cloud agent 取不到 DMSD），需物理 copy

**点呼机软件代替方案**（4-22 砍 Pi 后）:
- `demo_server.py` + polling TTS（iPad Safari Web Speech API 日语播报 / fallback Mac `say -v Kyoko`）
- iPhone Shortcuts + itsuki 自有 NFC 卡触发签到
- `./tomoshibi` CLI 启动整套

**学生改动履歴（监查 log）规格**（D3）:
- 学号 / 房间号 / 邮箱 / 电话 / 密码事实全记录
- 老师 Web アクティビティ履歴 tab + 学生 App 変更履歴

**房间号管理**（D3）:
- 注册时学生手入力 + v1.1 老师 Web 一括分配 drag & drop + 学生 App 自動受信

**コミュニティ 拆分**（D3）:
- 通報保留 / 宅配+忘れ物 フロント業務へ / リクエスト曲 古い順 + 寮内 BGM

**巴士实公告 + 系統**（D3）:
- 实公告 2026-03-22 保管 → `06_assets/real_samples/bus_notice_2026-03-22_特別運行便.md`
- 規格入 system_features.md §6.6（閲覧 / CRUD / 乗車名簿）

**新建文档**:
- `00_admin/demo_4-28/demo_script.md`（286 行 demo 流程脚本）
- `00_admin/demo_4-28/questions_for_requirements.md`（181 行问题队列）
- `00_admin/demo_4-28/scope_tier.md`（384 行 Tier 1/2/3 范围分层）
- `00_admin/文件结构指南.md`（366 行，全 repo 文件级清单 + 权限 + 反向索引）
- `02_design/system_features.md`（共用功能真值）
- `02_design/teacher_requirements.md`（老师需求文档）

### Changed — 03_dev 物理重构 + 业务规则修订

- **03_dev 物理重构**（D3）: `demo_4-28/` 嵌套解除 → `03_dev/{backend, teacher_web, student_ios, device}/` 平置化 + 27 MD 文件 path 引用更新 + `03_dev/LATEST.md` 新建（最新 HTML 索引）
- **HTML build 顺序明文化**: jsx 改 → `rebuild.command` → `build_single_file.py` 三段
- **CLAUDE.md §账号规则 patch v3**（推翻 4-20 议题 C "入学日面签确认"）: App 内 4-step 注册即激活 + 锁定升级 5 阶段 + 账号 ID 分配（00 demo seed / 01+ 真实）+ 密码重置走宿管后台
- **demo-day fix**（4-29）: リュウ イヒ 060218 対齐 / 部活合宿→外宿 / 宿監→寮監 / 巴士平日登校便 寮発→岡山駅西口発 7:30 / roster 削减 4 男+3 女 + ghost student 全清扫 5 名 5 房间号 / 全页面 maxWidth 砍 9 容器 → iPad/Mac 浏览器自适应

### Fixed — Demo crash + 文案细修

- **crash bug 修 2 处**: startSession seeded[8] / NotificationsPage roster[3]（hardcoded index 不防御短 roster）
- **白屏 debug 2 次**: file:// CORS（integrity/crossorigin strip）+ Round 2 数组越界（roster 13 人但 statuses 12 项 → `i % len`）
- **日语 native 文案审查**: 名単→リスト / 距 X まで→X まで残り / 晚→晩 / スプレッドシート×入力→食数の自由記入可 / 名前搜索 normalize 去空格 等约 12+ 处中文残留修正
- **细部文案 4 件**（4-29）: 匿名建議 自販機 / 記録 Shortcut→スマホ / override 閾値超で入寮→定刻に間に合わず / 期限後→期限内
- **デフォルト中文回答漂移** 自我观察 → memory `feedback_default_chinese_response.md` 新建（多次纠正"做日语 UI 时 CC 整段日语漂移"）

### Added — 4-29 close 时一并完成（v0.5.0 范围内）

**版本管理 SOP 建立**（解决 "4-21 → 4-29 9 天没 bump" 问题）:
- `00_admin/版本管理SOP.md` 新建（运行手册 — 当前版本 / 决策树 / 5 步 bump 流程 / 联动文件清单 / commit 前缀 / 多会话协调 / 30 秒判断 / 12 节）
- 和 iCloud `00_通用指南/版本管理实践指南.md`（教科书）明文分工
- **让 Claude 必读 SOP 的 4 层机制**：
  1. CLAUDE.md inline "版本号操作核心 5 条" + 触发条件清单
  2. WIP.md 头部第一行 `**当前版本**: vX.Y.Z`（带 VERSION_OK 豁免）
  3. pre-commit hook 检测 `01_specs/` / `02_design/` 改动 → "考虑 bump" 提醒（非阻塞）
  4. CLAUDE.md §会话结束 加第 4 项 "版本 bump 判断"（30 秒决策树）

**文件名 `_v0.1` 去后缀**（按 iCloud 版本管理实践指南 §5）:
- 11 个文件 git mv（+ 1 个 mv 处理 untracked）：API_CONVENTIONS / DEVICE_REGISTRY / ENUM_REGISTRY / ERROR_CODES / FIELD_REGISTRY / RollCall_Spec / flow_design / hardware_design / system_features / teacher_requirements
- 36 个活跃文档 perl 批量替换引用（保留 5 类历史快照例外：raw/* / vX.Y.Z_AC叙事 / progress_overview_draft / Batch3 / 99_archive）
- `v0.1_冻结决策.md` 保留（合法历史快照命名）

**v0.4.0 + v0.5.0 双 minor close**（4-29）:
- CHANGELOG 头部 + [0.4.0] 段 + [0.5.0] 段（一次性 close 4-21 至 4-29 9 天累积 15 commit）
- `00_admin/v0.4.0_AC叙事.md` + `00_admin/v0.5.0_AC叙事.md`（按 v0.3.0 模板 6 节）
- `00_admin/版本演变一览.md` 加 v0.4.0 + v0.5.0 段 + 路线表更新
- `00_admin/文档同步点清单.md §9` 文件名版本号规则
- `00_admin/文件结构指南.md` 加 SOP / 02_design 新文件 / AC 叙事

### Notes

- **本版本仍是 demo prototype 阶段**（Web HTML + iOS HTML + ./tomoshibi CLI），不是生产代码。`v1.0.0 = 系统在宿舍正式上线`目标不变
- **Demo 4-28 当天**（2026-04-28）by itsuki 实际执行结果 → 见 `05_logs/raw/2026-04-28*.md`（如有）/ `00_admin/demo_4-28/post_mortem.md`（如有）
- **跨会话改動履歴**: Tomoshibi-iOS 側 `STATUS.md` + `REMOTE_AGENT_GUIDE.md` 设 "最近の改动 log" section
- **AC 素材新增**: `raw/2026-04-22_iOS前端设计_Round1.md` + `raw/2026-04-23.md`（10 section + AC 候补 🌟 5 件）+ `raw/2026-04-24.md` + `raw/2026-04-29.md`（10 section + AC 候补 ⭐ 5 件）
- **本版本是项目第一个 "stakeholder-facing" 版本** — v0.5.0 AC 叙事文件指出这是 AC 叙事核心素材的特殊地位
- **首次执行版本管理 SOP** — close 流程跑了 SOP §3 五步 + §4 联动 6 处（CHANGELOG / WIP 头部 / 版本演变一览 / vX.Y.Z_AC叙事 / raw / git tag 等 itsuki 拍板）

---

## [0.4.0] - 2026-04-22 17:00（系统正式命名 Tomoshibi + S 系列 spec 闭合 + Device_Contract 骨架）

> **为什么 minor bump**（对照版本管理 SOP §2 决策树）：S 系列 spec 漏洞批量闭合（S1/S2/S3/S4/S7/S9/S10/S11/S12/S13/S14/S16/S19/S20）= 改了字典 + spec 主体（条件 1+2 minor 触发）+ Device_Contract 骨架是新设计层（条件 3 minor 触发）+ Tomoshibi 命名是 patch 但叠加上面归入 minor。
>
> **9 commit 归入本版本**：`2e49878` / `9d1cecf` / `eeb39d2` / `c8e05ea` / `b77b12a` / `71ffb38` / `d02ba18` / `00e5aab` / `8a9d226`（4-20 22:53 → 4-22 17:00）。
>
> **历史回顾**: 本版本 4-21 时标 `[0.4.0-wip]` 启动，但拖了 9 天没 close（直到 4-29 SOP 建立后回头追认 close）。教训：wip 状态有 deadline，不能拖。

### Naming — 系统正式命名 **Tomoshibi**（灯火 / ともしび）

**决策**（4-21 拍板）：
- **项目名**（repo / 开发代号 / AC 叙事项目名）保留 **DMSD**（Dormitory Management System Digitalization）
- **系统/产品名**（面向用户、学生 App、老师 Web、点呼机终端品牌、对管理员/教授文案）定名 **Tomoshibi**

**理由**（itsuki 定版 AC 面试话术）：
> "我在日本留学，宿舍是我在异国的第二个家。这个系统守护的是'灯火'——每个学生夜晚平安归来、房间亮起一盏灯。所以取日语名 Tomoshibi（灯火）。"

### Added — spec 实质改动

**字典扩**（`01_specs/rollcall/` 多文件）:
- `ENUM_REGISTRY` 新增 enum 值（修 S1/S2/S3 字典缺）
- `FIELD_REGISTRY` 新增字段（card_uid / student_status 等，修 S2/S3/S4）+ 禁止字段溯源（修 S20）
- `ERROR_CODES` 响应约定（修 S19/S20）
- `API_CONVENTIONS` 48 → 240 行扩写（URL / 动词 / 幂等 / 分页 / 日期 / 命名 / 状态码 / error.detail，修 S13）

**v0.4.0 开工启动**（4-21 上午）:
- `00_admin/v0.4.0_S2_S3_字段draft.md`（S2 card_uid 完整定义 + S3 student_status 4 取值 ENUM + 配套生命周期字段）
- `00_admin/v0.4.0_Device_Contract骨架.md`（210 行，9 节骨架 + OQ1-9 Open Questions：mTLS / nonce+HMAC / HTTP 超时 / device 注册 / 心跳 / 降级策略 / 固件更新 / LED 语义 / path_type 扩展）

**4-19 项目审查 backlog 剩余抽取**:
- `00_admin/漏洞_剩余清单_2026-04-21.md`（38 条分 D / S / T-L 三段 + 权限标签）
- 解决"backlog 87 条体量太大下次会话不知从哪开始"问题

**版本演变一览升级**:
- `00_admin/版本演变一览.md` 详细版（每个变化单独一句话解释，覆盖 18 tag + 补 v0.1.0 - v0.1.3 四个遗漏 tag）

**memory**:
- memory `project_naming_tomoshibi.md`（跨会话 memory，本地、不在公开仓库）

### Changed — 全局系统名同步 + spec 主体修补

- `CLAUDE.md §项目信息` 第一行区分项目名 vs 系统名 + AC 话术定稿
- `README.md` 标题改 "DMSD → Tomoshibi（灯火）"，新增"为什么叫 Tomoshibi"段
- 所有面向用户 / 面向教授的文档（spec / design / demo_4-28 材料 / AC 叙事 / backlog / 面试准备索引）同步更新 Tomoshibi
- spec 主体 `RollCall_Spec` §7 + §10.2 修漏洞（S1/S4/S7/S10）
- 项目 / 仓库 / git 历史 / commit 上下文继续用 DMSD
- 早期 throwaway iOS 代码（`03_dev/Student/DMSDStudentApp*`）不改（本就是待归档产物）

### Fixed — backlog 收口

- ✅ S1 / S2 / S3 / S4 / S7 / S9 / S10 / S11 / S12 / S13 / S14 / S16 / S19 / S20（14 条 spec 漏洞批量闭合）
- ✅ L10（FIELD_REGISTRY 禁止字段溯源）
- ✅ D21（CHANGELOG v0.2.0 / v0.3.0 header 加 HH:MM 时间戳精化）

### Notes

- **不含代码 / 不动 spec 主体大改**（仍是 spec-only 项目状态）
- **Device_Contract** 仍是骨架阶段，9 个 OQ 等 itsuki 拍板（部分留 v0.5.0+ 解决）
- **Tomoshibi 命名落地** 跨 30+ 文件同步，但 git 历史 / spec 文件名 / 项目代号继续 DMSD（双层不冲突）
- **首次跨会话并行下半天**: [Mac-主会话] 修 spec + [Mac-另一会话] 议 Tomoshibi 命名，commit 分工不冲突

---

## [0.3.6] - 2026-04-22（修订：插空补标 — spec）

> **修订号**：fix(spec): S13 API_CONVENTIONS 48→240 行扩写 — URL/动词/幂等/分页/日期/命名/状态码/error.detail。commit `8a9d226`。

## [0.3.5] - 2026-04-22（修订：插空补标 — spec）

> **修订号**：fix(spec): S19/S20/L10 + S4 遗漏面补齐 — ERROR_CODES 响应约定 + FIELD_REGISTRY 禁止字段溯源。commit `00e5aab`。

## [0.3.4] - 2026-04-22（修订：插空补标 — spec）

> **修订号**：fix(spec): S9/S11/S12/S14/S16 五条 CC 可独立漏洞一次性扫完。commit `d02ba18`。

## [0.3.3] - 2026-04-21（修订：插空补标 — spec）

> **修订号**：fix(spec): S1/S2/S3/S4/S7/S10 真闭合 — 字典扩 + §7 + §10.2 修漏洞。commit `c8e05ea`。

## [0.3.2] - 2026-04-20 深夜（v0.3.1 post 持续推进 + 议题 D 结论 + 架构决策推翻 4-19 部分）

> **为什么 patch bump**（对照版本管理指南 §2 / §3 + CHANGELOG 自身约定 "spec 实质内容未变 = patch"）：
> 1. `RollCall_Spec_v0.1.md` 主体**没改一行** —— 所有新决策落在 `02_design/`（新文档层）+ `CLAUDE.md`（元规则 / 项目信息）+ `raw/`（AC 素材），spec 主体留给 v0.4.0 闭环
> 2. 和同日早些的 v0.3.1 patch 判断**保持一致性**（v0.3.1 新建 10+ 文档文件也是 patch）
> 3. 保留 v0.4.0 名额给原 roadmap `spec 层闭环 + Device_Contract + S1-S7 修复`
>
> **两会话并行协调成果**：今日 DMSD 仓库有两个并行 CC 会话 —— `[Mac-主会话]`（8 commit，持续推 backlog）+ `[Mac-议题讨论会话]`（1 commit `d8be72b`，推 5 议题 A-E）。通过 commit 分工 + 不覆盖对方文件协调。两会话未冲突。

### Added — 12 个新建文件

**设计文档层**（`02_design/`）:
- `02_design/flow_design_v0.1.md`（324 行）— 签到端到端流程 + 攻击路径 + 防御机制
- `02_design/hardware_design_v0.1.md`（260 行）— 硬件选型 + 采购清单 + keystore 备份方案

**AC readiness / 面试准备**:
- `00_admin/AC_提交_checklist.md` — 5-10 月每月 gate + 技术/AC 叙事双线 + 滑动条件降级
- `00_admin/面试准备_索引.md` — 6 大类 42+ 题目 + 素材指针 + 教授追问模板
- `00_admin/v0.3.0_AC叙事.md` — CLAUDE.md "版本 bump 触发 AC 记录" 首次落地 + 未来模板

**基建 / 评估文档**:
- `LICENSE` — All Rights Reserved + AC 后 4 方向评估表
- `00_admin/T2_iOS归档_dryrun评估.md` — 3 方案对比 + 推荐 A + 完整执行命令（不执行，待授权）
- `00_admin/v0.4.0_S系列spec漏洞优先级分析.md` — 20 条 S 分 MVP(7)/Nice-to-have(8)/Defer(5) + Week 1-3 节奏 + 总估 15-20 小时

**AC 素材 / 读者导航**:
- `05_logs/raw/2026-04-20.md`（958 行）— 下午议题讨论会话 AC 素材，14 条 / 10 #AC候选
- `05_logs/raw/2026-04-20_v0.3.1发布执行.md` — 本主会话 AC 素材，4 条 #AC候选
- `05_logs/raw/README.md` — 给教授/访客的 raw/ 目录导航
- `05_logs/dev_log/2026-04-10_空白期反思_索引.md` — 指向 iCloud 反思原文（不泄露私密）

### Changed — 元规则 / 基建修订

**CLAUDE.md**（两会话各自改一次）:
- §项目信息 技术栈细化（BTR / App Links / Pi 4B 2GB / ST25DV16K / Android 10+）+ 防御核心 + 硬件流程权威源指针
- §项目信息 **推翻 4-19 G2 "一设备一账号"决策** → 改为"任意设备签名 + 入学日老师扫码面签确认"（下午议题 C 新决策）
- §项目信息 keystore 备份方案定稿（Mac + 服务器加密压缩包 + 纸质密码 + 不存 iCloud）
- §目录结构 `02_design/` 加注释
- §对话规则 **新增第 5 条 "讨论=产出，不等会话结束"**（itsuki 元规则 + memory `feedback_discuss_means_produce` 新建）

**记录指南**:
- `CLAUDE_CODE_记录指南.md §2` 去 `date` 命令冗余（改为读 env prompt `currentDate`）
- `CLAUDE_CODE_记录指南.md §12` raw 命名规则改为 3 步判断决策树（D26 + L6）

**基建**:
- `.gitignore` 从 18 行扩到 ~80 行（Python/Node/Android/IDE/日志/OS/SQLite/.claude 本地设置）
- `00_admin/create_local_dev_symlink.sh` 加 26 行头部注释 + 两层自检（Mac vs VPS 场景判别）
- `00_admin/TODO.md` 新增 4 条（宿舍综合官网 / keystore 备份 / 异常行为检测 v0.6.0+ 推迟 / 毕业交接包 2028-01）
- `CHANGELOG.md` 头部加 2026-04-20 pre-0.1 tag 追认说明

### Fixed — 架构决策推翻 + backlog 收口 14 条 ✅

**推翻 4-19 G2 两条**:
- "一设备一账号" → 取消（议题 C，改老师面签）
- "Phase 2 静态 NFC 贴纸" → 升级动态 ST25DV16K（议题 B，URL 复制漏洞）

**backlog 打 ✅（本版本 14 条）**:
- A2（志望動機占位）/ A4（commit 消息动机坦诚在 README）/ A5（raw/README）/ A6（AC 提交 checklist）/ A9（空白期反思锚点）/ A11（AI 协作声明在 README）/ A12（v0.3.0 AC 叙事模板）/ A13（面试准备索引）
- L1 超额（10 个 pre-0.1 annotated tag）/ L6（raw 命名决策树）
- T4（.gitignore 扩充）/ T6（LICENSE）/ T8（symlink 脚本注释+自检）/ T10（payload.json PII 检查无敏感）/ T13（.claude/settings.local.json 未 tracked）
- D26（记录指南 §2 date 去冗余）

**新增 backlog ⏳ 1 条**：T2 iOS 归档 dry-run 评估完成，待 itsuki 授权执行

**标过期 🟰 1 条**：T9 Mac↔VPS 同步协议（VPS 已停用）

**新增 backlog M2 元条目**：版本管理指南 §5 / §7 / §12 iCloud 更新建议

### Notes

- **不含代码 / 不动 spec 主体** — 仍是 spec-only 项目状态
- **backlog 总进度**：✅ 25 / ⏳ 12 / 🟰 1 / 剩 49（从 v0.3.1 的 11 ✅ 升到 25 ✅）
- **git tag 追认**：本版本区间内补了 10 个 pre-0.1 annotated tag（`v0.0.1` - `v0.0.10`）指向 initial commit，完整版本历史可用 `git tag | sort -V` 查看
- **10 commit 归入本版本**：
  - `f36d10b` / `8fac003` / `d7e587e` / `85e3b21`（[Mac-主会话] v0.3.1 发布后的持续 patch）
  - `d8be72b`（[Mac-议题讨论会话] 议题 D/E 补）
  - `ca16614`（WIP 锚 v0.3.2 方向）
- **议题 E 遗留**（Demo 范围）2026-04-21 itsuki fact-check 筑波官网时间表后拍板
- **下一步 v0.4.0 minor** = 原 roadmap scope：Device_Contract + 字典补字段（S2/S3）+ spec 主体漏洞 S1/S4/S7 修复 + 其他 Nice-to-have

---

## [0.3.1] - 2026-04-20（AC readiness 文档层同步 + 文档同步机制 A+B+C）

> **为什么 patch bump**：本版本是"修正已有内容到事实一致 + 补必要的外观文档"，不新增 spec 范围。按版本管理指南 §2 / §3 属于 Patch 语义（"攒了一批小修复准备发布"）。
>
> **scope**：闭合 backlog Tier 1 Batch 1（4 项 ✅）+ Batch 2/3 draft（CC 起草待 itsuki 合并，4 项 ⏳）+ M1 文档同步机制（4-19 建立）+ A2 志望動機占位。项目审查 backlog 87 条里累计处理 10 条 ✅ + 11 条 ⏳。
>
> **路径**：v0.3.0（2026-04-17 spec 主体 rewrite）→ v0.3.1（文档同步 + AC 门面） → v0.3.2（itsuki 手笔区补完）→ v0.4.0（spec 层闭环 + Device_Contract）

### Added — 新建文件

- `README.md`（根目录，103 行）：项目门面。段落：是什么 / 为什么做 / 做到哪了 / 目录导航（推荐阅读顺序）/ 技术栈（反映 4-19 G2 决策）/ 关于 AI 协作（A11 内嵌声明）/ 升学目标（坦诚 AC 动机）
- `00_admin/原创设计_语音播报防作弊.md`（135 行）：核心原创设计 showcase。按"起点观察（宿舍代刷）→ 四步推导 → 替代方案对比 → 设计本质 → 面试原话 → 证据链"结构。第一人称叙事，不是 spec 风格
- `00_admin/AC_志望動機_素材.md`：A2 占位框架（8 个必答子问题 Q1-Q8 + 辅助素材收集清单 + 填写顺序建议 + 更新触发信号）。内容留白由 itsuki 自己填
- `00_admin/文档同步点清单.md`（M1，4-19）：版本号 / 目录结构 / 5 核心问题 / 分阶段策略的单源真值清单 + Release / Onboarding Checklist
- `00_admin/2026-04-19_项目审查_backlog.md`（4-19）：87 条漏洞 + Tier 0-4 版本路线图
- `00_admin/hooks/pre-commit` + `install.sh` + `README.md`（M1，4-19）：声明性文件版本号硬编码拦截机制
- `00_admin/progress_overview_draft_2026-04-20.md`（⏳ Batch 2a draft，待 itsuki 审合并后删）
- `00_admin/Batch3_itsuki手笔素材指引.md`（⏳ Batch 3 辅助，9 条 decision + 5 次 project_evolution 转折 + Python/PostgreSQL 补答 draft，待 itsuki 粘贴后删）

### Changed — 文档同步

- `CLAUDE.md` §项目信息 整段重写（去硬编码版本号 + 反映 4-19 G2 决策"v1.0 一次上，取消 Phase 1/Phase 2"）
- `CLAUDE.md` 新增 §文档一致性规则 章节（单源真值表 + 声明性文件清单 + 会话结束前 CC 必做 3 项 + hook 安装指令）
- `CLAUDE.md` §会话结束 扩展到 7 步 + 增加"git 后要讲 commit 内容不讲 git 工具"的前提规则（含 ❌/✅ 对比）
- `TODO.md` 头部版本号改指针 + 3 条过期 🟢 TODO 打 ✅（D14 / D15 / D16）
- `WIP.md` 多次更新（头部时间戳 4-19 → 4-20 / 最近完成 4-19 段 + 4-20 段 / 更新日志 append 6 条）
- `CHANGELOG.md` 头部加"最后更新"时间戳（D20）

### Fixed — backlog 处理（10 条 ✅ + 11 条 ⏳）

- ✅ D19 / D20 / D22 / D23 / D24 / D25 / L11 / A1 / A2 / A3 / A11
- ⏳ D1 / D2 / D3 / D4 / D7 / D8 / D9 / D10 / D11 / D12 / D13（CC 起 draft 就绪，等 itsuki 手动合并，见 Batch3 素材指引 + progress_overview draft）

### Notes

- **本版本不含代码改动**（项目仍 spec-only）
- **未 push 到 origin**：所有 commit 都在 local。itsuki 说"push" 时再推
- **raw/2026-04-20.md**（今日下午另一会话定稿 BTR + ST25DV + Pi 2GB 的 5 条 AC 素材）不在本版本 commit 里，留 itsuki 或下次会话处理
- **v0.3.2 预期 scope**：itsuki 手动合并 Batch 2 / Batch 3 draft → decision_log / project_evolution / learning_path / progress_overview 正文更新到位 → 闭合剩余 11 条 ⏳
- **M2 新增**（指南待更新）：版本管理指南 iCloud §5 / §7 / §12 与实际脱节，详见 backlog §3.6 M2，等 itsuki 手动改

---

## [0.3.0] - 2026-04-17 晚 18:53（spec 主体 rewrite）

> **为什么 minor bump**：v0.2.0 完成了字典三件套 + DEVICE_REGISTRY 的"定义层"。本版本完成"业务规则层"——把新字典实际写进 spec 主体，并新增 3 块业务规则（双路径信号流 / 4 台协调 / 改判时限+扣分联动）。是 v0.2.0 承诺的实现完成。

### Added — spec 主体新增章节
- **§1 双路径并存**：路径 A（NFC 卡 / Phase 1） + 路径 B（iPhone 静态标签 / Phase 2）双路径定义 + thin client 架构原则
- **§5.1 双路径签到信号流**：路径 A / 路径 B 的端到端流程图 + §5.1.3 防代签人防补偿
- **§9 系统组件职责** rewrite：thin client / thick server 落地到 7 个组件分工 + 引用 DEVICE_REGISTRY
- **§11.3 改判时限矩阵**（角色 × 时间）：解决附录 B.9 涉及金钱/处分字段的时间窗
- **§11.4 改判与扣分联动表**：6 种状态转换的自动 ledger 规则
- **附录 C — 4 台点呼机协调规则**（C.1-C.5）：学生归属 / session 边界 / 重复碰处理 / 物理布局候选 / 学生 → session 归属
- **附录 D — v0.2 收口清单**：附录 A/B 共 25 项的 ✅/🟡/🔄 状态盘点

### Changed — spec 主体对齐字典
- §1 概述移除"App 触碰"假设（A.1 ✅ 收口）
- §2.1 base_status 表：`exempt_range` 从 overlay 改为 base（Q1 落地）
- §2.2 overlay_badges：分两类（纯装饰型 / 改底色型）
- §2.4 底色优先级：`exempt_range` 进入排序
- §3.2 弹窗信息：`本场来自的点位（A 或 B）` → `device_id` + `path_type`（B.16 ✅ 收口）
- §5 重排：原 5.1-5.4 → 5.2-5.5，新插 5.1 双路径信号流
- §7 边界：`NOT_STARTED` / `ENDED` → 统一 `SESSION_NOT_RUNNING`；新增 5 个错误码引用
- §8.2 / §8.3：`EXEMPT_RANGE` 不再是 overlay
- §10 数据模型：rollcall_event 新增 `device_id` / `path_type` / `applied_group` / `idempotency_key`
- 所有大写状态值（`INIT/PRESENT/LATE/ABSENT/EXEMPT_RANGE`）改为小写以匹配 ENUM_REGISTRY 规则

### Notes
- 附录 A/B 仍开放项（约 9 项 🔄）留给 itsuki 拍板或 v0.4 / v0.5 继续
- spec 现 958 行，比 v0.2.0 时增加 ~280 行（新增 3 块规则 + 附录 C/D + 信号流图）
- `.pages` 原稿继续保留为历史快照，本 `.md` 是唯一真值

---

## [0.2.0] - 2026-04-17 晚 18:22

> **为什么 minor bump**：字典三件套全部重写 + `DEVICE_REGISTRY` 新建 = spec 实质改动，触达 SemVer minor 阈值。原计划的 v0.1.4（纯元工作）因此次 commit 合并了字典改动被合并到 v0.2.0 一并发布。

### Added — spec 实质变动
- `01_specs/rollcall/DEVICE_REGISTRY_v0.1.md` 新建：`device_type` 三类 / 4 台候选位置 / 注册流程 / 生命周期
- `ENUM_REGISTRY` 新增：`session_event_source` / `device_type` / `path_type` / `day_type` / `student_group` / `schedule_mode`
- `FIELD_REGISTRY` 新增：`device_id` / `started_source` / `ended_source` / `device_*` 6 字段
- `ERROR_CODES` 新增：`UNKNOWN_CARD` / `UNKNOWN_DEVICE` / `DEVICE_NOT_ACTIVE` / `NO_ROLLCALL_FOR_TODAY` / `INVALID_SIGNATURE`
- spec 附录 B.9 扩写"修改时间窗矩阵"（角色×时间，月结冻结）
- spec 附录 A.2 明确"当前假设：足球部祝休日训练导致时间与平日相同 + 待 itsuki 最终确认"

### Changed — spec 实质变动
- `ENUM_REGISTRY.base_status` 重命名（原 `background_status`）+ overlay 分两类（badge / range）
- `ERROR_CODES` 按通用/场次/签到分组 + 移除 `NOT_STARTED`/`ENDED`（用 `SESSION_NOT_RUNNING` 替代）
- `FIELD_REGISTRY` 废弃 `background_status`
- spec 附录 B.11 从 🟢 升 🟡（Phase 1 无 App 时申请流程的根本问题记入 spec 主体）

### Added — 元工作
- CHANGELOG 细粒度重建：pre-0.1 追认 6 条（2025-12 ChatGPT 方案级迭代）+ 2-02 至今每实质节点一条
- `99_archive/README.md`：10 项归档条目 + 归档原则 + 清理 SLA
- `raw/2026-04-17.md`：全项目审查（16 处文档/字典内部冲突 + 5 个外人视角担忧）+ 版本号方法论修正 + 早期 chat log 整合 + 9 项重要不紧急问题方案 + 2025-12 对话日期锁定（2025-12-19 23:11 JST）+ project_evolution 起点章节草稿

### Changed — 元工作（单源化 / 反冗余）
- `CLAUDE.md`：权限表 / 目录结构改为唯一真值源
- `CLAUDE_CODE_记录指南.md`：大幅简化，5 核心问题 / 目录边界都改为"见 CLAUDE.md"；新增 `[方法论决策]` 标签
- 元文档行数：1563 → 1362（省 201 行）

### Changed — 清理（6 项 🟢）
- 删 `05_logs/.trash_dev_log/` / `.trash_problem_solving/` / `.trash_raw/` 三个空目录
- `00_admin/Folder Structure Overview.pages` → `99_archive/2026-03-08_Folder_Structure_Overview.pages`
- `01_specs/Overview/*.docx`（2 个 Word 原稿）→ `99_archive/01_specs_Overview_原稿/`
- `.gitignore` 删 3 条过期规则（`99_archive/2025-12_早期GPT对话/` 已 tracked；`99_archive/05_logs_ac_v2归档/` 与 `全量日志/` 已不存在）
- `99_archive/2025-12_早期GPT对话/` 三个 JSON 文件正式入 git
- `00_admin/executable_dev_checklist_v0.1.md` → `99_archive/2026-04-12_executable_dev_checklist_v0.1.md`（功能被 TODO.md 吸收）
- `00_admin/目录架构.md` 删除（CLAUDE.md §目录结构是权威源；git 历史可恢复）

### Notes
- spec 主体 rewrite（§1 双路径 / §2 Q1 / §5 / §7 / §9 / §10 / 附录 C）仍未落地 → 留给 v0.2.1 或 v0.3.0
- 本 commit 由两个 CC 会话并行工作的合流产物（无文件冲突，字典与清理零重叠）

---

## [0.1.3] - 2026-04-17 上午

### Added
- `01_specs/rollcall/RollCall_Spec_v0.1.md`：把 .pages 原稿数字化为 Markdown，附录 A（7 项整理时发现的问题）+ 附录 B（18 项深度审查发现的 spec 漏洞，共 25 项）
- iCloud AC 素材第 2 层首次批量填充：10 条候选 + 候选索引
- iCloud AC 目录结构重构（扁平版与嵌套版合并，按编号分类）
- AC 入试记录指南 v3.0 → v3.1（§1 目录图、§11 起步清单修订）
- `DMSD/CLAUDE.md` iCloud 权限子表（CC 可读 iCloud AC 目录；写 03/04 需当场授权；永不写 05_产出）

### Changed
- spec 源权威性从 `.pages`（二进制，Git 无法 diff）过渡到 `.md`（可追溯）
- 修正 RollCall spec 中若干日文打字错误（おす→押す、人ってから→入ってから 等）
- spec §2 颜色优先级统一为详细版（两套写法合并）

### Notes
- 本版本是 **spec 可追溯化** 的里程碑：从此 spec 修改每一次都能被 git 看见
- spec 主体（§1 "App 触碰" 与 Phase 1 "卡触碰" 脱节）未重写 → 留给 v0.2.0

---

## [0.1.2] - 2026-04-15

### Added
- 核心架构原则：**thin client / thick server**（点呼机只搬运数据，业务判断全在后端，由 itsuki 主动提出反驳 AI 的过度配置）
- Phase 2 双路径架构：卡（RFID）+ iPhone（读点呼机外贴静态 NFC 标签 → 自己联网发后端 → WS 推回点呼机播报），不走 HCE
- iOS 第三方 App 无 Secure Element / HCE 权限的根本限制认知（Apple Pay 背后是 SE + 一次性 token）
- RPi vs ESP32 全维度重开对比 → 确认方向 A（Raspberry Pi），推翻 4-12 "已决定 RPi" 的伪决策

### Changed
- 点呼机硬件配置降级：Pi 4B 4GB → Pi Zero 2 W / Pi 4B 2GB 候选（职责最简化 → 配置需求最小化）
- 点呼机代码估计 < 100 行 Python（极简化）

### Notes
- 本版本是 **架构原则层** 的升级，spec 文件未改 → patch
- 发现 spec gap：v0.1 spec 完全没写点呼机契约（记入项目债）
- Android 版 Phase 2 方案未细化（HCE 机制与 iOS 不同，记入项目债）

---

## [0.1.1] - 2026-04-13

> **注**：本版本原标记为 0.2.0，但内容实质上仅为 **命名与元数据整理**（spec 文件实质内容未变），按 SemVer 规范应为 patch 而非 minor bump。2026-04-17 审查时更正。

### Added
- `CHANGELOG.md` 版本记录文件
- 版本管理实践指南（放在 iCloud `00_通用指南/`）
- AC 入試 三层记录体系（raw / 候选 / 成品）
- `00_admin/WIP.md` 多会话协调文档
- `00_admin/CLAUDE_CODE_记录指南.md` CC 操作手册

### Changed
- spec 文件命名统一：所有文件从 "v1.0" 重命名为 "v0.1"
- 更新 `00_admin/executable_dev_checklist_v0.1.md`：点呼主闭环增加硬件架构和分阶段说明
- 更新 `CLAUDE.md`：反映分阶段策略和版本管理

### Notes
- 本版本是 **命名与元数据整理**，spec 文件实质内容无变化
- 4-12 的设计决策（NFC 硬件 / 分阶段 / 播报防作弊 / NFC vs 二维码）未写入 spec，记录在 `05_logs/decision_log.md`
- commit hash: `3b01345` / `e637034` / `e346dca` / `43c73ec` / `91a4294` / `d89b435` / `666faf8`

---

## [0.1.0] - 2026-02-12

### Added
- 规格文档冻结：`ENUM_REGISTRY` / `FIELD_REGISTRY` / `API_CONVENTIONS` / `ERROR_CODES`
- `RollCall_Spec` 点呼行为规格（.pages 原稿）
- `v0.1_冻结决策.md`：纪律阈值（迟到 0.5 / 缺席 1.0 / 月 ≥4 罚扫 / ≥9 禁足）+ session 状态机 + 规则优先级
- 8 条验收场景
- 可执行开发清单

### Notes
- 这是项目的 **第一个正式版本基线**
- 原始文件名使用 "v1.0"，已在 0.1.1 中统一重命名为 "v0.1"
- 冻结的是 **规则与数据模型**，未冻结硬件架构 / 点呼机契约 / API 详细 schema（留给后续版本）

---

## [0.0.10] - 2026-02-08

### Added
- 学生分类（普通寮生 / 足球部 / 未分类）与点呼场次合并思路

### Notes
- 为 v0.1.0 冻结做准备的倒数第二稿
- 来源：`05_logs/dev_log/2026-02-08_学生分类和点呼合并.md`

---

## [0.0.9] - 2026-02-04

### Changed
- 全体計画改善（全体规划迭代）

### Notes
- 来源：`05_logs/dev_log/2026-02-04_全体計画の改善.md`

---

## [0.0.8] - 2026-02-03

### Added
- 点呼规格大纲（第一版成文的点呼业务规则）

### Notes
- 来源：`05_logs/dev_log/2026-02-03_点呼规格大纲完成.md`
- 这是 spec 的前身

---

## [0.0.7] - 2026-02-02

### Added
- 项目目录结构与命名规划初稿

### Notes
- 来源：`05_logs/dev_log/2026-02-02_目录结构和命名规划.md`
- 进入 git 时代前夕的工程基础

---

## [0.0.6] - ~2025-12（追认，日期不精确）

> **pre-0.1 追认**：以下版本记录的是 2025-12 ChatGPT 对话里的方案级迭代。原始记录见 `05_logs/raw/2025-12_NFC系统早期设计对话.md`。日期是大致估计，不是精确 tag 时间。

### Added
- **v2.1 加固版**：Android 碎片化对策（enableReaderMode 前台模式 + NDEF 纯文本避免系统抢占）
- ECDSA 签名格式强制统一（DER base64），避免 iOS/Android 验签不兼容
- nonce 预取池（解决弱网下 challenge→submit 的逻辑悖论）
- 内网服务发现：路由器静态 DHCP + 内网 DNS + App 内置管理员改 Base URL 入口
- 内网 HTTPS 策略：校内自建 CA 或证书 Pinning，不用"自签 + 忽略"
- 复用监控服务器的 I/O 争抢对策：PostgreSQL 数据目录必须与监控录像分盘
- PostgreSQL 备份策略：每日 pg_dump 加密 + 双地点落地
- 物理瓶颈修正：同一教室贴 2-3 个 NFC 标签并行读取，避免门口堵死
- 无 NFC 学生兜底：老师手动签到 + 临时设备登记

### Notes
- 这是 pre-0.1 最成熟的方案；之后的 v0.0.7（2-02 目录规划）开始才落纸进 git 体系

---

## [0.0.5] - ~2025-12（追认）

### Added
- **v2.1 方案**：去掉 FaceID（iPhone / Android 统一）；身份证明改为"账号登录 + 设备私钥签名"
- 后端选型：Python + FastAPI + PostgreSQL + WebSocket
- 部署方向：宿舍内网本地服务器（复用现有"监控服务器"跑该系统，尽量低成本）
- Android 支持：Android Keystore 生成 P-256 私钥（hardware-backed 优先，不强制 StrongBox）

### Removed
- FaceID / 生物识别依赖（统一 iOS + Android 不对生物识别做要求）

### Notes
- 去 FaceID 后，"防代刷"靠老师现场监督 + 单设备绑定 + 换机审批 + nonce/验签，**不靠纯技术**
- 开始明确"内网 + 不一定要公网 IP + 预算极低"的现实约束

---

## [0.0.4] - ~2025-12（追认）

### Added
- **v2 综合方案**：
  - 安全闭环：设备密钥（iOS Secure Enclave / CryptoKit）+ P-256 ECDSA + 一次性 nonce + 服务端 session 时间窗
  - 可选强化：Apple App Attest（防伪造 App/脚本）
  - 扫除拍照：水印 + 照片 hash + 设备签名证明（非单纯水印）
  - 数据模型：事件溯源（append-only）+ 状态投影（seat_status_snapshot）
  - 状态机：present / late / absent / invalid / manual_override + 规则优先级
  - 运维可靠性：学生端本地队列 + 重试 + 幂等 key；老师端 WS 断线重连 + 全量快照校准

### Notes
- v2 是第一个"可交付级"综合方案，但还依赖 FaceID（后在 v0.0.5 被去除）

---

## [0.0.3] - ~2025-12（追认）

### Added
- 学习 NXP NTAG 424 DNA 的 **SDM/SUN 动态认证机制**
- 认知："每次触碰 tap-unique"→ 后端用 AES key 验证 CMAC + 防重放计数器
- 理解"复制 tag 数据 ≠ 能伪造签到，关键是服务端验的是什么"

### Changed
- 点位防复制方案从"普通静态 tag"升级为"安全标签"候选

### Notes
- 这是关键认知突破：从"静态 ID 不能当凭证"到"需要动态认证机制"

---

## [0.0.2] - ~2025-12（追认）

### Added
- 方案改为 **iPhone 读固定点位 NFC tag**（Core NFC 原生能力）
- 服务端 session 时间窗 + 挑战/签名 + 设备绑定的基础安全模型

### Removed
- HCE 手机当卡方案（iOS 第三方 App 无 HCE 权限，Apple 只对 EEA 开放且有授权条件）

### Notes
- 第一个重大方案推翻。认知：iPhone 不能被"自制读卡器"读作卡；只能反过来让手机读标签

---

## [0.0.1] - ~2025-12（追认）

### Added
- **最初设想**：学生手机当 NFC 卡，碰一碰教室里的读卡机完成签到（灵感来自日本 NFC 自动贩卖机）
- 最初业务方案：钥匙贴二维码 = 学生信息，一人一设备绑定，老师 iPad 座位表实时亮灯
- 扣分处分规则雏形（迟到 0.5 / 缺席 1.0 / ≥4 罚扫 / ≥8 禁足）
- 扫除拍照审核 + 加分抵扣设想

### Notes
- 这是项目的起点方案，**多处被后续迭代推翻**（HCE 不可行、钥匙二维码是隐私雷、单纯水印防伪不足）
- 但业务形态（固定时间 / 固定教室 / 固定座位 / 碰一下签到 / 老师 iPad 实时亮）**从头到尾保留至今**
- 证据：`05_logs/raw/2025-12_NFC系统早期设计对话.md` 早期段落

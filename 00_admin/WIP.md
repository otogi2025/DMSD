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

**当前版本**: v0.7.0（2026-04-30 晚 close — 三轨 A+B+C 同日完成：38 条 B 标准 baseline + system_features §9 8 条拍板 + 实装包拆分到 BACKEND/iOS/Web LOG + 实物表 evidence 推翻 LINE 文字推测 + 沟通规则 #6 + SOP §8.5 版本路线图）<!-- VERSION_OK -->
**版本管理 SOP**: `00_admin/版本管理SOP.md`（CC 改 spec / 02_design / 03_dev 主体后必读 §2 决策树）

**最后更新**: 2026-05-01 夜 by [Mac-会话D-iOS-完全体] — **iOS 学生侧完全体（基于 `a7eb860`、未 commit 等 itsuki 明示）**：P0×3 完成（#37 Music 入口加 LifeTab / 出寮届修改届完整表单 + audit log 履歴 tab + chain 重置 / 学習 NFC 3 次碰 + マイページ 学習履歴）+ P1×2 完成（マイページ MyInfoEdit 修订 spec 违反 §6：学号/姓名 read-only + 邮箱/电话/房间号可改 / 注册留学生 chip + 锁定升级 30s→1m→5m→30m→1h→永久）+ P2×1（push listener mock 4 trigger 入口在 MySettings 底）+ 中途反馈 6 件（chain → 自然日语「承認の流れ」/ 推移 → グラフ / BottomNav hit area maxHeight infinity + 透明度提升 / breadcrumb popup 重做 → iOS Safari 风格左上小卡 / Liquid Glass morph GlassEffectContainer + glassEffectID interactive / 修改届 原値 strikethrough 删除）+ ⭐⭐ **リクエスト曲改造拍板**（赞踩 → 投诉系统 5/10/15 自动封禁 1m/3m/永久 + 老师手动封禁 + 7 件 badge）→ system_features.md §7.11.2 spec 落地 + iOS 全实装（SongReportSheet 4 理由 + 投诉 button + 投稿封禁 banner）。BUILD SUCCEEDED 全程绿。**不动**: backend / teacher_web（别 agent 主写区）。**dump**: `05_logs/raw/2026-05-01.md §6-§9` 追加（早上「三端对齐审计」§1-§5 保留）。
**上一次更新（保留参考）**: 2026-05-01 by [Mac-主会话] — **三端对齐审计 dump + 方案 ABC 提案 + Q1/Q2 阻塞**（不动手代码、等 itsuki 拍板）：3 个 Explore subagent 并行扫 backend v1 + iOS v1 Swift + teacher_web → 交叉对齐 → **失配清单 15 条 F1-F15**（🔴 阻塞 7 条 / 🟡 体面 5 条 / ⚪ 可延后 3 条）。核心阻塞: **F1 apply kind 三端不同值**（iOS `stay/holiday/returncountry` ↔ backend `外泊/帰省/帰国`）/ **F3 stay_locations 形状不同**（iOS 平面 string[] ↔ backend `[{kind,name,address?,phone?}]`）/ **F4 meals_skip 形状不同**（iOS `{date,meal:朝食}` ↔ backend `datetime`）/ **F5 iOS 多发 student_id（backend 拒）+ 少发 reason（backend 没这字段）/ F6 backend 没实装注册 endpoint（D10 纸上有代码无）/ F7 iOS 完全没接 URLSession**。**修正方案 ABC**: A = iOS 5 处映射 ~150 行 + backend 加 reason 字段 / B = A + APIClient + 注册登录全流程 / C = B + 文档同步 + Web v1 启动。CC 推荐先 A。**Q1/Q2 阻塞等 itsuki 拍**: Q1 = status 枚举对齐方案（iOS cancelled↔backend withdrawn 合并？iOS draft 保留？returned 砍掉？） / Q2 = reason 字段归属（backend 加 / iOS 砍 / leave_method 末尾 hack）。**dump**: `05_logs/raw/2026-05-01.md` 5 节（§3 失配清单 F1-F15 / §4 方案 ABC / §5 阻塞 Q1+Q2 + 接续指引）。**未动**: teacher_web demo（锁定）/ v1（未开工）/ system_features.md / DESIGN_LOG / 任何 Swift 或 Python 代码。 <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-30 夜 by [Mac-主会话调配] — **4-30 後續 第二轮决策落地**（commit `512424d`）：iOS 起手实装 — SeedModels.User 加 isStudyTarget / AppStore 加 StudyState + StudyLeaveRange + 字段 + submitStudyLeave (>3 触发文案 A) + cycleDemoStudyState long press / HomeStubs **砍 segmented + コミュニティ tab + 通知 tab + 对应 #Preview**（itsuki: tab 重复砍，功能集中一页）→ Home 直显 LifeTab + amber Card **三态 ⚠️ DEMO-ONLY** / ApplyStubs APPLY_TYPES 加 studyAbsence + StudyAbsenceForm + DateField/TimeField **ja_JP locale**（修月份英语）+ ApplyDetailView **redirect StayDetailView**（修 #5 申请人看不到 chain bug）。**system_features.md 5 节落地**: §3.4 教师权限按职责勾选 + 旧教师辅助新教师 / §7.2.4-5 出寮届修改届（状态机 + 字段范围 + chain 重置 + audit log 可见性）/ §7.3.3-10 学習大扩充（NFC 3 次碰 + 时间锁定 + 状态机 + 异常老师手动判 + 月度 ≥3 次提醒文案 A + 今日中止 + amber Card 三态 DEMO-ONLY + 名单变更通知）/ §7.13 R1 邮件例外（学習 push + 老师 Web 通知中心）/ §10 +1。**memory** project_demo_scaffolds_to_remove_before_v1 #15 加 amber Card 三态。**raw/2026-04-30.md §11** AC 痕（⭐⭐ 学習 NFC 化 / ⭐⭐ 教师权限模型 / ⭐ R1 例外、~1500 字）。xcodebuild → BUILD SUCCEEDED。**仍 ⏳ 下次会话补**: §8 数据模型 6 张新表 / RollCall_Spec 加学習平行 / DESIGN_LOG.md 各 / TODO.md 38 条 baseline 更新 / iOS 待做（Music 入口 加 LifeTab / StayDetailView 编辑按钮 / 学習 NFC 真流程 / 注册登录 / マイページ）。 <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-30 夜 by [Mac-会话B-backend] — **会话 B backend P0 起手版 close**：`03_dev/backend/v1/` 从零搭建（FastAPI + SQLAlchemy 2.x 同期 + SQLite/PG + bcrypt + JWT），覆盖完成定义 4 项：(1) **#2 schema** = 帰省/外泊/帰国 三种 discriminated Pydantic + ORM models（applications + application_approvals + students + teachers + class_teacher_assignment + notification_log + audit_logs）(2) **#5 GET /applications/{id}** = 学生本人 + 教师 dorm filter 两路、承认 chain 全段返回 (3) **#6 SendGrid 邮件** = 提交时按 D4 实物表 chain → 全 chain 役职 email 一斉送信 + notification_log 记录 + 失败不阻塞 + dev mode（无 KEY 时降级 pending）+ `POST /notifications/test` smoke (4) **#7 食堂 Excel** = `GET /meals/calc`(JSON debug) + `GET /meals/export`(.xlsx) 双 sheet「日別集計 + 学生別詳細」openpyxl 实装、朝7/昼12/夕18 食时刻暫定值。**chain 实装**: 外泊 D4 实物表 evidence 为準（一般 3 行 / 留学生 5 行）/ 帰省・帰国 evidence 待補 → `EXTERNAL_ROLES_BY_KIND` 暫定値 + `PROVISIONAL_CHAINS` flag + response 头 `X-Approval-Chain-Provisional: true` 警告。**測試**: pytest 19 ケース全 pass（chain D4 5/3 行 / 暫定 / 他人届 403 / #3 出寮日今日 422 / Excel バイナリ妥当性 / SendGrid dev mode pending）。**seed**: 役职 7 種網羅（寮務部長/課長 + 国際交流部長/課長 + 管理係 + 寮監 + 学習担当）+ 担任 2 + 学生 2（留学生 060218 + 一般 060103）+ 共通密码 `tomoshibi-dev-2026`。**未实装**（後續会話）: 役职承認 #10-#13 / 学習出席 / 点呼 / Alembic migration / async 化 / Refresh token rotation。**实装的不动文件遵守**: `03_dev/student_ios/v1/*` (会话 A) / `03_dev/teacher_web/v1/*` (会话 C) は触っていない。 <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-30 晚 by [Mac-主会话] — **v0.7.0 close**（5 commit 归入：`604bc9b` 轨道A baseline / `4272fc7` 轨道B §9 拍板 / `f25255b` SOP §8.5 路线图 / `6f508d4` 轨道B-followup / `184c0c6` 轨道C 实装包拆分 + 本 release commit）：三轨 A+B+C 同日完成 38 条老师反馈的「设计 → 拍板 → 实装 brief」全闭环。SOP §4 必改 6 处全同步：CHANGELOG / WIP 头部 / 版本演变一览 / v0.7.0_AC叙事.md（CC 起草等审）/ raw/2026-04-30.md §9 / git tag 等 itsuki 明示。**仍 ❌ 不动**：#21 老龄宿管老师 iPad UI / #30 教师当天代录 — B/C 范围外，留 v0.7.x patch 单议题处理。 <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-30 by [Mac-轨道C] — **轨道 C close**：(1) 起手按 itsuki prompt 字面新建了 3 个 `REQUIREMENTS.md`，被 itsuki 指出违反"既存 LOG 已覆盖 + 单源真值"原则 → 全合并到既存 LOG（backend `BACKEND_DESIGN_LOG.md` 新建对称 / iOS+Web LOG §11 v1.0 实装清单 append + 砍重复段）+ 删原 REQUIREMENTS.md (2) **当日 25+ 条决策清完**：D1 SendGrid（自建 SMTP deliverability 劝退）/ D2-D9 一次过按 CC 推荐 / D5+I6+D10 注册即用 / D11 担任单独表 `class_teacher_assignment` / D12 ENUM 加管理係 / W1 升级 TS+Vite+Zustand / I1-I10 + W2-W8 一次过 (3) **⭐⭐⭐ 实物表 vs LINE 文字 evidence 推翻** — itsuki 给 2 张实物外泊届表，CC 之前所有 chain 推测被推翻：担任 + 管理係 必有（LINE 漏写）/ 国際交流課長 实际不存在（LINE 误写）/ 一般外泊 = 3 人 vs CC 推 2 人 / 留学生外泊 = 5 人 vs CC 推 4 人 → system_features §7.2.2 修订 + backend D4 ✅ + I11 / W9 实装 brief 调整 (4) `CLAUDE.md` + `00_admin/文件结构指南.md` 加 BACKEND_DESIGN_LOG 指针 (5) `TODO.md` 加「📦 轨道 C」section 含 evidence 缺口（帰省 / 帰国 实物表 ×4 + 担任 seed）(6) `raw/2026-04-30.md §7` dump 完整含 ⭐⭐⭐ AC 候选「信息源选择 lesson — chat 文字 vs 物理事实」+ CC 4 mistake 自审。 <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-30 晚 by [Mac-轨道B] — **轨道 B close**（commit `4272fc7`）：§9 8 条 (a)-(h) + Q12 全部拍板 + 落地 `system_features.md` 8 处章节（§3.3 寮物理关系 / §3.4 账号运用 4-30 修订 / §4.2 学号生命周期 / §5 房间号 M/A/W 编码新建 / §6 改动履历字段重分类 / §7.1+§7.10+§7.13 矩阵+通知 / §7.3 晚自习 UX 大扩充 / §8.1+§8.6 数据模型 + §9 全 close + §10 改订历史 +1 行）+ `raw/2026-04-30.md` 新建（轨道 A §1-§4 38 条 baseline + 沟通规则升级 ⭐⭐ AC 候选 + 轨道 B §5 8 条拍板含 (d) 指导履歴 scope 警觉 + (h) memory 自我修正 ⭐⭐ AC 候选 + §6 § 符号偏好 ⭐⭐ AC 候选）+ WIP §🔄 [Mac-轨道B] 标 ✅ DONE。**不 bump v0.6.0**（itsuki 明示）— 等轨道 C 完成统一评估。 <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-29 晚 by [Mac-主会话] — **v0.6.0 close**（commit `fd111be`、tag 已打、push 已发）：(1) **老师 4-29 LINE 38 条受领** → TODO.md 顶部最高优先级 backlog + R1-R4 4 条硬约束锁定 + Q1-Q12 已答 11 个 + itsuki 4 条砍/留（学生发帖/社区/匿名 砍 + 音乐 留）(2) **RollCall_Spec.md 5 处时序修订**：§4.2 老师时刻表加列「应开始 -5min / 兜底自动 -3min」+ §5.2 流程 3→5 步 + §5.4 推翻平移规则改"窗口固定" + §5.5 自动开始时点 window_start → on_time_end-3min + §5.6 「点呼総結」中层页新增（4 区块：缺席/迟到/特殊要求/外宿自动跳过）+ 附录 A.4 ✅ CLOSED (3) **system_features.md 中文骨架大重写**：357→830 行，删文件级 v0.x 版本号（违反单源真值）+ §2 R1-R4 顶部新章 + §3 5 角色+设备分布 + §7 14 子节功能矩阵全覆盖老师 38 条 + §8 数据模型扩充（applications/study/events/bus/meals/teachers + R4 一致性 CHECK）+ APPENDIX A 老师 LINE 原文 evidence (4) **03_dev demo/v1 分离**：backend/teacher_web/student_ios 各自分 demo/v1 + 4 README.md 占位 + bin/sync-ios-refs.sh 路径修正 designs→demo + LATEST.md/文件结构指南.md 同步 (5) **AC 记录**：raw §13 ⭐⭐⭐ 档案体系治理思维（~2000 字方法论级，"整理一次不够要建立规范"）+ §14 ⭐⭐ CC 第一次完整跑 SOP 自主决策 bump (6) **CLAUDE.md / CLAUDE_CODE_记录指南.md** 触发清单加一条「档案体系/文件管理规范 元思考」让 CC 主动识别同类元决策 (7) **SOP §4 必改 6 处全同步**：CHANGELOG / WIP 头部 / 版本演变一览 / v0.6.0_AC叙事.md（CC 起草等 itsuki 审）/ raw §14 / git tag v0.6.0 (8) **3 commit chain**：0d1da76（itsuki cleanup checkpoint） → d590159（CLAUDE.md 指针化 by 别会话） → fd111be（本 release）。 <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-29 下午 by [Mac-VersionMgmt-CC] — **版本管理总修 + v0.4.0+v0.5.0 双 minor close**：(1) `00_admin/版本管理SOP.md` 建立（运行手册 12 节，和 iCloud 教科书分工）(2) **4 层叠加机制让 Claude 必读 SOP**：CLAUDE.md inline 5 条核心 + WIP 头部当前版本行 + pre-commit hook 改 spec 提醒 + §会话结束 第 4 项 30 秒 bump 判断 (3) CHANGELOG `[0.4.0-wip]` → `[0.4.0]` + 新建 `[0.5.0]`（4-21 → 4-29 9 天累积 15 commit + 本 release commit 一次 close）(4) **11 文件去 `_v0.1` 后缀**（另一会话 14:06 已 git mv，本会话补 36 个活跃文档 perl 引用替换 + 5 类例外清单）(5) `v0.4.0_AC叙事.md` + `v0.5.0_AC叙事.md`（按 v0.3.0 模板 6 节，留 itsuki 自补面试原话标注；v0.5.0 标"项目第一个 stakeholder-facing 版本"特殊地位）(6) 双 git tag v0.4.0 + v0.5.0 已打 + push GitHub (7) 文档同步点清单 §9 / 文件结构指南 / 版本演变一览 全部联动更新。`raw/2026-04-29.md §11` ⭐⭐⭐ #AC候选 dump（失败转成系统性解法 / 4 层 fault-tolerant 设计）。 <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-29 上午 by [Mac-Web-CC] — **Web 4-28 demo prep 收尾**：(1) **roster 削减 4 男+3 女**（リュウ/田中 隼人/ゴテンウ/ヨウシエン + リシンさん/ソンキゼン/ゴキンウ）+ **ghost student 全清扫** 3 文件 sed 1:1 替换 5 名 5 房间号 (2) **crash bug 修 2 处**（startSession seeded[8] / NotificationsPage roster[3] — hardcoded index 不防御短 roster）(3) **個人番号 6 桁化跟 iOS 对齐**（DEMO_SEED_NO=060218 单源 + sid-based 判定 + accounts.jsx 番号列 70→130px + 「次の新規 07」→「フォーマット 06????」）(4) **行事カレンダー仿 iOS**（月グリッド + 选择日列表 + ＋追加 modal 复用 ModalShell 共有）(5) **リクエスト曲管理 男女寮分け + 提出順 + 承認/拒否ワークフロー**（#番号 寮×朝/晩 4 組合別自動採番）(6) **主页ショートカット URL 自动检测 LAN IP**（demo_server.py /api/server-info + manual fallback + localStorage）+ 上下重複の上カード削除 (7) **全页面 maxWidth 砍** sed 1 命令 9 容器 → iPad/Mac 浏览器自适应 (8) **巴士平日登校便修正** 寮発→岡山駅西口発 7:30 単一便 (9) **細部文案 4 件**：匿名建議 自販機 / 記録 Shortcut→スマホ / override 閾値超で入寮→定刻に間に合わず / 期限後→期限内 (10) **デフォルト中文回答漂移** 自我観察 → memory feedback_default_chinese_response.md。`raw/2026-04-29.md` 10 section（AC 候補 ⭐ 5 件）。 <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-23 夜 by [Mac-demo-sprint] — **D3 設計ラッシュ + 03_dev 重構**：(1) **学号体系 6 桁拍板**（学年 × 組 × 番号、中高一貫 6 年制、A=01/B=02、060218 = 高3 B 18、リュウ イヒ demo seed 00 → 060218）(2) **跨会话同步規則 A+B+C**（system_features.md 新建 = iOS+Web+後端共用真值 / `bin/sync-ios-refs.sh` 建立 / CLAUDE.md 明文ルール）(3) **[iOS-Swift-CC] との独立収束確認**（両会話が独立に 6 桁規則到達、`00_admin/跨会话_ios_共享决策.md` + 本会話の system_features 互指ポインタで統合）(4) **学生改动履歴（監査ログ）規格**（学号/房间号/メール/電話/パスワード事実 全記録、老师 Web アクティビティ履歴 tab + 学生 App 変更履歴）(5) **房间号管理**（注册時学生手入力 + v1.1 老师 Web 一括分配 drag & drop + 学生 App 自動受信）(6) **コミュニティ 拆分決定**（通報保留 / 宅配+忘れ物 フロント業務へ / リクエスト曲 古い順 + 寮内 BGM / 朝晩字段 pending）(7) **男寮教員 新股/小林/難波 + 姓後先生統一**（theme.jsx TEACHERS + applications.jsx 承認 workflow 全 approver）(8) **巴士実公告 2026-03-22 保管** → `06_assets/real_samples/bus_notice_2026-03-22_特別運行便.md` + 規格入 system_features §6.6（閲覧/CRUD/乗車名簿）(9) **03_dev/ 物理重構**: `demo_4-28/` 嵌套解除 → `03_dev/{backend,teacher_web,student_ios}/` 平置化 + `Student/DMSDStudentApp(iOS)` → `99_archive/2026-03-08_throwaway_ios_swift/` + 27 MD ファイル path 引用更新 + `03_dev/LATEST.md` 新建（最新 HTML 索引）(10) **HTML build 順序明文化**: jsx 改 → `rebuild.command` → `build_single_file.py` の 3 段階。Prototype_v3.html 凍結版削除（密码 12345678 弾き事故防止）。`raw/2026-04-23.md` 10 section 新建（AC 候補 🌟 5 件）。 <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-22 夜 by [Code-Agent] — **4-28 demo 收尾**：Round 3 導入+解包+bug修+日語 2 輪 QA+single-file 打包(32MB) + 点呼機代替（demo_server.py + polling TTS）+ accounts.jsx 学生管理 + 外泊期限規則 + ./tomoshibi CLI <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-22 夜 by [Mac-demo-sprint] — 砍 Pi 文档层落地 + 35 问管理员清单 + Wi-Fi 测试手册（文档会话方向；和本 Code-Agent 代码方向配对） <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-22 晚 by [Code-Agent] — Web 学生アカウント管理页面新建（`accounts.jsx` + `ACCOUNTS` seed 24 人 + Shell nav + modal 2 tab + iOS 设计 §9.2 ✅） <!-- VERSION_OK -->
**上一次更新（保留参考）**: 2026-04-22 晚 by [Mac-demo-sprint] — iOS 前端设计 Round 1 Prompt 落盘（3 按钮 nav + Home omnibus + 中央点呼 sheet + 注册 4-step + 锁定升级 + 00 号 seed + Round1_Prompt.md 38KB / 878 行 / 73 画面 Phase A+B 一次出） <!-- VERSION_OK -->
**上上一次更新（保留参考）**: 2026-04-22 下午 by [Code-Agent] — Web Round 3 导入 + 解包 + 4 UI 调整 + 2 次白屏 debug + 日语 native 文案审查 + single-file bundle 脚本化 <!-- VERSION_OK -->
**当前版本**: 见 `CHANGELOG.md` 顶部 · **重大状态**: **4-28 管理员 demo 为最高优先级** — 7 天冲刺（4-21→4-28）— 硬件 Pi 3A+（推翻 4-20 Pi 4B 2GB）+ 采购分阶段 Demo 1 台 / 部署 3 台 + 范围硬裁剪（保点呼机全 + Web 全 + iOS Xcode + 快捷指令代 App tap / 砍 Android / 砍外壳 / 砍风控）+ sprint plan 建立。v0.4.0 S2/S3 + Device_Contract 主线由 [Mac-主会话] 维护，本会话不碰。 <!-- VERSION_OK -->


---

## 🎯 当前焦点

**4-28 宿舍管理员 Demo 冲刺（2026-04-21 启动 → 4-28 Demo Day）** — 最高优先级，真实 stakeholder（宿舍管理员）决定是否采纳系统。权威 sprint plan：`99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/sprint.md`。

**范围**（2026-04-22 二次修订 — 砍 Pi 硬件）：
- ✅ 保：老师 Web 全（记录/实时/外宿/归国审批）+ iOS Xcode 模拟器（6 屏）+ **iPhone Shortcuts + itsuki 自有 NFC 卡**（代替 Pi 点呼机）+ **iPad Safari Web Speech API 日语 TTS**（代替 Pi 喇叭）
- ❌ 砍：**Pi 点呼机硬件（4-22 新砍）** / 点呼机外壳 / Android 端 / 完整风控 / 多点呼机协调

**硬件**（2026-04-22 再次推翻 4-21 "Pi 3A+ 下单"计划）：**Demo 阶段 0 采购**
- 理由：7 天 deadline + 零基础，PN532 I²C 驱动 + TTS + 接线是最大失败风险
- Demo 成功率 60% → 95%（砍硬件后）
- **上线版 v1.0 仍按 Pi 3A+ 方案**（`02_design/hardware_design.md §2.1` 保留，管理员采纳后启动）
- 详见 `99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/scope_tier.md §0.1` + `hardware_design.md §4.1`

**并行**：v0.4.0 主线（S2/S3 + Device_Contract）由 [Mac-主会话] 维护，demo sprint 不动 `00_admin/v0.4.0_*.md`。

**历史焦点（保留参考）**：v0.4.0 开工（2026-04-21 上午 S2/S3 draft + Device_Contract 骨架 + OQ1-9）。 <!-- VERSION_OK -->

**历史焦点（上个阶段收尾，保留参考）**：4-19 G2 决策 + 点呼流程定稿 + 项目审查 backlog 落地 — 架构 / 流程 / 记录规则全部重大更新。

**架构层（4-19 重大转向）**:
- **G2 拍板**: 取消 Phase 1 / Phase 2 分阶段上线；**v1.0 直接 iOS + Android + 卡 完整版一次上线**。开发内部仍按 M1→M5 里程碑顺序（风险兜底：做不完至少 M1+M2 可 demo）。
- **点呼路径**: A 路径（NFC 卡 tap 点呼机 PN532）+ B 路径（iPhone / Android 都走 tap 外贴静态 NFC 贴纸）三路共存；Android **不走 HCE**，保持跨平台一致。
- **核心原则保留**: thin client / thick server；服务器唯一判定者；语音播报防作弊。

**卡生命周期（4-19 定稿）**:
- 空白 NTAG215 + 学生自贴"名字便签"（为毕业回收复用，不贴学号）
- App 内"绑定卡片" → tap 卡 → UID 录入学生账户（自助绑定）
- 没手机学生走"管理员代录"特殊通道
- 丢卡：新卡发 + 新绑定 + 旧 UID 作废（不收钱）
- 毕业：清除卡 UID 绑定（账户保留作历史记录），卡可回收给下一届

**App 账号规则（4-19 定稿）**:
- 注册：姓名 + 生日 + 性别（**不要学号**）
- 一设备一账号；换设备必须老师→管理员后台操作（学生不能自助换机）
- Android 分发：自建网站托管 APK，学生下载

**点呼规则（4-19 定稿）**:
- 三路径（卡 / iPhone / Android）并存，学生随便用
- 每时间窗只能点呼一次（幂等）

**记录体系更新（4-19）**:
- `00_admin/CLAUDE_CODE_记录指南.md §3.4` 新增"记录详细度要求"（5 模块 + 篇幅指引 + 失败模式清单）
- raw 每条目标 500-2000 字（按重要度），不再是 100-300 字的"决策快照"

**仍挂的遗留（下次会话讨论）**:
- iPhone / Android tap 贴纸的技术细节（Background Tag Reading / Android 后台唤 App）
- 一设备一账号的具体实现（设备指纹 / 硬件 ID / 推送 token）
- 风控策略起草（CC 起草 → itsuki review）
- Demo 范围构思（G2 兜底）
- 点呼机硬件零件选型（最后做，等 spec 定）
- 宿舍点呼位置网络情况（itsuki 问老师）

**下一个大动作（v0.3.1 Tier 1，1-3 天）**: **文档同步 + AC readiness 第一步**（详见 `00_admin/2026-04-19_项目审查_backlog.md` Tier 1，87 条漏洞里的 11 条）—— 根目录 README / project_evolution 补 3 次转折 / decision_log 补 3 条 / progress_overview 全面更新 / CLAUDE.md 修过期表述 / 志望動機 #5 占位 / 原创设计 showcase / AI 协作坦诚声明。

**v0.3.0 → v0.3.1 → v0.4.0 → v0.5.0 → v0.6.0 路线图**见 backlog Part 5。

---

## 🔄 进行中的任务

> **2026-04-30 启动**: 38 条老师反馈 3 轨并行 — 路线图详见 `00_admin/TODO.md §🛣️ 推进路线图`。

### [Mac-主会话] 三端对齐审计（2026-05-01 ⏸ **阻塞中**、等 Q1/Q2 答复）

**任务**: itsuki「ios app 还有 web 还有后端三个都过几遍然后对齐和修正」。

**完成 (1/2)**: 调查 + 失配清单 + 方案提案。
- 3 Explore subagent 并行扫 backend v1 / iOS v1 Swift / teacher_web → 交叉对齐
- **失配清单 F1-F15**: 🔴 阻塞 7 条 / 🟡 体面 5 条 / ⚪ 可延后 3 条
- **修正方案 ABC**: A = iOS 5 处映射 ~150 行 + backend reason / B = A + APIClient + 注册全流程 / C = B + 文档同步 + Web v1
- CC 推荐先 A（无 design trade-off、纯字段映射）
- **dump**: `05_logs/raw/2026-05-01.md`

**阻塞 (2/2)**: itsuki 答 Q1 + Q2 后才动手。
- **Q1**: status 枚举对齐 — iOS 6 値 / backend 5 値，cancelled↔withdrawn 合并？draft 保留？returned 砍？
- **Q2**: reason 字段归属 — backend 加 / iOS 砍 / hack 进 leave_method？

**下次会话执行点**（A 方案）:
- `03_dev/student_ios/v1/TomoshibiApp/Features/Apply/ApplyStubs.swift` — kind 映射 + stay_locations 形状 + meals_skip 形状 + 砍 student_id + 处理 reason
- `03_dev/student_ios/v1/TomoshibiApp/Foundation/Seed/SeedModels.swift` — ApplicationItem.status 加 approved_partial / withdrawn
- `03_dev/backend/v1/app/{models,schemas}.py` — Q2 选 A 时加 reason 字段 + Alembic（後續）

**不动**: teacher_web 任何文件（demo 锁定 / v1 未开工）/ system_features.md / DESIGN_LOG。

---

### [Code-iOS-会话C] iOS 状态列表 + 资源显示（2026-04-30 晚 ✅ **DONE**）

**任务**: 老師 38 条反馈 #5 / #8 / #9 的 iOS 实装（mock 数据，B 后端就位后切真 API）。

**新增文件**（全部位于尚未 git 追踪的 `03_dev/student_ios/v1/TomoshibiApp/`）:
- `Features/StayList/StayListStubs.swift` — `StayListView`（申請履歴 一覧 + chain 摘要 dot 列）+ `StayDetailView`（縦 timeline 各役职 决定 + 时刻 + comment）+ `ApprovalChainBuilder`（IOS_DESIGN_LOG §11.9 I11 規則: 外泊・一般 = 3 行 / 外泊・留学生 = 5 行 / 帰省・帰国 = 暂同外泊待 evidence）+ `BusListMock` 占位
- `Features/Schedule/ScheduleStubs.swift` — `ScheduleView`（任意月スクロール対応の月历 + 日选 + 多 dot 表示），`YearMonth` 値型自前計算（DateComponents + Asia/Tokyo 固定）。詳細は既存 `EventDetailView`（CommunityStubs.swift）再利用
- `Features/BusList/BusListStubs.swift` — `BusListView`（`BusKind` フィルタ tab + 空港便 only switch + 日付別グループ）+ `SpecialBusRoute` 模型（system_features.md §7.6.1 bus_routes に対応）+ `BusListMock`（SEED.busSchedule から派生）

**修改ファイル** (3 件):
- `Foundation/Routing/Route.swift` — case 追加: `.stayList` / `.stayDetail(id:)` / `.schedule` / `.busList` + displayName 4 件 + isMyBranch 拡張
- `Root/RootView.swift` — 4 ケースの dispatch 追加（§4 V1 リファレンス系）
- `Features/MyPage/MyPageStubs.swift` — 「申請履歴」grid block の route を `.apply` → `.stayList` に修正（design 整合）+ Settings list に「行事予定」「特別運航便」2 行追加 → 3 view 全部マイページから到達可能

**API 対応（B 未到位 → 全件 SEED ベースの mock 返却）**:
| iOS 画面 | backend API（B 完了後切替） | mock 出処 |
|---|---|---|
| `StayListView` | `GET /applications/mine` | `StayListMock.all`（SEED.applications を StayApplication に拡張、kind/status から chain 自動生成）|
| `StayDetailView` | `GET /applications/:id` | 同上 |
| `ScheduleView` | `GET /events?from=&to=` | `SEED.events` 直読み |
| `BusListView` | `GET /buses` | `SEED.busSchedule` を `SpecialBusRoute` に変換 |

**チェック**: `swiftc -typecheck` 全 31 ファイルで 0 error / 0 warning（`xcrun --sdk iphonesimulator` で確認済）。Xcode 開いた時の SourceKit「Cannot find type X」は cross-file 解析ノイズで実コンパイルでは無視可。

**未対応 / 申送り**:
- 帰省・帰国届の chain 真値 = itsuki 实物表 evidence ×4 待ち。`ApprovalChainBuilder.holidayChain` は暫定で外泊と同 chain。実物表入手後は同関数の中身だけ調整（呼出側 view 修正不要）。
- 留学生フラグ: `SEED.user` に `is_overseas` 無しなので `StayListMock.isOverseas = true` ハードコード（リュウ イヒ = 留学生扱い）。`User` モデル拡張は会话 A の StayForm 側で既に決まってる可能性あり、要確認。
- API 接続切替時の取り回し: `StayListMock.all` → `URLSession + async/await`（IOS_DESIGN_LOG §11.9 I2）に置換。view 側の `@State`/`@StateObject` パターンは未変更で済むよう、static var → ObservableObject に移行する形が良さそう。

**git commit 対応**: `03_dev/student_ios/v1/TomoshibiApp/` 全体が untracked、A/B/C 三轨混在の WIP。本会話単独 commit は他轨道 untracked Swift コード未取込のため clean clone 編集失敗 → **commit 見送り**、itsuki が三轨収束時に統一 commit 推奨。



### [Mac-轨道A] 38 条状态盘点（2026-04-30 ✅ **DONE**）

**完成** 2026-04-30 by 当前主会话
**结果**（B 标准 — UI 画过 + 字段都列了 + API 形状定了 三项全 = ✅）: ✅ 设计完成 7 / 39（#16-#20 #37 #38）+ ⏳ 设计部分 27 / 39 + ❌ 几乎没碰 3 / 39（#21 老龄一本道 / #28 寮务追加删除 / #30 教师代录）+ 🚫 已砍 2 / 39（#35 学生发帖 / #36 匿名建议）+ 🔧 待实装 37 / 39（轨道 C）
**历史**: 4-30 第一版 baseline 用 CC 自定宽松标准（"列入 system_features.md = ✅" → ✅ 34/39）→ itsuki 推翻 → B 标准重做（本节）
**落地**: `00_admin/TODO.md §📊 baseline` + 38 条逐条 emoji 前缀 + Q1-Q11 ✅ + Q12 ⚠️ 矛盾保留
**raw dump**: `05_logs/raw/2026-04-30.md §1-§4`（§4 ⭐⭐ 沟通规则升级 AC 候选）
**已 commit**: `604bc9b`（v0.7.0 归入）

### [Mac-轨道B] §9 + Q12 拍板（2026-04-30 ✅ **DONE**）

**完成** 2026-04-30 下午~晚 by 本会话(Mac-轨道B)
**结果**: 8 条 (a)-(h) + Q12 全 close + 落地到 `system_features.md §3-§8` 对应位置
- (a) 罚则数值 hardcode 常量 → §7.12 / (b) 学号变更老师 Web 全权 → §4.2/§6/§7.1/§7.13 / (c) 房间号 M/A/W 编码 → §5+§8.1 / (d) 指导履历 C 案 申请开示 → §7.10/§7.13/§8.6 / (e) 寮監账号 任设备登+前台禁注册 → §3.4/§7.1 / (f) 晚自习 7 tab+双视图 → §7.3 / (g) 寮物理关系 close+事实记录 → §3.3 / (h) 杭田 UI close 不矛盾
**落地**: `02_design/system_features.md` 8 处章节 + §10 改订历史 + 头部时间戳
**raw dump**: `05_logs/raw/2026-04-30.md §5`(8 条拍板)+ §6(§ 符号 AC 候选 ⭐⭐)
**已 commit**(本 commit), v0.6.0 不 bump(itsuki 明示)— 等轨道 C 完成后统一评估

### ✅ [Mac-会话B-backend] backend v1.0 P0 起手（2026-04-30 夜 ✅ **DONE**）

**完成** 2026-04-30 夜 by 本会话(Mac-会话B-backend)
**目的**: 老師 38 条反馈の #2 schema / #5 GET / #6 邮件 / #7 食堂 Excel — 4 任務まとめて backend v1.0 起手版を 0 → 1 で築く（轨道 C で `BACKEND_DESIGN_LOG.md` D1-D12 拍板済 → そのまま実装に落とす）。

**主写区**: `03_dev/backend/v1/`（新規 14 ファイル）
- `app/` — FastAPI app: main.py / config.py / database.py / deps.py / security.py / models.py / schemas.py / routers/{auth,applications,meals,notifications}.py / services/{approval_chain,email,meals}.py
- `tests/` — conftest.py + test_smoke.py（19 ケース全 pass）
- `seed.py` — 役职 7 種網羅 + 担任 2 + 学生 2（留学生 + 一般）seed
- `requirements.txt` / `.env.example` / `.gitignore` / `README.md`(更新)

**完成定义チェック**:
- ✅ POST /api/v1/applications（提出 + chain 自動生成 + R1 邮件 trigger）
- ✅ GET /api/v1/applications/{id}（#5 承认状态、学生本人 / 教師 dorm filter 両対応）
- ✅ GET /api/v1/applications/mine（自分の履歴）
- ✅ GET /api/v1/meals/export（食堂 Excel — 2 sheet 双层）+ /meals/calc（JSON debug）
- ✅ POST /api/v1/notifications/test（SendGrid smoke）
- ✅ POST /api/v1/sessions/{student,teacher}（JWT login）
- ✅ 表創建（`Base.metadata.create_all`、Alembic 後續）+ 役职 seed（7 種 + 担任）
- ✅ SendGrid 発信ロジック（実 API 接続は API_KEY 未設定なので「dev mode = pending 扱い」記録、本物 KEY 入れ次第そのまま稼働）

**chain 設計（D4 实物表 evidence 反映）**:
- 外泊（一般）= 担任 + 寮務課長 + 管理係 = 3 ✅ 確定
- 外泊（留学生）= 担任 + 国際交流部長 + 寮務課長 + 寮務部長 + 管理係 = 5 ✅ 確定
- 帰省・帰国 = ⏳ 暫定（外泊 chain - 国際交流）/ `PROVISIONAL_CHAINS` flag + response header `X-Approval-Chain-Provisional: true` で警告
- 实物表 ×4 入手後は `app/services/approval_chain.py` の `EXTERNAL_ROLES_BY_KIND` 定数だけ書き換える

**残課題**（後續会話）: Alembic migration / async 化 / Refresh token rotation / lock_level 升級 / 役职承認 #10-#13 / コメント #13 / 学習出席 / 点呼 / 寮監事務室 一覧。

### ✅ [Mac-轨道C] 实装包拆分（2026-04-30 启动 → 2026-04-30 close）

**最終認領**:
- `03_dev/backend/BACKEND_DESIGN_LOG.md`（**新建** — backend 専属設計 + v1.0 实装清单、对称 iOS / Web 既存 LOG）
- `03_dev/student_ios/IOS_DESIGN_LOG.md` §11（**append** — v1.0 实装清单）
- `03_dev/teacher_web/WEB_DESIGN_LOG.md` §11（**append** — v1.0 实装清单）
- `02_design/system_features.md §7.2.2`（**修订** — 实物表 evidence 推翻老师 LINE 文字推测、承认 chain 表重写）
- `00_admin/TODO.md`（路线图 + evidence 待补 section 加）
- `CLAUDE.md` + `00_admin/文件结构指南.md`（指针更新加 BACKEND_DESIGN_LOG）
- `05_logs/raw/2026-04-30.md` §7（dump — 实装包拆分過程 + ⭐⭐⭐ 实物表 vs LINE 文字 evidence 教训）

**path 调整**: 起手按 itsuki prompt 字面新建了 3 个 `REQUIREMENTS.md`，被 itsuki 指出违反"既存设计文档 + 单源真值原则"→ 改名 backend / 合并 iOS+Web 内容到既存 LOG → 删除原 REQUIREMENTS.md。

**当日決策（25+ 条）**:
- ✅ D1 SendGrid / D2-D9 一次过按 CC 推荐 / D4 实物表为准（外泊 chain）/ D5+I6+D10 注册即用 / D11 单独表 / D12 ENUM 加管理係
- ✅ I1-I10 一次过按 CC 推荐 / I9-I10 既決確認 / I11 实装层（待 D11/D12 实施）
- ✅ W1 升级 TS+Vite+Zustand / W2-W8 一次过 / W9 实装层

**残 evidence**: 帰省 / 帰国 实物表 ×4 张（itsuki 下次见老师拿）+ 担任名簿 seed → TODO.md `📦 轨道 C` section 已记。

**不阻塞 code agent 接手**: 学生注册 / login / 学習出席 / 点呼 / 邮件通知 framework / DB schema / API endpoints 全部可干。唯阻塞 = 帰省・帰国届承认 chain 生成函数（外泊已可、暫定実装可、evidence 入った時点で chain 設定値だけ調整）。

### [Mac-demo-sprint] 4-28 Demo 冲刺（D1 · 2026-04-21）

**认领文件**：
- `99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/`（新文件夹，含 README / sprint / scope_tier / ST25DV_fallback / demo_script 5 个档案）
- `02_design/hardware_design.md`（§2.1 + §2.3 + §2.5 + §4 修订）
- `CLAUDE.md` §项目信息硬件/demo 段
- `05_logs/raw/2026-04-21.md`（新建 + 追加）
- `03_dev/backend/`（skeleton 起好，代码后续交其他 agent）
- `00_admin/TODO.md` 顶部加 demo sprint 指针段

**分工（2026-04-21 itsuki 明示）**：
- 本会话 [Mac-demo-sprint] 只做需求/文档/清单
- 前端/后端/iOS/点呼机代码实现交其他 agent 做
- 代码 agent 的需求来源 = `99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/scope_tier.md`

**不动文件**（[Mac-主会话] 认领）：
- `00_admin/v0.4.0_S2_S3_字段draft.md`
- `00_admin/v0.4.0_Device_Contract骨架.md`
- `00_admin/v0.4.0_S系列spec漏洞优先级分析.md`
- `00_admin/2026-04-19_项目审查_backlog.md`
- `CHANGELOG.md`（等 demo 后评估如何纳入版本）

**D1 已完成**：
- [x] 议题 E 拍板（E-1/E-2/E-3/E-4）
- [x] Pi 3A+ 选型推翻 Pi 4B 2GB（5 方案对比 + Pi 3A+ 反直觉胜出）
- [x] MVP 思维：硬件采购分阶段（Demo 1 台 / 部署 3 台）
- [x] `02_design/hardware_design.md` §2.1 + §2.5 + §4 完整修订
- [x] `CLAUDE.md` §项目信息 硬件 + demo 段更新
- [x] `05_logs/raw/2026-04-21.md` 建立（6 条碎片 / 3 条 #AC候选🌟）
- [x] `03_dev/backend/` skeleton 起好（README / requirements / database / models / schemas / ws_manager / main / seed，14 个 API 端点 + WebSocket）
- [x] **Scope 扩展讨论 + Tier 分层拍板**（Tier 1 真跑 / Tier 2 UI skeleton / Tier 3 砍）
- [x] **ST25DV fallback 决策**（方案 A：NTAG215 + iOS Shortcuts Automation，iOS 26 确认）
- [x] **扣分规则拍板**（暂定数字 + discipline_config 可配置表）
- [x] **文件夹化** `99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/`（sprint.md 迁入 + 4 子档新建：README / scope_tier / ST25DV_fallback / demo_script）
- [x] `CLAUDE.md` 第二轮更新（路径 + ST25DV fallback + 扣分可配置）

**D1 剩余**（今晚 / 明天早）：
- [ ] itsuki Amazon 日本下单 Pi 3A+ + 配件（明天 4-22 到）
- [ ] itsuki 淘宝下单 ST25DV16K（供货延迟但仍买，v1.0 上线用）
- [ ] itsuki 看 `demo_4-28/scope_tier.md §5` 补 Tier 1 漏项 / Tier 2 升级项（如需）
- [ ] itsuki 看 `demo_4-28/demo_script.md` 确认台词风格
- [x] 代码 agent 起会话 —— `[Code-Agent]` 2026-04-21 晚接管（下一段认领）

### [Code-Agent] 4-28 Demo 代码实现（D1 onboard · 2026-04-21 晚）

**身份**：代码实现 agent（前端 / 后端 / iOS / Pi 点呼机所有代码），需求来源 = `99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/scope_tier.md`。

**认领文件**（briefing `for_code_agent.md §3` 权限内，**路径根据 itsuki 2026-04-21 "demo 文件不要污染主项目" 指令全部挪到 `03_dev/demo_4-28/` 下**）：
- `03_dev/backend/`（**2026-04-21 晚 itsuki 拍板后 mv 自原 `03_dev/backend/`** —— skeleton 保持完整，README.md path 已同步更新）
- `03_dev/teacher_web/`（新建；**2026-04-21 晚 Claude Design Round 2 handoff bundle 已导入**：`index.html` + `round2/*.jsx` 6 组件 + `standalone-offline-backup.html` 8.4MB + `handoff/` 归档含 chat1.md AC 素材；设计方向 = Ryo / Noto Sans JP / 近黑+コバルト；Round 2 已做 login + roll-call dashboard + live 座席表 + override modal 4 项，Tier 1 剩 7 页 + Tier 2 15 skeleton 留 Round 3；D3 起把 seed 换成 API fetch + WS 订阅）
- `03_dev/student_ios/`（新建，SwiftUI；已建 `DESIGN_BRIEF.md` = Claude Design 任务书，iOS 版和 Web 版分开 project）
- `03_dev/device/`（新建，Python + PN532 + pyttsx3）
- `99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/questions_for_requirements.md`（新建，提问队列，只写自己的问题段，不改 itsuki/需求会话的回复段）
- `00_admin/WIP.md` 本段（进度登记）

**不碰**：`99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/{README,sprint,scope_tier,demo_script,ST25DV_fallback,for_code_agent}.md` / `01_specs/` / `02_design/` / `00_admin/v0.4.0_*.md` / `CLAUDE.md` / `05_logs/raw/` / `CHANGELOG.md` / `00_admin/2026-04-19_项目审查_backlog.md` / 旧 `03_dev/Student/`（throwaway）。

**D1 已完成**：
- [x] 读完 briefing 8 个文件（CLAUDE / WIP / demo_4-28 5 档 / hardware_design / backend README）+ 实际看了 backend 全 6 个源码文件摸清缺口
- [x] 建 `questions_for_requirements.md` 首批 5 阻塞 Q + 3 非阻塞建议
- [x] 识别 Tier 1 实际技术缺口：`Checkin.status` 字段 / `roll_call/live` 聚合 API / 改判 / 健康 / 请假 / 扣分配置表 / 搜索聚合 6 处
- [x] WIP 登记本段

**D1 剩余 / D2 开工前阻塞**：
- [ ] itsuki 回复 Q1-Q5（questions_for_requirements.md）→ 否则 schema 不敢定
- [ ] Q 回复 + D2 上午开工：backend `models.Checkin.status` + discipline_config 表 + seed 扩到 30 学生 + 造扣分历史
- [ ] D2 下午：端到端本地测 `POST /api/checkin` + WS 推送（先用 `wscat` 测）

**当前等**：
- itsuki 明天（4-22）把 `round3_handoff/` 整个文件夹 + `Round3_Prompt.md` 内容贴到 Claude Design → 产出 Round 3 prototype → 给回 share link
- 硬件 4-22 到货 → itsuki 烧 SD + 连 WiFi + SSH（D2）
- D2 上午后端开工：`models.Checkin.status` 加字段 + `discipline_config` 表 + seed 扩 30 学生 + 造扣分历史 + 6 API 缺口补

**今晚（D1 收尾）Code-Agent 产出清单**：
- [x] 读 briefing 8 档 + 盘点 backend 缺口（6 处）
- [x] questions_for_requirements.md 5 阻塞 Q + 3 非阻塞 + itsuki Q1-Q11 答复归档
- [x] backend + 3 新目录挪到 `03_dev/demo_4-28/`
- [x] Q2 late 状态理解错 → itsuki 纠正 → 回归 spec §4.1 §5.3 权威规则
- [x] Claude Design Round 2 bundle 导入（index.html + 6 jsx + 8.4MB 内嵌 + handoff 归档）
- [x] Tomoshibi rebrand 落地 Web（logo 图、wordmark、title）
- [x] Round 3 prompt 敲稿 14 节（14 小修改 / 新增）+ round3_handoff/ 文件夹完整（prompt .md + .txt + 3 图 + README）
- [x] WEB_DESIGN_LOG.md 归档所有 Web 设计决策（10 节 20KB）
- [x] 文件结构指南.md 建立（全 repo 文件级清单 + 权限 + 反向索引）
- [x] CLAUDE.md §目录结构 + §单源真值 同步加指针
- [x] 文档同步点清单.md §2 升级双层
- [x] AC 记录：raw/2026-04-21.md append 7 条（3 条 #AC候选🌟）

---

## ✅ 最近完成(24-48 小时内)

### 2026-04-22 晚（iOS 前端设计 Round 1 Prompt 落盘）

- **[Mac-demo-sprint]** **iOS 架构重构拍板**：推翻 [Code-Agent] 2026-04-21 晚写的 4-tab 旧方案（`student_ios/DESIGN_BRIEF.md v1` 已归档）→ 新架构 3 按钮 nav（申し込み / ⭐点呼 action button / マイページ）+ Home omnibus（承载除 2 tab 外所有功能：Community / 扣分 / 快递 / 遗失物 / 点歌 / 通知）+ 中央点呼 sheet flow（iOS 26 Liquid Glass 毛玻璃 + SUNTORY ジハンピ 风格 4 态动画）+ 注册 flow 4-step（氏名 / 生日→自动分寮 / 学生区分 一般 or サッカー部 / 联络先 / 密码 ×2）+ 锁定升级 5 阶段（30 秒 → 1 分 → 5 分 → 30 分 → 1 时 → 永久锁）+ 00 号测试账户 seed "demo 魔法"（注册流程演示 + 实际登入预 seed 00 号 リュウ イヒ · 4 分扣分）+ 持续顶部点呼 bar 全 App（3 态 + 可点反馈 sheet）+ 导航规则（Level 1 Home icon 简笔画 / L2+ ← / 长按 0.4 秒 breadcrumb）
- **[Mac-demo-sprint]** **Q1-Q8 + N1-N20 全答**：iPhone 17 Pro + iOS 26 Liquid Glass / Home 加 tabs+sections / Claude Design 一轮全出 Phase A+B / logo 仅 splash 用 / 暗色模式做 / 宿舍墙实名 / Demo 切学生砍（注册 flow 取代）等 28 条决策归档进 `IOS_DESIGN_LOG.md`
- **[Mac-demo-sprint]** 落盘 4 档件 + 4 参考图到 `03_dev/student_ios/`：
  - `IOS_DESIGN_LOG.md`（303 行 / 15 KB） — 决策归档
  - `DESIGN_BRIEF.md`（168 行 / 10 KB） — 实装进度追踪
  - `round1_handoff/Round1_Prompt.md`（**878 行 / 38 KB**）— 发给 Claude Design 的完整 prompt（73 画面字段级 spec + Phase A 3 variations 指令 + Phase B 一次出 + Seed data + Interactive behaviors）
  - `round1_handoff/README.md` — itsuki 发送手順
  - `round1_handoff/references/` 4 图（logo / 手绘 nav / SUNTORY 扫 sheet ×2，从 `.claude/image-cache/` 导入）
  - 旧 v1 DESIGN_BRIEF 重命名 `_archived_v1_DESIGN_BRIEF_2026-04-21.md` 保留推翻痕迹
- **[Mac-demo-sprint]** **CLAUDE.md §账号规则 patch 到 v3**：推翻 2026-04-20 议题 C "入学日面签" → App 内 4-step 注册即激活 + 锁定升级 + 账号 ID 分配（00 demo seed / 01+ 真实）+ 密码重置走宿管后台（feedback_overruled_rule_means_update_rule 执行）
- **[Mac-demo-sprint]** **raw log**：`05_logs/raw/2026-04-22_iOS前端设计_Round1.md`（同日主题版，6 条碎片 / 2 条 #AC候选🌟）—— 架构重构心路历程 + 00 号 seed demo 魔法 product thinking + 会话开场方式变化 + 跨文档同步治理
- **[Mac-demo-sprint] 2026-04-22 夜续（收尾段）**：itsuki 已跑 Phase A 3 variations → 选定 → Phase B 73 画面 standalone（1.93 MB）产出。CC 导入 `designs/Tomoshibi_iOS_PhaseB.html` + Python 解包 11 资源 → **QA 产出** `QA_Round1_PhaseB.md`（🔴 C1 中文残留 / C2 データ Web 不一致 / C3 申请类型 8 vs 7 / C4 iPhone frame 双层）→ **CC 直接改 JS 源 + gzip+base64 重打包** 产出 **`Tomoshibi_iOS_PhaseB_v2.html`**（C1 + C2 全修 · 点歌→リクエスト曲 + 宿舍墙→寮ウォール + 快递→宅配 + 晚→晩 全量 + W101→M101 / 女寮→男寮 / 4.0→4.5 + SEED.points/rollcall 重建 · template 剥离 integrity/crossorigin 避 file:// CORS）。C3 写 `Round2_Prompt_C3.md` 待 itsuki 决定（默认接受 Claude Design 8 种重构方案 (iii)）。写 `handoff_for_code_agent.md` 拟做 Xcode WKWebView 壳（~30 行 SwiftUI + CSS override 隐藏 Phase B 自带 iPhone frame + 工程放 `~/dev/TomoshibiiOSApp/` DMSD 外）。
- **[Mac-demo-sprint] ⭐ itsuki 推翻 Xcode 壳方案** → 选 "普通浏览器（Safari）直接打开" → handoff 标 DEPRECATED（保留作推翻痕迹 + post-demo v1.0 Xcode 起点参考）。**Demo 演示路径改 Safari 直开 v2 HTML**（Mac 接大屏 → Safari → file:// → 点 caption "🏠 Home" 快捷 → 走 73 页）。**iOS Round 1 正式收尾** ✅
- **AC log 追加**：raw/2026-04-22_iOS前端设计_Round1.md §20:00（Phase B 导入 + QA + v2 产出）+ §21:00 #AC候选🌟（**itsuki 推翻 Xcode 壳 · 最简工程决策** — CC 写 30 行 SwiftUI + handoff.md + Round 2 prompt 的"最优路径"被 10 字推翻；AC 面试核心素材："AI 提示的完美方案不一定是正确答案 · 过度工程识别能力"）

### 2026-04-22 下午（Web Round 3 导入 + 解包 + debug · [Code-Agent]）

- **[Code-Agent]** Claude Design Round 3 `Tomoshibi_Prototype_v3__Standalone_.html`（9.4 MB）导入 `03_dev/teacher_web/round3/` + Python 脚本解包 manifest（146 资源）→ `round3/src/` 12 组件 + 3 vendor + 130 字体（人类可读）
- **[Code-Agent]** itsuki 走查发现 4 项调整：詳細列宽 / リュウ イヒ 男寮迁移 W101 → M101 / 扣分触发清扫线 / 名前搜索 normalize 去空格
- **[Code-Agent]** 2 次白屏 debug：Round 1 file:// CORS（integrity/crossorigin strip）+ Round 2 数组越界（roster 13 人但 statuses 12 项 → `i % len` 修复）
- **[Code-Agent]** 日语 native 文案审查：名単→リスト / 距 X まで→X まで残り / 晚点呼→晩点呼 / スプレッドシート×入力→食数の自由記入可 等约 12 处中文残留修正
- **[Code-Agent]** `build_single_file.py` 脚本：woff2 字体 base64 inline → `Tomoshibi_v3_single.html` 32 MB（U 盘 demo 兜底）
- **[Code-Agent]** WEB_DESIGN_LOG §1 Timeline + §4.0 Round 3 完整清单 + §9 开放项刷新 + §10 quick-start 更新
- **[Code-Agent]** raw log：`05_logs/raw/2026-04-22.md`（日期版，7 条碎片 / 3 条 #AC候选🌟）

### 2026-04-21（v0.4.0 开工启动 — 不打 tag）

- **[Mac-主会话]** **D21 🟡 ✅** CHANGELOG.md v0.2.0 / v0.3.0 header 加 HH:MM 区分（v0.2.0 → 18:22 / v0.3.0 → 18:53）；CHANGELOG 头部"最后更新"同步到 2026-04-21
- **[Mac-主会话]** **S2 🔴 ⏳** 起草 `00_admin/v0.4.0_S2_S3_字段draft.md §1`：card_uid 完整定义 + 配套 §2.9 卡生命周期 4 字段（char(14) UNIQUE / 多对一到 student_id / 小写 hex）+ 依赖链（S1+S10+S4）+ 备选方案对比
- **[Mac-主会话]** **S3 🔴 ⏳** 同 draft §2：student_status 4 取值 ENUM + 配套 §2.10 学生生命周期 audit 字段 + 对应 spec 附录 C.5 状态转换 + paused 不区分理由 / graduated 保留历史两业务决策待 itsuki 拍板
- **[Mac-主会话]** 新建 `00_admin/v0.4.0_Device_Contract骨架.md`：9 节骨架（目的/职责/HTTP 契约/WS 协议/配置/错误处理/生命周期/硬件/交叉引用）+ 9 个 Open Questions 汇总表（OQ1 mTLS / OQ2 nonce+HMAC / OQ3 HTTP 超时 / OQ4 device 注册 / OQ5 心跳 / OQ6 降级策略 / OQ7 固件更新 / OQ8 LED 语义 / OQ9 path_type 扩展 — 每条含 CC 推荐方案 + 阻塞 Phase 1 标注）
- **[Mac-主会话]** backlog 打 ✅ 1 条（D21）+ 打 ⏳ 2 条（S2/S3）；累计 ✅ 26 / ⏳ 14 / 🟰 1 / 剩 46

### 2026-04-20 深夜 v0.3.2 发布（本来要明天做，itsuki 决定今晚赶完）

- **[Mac-主会话]** **CHANGELOG [0.3.2] 段** — 完整列 Added 12 新建 / Changed 元规则 + 基建 / Fixed 14 条 ✅ + 推翻 4-19 两条架构 / Notes 不含代码 + 两会话并行 0 冲突 + 议题 E 遗留
- **[Mac-主会话]** **v0.3.2_AC叙事.md** — 按 v0.3.0 建立的 6 节模板 —— 核心 AC 价值：架构决策可推翻但要留痕 / 两会话并行的工程协调 / AI 协作成熟度 4 层认知（防粉饰 / 推翻 AI 推荐 / 拒绝 AI 倒戈 / 讨论=产出元规则）
- **[Mac-主会话]** `git tag -a v0.3.2` + push commits + tag 到 GitHub
- **[Mac-主会话]** backlog 相关条目 ✅ 实际都在此前 commit 里已经标完（A2/A4/A5/A6/A9/A11/A12/A13/L1/L6/T4/T6/T8/T10/T13/D26 全部 v0.3.2 区间完成）

### 2026-04-20 深夜再再后续（itsuki 三次"继续"→ 基建 6 条 + v0.4.0 输入 + memory 更新）

- **[Mac-主会话]** **T8 🟡 ✅** `create_local_dev_symlink.sh` 加注释 + 两层自检（Mac / VPS 场景区分）
- **[Mac-主会话]** **T10 🟡 ✅** `99_archive/2025-12_早期GPT对话/payload.json` PII 检查 —— 无敏感（2025-12 DMSD 设计 prompt）
- **[Mac-主会话]** **T13 🟢 ✅** `.claude/settings.local.json` check —— 仅 permissions 字段，未 tracked，.gitignore 已排除
- **[Mac-主会话]** **D26 🟢 ✅** `CLAUDE_CODE_记录指南.md §2` 第 1 条改："用 `date`" → "从 environment prompt 看 `currentDate`"
- **[Mac-主会话]** **L6 🟢 ✅** `CLAUDE_CODE_记录指南.md §12` raw 命名规则加判断决策树（日期版 vs 主题版如何选）
- **[Mac-主会话]** **T6 🟡 ✅** 新建 `LICENSE`（All Rights Reserved + AC 后 4 方向评估表）
- **[Mac-主会话]** **T9 🟡 🟰** 标注过期（VPS 已停用 DMSD，Mac ↔ VPS 协议无必要建）
- **[Mac-主会话]** **v0.4.0 输入就位** 新建 `00_admin/v0.4.0_S系列spec漏洞优先级分析.md` —— 20 条 S 分 MVP 必修(7) / Nice-to-have(8) / Defer(5) + 每条复杂度估算 + Week 1/2/3 节奏建议 + 总工作量约 15-20 小时
- **[Mac-主会话]** **memory 更新** 2 条过期（v0.2 rewrite 已完成 / .pages PDF 版本错误）+ Key Dates 加 4-20 两行

### 2026-04-20 深夜再后续（itsuki 二次"继续做"→ Tier 2/3 五条 + pre-0.1 tag）

- **[Mac-主会话]** **A4 🟡 ✅** —— README 已覆盖 AC 动机坦诚声明（Batch 1 阶段做的），本次只是 backlog 打 ✅
- **[Mac-主会话]** **A13 🟡 ✅** `00_admin/面试准备_索引.md` —— 6 大类 42+ 题目标签 + 素材指针 + 教授追问模板（回答正文留 iCloud `05_产出/`）
- **[Mac-主会话]** **A12 🟡 ✅** `00_admin/v0.3.0_AC叙事.md` —— CLAUDE.md "版本 bump 触发 AC 记录" 首次落地 + 未来 v 版本号叙事的模板
- **[Mac-主会话]** **L1 🟢 ✅ 超额** —— 打 10 个 pre-git annotated tag（v0.0.1 - v0.0.10）指向 initial commit `3baa168`，CHANGELOG 头部加更新段。`git tag | sort -V` 现看完整版本历史 10 + 3 = 13 个 tag
- **[Mac-主会话]** **T2 🔴 ⏳** `00_admin/T2_iOS归档_dryrun评估.md` —— dry-run 评估（不执行）：3 方案对比 + CC 推荐 A（git mv 归档 + 改名去括号 + 全英路径）+ 含完整执行命令。**关键发现**：T2 原描述 "xcuserdata 已在 repo" 诊断**过期**，实测 `git ls-files` 为 none（原 .gitignore 早就排除）。**等 itsuki 明确授权"做 T2 方案 A"后执行**
- **[Mac-主会话]** **raw log append** —— `raw/2026-04-20_v0.3.1发布执行.md` 末尾加 "~00:30 [执行补]" 段，记录本批 5 条 + L1 超额 + T2 诊断纠正

### 2026-04-20 深夜后续（v0.3.1 post-release patch + 代 commit 下午会话）

- **[Mac-主会话]** **raw log 落盘**：`05_logs/raw/2026-04-20_v0.3.1发布执行.md`（同日主题版，4 条 / 4 #AC候选）—— itsuki"漏洞都修好了吗"追问（#2+#4）/ Batch 1/2/3 权限三分类设计（#3+#4）/ v0.3.1 tag 判据（#3+#4）/ 多会话协调不揉 02_design（#3）
- **[Mac-主会话]** **A5 ✅** `05_logs/raw/README.md` —— 给教授读者的 raw/ 说明 + 命名规则 + "不从 raw 读项目" 指引 + "作品集在哪里" 清单
- **[Mac-主会话]** **A9 ✅** `05_logs/dev_log/2026-04-10_空白期反思_索引.md` —— 100 字内 in-repo 锚点指向 iCloud 原文，不泄露私密反思内容
- **[Mac-主会话]** **A6 ✅** `00_admin/AC_提交_checklist.md` —— 5/6/7/8/9/10 月每月 gate + 技术/AC 叙事双线详细 checklist + 滑动条件降级规则
- **[Mac-主会话]** **T4 ✅** `.gitignore` 18 → ~80 行（Python/Node/Android/IDE/日志/OS/SQLite/.claude 本地设置）
- **[Mac-主会话]** **代 commit 下午 [Mac-另一会话] 产出**（`f36d10b`，**v0.3.1-post** 不进 v0.3.1 tag）：02_design/flow_design.md (246 行) + hardware_design.md (260 行) + raw/2026-04-20.md (958 行，5 条 / 4 #AC候选) + TODO.md 新增 2 条（宿舍官网 + keystore 备份）。commit message 明确归属 + scope 分隔
- **[Mac-主会话]** **backlog 更新**：A5 / A6 / A9 / T4 打 ✅（Tier 3 AC 补强 + Tier 4 基建预备）

### 2026-04-20 深夜（Tier 1 Batch 2/3 — v0.3.1 发布就绪）

- **[Mac-主会话]** **Batch 2a**：`00_admin/progress_overview_draft_2026-04-20.md`（CC 起草完整新版，含 D7-D13 所有修订 + G2 决策整段替换原"分阶段策略" + 硬件采购段 + 5 次新转折索引 + 仓库结构地图修正）—— 等 itsuki 审完整体替换
- **[Mac-主会话]** **Batch 2b**：`00_admin/AC_志望動機_素材.md`（A2 占位框架 —— 8 个必答子问题 Q1-Q8 + 辅助素材清单 + 填写顺序 + 更新触发信号）**✅ 打 x**（占位符本身是目标）
- **[Mac-主会话]** **Batch 3 辅助**：`00_admin/Batch3_itsuki手笔素材指引.md`（§1 9 条 decision_log draft / §2 5 次 project_evolution 转折 draft / §3 Python Day 2 坦诚 draft / §4 PostgreSQL 选型 5 条理由 draft）—— 粘贴式使用，itsuki 30-45 分钟闭合 D1/D2/D3/D4/D7-D13
- **[Mac-主会话]** **backlog 更新**：A2 打 ✅ / D1-D4 + D7-D13 加 ⏳ 标注 draft 就绪 + 新增元条目 M2（版本管理指南 §5/§7/§12 需更新）
- **[Mac-主会话]** **CHANGELOG v0.3.1 条目**：Added（8 新文件）+ Changed（文档同步）+ Fixed（backlog 10 ✅ / 11 ⏳）+ Notes（无代码 / 未 push / raw/4-20 留 / v0.3.2 预期 scope）
- **[Mac-主会话]** **v0.3.1 tag 准备**：总计 v0.3.0 → v0.3.1 区间 8 个 commit（`1557cef` / `cc12ebc` / `ad31d7b` / `2a7751d` / `e39910c` / `7db04ea` + 即将的 Batch 2/3 commit）

### 2026-04-20 晚（Tier 1 Batch 1 — AC readiness 第一步）

- **[Mac-主会话]** **backlog Tier 1 Batch 1 完成**（4/4 产出）：
  - **A1 🔴** 新建根目录 `README.md`（103 行，commit `e39910c`）—— 结构：是什么 / 为什么做 / 做到哪了 / 目录导航 / 技术栈（反映 G2）/ AI 协作声明 / 升学目标
  - **A11 🔴** AI 协作坦诚声明内嵌 README（~200 字，独立章节）—— 选方案 A 不选独立文件（独立文件易被跳过），指向 CLAUDE.md + decision_log 4-15 + backlog
  - **A3 🔴** 新建 `00_admin/原创设计_语音播报防作弊.md`（135 行，commit `7db04ea`）—— 故事叙事风格，第一人称，按"起点观察（宿舍代刷）→ 四步推导 → 替代方案对比 → 设计本质 → 面试原话 → 证据链"结构
  - **D20 🟡** `CHANGELOG.md` 第 3 行加 `**最后更新**: 2026-04-20` 字段
- **[Mac-主会话]** **2 commit 落盘**（都过 pre-commit ✅，均未 push）：
  - `e39910c` docs(README): A1 + A11
  - `7db04ea` docs(v0.3.1-wip): A3 + D20 + backlog 4 ✅
- **[Mac-主会话]** **backlog 四条 ✅**：A1 / A3 / A11 / D20（格式与 M1 / D19 / D22 / D23 / D24 / D25 / L11 一致，保留原文 + ~~附注~~）
- **[Mac-另一会话（今日下午）]** **iPhone 路径 + 动态 NFC 贴纸定稿**（素材在 `05_logs/raw/2026-04-20.md`，**untracked / 未 commit**）：BTR + Universal Link + AASA（选项 A 正式域名）→ itsuki 发现 URL 复制漏洞（方案 A/B/C/D 选 B 彻底）→ 下单 ST25DV16K × 4（¥100 RMB）+ Qwiic 转杜邦线（nonce 10 秒刷新）→ 追问"为什么要树莓派"确认 thin client ≠ no client，拍板 Pi 4B 2GB × 4（¥1200 RMB）。**5 条 / 4 #AC候选**

### 2026-04-19 晚（点呼流程 + 卡生命周期 + 记录规则 + 项目审查 backlog）

- **[Mac-主会话]** **点呼流程重新拍板**：会话开场 itsuki "之前的决定全砍了，从 0 开始"；CC 连续跳步 3 次（默认双路径架构 / 没读 spec 推 C5 / 又跳硬件）每次被纠正；最终确立"先流程后硬件"方法论
- **[Mac-主会话]** **G2 决策** — 取消 Phase 1/Phase 2 分阶段上线；v1.0 一次全上（iOS + Android + 卡）；开发内部保留 M1→M5 里程碑
- **[Mac-主会话]** **NFC 卡完整生命周期定稿** — F1 修订（空白 NTAG215 + 学生自贴名字）/ App 内 tap 绑定 / 没手机学生管理员代录 / 丢卡不收钱 / 毕业清 UID 绑定保留账户 / 卡可回收复用
- **[Mac-主会话]** **App 账号规则定稿** — 姓名+生日+性别（不要学号）/ 一设备一账号 / 换机走管理员
- **[Mac-主会话]** **Android 路线拍板** — tap 贴纸（不走 HCE）+ APK 自建网站分发
- **[Mac-主会话]** **三路径 + 时间窗幂等规则定稿**
- **[Mac-主会话]** **记录指南 §3.4 新增** — 记录详细度要求（5 模块 / 篇幅指引表 / 失败模式清单）。触发点：itsuki 反馈"简略的 raw 等于没记录"
- **[Mac-主会话]** **`05_logs/raw/2026-04-19.md`** — 12 条碎片 / 11 条 #AC候选 / ~700 行（经 2 轮重写，按新 §3.4 标准展开）
- **[Mac-主会话]** **`00_admin/2026-04-19_项目审查_backlog.md` 落地** — 87 条漏洞清单（D30 + S20 + A13 + T13 + L11）+ Tier 0-4 版本路线图 v0.3.1 → v0.6.0（**本会话没动清理，Tier 0/1 归入 v0.3.1 下次会话**）
- **[Mac-主会话]** **memory 治理** — 新建 raw_log_depth feedback 后撤回（理由：not git-tracked / 不跨机器同步），规则 merge 进 `CLAUDE_CODE_记录指南.md §3.4`；顺手修 MEMORY.md 3 条过期（v1.0 iOS only → iOS+Android / v1.0 frozen → v0.1 frozen / VPS 不再推进 DMSD）
- **[Mac-主会话]** **文档同步机制 A+B+C 建立** — itsuki 从 spec 文件名 v0.1 vs 内容 v0.2 不同步（raw 20:45）发现根因"多源必然漂移"，拍板全做 A+B+C。**A 单源真值**：新建 `00_admin/文档同步点清单.md`（§1 版本号 / §2 目录结构 / §3 5 核心问题 / §4 分阶段 / §5 时间戳 / §6 Release Checklist / §7 Onboarding Checklist）。**B 会话结束前扫描**：CLAUDE.md 新增"文档一致性规则"节（单源真值表 + 声明性文件清单 + 会话结束前 CC 必做 3 项）。**C pre-commit hook**：`00_admin/hooks/pre-commit` + `install.sh` + `README.md`（首次 clone 后跑 install.sh 设 `core.hooksPath`；hook 拦截声明性文件里的硬编码版本号，支持 `<!-- VERSION_OK -->` 豁免）。配套改动：CLAUDE.md / WIP / TODO 去硬编码版本号 + 反映 G2 决策；backlog D22/D23/D25/L11 打 ✅ + 加元条目 M1；AC 素材记入 `raw/2026-04-19.md §21:30`

### 2026-04-17 晚（spec 修订 3-commit 全部完成）

- **[Mac-主会话]** **v0.3.0**（commit `2ef7ff7`，已 push + tag）— spec 主体 rewrite：§1 双路径并存 / §5.1 双路径信号流 / §11.3 改判时限矩阵 / §11.4 改判扣分联动 / 附录 C 4 台协调 / 附录 D 25 项收口清单。spec 681→958 行（+277）。收口附录 ✅ 13 项 / 🔄 10 项
- **[Mac-主会话]** **v0.2.0**（commit `48e9b38`，已 push + tag）— 字典三件套全改（base_status 重命名 / overlay 分两类 / +5 ENUM 枚举 / +6 FIELD 字段 / +5 ERROR_CODES）+ DEVICE_REGISTRY 新建 + 6 项 🟢 清理（删 .trash_* / 归档 Folder Structure / Overview.docx → 99_archive/ / .gitignore 删 3 条 / 99_archive/README.md / 目录架构.md 删除）+ CHANGELOG 细粒度重建（pre-0.1 追认 6 条 + 2-02 至今每节点一条）+ 元文档单源化（CLAUDE.md ↔ CLAUDE_CODE_记录指南.md，1563→1362 行）
- **[Mac-主会话]** **v0.1.1**（commit `8706fed`，已 push）— CHANGELOG revert v0.2.0→v0.1.1 + CLAUDE.md 措辞修正 + raw 18:00 dump + WIP 启动 spec 修订 3-commit 计划

### 2026-04-17 上午

- **[Mac-主会话]** 把 `RollCall_Spec_v0.1.pages` 数字化为 Markdown（`01_specs/rollcall/RollCall_Spec.md`），顺便反向审查 spec 漏洞 7+18=**25 项**（附录 A + B，5 项 🔴 为 Phase 1 阻塞项）
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
| `03_dev/student_ios/` | iOS 会话 |
| `03_dev/teacher_web/` | 老师端会话 |
| `01_specs/` | 一次只允许一个会话改(规格冻结区) |
| `00_admin/` | 主会话管理 |
| `05_logs/dev_log/` | 各会话写自己今天的,文件名不撞就好 |
| `05_logs/raw/` | 同上 |

---

## 📝 给新会话的上下文(关键信息)

新会话读完 `CLAUDE.md` 和本文件应该知道:

1. **当前版本**: 见 `CHANGELOG.md` 顶部 — 项目仍在规格和设计阶段，未开始写代码。CHANGELOG 已于 2026-04-17 晚重建为细粒度（pre-0.1 追认 + 2-02 至今每实质节点一条）
2. **上线姿态（4-19 G2 决策）**: 取消 Phase 1 / Phase 2 分阶段；v1.0 直接 iOS + Android + 卡 完整版一次上线。开发内部仍按 M1→M5 里程碑
3. **防作弊核心**: 语音播报（原创设计，详见 `05_logs/decision_log.md`）
4. **版本体系**: 0.x.x = 开发中，1.0.0 = 宿舍正式上线
5. **记录体系**: CC 侧见 `00_admin/CLAUDE_CODE_记录指南.md`；方法论总章（`AC入试记录指南_v3.md`）在 iCloud，CC 不读
6. **文件地图**: 见 `CLAUDE.md §目录结构`（单源真值，见 `00_admin/文档同步点清单.md §2`）
7. **文档一致性**: 声明性文件不写硬编码版本号，见 `CLAUDE.md §文档一致性规则` + `00_admin/文档同步点清单.md` + `00_admin/hooks/pre-commit`
8. **itsuki 的偏好**: 给选项用 A/B/C 不用甲乙丙；决策她拍板；不盲从 AI

---

## 🕘 更新日志(本文件自己的)

- 2026-04-13 17:30 — [Mac-主会话] 初次创建 WIP.md
- 2026-04-13 晚 — [Mac-主会话] 开放任务迁移到 `TODO.md`;WIP 聚焦多会话协调;更新当前焦点(NFC 硬件选型中)
- 2026-04-13 深夜 — [Mac-主会话] 补充今天的完成清单(commit 91a4294/d89b435/666faf8 + 2025-12 raw)
- 2026-04-15 晚 — [Mac-主会话] 刷新当前焦点(Phase 1+2 架构敲定,进入硬件收尾+spec 补完阶段);登记 4-15 完成清单;记入两项新项目债(点呼机 spec、Android Phase 2 方案)
- 2026-04-17 18:00 — [Mac-主会话] 启动 RollCall v0.1 spec 修订(3 commit 计划);版本号 v0.3.0 revert 到 v0.1.1 patch（命名整理而已，spec 内容未变）;新增"进行中任务 A"
- 2026-04-17 18:09 — [Mac-主会话] CHANGELOG 细粒度重建：pre-0.1 追认 6 条 2025-12 方案级迭代（HCE→tag→SDM/SUN→v2→v2.1→v2.1加固版，来源 itsuki 贴出的早期 ChatGPT log）+ 2-02 至今每个实质节点一条 patch，当前 = v0.3.0
- 2026-04-17 19:00 — [Mac-主会话] **会话结束**：v0.3.0 spec 主体 rewrite 完成（commit `2ef7ff7`） + v0.2.0/v0.3.0 双 tag 推上 GitHub；任务 A 全结，移到"最近完成"
- 2026-04-19 21:15 — [Mac-主会话] **会话结束**：G2 取消分阶段决策 + NFC 卡生命周期定稿 + Android tap 贴纸路线 + App 账号规则 + 三路径幂等 + 记录指南 §3.4 新增 + raw/2026-04-19.md（12 条 / 11 #AC 候选） + MEMORY.md 过期 3 条修正 + 项目审查 backlog（87 条）落地。**git 暂未 commit/push**（itsuki 有另一个 agent 在改文件，避让）。下次开会话先 commit 这批 + v0.3.1 Tier 1 文档同步开工
- 2026-04-19 22:00 — [Mac-主会话] **文档同步机制 A+B+C 建立**（本次会话）：itsuki 从"版本号漂移"症状识别系统性病根，选最彻底方案。新建 `00_admin/文档同步点清单.md` + `00_admin/hooks/pre-commit` + `install.sh` + `README.md`；CLAUDE.md 加"文档一致性规则"节 + 去硬编码版本号；WIP / TODO 去硬编码。backlog 打 x 4 条 + 加 M1。AC 记录追加 raw §21:30
- 2026-04-19 22:30 — [Mac-主会话] commit `1557cef` 锁定主体工作（11 文件 / +1750 / -66）；commit `cc12ebc` 加 CLAUDE.md §会话结束 第 6 步"git 要解释"前提规则（CC 当时理解错方向，以为是讲 git 工具）
- 2026-04-19 22:45 — [Mac-主会话] itsuki 指出 `cc12ebc` 规则方向错了（应是讲 commit **内容**，不是讲 git **工具**）→ commit `ad31d7b` 纠正 CLAUDE.md，加 ❌/✅ 例子对比 + 逃生条款（itsuki 主动问才讲工具）
- 2026-04-19 22:50 — [Mac-主会话] **会话正式结束**：3 个 commit 都在本地（`1557cef` / `cc12ebc` / `ad31d7b`），**未 push**；pre-commit hook 三次都自动跑 ✅；下次会话先做 v0.3.1 Tier 1 剩余项（根目录 README / project_evolution 补 4-15/4-17/4-19 / decision_log 4-17/4-19 手写 / progress_overview 章节级更新 / 志望動機 #5 占位 / 原创设计 showcase / AI 协作声明）
- 2026-04-20 晚 — [Mac-主会话] **Tier 1 Batch 1 完成**：backlog 4 项 ✅（A1 / A3 / A11 / D20）；2 commit 落盘（`e39910c` README+A11 / `7db04ea` 原创设计 showcase + CHANGELOG 时间戳 + backlog ✅），都过 pre-commit ✅，均**未 push**。**未触碰** `05_logs/raw/2026-04-20.md`（下午另一会话的 AC 素材，留 itsuki 或下次会话处理）
- 2026-04-20 深夜 — [Mac-主会话] **Tier 1 Batch 2/3 完成 + v0.3.1 tag 发布**：itsuki 指令"修啊，别忘了迭代版本"后一次性推进；新建 3 文件（progress_overview draft / AC_志望動機占位 / Batch3 素材指引） + backlog 12 处更新（A2 ✅ / D1-D4 + D7-D13 加 ⏳ / M2 新增） + CHANGELOG v0.3.1 条目。**v0.3.1 tag 已打**（`fb330c2`，暂未 push）
- 2026-04-20 深夜后续 — [Mac-主会话] itsuki "没做完的接着做 + 记得写 log" → 本会话 raw 落盘（4 条 #AC候选） + A5/A6/A9/T4 ✅ 四条 patch（`raw/README.md` / `AC_提交_checklist.md` / 空白期反思锚点 / `.gitignore` 大扩充） + 代 commit 下午会话产出 `f36d10b`（v0.3.1-post，02_design + raw/4-20 + TODO 新增）+ backlog 累计 ✅ 15 / ⏳ 11 / 剩余 61
- 2026-04-20 深夜再后续 — [Mac-主会话] itsuki "继续做" → A4/A12/A13/L1/T2 五条（L1 超额：10 个 pre-0.1 annotated tag 指向 initial commit；T2 dry-run 评估不执行）+ `面试准备_索引.md` / `v0.3.0_AC叙事.md` / `T2_iOS归档_dryrun评估.md` 新建 + CHANGELOG 头部 pre-0.1 tag 说明 + raw log append ~00:30 执行补段 + backlog 累计 ✅ 19 / ⏳ 12 / 剩余 57
- 2026-04-20 深夜再再后续 — [Mac-主会话] itsuki "继续" → T6/T8/T10/T13/D26/L6 ✅ 6 条 + T9 🟰 标过期 + `LICENSE` 建立 + `create_local_dev_symlink.sh` 自检 + `CLAUDE_CODE_记录指南.md` §2 §12 改 + 新建 `v0.4.0_S系列spec漏洞优先级分析.md`（v0.4.0 minor 开工 input，20 条 S 分 MVP/Nice/Defer + Week 1-3 节奏）+ memory 更新（2 条过期纠正 + Key Dates 加 4-20 两行）+ raw append ~01:00 段 + backlog 累计 ✅ 25 / ⏳ 12 / 🟰 1 / 剩余 49
- 2026-04-20 深夜 v0.3.2 发布 — [Mac-主会话] itsuki 从"明天做"改为"今晚做完"→ 4 步：CHANGELOG [0.3.2] 完整段 + 新建 `v0.3.2_AC叙事.md`（6 节模板，核心 AC 是 AI 协作成熟度 4 层 / 架构决策可推翻但要留痕 / 两会话并行协调）+ `git tag v0.3.2` + push。今日总战绩：13+ commit + 1 release tag (v0.3.2) + 10 pre-0.1 tag 追认 + backlog 25 ✅。正式结束 4-20 会话
- 2026-04-21 — [Mac-主会话] **v0.4.0 开工启动日（不打 tag）**：D21 ✅（CHANGELOG HH:MM）+ S2/S3 字段 draft ⏳（card_uid / student_status 完整定义 + 配套生命周期字段 + 业务决策点）+ Device_Contract 骨架 draft（9 节 + OQ1-9 清单）+ backlog 累计 ✅ 26 / ⏳ 14 / 剩 46。等 itsuki 审 draft + 拍板 OQ → 合并进字典 + spec → 继续修 S1/S4/S7/S10 → 打 v0.4.0 tag
- 2026-04-21 晚 — [Code-Agent] **Demo 4-28 代码实现会话 onboard**：读完 `for_code_agent.md` briefing + 剩余 8 档 + backend 全 6 源码；盘点 Tier 1 真实技术缺口 6 处（`Checkin.status` / `/api/roll-call/live` 聚合 / 改判 / 健康 / 请假 / discipline_config + 搜索聚合）；建 `99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/questions_for_requirements.md` 首批 5 阻塞问题（Q1 缺席记录产生时机 / Q2 Checkin.status + 迟到窗口阈值 / Q3 iOS 切学生方案 / Q4 Web UI 中文 vs 日语 / Q5 seed 扩到 30 人 + 造扣分历史）+ 3 非阻塞建议（N1 红十字改 🏥 / N2 IP 配置策略 / N3 WS 先上 fallback 后备）；WIP §进行中 加本会话段登记文件认领边界。**今晚不写代码**（等 Q 回复 + 硬件 4-22 到），D2（4-22）上午按答复启动 schema + seed + 6 API 缺口补全
- 2026-04-22 下午 — [Code-Agent] **Web Round 3 产出导入 + 解包 + 修正**：Claude Design Round 3 成品 `Tomoshibi_Prototype_v3__Standalone_.html` 9.4 MB 导入 → Python 解包 manifest 146 资源到 `round3/src/`（12 组件 + 3 vendor + 130 字体 人类可读）+ itsuki 走查 4 项 UI 调整（詳細列宽 / リュウ迁 M101 / 扣分线 / 搜索 normalize）+ 2 次白屏 debug（file:// CORS / 数组越界 `i % len`）+ 日语 native 文案审查（约 12 处中文残留修正 名単→リスト / 晚→晩 等）+ `build_single_file.py` 脚本化 32 MB U 盘版。等 itsuki 视觉 QA
- 2026-04-22 晚 — [Mac-demo-sprint] **iOS 前端设计 Round 1 Prompt 落盘**：推翻 4-21 [Code-Agent] 的 4-tab iOS 方案（归档）→ 3 按钮 nav + Home omnibus + 中央点呼 sheet（iOS 26 Liquid Glass）+ 注册 flow 4-step + 锁定升级 5 阶段 + 00 号 seed demo 魔法 + 长按 breadcrumb；Q1-8 + N1-20 全答；落盘 4 档件（IOS_DESIGN_LOG 15 KB / DESIGN_BRIEF 10 KB / **Round1_Prompt.md 38 KB / 878 行 / 73 画面 Phase A+B 一次出** / README）+ 4 参考图（logo / 手绘 nav / SUNTORY 扫 sheet ×2）；CLAUDE.md §账号规则 patch v3（推翻 4-20 议题 C 面签 → 即激活）；raw log `2026-04-22_iOS前端设计_Round1.md`（6 条 / 2 #AC候选🌟）。**等 itsuki audit Prompt → 送 Claude Design 新 project → Phase A → Phase B**

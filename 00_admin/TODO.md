# DMSD 待办清单

> **这个文件是给 itsuki 看的**,用来跟踪所有该做但还没做的事。
>
> - 和 `WIP.md` 的区别: WIP 是给 Claude 看的"当下在做什么 + 多会话协调",TODO 是给 itsuki 看的"还没做的所有事"
> - 和 `progress_overview.md` 的区别: progress_overview 是稳定的章节目录,TODO 是可以频繁增删的任务池
> - 完成的任务: 在 checkbox 前打 x,隔段时间(每周或每月)批量移到"已完成归档"

**最后更新**: 2026-05-04（加 §📋 旧 backlog + 全文件审查 未结余项整合）
**当前版本**: 见 `CHANGELOG.md` 顶部 · 单源真值，见 `00_admin/文档同步点清单.md`

> **2026-04-17 归档说明**：`executable_dev_checklist.md` 已归档到 `99_archive/2026-04-12_executable_dev_checklist.md`（内容已过期，功能被本 TODO.md 吸收）。

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

## 🎯 2026-04-28 管理员 Demo 冲刺（最高优先级）

**Deadline**: 2026-04-28（7 天）
**权威源**: `99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/`（整个文件夹）
**总纲**: [`99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/sprint.md`](./demo_4-28/sprint.md)

本 TODO 不展开 demo 细节，避免和 sprint plan 重复。demo 相关的所有任务看 sprint.md §3 时间表。

**itsuki 侧 D1 剩余**：
- [ ] Amazon 日本下单 Pi 3A+ + 配件（明天 4-22 到）
- [ ] 淘宝下单 ST25DV16K（供货延迟也要买，v1.0 用）
- [ ] 看 `demo_4-28/scope_tier.md §5` 补 Tier 漏项（如需）
- [ ] 看 `demo_4-28/demo_script.md` 确认台词风格
- [ ] 给代码 agent 分配任务（前端 / 后端 / iOS / Pi 4 个模块）

**demo 后（4-29+）**：
- [ ] 管理员反馈整理到 `05_logs/raw/2026-04-28.md`
- [ ] 根据反馈决定：推进 v1.0（纳入 v0.5.0 路线）/ 推翻重做 / 局部调整

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

- [ ] **CLAUDE.md 4-step vs IOS_DESIGN_LOG 5-step 矛盾(同时存在)**
  - 现状:CLAUDE.md 之前写"App 内 4-step 注册流程",IOS_DESIGN_LOG.md §3.9.2 升级到"新 5 step"加学年/組/番号 step
  - 当前已规避:CLAUDE.md 改成"多步注册"避免硬编码,但**真值未确认**
  - 待 itsuki 确认:当前是 4-step 还是 5-step?哪个权威?
  - 选项 a:确认 5-step 是真值,CLAUDE.md 改回"5-step"具体描述,IOS_DESIGN_LOG 是权威
  - 选项 b:确认 4-step 是真值,IOS_DESIGN_LOG §3.9.2 是过期描述要回滚

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
- [ ] **iOS 3 个空壳 view 决定命运**：`Schedule` / `StayList` / `BusList`（5-01 审查推荐都删，已并入 Home / Apply / Community Bus card）
- [ ] **`00_admin/AC_志望動機_素材.md` Q1-Q8 itsuki 自己起草**（185 行框架 17 个小节占位 / 内容待填 — AC 5 核心问题 #5 志望動機，repo 内最大空白）

### B. CC 可独立做（每条 < 30 分钟，下次开会话「做 B 类」即可）

- [ ] 改名 `03_dev/student_ios/DESIGN_BRIEF.md` → `_archived_DESIGN_BRIEF_Round1_context.md`（IOS_DESIGN_LOG 已全覆盖）
- [ ] 改名 `03_dev/student_ios/demo/Round2_Prompt_C3.md` → `_archived_Round2_Prompt_draft.md`（C3 已 resolve）
- [ ] 删 `99_archive/2026-04-15_old_demo/.DS_Store`（误进 git）
- [ ] 删 3 个已过期的 admin 文件：
  - `00_admin/v0.4.0_S系列spec漏洞优先级分析.md`（已被「漏洞_剩余清单」吸收）
  - `00_admin/T2_iOS归档_dryrun评估.md`（已执行）
  - `00_admin/跨会话_ios_共享决策.md`（iOS 工程已独立 repo）
- [ ] backend `03_dev/backend/v1/app/models.py` 13 张表 docstring 各标 P0 / P1 / P2
- [ ] 更新 `00_admin/文件结构指南.md`（补 v0.6.0 / v0.7.0 / v0.8.0 AC 叙事文件 + 新 raw 日志）
- [ ] 更新 `99_archive/README.md` 时间戳 + 鬼影文件解决说明
- [ ] **S18（低价值）**：`DEVICE_REGISTRY §6` 候选位置 `dorm-A-01 / dorm-B-01` 跟 `path_type` A/B 撞字 — 改成 `dorm-1-01 / dorm-2-01`。真部署 4 台时顺手做也行
- [ ] **后端补漏**：`routers/applications.py` 加 `POST /{id}/approvals`（役职审批 #10-#13）+ `DELETE /{id}`（D3 撤回）+ `services/email.py` 补 retry 3 次循环

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
- ✅ teacher_web v1 真改造已启动 — 5-01 时是 demo 100% MD5 镜像，5-02 起 TS+Vite+Zustand 已落地
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

### 硬件架构层

- [ ] **点呼机"大脑"选型**: Raspberry Pi(A) vs ESP32(B)
  - A: Python 能复用,上线快,单台 ¥13,500,AC 入試展示"动手能力"
  - B: C/C++,更便宜(¥3,000-4,000),AC 入試展示"真·嵌入式工程",但要多学一门语言
  - 当前状态: **4-15 已确认方向 A(Raspberry Pi)**,仅型号待定
  - 阻塞: 等宿舍网络情况确认

- [ ] **Pi 具体型号**:Zero 2 W(¥100,GPIO 要焊) vs 4B 2GB(¥300,易用)
  - 阻塞:宿舍网络情况

- [ ] **PN532 NFC 读头接口**:GPIO 接法 vs USB 接法(和 Pi 型号绑)

- [ ] **LED 灯方案**:单灯(红/绿切换)vs 双灯(红+绿)vs RGB,接 GPIO 还是 HAT
  - 屏幕暂不做,留 v1.0 正式版后考虑

- [ ] **扬声器方案**:USB 小喇叭 / 3.5mm 接口 / HAT

- [ ] **电源与贴墙方式**:USB 电源 + 墙插;双面胶/螺丝/支架

- [ ] **点呼机部署数量**:**4 台**(已定),但位置和通道分配待确认

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

- [ ] **v1.0 产品化前：清理 Tomoshibi iOS / Web 的 demo-only 代码**（2026-04-24 itsuki 提出）
  - 背景：4-28 演示用的 iOS + Web 两个前端，itsuki 决定演示通过后直接拿去产品化（不重写）
  - 但为了演示方便加了 **客户端自造状态** 的 demo 捷径，正式上线前必须删干净，否则变成安全漏洞（学生能自己伪造点呼状态）
  - 已知清单：
    - iOS：`Features/Home/HomeStubs.swift` 点数卡 `LongPressGesture` → `app.cycleDemoRollState()`
    - iOS：`Foundation/AppState/AppStore.swift` 的 `cycleDemoRollState()` + `tickCountdown()` + `simulateCheckin()` 前端自走倒计时逻辑
    - iOS：SEED.user 硬编码 リュウ イヒ / 060218 / 男寮 M101 / 4.5 点 → 生产版走登录拉后端
    - iOS：AppStore.changeLog 里的 "高2→高3" seed
    - iOS：各种 `"Demo · ..."` 前缀的 toast 文案
    - Web（teacher_web/round3）：同类 demo seed / mock state（需 grep 清单）
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

- [ ] 🔴 **项目文件总览升级为"项目唯一入口" + 文件联动 3 层架构**（2026-05-04 itsuki 拍板，CC 之前判断错被 itsuki 纠正）
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

- [ ] **.pages 文件转 Markdown**(4 个文件)
  - `01_specs/API_Contract_v0.1.pages`
  - `01_specs/IA_UI_v0.1.pages`
  - `01_specs/Overview_of_Features_v0.1.pages`
  - `01_specs/rollcall/*.pages`

- [ ] **清理 `01_specs/临时PDF/` 下的"のコピー"副本**(5 个文件)
  - git status 里一直挂着

- [ ] **归档早期 iOS throwaway 代码**
  - 从 `03_dev/Student/` → `99_archive/`

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

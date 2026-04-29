# Tomoshibi 系统功能设计 — 共用真值

> **系统对外名**: **Tomoshibi**(灯火);DMSD 是项目/仓库代号。
> **本文作用**: **iOS App + 老师 Web + 后端 API 共用功能矩阵的唯一真值**。任何功能改动 → 先更新本文 → 再改实装。
> **上游参考**:
> - `01_specs/rollcall/RollCall_Spec.md`(点呼业务规则 + §4 时刻表 + §5.4-5.6 流程)
> - `02_design/hardware_design.md`(硬件)
> - `02_design/flow_design.md`(流程)
> **下游 LOG**:
> - `03_dev/student_ios/IOS_DESIGN_LOG.md`(iOS 専属)
> - `03_dev/teacher_web/WEB_DESIGN_LOG.md`(Web 専属)
> **最后更新**: 2026-04-29 晚(大重写 — 以老师 4-29 LINE 38 条要件 + Q1-Q12 答案 + R1-R4 硬约束 + itsuki 4 条砍/留 为锚)

---

## 0. 文档状态 + 重写背景

### 重写背景(2026-04-29)

4-28 demo 通过老师认可后,4-29 老师通过 LINE 发来完整需求清单 — **38 条产品要件 + 1 条订正**(通知改邮件)。同日 itsuki 自己拍板 **4 条砍/留**(社区类砍、音乐留)+ 回答了 **Q1-Q12** 12 个开放问题。

之前版本(2026-04-23 首版)的内容是 demo sprint 期间自己拍脑袋的设计 — 没对齐老师真实需求。本次重写以**老师 38 条 + Q 答案 + R1-R4 + 4 砍/留**为锚。

### 章节状态

| 章节 | 状态 | 来源 |
|---|---|---|
| §1 用途 + 同步规则 | 保留 | 2026-04-23 |
| §2 必读硬约束 R1-R4 | ⭐ 新增 | 2026-04-29 老师 LINE |
| §3 5 角色体系 + 设备分布 | ⭐ 大扩充 | 老师 LINE + Q1 + Q4 + Q5 + Q6 |
| §4 学号体系 | 保留 | 2026-04-23 |
| §5 房间号管理 | 保留 | 2026-04-23 |
| §6 学生改动履历 | 保留 | 2026-04-23 |
| §7 功能矩阵 | ⭐ 大重写 | 14 子节,覆盖老师 38 条 |
| §8 数据模型 | 部分扩充 | 新增出寮届 / 学習 / 行事 / 巴士 / 食堂 等表(部分待完整) |
| §9 待拍板事项 | 更新 | 加进尚未答复的 Q |
| §10 改订历史 | 加 4-29 改动 |
| **APPENDIX A** | ⭐ 新增 | 老师 LINE 原文(保留作 evidence) |

---

## 1. 用途 + 同步规则

### 1.1 为什么有这份文档

**问题**: iOS App / 老师 Web / 后端 API 是别 repo + 别会话实装的。
- iOS 在 `~/dev/TomoshibiiOSApp/`(独立 repo `otogi2025/Tomoshibi-iOS`,cloud agent 并走)
- Web 在 `~/dev/DMSD/03_dev/teacher_web/{demo,v1}/`(2026-04-29 demo/v1 分离后)
- 后端在 `~/dev/DMSD/03_dev/backend/{demo,v1}/`(同上)

→ **共用功能**(账号 / 申请 / 通知 / 出寮届 / 学習 / 点呼 等)在一边改了,另一边没跟上 → 必然漂移。

**解决**: 本文 = 全实装层都参照的 **single source of truth**。改功能时先改这里 → 再到各实装的 LOG 转记。

### 1.2 跨会话同步规则(CC + cloud agent 必读)

| 改动种类 | 必须动作 |
|---|---|
| 改了 iOS 功能 / 设计判断 | (1) 在 `IOS_DESIGN_LOG.md` 时间线记录 (2) **更新本文 §7 矩阵对应行** (3) 必要时跑 `bin/sync-ios-refs.sh` 同步到 Tomoshibi-iOS |
| 改了 Web 功能 / 设计判断 | (1) 在 `WEB_DESIGN_LOG.md` 时间线记录 (2) **更新本文 §7 矩阵对应行** |
| 在 Swift 代码改了功能行为 | (1) 在 `Tomoshibi-iOS/STATUS.md` 记录 (2) **通知 itsuki → 触发本文 + IOS_DESIGN_LOG 反向同步** |
| 加了 / 改了后端 API | (1) **更新本文 §7 矩阵 API 列** (2) 更新 `03_dev/backend/v1/` 内的 README / OpenAPI 草案 |
| 提了新功能(未实装) | 在本文 §7 加一行标"⏳ 提案中"→ 等 itsuki 拍板 |

### 1.3 sync-ios-refs.sh 的作用

DMSD 是 source of truth。Tomoshibi-iOS 的 `refs/` 是复制品(cloud agent 拿不到 DMSD repo,必须物理复制)。

DMSD 内 `bin/sync-ios-refs.sh` 一条命令就把:
- `02_design/system_features.md` → `Tomoshibi-iOS/refs/`
- `03_dev/student_ios/IOS_DESIGN_LOG.md` → 同上
- `03_dev/student_ios/demo/Tomoshibi_iOS_PhaseB_v2.html` → 同上(2026-04-29 路径变更:`designs/` → `demo/`)
- `03_dev/student_ios/demo/phaseB_src/` → 同上

复制完之后 itsuki 自己在 Tomoshibi-iOS 那边 `git status` 确认 → 手动 commit / push(不自动 push,安全考虑)。

---

## 2. ⚠️ 必读硬约束 R1-R4(2026-04-29 老师 LINE 拍板)

设计任何功能时**必须**满足以下 4 条硬约束。违反就推翻设计。

### R1 — 通知 = 邮件固定(push 不可)

**老师订正原文**:「現在メールで行っています。提出したことが『残る』からです。... もしこれをプッシュ通知にすると、通知を消して忘れ去られる可能性が高い」(意思: 现在用邮件,因为提交"留得下"。push 通知一消就忘)

- 役职审批通知(出寮届承认请求 / 学生提交事件 / 改动通知)= **邮件**
- 学生侧通知不限制(push / in-app 都可)
- **设计影响**: 后端必须接 SMTP / SendGrid 之类邮件服务,不能只靠 push 服务(FCM/APNs)

### R2 — 老龄寮監 UX = 一本道

**老师原文**:「上記は高齢の寮監が使用するため、使用法を極力単純化する必要あり」(意思: 给老龄寮監用,使用方法要极力简化,**不能有条件分歧**;任何情况都"按这个 → 然后按这里",步骤固定)

- 寮監使用的功能(点呼 / 学习出席 / iPad 操作)**不能有"如果 X 则 Y / 否则 Z"的多分支**
- **设计影响**: 寮監 UI 不要 dialog 选项 / 不要分支 flow,直线流程到底

### R3 — 教师每人单独账号密码

**itsuki 补足 + Q4 答**:每个人一个单独的账号,换人之前号主自己点退出登录,然后新的人点登陆,输入账号密码后进入管理页面。

- 不是"职位账号共享"
- 寮監 iPad 共用,但**每个寮監一个账号**(Q5: iPad 共用,换班时间不固定,老师自己退出登录就行)
- 教师密码重置 = 交给宿舍负责跟进项目的老师(Q10)
- **设计影响**: account 表必须支持教师角色 + 单独凭据;teacher_id 关联到 role 而不是 station

### R4 — 1·2 寮 vs 4 寮 分别表示

**老师原文**:「1,2 寮と 4 寮を分ける(別表示)」

**Q1 答**: 1·2 寮 = 男生寮(2 寮虽独立但点呼跟 1 寮一起),4 寮 = 女生寮,点呼独立。

- 寮单位 = 物理实体 + 性别隔离
- 1·2 寮(男)/ 4 寮(女)= 各自独立 session 跑点呼
- 出寮者一覧、roster、统计都按"1·2 寮 vs 4 寮"分开
- **设计影响**: dorm 字段不只是 `male/female`,要 `dorm_unit ∈ {1, 2, 4}` + `gender` 一致性约束

---

## 3. 5 角色体系 + 设备分布(2026-04-29 老师 LINE 拍板)

### 3.1 5 角色(老师定义)

| 角色 | 平台标记 | 平台 | 谁 |
|---|---|---|---|
| **学生** | 〇 | iOS / Android App | 全寮生 |
| **役职**(寮務部長 / 寮務課長 / 国際交流部長 / 国際交流課長)| 〇 | iOS / Web 兼用 | 这 4 个职位的老师 |
| **寮監・学習担当** | ★ | **iPad(寮管室 + 食堂)**专用 | 寮監(高龄、轮番)+ 学習担当 |
| **寮監事務室** | ● | **事務室 PC** 专用 | 寮監(出寮者一覧确认用)|
| **寮務部教师** | 〇 | iOS / Web 兼用 | 寮務部所属的教师 |

**平台标记的意思**(老师用法):
- **〇** = 任何地方都能输入处理最理想,多平台
- **★** = 寮 iPad 专用
- **●** = 事務室 PC 专用(独自 UI / Excel / Spreadsheet 都行)

### 3.2 设备分布(Q6 答)

| 场所 | 设备 | 用途 |
|---|---|---|
| **職員室** | 各教师 PC | 国際交流部長等教师个人账号、〇 功能 |
| **事務室** | PC | 寮監出寮者一覧确认(● 功能)|
| **寮管室** | iPad | 寮監点呼操作 + 学习出席(★ 功能)|
| **食堂** | iPad | 食事数 Excel 导出确认 |

### 3.3 寮单位(R4 + Q1 答)

| 寮 | 性别 | 点呼 |
|---|---|---|
| **1 寮** | 男 | 1+2 寮合同 session(物理隔离但点呼合并)|
| **2 寮** | 男 | 跟 1 寮合同 |
| **3 寮** | — | (不存在 / 已废止)|
| **4 寮** | 女 | 独立 session |

**设计上的意思**:
- 点呼 = 2 个 session 同时跑(1+2 寮男 / 4 寮女)
- 出寮者一覧 = 按男女分开显示(R4)
- roster 的 `dorm_unit` 字段是 `1` / `2` / `4` 3 值(跟 gender 矛盾要校验)

### 3.4 账号运用规则(Q4 + Q5 + Q11 答)

- **役职・寮監・寮務部教师**: 每人单独账号密码(R3)
- **iPad 共用**: 寮管室 + 食堂 iPad 是物理 1 台,寮監登录 → 操作 → 退出 → 下一个人登录
- **留学生 flag**: App 注册时学生自己选"是 / 不是"(Q11)→ 数据来源 = 自己申报,不是学校官方名单
- **教师密码重置**: 学生 → 找宿管 → 宿管在 Web 后台手动重置 / 教师 → 找跟进项目的负责老师(Q10)

---

## 4. 学号体系(6 桁 学年×組×番号)

### 4.1 编码规则

```
060218
├── 06 = 学年(2 桁,6 年制中高一贯对应)
├── 02 = 组  (2 桁,A=01 / B=02 — 当校只到 B 组,C 以后没有)
└── 18 = 番号(2 桁,班里通号,1〜99)
```

**学年映射**(当校 = 中高一贯 6 年制):

| 学年 | 编码 |
|---|---|
| 中 1 | 01 |
| 中 2 | 02 |
| 中 3 | 03 |
| 高 1 | 04 |
| 高 2 | 05 |
| 高 3 | 06 |

### 4.2 生命周期

- **新入生注册时**: App 内输入"学年 / 组 / 番号"→ 系统**计算**出 6 桁学号(不是"分配",是 deterministic 计算)
- **进级时(每年 4 月)**: 学号变(例: 050218 → 060218)→ **学生本人在 App 内更新** → **老师 Web 改动履历自动记录**
- **转校生(年度途中编入)**: 班里末番 + 1,学生本人手输入
- **毕业生**: 学号在历史上保留(后端 PK 不变,见 §8)

### 4.3 demo seed 的 00 → 060218

リュウ イヒ(itsuki 自己)的 demo seed: 番号 `00` → 学号 `060218`(高 3 / B 组 / 18 番)。房间 M101(保持)。

---

## 5. 房间号管理

### 5.1 注册时(v1.0)

- 学生 iOS App 注册步骤里加"房间号"(手输入,格式例 `M101` / `W203`)
- 老师 Web 学生账号管理页能看到房间号
- **没校验**(demo 阶段)→ v1.1 加"老师侧 ROSTER 对照 + 重复房间警告"

### 5.2 一括分配工具(v1.1 未来功能 ⏳)

- 房间是**1 年 1 度大调整**
- 老师 Web "房间号一括分配"页(drag & drop UI)
- 学生 App: 一括分配应用后是 read-only / 应用前可编辑
- 改动履历:「老师把你的房间从 M101 改到 M205(2026-04-25 09:30)」记到学生 + 老师两边的履历里

---

## 6. 学生改动履历(审计日志)

学生在 App 内做的信息变更全部从老师 Web 可阅览。

**对象字段**: 学号构成 / 房间号 / 邮箱 / 电话 / 姓名(要老师承认 ⏳)/ 密码(只记"变更事件",不记哈希)/ 头像

**履历 entry 形式**:

```json
{
  "timestamp": "2026-04-23T21:30:00+09:00",
  "actor": "self",
  "actor_name": "リュウ イヒ",
  "field": "grade_code",
  "old_value": "05",
  "new_value": "06",
  "context": "进级更新"
}
```

**通知**:
- 老师编辑 → 给学生 push 通知
- 学生编辑 → 不通知老师(履历里查就行)。例外: 学号变更要给老师**邮件**通知(R1,误输入检测用)

---

## 7. 功能矩阵(以老师 38 条 + Q 答案 + 4 砍/留 为锚 重写)

凡例:
- ✅ = 已实装 / 〇 = 设计确定待实装 / ⏳ = 设计中 / 🔴 = 未着手 / — = 不适用
- (D) = Demo(4-28)对象 / (V1) = v1.0 上线对象 / (V1.1+) = 未来扩展
- **角色标记**: 〇 = 多平台 / ★ = iPad 专用 / ● = 事務室 PC 专用

### 7.1 账号

| 功能 | 学生 iOS | 老师 Web | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|---|
| 学生注册(4 step + 学号 + 房间号 + 留学生 flag)| 〇 | — | `POST /accounts` ⏳ | 学生 | (V1) |
| 学生登录(学号 + 密码)| ✅ Auth Stub | ✅ login.jsx | `POST /sessions` ⏳ | 学生 | (D) |
| 教师登录(教师 ID + 密码,各 1 名独立 R3)| — | ⏳ teacher login | `POST /sessions/teacher` ⏳ | 全教师 | (V1) |
| 密码重置(自助没有,宿管 Web 操作)| 〇 注册画面文案 | ✅ accounts.jsx | `POST /accounts/:id/password-reset` ⏳ | 寮務 | (D) |
| 教师密码重置(项目负责老师经手)Q10 | — | ⏳ admin page | ⏳ | 项目负责 | (V1) |
| 解锁 | — | ✅ accounts.jsx | `POST /accounts/:id/unlock` ⏳ | 寮務 | (D) |
| 学号构成编辑(学年/组/番号)| 〇 マイページ | ✅ 阅览 + 履历 | `PATCH /accounts/:id` ⏳ | 学生 + 寮務 | (V1) |
| 房间号 学生编辑 | 〇 マイページ | ✅ 阅览 + 履历 | `PATCH /accounts/:id` ⏳ | 学生 | (V1) |
| 房间号 一括分配(老师侧)| 自动同步 | ⏳ V1.1 | `POST /room-assignments/batch` ⏳ V1.1 | 寮務 | (V1.1+) |
| 留学生 flag(自己申报)Q11 | 〇 注册时 select | ✅ 阅览 + 履历 | 包含在 `POST /accounts` 里 | 学生 | (V1) |
| 账号改动履历 显示 | 〇 マイページ「変更履歴」| ✅ アクティビティ tab | `GET /accounts/:id/activity` ⏳ | 学生 + 寮務 | (D) |

### 7.2 出寮届(帰省 / 外泊 / 帰国) — 老师 38 条 #1-#13

> **设计原则**:
> - 学生**只能提交自己的届**,不能代填(#1)
> - 出寮日 = 明天起(不能选今天)(#3)
> - 不需要的字段不显示(动态非表示)(#4)
> - 提交后 → 显示承认状态(#5)
> - 通知 = **邮件**(R1)

#### 7.2.1 字段(3 种,逐层累积)

| 种类 | 字段 |
|---|---|
| **帰省** | 出寮日 / 帰省方法 / 出寮时刻 / 帰寮日 / 帰寮方法 / 帰寮时刻 |
| **外泊** | 帰省字段 + 外泊地点(可多个)+ 食事不要期间(from/to 明确 #38)|
| **帰国** | 外泊字段 + 出发机场 / 飞机出发时刻 / 到达机场 / 飞机到达时刻 |

#### 7.2.2 承认流程(#5 + R1 邮件)

| 种类 | 承认者 |
|---|---|
| **帰省** | 寮務部長 + 寮務課長 |
| **外泊** | 寮務部長 + 寮務課長 +(留学生时)国際交流部長 + 国際交流課長 |
| **帰国** | 同外泊 |

→ 提交时给上述役职发**邮件**(R1,push 不可)。
→ 提交者在 App 里能看到**承认 / 不承认 / 待审**状态。

#### 7.2.3 功能矩阵

| 功能 | 学生 iOS | 老师 Web | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|---|
| 出寮届 提交(3 种)#1-#5 | 〇 ApplyForm | — | `POST /apply/outstay` ⏳ | 学生 | (D) |
| 不能代别人提交 #1 | 〇 提交时 user 校验 | — | 后端再校验必须 | 学生 | (V1) |
| 动态非表示(不需要字段不显示)#4 | 〇 ApplyForm conditional | — | — | 学生 | (D) |
| 出寮日 = 明天起 #3 | 〇 DatePicker disable today | ✅ 同样(教师当天录入用 例外)| 后端校验 ⏳ | 学生 + 教师 | (D) |
| 承认状态显示 #5 | 〇 マイページ | ✅ 一覧 | `GET /apply/:id` ⏳ | 学生 | (D) |
| 给役职发**邮件**通知 #6 / R1 | — | — | `POST /notifications/email` ⏳ | 系统 | (V1) |
| 役职 承认 / 不承认 #10 | 〇 通知接收 | ✅ ApprovalPage | `PATCH /apply/:id/state` ⏳ | 役职 | (V1) |
| 给提交者发评论 #13(**杭田弱点**)| 〇 通知接收 | ✅ 评论栏 | `POST /apply/:id/comment` ⏳ | 役职 | (V1) |
| 寮生特别运航便 一覧显示 #8(**杭田没实装**)| 〇 帰省方法选择时 select | ✅ 编辑 #11 | `GET /bus/special` ⏳ | 学生 + 役职 | (V1) |
| 行事予定显示 #9 | 〇 マイページ | ✅ 编辑 #12 | `GET /events` ⏳ | 学生 + 役职 | (V1) |
| 食堂食数计算(食事不要期间 → 朝/昼/夕 → **Excel 导出**)#7 / Q7 | — | ✅ MealsPage 显示 | `GET /apply/meals/calc?date=` ⏳ | 寮務 | (V1) |

### 7.3 学習(晚自习) — 中学全员 / 高中手动名单(Q2 Q3 答)

> **设计原则**:
> - 中学生 = **默认全员**晚自习
> - 高中生 = **老师手动加**(开学考 + 期末考不合格者)→ 期末后 reset = 名单变动剧烈
> - 学習时间 = **19:40 – 21:45**
> - 学習欠席届 = App 提交,提交期限 = 学習开始前
> - 学習担当老师 1 名

#### 7.3.1 功能矩阵

| 功能 | 学生 iOS | 老师 Web | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|---|
| 学習对象寮生 名单 显示・修改(中学:全员自动 / 高中:手动)#29 / Q2 | — | ✅ StudyRosterPage | `GET/PATCH /study/roster` ⏳ | 寮務教师 | (V1) |
| 学期初 reset / 期末后再构成 | — | ✅ 一括加・一括删 | 同上 | 寮務教师 | (V1) |
| 学習欠席届 提交 Q3 | 〇 ApplyForm(学習欠席届)| — | `POST /study/absence-request` ⏳ | 学生 | (V1) |
| 学習欠席届 截止(学習开始前 = 19:40 前)Q3 | 〇 提交时 block | ✅ 期限警告 | 后端再校验 | 系统 | (V1) |
| 学習欠席届 承认 Q3 | 〇 通知接收 | ✅ 学習担当老师 | `PATCH /study/absence-request/:id` ⏳ | 学習担当 | (V1) |
| 当日夜学習 出席者一覧(从 出寮届 + 学習欠席届 + 学習对象寮生 自动算出)#14 ★ | — | ★ iPad 专用 StudyAttendancePage | `GET /study/today/attendees` ⏳ | 寮監・学習担当 | (V1) |
| 夜学習 出席数计数,时刻 + 名字保存 #15 ★ | — | ★ "出席"按钮按下 | `POST /study/checkins` ⏳ | 寮監・学習担当 | (V1) |
| 学習 迟到・缺席 自动判定(基于时刻,后续可手动修)#20 ★ | — | ★ 修正 UI | 后端 cron + 手动 PATCH ⏳ | 系统 + 寮監 | (V1) |

### 7.4 点呼(朝 / 夜) — ★ iPad

> **详细规格**: `01_specs/rollcall/RollCall_Spec.md`(2026-04-29 §4 §5.2 §5.4 §5.5 §5.6 已修订)

#### 7.4.1 修订小结(2026-04-29 RollCall_Spec.md)

- **§4.2 老师侧时刻表**: "应开始 = 准时截止 -5min" + "兜底自动开始 = -3min" + "准时截止 = 起算迟到"
- **§5.4 老师手动开始**: 窗口固定(不平移,附录 A.4 close)
- **§5.5 自动开始**: 时点从 `window_start` 改到 `on_time_end - 3min`
- **§5.6「点呼総結」中层页(新增)**: 结束后"缺席 / 迟到 / 特殊要求 / 外宿自动跳过"4 区块显示 → "回主页"按钮 → 主页保留"看本场结果"入口

#### 7.4.2 功能矩阵

| 功能 | 学生 iOS | 老师 Web (iPad ★) | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|---|
| NFC 签到(路径 A:卡)| — | — | `POST /checkin?no=XX` ✅ demo_server | 系统 | (D) |
| NFC 签到(路径 B:iPhone BTR + Universal Link)| ⏳ V1.0 | — | 同上 | 学生 | (V1) |
| 点呼開始 / 終了 ★ | — | ✅ live-roll-call.jsx(demo)| `POST /sessions` ⏳ | 寮監 | (D) |
| 自动迟到判定(时刻过 → 黄)| — | ✅ live-roll-call.jsx | ⏳ | 系统 | (D) |
| 「点呼総結」中层页(4 区块)§5.6 | — | ⏳ V1.0 新增 | `GET /sessions/:id/summary` ⏳ | 寮監 | (V1) |
| 主页"看本场结果"入口 §5.6 | — | ⏳ V1.0 | 同上 | 寮監 | (V1) |
| 手动状态变更(绿/黄/红切换)| — | ✅ override-modal.jsx | `PATCH /checkins/:id` ⏳ | 寮監 | (D) |
| 顶部点呼 bar(学生侧 status)| ✅ HomeView TopRollBar | — | `GET /checkin/status` ⏳ | 学生 | (D) |
| 1·2 寮 / 4 寮 别 session R4 | — | ⏳ V1.0 | session.dorm_unit | 系统 | (V1) |

### 7.5 行事予定(完整 calendar,现有不够 Q9)

> **Q9 答**: 现有的日历不够用,要加强
> → 从 demo 单纯显示版升级到**完整 calendar 功能**

| 功能 | 学生 iOS | 老师 Web | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|---|
| 行事予定 阅览(日历 UI)#9 | 〇 calendar view | ✅ 阅览 | `GET /events?from=&to=` ⏳ | 学生 + 役职 | (V1) |
| 行事予定 加・改・删 #12 | — | ✅ 编辑 modal | `POST/PATCH/DELETE /events` ⏳ | 役职 | (V1) |
| 行事予定 通知(加・改时)| 〇 push + in-app | ✅ 编辑即反映 | (内部) | 系统 | (V1) |
| 出寮届 提交时旁边显示行事予定参考 | 〇 ApplyForm 旁边 calendar | — | 同上 | 学生 | (V1) |

### 7.6 寮生特别运航便(学校巴士 / 寮特殊巴士 / 学生选择) — 杭田没实装的差别化功能

> **Q8 答**: 学校有固定 bus(平日给通学生用)+ 宿舍特殊 bus(不固定时间去市区,老师手动加)。学生提交外宿之类的时候要加一个可以选哪班特别巴士或者平日巴士,因为有时候有特别巴士会送学生到机场。

#### 7.6.1 巴士数据模型

```
bus_routes
├── id              UUID PK
├── kind            ENUM('daily_commute','dorm_special')  -- 平日通学便 / 寮特殊便
├── name            TEXT                                   -- "朝便 6:50 寮 → 駅" 等
├── direction       TEXT                                   -- 寮 → 駅 / 駅 → 寮 / 寮 → 空港 等
├── schedule_at     TIMESTAMPTZ                            -- 出发时刻
├── arrival_at      TIMESTAMPTZ NULL                       -- 到达时刻(空港便等)
├── created_by      UUID FK → teachers.id                  -- 役职手动登录
├── visible_to      ENUM('all','dorm_only','men','women') -- 显示对象
└── deprecated      BOOLEAN DEFAULT FALSE
```

#### 7.6.2 功能矩阵

| 功能 | 学生 iOS | 老师 Web | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|---|
| 巴士一覧 阅览 #8 | 〇 マイページ「バス時刻」| ✅ 阅览 | `GET /bus/routes` ⏳ | 学生 + 役职 | (V1) |
| 巴士 录入・编辑・删除 #11 | — | ✅ BusManagementPage | `POST/PATCH/DELETE /bus/routes` ⏳ | 役职 | (V1) |
| 出寮届 提交时选巴士(特别便 / 平日便)#8 | 〇 ApplyForm 帰省方法 = bus 时 dropdown | — | apply 上加关联字段 | 学生 | (V1) |
| 空港送迎特别便 显示(只在 帰国届时)| 〇 帰国届 ApplyForm | ✅ 同上 | `GET /bus/airport` filter | 学生 + 役职 | (V1) |

### 7.7 食堂食数(Q7 答 — Excel 导出)

> **Q7 答**: 估计是 excel 表格,要包含的数据是哪些学生不需要餐食、什么期间。要可以一键导出 excel。

| 功能 | 学生 iOS | 老师 Web | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|---|
| 食堂食数 计算(出寮届 食事不要期间 → 朝/昼/夕 / 日别)| — | ✅ MealsPage 显示 | `GET /apply/meals/calc?date=` ⏳ | 寮務 | (V1) |
| Excel 一键导出 #7 / Q7 | — | ✅ 按钮按下 → .xlsx 下载 | `GET /apply/meals/export.xlsx` ⏳ | 寮務 | (V1) |
| 食堂 iPad 显示 / 打印 | — | ✅ 食堂 iPad(read-only)| 同 GET | 食堂 | (V1) |

### 7.8 寮監事務室 出寮者一覧 ● PC(#22-#27 + R4)

> **设计原则**(老师 #22-#27):
> - 寮監在**事務室 PC**确认
> - **能打印**(#23)
> - **不能编辑**(防误删 / #24)
> - **1·2 寮 和 4 寮 分开显示**(R4 / #25)
> - 出寮届录入后**1 小时以内反映**(#26)
> - Excel / Spreadsheet / 独自 UI 都行(#27)

| 功能 | 老师 Web ● | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|
| 出寮者一覧 显示(事務室 PC)#22 | ✅ DormOutStayListPage(read-only mode)| `GET /apply/active?dorm=1+2` / `?dorm=4` | 寮監 | (V1) |
| 打印按钮 #23 | ✅ window.print() / PDF 导出 | (内部) | 寮監 | (V1) |
| 不能编辑 #24 | ✅ UI 上没编辑控件 | (规约) | 寮監 | (V1) |
| 1·2 寮 / 4 寮 分开 #25 / R4 | ✅ tab / 别的页 | API 上 dorm filter | 寮監 | (V1) |
| 1 小时以内反映 #26 | ✅ auto-refresh 5min | 缓存 TTL ≤ 60min | 系统 | (V1) |

### 7.9 学生指导履历 + 事案录入 #31 #33

> **#33 杭田没实装的差别化功能**:「事案(事件)录入时,文中别学生的姓名 → tap 跳转到该学生个人数据」

| 功能 | 学生 iOS | 老师 Web | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|---|
| 学生指导履历 输入 #31 | — | ✅ DisciplineLogPage | `POST /students/:id/guidance` ⏳ | 寮務教师 | (V1) |
| 学生指导履历 阅览(自己的)| 〇 マイページ「指導履歴」(公开与否待重新讨论 ⏳)| ✅ 全件 | `GET /students/:id/guidance` ⏳ | 学生 + 寮務 | (V1) |
| 事案(事件)录入 #33 | — | ✅ IncidentPage(rich text editor)| `POST /incidents` ⏳ | 寮務教师 | (V1) |
| 事案文中 姓名 tap → 该学生数据画面 #33 | — | ✅ 名字 token → click navigate | `GET /students/:id` | 寮務教师 | (V1) |

### 7.10 学生个人数据显示 #32

> **老师 #32**: 学生個人数据显示(出寮願履歴 / 学習迟到欠席履歴 / 朝点呼迟到欠席履歴 / 夜点呼迟到欠席履歴 / 指導履歴 / 其他)

| 功能 | 学生 iOS | 老师 Web | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|---|
| 学生个人数据 aggregated view #32 | 〇 マイページ(只看自己)| ✅ StudentDetailPage(全件)| `GET /students/:id/profile` ⏳ | 学生(自己)+ 寮務 | (V1) |
| 出寮願履歴 | 〇 マイページ「申請履歴」| ✅ tab | `GET /students/:id/applications` | 学生 + 寮務 | (V1) |
| 学習迟到欠席履歴 | 〇 | ✅ tab | `GET /students/:id/study-attendance` | 学生 + 寮務 | (V1) |
| 朝点呼 / 夜点呼 履历 | 〇 | ✅ tab | `GET /students/:id/rollcall-history` | 学生 + 寮務 | (V1) |
| 指導履歴 | △ 显示与否 ⏳ | ✅ tab | `GET /students/:id/guidance` | 寮務 | (V1) |

### 7.11 リクエスト曲管理(音乐功能 — 4-29 itsuki 拍板"留")

> **itsuki 拍板**: 学生发帖功能 + 社区功能整体 — 砍 / 匿名建议 — 砍 / **音乐功能 — 留**
> 既存 demo round3 的 リクエスト曲管理 工作流(男女寮分け + 提交順 + 承认/拒否)继续用。

| 功能 | 学生 iOS | 老师 Web | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|---|
| 曲リクエスト 投稿 | 〇 投稿表单 | — | `POST /songs` ⏳ | 学生 | (D) → (V1) |
| 男女寮分け显示 + 提交順 | 〇 只看自己投稿 | ✅ コミュニティ管理 リクエスト曲 tab(男寮 / 女寮 tab + 件数)| `GET /songs?dorm=` ⏳ | 寮務 | (D) |
| 承认 / 拒否 / 审查取消 | 〇 通知接收 | ✅ 承认状态 toggle | `PATCH /songs/:id/state` ⏳ | 寮務 | (D) |

### 7.12 规律・处分

| 功能 | 学生 iOS | 老师 Web | 后端 API | 角色 | Demo/V1 |
|---|---|---|---|---|---|
| 减点累计 显示 | ✅ Home 三色 badge + MyPage 详细 | ✅ discipline.jsx | `GET /discipline/:id` ⏳ | 学生 + 寮務 | (D) |
| 减点 内訳(迟到/欠席)| 〇 MyPage | ✅ discipline.jsx 详细 | 同上 | 学生 + 寮務 | (D) |
| 罚扫当番 通知(≥4 点)| ✅ Home badge | ✅ 罚扫リスト | `GET /penalties/cleaning` ⏳ | 学生 + 寮務 | (D) |
| 禁足 通知(≥8 点)| 〇 マイページ | ✅ 罚则 list | `GET /penalties/grounding` ⏳ | 学生 + 寮務 | (D) |
| 密码锁 → 老师通报 | 〇 锁屏 | ✅ accounts.jsx「ロック中」filter | 自动连携 ⏳ | 系统 + 寮務 | (D) |

> **罚则 config 化**(待拍板 §9): 迟到 0.5 / 缺席 1 / 月 4 罚扫 / 月 8 禁足 → `discipline_config` 表化,上线前跟老师商。

### 7.13 通知(R1 邮件固定 + 学生 push)

| 通知种类 | 接收者 | 手段 | API |
|---|---|---|---|
| 出寮届 提交 → 役职 | 役职(寮務部長 等)| **邮件** R1 | `POST /notifications/email` |
| 役职 承认 / 不承认 → 学生 | 学生 | push + in-app | `POST /notifications/push` |
| 学習欠席届 提交 → 学習担当老师 | 学習担当 | **邮件** R1 | 同 email |
| 房间号 一括分配 → 学生 | 学生 | push + in-app | push |
| 学号变更 → 老师 | 老师 | **邮件** R1(误输入检测)| email |
| お知らせ投稿 → 学生 | 学生 | push + in-app | push |
| 巴士时刻表 更新 → 学生 | 学生 | push + in-app | push |

### 7.14 砍掉的功能(4-29 itsuki 拍板)

> **#35 #36 + 4-29 拍板**: 学生发帖 + 社区功能整体 — 砍 / 匿名建议 — 砍

| 功能 | 状态 | 理由 |
|---|---|---|
| **学生掲示板**(投稿 + 阅览 + 通报)| 🚫 **砍** | demo 期间为了"功能完整感"加的,demo 通过后回头看不在核心价值(点呼 + 出寮届 + 学習 + 扣分)里 |
| **社区功能整体** | 🚫 **砍** | 同上 |
| **匿名建议 投稿** | 🚫 **砍** | 同上 |
| **学生 → 帖子 通报功能** | 🚫 **砍**(基底功能砍了所以连带)| - |
| **音乐(リクエスト曲)功能** | ✅ **留**(§7.11)| 轻量、老师反馈没否定、对学生生活感有贡献 |

---

## 8. 数据模型(中心 entity 抜粋)

### 8.1 Student / Account(保留)

```
students                                    -- 学生本体(不变 PK)
├── id              UUID PK                 -- 内部不变识别符
├── grade_code      VARCHAR(2)              -- '01'-'06' (中1-高3)
├── class_code      VARCHAR(2)              -- '01' (A) | '02' (B)
├── seat_no         VARCHAR(2)              -- '01'-'99'
├── student_no      GENERATED ALWAYS AS (grade_code || class_code || seat_no) STORED
├── name            TEXT
├── name_kana       TEXT
├── birthday        DATE
├── gender          ENUM('male','female')
├── category        ENUM('一般寮生','サッカー部')
├── room_no         VARCHAR(8)              -- 'M101' / 'W203' 等
├── dorm_unit       SMALLINT                -- 1 / 2 / 4 (R4 / Q1)
├── is_overseas     BOOLEAN DEFAULT FALSE   -- 留学生 flag (Q11、自己申报)
├── email           TEXT
├── phone           TEXT
├── avatar_url      TEXT
├── registered_at   TIMESTAMPTZ
└── status          ENUM('active','locked','graduated')

CHECK (
  (gender = 'male'   AND dorm_unit IN (1, 2)) OR
  (gender = 'female' AND dorm_unit = 4)
)  -- R4 一致性

accounts                                    -- 认证信息(students 1:1)
├── id, student_id, password_hash, failed_count, locked_until, last_login_at, created_at

teachers                                    -- 教师(R3 = 各 1 名独立)
├── id              UUID PK
├── name            TEXT
├── role            ENUM('寮務部長','寮務課長','国際交流部長','国際交流課長','寮監','学習担当','寮務一般教师')
├── email           TEXT
├── ... (account 相当)
```

### 8.2 出寮届(新增)

```
applications                                -- 出寮届(帰省 / 外泊 / 帰国)
├── id              UUID PK
├── student_id      UUID FK → students.id
├── kind            ENUM('帰省','外泊','帰国')
├── leave_date      DATE                    -- 出寮日(明天起 #3)
├── leave_method    TEXT
├── leave_time      TIME
├── return_date     DATE
├── return_method   TEXT
├── return_time     TIME
├── stay_locations  JSONB                   -- 外泊时,可多个
├── meals_skip_from TIMESTAMPTZ NULL        -- 食事不要 from(#38 from/to 明确)
├── meals_skip_to   TIMESTAMPTZ NULL        -- 食事不要 to
├── flight_dep_air  TEXT NULL               -- 帰国时,出发机场
├── flight_dep_at   TIMESTAMPTZ NULL
├── flight_arr_air  TEXT NULL
├── flight_arr_at   TIMESTAMPTZ NULL
├── bus_route_id    UUID FK → bus_routes.id NULL  -- 选特别运航便等 (Q8)
├── submitted_at    TIMESTAMPTZ
└── status          ENUM('pending','approved_partial','approved','rejected')

application_approvals                       -- 承认的足迹(多役职)
├── id              UUID PK
├── application_id  UUID FK → applications.id
├── approver_id     UUID FK → teachers.id   -- 寮務部長 / 国際交流部長 等
├── approver_role   ENUM(...)
├── decided_at      TIMESTAMPTZ NULL        -- 没承认时 NULL
├── decision        ENUM('approve','reject') NULL
└── comment         TEXT NULL                -- #13 给提交者显示的评论

UNIQUE (application_id, approver_role)
```

### 8.3 学習(新增)

```
study_roster                                -- 学習对象寮生(中:自动 / 高:手动)
├── id              UUID PK
├── student_id      UUID FK → students.id
├── academic_term   TEXT                    -- '2026-spring' / '2026-fall' 等
├── added_by        UUID FK → teachers.id   -- system or teacher
├── added_at        TIMESTAMPTZ
└── removed_at      TIMESTAMPTZ NULL        -- 期末后 reset

study_absence_requests                      -- 学習欠席届
├── id              UUID PK
├── student_id      UUID FK
├── target_date     DATE
├── reason          TEXT
├── submitted_at    TIMESTAMPTZ
├── status          ENUM('pending','approved','rejected')
└── decided_by      UUID FK → teachers.id NULL

study_checkins                              -- 学習出席记录
├── id              UUID PK
├── student_id      UUID FK
├── target_date     DATE
├── checked_at      TIMESTAMPTZ NULL        -- NULL = 缺席
├── status          ENUM('present','late','absent')
└── overridden_by   UUID FK → teachers.id NULL  -- 后续手动修正
```

### 8.4 行事 / 巴士 / 食堂

```
events                                      -- 行事予定 (Q9)
├── id, kind, title, starts_at, ends_at, description, created_by, ...

bus_routes                                  -- 见 §7.6

meals_skip_log                              -- 食堂食数计算用 view
├── target_date     DATE
├── student_id      UUID
├── breakfast_skip  BOOLEAN
├── lunch_skip      BOOLEAN
└── dinner_skip     BOOLEAN
-- → /apply/meals/export.xlsx 聚合
```

### 8.5 RollCall(参考,详细看 RollCall_Spec.md)

```
rollcall_sessions                           -- 点呼 session
├── id, dorm_unit (1+2 / 4), session_type (morning/evening), schedule_mode, ...
├── started_at, started_source (teacher/system)
├── ended_at, ended_source
└── ...

rollcall_events                             -- 各学生的 signin/late/absent
```

### 8.6 指导履历 / 事案 / 其他(⏳)

```
guidance_logs                               -- 学生指导履历 #31
incidents                                   -- 事案录入 #33(rich text + 名字 token)
notifications                               -- 通知(email + push 两对应)
posts / songs / suggestions                 -- §7.14 砍掉的 → schema 删除
```

---

## 9. 待拍板事项

| ID | 项目 | 提案 | 状态 |
|---|---|---|---|
| (a) | 罚则 config 化(迟到 0.5 / 缺席 1 / 月 4 罚扫 / 月 8 禁足)| `discipline_config` 表化,上线前跟老师商 | 上线前 |
| (b) | 学号变更时要不要老师承认 | 案 1: 学生自由变更 + 履历 / 案 2: 学生申请 → 老师承认 | itsuki 拍板待 |
| (c) | 房间号 一括分配的单位 | 个室 / 部屋＋床号 | V1.1 设计时 |
| (d) | 学生个人数据的"指导履历"给学生本人显示吗 | 案 1: 显示(透明性)/ 案 2: 不显示(教育考虑)| itsuki 拍板待 |
| (e) | 寮監 = 几名 / 当番轮替 | iPad 共用前提下,运用方式另定 | 老师追加问题待 |
| (f) | 高中学習对象名单的 reset 时期 | 期末后立即 reset / 下学期初 reset | 学習担当老师确认待 |
| (g) | 寮 物理关系(1 寮和 2 寮 物理上相邻?栋 / 楼?)| Q1 答里性别 + 点呼单位定了,物理关系待 ⏳ | 老师追加问题待 |
| (h) | 杭田 既存 UI 参考要不要 | itsuki 说"没参考价值",老师说"基本上什么都给看"| 矛盾,itsuki 再判断 |

---

## 10. 改订历史

| 日期 | 改订内容 | 担当 |
|---|---|---|
| 2026-04-23 | 首版(学号体系 + 房间号 + 改动履历 + 功能矩阵 + 数据模型中心 entity)| [Mac-demo-sprint] CC |
| **2026-04-29 晚** | **大重写** — 老师 4-29 LINE 38 条要件 + Q1-12 答案 + R1-R4 硬约束 + itsuki 4 条砍/留 全反映。新章 §2(R1-R4)+ §3(5 角色 + 设备分布)+ §7.2-7.14(出寮届 / 学習 / 行事 / 巴士 / 食堂 / 出寮者一覧 / 指导履历 / 个人数据 / 砍掉功能)。RollCall_Spec.md §4-§5.6 修订参照。数据模型 §8 扩充(applications / study / events / bus / meals / teachers)+ R4 一致性 CHECK。**同时**:删掉文件级版本号(原 v0.1 / v0.2 标记,违反单源真值原则;改用 git history + 本节作为唯一改订记录)。中文骨架重写,只保留专有名词的日语 | itsuki + CC |

---

## APPENDIX A — 老师 4-29 LINE 原文 + 38 条要件 + Q1-Q12 答案

> **保留作 evidence**(中文翻译 + 日语原文)
> **完整翻译 + 38 条整理** 看 `00_admin/TODO.md §🎯 4-28 demo 后老师反馈 backlog`
> **聊天原文记录** 看 `05_logs/raw/2026-04-29.md`

### A.1 平台标记

- 〇 = 多平台(iOS / Web / PC 都可)
- ★ = iPad 专用
- ● = 事務室 PC 专用

### A.2 38 条要件小结(按 5 角色分组)

- **〇 学生用 出寮届提交**(#1-#9)
- **〇 役职 出寮届承认**(#10-#13)
- **★ 寮監・学習担当 点呼/学習用**(#14-#21)
- **● 寮監事務室 出寮者一覧**(#22-#27)
- **〇 寮務部教师确认用**(#28-#33)
- **老师订正**(#34)= 通知 = 邮件固定(→ R1)
- **itsuki 补足**(#35-#39)= 学生发帖砍 / 社区砍 / 音乐留 / 食事 from/to 明确 / 教师单独账号

### A.3 R1-R4 硬约束(见 §2)

- R1 通知 = 邮件
- R2 老龄寮監 一本道 UX
- R3 教师 1 人 1 账号
- R4 1·2 寮 / 4 寮 分别表示

### A.4 12 Q 答案小结(itsuki 4-29 已答)

- **Q1**(寮单位): 1·2 寮 = 男 / 4 寮 = 女,3 寮 废止
- **Q2**(学習对象): 中学全员自动 / 高中开学考+期末考不合格者手动 → 期末后 reset
- **Q3**(学習欠席届): App 提交,19:40 开始前,专任老师承认
- **Q4**(役职账号): 各 1 名,退出 → 下个人登录
- **Q5**(寮監): 几名未定,iPad 共用,退出登录切换
- **Q6**(PC 环境): 職員室 PC + 事務室 PC + 寮管室 iPad + 食堂 iPad
- **Q7**(食堂): Excel 导出,不要餐食的学生 + 期间
- **Q8**(特别便): 学校固定便 + 寮特殊便(市内・空港),学生选
- **Q9**(行事予定): 现有不够,要加强
- **Q10**(教师密码重置): 项目负责老师经手
- **Q11**(留学生 flag): 注册时自己选
- **Q12**(杭田 UI): itsuki "没参考价值" / 老师"基本上什么都给看"(矛盾,判断保留)

### A.5 老师 LINE 完整原文(日语,再录,作 evidence)

```
寮の点呼、帰省・外泊・帰国願、学習欠席等の処理ソフトを作ってくれていると聞きました。ありがとう！
作った後に「あれが必要」「この機能つけて」と言われても、大幅な変更が必要になり、困ることになるかもしれないので、必要な要件（機能）を書き出しておきます。
よろしく！！

〇：どこでも入力、処理ができることがベストなので、android,iphone対応が望ましい。webアプリかappか。
★：寮監が点呼に使用するため、寮ipadで使用できることが望ましい。
●：寮監が寮事務室で確認できるよう、スプレッドシート、Excel、webアプリ等が望ましい。

〇生徒用届提出用
・他の生徒を入力できないようにする
・帰省・外泊・帰国願（以下出寮願）の入力ができる
　帰省：出寮日、帰省方法、帰省時刻、帰寮日、帰寮方法、帰寮時刻
　外出：帰省に加えて外泊先（複数入力可）、食事不要期間
　帰国：外出に加えて出発空港、飛行機空港発時刻、到着空港、飛行機空港到着時刻
　※出寮日は明日以降しか選択できないようにする
　※不要な入力を防ぐため、入力不要な場合は入力欄を表示しない
・入力完了後、以下の役職に承認を得たこともしくは承認を得ていないことが出寮届提出者にわかるようにする
　帰省：寮務部長、寮務課長
　外泊：寮務部長、寮務課長＋留学生の場合には国際交流部長、国際交流課長
　帰国：外泊と同じ
・出寮願提出時、上記の役職に通知を送る（修正→現在メール通知）
・食堂スタッフへの食数通知（食事不要期間から計算、Excel 出力）
・寮生特別運航便一覧表示（杭田未実装）
・行事予定表示

〇役職の出寮届許可用
・出寮届を確認し、許可もしくは不許可を出す
・寮生特別運航便の入力＆編集
・表示する行事予定表の変更
・出寮届提出者にコメントを表示する（杭田弱）

★寮監・学習担当使用点呼学習用
・出寮願、学習欠席届、学習に出席する寮生から本日夜学習出席者リスト
・夜学習出席カウント、時刻 + 名前保存
・本日夜点呼出席者リスト
・夜点呼出席カウント、時刻 + 名前保存
・本日朝点呼出席者リスト
・朝点呼出席カウント、時刻 + 名前保存
・時刻から学習・朝点呼・夜点呼の遅刻、欠席を判断（後から修正可）
※高齢寮監使用、極力単純化（一本道）

●寮監確認用出寮者一覧
・事務室 PC で確認
・印刷可能
・編集不可（誤消去防止）
・1,2 寮と 4 寮 別表示
※Excel / Spreadsheet / 独自 UI どちらでも、出寮届入力から 1 時間以内反映

〇寮務部教師確認用
・寮生の追加、削除
・学習に出席する寮生の変更
・出寮届一覧閲覧、入力（教師用は当日入力可）
・生徒の指導歴入力
・生徒個人データ表示（出寮願履歴 / 学習遅刻欠席履歴 / 朝点呼遅刻欠席履歴 / 夜点呼遅刻欠席履歴 / 指導履歴 / 其他）
・事案（事件）入力（学生氏名 → tap で個人データ）杭田未実装

訂正：役職への通知はメールにしてください。... 提出したことが「残る」からです。
```

---

**END** — 改功能时先更新本文,再进实装。

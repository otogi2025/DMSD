# Demo 4-28 — 代码 Agent 给需求会话的疑问队列  <!-- VERSION_OK -->

> **作用**：代码 agent（`[Code-Agent]`）读完 8 份 briefing 后，开工前需要需求会话（`[Mac-demo-sprint]`）对齐的模糊点。
> **协作规则**（见 `for_code_agent.md §8`）：代码 agent 写到这里 → itsuki 看到后同步到需求会话 → 需求会话改 `scope_tier.md` / 其他档 → 代码 agent 按更新继续。
> **代码 agent 不直接改需求档**。
> **建立**：2026-04-21 晚，D1 onboard

---

## 2026-04-21 晚 · 首批 5 个疑问（阻塞 D2-D3 开工）

### Q1 · 缺席记录何时产生？（阻塞 D2 后端 + D4 前端）

**背景**：
- `scope_tier.md §1.3` 座位表颜色：准时=绿 / 迟到=黄 / **缺席=红** / 未签到=灰。
- `§1.12` 扣分统计：需要后端算"本月迟到 N 次 + 缺席 M 次"。
- 但目前 `models.Checkin` 只在"学生真 tap"时生成 —— **缺席的学生永远不会产生 Checkin 行**。

**具体问题**：session.end 结束时，未签到的学生怎么记录？

**方案 A**（我推荐）：`end_roll_call` 时后端扫一遍全员，没签到的自动插一条 `Checkin(status='absent', method='auto')`。扣分统计直接 SUM，座位表 live API 直接读。
**方案 B**：不写 absent 行。缺席由前端聚合（students - 签到 = 缺席）。扣分统计每次 query 时临时算。

**推荐 A**：单源真值在数据库，前端/扣分/搜索都简单；B 会在三处各算一次口径容易飘。

**等 itsuki 回复**：选 A 还是 B？

---

### Q2 · `Checkin.status` 字段要不要加？迟到窗口多少分钟？（阻塞 D2 schema）

**背景**：
- scope 里反复出现 `on_time / late / absent / exempt / manual_override` 5 种状态，但当前 `models.Checkin` 没有 `status` 字段，只有 `checkin_at` 时间戳。
- 迟到判定需要阈值（比如 session 开始后 5 分钟内=准时，5-15 分钟=迟到，>15 分钟=缺席？）

**推荐方案**：
1. `Checkin` 表加 `status` 字段（`on_time / late / absent / exempt / override`）
2. POST `/api/checkin` 时后端根据 `now - session.started_at` 算 status：
   - ≤ `late_window_minutes`（默认 5）→ `on_time`
   - ≤ `absent_window_minutes`（默认 20）→ `late`
   - > `absent_window_minutes` → `absent`（这种情况学生很晚来 tap 了，按缺席处理但仍记录）
3. 阈值存 `discipline_config`，不硬编码

**等 itsuki 回复**：迟到窗口 5 分钟 OK 吗？缺席窗口 20 分钟 OK 吗？（demo 时老师开点呼后 itsuki 立刻 tap 演准时，手动等 6 分钟演迟到不现实，所以 demo 这个窗口只是代码路径，不真演。但数字要拍板。）

---

### Q3 · iOS App 怎么"切学生"？（阻塞 D3 iOS 起项目）

**背景**：
- `demo_script.md §6` 要求用"另一个模拟学生账号"演请假 → iPad 座位表橙色问号 → 老师审批。
- iOS App 6 屏：签到 / 健康 / 请假 / 外宿 / 归国 / 扣分查看。
- **backend 没有学生 Login API**（只有老师 `teacher/1234`）。

**我的方案**（推荐）：
- iOS App 完全不做登录流程。
- App 顶部栏一个"切学生"下拉选单（从 `GET /api/students` 拿列表），默认 itsuki。
- 所有 API 调用带 `student_id: currentStudentId`。
- Demo 场景：itsuki 切到自己 → 提健康；切到"張三" → 提请假；老师 iPad 看到两个座位叠加图标。

**等 itsuki 回复**：
- 接受这个"切学生下拉"方案吗？
- 还是想做真的 App 登录（增加工作量 + 增加 Q9 管理员追问的攻击面）？

---

### Q4 · 老师 Web UI 的语言是中文还是日语？（阻塞 D4 前端）

**背景**：
- `demo_script.md` 的台词是中文（itsuki 对管理员讲话）。
- 但宿舍管理员大概率是**日本人老师**（itsuki 在日本上学）。
- iPad Safari 上的页面文字（按钮、表头、提示）是**日语**才能让管理员看懂，还是中文？
- 如果双语，工作量 +30%（或用一个简单 i18n dict）。

**我的倾向**：
- **UI 文字日语**（管理员看）；**代码注释中文**（itsuki 看）；**commit message 中文**。
- itsuki demo 时用中文讲解，但管理员看 iPad 上显示的是"点呼开始 → 点呼を開始"。

**等 itsuki 回复**：
- 管理员是日本人吗？（影响 UI 语言）
- 日语文字 itsuki 自己写还是要我用常见宿舍/点呼术语起草再她校对？

---

### Q5 · seed 数据规模 + 扣分历史怎么造？（阻塞 D2 seed.py + D6 扣分展示）

**背景**：
- 当前 `seed.py` 只有 6 个学生。
- `demo_script.md §8.2` 要展示"本月全员排名 + 罚扫名单 + 禁足名单 + 连续超标预警"。
- 6 个学生看排名没压迫感；"罚扫/禁足名单"要求某几个学生有真实的历史违规数据。
- `§1.12` 学生端看"本月迟到 2 次 + 缺席 0 次 + 距离罚扫差 3 分" → 需要 itsuki 账号有真实扣分历史。

**我的方案**（推荐）：
- seed 扩到 **30 学生**（本人 itsuki + 张三/李四/王五/田中/佐藤 + 再 mock 24 人）
- seed 一个 fake "过去 30 天"的签到历史：
  - itsuki：迟到 2 次 + 缺席 0 次（本月 1 分，距罚扫 3 分，距禁足 7 分）
  - 張三：迟到 2 + 缺席 3 = 4 分 → 刚好触发下月罚扫（demo 时在"预警名单"展示）
  - 李四：迟到 4 + 缺席 6 = 8 分 → 触发下月禁足
  - 田中/佐藤/王五：0 违规（展示"完美出勤"组）
  - 其他 24 人：随机散布 0-3 分

这让 demo_script §8 的所有数字都"真"。

**等 itsuki 回复**：
- 30 学生 OK 吗？少了像 mock，多了 iPad 座位表渲染压力大（30 还行）。
- 扣分历史剧本接受吗？（我会写成可重跑的 `seed.py`，itsuki demo 前 `python seed.py --reset` 一次恢复）
- 有没有其他"想在排名里出现的名字"？（比如宿舍真同学的日语名字，让管理员有代入感）

---

## 2026-04-21 晚 · 非阻塞但建议确认

### N1 · "红十字"图标的文化问题

scope §1.3 + demo_script §5 用"红色十字"叠加表示健康问题。但日本的"赤十字"是赤十字社的专有标志，随便用可能有版权敏感。建议改为 🏥 / 🤒 / ⚠️ / 红色圆点。**D4 前端开写前我会默认用医院 emoji 🏥，itsuki 不喜欢再改**。

### N2 · Mac 局域网 IP 怎么传给 iPhone / Pi / iPad

`for_code_agent.md §7.3` 说"不要硬编码 Mac IP"，建议：
- 后端：读环境变量 `HOST_IP`，前端从 `window.location.host` 拿（前端也跑在同一个 FastAPI 下就自动同步）
- iOS：SwiftUI 里 `@AppStorage("baseURL")` 做成设置页面（itsuki 零基础 → 写成代码里一个常量更好，demo 前手动改一行，我会加 `// 改这里 →` 注释让她清楚）
- Pi：`.env` 文件读 `BACKEND_URL`，我会附一个 `.env.example`
- iOS Shortcuts Automation：URL 填 Mac IP，itsuki 配 Shortcut 时写死。itsuki 已经要亲手配这个。

**默认执行方案**：除非 itsuki 反对，我按上面方案做。

### N3 · WebSocket vs 3 秒轮询

`sprint.md §5` 风险清单说"WS 跑不通 → fallback 3 秒轮询"。**默认我先走 WS**，D4 前端接入，D5 真连 iPad 测试如果不稳，再降级轮询。不做"两路同时在"。

### N4.5 · Demo 后功能 backlog（itsuki 2026-04-21 晚要求"帮我记着"）

以下 feature itsuki 明说"demo 暂不做，但记下"，demo 4-28 完成后纳入 backlog：

- **后端自动迟到/欠席警告短评脚本**：后端常驻 script 监测每个学生累计的遅刻・欠席次数，达到阈值时自动生成"经常迟到 / 经常缺席"之类短评，推送到教员 Web 的一个专用栏目（**Round 3 UI 里已预留视觉占位**，见 `03_dev/demo_4-28/teacher_web/round3_handoff/Round3_Prompt.md §7.5.1`，amber badge "自動アラート（開発中）" card，demo 当日不启用逻辑）。
  - 阈值数字：与 `discipline_config` 联动，上线前和老师商议
  - 推送方式：教员 Web 页面 banner 显示 + push 通知（可选）
  - 后端实装：FastAPI scheduled task (apscheduler) 或独立 worker
  - 关联：`规律・処分` 页 / `通知中心` 页 / 学生 iOS App 的"本人向け警告"
  - 实装优先级：demo 采纳后第一批 post-demo feature

### N4 · briefing §3 路径引用已过期（需求会话请同步）

**触发**：2026-04-21 晚 itsuki 指令 "demo 的文件单独放到 demo 文件夹里，不要污染主项目"。`[Code-Agent]` 已执行：
- `03_dev/backend/` → `03_dev/demo_4-28/backend/`（`mv`，因 backend 是 untracked 状态无法 `git mv`；README.md 内 `cd 03_dev/backend` 已同步改为 `cd 03_dev/demo_4-28/backend`）
- 新建 `03_dev/demo_4-28/{teacher_web, Student_iOS_new, device}/`

**请需求会话更新**：
- `for_code_agent.md §3` "你负责的文件" 4 行路径
- `for_code_agent.md §4` 技术栈表里对应 skeleton 路径描述
- `scope_tier.md §4` "代码 agent 入口" 4 行路径
- `sprint.md` 如有路径引用也同步

代码 agent 不改 briefing 本身（§3 权限）。

---

---

## 2026-04-21 晚 · itsuki 答复首批 5 问

- **Q1 答复** → 方案 A，session.end 时后端扫全员自动插 `Checkin(status='absent', method='auto')`。老师端展示用。
- **Q2 答复**（2026-04-21 晚 itsuki 追加纠正，并指明 `RollCall_Spec.md` 里写过权威规则）→ **保留 late 状态**，规则按 spec：
  - **准时**：`window_start ≤ t ≤ on_time_end` → `on_time`（绿）
  - **迟到**：`t > on_time_end` 未签 → 座位自动变 `late`（黄），"过点了"预警给老师；过点后才来签到的仍记 `late`（签到成功但迟到）
  - **缺席**：老师点"结束点呼" → 所有仍未签到的（灰+黄）全变 `absent`（红）
  - Spec §5.3 还有 `late_end = on_time_end + 1 秒`（过 late_end 返回 TIMEOUT 不给签）+ `auto_end_at = on_time_end + X 分钟` 系统兜底自动结束 —— demo 阶段**略过 TIMEOUT 机制**（允许学生随时签到直到老师点结束），等 v1.0 再实装
  - **demo 迟到阈值**：沿用 spec §4.2 老师 slack 数字 **3 分钟**（老师点"开始"后 3 分钟开始算迟到）。存 `discipline_config.late_threshold_seconds = 180`，彩排时 itsuki 可临时调小（如 30 秒）方便演示
  - [Code-Agent] **撤之前的 "砍 late" 反问**，按 spec 规则实装 5 状态（`on_time / late / absent / exempt / override`）。Spec 还有 `absence_request_pending`（黑 overlay）+ `exempt_range`（独立 base_status）在 demo 里也要考虑是否收敛
- **Q3 答复** → 接受"切学生下拉"方案，iOS App 不做登录。
- **Q4 答复** → **Web 和 iOS App 的 UI 文字都用日语写**。代码注释中文、commit message 中文、开发沟通中文不变。
- **Q5 答复** → 30 学生 + 3 档扣分历史剧本接受。

**[Code-Agent] D2 开工解除阻塞 ✅**（Q2 late 状态砍掉的反问不阻塞）。

---

## 历史状态

- 2026-04-21 晚 · `[Code-Agent]` 建立本文件 + 提首批 5 阻塞问题 + 3 非阻塞建议
- 2026-04-21 晚（稍后）· itsuki 当场答复 Q1-Q5，`[Code-Agent]` D2 开工解除阻塞；仅留 Q2 "late 状态是否完全砍掉"一个低风险反问

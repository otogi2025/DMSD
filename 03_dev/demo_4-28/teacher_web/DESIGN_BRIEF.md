# 老师 Web — 设计 & 实装状态

> **系统名**：**Tomoshibi**（灯火，2026-04-21 定名）。UI 里的品牌字符串一律 `Tomoshibi`，不用 DMSD。
> **建立**：2026-04-21 by [Code-Agent]（原为 Claude Design 任务书 v1）
> **2026-04-21 晚更新**：Round 2 Claude Design 产出已落盘本目录，itsuki 拍板"就按这个版本来"。本文从"任务书"转型为"实装状态追踪"。
> **权威源**：`index.html` + `round2/*.jsx`（设计 = 代码）

---

## 1. 当前状态

Claude Design（claude.ai/design）产出的 Round 2 原型已 handoff + 落盘。itsuki 2026-04-21 晚在 Claude Design 里点了 "Save as standalone HTML: DMSD Round 2 Prototype.html" → 生成 handoff bundle（6.3MB gzip → 9.1MB tar）→ [Code-Agent] 通过 Anthropic 设计分享链接 fetch + 解压 + 导入本目录。

**设计方向敲定**：Variation C "涼 (Ryō)" — 近黑 `#14171f` + コバルト `#2b4d8c` accent + Noto Sans JP + 稍圆 8-12px + 极薄 shadow，近 monoxer / modern SaaS but 克制。完整 tokens 见 `round2/theme.jsx`。

## 2. 本目录文件清单

```
teacher_web/
├── index.html                       # 主入口（原 "DMSD Round 2 Prototype.html"，引用外部 jsx + CDN）
├── standalone-offline-backup.html   # 8.4MB 完整内嵌版（demo day 兜底：若 CDN/WiFi 断也能跑）
├── round2/
│   ├── theme.jsx                    # Ryo 色 token + 24 学生 ROSTER 种子数据
│   ├── login.jsx                    # ログイン画面
│   ├── shell.jsx                    # 左 nav + topbar（7 大类菜单已写）
│   ├── roll-call-landing.jsx        # 点呼ダッシュボード（截图里那页）
│   ├── live.jsx                     # フルスクリーン実时座席表（点呼中，主役=学生姓名大字）
│   └── override-modal.jsx           # 手動調整 modal
├── handoff/                         # Claude Design handoff 原档（AC 素材）
│   ├── README.md                    # Claude Design 给 coding agent 的指引
│   ├── chat1.md                     # itsuki ↔ Claude Design 完整对话（AC 叙事素材 ⭐）
│   ├── design-system-round1.html    # Round 1 3 variations 比较页
│   └── uploads/                     # itsuki 上传给 Claude Design 的截图
├── designs/                         # Round 3+ 产出时往这里丢
└── DESIGN_BRIEF.md                  # 本文件
```

## 3. Round 2 已实装范围

| 页面 | 文件 | 状态 |
|---|---|---|
| `/login` | `round2/login.jsx` | ✅ UI 完成（teacher/1234 硬编码验证） |
| `/roll-call` 点呼ダッシュボード | `round2/roll-call-landing.jsx` | ✅ UI 完成（session 选择 + 开始钮 + 4 统计卡 + 最近 session list） |
| `/roll-call/live` 实时座席表 | `round2/live.jsx` | ✅ UI 完成（24 人 6 列 grid，学生姓名大字 24-28px，部屋 11px，学号 10px mono；4 状态；叠加 badge） |
| 手動調整 modal | `round2/override-modal.jsx` | ✅ UI 完成（4 单选 + 原因必填 + 欠席届同時承認 checkbox） |
| Shell（左 nav + 7 大类菜单） | `round2/shell.jsx` | ✅ UI 完成 |

**状态枚举（theme.jsx 里已定）**：`ok / absent / exempt / unknown`，**当前没有 late 黄色**（和 spec §4.1 五色表冲突 — 见 §5 追记）。

## 4. 未实装范围（Round 3 计划）

Tier 1 剩 7 页（Claude Design 尚未做）：
- `/applications/outstay` 外泊列表 + 详情 + 承認
- `/applications/return-home` 帰国同上
- `/discipline` 全员月排名 + 罚扫 / 禁足 / 警告リスト
- `/records` 签到历史按日筛
- `/search` 按学生 / 按日期聚合
- 健康上报 flow（学生 iOS 提交 → Web 座席 🏥 overlay）
- 请假 flow（学生 iOS 提交 → Web 座席 ? overlay → 一键承認）

Tier 2 skeleton 15 项（一个统一 `<SkeletonPage>` 组件复用）：
清掃審査 / 帰県申請 / タクシー予約 / バス時刻 / 行事カレンダー / 匿名建議 / 忘れ物 / 寮掲示板 / リクエスト曲 / 宅配通知 / 長期免除 / 清掃評分・抵扣 / 連続超標預警 / CSV・PDF 出力按钮 / 通知中心（聚合 4 数字）

## 5. ⚠️ Spec 对齐项（Round 3 前 itsuki 决策一次）

Round 2 原型里 `theme.jsx` 的状态只有 4 色（`ok / absent / exempt / unknown`，**无 late**），注释 `// seat statuses (no late)`。但 2026-04-21 晚 itsuki 纠正："黄色是迟到，等到了具体时间还没签到的人，就自动变成黄色"，并指明 `01_specs/rollcall/RollCall_Spec_v0.1.md §4.1 §5.3` 里有权威规则（绿/黄/红/灰/蓝 + overlay 黑）。

**影响**：`theme.jsx` 需要加 `late` token（黄色系）+ `late` status；`live.jsx` 需渲染第 5 色；session 开始后达到迟到阈值（默认 3 分钟 = `on_time_end - window_start`）时前端自动把"未签到的 unknown"渲染成 late 黄。

**Round 3 开工前要做**：
- [ ] itsuki 下次丢给 Claude Design 一条消息让它加 late 状态 + 迟到阈值逻辑（或代码 agent 直接在 `round2/theme.jsx` + `round2/live.jsx` patch）
- [ ] 迟到具体时间做成 `discipline_config.late_threshold_seconds`（默认 180），demo 彩排可临时改小

## 6. 下一步（code agent 侧实装路线）

这份设计当前是静态 prototype（seed 假数据在 `theme.jsx ROSTER` + `index.html seed()` 函数里）。变成**真前端**需要：

1. **D3**（4-23）：把 `seed()` 函数改成 `fetch('/api/students')` + `useEffect` 初始化
2. **D3**：接入 WebSocket（`new WebSocket('/ws/teacher')`），收 `checkin / outstay_new / ...` 事件后 `setStudents` 更新
3. **D3**：点"点呼を開始" 改成 `POST /api/roll-call/start`；"終了" 改成 `POST /api/roll-call/end` + 后端补 absent
4. **D4**：override modal 的保存改成 `PATCH /api/checkins/{id}/override`
5. **D5**：Tier 1 剩余 7 页按 Claude Design Round 3 产出补
6. **D6**：Tier 2 skeleton 15 项一次性生成

接入方案：**不改设计师的 JSX 源码结构**，只把数据源从 ROSTER 常量 → API response。所有 UI 保持 pixel fidelity（handoff `README.md` 明确要求 "match visual output"）。

## 7. Demo Day 兜底

- 正常：iPad Safari 打开 `http://{Mac IP}:8000/teacher_web/` → 经 FastAPI StaticFiles 挂载 → 加载 index.html
- CDN 断（Google Fonts / unpkg React 不可达）：改打开 `standalone-offline-backup.html` —— 8.4MB 完全内嵌，无外部依赖

## 8. 日语 UI 术语对照表（Round 2 已用词 + 待 Round 3 扩展）

| 中文 | 日语（Round 2 已用） |
|---|---|
| 点呼 | 点呼 |
| 开始 / 结束 | 開始 / 終了 |
| 准时 / 迟到 / 缺席 / 免点呼 / 未签 | 時間内 / 遅刻（Round 3 待加）/ 欠席 / 免除 / 未点呼 |
| 座位表 | 座席表 |
| 手动改判 | 手動調整 |
| 请假申请 | 欠席届 |
| 外宿 / 归国 / 归县 / 出租车 | 外泊 / 帰国 / 帰省 / タクシー |
| 扣分 | 減点 |
| 罚扫 / 禁足 | 清掃罰則 / 外出禁止 |
| 预警 | 警告リスト |
| 开发中 | 開発中 |
| 切换账号 | 切替（左下）|
| 老师 | 先生（Round 2 用 "田中 先生"）|
| 第 X 寮 | 第一寮（Round 2 mock）|

---

## 附录 · 历史（Round 1-2 任务书原文）

Round 1-2 的 Opening Prompt 已被 Claude Design 消化，原文留在 `handoff/chat1.md` 里（作 AC 素材 —— 展示 itsuki 如何引导 AI 设计师迭代出满意结果）。

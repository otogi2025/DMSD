# 2026-05-26 — teacher_web Vite 实装版废弃 + Ryō polish 尝试回滚

> 5-26 第 3 个会话（前 2 个：早段 iOS Bot 1 复查 + 全项目中枢注册 → `raw/2026-05-26.md` / 晚段-2 dmsd-startup skill 立项 + DMSD CLAUDE.md 247→190 行重写 → `raw/2026-05-26_dmsd-startup+CLAUDE.md大改.md`）。
> 本会话主线：itsuki 让 CC 推进 teacher_web → CC 起 Vite dev server → itsuki 看到「这他妈根本不是我的 web」→ 拍板「Vite 实装版垃圾，归档，用 B」→ CC 归档 + 跑 frontend-design skill 提 Ryō polish → itsuki 看完不喜欢 → 全部回滚 → 修破工具 + 文档同步。

---

## 21:00 [推进] itsuki 启动「推进 teacher_web 开发」

### 背景

itsuki 进会话第一条：「我们推进 teacher web 的开发 我是不是有一个前段的 skill？」

「前段」= 「前端」typo（错别字）。

CC 报告 — 有 plugin 提供的 `frontend-design` skill（建网页组件 / 页面 / 整个前端应用时调，专门做「不像 AI 默认审美」的高质量界面）。

提 A/B/C 范围：
- A — Vite 实装版（要上线那套）
- B — 4-21 Ryō prototype（Claude Design 出的那套）
- C — 调 skill 让它接管

itsuki 选 C（「调那个 skill，优化一下 teacher web 的设计」）。

### itsuki 原话

> "我们推进 teacher web 的开发 我是不是有一个前段的 skill？"
> "调用那个 skill，优化一下 teacher web 的设计"

### AC 价值

- **核心问题 #2 技术判断** — itsuki 主动用「工具盘点」开会话（不是直接 dive 进代码） — 元层面的工作方式判断
- **模式 5 触发候选** — itsuki 不完全确定自己有哪些 skill 工具（「我是不是有...」） → CC 报告资源 → itsuki 选哪个用

#AC候选 #技术判断 #工具发现

---

## 21:05 [学习] 前端开发流程教学 — 三窗口工作流 + HMR

### 背景

CC 准备起 Vite dev server，itsuki 问：「先告诉我，我现在怎么看 teacher web？」+ 后续追问：「一般开发者开发的时候怎么做的呢？怎么变改边做？」

itsuki 零基础前端开发 — 他不知道：
- 前端开发的「实时反馈循环」
- dev server / HMR 是什么
- 改文件后浏览器怎么自动刷新

### CC 教了什么

**核心：三窗口同开 + 实时反馈循环**

3 个窗口分工：
1. 编辑器（VS Code）— 改 .jsx / .css
2. 浏览器（Chrome / Safari）— 看 UI
3. 终端（跑 `npm run dev` 的黑框）— 看开发服务器日志 + 报错

**为啥秒刷新 — HMR（Hot Module Replacement，热模块替换）机制**：

Vite 在后台监听文件变化，只把改的那一小块送到浏览器替换，不整页重载。所以：
- 弹窗填一半 → 改样式 → 弹窗还在 + 内容不丢
- 改按钮颜色 → 100 毫秒内浏览器颜色变了

**跟 itsuki 熟悉的两端反馈速度对比表**：

| 端 | 改代码后等多久看到效果 | 工具 |
|---|---|---|
| iOS（Swift / Xcode） | 5-15 秒（重编译 + 模拟器重启 app） | Xcode |
| backend（Python / FastAPI） | 1-2 秒（uvicorn `--reload` 重启 worker，worker = 处理请求的进程） | `uvicorn --reload` |
| 前端 Vite | 50-200 毫秒（几乎实时） | `npm run dev` |

**前端是 3 端里反馈最快的** — 所以前端开发节奏可以很碎：「调一下间距 → 看 → 不对再调 → 看」每次循环 5 秒。

### itsuki 原话

> "先告诉我，我现在怎么看 teacher web？"
> "一般开发者开发的时候怎么做的呢？怎么变改边做？"

### AC 价值 ⭐⭐⭐⭐⭐ 模式 5 顶级

- **核心问题 #5 自己認識** — itsuki 主动承认不知道 + 主动问真正的开发者怎么做 = 学习能力证据
- **模式 5 完整结构**（按 §1.2 标准格式）：
  - 之前：不知道前端怎么「边改边做」
  - 转折：5-26 跟 CC 协作做 teacher_web，主动问「真开发者怎么搞」
  - 现在：理解「三窗口工作流 + HMR + 跨端反馈速度差异」
- **学术延伸性**：
  - 软件工程「反馈循环长度」概念 — Lean / DevOps 核心议题
  - 跨技术栈的工具链对比能力（iOS / backend / 前端 3 端反馈节奏完全不同）
  - AC 面试可挂「我对开发工具链的理解」

#AC候选 #AC強候補 #认知改变 #学习 #方法论

---

## 21:15 [假设崩+推翻] itsuki 看到的不是「我的 web」 — Vite 实装版整体废弃

### 背景

CC 起 Vite dev server → 浏览器打开 `localhost:5173` → itsuki 看到屏幕。

itsuki 第一反应：

> "这他妈根本不是我的 web 啊，这他妈是什么？"

### 经过

CC 调查发现 `v1/` 目录两套东西并存：

1. **Vite + TypeScript 实装版**（5-02 起 v0.8 立项做的，入口 `index.html` → `main.tsx` → `App.tsx`，4 标签页：Applications 申请 / Study 学習 / RollCall 点呼 / Teachers 教师）
2. **Ryō standalone HTML 老 demo**（`v1/src/index.html` 7774 行，4-21 Claude Design Round 2 产出，含明文密码 `12345678` — 历史 FC-024 / A-039 漏洞）

itsuki 心里的「我的 web」 = 4-21 Round 2 Ryō prototype（涼，深色蓝调 + コバルト + Noto Sans JP + 24 学生座席表 + 实时点呼仪表盘）。

但 Vite 跑的是 5-02 实装版。**两套不是同一个东西**。

### CC 失误

CC 第一时间没核对启动到底是哪一套 → 直接说「就是你的 web」 → 翻车被怒怼。

### itsuki 拍板 — 推翻 5-02 立项决定

> "Vite 实装版就是个垃圾，给我归档，用 B"

**B = 用 Ryō standalone（4-21 Claude Design 出的那套）**。

### itsuki 原话

> "这他妈根本不是我的 web 啊，这他妈是什么？"
> "Vite 实装版就是个垃圾，给我归档，用 B"
> "之前的垃圾 web 不要再污染我的项目文件了，归档"

### AC 价值 ⭐⭐⭐⭐⭐ 模式 3 + 模式 2 + 模式 6

- **模式 3 失败→吸取教训**：5-02 立项 Vite + TS + Zustand + React 18 实装版 → 5-26 推翻整体废弃。期间约 1 个月间隔 + 5 端 v0.8 共同启动里 teacher_web 这一端**作废**。失败原因（itsuki 主观）：1 个月后看不出价值 = 「垃圾」。
- **模式 2 假设崩**：itsuki 假设 `v1/` 就是 Ryō → 实际并存两套 → 真因 = 5-02 立项时没归档老 Ryō 老 demo
- **模式 6 取舍**：废 Vite 实装版 + 留 `api/client.ts`（后端对接代码）+ 留 `_legacy/*.jsx`（Ryō JSX 源）+ 归档其他 Vite 文件
- **主体性 ⭐⭐⭐⭐⭐**：itsuki 自己推翻自己 5-02 立项的决定 — 不是 CC 推荐废弃，是 itsuki 看了直接拍板
- **学术延伸性**：
  - 「Sunk cost fallacy」反例 — itsuki 不为「已经做了 1 个月的工作」感情用事
  - 用户体验驱动技术决策（一打开不是预期 = 立刻废弃，不为「技术先进性」让步）

#AC候选 #AC強候補 #推翻 #失败 #方向反转 #技术判断

---

## 21:25 [设计决策+取舍] CC 调查归档范围 — 留 client.ts + _legacy + vendor

### CC 主动 propose 范围（itsuki 说「看你」全权授权后 CC 自定）

| 动作 | 文件 | 理由 |
|---|---|---|
| 归档 Vite 实装版 | `App.tsx` / `main.tsx` / `pages/` / `components/Shell.tsx` / `store/` / `index.html`（Vite 根入口） | 5-02 起做的 React + TypeScript 实装，已废 |
| 归档 Vite 构建配置 | `package.json` / `package-lock.json` / `vite.config.ts` / `tailwind.config.js` / `postcss.config.js` / `tsconfig*` | Ryō standalone 不需要 Vite 编译 |
| **保留** | `v1/src/api/client.ts` | 后端对接代码（6 大模块：auth/applications/announcements/teachers/students/rollcall）— 未来 Ryō 接真后端复用 |
| **保留** | `v1/src/index.html`（7774 行 standalone） | Ryō prototype 主体（4-21 产出） |
| **保留** | `v1/src/_legacy/*.jsx` 14 个文件 | Ryō JSX 组件源（误导命名 — 实际不是 legacy 而是主源） |
| **保留** | `v1/src/vendor/` | React 18 + Babel 本地副本（standalone HTML 用，浏览器端编译 JSX） |
| **保留** | `v1/src/_assets/` + `assets/` + `index.css` | 字体 + 图标 + 极简 CSS |
| 物理删除 | `node_modules/`（81 MB） + `dist/` | Vite 依赖 + Vite build 产物，gitignore 没污染 repo 但占磁盘 |

### CC 失误

CC 第一时间假设 `round2/*.jsx` 目录存在（基于 `DESIGN_BRIEF.md` 描述），实际 `find` 全项目找不到 — `round2/*.jsx` 已经全部塌缩进 `v1/src/index.html` 7774 行 standalone 里。同时 14 个 JSX 源在 `_legacy/`（命名误导）。

CC 主动停下来调查 + 调整方案，没直接归档。

### itsuki 原话

> "看你"（协作授权颗粒度）
> "之前的垃圾 web 不要再污染我的项目文件了，归档"

### AC 价值 ⭐⭐⭐⭐ 模式 6 + 模式 2

- **模式 6 取舍 5 条**：归档 vs 保留 vs 物理删 — 每条都给理由
- **模式 2 CC 假设崩**：CC 假设 round2/ 存在 → 调查 → 真相（塌缩到 standalone + JSX 在 _legacy/）→ 调整方案
- **协作授权颗粒度** — itsuki「看你」= 信任 CC 工程层决策（哪些归档 / 哪些保留），但保留对设计层决策（A/B/C/D 范围）的拍板权
- **主体性 ⭐⭐⭐⭐**：3 次明确拍板（推 Vite / 用 B / 看你）+ 1 次工程洁癖（垃圾不要污染）

#AC候选 #设计决策 #技术判断 #取舍

---

## 21:45 [推翻] frontend-design skill polish 试做 + 整体回滚

### 背景

itsuki 拍板「用 B」（Ryō prototype）后说：「用 web skill 跑，看能给出什么改动建议」+ 「试一下，全改完后我看看效果」。

CC 跑 frontend-design skill，分析 Ryō 现状给出方向：

**诊断** — Ryō 是「合格但保守」的现代 SaaS 风（深蓝 + Noto Sans JP + 浅灰白 + 极薄阴影）— 不算 AI slop 但远没到「让人记住」。整体太「日式 SaaS 工业品」（像 freee / SmartHR），跟「Tomoshibi 灯火」叙事的人情温度对不上。

**Polish 方向**：Quiet Luxury Japanese Editorial（克制日式编辑感）

5 条改动 + 3 阶段：

| 改动 | 改的是 | 阶段 |
|---|---|---|
| 字体加 display = Shippori Mincho B1（日式明朝） | RYO 新 token + Google Fonts CDN 引入 | 1 |
| 纸面色 `#f4f5f7` → `#f3efe8`（米白和纸） | body 背景 + RYO.paper | 1 |
| 加 vermillion `#c43d2d`（朱赤） | RYO 新 sharp accent token | 1 |
| 升级 shadow 0.04 → 0.07 | RYO.shadow1/2/Modal | 1 |
| 加 SVG 噪点 + 朱+钴双角微渐变 | body::before 伪元素 | 2 |
| 主按钮「点呼を開始」换朱色 | inline style | 3 |
| logo「Tomoshibi」用 display 字体（2 处） | inline style | 3 |
| Stat 数字 mono → display + 38px + tabular-nums | inline style | 3 |

### CC 失败 + itsuki 一键回滚

itsuki 看完浏览器效果（localhost:8787）→ **整体不喜欢** → 一句话「回滚」。

CC 跑 `git checkout 03_dev/teacher_web/v1/src/index.html` → 全部退回 4-21 原 Ryō（冷灰白 + Cobalt + Noto Sans JP）→ 同步删 README + DESIGN_BRIEF 里写的「polish 完成」段，改成「试过被回滚」事实记录。

### CC 安全设计 — 提前承诺「能回滚」

CC polish 前主动给 itsuki 承诺：「全部改动在 index.html 一个文件里，git checkout 一行退回」。这个承诺让 itsuki 敢试。

### itsuki 原话

> "用 web skill 跑，看能给出什么改动建议"
> "试一下，全改完后我看看效果"
> "所以，万一就算改的我不喜欢，我们也可以回滚之前的设计对吧？"
> "回滚"

### AC 价值 ⭐⭐⭐⭐⭐ 模式 5 + 模式 6 + 协作判断力

- **模式 5 元认知**：itsuki 看完不喜欢直接拒绝 — 不被 AI 设计建议 / 「frontend-design skill 专业意见」绑架。审美主观性 = 工程不可量化部分 = 主人拍板。
- **模式 6 取舍**：试 polish vs 不试 — 试了。喜欢 vs 不喜欢 — 不喜欢。改 vs 回滚 — 回滚。每步都拍板。
- **协作纠错 ⭐**：itsuki 拒绝 AI 建议 = 直接证据「不是被 AI 牵着走」（合格者报告里这是金贵素材）
- **CC 工程设计**：提前承诺「可回滚」 → 降低 itsuki 尝试成本 → 协作敢于试验
- **学术延伸性**：
  - 设计审美的不可量化性 + 工程方法（all-in-one-file → 一行回滚）
  - 协作信任设计 — CC 主动给安全网降低用户尝试门槛
  - 「failed exploration ≠ failed work」— 试错过程本身有价值

#AC候选 #AC強候補 #推翻 #分歧 #设计决策 #协作纠错

---

## 22:00 [问题→解决] 修破工具 — demo_server.py 引用 / node_modules 清理

### 背景

itsuki 说「之前的垃圾不要再污染我的项目文件了，归档」+ 「下次如何打开这个网页看效果」。

CC 调查发现两个脚本引用不存在的 `demo_server.py`：

1. `v1/开发模式跑.command` 第 24 行 — `python3 demo_server.py`
2. `v1/tomoshibi` CLI 的 `cmd_start` — `exec python3 demo_server.py`

历史上 `demo_server.py` 提供：
- 静态文件服务
- POST `/checkin?no=XX`（iPhone 快捷指令 → 服务器 → 浏览器实时点呼）
- GET `/events/latest`（1 秒 poll）
- GET `/api/server-info`

但 `find` 全项目找不到 `demo_server.py` — 这文件从来没在 git 仓库里。脚本一直是死链状态。

### CC 修复

两个脚本都改成 `python3 -m http.server 8787 -d src`（Python 内建静态服务器）。

副作用 — NFC iPhone 快捷指令实时点呼 demo 功能失效。要恢复需要写 `demo_server.py`（独立任务，记 TODO）。

物理删除：
- `v1/node_modules/`（81 MB Vite 依赖）
- `v1/dist/`（Vite build 产物）

两者都被 `.gitignore` 忽略 — 不污染 git repo，但占磁盘空间。

### itsuki 原话

> "之前的垃圾 web 不要再污染我的项目文件了，归档"
> "并且文件记得整理下"
> "然后告诉我一下文件结构，并且我下次如何打开这个网页看效果"

### AC 价值 ⭐⭐⭐ 模式 1 + 工程洁癖

- **模式 1 派生痛点 → 工程修复**：CC 发现脚本死链 → 修脚本 + 标残留 TODO
- **工程洁癖**：itsuki 不容忍「垃圾在项目里」 — 强制 CC 物理清理（不只是 gitignore）
- **学术延伸性**：
  - 脚本「死链文档」反模式 — README 说有 demo_server.py 但实际从来没在 repo
  - 注释跟实际代码漂移（脚本注释停留在 round3 阶段）

#AC候选 #问题解决 #工程方法论

---

## 22:10 [文档同步] 改 README + DESIGN_BRIEF + 写「怎么打开」指引

### 改了什么

1. `v1/README.md` 全文重写 — 加「怎么打开看效果」段（双击启动 + CLI 用法）+ 技术栈段（standalone HTML + React via Babel CDN）+ polish 试做记录
2. `teacher_web/DESIGN_BRIEF.md` — 删 `round2/*.jsx` 段（实际不存在，已塌缩）+ 加 `_legacy/` 实际位置 + 加 2026-05-26 polish 试过被回滚记录
3. itsuki 回滚后 — 把 README 跟 DESIGN_BRIEF 里的「polish 完成」段改成「试过被回滚」事实记录（保留历史诚实性，不假装从来没试过）

### 设计原则 — 诚实记录历史

CC 没把 polish 痕迹完全抹掉。原因：
- git log 还能查到（不可能真隐藏）
- 文档里写「polish 试过被回滚」= 给未来读者 / itsuki 自己 / AC 教授 看到完整决策脉络
- AC 价值：失败素材 > 50% 占比（合格者报告统计）— 试 + 拒绝 比 没试 更有叙事力

### AC 价值 ⭐⭐⭐ 工程方法论 + 叙事策略

- **模式 5 设计哲学**：文档诚实记录 = 历史可追溯（不抹失败）
- **学术延伸性**：「version control as memory」— git + 文档双层记忆，文档讲故事 + git 存证据

#AC候选 #方法论 #设计决策

---

## 工程动作汇总（这次会话改了什么）

### 改了

| 文件 | 改动 |
|---|---|
| `v1/src/index.html` | polish 试做 → itsuki 拒绝 → `git checkout` 退回 |
| `v1/开发模式跑.command` | 改用 `python3 -m http.server 8787 -d src`（原 demo_server.py 死链） |
| `v1/tomoshibi` CLI | `cmd_start` 改用 `python3 -m http.server`（同上） |
| `v1/README.md` | 重写 — 加「怎么打开」+ 技术栈 + polish 试过被回滚记录 |
| `teacher_web/DESIGN_BRIEF.md` | 删 round2/ 段 + 加 _legacy/ 实际位置 + 加 polish 试过被回滚 |

### 归档（`git mv` → `99_archive/2026-05-26_teacher_web_vite实装作废/`）

13 个文件：`App.tsx` / `main.tsx` / `Shell.tsx` / `pages/`（5 个）/ `store/` / `package.json` / `package-lock.json` / `vite.config.ts` / `tailwind.config.js` / `postcss.config.js` / `tsconfig.json` / `tsconfig.tsbuildinfo` / `vite_root_index.html`（原 Vite 入口）

### 物理删（`.gitignore` 忽略）

- `v1/node_modules/`（81 MB）
- `v1/dist/`

### 保留

- `v1/src/index.html`（Ryō standalone）
- `v1/src/_legacy/`（14 个 JSX 源）
- `v1/src/api/client.ts`（后端对接代码）
- `v1/src/vendor/`（React + Babel 本地副本）
- `v1/src/_assets/` / `assets/` / `index.css`
- `v1/build_single_file.py` / `rebuild.command` / `打包单文件.command`（Ryō workflow 工具）

---

## 残（下次跟进）

1. `demo_server.py` 写一份 — 恢复 NFC iPhone 快捷指令实时点呼 demo 功能（GET `/api/server-info` / POST `/checkin?no=XX` / GET `/events/latest`）
2. TODO line 106 `A-039` 条目「需 vite 验证」描述失效 — 改成「Ryō standalone 直接验证」
3. TODO line 883 ✅ S15 / line 1023 Vite 引用 — 已废，要更新
4. `00_admin/系统bug专栏.md` 里 FC-024 / A-039 等 teacher_web 漏洞条目要重新审视 — 部分（如「v1 是 demo 包含明文密码」）依然有效，部分（如「Vite 字段对齐」FC-025/26/27/28）已 N/A 因为 Vite 整体废了
5. WEB_DESIGN_LOG.md 加本次会话条目（5-02→5-26 演化 + polish 试过被回滚 + 当前权威源调整）
6. 设计层面要不要再试 polish — 候选方向（如果未来再起意）：单页改造（B 改成具体一页换风格）/ 字体单独换不动颜色 / 找 itsuki 喜欢的具体参照系（某个 web）

---

## AC 价值评分总览

| 模式 | 命中条数 | 强度 |
|---|---|---|
| 模式 1（问题→解决） | 1（修破脚本 + 物理清理） | ⭐⭐⭐ |
| 模式 2（假设崩→真因） | 2（itsuki 假设 v1=Ryō + CC 假设 round2/ 存在） | ⭐⭐⭐⭐ |
| 模式 3（失败→吸取教训） | 1（Vite 实装版 5-02→5-26 整体废弃） | ⭐⭐⭐⭐⭐ |
| 模式 4（v1→v2 版本演化） | 1（5-02 Vite 实装 → 5-26 回归 Ryō standalone） | ⭐⭐⭐⭐ |
| 模式 5（认知改变） | 2（前端开发流程教学 + 文档诚实记录哲学） | ⭐⭐⭐⭐⭐ |
| 模式 6（取舍） | 多（A/B/C/D 范围选项 + polish 5 条改动 vs 回滚 + 归档范围 5 条 + 物理删 vs 留） | ⭐⭐⭐⭐ |

**协作纠错 × 3**：
1. CC 没核对清楚启动了哪套 → itsuki 怒怼「这他妈根本不是我的 web」
2. CC 假设 round2/*.jsx 存在 → 调查发现塌缩 → 调整
3. CC polish 试做 → itsuki 拒绝 → 回滚（最大一次）

**主体性 ⭐⭐⭐⭐⭐**：itsuki 7 次明确拍板：
1. 调 frontend-design skill
2. 怎么看 web（教学需求）
3. Vite 实装版垃圾归档
4. 用 B（Ryō）方向
5. 「看你」工程层授权
6. 试 polish + 看完效果
7. 回滚 + 垃圾不污染项目

**学术延伸性**：
- Sunk cost fallacy 反例（不为 1 个月 Vite 工作感情用事）
- 用户体验驱动 vs 技术先进性（一打开不对 = 立刻废）
- 设计审美主观性 + 可回滚工程方法（all-in-one-file + git checkout）
- 跨技术栈反馈循环长度对比（iOS 5-15s / backend 1-2s / 前端 50-200ms）
- 协作信任设计（CC 提前承诺可回滚降低试验门槛）
- 文档诚实记录 = 历史可追溯（不抹失败）
- AC 面试可挂「跟 AI 协作时的判断力 — 何时采纳何时拒绝」

#DMSD #teacher_web #vite废弃 #polish回滚 #模式3 #模式5 #AC強候補

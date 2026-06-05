# 老师网页 HTML → React + TypeScript + Vite 迁移 · 施工清单

> **状态**：规划完成，未开工（2026-06-05 itsuki 拍板「现在一步到位上 TypeScript」）
> **执行方式**：compact 后新会话照本清单 + 配套 GOAL 提示词执行
> **本文是单源真值**：迁移期间所有决策 / 进度 / 阶段在这里维护

---

## 0. 一句话目标

把老师网页从「单个 29305 行 `index.html` + 浏览器内 Babel 现场编译 React」迁成「React + TypeScript + Vite 的正规模块化工程」，**界面 100% 不变**，部署到服务器。

---

## 1. ⚠️ 铁律（违反 = 重蹈 5-26 覆辙）

1. **界面 100% 冻结** —— 现在的页面布局 / 内联样式 / Ryō 配色，逐页**原样搬运**，一个像素都不改外观。**绝不重新设计界面**。
2. **逐页对比验证** —— 每搬完一页，跟旧 `index.html` 版肉眼对比该页，确认长得一模一样再搬下一页。
3. **不引入新设计体系** —— 样式保持现在的内联 `style={{...}}` + `window.RYO` 配色（迁成 import 的 theme 模块）。**不改 Tailwind**（5-26 失败版用了 Tailwind，是界面变样的元凶之一）。
4. **状态管理用 React 自带** —— 现有 `React.useState` 逻辑不变；跨页共享状态用 React Context。**不引 Zustand 等额外库**（先求迁对，不叠加新东西）。
5. **别拿「itsuki 零基础 / 维护难」当任何论据** —— 见 memory `feedback_no_zero_basis_excuse`。

### 为什么有这些铁律 —— 5-26 失败复盘

2026-05-26 上次 Vite 迁移被 itsuki 一句「这他妈根本不是我的 web」否决归档。**根因不是技术，是产品方向错**：5-02 立项时本该把现有 Ryō 界面接后端，结果**重做了一套全新的 4 标签管理后台界面**，跟 itsuki 满意的座席表+仪表盘完全不同。
- 失败版归档在 `99_archive/2026-05-26_teacher_web_vite实装作废/`（React18 + TypeScript5 + Vite6 + Zustand5 + Tailwind3，13 文件）
- **它的工程配置（package.json / vite.config.ts / tsconfig.json）技术上没问题、可参考；但它的界面代码（App.tsx / pages/*.tsx / Shell.tsx）不可用 —— 界面要用现在 `index.html` 里的**
- 复盘详情：`05_logs/raw/2026-05-26_teacher_web_vite废弃+polish回滚.md`

---

## 2. 技术栈（已定）

| 项 | 选择 | 备注 |
|---|---|---|
| 框架 | React 18 | 现在就在用（浏览器版），换成正式 npm 依赖 |
| 语言 | **TypeScript**（一步到位，itsuki 6-05 拍板）| 全部代码加类型 |
| 构建 | Vite | 替掉浏览器内 Babel 现场编译 |
| 样式 | 内联 `style` + `window.RYO`→theme 模块 | **不用 Tailwind** |
| 状态 | React 自带 useState + Context | **不引 Zustand** |
| 路由 | 沿用现有「一个大 switch 按 view 切页」即可，或轻量 React 路由 | 不强求引重型路由库 |

环境已确认：node v25.5.0 / npm 11.8.0 可用。

---

## 3. 现状清单（要迁的东西）

**起点文件**：`03_dev/teacher_web/v1/src/`
- `index.html` —— **29305 行**，单文件含全部界面 + 逻辑
- `api/client.js` —— **571 行**，后端调用封装（`window.tomoshibiApi`），约 65 处直连后端接口路径
- `index.css` —— 51 行
- `vendor/` —— `react.development.js`（**开发版！未压缩、慢**，正是上线该换掉的）+ `react-dom.development.js` + `babel.min.js`

**16 个主页面组件**（`window.XxxPage`，迁成 `pages/XxxPage.tsx`）：
1. AccountsPage（学生账号管理）
2. ActiveLeavesPage（出寮者一覧）
3. ApplicationsPage（申請）
4. CleaningPage（清掃確認）
5. CommunityPage（コミュニティ管理）
6. DisciplinePage（規律・処分）
7. DisclosureRequestsPage（開示申請）
8. FrontDeskPage（フロント業務）
9. IncidentsPage（事案録入）
10. InfoPage（お知らせ・バス）
11. NotificationsPage（通知）
12. ProxyApplicationPage（代録 — 6-05 刚做）
13. RecordsPage（記録）
14. SearchPage（検索結果）
15. StudyAttendancePage（学習出席）
16. TeachersAdminPage（教員アカウント管理）

**还有**（不在上面 16 个里，也要搬）：登录页（LoginScreen / select-teacher）、外壳/导航（Shell / NAV 数组 + pageLabel 映射 + 路由 switch，约 `index.html` 11353 / 28150 行附近）、各种弹窗 Modal 组件、`window.RYO` 配色板（约 9991-10033 行）。

**构建 / 启动脚本**（迁完要相应改）：
- `启动老师网站.command` —— 现在起后端 + 后端用 `TEACHER_WEB_DIR` 托管 `src/` 到 `/teacher/`。迁完要改成托管 Vite 构建产物 `dist/`
- `build_single_file.py` / `打包单文件.command` / `rebuild.command` / `tomoshibi` CLI —— 单文件时代的打包脚本，迁完多数废弃，归档

---

## 4. 分阶段计划

> 每阶段做完都要能验证，不一次性大爆炸。

### 阶段 1 — 搭 Vite + TypeScript 骨架
- `package.json`（React + TypeScript + Vite + @vitejs/plugin-react，参考归档版但去掉 Tailwind/Zustand）
- `vite.config.ts` / `tsconfig.json` / 入口 `index.html`（精简壳）/ `src/main.tsx`
- `npm install` 通 + `npm run dev` 能起一个空白页 + `npm run build` 能产出 `dist/`
- **验证**：构建链跑通，浏览器能打开开发服务器

### 阶段 2 — 抽公共层
- `window.RYO` → `src/theme.ts`（export 配色 token + 类型）
- `client.js` → `src/api/client.ts`（ES 模块 export + 加返回类型；后端接口的请求/响应类型定义到 `src/api/types.ts`）
- 公共组件（输入框 / 弹窗壳 / 徽章等反复用的）抽到 `src/components/`
- **验证**：`tsc` 类型检查通过

### 阶段 3 — 逐页搬运（16 页 + 登录 + 弹窗）
- 每个 `window.XxxPage` → `src/pages/XxxPage.tsx`：界面 JSX + 内联 style **原样搬**，把 `window.tomoshibiApi`→`import api`、`window.RYO`→`import theme`，给 props / state 加类型
- **每搬一页：跟旧版肉眼对比该页界面一致**
- **验证**：逐页对比无差异 + 该页 tsc 通过

### 阶段 4 — 组装外壳 + 路由 + 全局状态
- Shell（导航栏 NAV + 顶栏 + 页面切换 switch）搬成 `src/Shell.tsx`
- 全局状态（登录态 / authToken / 当前角色等 `window.*`）→ React Context
- **验证**：登录 → 各页切换 → 全流程跑通

### 阶段 5 — 切换托管 + 全面回归
- `vite build` → `dist/`；改 `启动老师网站.command` 让后端托管 `dist/`
- **逐页跟旧 `index.html` 版对比，确认 16 页 + 登录全部长得一模一样**
- 功能回归：登录 / 代録 / 出寮者一覧 / 审批 / 点呼 等核心流程真点一遍
- 旧 `index.html` + 单文件打包脚本归档（不删，留对比）
- **验证**：界面 100% 一致 + 功能无回归 + `npm run build` 0 错误 + `tsc` 0 错误

---

## 5. 完成的总验证标准

- [ ] `npm run build` 成功产出 `dist/`，0 报错
- [ ] `tsc`（TypeScript 类型检查）0 错误
- [ ] 16 个主页面 + 登录页逐页跟旧版**界面一致**（肉眼对比，这是最硬的标准）
- [ ] 核心功能跑通：登录 / 代録出寮届 / 出寮者一覧 / 申請审批 / 点呼板 / 学習出席
- [ ] 起后端托管 `dist/`，浏览器访问正常
- [ ] 后端 295 测试仍全过（迁移不应碰后端，若碰了要确认）

---

## 6. 不碰的（边界）

- **后端**（`03_dev/backend/`）—— 迁移只动前端，后端接口不变。客户端调用对齐现有接口。
- **iOS / Android** —— 跟老师网页迁移无关，不碰。
- **specs（`01_specs/`）** —— 冻结。
- **后端测试** —— 不应受影响。

---

## 7. 顺带的独立任务（跟迁移并行、互不阻塞）

**邮件服务换 Resend**（2026-06-05 itsuki 拍板）：
- 现在后端 `03_dev/backend/v1/app/services/email.py` 用 SendGrid（60 天后收费）。换成 **Resend**（永久免费 3000 封/月、可绑自有域名）。
- **待 itsuki 操作**：去 `resend.com` 注册 → 拿密钥（API key）→ 绑发信域名。
- CC 可先改 `email.py` 成 Resend 版（没密钥时跟现在一样 dev 模式只记日志不真发），itsuki 拿到密钥填配置就能真发。
- 这是后端小改 + 带 pytest，跟前端迁移无关，可单独做。

---

## 8. 进度记录（执行时在这里更新）

- 2026-06-05：规划完成，未开工。等 compact + GOAL 提示词触发执行。

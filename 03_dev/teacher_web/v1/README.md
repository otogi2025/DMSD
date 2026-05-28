# 03_dev/teacher_web/v1/

**老师 Web v1.0 — Ryō standalone prototype + 2026-05-26 polish**

## 怎么打开看效果（下次想看就这么做）

**方式 A — 双击启动（推荐）**：Finder 找到项目根 `~/dev/DMSD/启动老师网站.command` 双击 → 同时起后端（8000 端口）+ 前端（8787 端口）+ 自动开浏览器到 `http://localhost:8787/`

> 2026-05-28 起改用这个「全套」脚本。原 `v1/开发模式跑.command` 只起前端、不起后端，已归档到 `99_archive/2026-05-28_开发模式跑_被启动全套脚本替代/`。原因：5-27 老师登录改成实名账户（密码存后端数据库），只起前端会卡在登录界面。

**方式 B — 命令行 CLI（仅 NFC 实时点呼演示用）**：
```bash
cd ~/dev/DMSD/03_dev/teacher_web/v1
./tomoshibi start      # 起前端 + demo_server.py（NFC 演示端点）
./tomoshibi stop       # 停止
./tomoshibi status     # 看跑没跑
./tomoshibi help       # 看全部命令
```
> ⚠️ tomoshibi 只起前端、不起后端 — 走正式登录还是用方式 A。

**改了 HTML 想看效果**：浏览器手动刷新（Cmd+R）。没有 HMR（热重载，秒刷）— 这是 standalone HTML 项目的限制。

## 技术栈

- **不用 Vite**（2026-05-26 已归档 Vite + TypeScript 实装版到 `99_archive/`）
- **standalone HTML**：`src/index.html` 单文件 7700+ 行，自带所有 CSS / JS / 字体 / 24 学生种子数据
- **React via Babel CDN**：浏览器端编译 JSX — `src/vendor/` 装的是 React 18 + Babel 本地副本
- **JSX 源文件**：`src/_legacy/*.jsx` 14 个组件源（Round 2 + Round 3 设计） — 改完用 `./tomoshibi rebuild` 重新内联到 `index.html`

## 2026-05-26 frontend-design polish — 试过被回滚

当天跑过 `frontend-design` skill 给 Ryō 做了一次「日式编辑感」polish（米白和纸 / 朱色 sharp accent / 明朝体 display / SVG 噪点纹理 / shadow 加深 / logo + 主按钮 + 仪表盘数字 4 处用新 token）。

itsuki 看完效果后**整体不喜欢**，当场 `git checkout 03_dev/teacher_web/v1/src/index.html` 全部退回。

完整 polish 内容跟未来如果再想试都看 commit 历史 + 5-26 raw log。

## 当前状态（UI ~90% / 真接口 0%）

- ✅ **设计权威**：`src/index.html` + `src/components/_legacy/*.jsx`（14 个 jsx 设计即代码）
- ✅ **16 个 page / modal 已 UI 实装**（不只 5 个 Round 2）：Login / SelectTeacher / Shell / RollCallLanding / LiveRollCall / OverrideModal / ApplicationsPage + OutstayDetailModal / DisciplinePage / RecordsPage / SearchPage / NotificationsPage / CleaningPage / InfoPage（含 EventCalendar / BusSchedule） / CommunityPage / FrontDeskPage / AccountsPage
- ✅ **late 黄色 + 迟到阈值已加**（5-26 之前别会话 — `theme.jsx` `late: '#b8871f'` + `LATE_THRESHOLD_SEC = 180`）
- ✅ **FC-024 明文密码已删**（5-26 commit `b0bed26`）— LoginScreen 改 fetch `${API_BASE}/sessions/teacher` 真后端认证
- ✅ **`src/api/client.ts` 保留**（416 行，已定义 26 个 endpoint 接口 — 未来 Ryō 接真后端时复用）
- ⏳ **3 个 SkeletonTab 占位未补**：applications.jsx 内的 帰国 / 帰省 / タクシー（仿 OutstayList 模式补 List + Detail + 承認）
- ⏳ **真接口对接全部待做**（除 Login）：16 个 page 仍用 `window.ROSTER` / `window.OUTSTAY_APPS` 等假数据；详细路线见 `../DESIGN_BRIEF.md §6`
- ⚠️ **demo_server.py 不存在**：原本支持 iPhone 快捷指令 → 服务器 → 浏览器实时点呼。当前 `./tomoshibi start` 跑 `python3 -m http.server` 只做静态，NFC 实时点呼 demo 功能暂时失效。itsuki TODO §🛠️ §L 第 1 条已列为待办

## 已知问题

详见 `00_admin/系统bug专栏.md §🤖 Codex 段`：

- [FC-024] 🔴 ✅ **已修**（5-26 commit `b0bed26`）— 删 `window.SHARED_PASSWORD = '12345678'` + LoginScreen 改 backend 真认证
- [FC-025] 🟡 ✅ **N/A**（itsuki 5-26 TODO §🛠️ §L 拍板 — Vite 整体废弃；client.ts 没归档 → Task 真接口对接时重新审视）
- [FC-026] 🟡 ✅ N/A（同上）
- [FC-027] 🟡 ✅ N/A（同上 + backend 端 `get_current_student` vs `get_current_teacher` 权限契约待 Task 真接口对接时一起补）
- [FC-028] 🟡 ✅ N/A（同上 — Web 侧 `pages/Teachers.tsx` 已归档；但 backend `routers/teachers.py:28` 角色清单仍要跟未来 Ryō 邀请码 UI 对齐）

## 历史

- 2026-04-21 — Claude Design Round 2 产出 Ryō prototype（涼 + Cobalt + Noto Sans JP）
- 2026-05-02 — Vite + TypeScript 实装版立项（5-端 v0.8 启动）
- 2026-05-26 — Vite 实装版废弃归档，回到 Ryō standalone 主线 + frontend-design polish 上线

## 设计权威

- 共用规则：`02_design/system_features.md`
- Web 専属设计：`../WEB_DESIGN_LOG.md`
- API 字段对齐：`01_specs/rollcall/FIELD_REGISTRY.md` + `backend/v1/app/schemas.py`

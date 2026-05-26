# 03_dev/teacher_web/v1/

**老师 Web v1.0 — Ryō standalone prototype + 2026-05-26 polish**

## 怎么打开看效果（下次想看就这么做）

**方式 A — 双击启动**：Finder 找到 `v1/开发模式跑.command` 双击 → 自动起 Python 服务器（8787 端口）+ 自动开浏览器到 `http://localhost:8787/`

**方式 B — 命令行 CLI**：
```bash
cd ~/dev/DMSD/03_dev/teacher_web/v1
./tomoshibi start      # 启动
./tomoshibi stop       # 停止
./tomoshibi status     # 看跑没跑
./tomoshibi help       # 看全部命令
```

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

## 当前状态

- ✅ **设计权威**：`src/index.html` + `src/_legacy/*.jsx`（设计即代码）
- ✅ **5 个 Round 2 页面已实装**：Login / RollCall Landing / Live Seat Grid / Override Modal / Shell
- ✅ **`src/api/client.ts` 保留**（后端真接口对接代码 — 未来 Ryō 接真后端时复用）
- ⏳ **Tier 1 剩 7 页未做**：外泊申请 / 归国 / 扣分排名 / 签到历史 / 搜索 / 健康上报 / 请假流程
- ⏳ **Tier 2 skeleton 15 项未做**：清扫审査 / 帰県申請 / タクシー予約 / ...
- ⚠️ **demo_server.py 不存在**：原本支持 iPhone 快捷指令 → 服务器 → 浏览器实时点呼。当前用 Python 内建 http.server 只做静态，NFC 实时点呼 demo 功能暂时失效

## 已知问题

详见 `00_admin/系统bug专栏.md §🤖 Codex 段`：
- [FC-024] 🔴 `src/index.html` 仍有明文密码 `12345678`（v1.0 上线前必删）
- [FC-025] 🟡 `StayLocation` 字段形状跟后端不一致
- [FC-026] 🟡 `StudyAbsenceRequestOut` 缺 `period` 字段
- [FC-027] 🟡 老师公告 client 跟后端权限不一致 + 无页面使用

## 历史

- 2026-04-21 — Claude Design Round 2 产出 Ryō prototype（涼 + Cobalt + Noto Sans JP）
- 2026-05-02 — Vite + TypeScript 实装版立项（5-端 v0.8 启动）
- 2026-05-26 — Vite 实装版废弃归档，回到 Ryō standalone 主线 + frontend-design polish 上线

## 设计权威

- 共用规则：`02_design/system_features.md`
- Web 専属设计：`../WEB_DESIGN_LOG.md`
- API 字段对齐：`01_specs/rollcall/FIELD_REGISTRY.md` + `backend/v1/app/schemas.py`

# 03_dev/teacher_web/v1/

**老师 Web — React 18 + TypeScript + Vite**（2026-06-05 从 HTML 单文件迁来；界面 100% 冻结、逐页原样搬，吸取 5-26「不是我的 web」失败教训）

## 怎么打开看效果

双击项目根 `~/dev/DMSD/启动老师网站.command` → 自动 build 出 `dist/` + 起后端（8000 端口）托管 dist + 开浏览器到 `http://localhost:8000/teacher/`。

> 后端托管前端 + 接口同源（都在 8000），老师登录是实名账户（密码存后端数据库），所以前端不能单独跑，必须后端一起起。

## 技术栈

- **React 18 + TypeScript + Vite**（Vite = 构建工具，替掉以前浏览器内 Babel 现场编译）
- 样式：内联 `style` + Ryō 配色（`theme.ts`），**不用 Tailwind**
- 状态：React `useState` + Context，**不用 Zustand**
- 入口链：根 `index.html` → `src/main.tsx` → `src/App.tsx`（鉴权 + 路由）→ `src/Shell.tsx`（侧栏 17 菜单）

## 开发命令

```bash
cd ~/dev/DMSD/03_dev/teacher_web/v1
npm run dev      # Vite 开发服务器(5173) + 热重载(HMR)，/api 自动代理到后端 8000
npm run build    # tsc 类型检查 + 打包出 dist/（启动脚本就是跑这个）
npm run preview  # 本地预览 dist
```

## 源码结构（`src/`）

- `main.tsx` / `App.tsx` / `Shell.tsx` —— 挂载 + 鉴权路由 + 外壳侧栏
- `theme.ts`（RYO 配色 + 常量 + `API_BASE="/api/v1"`） / `utils.ts`（JST 日本时间助手）
- `api/client.ts`（60+ 接口方法） + `api/types.ts`（对齐后端 `schemas.py`）
- `components/` —— 26 个 `.tsx`（22 页 + 3 弹窗 OverrideModal/OutstayDetailModal/StudentProfileModal + `shared.tsx`）
- `_assets/`（fonts.css 引用的字体） + `assets/`（图标） + `fonts.css` + `styles.css`
- 配置：`vite.config.ts`（`base:"./"` + proxy /api→8000 + resolve.extensions .ts 优先） + `tsconfig.json` + `package.json`
- 构建产物 `dist/` 已 gitignore（不提交，启动脚本现 build）

## 旧版（HTML 单文件）已归档

2026-06-05 前是「29629 行 `index.html` + 浏览器内 Babel 编译 React + `react.development.js` 开发版」。已整组归档到 `99_archive/2026-06-05_teacher_web_html单文件版归档/`（含旧 index.html / client.js / vendor / 打包脚本 / `Tomoshibi_v3_single.html` 33MB 自包含版，双击可看旧版界面做对比）。迁移完整记录见 `../WEB_DESIGN_LOG.md` §16 + `../Vite迁移_施工清单.md`。

## 当前状态

- UI 迁移完成：17 页 chrome 实测全渲染 + 27 接口全 200 + 真数据通；后端 311 测试全过
- **仅剩 itsuki 肉眼签收 + push**
- 已知遗留：`RollCallLanding`（点呼默认页）统计卡 / 趋势图是从旧版原样照搬的硬编码 demo 数据（带「DEMO」标记），接不接真后端待 itsuki 决策

## 设计权威

- 共用规则：`02_design/system_features.md`
- Web 専属设计：`../WEB_DESIGN_LOG.md`（§16 = Vite 迁移记录）
- API 字段对齐：`01_specs/rollcall/FIELD_REGISTRY.md` + `backend/v1/app/schemas.py`

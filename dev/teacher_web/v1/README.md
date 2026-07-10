# dev/teacher_web/v1/

**老师 Web — React 18 + TypeScript + Vite**（由 HTML 单文件版迁移而来，迁移时界面 100% 冻结、逐页原样搬）

## 怎么打开看效果

```bash
cd dev/teacher_web/v1
npm ci          # 安装依赖（按 package-lock.json 精确装）
npm run build   # 产出 dist/（tsc 类型检查 + vite 打包）
```

然后起后端，让后端用 `TEACHER_WEB_DIR=dist` 把 `dist/` 托管到 `/teacher/` 路径（8000 端口），浏览器打开 `http://localhost:8000/teacher/`。

> 后端托管前端 + 接口同源（都在 8000），老师登录是实名账户（密码存后端数据库），所以前端不能单独跑，必须后端一起起。

## 技术栈

- **React 18 + TypeScript + Vite**（Vite = 构建工具，替掉以前浏览器内 Babel 现场编译）
- 样式：内联 `style` + Ryō 配色（`theme.ts`），**不用 Tailwind**
- 状态：React `useState` + Context，**不用 Zustand**
- 入口链：根 `index.html` → `src/main.tsx` → `src/App.tsx`（鉴权 + 路由）→ `src/Shell.tsx`（侧栏菜单，分组定义见其中 `NAV_GROUPS`）

## 开发命令

```bash
cd dev/teacher_web/v1
npm run dev      # Vite 开发服务器(5173) + 热重载(HMR)，/api 自动代理到后端 8000
npm run build    # tsc 类型检查 + 打包出 dist/
npm run preview  # 本地预览 dist
```

## 源码结构（`src/`）

- `main.tsx` / `App.tsx` / `Shell.tsx` —— 挂载 + 鉴权路由 + 外壳侧栏
- `theme.ts`（RYO 配色 + 常量 + `API_BASE="/api/v1"`） / `utils.ts`（JST 日本时间助手）
- `api/client.ts`（60+ 接口方法） + `api/types.ts`（对齐后端 `schemas.py`）
- `components/` —— 页面组件 + 弹窗组件 + `shared.tsx` 共用件（清单以目录本身为准；页面与侧栏菜单的对应关系见 `Shell.tsx` 路由）
- `_assets/`（fonts.css 引用的字体） + `assets/`（图标） + `fonts.css` + `styles.css`
- 配置：`vite.config.ts`（`base:"./"` + proxy /api→8000 + resolve.extensions .ts 优先） + `tsconfig.json` + `package.json`
- 构建产物 `dist/` 已 gitignore（不提交，`npm run build` 现 build）

## 旧版（HTML 单文件）已归档

迁移前是「29629 行 `index.html` + 浏览器内 Babel 编译 React + `react.development.js` 开发版」。旧版已整组归档，不在公开仓库（含旧 index.html / client.js / vendor / 打包脚本 / 自包含单文件版，可看旧版界面做对比）。迁移完整记录见 `../WEB_DESIGN_LOG.md` §16 + `../Vite迁移_施工清单.md`。

## 当前状态

- Vite 迁移已完成并入 main（迁移后仍在持续迭代 — 各页现状以 `src/` 目录 + `../WEB_DESIGN_LOG.md` 为真值）
- 已知遗留：`RollCallLanding`（点呼默认页）统计卡 / 趋势图是从旧版原样照搬的硬编码 demo 数据（带「DEMO」标记），接不接真后端待决策

## 设计权威

- 共用规则：`design/system_features.md`
- Web 専属设计：`../WEB_DESIGN_LOG.md`（§16 = Vite 迁移记录）
- API 字段对齐：`specs/rollcall/FIELD_REGISTRY.md` + `backend/v1/app/schemas.py`

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

// 版本号单源真值 = 仓库根 CHANGELOG.md 顶部第一条 `## [vX.Y.Z]`（见 admin/文档同步点清单.md）。
// 构建 / 启动 dev server 时读一次，注入成全局常量 __APP_VERSION__，前端 theme.ts 直接用。
// 这样网页版本号永远跟着 CHANGELOG 走 —— 发版只要重新构建网页就自动同步，
// 杜绝过去「发 patch 时忘改 theme.ts 里写死的版本号」造成的漂移（联动靠机制，不靠记性）。
function readAppVersion(): string {
  try {
    // vite.config 在 dev/teacher_web/v1/ → 仓库根需回退三层
    const here = dirname(fileURLToPath(import.meta.url));
    const changelog = readFileSync(
      resolve(here, "../../../CHANGELOG.md"),
      "utf-8",
    );
    const m = changelog.match(/^##\s*\[v?([\d.]+)\]/m);
    return m ? `v${m[1]}` : "v0.0.0";
  } catch {
    // 读不到 CHANGELOG（路径变动 / 文件缺失）时不让构建挂掉，退回占位版本号
    return "v0.0.0";
  }
}

// 老师网站 Vite 配置
// - base "./": 构建产物用相对路径，后端把 dist 托管到 /teacher/ 子路径也能正确加载资源
// - server.proxy: 开发时（vite dev 跑 5173）把 /api 请求转发到后端 8000，绕开跨域
// - define.__APP_VERSION__: 见上方 readAppVersion，版本号构建时从 CHANGELOG 注入
export default defineConfig({
  base: "./",
  define: {
    __APP_VERSION__: JSON.stringify(readAppVersion()),
  },
  plugins: [react()],
  // src/api/ 下旧 client.js（旧网页 standalone 用，IIFE 挂 window 无 export）和新 client.ts 同名。
  // 让 .ts 优先解析，import "./api/client" 命中 client.ts（有 export api），不是 client.js。
  // 旧 client.js 阶段5 归档旧网页时一起清掉。
  resolve: {
    extensions: [".ts", ".tsx", ".mjs", ".js", ".jsx", ".json"],
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});

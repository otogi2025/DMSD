import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// 老师网站 Vite 配置
// - base "./": 构建产物用相对路径，后端把 dist 托管到 /teacher/ 子路径也能正确加载资源
// - server.proxy: 开发时（vite dev 跑 5173）把 /api 请求转发到后端 8000，绕开跨域
export default defineConfig({
  base: "./",
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

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// 老师网站 Vite 配置
// - base "./": 构建产物用相对路径，后端把 dist 托管到 /teacher/ 子路径也能正确加载资源
// - server.proxy: 开发时（vite dev 跑 5173）把 /api 请求转发到后端 8000，绕开跨域
export default defineConfig({
  base: "./",
  plugins: [react()],
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

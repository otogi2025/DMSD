/// <reference types="vite/client" />

// 构建时由 vite.config.ts 的 define 注入（值 = 仓库根 CHANGELOG.md 顶部版本号）。
declare const __APP_VERSION__: string;

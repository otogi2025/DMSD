# teacher_web/demo/ 归档

**归档日期**：2026-05-21（A-032 修复）

## 背景

teacher_web/demo/ 是 2026-04-22 demo 4-28 sprint 时建的 14 文件 jsx + 单页 HTML SPA，含：
- `demo_server.py` — FastAPI 后端 demo（POST `/checkin?no=XX`）
- `build_single_file.py` — 打包 SPA 成单 HTML 脚本
- `开发模式跑.command` / `打包单文件.command` — itsuki 双击启动
- `NFC_DEMO_SETUP.md` — iPhone 快捷指令配置 + 局域网 IP + 演示台本

2026-05-02 起 teacher_web `v1/` 已用 TypeScript + Vite + Zustand 重做，接真 backend。 demo/ 不再使用但留在原位 17 天，5-21 audit findings A-032 拍归档。

## 归档理由

- 真生产代码已在 `03_dev/teacher_web/v1/`
- demo/ 残留会随 v1/ 漂移成废弃代码
- public repo 里同目录有「真版 + demo 版」容易误读

## 复活方法

如果需要重做 4-28 那种快速 demo（iPhone NFC + 单页 HTML），整目录 `git mv` 回 `03_dev/teacher_web/demo/`。

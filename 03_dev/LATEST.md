# 最新 HTML プロトタイプ 位置速查

> **2026-04-23 建立** — 「最新の HTML はどこ？」の single source of truth。HTML プロトタイプを更新したら必ず本文を更新する。

---

## 老师 Web（教员向け iPad）

> **2026-04-29 大整理**：`teacher_web/round3/` → `teacher_web/demo/`（demo 锁定不动）+ `teacher_web/v1/`（未开始）。

| 項 | パス |
|---|---|
| ⭐ **demo 起動 CLI**（editing + live reload + 自動 IP 検出）| `cd 03_dev/teacher_web/demo && ./tomoshibi` |
| ⭐ **単一ファイル**（双击 Safari、32MB、off-line、UI 確認用）| `03_dev/teacher_web/demo/Tomoshibi_v3_single.html` |
| ⭐ **編集版**（`.jsx` 編集可）| `03_dev/teacher_web/demo/src/index.html` |
| ログイン情報 | 管理員パスワード **`12345678`**（`theme.jsx` 内 `window.SHARED_PASSWORD`）|

> **demo demo 用法注意**：双击 HTML 只看 UI（无 NFC 集成）；要给老师演示 NFC 实时签到，**必须用 `./tomoshibi`** 启动 demo_server.py（提供 `/api/server-info` 接口让前端自动检测 LAN IP）。

| Version | Round 3（2026-04-22 交付 + 2026-04-23 継続改動 + 2026-04-24 demo prep + 2026-04-29 demo 锁定）|
| Design System | Ryō（涼）— Paper + Cobalt + Noto Sans JP |
| 設計 LOG | `03_dev/teacher_web/WEB_DESIGN_LOG.md` |
| v1.0 開発 | `03_dev/teacher_web/v1/`（未開始、見 `v1/README.md`）|

**旧 Round 1 / Round 2 関連物**（handoff / index.html / round2 jsx / round3_handoff 入力素材）は **2026-04-29 大整理で `99_archive/2026-04-29_pre_v1.0_cleanup/` に移動済**（歴史保留、本ファイルからは指し示さない）。

**2026-04-29 晚 demo / v1 分离**: 原 `teacher_web/round3/` → `teacher_web/demo/`，原 `student_ios/designs/` → `student_ios/demo/`，新增 `*/v1/` 占位目录（v1.0 開発位置、未着手）。理由：itsuki 拍板「demo 锁定不动，正式版从 demo 复制需要的部分」。详见 `00_admin/文件结构指南.md §6`。

### ⚠️ ビルド順序（jsx 改動時）

1. `.jsx` 編集（`demo/src/components/`）
2. `bash demo/rebuild.command` → jsx を `src/index.html` に内联
3. `python3 demo/build_single_file.py` → `Tomoshibi_v3_single.html` を再生成
4. ダブルクリック で確認

**rebuild → repack の順序を守らないと、single HTML は古い内联結果になる。** 2026-04-23 22:00 のハマり例: 男寮教員名 改動後 rebuild せず repack → single に 田中 健一 残留。

> **2026-04-29 注**：demo 已锁定，原則上不再改 .jsx。如果要在 v1.0 改设计 → 把 `demo/src/` 复制到 `v1/src/` 起点，在 v1/ 内迭代。

---

## 学生 iOS（Swift 実装 の 視覚 source of truth）

> **2026-04-29 大整理**：`student_ios/designs/` → `student_ios/demo/`（demo 锁定不动）+ `student_ios/v1/`（独立 repo 链接）。

| 項 | パス |
|---|---|
| ⭐ **最新 HTML プロトタイプ**（Phase B v2、双击 Safari 看 UI）| `03_dev/student_ios/demo/Tomoshibi_iOS_PhaseB_v2.html` |
| JSX 解包源（Swift agent が参照）| `03_dev/student_ios/demo/phaseB_src/` |
| QA 記録 | `03_dev/student_ios/demo/QA_Round1_PhaseB.md` |
| Version | Phase B v2（2026-04-22 完成、2026-04-29 demo 锁定）|
| 設計 LOG | `03_dev/student_ios/IOS_DESIGN_LOG.md` |
| Swift v1.0 実装（別 repo）| `~/dev/TomoshibiiOSApp/`（详见 `student_ios/v1/README.md`）|

Swift 実装は **本 HTML を 1:1 pixel-level fidelity で書き起こす**（`~/dev/TomoshibiiOSApp/REMOTE_AGENT_GUIDE.md` §1.1 铁律）。

---

## 更新ルール

1. 新 HTML が出た → 本文の該当行「⭐ 最新」パスを更新 + 日付 + Version
2. 旧 HTML は削除せず、ファイル名はそのまま残す（歴史参照）
3. iOS の HTML を更新したら `bash bin/sync-ios-refs.sh` を走らせて Tomoshibi-iOS/refs/ に同期
4. 本文を更新した commit は `docs(html-latest):` プレフィクスを付ける

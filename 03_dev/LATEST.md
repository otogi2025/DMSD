# 最新 HTML プロトタイプ 位置速查

> **2026-04-23 建立** — 「最新の HTML はどこ？」の single source of truth。HTML プロトタイプを更新したら必ず本文を更新する。

---

## 老师 Web（教员向け iPad）

| 項 | パス |
|---|---|
| ⭐ **ダブルクリック で起動**（単一ファイル 32MB、off-line、全改動込み）| `03_dev/teacher_web/round3/Tomoshibi_v3_single.html` |
| ⭐ **編集版**（`.jsx` 編集可、サーバ起動必要）| `03_dev/teacher_web/round3/src/index.html` |
| ⭐ **サーバ起動 CLI**（editing + live reload）| `cd 03_dev/teacher_web/round3 && ./tomoshibi` |
| ログイン情報 | 管理員パスワード **`12345678`**（`theme.jsx` 内 `window.SHARED_PASSWORD`）|

> **2026-04-23 旧 Claude Design 原始交付 `Tomoshibi_Prototype_v3.html` は削除済**（itsuki の改動未反映で密码 12345678 効かずハマりの元になったため）。`round3/` 下に .html ファイルは `Tomoshibi_v3_single.html` の 1 本のみ。
| Version | Round 3（2026-04-22 交付 + 2026-04-23 継続改動）|
| Design System | Ryō（涼）— Paper + Cobalt + Noto Sans JP |
| 設計 LOG | `03_dev/teacher_web/WEB_DESIGN_LOG.md` |

**旧 Round 2** は `03_dev/teacher_web/round2/` + ルート `index.html`（歴史保留、改動禁止）。

### ⚠️ ビルド順序（jsx 改動時）

1. `.jsx` 編集（`src/components/`）
2. `bash round3/rebuild.command` → jsx を `src/index.html` に内联
3. `python3 round3/build_single_file.py` → `Tomoshibi_v3_single.html` を再生成
4. ダブルクリック で確認

**rebuild → repack の順序を守らないと、single HTML は古い内联結果になる。** 2026-04-23 22:00 のハマり例: 男寮教員名 改動後 rebuild せず repack → single に 田中 健一 残留。

---

## 学生 iOS（Swift 実装 の 視覚 source of truth）

| 項 | パス |
|---|---|
| ⭐ **最新 HTML プロトタイプ**（Phase B v2）| `03_dev/student_ios/designs/Tomoshibi_iOS_PhaseB_v2.html` |
| 旧 Phase B v1 | `03_dev/student_ios/designs/Tomoshibi_iOS_PhaseB.html`（歴史保留）|
| JSX 解包源（Swift agent が参照）| `03_dev/student_ios/designs/phaseB_src/` |
| QA 記録 | `03_dev/student_ios/designs/QA_Round1_PhaseB.md` |
| Version | Phase B v2（2026-04-22 完成）|
| 設計 LOG | `03_dev/student_ios/IOS_DESIGN_LOG.md` |
| Swift 実装（別 repo）| `~/dev/TomoshibiiOSApp/` |

Swift 実装は **本 HTML を 1:1 pixel-level fidelity で書き起こす**（`~/dev/TomoshibiiOSApp/REMOTE_AGENT_GUIDE.md` §1.1 铁律）。

---

## 更新ルール

1. 新 HTML が出た → 本文の該当行「⭐ 最新」パスを更新 + 日付 + Version
2. 旧 HTML は削除せず、ファイル名はそのまま残す（歴史参照）
3. iOS の HTML を更新したら `bash bin/sync-ios-refs.sh` を走らせて Tomoshibi-iOS/refs/ に同期
4. 本文を更新した commit は `docs(html-latest):` プレフィクスを付ける

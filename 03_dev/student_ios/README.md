# Student iOS — 設計文書 + HTML プロトタイプ

> **Swift 実装は本ディレクトリに**ない**。別 GitHub repo `otogi2025/Tomoshibi-iOS` → ローカルは `~/dev/TomoshibiiOSApp/`**。
>
> 本ディレクトリの役割 = iOS App の **設計文書** + **HTML プロトタイプ**（Claude Design 産出物、視覚 source of truth）。Swift 実装はこれらを参照して書かれる。

---

## ファイル一覧

| ファイル / ディレクトリ | 役割 |
|---|---|
| `IOS_DESIGN_LOG.md` | iOS 専属設計決定の完全アーカイブ（§3 注册 flow、§3.9 学号 6 桁、§3.10 房间号、§3.11 改动履歴 など）|
| `DESIGN_BRIEF.md` | 初期 Claude Design 入力（Round 1-2 履歴）|
| `handoff_for_code_agent.md` | コード agent 向け引き継ぎ |
| `_archived_v1_DESIGN_BRIEF_2026-04-21.md` | v1 の旧 brief（4 tab 旧方案、2026-04-22 架構推翻時に archive）|
| `round1_handoff/` | Round 1 Prompt + 参考画像 |
| `designs/` | HTML プロトタイプ本体 + JSX 解包源 + QA 記録 |

---

## 関連文書（外部）

- **共用機能マトリクス（long-term source of truth）**: `../../02_design/system_features_v0.1.md`
- **Swift 実装** : `~/dev/TomoshibiiOSApp/`（独立 repo）
- **Swift 進捗** : `~/dev/TomoshibiiOSApp/STATUS.md`
- **Remote Agent 仕様**: `~/dev/TomoshibiiOSApp/REMOTE_AGENT_GUIDE.md`
- **跨会话協作 スナップショット**: `../../00_admin/跨会话_ios_共享决策.md`

---

## 同步フロー

DMSD (本リポ) → Tomoshibi-iOS/refs/ は `bin/sync-ios-refs.sh` で単方向コピー。
本ディレクトリの設計文書を改動したら `bash bin/sync-ios-refs.sh` を走らせ、Tomoshibi-iOS 側で commit を促す。

---

## 改名履歴

- 2026-04-22: `03_dev/demo_4-28/Student_iOS_new/` として作成（4-28 冲刺命名）
- 2026-04-23: `03_dev/student_ios/` に改名（冲刺日付を命名から外し、v1.0 までの正式位置に）

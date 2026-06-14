# Student iOS — 設計文書 + HTML プロトタイプ

> **当時の Swift 実装は本ディレクトリには**ない**。別 GitHub repo `otogi2025/Tomoshibi-iOS` 上にあった（後に DMSD `dev/student_ios/v1/` へ統合）。**
>
> 本ディレクトリの役割 = iOS App の **設計文書** + **HTML プロトタイプ**（Claude Design 産出物、視覚 source of truth）。Swift 実装はこれらを参照して書かれる。

---

## ファイル一覧

| ファイル / ディレクトリ | 役割 |
|---|---|
| `IOS_DESIGN_LOG.md` | iOS 専属設計決定の完全アーカイブ（§3 注册 flow、§3.9 学号 6 桁、§3.10 房间号、§3.11 改动履歴 など）|
| `v1/` | Swift 実装本体（TomoshibiApp Xcode プロジェクト + Foundation + Features + TASKS）|
---

## 関連文書（外部）

- **共用機能マトリクス（long-term source of truth）**: `../../design/system_features.md`

---

## 改名履歴

- 2026-04-22: `dev/demo_4-28/Student_iOS_new/` として作成（4-28 冲刺命名）
- 2026-04-23: `dev/student_ios/` に改名（冲刺日付を命名から外し、v1.0 までの正式位置に）

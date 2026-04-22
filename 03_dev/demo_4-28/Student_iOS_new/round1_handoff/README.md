# Round 1 Handoff — Tomoshibi 学生 iOS App

> **作用**: Claude Design project にまとめて上传する材料一式。itsuki が開いた新 Claude project（teacher_web 側とは**分ける**）に、本フォルダ全部を input として使う。

## フォルダ内容

| File | 作用 |
|---|---|
| `Round1_Prompt.md` / `.txt` | ⭐ Claude Design に貼付ける prompt 本体（38 KB · 73 画面の仕様全量）|
| `references/01_tomoshibi_logo.png` | Splash でのみ使う灯火 logo（1024×1024 方形導出前の白底圆角版。Claude Design 側は視覚参考で OK · 実装は後で itsuki が整形）|
| `references/02_bottom_nav_sketch.png` | itsuki 手書きラフ（3 按钮 bottom nav + 点呼 sheet 構造）|
| `references/03_scan_sheet_ref_a.png` | SUNTORY ジハンピ スキャン sheet 参考 1 |
| `references/04_scan_sheet_ref_b.png` | SUNTORY ジハンピ スキャン sheet 参考 2 |

## itsuki の使い方手順

1. **claude.ai で新 project を開く**（既存の DMSD Teacher Web project とは**別**にする。設計言語を独立させたいので）
2. 本フォルダ（`round1_handoff/`）を Finder で開き、**中身を全選択 → 新 conversation の input にドラッグ**（5 ファイル一括 upload）
3. Message に **`Round1_Prompt.md` の内容全部** を paste（txt 版を本文に使っても OK）
4. 送信
5. Claude Design が Phase A（3 variations）を出すまで待つ
6. 選定して「Variation X の <ここ>」系のコメントを返す
7. Claude Design が Phase B で全 73 画面を出す
8. 最後に `「Save as standalone HTML: Tomoshibi_iOS_Round1.html」` を依頼
9. ダウンロードした HTML を本フォルダ `../designs/` に置く（新規）

## 出力後の扱い

Claude Design の成果:
- 標準 HTML → `Student_iOS_new/designs/Tomoshibi_iOS_Round1.html`（8-10 MB 程度）
- Screenshot 一式 → `Student_iOS_new/designs/screenshots/`
- 日本語 校正 list → `Student_iOS_new/designs/wording_review.md`

**代码 agent はこの HTML を参照して SwiftUI に書き起こす**。pixel fidelity を維持。

## 注意点

- Round 1 で **73 画面一回出し**（web 側の Round 1-3 分割方式と違う）。Claude Design の credit 消費は大きくなる
- 分からないことがあれば Claude Design が listo_questions として返してくる → itsuki が回答 → 継続
- Phase A の 3 variations は 1 回の送信で出るはず。Phase B は 73 画面大きいので 1-2 回に分けて出る可能性あり
- 成果 HTML が大きすぎて standalone ダメな場合、external CDN 使用版でも OK（demo day CDN 不達の時用に web side のような offline-backup を後で生成）

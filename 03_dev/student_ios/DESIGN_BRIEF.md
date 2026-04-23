# Tomoshibi 学生 iOS App — 设计 & 实装状态

> **作用**: 実装進捗追跡 + Claude Design の reference。決定事項は `IOS_DESIGN_LOG.md` に詳細。本档は「今どこまで進んだか」の概要。
> **建立**: 2026-04-22 晚 · [Mac-demo-sprint]
> **最后更新**: 2026-04-22 晚（Round 1 Prompt 落盘）
> **権威源**: 本档 + `IOS_DESIGN_LOG.md` + `round1_handoff/Round1_Prompt.md`

---

## 1. 当前状态（2026-04-22 晚）

**フェーズ**: Round 1 prompt 完成、Claude Design に送る前の itsuki 最終 audit 待ち。

### 進捗マイルストーン

| マイルストーン | 状態 | 日期 |
|---|---|---|
| 需求棚卸（73 画面）| ✅ | 2026-04-22 晚 |
| 決定事項 lock-in（Q1-8 + N1-20）| ✅ | 2026-04-22 晚 |
| `IOS_DESIGN_LOG.md` 落盘 | ✅ | 2026-04-22 晚 |
| 参考画像 import（4 枚）| ✅ | 2026-04-22 晚 |
| `Round1_Prompt.md` 执筆（38 KB）| ✅ | 2026-04-22 晚 |
| itsuki audit Prompt | ⏳ | 次 |
| 跨文档同步（CLAUDE.md 账号规则）| ⏳ | 本会话 end 前 |
| Claude Design に送信 | ⏳ | itsuki 側 |
| Phase A（3 variations）受取 | ⏳ | Claude Design 側 |
| Variation 選定 | ⏳ | itsuki 側 |
| Phase B（73 画面）受取 | ⏳ | Claude Design 側 |
| standalone HTML import | ⏳ | `designs/` へ |
| SwiftUI 書起 | ⏳ | 代码 agent |

---

## 2. 本目录文件清单

```
student_ios/
├── IOS_DESIGN_LOG.md                         # ⭐ 決定事項全归档（唯一真值）
├── DESIGN_BRIEF.md                           # 本文件（進捗追跡）
├── _archived_v1_DESIGN_BRIEF_2026-04-21.md   # 旧 4-tab 版（[Code-Agent] 2026-04-21）
└── round1_handoff/                           # Claude Design へ送るパッケージ
    ├── README.md                             # itsuki への送信手順
    ├── Round1_Prompt.md                      # ⭐ Prompt 本体 (38 KB)
    ├── Round1_Prompt.txt                     # 同上 .txt version
    └── references/
        ├── 01_tomoshibi_logo.png             # Splash 用 logo
        ├── 02_bottom_nav_sketch.png          # itsuki 手書きラフ
        ├── 03_scan_sheet_ref_a.png           # ジハンピ 参考 1
        └── 04_scan_sheet_ref_b.png           # ジハンピ 参考 2
```

追加予定:
- `designs/` — Claude Design output 置場（standalone HTML + screenshots）
- `round2_handoff/` — Round 1 成果物に対する追加修正があれば（予定外）

---

## 3. Design System — 3 variations 候補（Phase A で Claude が提案）

itsuki 指示（Q5）: **Claude Design が 3 variations を提案、itsuki が選定**。本 project では事前 tokens 固定しない。

軸:
- 配色（Ryō cool / Warm 灯火 / Mono minimal 等）
- Liquid Glass 濃度
- Radius / Spacing のトーン
- Dark / Light 両方 preview

固定要求:
- Font: Hiragino Sans / Noto Sans JP
- iOS 26 Liquid Glass active
- Dark mode 必須
- Logo: splash のみ

---

## 4. 画面レンジ（73 項 · 詳細は Prompt 参照）

| Section | 範囲 | 数量 | Prompt 参照 |
|---|---|---|---|
| §0 認証 / 起動 | Splash + Onboarding + 注册 4 step + Login + Lockout + Pass-reset 説明 | 10 | Prompt §3 |
| §1 Home | 主屏 + 10 card + 持续 bar + 中央 sheet 4 態 + 3 種反馈 sheet | 8 | Prompt §4 |
| §1.4 Home 子頁 | 通知 / 快递 / 遗失物 / 点歌 / 宿舍墙 / 活動 / バス / 匿名建議 | 18 | Prompt §4.5 |
| §2 申し込み | Landing + 7 種申請 form + 詳細 + 免点呼閲覧 + 履歴 | 13 | Prompt §5 |
| §3 マイページ | Landing + 個人 + 8 種履歴 + 設定 + 関於 + ログアウト | 14 | Prompt §6 |
| §4 共通 Comp | TabBar + home icon + back + 顶部 bar + 举报 + 空状態 + error + loading + DEMO badge + confirm | 10 | Prompt §7 |

**合計 73 項**。

---

## 5. Spec 対齐项

### 5.1 点呼時間（Prompt §0.4）

- 一般寮生: 平日朝 7:00 / 晚 21:00 · 土日 朝 8:00 / 晚 21:30
- サッカー部: 平日朝 6:00 / 晚 21:00
- 迟到判定 3 分（`late_threshold_seconds = 180`, spec §4.2）

### 5.2 扣分ルール（Prompt §4.4.2）

- 遅刻 0.5 点 / 欠席 1.0 点
- 月 4 点 → 清掃罰則
- 月 8 点 → 外出禁止

### 5.3 男女寮分離

- 女性寮 W101-W112 / 男性寮 M101-M112
- 00 号 = W101 = リュウ イヒ

### 5.4 Web 側と整合

- 24 学生 ROSTER = web `round2/theme.jsx` と完全一致
- 扣分配置 = web `/discipline` と同 config
- 外泊 form fields = web `outstay-detail-modal` と mirror

---

## 6. 下一步（code agent 側実装路線）

Phase B HTML 出たら:

1. **D6**: Claude Design HTML を analyze → SwiftUI 構造に mapping
2. **D6**: Xcode project 新規作成（iOS 26 target · iPhone 17 Pro）
3. **D6**: Liquid Glass API 学習（`.glassEffect()` · `.glassBackgroundEffect()`）
4. **D7**: §0 認証 flow 実装 + Mock 后端 API 呼び出し
5. **D7**: §1 Home 実装（持续 bar + inner tabs + card grid）
6. **D7**: §2 申し込み · §3 マイページ 並列実装
7. **D7 夜**: §1.4 子ページ（Community 系）
8. **Demo 前夜**: Seed data 整合 + リハーサル

iOS App **Xcode シミュレータで demo**（Apple Developer Program 未加入 = 実機不可）。

---

## 7. Demo Day 兜底

- iPhone 17 Pro simulator で Xcode から App を走らせる
- Mac 画面を iPad に AirPlay（管理員に見える）
- もし Xcode で動かない場合: Claude Design HTML を Safari iPhone 17 Pro frame size で代替表示
- Mock 後端 API（`03_dev/backend/`）が落ちた場合: hardcoded seed でフォールバック

---

## 8. 日本語 UI 術語対照表（Web と一貫）

Web 側 `teacher_web/DESIGN_BRIEF.md §8` の表を iOS でもそのまま使用。追加:

| 中文 | 日本語 |
|---|---|
| 首頁 | ホーム |
| 申請（tab）| 申し込み |
| 我的 | マイページ |
| 點呼（按鈕）| 点呼 |
| 掃描準備 | スキャンの準備 |
| 鎖定 | ロック |
| 解除 | 解除 |
| 残り時間 | 残り時間 |
| 確認 | 確認 |
| 戻る | 戻る |
| 次へ | 次へ |
| 下書き保存 | 下書き保存 |
| 提出 | 提出 |
| 取り下げ | 取り下げ |
| 承認 | 承認 |

---

**END** — Round 1 送信前の最終 audit 待ち状態。

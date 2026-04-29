# Round 1 指令 — Tomoshibi 学生 iOS App（初回・完全版）

> **使用方法**：
> 1. 在 claude.ai 开 **新 Project**（和 teacher_web 的 DMSD project **分开**，设计语言不共享）
> 2. 把 `round1_handoff/references/` 文件夹**整体**拖进对话输入框（4 张图 + 本 prompt 一起上传）
> 3. 发送本 prompt 整段
> 4. Claude Design 会先出 Phase A（3 variations），itsuki 选定后 Phase B 一次性出全 73 页

---

こんにちは、Claude Design さん。

私は itsuki、中国からの留学生で日本の高校に在籍しています。筑波大学 AC 入試（2027 年 4 月入学）のプロジェクトとして、**寮の点呼・生活管理システム「Tomoshibi（灯火 / ともしび）」** を開発中です。老师用 iPad Web UI は別 project で既に Round 1-3 完了しています。本 project では **学生用 iPhone App（iOS 26 / iPhone 17 Pro）** の UI デザインを一括で仕上げたいです。

**AC 面試向けストーリー**（参考）:「日本で留学する私にとって、寮は異国の第二の家。このシステムが守るのは『灯火』—— 毎晩学生が無事に帰宅し、部屋に灯りが灯ること。だから日本語名を Tomoshibi（灯火）にしました。」

---

## 0. 最重要の前提（必ず読む）

### 0.1 Target 環境

- **Device**: iPhone 17 Pro portrait（画面 402×874 pt · 1206×2622 px）
- **OS**: iOS 26（Liquid Glass デザイン言語が使える最新世代）
- **言語**: **UI 全面日本語**。英語や中国語を UI に出さない
- **フォント**: Hiragino Sans / Noto Sans JP（英字・数字は SF Pro 可）
- **アイコン**: SF Symbols（HTML では Material Symbols Rounded で代替）
- **向き**: portrait only。landscape 非対応
- **ダーク / ライト**: 両方設計（iOS 26 Liquid Glass は暗モードで映える）

### 0.2 Liquid Glass（iOS 26 新デザイン言語）

- **Sheet / Modal / Blur Overlay** は Liquid Glass 効果を積極使用
- HTML mock では `backdrop-filter: blur(24px) saturate(180%)` + 半透明 `rgba(255,255,255,0.72)` / ダークモードでは `rgba(10,12,18,0.60)` で模倣
- 実装は SwiftUI 原生 `.glassEffect()` で落とすので、HTML は**視覚のみ再現**で OK

### 0.3 交付の二段階（重要）

**Phase A**（まず出して）— Design System Variations **3 案**:

Web 側 Round 1 でも 3 variations（A·静 / B·密 / C·涼）を出していただきました。iOS 側も同じ方式で、以下の軸で 3 案を提案ください:

- 軸: **配色 × 全体トーン × Liquid Glass の効かせ方**
- 各 variation で以下を見せる:
  - Home の主要部分（顶部点呼 bar + 扣分カード + Community カード x2）
  - Bottom nav（3 按钮 · 中央徽章タイプ）
  - 点呼 Sheet（Liquid Glass 展開状態）
  - 注册 Step 1（Form 基本コンポーネント）
  - Tokens 一覧（color / type / spacing / radius / elevation）

**Phase B**（itsuki が variation を選んだ後）— 本 prompt §2-§11 に書いてある **全 73 項** をワンショットで出力:
- 63 ページ + 10 共通コンポーネント
- ライト / ダーク両方
- Seed data は §12 に記載（必ず反映）

Phase A と Phase B は**同じ conversation 内で続ける**（新 project を開かない）。

### 0.4 添付ファイル（references/ フォルダ）

| ファイル | 内容 | 活用法 |
|---|---|---|
| `01_tomoshibi_logo.png` | 灯火アプリアイコン（炎 + 中心の黄色球）| Splash 画面のみで使用。他画面には出さない。1024×1024 方形（iOS が角丸を自動で付ける） |
| `02_bottom_nav_sketch.png` | itsuki が手書きしたラフ：3 按钮 bottom nav + 点呼 sheet の想像図 | Bottom nav の構造参考（申し込み / 点呼 / マイページ）|
| `03_scan_sheet_ref_a.png` | SUNTORY ジハンピ の "スキャンの準備ができました" sheet スクショ | 点呼 sheet の Liquid Glass + 白 sheet + 円形イラストレーション + キャンセルボタンの視覚参考 |
| `04_scan_sheet_ref_b.png` | 同上・状態 2 | 同上 |

### 0.5 Logo 使用範囲（厳守）

- **Splash（起動画面）のみで使用**
- Home / Nav / TabBar / マイページ すべて **logo を出さない**（itsuki 指示）
- アプリ内のブランド表現は文字「Tomoshibi」でのみ行う

---

## 1. システム全体像（背景 context）

- **Tomoshibi = 寮点呼・生活管理システム**
- **学生側（本 App）**: 签到 / 健康報告 / 欠席申請 / 各種申請 / 規律查看 / 生活モジュール（巴士 / 活动 / 宿舍墙 / 点歌 / 匿名建議 / 遗失物 / 快递）
- **老師側（別 project · iPad Web）**: 点呼開始・終了 / 座席表 / 手動改判 / 申請審批 / 規律管理 / 掲示物発行
- **点呼機（Raspberry Pi）**: 入口に設置、NFC タグ読取 + 音声読み上げ

**本 App は 4 月 28 日に寮管理員向け demo で動かす**。管理員が「このシステムを導入する」と決断する鍵は、**「この学生が 1 台の iPhone で全ての日常ケア・申請・点呼対応を完結できる」** と視覚で理解できること。

---

## 2. 全体 Navigation 構造（⭐ 最重要）

### 2.1 Bottom Navigation — 3 按钮（4 tab ではない）

```
┌───────────────┬─────────────┬───────────────┐
│  ✉ 申し込み   │  ⭐ 点呼    │  ✦ マイページ │
│                │  (中央・大) │                │
└───────────────┴─────────────┴───────────────┘
```

- **左・申し込み**: tab（タップで申し込み Landing へ）
- **中・点呼**: **action button**（徽章型・金色アクセント）— tap で点呼 sheet を現在画面の上に重ねて表示。**tab 切替はしない**
- **右・マイページ**: tab（タップでマイページ Landing へ）

`02_bottom_nav_sketch.png` を参照。デフォルト初期画面 = Home（**Home は nav 上の tab ではない** —— 中央ボタンが点呼以外で、Home は "画面全体のベース" として常駐）。

### 2.2 画面階層ルール

| 階層 | 左上 icon |
|---|---|
| **Home** | なし（ホーム自体なので） |
| **申し込み / マイページ Level 1**（それぞれの Landing） | 🏠 **Home icon**（line 細線・handdrawn 風の家シルエット、emoji ではない）→ tap で Home に戻る |
| **Level 2+**（申請 form / 履歴 list / 詳細 …）| `←` 通常の戻る矢印 → tap で前の階層に戻る |
| **Long-press `←`**（0.4 秒長押し）| **breadcrumb popup** 出現（今いる階層の上 1-3 層の名前 list + Home を含む。tap で直接ジャンプ）|

### 2.3 Home の扱い

**Home は "その他すべて" を抱える omnibus ページ**:
- 申し込み / マイページ 以外の**全機能**が Home 配下にある
- 各種機能へは Home の card を tap して Level 1 → Level 2 で潜る
- だから Home の card 密度は高い → **section 分け + 内部 tab** で縦長スクロールを抑える

### 2.4 持続 顶部 bar（全 App 常駐）

**全画面の最上部に点呼状態 bar を常駐**（Sheet / Modal 覆う時のみ非表示）。詳細は §4.1。

---

## 3. 画面 §0 · 認証 / 起動 flow（全 10 画面）

### §0.1 Splash（起動画面）

- 背景: 白（ライト）/ 近黒（ダーク）
- 中央: `01_tomoshibi_logo.png` を 160×160 pt で配置（周りに淡い glow）
- 下部: 小字「Tomoshibi · 灯火」+ バージョン `v0.1.0-demo`
- Fade-in 1 秒 → 0.5 秒 hold → Home（session あり）or 注册 flow（session なし）へ遷移

### §0.2 Onboarding（3 画面・初回のみ · skippable）

- 画面 1: 「点呼自動化」—— NFC タグに iPhone をかざすだけで签到完了
- 画面 2: 「申請線上化」—— 紙の外泊届 / 帰国届 を App で提出
- 画面 3: 「生活機能一体」—— 巴士 / 活动 / 宿舍墙 / 遺失物 / 快递 全部ここで
- 各画面: 上部イラストレーション + 下部文字（2-3 行）+ ページインジケーター + 「スキップ」(上部右) + 「次へ」「始める」(下部) 
- **第 3 画面の「始める」タップ → 注册 flow §0.3 に遷移**

### §0.3 注册 Step 1 · 基本情報

- 上部: 「アカウント作成 (1/4)」+ プログレスバー 25%
- 中央 form:
  - **氏名** input（placeholder「リュウ イヒ」）
  - **生年月日** (iOS wheel date picker、デフォルト 2006-01-01)
  - **性別** radio（男 / 女）+ ヒント「性別により自動的に男寮 / 女寮に配属されます」
  - **アバター**: 円形 placeholder + 「写真を選択」ボタン（画像アルバムから選ぶ）or 「デフォルトを使う」(氏名の頭 1 文字 + cobaltSoft 背景)
- 下部: 「次へ」primary button（全必須フィールド入力後有効化）

### §0.4 注册 Step 2 · 学生区分

- 上部: 「アカウント作成 (2/4)」+ 50%
- 中央: 「あなたの点呼区分」radio（大きめカード 2 枚）:
  - 一般寮生（点呼時間 平日朝 7:00 / 晚 21:00 · 土日 朝 8:00 / 晚 21:30）
  - サッカー部（早朝練があるため 平日朝 6:00 / 晚 21:00）
- 下部: 「戻る」(secondary) + 「次へ」(primary)

### §0.5 注册 Step 3 · 連絡先

- 上部: 「アカウント作成 (3/4)」+ 75%
- 中央:
  - **メールアドレス** input（placeholder「example@email.com」）+ 小字「認証メールは送信されません。将来のパスワードリセット時の確認用です」
  - **電話番号** input（placeholder「090-1234-5678」）+ 小字「寮監があなたに連絡する場合に使います」
- 下部: 戻る + 次へ

### §0.6 注册 Step 4 · パスワード設定

- 上部: 「アカウント作成 (4/4)」+ 100%
- ⚠ **必ず表示する警告 banner**（amber 背景 / 濃色縁）:
  > パスワードは自分では変更できません。変更には寮監への連絡が必要です。入力時は慎重にお願いします。
- Form:
  - **パスワード** input（secure text）+ 「8 文字以上」hint
  - **パスワード（確認）** input（secure text）
  - マッチしない場合 red 小字「パスワードが一致しません」
- 下部: 戻る + **「アカウント作成完了」** primary button

### §0.7 注册 完成画面

- 中央: 大きな ✅ 緑チェック + 「ようこそ、リュウ イヒ さん」
- 下: **「あなたのアカウント番号：00」** 大字 emphasis（Claude Design の seed で必ず 00 になる）
- 説明: 「次回からはこの 2 桁番号とパスワードでログインしてください」
- 「始める」primary button → Home へ

### §0.8 ログイン画面

- 上部: タイトル「Tomoshibi」+ 小字「ログイン」
- Form:
  - **アカウント番号** input（2 桁数字 · number pad 表示 · placeholder「00」）
  - **パスワード** input（secure text）
- 下部:
  - **「ログイン」** primary button
  - 下に小 link「パスワードを忘れた場合 →」 (§0.10 へ)
- フッター: `Tomoshibi v0.1.0-demo · 2026 AC 入試プロジェクト成果物`

### §0.9 ロックアウト画面

- ロック中にログインボタンを押した時の画面:
- 大きな 🔒 icon + 「ログイン試行が多すぎます」
- 残り時間 countdown mm:ss 大きく表示
- 下: 「宿監に通知しました · セキュリティのためロック中です」
- 解除後自動的に §0.8 に戻る
- **ロック段階の表示**（画面下に small note）:「現在 1 回目のロック（30 秒）· 次回失敗で 1 分間ロックに上がります」

### §0.10 パスワードリセット説明画面

- タイトル: 「パスワードをリセット」
- 本文:
  > パスワードのリセットは App 内では行えません。寮監に直接お声がけください。寮監がシステム後台で手動でリセットします。
- 小字（info box）: 「リセット後、新しいパスワードが寮監から伝えられます」
- 下部: **「戻る」** button → §0.8

---

## 4. 画面 §1 · Home（8 画面の主屏 + サブ画面多数）

### 4.1 ⭐ 持続顶部 bar（全 App 常駐 · 最重要）

**場所**: 画面最上部（Safe Area 下、Dynamic Island の下）。全ページ（sheet / modal 覆う時を除く）で常駐。

**3 つの状態**:

**① 日常（点呼なし）**:
```
[21:00 · 次の点呼まで 0h 0m]
```
- 高さ 44 pt
- 背景 Liquid Glass 半透明
- 時刻 mono font + 次回点呼までのカウントダウン
- tap 可能 → §4.2 の反馈 sheet

**② 点呼中（老師 iPad で開始済み）**:
```
[🔴 点呼中 · あと 2分 14秒で遅刻判定]
```
- 背景 amber 色チント + pulse animation
- 赤ドット + カウントダウン mono
- tap 可能 → 反馈 sheet（但是通常学生ここで直接中央ボタンを押す）

**③ チェックイン済（本人が既に签到した）**:
```
[✓ チェックイン済 21:02 · 時間内]
```
- 背景緑 チント
- 緑チェック + 時刻
- tap 不可（サイン完了済なので）

### 4.2 Bar 点击 → 反馈 sheet（§1.4.12）

半 modal（Liquid Glass 背景）下から 3 ボタン選択:

1. **体調問題を報告** → §1.4.13 form
2. **今回欠席の申請** → §1.4.14 form
3. **その他の問題** → §1.4.15 自由文本 form（+ 分類 tag: 遅刻理由 / 外出中 / その他）

### 4.3 中央 ⭐ 点呼ボタン + sheet flow

#### 4.3.1 ボタン本体

- Bottom nav の中央、3 分の 1 幅の領域を占有
- 中央に円形大 button（68 pt 径）
- 表面: 金色グラデーション背景 + ⭐ badge icon + 下に小字「点呼」
- tap 時: haptic feedback + shrink 0.95 → bounce back → §4.3.2

#### 4.3.2 Sheet ① 準備状態（image #4 · SUNTORY ジハンピ style）

Half-sheet（画面下 55% 占有）slide-up with Liquid Glass backdrop over the rest of screen:

```
┌─────────────────────────┐
│                   ✕    │ ← 右上 close button
│                         │
│  スキャンの準備ができ   │ ← title 24pt bold
│  ました                 │
│                         │
│  ① 入口の NFC マーク    │
│    にスマホをかざす     │
│  ② 画面が光ったら完了   │
│                         │
│     ┌─────────┐        │
│     │  📱 →  │        │ ← 圆形 animated illust
│     └─────────┘        │   (phone 往前一碰 loop)
│                         │
│   ╭─────────────╮      │
│   │  キャンセル  │      │ ← large blue pill button
│   ╰─────────────╯      │
└─────────────────────────┘
```

Background: 全屏 Liquid Glass `backdrop-filter: blur(32px)`.

#### 4.3.3 Sheet ② 成功状態（NFC 読取完了後 auto-transition）

同じ sheet 内で animated transition:
- 円形イラスト → 大きな緑チェック ✅（60 pt）
- タイトル → 「チェックイン完了」
- 中央: 「21:02 · 時間内」 badge（緑 chip）
- 小字: 「お疲れさまでした」
- 3 秒後自動 dismiss → Home に戻る（顶部 bar は緑 "チェックイン済" に変わる）

#### 4.3.4 Sheet ③ 失敗状態

- 赤 ❌（60 pt）+ 「チェックインに失敗しました」
- 原因を表示（例:「現在は点呼時間外です · 次の点呼は 21:00 から」/「ネットワーク接続エラー」/「NFC 署名検証失敗」）
- 下部: 「再試行」（primary）+ 「キャンセル」（secondary）

#### 4.3.5 非点呼時段タップ時の挙動

- まず sheet を出す（§4.3.2 と同じ）
- 但し小字に「⚠ 現在は点呼時間外です · デモ用に試すことができます」の黄色 banner を追加
- NFC をかざしても実際には後端に記録されない（ローカルで success animation のみ演出）

### 4.4 Home 主屏（スクロール view · 全 card を縦に配置）

**上から下へ**:

#### 4.4.1 Greeting card

- 高さ 72 pt
- 左: 「おかえり、リュウ イヒ さん」(18 pt bold) + 下に小字「2026 年 4 月 22 日（火）」
- 右: 未読通知 bell icon（badge で未読数）→ tap で §1.4.1 通知中心へ

#### 4.4.2 扣分スコア card ⭐（重要）

- 高さ 140 pt + margin
- 三色変化:
  - **0-3.5 点** → 🟢 緑 背景 「今月 {n} 点 · 安全」
  - **4-7.5 点** → 🟡 黄 背景 「今月 {n} 点 · 来月清掃罰則予定」
  - **8+ 点** → 🔴 赤 背景 「今月 {n} 点 · 来月外出禁止予定」
- **リュウ イヒ (00 号) seed は 4 点 → 黄色 card を出す**
- Card 内容:
  - 大字: `4.0 点`
  - 進捗バー: `0 ━━━╋━━━ 4 ╋━━━━━ 8`（4 の位置にマーカー、黄色 zone）
  - 小字: 「遅刻 2 回 · 欠席 3 回」
  - 右下: 「詳細 →」 link → マイページ・減点明細へ

#### 4.4.3 Section tabs — Community 部分を整理

Home の下半分は 3 つの inner tab で折りたたむ（縦長化防止、Q3 の指示）:

```
┌───────────────────────────────────────┐
│  [生活情報] [ コミュニティ ] [ 通知 ]  │ ← inner segmented control
└───────────────────────────────────────┘
```

**Tab 1 · 生活情報** (default):
- バス時刻 card（次便 mm:ss）→ tap で §1.4.10
- 活動カレンダー card（今週 3 件 preview）→ tap で §1.4.9
- 快递 card（待領 N 件 · 赤 badge）→ tap で §1.4.2
- 遺失物 card（最新 3 張サムネイル）→ tap で §1.4.4
- 匿名建議投稿 small card → tap で §1.4.11

**Tab 2 · コミュニティ**:
- 宿舍墙 feed（最新 3 帖 preview）→ tap で §1.4.7
- 点歌候補 top 3 + 投稿 FAB → tap で §1.4.6
- タブの下部「もっと見る」link → 各フルリストへ

**Tab 3 · 通知**:
- 未読通知 list（3-5 件）
- 各行 tap で §1.4.17 通知詳細

### 4.5 Home 子ページ (§1.4 系列 · Level 2 以下)

以下すべて Home の card から tap で遷移する画面。左上に 🏠 icon（Home に戻る）:

| # | 画面 | 内容要点 |
|---|---|---|
| §1.4.1 | 通知中心 full list | 全通知 時間降順 + 種類 filter（全 / 申請 / 減点 / 快递 / 活动）|
| §1.4.2 | 快递待領 list | 待領 / 領済 filter + 各行「確認 受取」button |
| §1.4.3 | 快递詳細 | 到着時刻 / 追跡番号 / 確認 button |
| §1.4.4 | 遺失物 grid | 2 col 写真 grid + 検索 + 投稿 FAB |
| §1.4.5 | 遺失物投稿 form | 画像 picker + 拾得場所 + 特徴 + 拾得日時 |
| §1.4.6 | 遺失物詳細 | 大画像 + 説明 + 「私のものです」button |
| §1.4.7 | 点歌主页 | 候補プール list（曲名 · アーティスト · 投稿者 · 👍/👎/举报）+ 投稿 FAB |
| §1.4.8 | 点歌投稿 form | Apple Music URL paste + 曲名 + アーティスト + 投稿理由 |
| §1.4.9 | 点歌詳細 | 曲情報 + 投票 + 举报 |
| §1.4.10 | 宿舍墙 timeline | SNS 風 feed + 発帖 FAB + 各帖下 like / 评论 / 举报 |
| §1.4.11 | 宿舍墙投稿 form | text + 画像 optional |
| §1.4.12 | 宿舍墙 post 詳細 | 原帖 + 评论 list + 评论 input |
| §1.4.13 | 活動リスト | カレンダー view / リスト view toggle |
| §1.4.14 | 活動詳細 | 時間 + 場所 + 説明 + **「iPhone カレンダーに追加」** button（EventKit）|
| §1.4.15 | バス時刻表 | 3 便 list + 臨時変更 banner 顶部 |
| §1.4.16 | バス臨時公告 | 変更内容 展開 |
| §1.4.17 | 匿名建議投稿 form | カテゴリ radio + textarea + 送信（匿名ヒント）|
| §1.4.18 | 匿名建議回応 feed | 老師が公開した回応 list |

### 4.6 顶部 bar 反馈 sheet の 3 form

#### §1.4.19 体調問題報告 sheet

- 「体調不良を報告」title
- 症状 radio（発熱 / 頭痛 / 腹痛 / 吐き気 / 風邪症状 / その他）
- 体温 optional number input（°C）
- 補足 textarea（placeholder「具体的な症状があれば教えてください」）
- 「提出」primary button → toast 「先生に通知しました」→ 自動戻る

#### §1.4.20 欠席申請 sheet

- 「今回の点呼を欠席したい」title
- 理由 textarea（必須）
- 「提出」primary → 「審査中」pending badge + 戻る

#### §1.4.21 その他の問題 sheet

- 「その他の問題」title
- 分類 tag 選択（遅刻理由 / 外出中 / NFC 不具合 / その他）
- 内容 textarea
- 「提出」primary

---

## 5. 画面 §2 · 申し込み Tab（全 13 画面）

### 5.1 §2.1 申し込み Landing（Level 1、左上 🏠）

- Title: 「申し込み」大字
- Sub: 「進行中の申請: 2 件」(badge 数字 card)
- Grid 7 大項目 card（2 列 × 4 行 · 最後 1 行中央 1 個）:
  1. **外泊申請** 🏨 （進行中 1 件 badge）
  2. **帰国申請** ✈️
  3. **帰省申請** 🚆 （周 Wed 締切 reminder）
  4. **タクシー予約** 🚕
  5. **掃除提出** 🧹 （進行中 1 件 badge）
  6. **欠席届（今回）** 📝
  7. **免点呼期間 閲覧** 👁️（老師が設定したもの、閲覧のみ）
- 下部: 「申請履歴を見る」link → §2.13

### 5.2 §2.2 外泊申請 form（Level 2、左上 ←）

**⭐ Web 側 "外泊詳細 modal" の実紙 digital 化と完全 mirror**。以下のフィールド:

**§ 申請者本人**
- 氏名（auto-fill: リュウ イヒ · read-only）
- 学年・組 · read-only（自動設定）
- 本人連絡先 input（携帯 / WeChat 等）

**§ 同行者**
- 氏名 input
- 連絡先 input

**§ 外泊日時**
- 出発予定日時 (date-time picker)
- 帰舎予定日時 (date-time picker)

**§ 移動手段**
- 行き: radio（西口バス便 / 金川バス便 / JR / 自家用車 / タクシー / 教員送迎 / 飛行機 [+便名 input]）
- 帰り: 同上

**§ 宿泊先（自宅以外）**
- 分類 radio（日本人宅 / 留学生宅 / ホテル / その他）
- 名称 input
- 住所 input
- 行先都市 input

**§ 食事**
- 朝 / 昼 / 夕 自食回数 (number × 3)
- 「自分で食事入力可」checkbox

**§ 外泊の理由** textarea
**§ 備考** textarea

**§ 保護者許可**
- 確認済 checkbox
- 保護者電話 input

**下部**: 「下書き保存」(secondary) + 「提出」(primary) 

### 5.3 §2.3 外泊申請 詳細 / 状態（Level 2）

- 申請日時 + 状態 badge
- 入力済 フィールド一覧（read-only）
- **4 段階承認 workflow** visualize:
  1. 担任 先生（田中 健一）— pending ⏱ / ✅ 承認済 / ❌ 却下
  2. 寮務課長 — 同
  3. 管理課長 — 同
  4. 国際交流部長 (杉原 大輔) — 同
- 各段階に時刻 + 担当者
- 下部: 「取り下げ」button（未承認段階のみ）

### 5.4 §2.4 帰国申請 form（Level 2）

- 出発日 + 帰着日 (date picker)
- 航空券番号 input
- 行先国 input
- 家族情報（連絡先 input）
- 滞在先住所 textarea
- 証明書アップロード（画像 picker 複数）
- 理由 textarea
- 「提出」primary

### 5.5 §2.5 帰国申請 詳細 → §2.3 と同構造

### 5.6 §2.6 帰省申請 form（Level 2）

- **顶部 reminder banner（amber）**: 「帰省申請は毎週水曜日 18:00 締切です」
- 出発日 + 帰舎日
- 行先都道府県 + 住所
- 交通手段 radio
- 理由

### 5.7 §2.7 帰省申請 詳細 → §2.3 と同構造

### 5.8 §2.8 タクシー予約 form

- 日時 (date-time)
- 乗車地 input
- 目的地 input
- 同乗者数 (stepper)
- 利用理由 textarea

### 5.9 §2.9 タクシー予約 詳細 → §2.3 と同構造

### 5.10 §2.10 掃除提出 form（Level 2）

- 日期 (date picker, default 今日)
- 掃除範囲 select（部屋 / 廊下 / 共用エリア / 浴場 / その他）
- **写真アップロード**（画像 picker、複数選択 OK · 最大 5 枚 · サムネイル grid）
- 備考 textarea
- 「提出」primary

### 5.11 §2.11 掃除提出 詳細

- 提出日時 + 状態 badge（審査中 / 通過 / 退回）
- 提出画像 gallery
- 先生評点（ある場合）+ コメント
- 退回の場合 「再提出」button

### 5.12 §2.12 免点呼期間 閲覧（Level 2、read-only）

- 現在有効な免点呼期間 list
- 各行: 期間（2026-04-20 〜 04-27）+ 理由（隔離 / 行事参加 / ...）+ 設定者（先生名）
- 「これは先生が設定したものです。修正は先生にご相談ください」

### 5.13 §2.13 申請履歴 統合 list

- 全種類の申請 統合時間線 filter 可
- 各行: 種類 icon + 提出日 + 内容 summary + 状態 badge
- tap で該当詳細へ

---

## 6. 画面 §3 · マイページ Tab（全 14 画面）

### 6.1 §3.1 マイページ Landing（Level 1、左上 🏠）

**上部: 個人情報カード**:
- 大 avatar（リ 字 + cobaltSoft 底）
- 氏名「リュウ イヒ」大字
- アカウント番号「00」subdued
- 下に 2 つの badge: 「女寮 W101」+ 「一般寮生」

**中央: 7 block grid**（2 列）:
1. **個人情報** → §3.2
2. **点呼履歴** → §3.3
3. **減点明細** → §3.5
4. **処分履歴** → §3.7
5. **体調報告履歴** → §3.8
6. **申請履歴** → §2.13（共用）
7. **掃除提出履歴** → §3.9
8. **快递領取履歴** → §3.10

**下部: List**:
- 通知設定 → §3.11
- Tomoshibi について → §3.12
- ログアウト → §3.13

### 6.2 §3.2 個人情報 詳細（Level 2）

- 全部 read-only
- 氏名 / 生年月日（19 歳） / 性別 / アカウント番号 / 寮・部屋 / 区分 / メール / 電話
- 下部 info box: 「情報を変更する場合は、寮監にご連絡ください」

### 6.3 §3.3 点呼履歴 list（Level 2）

- 月 filter 上部
- 日付降順 list（group by 日期）
- 各行: 日期 + session（朝/晚）+ 状態 badge（時間内 / 遅刻 / 欠席 / 免除）+ 方式（NFC / Shortcut / 手動改判 · icon）
- **リュウ イヒ seed の履歴**:
  - 2026-04-20 晚点呼 · 欠席 1 点
  - 2026-04-19 朝点呼 · 時間内
  - 2026-04-19 晚点呼 · 時間内
  - 2026-04-18 朝点呼 · 時間内
  - 2026-04-18 晚点呼 · 時間内
  - 2026-04-17 朝点呼 · 時間内
  - 2026-04-17 晚点呼 · 時間内
  - 2026-04-16 朝点呼 · 時間内
  - 2026-04-16 晚点呼 · 時間内
  - 2026-04-15 朝点呼 · 時間内
  - 2026-04-15 晚点呼 · 欠席 1 点
  - 2026-04-14 朝点呼 · 時間内
  - 2026-04-14 晚点呼 · 時間内
  - 2026-04-13 朝点呼 · 時間内
  - 2026-04-13 晚点呼 · 時間内
  - 2026-04-12 朝点呼 · 遅刻 0.5 点
  - 2026-04-12 晚点呼 · 時間内
  - ... etc（mock data 合計約 30 件）
  - 2026-04-08 晚点呼 · 欠席 1 点
  - 2026-04-05 朝点呼 · 遅刻 0.5 点

### 6.4 §3.4 点呼履歴 詳細（Level 3、session 単位）

- 該当 session の全情報
- 改判 された場合: 改判者（先生名）+ 時刻 + 理由
- チェックイン時刻 + 方式

### 6.5 §3.5 減点明細（Level 2）

- 月 filter
- 時間線（日付順）list:
  - 2026-04-05 朝点呼 遅刻 · 0.5 点
  - 2026-04-08 晚点呼 欠席 · 1.0 点
  - 2026-04-12 朝点呼 遅刻 · 0.5 点
  - 2026-04-15 晚点呼 欠席 · 1.0 点
  - 2026-04-20 晚点呼 欠席 · 1.0 点
  - 合計 **4.0 点**
- 底部: 「現在のルール: 遅刻 0.5 / 欠席 1.0 · 月累計 4 点で清掃罰則 · 月累計 8 点で外出禁止」

### 6.6 §3.6 減点推移 chart（Level 2、§3.5 から link）

- 過去 12 ヶ月の折れ線 chart
- mock: 先月 2 点 / 今月 4 点 / 他月 0-1 点

### 6.7 §3.7 処分履歴（Level 2）

- 過去の処分 list
- 各行: 月 + 処分種類（清掃罰則 / 外出禁止）+ 触発理由（当月累計 X 点）
- 00 号は処分履歴なし → 空状態「処分歴はまだありません」

### 6.8 §3.8 体調報告履歴（Level 2）

- 時間降順 list
- 00 号 seed: 2 件:
  - 2026-04-14 · 頭痛 + 体温 37.2°C + 補足「午後ずっと頭が重い」
  - 2026-04-03 · 腹痛

### 6.9 §3.9 掃除提出履歴（Level 2）

- 時間降順 list、各行: 日期 + 範囲 + 状態 + 評点（通過済の場合）
- 00 号 seed: 2 件:
  - 2026-04-19 · 部屋 · 通過 · 5 点
  - 2026-04-05 · 共用エリア · 退回（「床が汚れている」）→ 再提出待ち

### 6.10 §3.10 快递領取履歴（Level 2）

- 待領 / 領済 filter
- 00 号 seed: 1 件待領 「2026-04-22 · Amazon · 到着」+ 3 件領済

### 6.11 §3.11 通知設定（Level 2）

- Toggle list:
  - 点呼リマインダー ✅
  - 申請結果 ✅
  - 快递到着 ✅
  - 活動リマインダー ✅
  - 減点警告 ✅

### 6.12 §3.12 Tomoshibi について（Level 2）

- 中央: 「Tomoshibi · 灯火」 wordmark（logo ではなく文字デザイン）
- バージョン `v0.1.0-demo`
- 下部: 
  > Tomoshibi は、日本の寮での点呼と生活管理を一体化したシステムです。
  > 「日本で留学する私にとって、寮は異国の第二の家。このシステムが守るのは『灯火』—— 毎晩学生が無事に帰宅し、部屋に灯りが灯ること。だから日本語名を Tomoshibi（灯火）にしました。」
  > 
  > 2026 年 AC 入試プロジェクト成果物
  > — リュウ イヒ

### 6.13 §3.13 ログアウト 確認 sheet

- 二重確認 modal:
  - 「ログアウトしますか？」
  - 「次回起動時はアカウント番号とパスワードが必要です」
  - 「ログアウト」(danger red) + 「キャンセル」

---

## 7. 共通コンポーネント（全 10 個）

| # | コンポーネント | 仕様 |
|---|---|---|
| C1 | **Bottom Nav（3 按钮）** | 左 申し込み / 中 点呼（action button）/ 右 マイページ。現ページを示す highlight（icon tint）. 中央ボタンは tab ではない |
| C2 | **Home icon（line-drawn 家）** | 左上、Level 1 ページ用。細 stroke 2 pt、シンプルな三角屋根 + 四角 body。emoji でない |
| C3 | **戻る矢印 + 長押し breadcrumb** | Level 2+ で左上 `←`。長押し 0.4 秒 → popup with full path list each tappable to jump |
| C4 | **持続 顶部 bar（点呼状態）** | 常駐（sheet 覆う時除く）。3 態: 日常 / 点呼中 / チェックイン済 |
| C5 | **举报 modal** | 任意 feed 内ポスト 舆选する時。理由 radio + 補足 + 送信 |
| C6 | **空状態** | 各 list 無データ時。薄いイラスト + 「まだ {内容} がありません」 |
| C7 | **エラー banner** | 画面上部 red banner + 「サーバーとの通信に失敗しました」+ 「再試行」 |
| C8 | **Loading skeleton** | 各 list 読込中。薄灰 placeholder block、shimmer animation |
| C9 | **DEMO badge** | 右下浮遊、amber 背景、「DEMO」小字。tap で消す option |
| C10 | **確認 modal** | 送信 / 削除 / 取り下げ 等の二重確認 |

---

## 8. Design Tokens（Phase B で確定、Phase A で 3 variations 比較）

**Phase A で提示してほしい軸**:
- 配色（例: Ryō cool / Warm 灯火 / Mono minimal 等）
- Typography（Hiragino Sans 基準 + 英数字の組み合わせ）
- Radius / Spacing の全体トーン
- Liquid Glass の効かせ方（控えめ / 積極的）
- Dark / Light 両方 preview

**固定要求**:
- Primary font: **Hiragino Sans / Noto Sans JP**
- 英数字・mono（時刻・番号）: SF Pro Text / SF Mono
- Dark mode 対応必須
- Liquid Glass を Sheet / Modal / Top Bar で使う

**参考**（推翻可、itsuki が選ぶ時の材料）:
- Web 側 Ryō token（Cobalt `#2b4d8c` / 近黒 `#14171f`）
- 火焰 Logo の暖色（#e23c2c 赤橙 + #f5c842 黄）— logo 以外で使うかは variation ごとに判断

---

## 9. Seed Data（Phase B で必ず反映）

### 9.1 00 号アカウント（⭐ 必須）

```js
const USER_00 = {
  account_number: '00',
  name: 'リュウ イヒ',
  name_kana: 'りゅう いひ',
  birth_date: '2006-10-14',  // 19 歳
  gender: 'female',
  dorm: 'women',
  room: 'W101',
  category: 'regular',  // 一般寮生
  email: 'ryu_ihi@tomoshibi.local',
  phone: '090-0000-0000',
  avatar_default: true,  // リ 字 + cobaltSoft
  current_month_points: 4.0,
  discipline_status: 'pending_cleaning',  // 来月清掃罰則予定
  late_count: 2,
  absent_count: 3,
};
```

### 9.2 減点明細 seed

```
2026-04-05 朝点呼 遅刻 0.5 点
2026-04-08 晚点呼 欠席 1.0 点
2026-04-12 朝点呼 遅刻 0.5 点
2026-04-15 晚点呼 欠席 1.0 点
2026-04-20 晚点呼 欠席 1.0 点
合計 4.0 点
```

### 9.3 24 学生 ROSTER（Web 側 Round 2 と一致）

男寮 M101-M112 / 女寮 W101-W112 · 詳細は Web 側 `theme.jsx` ROSTER 参照。

00 号 = W101 = リュウ イヒ。

### 9.4 Demo 注册魔法

- Demo 中 itsuki が 4 step 注册 flow を歩く（観客前で入力）
- 入力値: リュウ イヒ / 2006-10-14 / 女 / 一般寮生 / 任意メール / 任意電話 / 任意パスワード
- 「アカウント作成完了」tap → **既存 00 号に login**（新規 account 作成ではない）
- Home に遷移 → 既に 4 点減点 + 履歴ある状態

### 9.5 点呼履歴 mock（詳細 §3.3 参照）

30 件ほど過去 2 週間分。late 2 / absent 3 / 他全部 time_in。

### 9.6 他 mock data

- 体調報告 2 件 · 掃除提出 2 件 · 快递 1 件待領 + 3 件領済
- 通知 5 件（快递 / 申請通過 / 減点警告 / 活動リマインダー / 点歌採用）
- 宿舍墙 20 件投稿（空白じゃない感じ）
- 遺失物 6 件
- 点歌候補 8 件
- 活動 3 件今週
- バス 3 便
- 匿名建議回応 3 件

---

## 10. Interactive Behaviors（Phase B で実装）

### 10.1 顶部 bar 状態遷移

- 老師側 iPad で点呼開始 → 全学生 App の 顶部 bar が日常 → 点呼中 に変わる（mock: demo では手動 state toggle）
- チェックイン成功 → 点呼中 → チェックイン済（緑）
- 老師が点呼終了 → リセットして次の点呼を待つ状態

### 10.2 中央点呼ボタン flow

- tap → sheet preparation state
- NFC 読取成功（mock: demo では「シミュレート」ボタンで success 起動）→ success state → 3 秒 auto dismiss
- キャンセル → 戻る

### 10.3 長押し breadcrumb

- `←` 長押し 0.4 秒 → context menu popup
- 表示例: 「マイページ > 点呼履歴 > 2026-04-12 詳細」
- 各階層 tap で直接ジャンプ

### 10.4 Liquid Glass の動作

- Sheet は下から滑り上がる時、背景 Liquid Glass が fade in
- Dismiss 時 fade out
- Modal は中央 zoom-in

### 10.5 Haptic feedback

- Primary button tap: light impact
- Success (チェックイン完了): success notification
- Error: error notification
- Long-press: medium impact

---

## 11. Footer / DEMO marker

- 全画面右下に small amber badge「DEMO」（prototype であることを明示）
- 画面下フッター（splash / login / onboarding / 注册 等の非 nav 画面のみ）: `Tomoshibi v0.1.0-demo · 2026 AC 入試プロジェクト成果物`

---

## 12. 完成後の delivery（お願い）

### 12.1 Phase A 終了時

以下 3 output お願いします:
1. **Design System Variations** 3 案（各 variation 1 つの HTML artifact）
2. 各 variation の artifact には:
   - Tokens list（color / type / spacing / radius）
   - Home の主要部分 preview（bar + 扣分 card + Community card x2 + bottom nav）
   - 点呼 Sheet preview
   - 注册 Step 1 preview
3. Dark / Light 両方の preview を各 variation で見せる

itsuki がいずれかの variation を選ぶまで Phase B に進まない。選定コメント例:「Variation 2 を基準に、Variation 1 の Liquid Glass 濃度を使う」。

### 12.2 Phase B 終了時

1. **Standalone HTML（1 ファイル）** — 全 73 画面を internalize + route 切替できる navigation 付き（hash route で OK、本物の router 不要）
2. **画面 screenshot**（10-15 枚、1206×2622 · iPhone 17 Pro サイズ）:
   - Splash
   - 注册 Step 1-4（4 枚 or 合成 1 枚）
   - Home Light + Dark（2 枚）
   - 点呼 Sheet Preparation + Success（2 枚）
   - 申し込み Landing
   - 外泊申請 form
   - マイページ Landing
   - 点呼履歴 list
   - 減点明細
3. **日本語 UI wording 自信なし list**（意訳怪しいと自分で気づいた箇所を itsuki が校正）

---

## 13. 実装技術 note（Claude Design へ）

- `ios_frame.jsx` starter component を使って iPhone 17 Pro フレームで全画面を包む
- 単一 HTML 中で hash route で画面切替（`#/home` / `#/register/step1` / `#/mypage` 等）
- 状態（dark/light toggle · 扣分スコア · 点呼状態）は画面上のボタンで切替可能にする（demo ringeur 操作のため）
- Seed data は `window.__SEED__` のような global に入れておく
- CSS: `backdrop-filter` / `-webkit-backdrop-filter` で Liquid Glass 模倣
- Font: Google Fonts から `Noto Sans JP` + `Hiragino Kaku Gothic ProN` fallback
- 全 asset は HTML 内 internalize（standalone bundle のため）

---

## 14. その他

- 「額度」(Anthropic API クレジット) に制約があるため、Phase A → B を**できる限り一息で仕上げる**お願い
- Round 2 以降は予定していない（一回出し切り）
- Round 1 完了後、itsuki が手元の code agent に HTML → SwiftUI 書き起こしを依頼する

---

以上です。よろしくお願いします。まず Phase A の 3 variations をお願いします。

— リュウ イヒ（itsuki）

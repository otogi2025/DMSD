# Round 3 指令 — Tomoshibi 教员 Web 扩展

> **使用方法**：
> 1. 回到 Claude Design 里的 DMSD 同一个 project（它已经有 Round 1-2 上下文）
> 2. 把本文件夹**整个**拖进对话输入框（3 张图 + 本文件会一起上传）
> 3. 发送此 prompt 整段内容
> 4. Claude Design 会基于已有 `round2/*.jsx` 扩展 + 新建 Round 3 所需组件

---

こんにちは、Round 3 に進みます。システムの正式名称が **Tomoshibi（灯火 / ともしび）** に確定しました。以下、全体改修 + 新規ページを一度に反映してください。Round 2 の設計言語（Ryō tokens · Noto Sans JP · 4 状態 + badge）を維持したまま、「late 状態の追加」と「大幅な機能拡張」を行います。

添付ファイル:
- `01_tomoshibi_icon.png` — 新しいアプリアイコン（炎 + 中心の黄色球。"灯火" のビジュアル化）。Shell 左上の ◇ を置き換え。
- `02_gaihaku_form_reference.jpeg` — 実在の「外泊許可願」原本。外泊申請 form のフィールド設計はこの実紙を digital 化してください。
- `03_current_header_before.png` — 現在の左上 header の状態（"DMSD · 寮管理システム"）。アイコンとブランド文字だけ差し替え、"寮管理システム" は残す。

---

## 1. 全体 rebranding

### 1.1 ブランド文字列の差し替え（grep 的に全 occurrence）
- `DMSD` → **`Tomoshibi`**（すべての UI テキスト / page title / app title / shell の左上 wordmark）
- `.md` 内の技術コメントや内部 variable 名はそのまま（e.g. `window.RYO` token 名は触らない — 色の logical key なので rename 不要）

### 1.2 Shell 左上 logo
- 現在の ◇ 菱形（shell.jsx line ~28）を **`01_tomoshibi_icon.png` のアイコンに置き換え**
- 横の "DMSD" → **"Tomoshibi"**
- 下の "寮管理システム" はそのまま
- 参考: `03_current_header_before.png` の右側が差し替え後のイメージ（同じレイアウト、中身だけ交換）

### 1.3 Browser tab title
- `<title>Tomoshibi · {現在のページ}</title>`（page route に応じて動的変更）

---

## 2. 認証 flow 再構築（Round 2 の login.jsx を全面置き換え）

### 2.1 /login — 共用密碼ログイン画面
- 入力フィールド 2 つ:
  - **アカウント ID**（placeholder: "tomoshibi"；demo では固定値、全寮宿監共通）
  - **パスワード**（共用密码，全老师共有）
- 「ログイン」button（primary, cobalt）
- 失敗時: `パスワードが違います (残り X 回)` メッセージ、3 回失敗で 30 秒ロック
- フッター極小文字: `Tomoshibi v0.1.0-demo · 2026 AC 入試プロジェクト成果物`

### 2.2 /login/select-teacher — 教員選択画面（⭐ 新規，Round 2 には無い）

**レイアウト:**
- 画面タイトル: 「担当者を選んでください」+ サブ: 「本日の点呼を担当する先生のカードを押してください」
- **左右 2 column**:
  - 左 column header: **「男性寮」**（アイコン: 男性寮を想起させる小シンボル or ただの "M"）
  - 右 column header: **「女性寮」**（同上 "F" / 識別可能なもの）
- 各 column 内に教員カードを縦に並べる

**教員カードの仕様:**
- 長方形、角丸（border-radius 12-16px）
- サイズ: 幅 約 280px / 高さ 約 88px（iPad でタップしやすい大きさ）
- 内容:
  - 左: 丸アバター（頭文字 1 字、cobaltSoft 背景）
  - 中央上: 氏名大（16-18px bold）
  - 中央下: 「{最近のログイン}」例「12 分前にログイン」/「本日未ログイン」/「初回ログイン」（ink3 小字）
  - 右上隅: 前回選択された教員には small「前回」tag or 薄いアクセント枠（ハイライト）
- hover / press 時の微細 feedback（shadow 強化）

**Demo seed 教員 (4 人, code で hardcode):**
- 男性寮: 田中 健一 先生 / 佐々木 陽一 先生
- 女性寮: 鈴木 美咲 先生 / 山田 花子 先生

**編集モード（⭐ 新機能）:**
- 画面右下に **「編集」floating button** (circular, ink 背景, white pencil icon)
- 押すと編集モードに入る:
  - 各教員カードの右上に **赤円 + 黒 × の削除ボタン**が現れる（アニメで pop-in）
  - 各 column の末尾に **「+ 追加」破線カード**（grayBorder dashed + 大 plus icon 中央 + 「教員を追加」文字）が現れる
  - 右下 FAB は「完了」に変わる（編集モード終了）
- × ボタンを押すと confirm modal:
  - 「{氏名} 先生のアカウントを削除しますか？」
  - 「削除」（danger red） / 「キャンセル」
  - 削除後 toast「{氏名} 先生を削除しました」
- 「+ 追加」カードを押すと追加 modal:
  - 氏名 input（必須、placeholder「田中 太郎」）
  - （optional field 提案）ふりがな input（optional、検索用）
  - 「追加」（primary）/「キャンセル」
  - どの column でクリックされたかで 担当寮 自動判定（左で押したら男性寮所属、右で押したら女性寮所属）
  - 保存後、該当 column 末尾（+ 追加 の上）にカードが挿入される

### 2.3 切替 / 自動退出 仕様（⭐ 重要）

**明示切替:**
- Shell 左下の「切替」→ /login/select-teacher に戻る（パスワード再入力なし）
- Shell 右上に 追加**「ログアウト」ボタン**（small, icon + text）→ /login に戻る（共用密码まで clear）

**自動退出タイマー:**
- **30 分間操作なし** → 自動で /login/select-teacher に戻る（パスワードログイン状態は保持）
- 操作定義: click / scroll / keypress / mousemove いずれか
- **例外**: 点呼 session active 中（/roll-call/live 表示中）は自動退出しない
- **25 分経過時**: 右上に toast「あと 5 分で教員選択画面に戻ります」+ 中に「継続」button（押すとタイマー reset）
- パスワード自体のログアウトは時間ベースでは行わない — 物理的に browser を閉じる or 手動「ログアウト」ボタンのみ

**Demo mode**:
- `TIMEOUT_MS` constant を file top に定義（default 30 min = 1800000）
- demo 当日 itsuki が 3 分（180000）に手動変更できる位置にコメント「// DEMO: 動作確認用に短縮する場合はここを変える」を添える

---

## 3. Shell 調整

### 3.1 左上 logo 差し替え（§1.2 と同）

### 3.2 Topbar 中央に **グローバル検索 input** 追加（⭐ 新機能）
- placeholder: 「学生名・部屋番号・日付で検索...」
- 幅: 480px（flex 1 で縮小可）
- アイコン: 左 inside に虫眼鏡
- 右 inside にキーボード shortcut hint `⌘K`
- focus 時にドロップダウン suggest（mock でいい: 「リュウ イヒ (101 号室)」「田中 翔 (104 号室)」「2026-04-21」...）
- Enter で /search?q={value} へ遷移
- このフィールドは Shell 常駐（/roll-call/live 以外のすべてのページで表示）

### 3.3 Topbar 右側 layout (左→右)
- （flex spacer）
- 点呼実施中 badge（既存、緑、押すと /roll-call/live 復帰）
- **WS 接続状態 indicator**（⭐ 新）: 小ドット + tooltip「サーバーに接続中」/「切断 · 再接続中」赤点滅
- 日時表示（既存、mono font）
- 「ログアウト」small button（§2.3）

### 3.4 Shell 左下 教員情報エリア
- 既存: アバター + 氏名 + 寮名 + 「切替」
- 追加: 氏名 下段に **担当寮 badge**（"男性寮" or "女性寮"、色分け）
- 追加: 右端に小 **「当番中 / 非番」indicator**（緑 / グレー、default 当番中）

---

## 4. /roll-call ダッシュボード 改修

### 4.1 ROSTER（seed 学生名簿）更新
- **⭐ 男女寮分離**: 各学生 record に `dorm: 'men' | 'women'` field を追加。現 24 人を **男 12 人 / 女 12 人 に分類**:
  - 男性寮（部屋 M101-M112）: 佐藤 健太 / 高橋 翔 / 渡辺 隼人 / 中村 大樹 / 吉田 蓮 / 山口 健 / 松本 翔太 / 斎藤 晴 / 阿部 悠真 / 木村 拓哉 / 山崎 航 / 佐々木 颯（1 人置換）
  - 女性寮（部屋 W101-W112）: リュウ イヒ / 田中 美咲 / 山本 綾 / 小林 美優 / 加藤 陽菜 / 山田 千夏 / 井上 結衣 / 清水 花音 / 林 美奈 / 池田 咲希 / 橋本 紗羅 / 鈴木 涼
  - 教員選択時に担当寮が決まる → Live はその寮の 12 人のみ表示（6 列 × 2 行 or 4 列 × 3 行）
- **itsuki bind 用**: `リュウ イヒ (S001, 女性寮 W101)` は demo 当日に彼女の iPhone を紐付ける固定席
- **Live 画面初期状態では全員 `unknown` 灰色**（Round 2 の seed() 関数は demo のために pre-populated チェックインしていたが、本物の iPhone tap と後端 API 連携テストをするため **初期 seed は全灰**にする）
- デモ用リセット button（Round 2 既存）は残す。座席を全灰に戻す

### 4.2 最近のセッション list 改修
- 既存 table に **「詳細」列** 追加（右端）
- 各行「詳細」リンク → `/records?date={日付}&session_id={id}` への navigation
- ハンドラは onClick callback で親コンポーネントが setRoute('records', params) する形で OK

### 4.3 ⭐ 新規カード「最近 7 日 遅刻・欠席トレンド」
- 位置: 4 つの統計カード（本日実施 / 欠席者 / 審査待ち申請 / 警告リスト）の **下**、最近のセッション list の **上**
- 幅: full width
- 内容: **小さめの bar chart**、横軸 7 日（一昨々々々日 → 今日）、縦軸 人数
- 2 系列表示（stacked or side-by-side）:
  - 黄 = 遅刻者数
  - 赤 = 欠席者数
- 各 bar hover で tooltip「2026-04-19 · 遅刻 2 / 欠席 1」
- bar click で /records?date={その日}
- mock data: demo 向けに 7 日分 random だがトレンドが分かる値（例: `[{date:'04-15',late:1,absent:0},{date:'04-16',late:0,absent:0},{date:'04-17',late:2,absent:1},...]`）

### 4.4 ダッシュボード タイトル
- 「点呼ダッシュボード」right に小字「2026-04-21（火）」（既存）
- サブタイトル「対象 24 名 · {担当寮} · {教員名}」

---

## 5. /roll-call/live 座席表 拡張

### 5.1 ⭐ late（黄色）状態の追加（Round 2 で漏れていた core 修正）

`theme.jsx` に late token を追加:
```js
late: '#c69320',       // amber
lateSoft: '#f5e7c2',
lateBorder: '#e5c98a',
```

（既存の warn を流用しても OK、あなたの判断で。ただし意味論上「late」を明示的に切る方が clear）

**判定 logic**:
- session 開始後、`LATE_THRESHOLD_SEC` 秒経過 → 未チェックインの学生の status を `unknown` → `late` に自動遷移（黄色）
- `LATE_THRESHOLD_SEC` は default 180 秒（= 3 分、spec §4.2 準拠）。`theme.jsx` に constant として export
- 閾値経過**後**にチェックイン → `late`（入れたけど遅刻扱い、黄色のまま）
- 老師が「終了」を押す → 未チェックインの灰 + 黄 全員 `absent` に変換

### 5.2 ⭐ 迟到判定 予告バー
- Live 画面上部（セッション名の下 or 横）に小字:
  - 経過 0-3 分: `あと X 分で遅刻判定開始`（cobalt / neutral）
  - 経過 3 分以上: `遅刻判定中 · 未チェックイン者は自動的に遅刻になります`（amber badge）
- リアルタイム カウント down / up

### 5.3 ⭐ バッジ / 叠加表現（extend）

座席カードの右上隅に重ね badge (position absolute):
- 🏥 体調報告（`ok` 色の座席でも赤十字っぽい small badge、詳細は override-modal expand で見る）
- ? 欠席届 pending（amber 半透明 ? badge）
- M 手動調整痕跡（hover tooltip で「○○先生 · HH:MM · 理由」、click で履歴 modal）
- 複数同時: 積み重ね OK

### 5.4 override-modal 拡張
- 既存の 4 radio + 理由 textarea + 欠席届同時承認 checkbox → 維持
- **expand**: 学生に pending の欠席届があれば、modal 上段に「提出された欠席届」card を展開 (学生からの理由 + 提出時刻 + 「承認」「却下」large button)
- **expand**: 学生が体調報告を提出していれば、同じく「体調報告」card (症状 + 補足 + 「既読」button)
- **expand**: 既に手動調整されている座席なら、履歴 section「調整履歴」に過去の変更 list

### 5.5 ⭐ 座席表 右下に「凡例」expandable button
- 折りたたみ可能 panel（default 閉じている or 薄く表示）
- 展開すると 5 状態色 + 4 badge の意味 一覧
- 管理员 demo 時に「この色は何？」対応に有効

### 5.6 ⭐ 点呼開始前の「対象選択」
- /roll-call ダッシュボードの session 名 dropdown を拡張:
  - 朝点呼 · 普通寮生
  - 朝点呼 · 部活早朝（現 spec §4.2 "足球部"）
  - 晚点呼 · 普通寮生
  - 晚点呼 · 部活早朝
- demo は「晚点呼 · 普通寮生」default

### 5.7 ROSTER 初期表示
- §4.1 の通り、Live 画面入った瞬間は全員 `unknown` 灰
- 担当寮の 12 人のみ表示（男寮教員 login 中なら男寮 12 人、女寮教員なら女寮 12 人）
- seed() 関数は残すが、pre-populated checkin は全削除（理由: 本物の iPhone tap で座席が順次色変化する様を管理员に見せたい）

### 5.8 ⭐ デモコンソール（下部 panel）
- Live 画面下部、凡例 button の隣に **「デモコンソール」expandable section**
- 開くと説明文: `NFC 読み取りに失敗した場合、以下のボタンでシミュレーション可能`
- ボタン群（現寮の 12 人分、dashed border 小 button）:「{学籍 ID} シミュレーション ({氏名})」
- click → 対応学生の座席を `ok` に変えて checkinAt を現在時刻に set（後端 API 呼び出しは optional、Claude Design 版では client-side state mutation で OK）
- 管理員 demo 時に万一 iPhone tap が効かないための fallback。itsuki の旧プロトタイプ（`handoff/uploads/` のスクショ）にあった feature を Round 3 で復活

---

## 6. /applications — 申請中心（⭐ 完全新規）

### 6.1 landing レイアウト
- 画面上部 4 tabs: **外泊 / 帰国 / 帰省 / タクシー**
- default tab: 外泊
- tab バッジ: pending 数を右肩に小円表示（例 外泊 `3`）

### 6.2 外泊 tab（Tier 1 完全実装）

#### 6.2.1 一覧ビュー
- 上部 sub-filter: **審査待ち（default）/ 承認済 / 却下 / 質問あり / 全て**
- table 列:
  | 申請者 | 部屋 | 担当寮 | 出発日時 | 帰舎予定 | 行先 | 提出時刻 | 状態 | 操作 |
  |---|---|---|---|---|---|---|---|---|
- 「操作」列: 「詳細」button
- 上部右: **「CSV 出力」button**（skeleton, click で alert「Demo 版未対応」）
- mock data 3-5 件（状態 mix）

#### 6.2.2 詳細 modal（⭐ 実物の外泊許可願 再現 — `02_gaihaku_form_reference.jpeg` 参照）

modal 内のフィールド layout（上から下）:

**§ 申請者本人**
- 氏名: リュウ イヒ
- 学年・組: 中 1 年 1 組
- 本人連絡先: 080-9490-2895 (携帯 / WeChat 等)

**§ 同行者**
- 氏名
- 連絡先

**§ 外泊日時**
- 出発予定日時: 2026-04-22 09:15
- 帰舎予定日時: 2026-04-23 17:00

**§ 移動手段（ラジオ群）**
- 行き: 西口バス便 / 金川バス便 / JR / 自家用車 / タクシー / 教員送迎 / 飛行機 （+ 便番号 input）
- 帰り: 同上（選択式）

**§ 寮生特別運行**（該当する場合のみ、checkbox）
- 期間: 月 日 ～ 月 日

**§ 宿泊先（自宅以外）**
- 分類: 日本人宅 / 留学生宅 / ホテル / その他 (radio)
- 名称: ジ・ワンフィス(ゾ) 岡山
- 住所: 岡山市北区野田 1-1-3
- 行先都市: 岡山

**§ 食事**
- 朝 / 昼 / 夕 の数 (number input × 3)
- 「自分で食事入力可（スプレッドシート × 入力）」checkbox

**§ 外泊の理由**
- textarea

**§ 備考**
- textarea

**§ 保護者許可**
- 確認済 checkbox + 保護者電話 input

**§ 承認 workflow（4 段階、demo では 1 段階に簡略化可）**
以下を横並び 4 つの状態 card で表示:
1. 担任 先生（田中 健一 先生）— 印 pending / ✅ 承認済 / ❌ 却下
2. 寮務課長
3. 管理課長
4. 国際交流部長 杉原 大輔

**§ modal 底部 action buttons（⭐ 3 button 横並び）**
- 「承認」 (primary, cobalt)
- 「却下」 (danger, red outline)
- 「質問あり（保留）」 (warning, amber outline)

押す前に確認 modal:「{氏名} の外泊申請を承認しますか？」+ 「承認」 / 「キャンセル」

**§ 承認後の表示**
- 詳細 modal に **承認者 + 承認時刻** が追記され表示（「田中 健一 先生 · 2026-04-21 19:40 承認」）
- 一覧 table の状態列が更新
- 学生 iOS App に push 通知送信（その部分は backend 側、UI としては toast「学生に通知しました」でいい）

### 6.3 帰国 / 帰省 / タクシー tabs（skeleton）

各 tab は共通の `<ApplicationTabSkeleton>` component:
- 上部: 状態 sub-filter (審査待ち / ...) — 存在するだけで中身は 0 件
- mock 2 件 の簡易 list + 「開発中」tag
- 詳細 modal は出さない（list click は何もしない or toast「Demo 版未実装」）

---

## 7. /discipline — 規律・処分（Tier 1 完全）

単一スクロールページ、以下を上から順に section で表示:

### 7.1 先頭: **ルール表示 card**（⭐ 新規）
- 「現在の減点ルール（運用前、先生と調整可）」タイトル
- 4 値 pill 表示:
  - 遅刻: 0.5 点
  - 欠席: 1.0 点
  - 清掃罰則 発動: 月累計 ≥ 4 点
  - 外出禁止 発動: 月累計 ≥ 8 点
- 右端に「値を変更 (管理者のみ)」button skeleton

### 7.2 §1 本月全員ランキング table
- 列: 順位 / 学生 / 部屋 / 減点合計 / 遅刻回数 / 欠席回数 / 距清掃まで / 距禁足まで
- 上部 filter: 月選択 (default 本月) + 寮選択 (default 現在担当寮)
- 点数高い順 default sort、列 header click で他ソート

### 7.3 §2 清掃罰則名単 cards（来月対象）
- grid card：学生氏名 + 部屋 + 当月減点 + 理由 timeline 抜粋

### 7.4 §3 外出禁止名単 cards（来月対象）
- 同じ form

### 7.5 §4 警告リスト（連続超標）
- 過去 2 ヶ月連続で閾値超の学生

### 7.5.1 ⭐ 将来機能の予告 section（UI 予約スペース, Demo では実装しない）
- §4 警告リスト の下に小さい card:
  - タイトル「自動アラート（開発中）」+ amber badge
  - 説明文（日本語）:
    > 将来、後端サーバーに常駐スクリプトを設置し、特定学生の遅刻・欠席が一定数に達した時点で自動的に宿監へアラート短評（例:「この学生は今月遅刻 5 回、要面談」）を生成する予定です。現 demo 版では手動確認のみ。
  - 視覚: 未実装なので grey out、mock alert 2 件だけ薄く表示（「{学生名} · 今月遅刻 5 回 · 要面談」のような文言）
  - **この機能は demo 当日は動作させない。UI のみ preview。itsuki が管理者に「こういう拡張を計画しています」と説明する時の視覚補助**

### 7.6 学生 card click → 学生詳細 modal
- 当月違反 timeline（日付 + 種別 + 減点）
- 累計 推移 line chart
- 「長期免除設定」button skeleton → modal skeleton「開発中」

---

## 8. /records — 記録（Tier 1）

- 上部: date picker (default 今日) + session 名 dropdown
- Table: 学生 / 部屋 / session / チェックイン時刻 / 状態 badge / 方式（NFC 卡 / Shortcut / 手動）/ 改判者
- 右上: 「CSV 出力」/「印刷 · PDF 保存」buttons（skeleton, printable view は `window.print()` で簡略版）
- 空状態: 「その日のデータがありません」

---

## 9. /search — 検索（Tier 1）

- URL query 対応: `/search?q={キーワード}` (Shell の global 検索から遷移)
- 上部 2 tabs: **「学生から」/「日付から」**
- 「学生から」tab:
  - 学生検索 input（担当寮内の学生のみ検索可）
  - 結果: 選択した学生の総合 card（**6 block + 折りたたみ可**）:
    1. 点呼履歴（遅刻 / 欠席 / 時間内 の推移、月別サマリー）
    2. 減点明細（日別、累計 line chart）
    3. 体調報告履歴（提出日時 + 種別 + 補足）
    4. 欠席届履歴（提出日時 + 理由 + 承認状態）
    5. 申請履歴（全 type 統合: 外泊 / 帰国 / 帰省 / タクシー予約 の提出 / 承認 / 却下 全記録）
    6. 清掃・活動・宅配 等その他記録（Tier 2 skeleton）
- 「日付から」tab:
  - date picker
  - 結果: その日の全寮集計（点呼統計 / 欠席名簿 / 体調異常 / 申請処理件数）

---

## 10. /notifications — 通知中心（Tier 2 半実装, Q7 A）

- 4 つの数字 card:
  - 審査待ち申請 → click で /applications
  - 清掃審査 → /cleaning
  - 通報 → (skeleton, click で toast)
  - 警告リスト → /discipline (anchor to §4)
- Mock values: 3 / 2 / 1 / 4（Shell nav の "7" badge の内訳：3+2+1+1 or 何か合計）
- 下部: 最近の通知 activity feed（mock 5 件、タイムスタンプ付き）

---

## 11. その他 nav の Skeleton pages

### 11.1 /cleaning — 清掃確認（Tier 2 skeleton）
- 学生清掃写真審査 list mock 3 件（学生 + 日付 + 写真 placeholder + 承認/却下 button）
- 「開発中」tag

### 11.2 /info — お知らせ・バス（Tier 2 landing + 3 tabs）
- Tab 1 **お知らせ**: 学校通知 mock 3 件
- Tab 2 **行事カレンダー**: 行事 mock 3 件
- Tab 3 **バス時刻表**: 3 便 mock (7:00 / 12:00 / 18:00)

### 11.3 /community — 寮コミュニティ（Tier 2 landing + 5 tabs）
- **掲示板** mock 3 件
- **リクエスト曲** mock 5 件
- **忘れ物** 写真 card mock 3 件
- **匿名建議** mock 2 件
- **宅配通知** mock 3 件

---

## 12. 全局 UI 約束（Round 3 で固める）

### 12.1 ページ共通
- 空状態: 「まだデータがありません」+ 薄い icon
- 読み込み中: spinner
- エラー: 画面上部 red banner「サーバーとの通信に失敗しました」+ 再試行 button
- 確認 modal: 全ての「承認」「却下」「削除」前に「本当に {動作} しますか？」

### 12.2 Breadcrumb（topbar 下)
- /applications/outstay/詳細 → 「申請 > 外泊 > リュウ イヒ の申請」

### 12.3 Footer / DEMO marker
- 画面右下に small badge「DEMO」amber(warn), demo prototype であることを明示
- Footer 最下部: 「Tomoshibi v0.1.0-demo · 2026 AC 入試プロジェクト成果物」

---

## 13. ⭐ 実装技術 note（Claude Design へ）

- 既存の Ryō tokens + `round2/*.jsx` 設計言語を尊重。色、字体、spacing 一貫。
- 新規 component: `round3/select-teacher.jsx` / `round3/applications.jsx` / `round3/outstay-detail-modal.jsx` / `round3/discipline.jsx` / `round3/records.jsx` / `round3/search.jsx` / `round3/skeleton-page.jsx` / `round3/trend-chart.jsx` / `round3/global-search.jsx` — 適宜分割
- 既存 `round2/*.jsx` のうち修正必要なもの:
  - `theme.jsx` — late token 追加 + ROSTER 更新 + TIMEOUT / LATE_THRESHOLD constants
  - `shell.jsx` — logo 差し替え + 全局検索 + WS indicator + ログアウト button + 担当寮 badge
  - `login.jsx` — 2 field に改修（共用密码）
  - `roll-call-landing.jsx` — 最近 session 詳細 link + トレンド chart
  - `live.jsx` — late 色 + 予告バー + badge extend + 凡例 + 対象選択
  - `override-modal.jsx` — 欠席届 / 体調 / 履歴 の expand

- 実装後、**「Save as standalone HTML」で `DMSD Round 3 Prototype.html` として export**

---

## 14. 完成後のお願い

Round 3 完成後、以下 output:
1. 更新された standalone HTML（全機能 internalize 済）
2. 主要ページ screenshot (10 枚程度, 1366×1024):
   - /login
   - /login/select-teacher (通常 + 編集モード)
   - /roll-call ダッシュボード
   - /roll-call/live (全 4 状態 + late 含む seat variations が見えるもの)
   - /applications 外泊一覧
   - 外泊詳細 modal
   - /discipline
   - /records
   - /search
3. 日语 UI wording で「これは意訳が怪しい」と自分で気づいた箇所の list（itsuki が校正）

---

以上、よろしくお願いします。

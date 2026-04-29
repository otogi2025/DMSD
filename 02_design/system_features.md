# Tomoshibi システム機能設計 v0.1  <!-- VERSION_OK -->

> **系统对外名**：**Tomoshibi**（灯火）；DMSD 是项目/仓库代号。
> **本文版本**: v0.1（2026-04-23 首版）
> **本文作用**: **iOS App + 老师 Web + 后端 API 共用功能矩阵的唯一真值**。任何功能改动 → 先更新本文 → 再改实装。
> **上游参考**: `01_specs/rollcall/RollCall_Spec.md`（点呼业务规则）
> **配套文档**:
> - `02_design/hardware_design.md`（硬件）
> - `02_design/flow_design.md`（流程）
> - `03_dev/student_ios/IOS_DESIGN_LOG.md`（iOS 专属设计）
> - `03_dev/teacher_web/WEB_DESIGN_LOG.md`（Web 专属设计）
> **最后更新**: 2026-04-23 首版

---

## 0. 文档状态

| 章节 | 状态 | 来源 |
|---|---|---|
| §1 用途 + 同步规则 | ✅ 定稿 | 2026-04-23 itsuki 拍板「跨会话同步规则」 |
| §2 角色 | ✅ 定稿 | 2026-04-23 |
| §3 学号体系（6 桁 学年×組×番号）| ✅ 定稿 | 2026-04-23 itsuki 拍板 |
| §4 房间号管理 | 🟡 部分定稿 | 注册时学生填 ✅ / 一括分配 ⏳ 未来 |
| §5 学生改动履歴 | ✅ 定稿 | 2026-04-23 itsuki 拍板 |
| §6 機能マトリクス | 🟡 进行中 | 5 大块 skeleton + 增量补完 |
| §7 データモデル（中心 entity）| 🟡 部分定稿 | Student / Account / RoomAssignment ✅ / その他 ⏳ |
| §8 待拍板 | 🟡 進行中 | 通報 / コミュニティ拆分目的地 / リクエスト曲 朝晩 字段 |

---

## 1. 用途 + 同步规则

### 1.1 なぜこの文書がある

**問題**: iOS App / 老师 Web / 后端 API は別 repo + 別会話で実装される。
- iOS は `~/dev/TomoshibiiOSApp/`（独立 repo `otogi2025/Tomoshibi-iOS`、cloud agent 並走）
- Web は `~/dev/DMSD/03_dev/teacher_web/`（DMSD repo 内）
- 後端は `~/dev/DMSD/03_dev/backend/`（DMSD repo 内）

→ **共有機能**（账号体系 / 申請 / 通知 / コミュニティ）を片方で改動すると、もう片方が古いまま漂移する事故が必ず起きる。

**解決**: 本文 = 全実装層が参照する **single source of truth**。功能を改動する際は、まずここを改動 → 各実装の LOG に転記。

### 1.2 跨会话同步规则（CC + cloud agent 必読）

| 改動の種類 | 必須アクション |
|---|---|
| iOS 機能を変えた / 設計判断した | (1) `IOS_DESIGN_LOG.md` 时间线に記入 (2) **本文 §6 マトリクス対応行を更新** (3) 必要なら DMSD → Tomoshibi-iOS の `bin/sync-ios-refs.sh` を走らせる |
| Web 機能を変えた / 設計判断した | (1) `WEB_DESIGN_LOG.md` 时间线に記入 (2) **本文 §6 マトリクス対応行を更新** |
| Swift コードで機能挙動を変えた | (1) `Tomoshibi-iOS/STATUS.md` に記入 (2) **itsuki に通知 → 本文 + IOS_DESIGN_LOG への逆同期を促す** |
| 後端 API を加えた / 変えた | (1) **本文 §6 マトリクス API 列を更新** (2) `03_dev/backend/` 内の README / OpenAPI 草案を更新 |
| 新しい機能を提案した（未実装）| 本文 §6 に「⏳ 提案中」で行追加 → itsuki 拍板待ち |

### 1.3 sync-ios-refs.sh の役割

DMSD は source of truth。Tomoshibi-iOS の `refs/` は複製品（cloud agent はDMSD repo を取得不可なので物理コピー必要）。

DMSD 内 `bin/sync-ios-refs.sh` 1 コマンドで：
- `02_design/system_features.md` → `Tomoshibi-iOS/refs/`
- `03_dev/student_ios/IOS_DESIGN_LOG.md` → `Tomoshibi-iOS/refs/`
- `03_dev/student_ios/designs/Tomoshibi_iOS_PhaseB_v2.html` → `Tomoshibi-iOS/refs/`
- `03_dev/student_ios/designs/phaseB_src/` → `Tomoshibi-iOS/refs/`

→ コピー後、Tomoshibi-iOS で `git status` 表示 → itsuki が手動 commit / push（自動 push しない、安全のため）。

---

## 2. 角色

| 角色 | 用什么 | 主要機能 |
|---|---|---|
| 学生 | iOS / Android App | 自分のアカウント管理 / 点呼署名 / 申請 / コミュニティ参加 / 通知受信 |
| 寮監（老师 / 宿管）| 老师 Web | 学生アカウント管理 / 点呼判定 / 申請承認 / コミュニティ管理 / 規律・処分 / 房间号一括分配 |
| システム管理者（itsuki / 開発側）| Web 管理ページ（未実装）| 学校・学年構造設定 / 寮監アカウント発行 / システム設定 |

---

## 3. 学号体系（6 桁 学年×組×番号）

### 3.1 編碼規則

```
060218
├── 06 = 学年（2 桁、6 年制中高一貫対応）
├── 02 = 組  （2 桁、A=01 / B=02 — 当校は B 組まで、C 以降存在せず）
└── 18 = 番号（2 桁、班里通し番号、1〜99）
```

**学年マッピング**（当校 = 中高一貫 6 年制）:

| 学年 | コード |
|---|---|
| 中 1 | 01 |
| 中 2 | 02 |
| 中 3 | 03 |
| 高 1 | 04 |
| 高 2 | 05 |
| 高 3 | 06 |

### 3.2 ライフサイクル

- **新入生 注册時**: App 内で「学年 / 組 / 番号」を入力 → システムが 6 桁学号を **計算** して付与（"分配" ではなく deterministic 計算）
- **進級時（毎年 4 月）**: 学号変わる（例: 050218 → 060218）→ **学生本人が App 内で更新**（マイページ → 学生情報編集）→ **老师 Web の改动履歴に自動記録**
- **転校生（年度途中編入）**: 班里末番 + 1 を学生本人が手入力（例: 既存 18 番まで埋まっていれば 19 を入力）
- **卒業生**: 学号は履歴上残る（後端 PK は不変、§7 参照）

### 3.3 demo seed の 00 → 060218 へ移行

リュウ イヒ（itsuki 自身）の demo seed は:
- 旧: 番号 `00`（demo 専用 reserved）
- 新: 学号 `060218`（高 3 / B 組 / 18 番）
- 部屋: M101（既存維持）
- 性別: 女（M101 は男寮... → §4.2 参照、demo 上の例外として許容）

### 3.4 学年・組・番号 の存続

**ある**:
- データベース: `students.grade_code` (varchar(2)) / `students.class_code` (varchar(2)) / `students.seat_no` (varchar(2))
- 表示用 student_id は計算プロパティ: `grade_code || class_code || seat_no`

**ない**: 6 桁 学号自体を PK にしない（進級で変わるため）。PK は内部 `id`（UUID or auto-inc）。

---

## 4. 房间号管理

### 4.1 注册時（v1.0）

- 学生 iOS App 注册 step に「部屋番号」追加（手入力、フォーマット例 `M101` / `W203`）
- 老师 Web 学生アカウント管理ページで部屋番号確認可能
- **検証なし**（demo 段階）→ v1.1 で「老师側 ROSTER と照合 + 重複部屋警告」追加予定

### 4.2 一括分配ツール（v1.1 未来機能 ⏳）

**背景**: 部屋は **1 年 1 度入れ替え**。卒業 / 進級 / 新入で大規模再配置が発生 → 学生に毎回手入力させると老师側で照合不能。

**設計（draft）**:
- 老师 Web 「房间号一括分配」ページ（`teacher_web/round4` 想定）
- グリッド UI（房间×学生の drag & drop）
- 老师が割り当てを保存 → 後端が学生 App に push → 学生 App の房间号自動更新
- 学生 App 側: マイページ表示は read-only（一括分配適用後は編集不可）/ 分配前は編集可
- 改动履歴: 「老师 によって M101 → M205 に変更（2026-04-25 09:30）」を学生・老师両方の履歴に記録

**未確定**:
- ⏳ 部屋指定の単位（個室 or 部屋＋ベッド番号）
- ⏳ 学生の希望調査機能（事前に「相部屋希望」「個室希望」収集）
- ⏳ 男女寮の分配 UI 分離

---

## 5. 学生改动履歴（監査ログ）

### 5.1 ルール

**学生が App 内で行う情報変更は全て老师 Web から閲覧可能。**

対象フィールド（全変更を記録）:
- 学号構成（学年 / 組 / 番号）
- 房间号（学生編集時 + 老师一括分配時）
- メールアドレス
- 電話番号
- 氏名（誤入力修正用、要老师承認 ⏳ 未実装）
- パスワード（変更内容ではなく「変更が起きた事実」のみ、ハッシュは記録しない）
- アバター

### 5.2 表示位置

- **老师 Web**: 「学生アカウント管理」→ 学生詳細 modal → 「アクティビティ履歴」tab に時系列表示
- **学生 iOS**: マイページ → 「変更履歴」項目（自分の変更のみ閲覧可）

### 5.3 履歴 entry 形式

```json
{
  "timestamp": "2026-04-23T21:30:00+09:00",
  "actor": "self",                  // self | teacher | system
  "actor_name": "リュウ イヒ",
  "field": "grade_code",
  "old_value": "05",
  "new_value": "06",
  "context": "進級による更新"        // optional, 自由文
}
```

### 5.4 通知

- 老师編集 → 学生に push 通知（「あなたの部屋番号が M101 → M205 に変更されました」）
- 学生編集 → 老师に push 通知 OFF（履歴で確認）。但し例外: 学号変更は老师に通知（誤入力検知のため）

---

## 6. 機能マトリクス

凡例:
- ✅ = 実装済 / 〇 = 設計確定実装待ち / ⏳ = 設計中 / 🔴 = 未着手 / — = 該当機能なし
- (D) = Demo（4-28）対象 / (V1) = v1.0 リリース対象 / (V1.1+) = 将来拡張

### 6.1 アカウント

| 機能 | 学生 iOS | 老师 Web | 後端 API | Demo/V1 |
|---|---|---|---|---|
| 登録（4 step + 学号 step + 房间号 step）| 〇（IOS_DESIGN_LOG §3）| — | `POST /accounts` ⏳ | (D) |
| ログイン（学号 + password）| ✅ Auth Stub（Tomoshibi-iOS Agent A）| ✅ login.jsx | `POST /sessions` ⏳ | (D) |
| パスワード重置（自助なし）| 〇 注册画面に文言 | ✅ accounts.jsx 「パスワード初期化」 | `POST /accounts/:id/password-reset` ⏳ | (D) |
| ロック解除 | — | ✅ accounts.jsx 「ロック解除」 | `POST /accounts/:id/unlock` ⏳ | (D) |
| 学号構成編集（学年/組/番号）| 〇 マイページ | ✅ 閲覧 + 履歴表示 | `PATCH /accounts/:id` ⏳ | (D) |
| 房间号 学生編集 | 〇 マイページ | ✅ 閲覧 + 履歴表示 | `PATCH /accounts/:id` ⏳ | (D) |
| 房间号 一括分配（老师側）| ✅ 自動同期受信 | ⏳ V1.1 backlog | `POST /room-assignments/batch` ⏳ V1.1 | (V1.1+) |
| アカウント改动履歴 表示 | 〇 マイページ「変更履歴」| ✅ アクティビティ履歴 tab | `GET /accounts/:id/activity` ⏳ | (D) |

### 6.2 点呼

| 機能 | 学生 iOS | 老师 Web | 後端 API | Demo/V1 |
|---|---|---|---|---|
| NFC 签到（路径 A: 卡）| — | — | `POST /checkin?no=XX` ✅ demo_server | (D) |
| NFC 签到（路径 B: iPhone BTR + Universal Link）| ⏳ V1.0 | — | 同上 | (V1) |
| 点呼開始 / 終了 | — | ✅ live-roll-call.jsx | ⏳ | (D) |
| 自動遅刻判定（時刻過ぎ → 黄）| — | ✅ live-roll-call.jsx | ⏳ | (D) |
| 手動状態変更（緑/黄/赤切替）| — | ✅ override-modal.jsx | ⏳ | (D) |
| 顶部点呼 bar（学生側 status）| ✅ HomeView TopRollBar（Agent B）| — | `GET /checkin/status` ⏳ | (D) |

### 6.3 申請

| 機能 | 学生 iOS | 老师 Web | 後端 API | Demo/V1 |
|---|---|---|---|---|
| 外泊申請 提出 | 〇（Apply Agent D ⏳）| — | `POST /apply/outstay` ⏳ | (D) |
| 外泊申請 期限チェック（出発日週水曜 23:59 / 出発 48h 前 早い方）| 〇 提出時 block + 説明 | ✅ DeadlineSection 表示 | 後端で再検証必須 ⏳ | (D) |
| 申請承認 / 却下 / 質問 | ✅ 通知受信 | ✅ outstay-detail-modal.jsx | `PATCH /apply/:id/state` ⏳ | (D) |
| 申請履歴 | 〇 マイページ | ✅ applications.jsx | `GET /apply` ⏳ | (D) |
| 体調報告 / 欠席申請（点呼 bar 経由）| 〇 Home FeedbackSheet | ⏳ Web 表示 backlog | `POST /reports/health` ⏳ | (D) |

### 6.4 コミュニティ + フロント業務（拆分後）

**コミュニティ管理 = 学生発信の場**:

| 機能 | 学生 iOS | 老师 Web | 後端 API | Demo/V1 |
|---|---|---|---|---|
| 掲示板（投稿 + 閲覧 + 通報）| 〇 Community Agent C | ✅ CommunityPage 掲示板 tab | `GET/POST /posts` ⏳ | (D) |
| リクエスト曲（学生投稿、朝/晩 ⏳ 字段検討中、**古い順 表示**）| 〇 投稿 step 加 朝/晩 select | ✅ コミュニティ管理 リクエスト曲 tab、**ラベル「館内 BGM」→「寮内 BGM」修正必須** | `GET/POST /songs` ⏳ | (D) |
| 匿名建議 | 〇 投稿 | ✅ コミュニティ管理 匿名建議 tab | `GET/POST /suggestions` ⏳ | (D) |
| 通報機能（学生 → 帖子）| 〇 投稿に通報 button | ✅ 通報数表示 + 削除 / 通報解除 | `POST /posts/:id/flag` ⏳ | (D) — itsuki 拍板「保留」 |

**フロント業務 = 寮監前台代行 + 自動通知**（コミュニティから拆出）:

| 機能 | 学生 iOS | 老师 Web | 後端 API | Demo/V1 |
|---|---|---|---|---|
| 宅配通知（自動 push）| ✅ 通知受信 | ⏳ **新 nav「フロント業務」or 「通知」内 tab に移設**（移設先 itsuki 確認待ち、§8 (a)）| `POST /deliveries` ⏳ | (D) |
| 宅配 受取済 操作 | 〇 ボタン押下 | ✅ 状態変更 | `PATCH /deliveries/:id` ⏳ | (D) |
| 落とし物（忘れ物）登録・閲覧 | 〇 投稿 + 閲覧 | ⏳ **同上、移設先 itsuki 確認待ち** | `GET/POST /lost-items` ⏳ | (D) |

### 6.5 規律・処分

| 機能 | 学生 iOS | 老师 Web | 後端 API | Demo/V1 |
|---|---|---|---|---|
| 減点累計 表示 | ✅ Home 三色 badge（Agent B）+ MyPage 詳細（Agent E ⏳）| ✅ discipline.jsx | `GET /discipline/:id` ⏳ | (D) |
| 減点 内訳（遅刻/欠席）| 〇 MyPage | ✅ discipline.jsx 詳細 | 同上 | (D) |
| 罰掃当番 通知（≥4 点）| ✅ Home badge | ✅ discipline.jsx 罰掃リスト | `GET /penalties/cleaning` ⏳ | (D) |
| 禁足 通知（≥8 点）| 〇 マイページ | ✅ 罰則 list | `GET /penalties/grounding` ⏳ | (D) |
| パスワードロック → 老师通報 | 〇 ロック画面 | ✅ accounts.jsx 「ロック中」filter | 自動連携 ⏳ | (D) |

### 6.6 通知

| 機能 | 学生 iOS | 老师 Web | 後端 API | Demo/V1 |
|---|---|---|---|---|
| お知らせ閲覧 | 〇 Home Notifications（Agent C）| ✅ pages-records-search-etc InfoPage | `GET /notices` ⏳ | (D) |
| お知らせ投稿（老师 → 学生）| — | ✅ ComposeNoticeModal | `POST /notices` ⏳ | (D) |
| バス時刻表 閲覧 | 〇 マイページ / Home 専用 tab | ✅ お知らせ・バス 内「バス時刻表」tab | `GET /bus-schedule/posts` ⏳ | (D) |
| バス時刻表 管理（CRUD）| — | ⏳ 新規 Post 作成 + Event + 時刻行 drag & drop 並び替え（サンプル: `06_assets/real_samples/bus_notice_2026-03-22_特別運行便.md`）| `POST/PATCH/DELETE /bus-schedule/*` ⏳ | (V1) |
| バス乗車名簿（寮生事前チェック）| 〇 マイページ | ✅ 乗車簿確認 + 調整 | `POST /bus-schedule/:event/riders` ⏳ | (V1) |

---

## 7. データモデル（中心 entity 抜粋）

### 7.1 Student / Account

```
students                                    -- 学生本体（不変 PK）
├── id              UUID PK                 -- 内部不変識別子
├── grade_code      VARCHAR(2)              -- '01'-'06' (中1-高3)
├── class_code      VARCHAR(2)              -- '01' (A) | '02' (B)
├── seat_no         VARCHAR(2)              -- '01'-'99'
├── student_no      GENERATED ALWAYS AS (grade_code || class_code || seat_no) STORED
├── name            TEXT
├── name_kana       TEXT
├── birthday        DATE
├── gender          ENUM('male','female')
├── category        ENUM('一般寮生','サッカー部')
├── room_no         VARCHAR(8)              -- 'M101' / 'W203' etc
├── dorm            ENUM('men','women')
├── email           TEXT
├── phone           TEXT
├── avatar_url      TEXT
├── registered_at   TIMESTAMPTZ
└── status          ENUM('active','locked','graduated')

accounts                                    -- 認証情報（students と 1:1）
├── id              UUID PK
├── student_id      UUID FK → students.id
├── password_hash   TEXT
├── failed_count    INT DEFAULT 0
├── locked_until    TIMESTAMPTZ NULL        -- ロック解除予定時刻
├── last_login_at   TIMESTAMPTZ
└── created_at      TIMESTAMPTZ

account_activity_log                        -- §5 改动履歴
├── id              UUID PK
├── student_id      UUID FK → students.id
├── timestamp       TIMESTAMPTZ
├── actor           ENUM('self','teacher','system')
├── actor_name      TEXT
├── field           TEXT                    -- 'grade_code' / 'room_no' / 'email' etc
├── old_value       TEXT
├── new_value       TEXT
└── context         TEXT NULL
```

### 7.2 RoomAssignment（一括分配 v1.1）

```
room_assignments                            -- 年度別の部屋割り
├── id              UUID PK
├── academic_year   INT                     -- 2026 / 2027 ...
├── student_id      UUID FK → students.id
├── room_no         VARCHAR(8)
├── assigned_by     UUID FK → teachers.id
├── assigned_at     TIMESTAMPTZ
└── effective_from  DATE                    -- 適用開始日
```

### 7.3 その他 entity（追記予定）

⏳ Posts / Songs / Suggestions / Deliveries / LostItems / Notices / Penalties / Apply / RollCallSession / CheckIn

---

## 8. 待拍板事項

| ID | 項目 | 提案 | 状態 |
|---|---|---|---|
| (a) | コミュニティ から 宅配通知 + 忘れ物 を移設する先 | 案 1: 新 nav「フロント業務」 / 案 2: 既存「通知」内 tab | itsuki 拍板待ち |
| (b) | リクエスト曲 朝/晩 字段の追加 | iOS 投稿 step に select 追加、Web 側で枠 filter | itsuki 拍板待ち（itsuki 「3 古い順」回答済 = 排序確定 / 朝晩字段 未明示） |
| (c) | 罰則 config 化（遅刻 0.5 / 欠席 1 / 月 4 罰掃 / 月 8 禁足）| `discipline_config` テーブル化、上線前に老师と協議 | 上線前に老师と相談 |
| (d) | 学号変更時の老师承認要否 | 案 1: 学生自由変更 + 履歴 / 案 2: 学生申請 → 老师承認 | itsuki 拍板待ち |
| (e) | 房间号 一括分配の単位 | 個室 / 部屋＋ベッド番号 | V1.1 設計時拍板 |

---

## 9. 改訂履歴

| 日付 | 改訂内容 | 担当 |
|---|---|---|
| 2026-04-23 | v0.1 首版（学号体系 + 房间号 + 改动履歴 + 機能マトリクス + データモデル中心 entity）| [Mac-demo-sprint] CC |

---

**END** — 機能改動時はまずこの文書を更新してから実装に入ること。

# Tomoshibi — App Store Connect 元数据起草

> itsuki 在 App Store Connect（appstoreconnect.apple.com）创建 app + 提交审核时，复制粘贴下面的内容到对应字段。
> 主语言 = 日本語。所有文案以日语为正本，括号内的中文是给 itsuki 自己的注释。

---

## 1. App 基本信息

| ASC 字段 | 内容 |
|---|---|
| Name (App Store 显示名) | `Tomoshibi` <br> ⚠️ 提交前 itsuki 必须先在 App Store iOS 端搜索「Tomoshibi」「ともしび」「灯火」确认未被占用 |
| Subtitle (副标题，最多 30 字) | `寮の点呼デジタル化` |
| Bundle ID | `com.itsuki.tomoshibi` |
| SKU (内部识别码，不公开) | `TOMOSHIBI-IOS-V1` |
| Primary Language | 日本語 |
| Category | Primary: `Education` / Secondary: `Lifestyle` |
| Age Rating | `4+` |
| Price | Free / 免費 |
| Availability | All countries / 全世界 |

---

## 2. 描述（Description，最多 4000 字符，日语）

```
Tomoshibi は学生寮の点呼を完全デジタル化するアプリです。

紙の出席簿を NFC タッチに置き換え、外泊・帰省・帰国の申請も全部スマホで完結。
寮監・寮務・国際交流・学習担当などの先生による多段階承認も、すべてアプリ内で見える化されます。

【主な機能】

■ デジタル点呼
NFC カードを点呼機にかざすだけで自動的に出席が記録されます。遅刻・欠席の判定も自動化、面倒な紙の確認が不要になります。

■ 外泊・帰省・帰国 申請
外出先・期間・連絡先を入力すれば、関連する先生全員に申請が回り、承認状況をリアルタイムで確認できます。

■ お知らせ
寮全体・特定の学年・特定の生徒に向けた先生からのお知らせを受け取り、必要に応じて返信もできます。

■ 体調報告・掃除提出履歴
体調不良や掃除当番の提出履歴を一元管理。減点の理由も透明化されます。

■ 個人情報・履歴
自分の点呼出席率・減点履歴・申請履歴を一画面で確認。プロフィール情報の編集も可能です。

【こんな方におすすめ】

- 学生寮で生活している中学生・高校生・大学生
- 紙の出席簿の管理に時間を取られている寮関係者
- 申請書の往復で時間を浪費したくない学生

【ご注意】

- 本アプリは寮で発行される登録コード（先生から取得）が必要です。コードは 5 分間有効、教師が iPad の管理画面で発行します。
- NFC 機能は対応する iPhone（iPhone 7 以降）で動作します。
- 一部の機能（点呼参加、外泊申請）は寮側のシステム連携が必要です。寮の運用ポリシーに従ってご利用ください。

【お問い合わせ】

不具合や機能改善のご要望は、設定画面から直接お送りいただけます。

【プライバシー】

本アプリは寮の点呼・申請・履歴管理のために氏名・学籍番号・寮室番号などの最小限の個人情報を取得します。詳細はプライバシーポリシーをご確認ください。
```

---

## 3. キーワード（Keywords，最多 100 字符，半角逗号分隔）

```
寮,点呼,出席,寄宿舎,宿舎,学生,NFC,申請,外泊,帰省,デジタル化,寮監,寮務,出席簿
```

（中文备注：覆盖宿舍 / 点呼 / 学生 / NFC 申请等核心词。如撞名，可加学校名增加区分度。）

---

## 4. URL 字段

| 字段 | 值 | 备注 |
|---|---|---|
| Support URL | `https://otogi2025.github.io/tomoshibi-pages/support` | ✅ 已部署（2026-05-08）|
| Marketing URL（可选） | （留空 OK） | 没有官网就不填 |
| Privacy Policy URL | `https://otogi2025.github.io/tomoshibi-pages/privacy_policy` | ✅ 已部署（2026-05-08）|

---

## 5. App Privacy（数据收集声明，ASC 表格逐条填）

| データの種類 | 収集する? | 用途 | ユーザーに紐付く? | トラッキング目的? |
|---|---|---|---|---|
| 氏名（Name） | ✅ | App Functionality（出席簿表示） | はい | いいえ |
| メールアドレス（Email Address） | ✅（任意） | App Functionality（パスワード復旧） | はい | いいえ |
| 電話番号（Phone Number） | ✅（任意） | App Functionality（緊急連絡） | はい | いいえ |
| 学籍番号 / 学生 ID（Other User Contact Info） | ✅ | App Functionality（点呼識別） | はい | いいえ |
| 寮の部屋番号（Coarse Location 相当 — 「Other Data Types」へ手動追加可） | ✅ | App Functionality（部屋ごと管理） | はい | いいえ |
| 出席履歴（Other Data Types） | ✅ | App Functionality（履歴表示・処分判定） | はい | いいえ |
| 端末識別子（Device ID） | ❌ | — | — | — |
| 位置情報（GPS） | ❌ | — | — | — |
| 写真・カメラ | ❌ | — | — | — |
| Cookie / 広告識別子 | ❌ | — | — | — |
| クラッシュデータ / Diagnostics | ❌（v1.0 段階） | — | — | — |

注：すべて「Tracking なし」「サードパーティ共有なし」。

---

## 6. App Review Information（提交时填，给 Apple 审核员）

### Sign-In Required: ✅ Yes

### Demo Account（审核员用）
```
学籍番号: 060199
パスワード: Reviewer-2026
登録コード（注册流程跑通时用）: 999999
```

### Notes（双语 — 日本語主 + English 副）

```
[日本語]

ご審査ありがとうございます。本アプリは寮生活デジタル化を目的とした
学生向けアプリです。以下の点をお伝えします：

1) ログイン方法
   - 起動 → 自動的に Login 画面に遷移します
   - 学籍番号 060199 / パスワード Reviewer-2026 でログインしてください
   - これで Home / 申請 / マイページ など全機能をテスト可能です

2) 新規登録フロー（任意で確認したい場合）
   - Login 画面の「新規登録」リンクから 6 ステップの登録フローへ
   - Step 5 で登録コード「999999」を入力（reviewer 専用、長期有効）
   - 学籍番号は重複しないものに設定してください
     （060199 はすでに reviewer アカウントが使用中）

3) NFC 機能について
   - 中央の点呼ボタンから NFC 読み取りが起動します
   - 専用の NFC カード（NTAG215）が必要です。Apple 側に物理カードが
     ない場合、任意の NFC タグでも読み取り UI は表示されます
     （カードが認証されない場合はエラー表示、これが正常動作）
   - 現バージョンでは点呼機との実連携は未稼働ですが、UI フローと
     エラー処理は完全実装されています

4) アカウント削除
   - マイページ → 設定 → 「アカウントを削除」から実行可能
   - Apple Guideline 5.1.1(v) 準拠

5) 利用想定
   - 本アプリは学生寮の点呼・申請管理を目的としており、寮との連携を
     前提とします。一般ユーザーは登録コードがなければ利用できません
     が、これは部屋・寮室番号などのプライバシー保護のためです

不具合がございましたら otogi2025@gmail.com までお気軽にご連絡ください。

[English]

Thanks for reviewing. Tomoshibi is a digital roll-call app for student dormitories.
A few notes:

1) Login: tap-launch → Login screen. Use student ID 060199 / password Reviewer-2026
   to access all features (Home / Applications / MyPage).

2) Registration flow (optional): "新規登録" link on Login screen → 6-step flow.
   Use registration code "999999" at step 5 (reviewer-only, long-lived).
   Pick a unique student ID different from 060199.

3) NFC: Center button triggers NFC reader. Requires NTAG215 cards (not shipped to
   Apple). Any NFC tag will trigger the read UI; unauthenticated cards show an
   error (expected behavior). NFC hardware integration is staged for v1.1.

4) Account deletion: MyPage → Settings → "アカウントを削除" (per 5.1.1(v)).

5) Usage: dormitory roll-call & application management. Registration codes
   gate sign-up to protect room number / dormitory privacy.

Reach me at otogi2025@gmail.com for any issue.
```

---

## 7. Screenshots 要件

| デバイス | サイズ | 最低枚数 | 推奨内容 |
|---|---|---|---|
| iPhone 6.9" (16/17 Pro Max) | 1290 × 2796 | 3 | Login → Home → Apply List |
| iPhone 6.5" (XS Max / 11 Pro Max) | 1284 × 2778 | （6.9 から自動派生可） | 同上 |
| iPad Pro 12.9" 第 6 世代 | 2048 × 2732 | 0（iPad 対応していない場合） | iPhone only なので不要 |

**取り方**：
1. Xcode → iPhone 16 Pro Max simulator で Tomoshibi を起動
2. login → reviewer 凭证でログイン
3. 各画面で `Cmd+S`（File → New Screen Shot）
4. simulator は自動で `~/Desktop` に PNG 保存
5. ASC へ drag & drop でアップロード

---

## 8. What's New in This Version

```
初回リリース版です。寮生活をデジタル化する Tomoshibi の最初のバージョンとして、
点呼・申請・お知らせ・履歴管理など中核機能を一通り提供します。

- NFC タッチ点呼（基盤実装）
- 外泊・帰省・帰国 申請フロー
- お知らせ受信 + 返信
- 出席履歴・減点履歴・申請履歴の一元管理
- 個人情報の編集

次回バージョン（1.1.0）以降で点呼機との実連携を稼働予定です。
```

---

## 9. App Information の他フィールド

| フィールド | 値 |
|---|---|
| Copyright | `2026 itsuki / DMSD Project` |
| Trade Representative Contact Information | itsuki / otogi2025@gmail.com / Japan |
| Contact Information for App Review | 上記と同じ |

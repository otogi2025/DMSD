# Tomoshibi プライバシーポリシー / Privacy Policy

最終更新日: 2026 年 5 月 7 日 / Last Updated: May 7, 2026

---

## 日本語版

### 1. 取得する情報

Tomoshibi（以下「本アプリ」）は、寮生活の点呼・申請・履歴管理機能を提供するために、以下の最小限の個人情報を取得します。

| 種別 | 用途 |
|---|---|
| 氏名（フリガナ） | 出席簿・申請書の表示 |
| 学籍番号（学年 + 組 + 出席番号 = 6 桁） | 個人識別・点呼判定 |
| 寮室番号（M101 / W203 など） | 部屋ごとの点呼集計 |
| 寮タイプ（男寮 / 女寮 / 国際寮） | 役職別承認チェーン |
| 留学生フラグ | 国際交流部承認チェーンの分岐 |
| メールアドレス（任意） | パスワード再発行通知 |
| 電話番号（任意） | 緊急連絡 |
| 出席履歴 / 減点履歴 / 申請履歴 | アプリ内の履歴表示・処分判定 |
| NFC カード ID（v1.1 以降） | 点呼機と紐付けて出席記録 |

### 2. 利用目的

取得した情報は以下の目的でのみ使用します：

- 寮の点呼・出席記録
- 外泊・帰省・帰国などの申請承認フロー
- 寮監・寮務・国際交流・学習担当などの先生による多段階承認の見える化
- 履歴情報の表示（個人情報・点呼・減点・申請）
- パスワード再発行などのアカウント管理

### 3. 第三者提供

本アプリは利用者の個人情報を**第三者に提供しません**。広告 SDK・分析 SDK の類は搭載しておりません。

### 4. データの保管

- データは寮側が管理する Backend サーバ（日本国内、TLS 通信）に保存されます
- データベースは PostgreSQL、暗号化は OS / インフラレイヤーで実施します
- 通信は HTTPS（Let's Encrypt 証明書）で暗号化されます

### 5. データの保管期間

- 在籍中は保管。卒業・退寮・アカウント削除後 1 年で物理削除します
- 監査要件で必要な点呼ログは匿名化した上で 5 年間保管する場合があります

### 6. ユーザーの権利（GDPR / 日本個人情報保護法対応）

利用者は以下の権利を有します：

- **閲覧権**：マイページから自身の全データを閲覧できます
- **修正権**：マイページの編集機能から氏名・連絡先などを修正できます
- **削除権**：マイページ → 設定 → 「アカウントを削除」から本人で削除可能
- **撤回権**：アカウント削除はいつでも可能です

### 7. アカウント削除

App Store Review Guideline 5.1.1(v) に準拠し、アプリ内からアカウント削除が可能です。
削除後は学生情報のステータスが「deleted」となり、ログイン・API 呼び出しがすべて拒否されます。

### 8. クッキー / トラッキング

本アプリは：
- **クッキーを使用しません**
- **広告識別子（IDFA）を使用しません**
- **App Tracking Transparency（ATT）対象の追跡を一切行いません**
- **第三者の分析ツールを使用しません**

### 9. お子様のプライバシー

本アプリは中学生・高校生・大学生など 13 歳以上の学生が利用することを想定しています。13 歳未満の方の利用は想定しておりません。

### 10. プライバシーポリシーの変更

本ポリシーは予告なく変更される場合があります。重要な変更があった場合はアプリ内のお知らせで告知します。

### 11. お問い合わせ

プライバシーに関するご質問・データ削除のご依頼は以下までご連絡ください：

- メール: otogi2025@gmail.com
- 開発者: itsuki（伊月）

---

## English Version

### 1. Information We Collect

Tomoshibi collects the following minimum personal information to provide dormitory roll-call, application, and history management features:

| Type | Purpose |
|---|---|
| Name (with Kana) | Display in roll-call / application forms |
| Student ID (grade + class + seat = 6 digits) | Identification & roll-call detection |
| Dorm Room Number | Per-room roll-call aggregation |
| Dorm Type (M / W / I) | Routing of approval chains |
| International Student Flag | International office approval branching |
| Email Address (optional) | Password recovery notifications |
| Phone Number (optional) | Emergency contact |
| Attendance / Discipline / Application History | In-app history display |
| NFC Card ID (v1.1+) | Tag-based attendance recording |

### 2. How We Use Information

Collected data is used only for:
- Dormitory roll-call and attendance recording
- Application approval flow (overnight stay / home leave / international travel)
- Multi-stage approval visibility (warden / dormitory office / international office / study supervisor)
- History display (personal info / roll-call / discipline / applications)
- Account management (password recovery, etc.)

### 3. Third-Party Sharing

We do **NOT** share your personal information with any third parties. We do **NOT** include any advertising SDKs or analytics SDKs.

### 4. Data Storage

- Data is stored on dormitory-managed backend servers (located in Japan, TLS encrypted)
- Database: PostgreSQL with OS / infrastructure-level encryption
- Communication: HTTPS (Let's Encrypt certificates)

### 5. Data Retention

- Retained during enrollment
- Physically deleted 1 year after graduation / dorm exit / account deletion
- Anonymized roll-call logs may be retained for 5 years for audit purposes

### 6. Your Rights (GDPR / Japan PIPA Compliant)

You have the following rights:
- **Access**: View all your data from MyPage
- **Correction**: Edit name / contact info etc. from MyPage edit feature
- **Deletion**: Delete account from MyPage → Settings → "Delete Account"
- **Withdrawal**: Account deletion is available at any time

### 7. Account Deletion

In compliance with App Store Review Guideline 5.1.1(v), account deletion is available within the app itself. Upon deletion, the student record status becomes "deleted", rejecting all subsequent logins and API calls.

### 8. Cookies / Tracking

This app:
- Does NOT use cookies
- Does NOT use advertising identifiers (IDFA)
- Does NOT perform any App Tracking Transparency (ATT) covered tracking
- Does NOT use third-party analytics

### 9. Children's Privacy

This app is intended for students 13 years or older (junior high / high school / university). Use by children under 13 is not anticipated.

### 10. Changes to This Policy

This policy may change without prior notice. Significant changes will be announced via in-app notifications.

### 11. Contact

For privacy questions or data deletion requests:

- Email: otogi2025@gmail.com
- Developer: itsuki

---

> Note for itsuki: 把这个文件转成 HTML（or 用 Markdown 直接 GH Pages 渲染），URL 填到 ASC 的「Privacy Policy URL」字段。
> GH Pages 部署：在 GitHub 创建一个 public 仓库（如 `itsuki-cn/tomoshibi-pages`），把这个 .md 推上去，Settings → Pages 启用 → URL 即得。

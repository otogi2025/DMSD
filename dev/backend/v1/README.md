# dev/backend/v1/

**v1.0 正式版后端 — P0 範囲 实装中** (2026-04-30 由 [Mac-会话B] 起手)。

---

## ⭐ 当前状态

**P0 部分** (出寮届 + メール + 食堂 Excel) 起手版完成:

| エンドポイント | 用途 | 状態 |
|---|---|---|
| `POST /api/v1/sessions/student` | 学生 login | ✅ |
| `POST /api/v1/sessions/teacher` | 教师 login | ✅ |
| `POST /api/v1/applications` | 出寮届 提出 (#2 + #6 メール) | ✅ |
| `GET  /api/v1/applications/mine` | 自分の履歴 | ✅ |
| `GET  /api/v1/applications/{id}` | #5 承认状态查询 | ✅ |
| `GET  /api/v1/meals/calc` | #7 食数計算 (JSON) | ✅ |
| `GET  /api/v1/meals/export` | #7 食数 Excel 导出 | ✅ |
| `POST /api/v1/notifications/test` | SendGrid smoke | ✅ |

**追加实装** (2026-05-12 校准):
- 役职 承认 (#10-#13) — `applications.py:394-443` ✅
- 学習出席 — `study.py` 已挂載 + alembic c3d4e5f6a7b8 加 period 字段 ✅
- 点呼 — `rollcall.py` 已挂載 ⚠️（NFC 防作弊 card_uid 未真接 — 见 SOP Bug B4）
- 公告 — `announcements.py` ✅
- 学生注册码 — `admin_registration_code.py` ✅（5 分钟有效，App Store 上架对策）
- 教师管理 — `teachers.py` ✅

**仍 ⏳**: 巴士 / 行事 / 指導履歴 / 事案 / 食堂他データ / WebSocket + Redis / refresh_token rotation / 整点 session minute-5 bug。

権威設計文書 → `../BACKEND_DESIGN_LOG.md` (P0 範囲は §2.1)。

---

## ⚡ 起動 (5 分で動かす)

```bash
cd dev/backend/v1

# 依存
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 設定 (SENDGRID_API_KEY を本物にすると 実 SendGrid に送信)
cp .env.example .env

# DB 初期化 + ダミーデータ投入
python -m seed

# サーバ起動
python -m app.main
# → http://localhost:8000/docs で OpenAPI UI
```

---

## 🧪 テスト

```bash
pytest -v
```

**カバー**:
- 役职 chain (D4 实物表) — 留学生外泊 = 5 行 / 一般外泊 = 3 行 / 帰省・帰国 暫定 chain
- POST /applications + メール トリガー (notification_log 行作成確認)
- GET /applications/{id} (学生本人 / 他人 403 / 留学生帰省 chain 暫定)
- GET /meals/calc + /meals/export (Excel バイナリ妥当性)
- 認証エラーパス (401 / 403 / 422)
- evidence pending な chain は `X-Approval-Chain-Provisional: true` header

---

## 🛠 SendGrid を実機接続する

1. SendGrid アカウント作成 → API Key (Mail Send) 発行
2. Sender Verification (single sender or domain)
3. `.env` に:
   ```
   SENDGRID_API_KEY=SG.xxxxxxx
   EMAIL_FROM=verified-sender@your-domain.jp
   ```
4. smoke test:
   ```bash
   # 1. 教师 login で token 取得
   TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/sessions/teacher \
     -H 'Content-Type: application/json' \
     -d '{"login_id":"ryomu_kachou","password":"tomoshibi-dev-2026"}' \
     | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

   # 2. テストメール送信
   curl -X POST http://localhost:8000/api/v1/notifications/test \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"to":"itsuki@your-mail.jp","subject":"smoke","body_text":"テスト"}'
   ```

---

## 📁 構成

```
v1/
├── app/
│   ├── main.py           # FastAPI app (lifespan + routers 登録)
│   ├── config.py         # 設定 (BaseSettings)
│   ├── database.py       # SQLAlchemy engine + Session
│   ├── deps.py           # 依存注入 (current_student / current_teacher)
│   ├── security.py       # JWT + bcrypt
│   ├── models.py         # SQLAlchemy 2.x ORM (P0 8 表)
│   ├── schemas.py        # Pydantic v2 (届 3 種 discriminator)
│   ├── routers/
│   │   ├── auth.py            # 学生/教师 login
│   │   ├── applications.py    # #2 #5 #6
│   │   ├── meals.py           # #7
│   │   └── notifications.py   # SendGrid smoke
│   └── services/
│       ├── approval_chain.py  # D4 chain 生成 (provisional flag)
│       ├── email.py           # SendGrid + notification_log
│       └── meals.py           # 食数計算 + openpyxl Excel
├── tests/
│   ├── conftest.py
│   └── test_smoke.py     # 17 ケース (chain / api / Excel)
├── seed.py               # 役职 7 種網羅 + 担任 + 学生 (留学生 + 一般)
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚠️ 既知の制約 (P0 範囲外, 後続会話で実装)

| ID | 項目 | 移送先 |
|---|---|---|
| - | Alembic migration | P0 後 (今は `Base.metadata.create_all`) |
| - | async SQLAlchemy | P0 後 (今は同期、code 読みやすさ優先) |
| - | Refresh token rotation | P1 |
| - | 学生 lock_level 升級 (連続失敗 3 → 30s ...) | P1 |
| - | 役职 承認・拒否 (#10-#13) `POST /applications/:id/approvals` | P1 (会話 続) |
| - | コメント追加 (#13 杭田弱点) | P1 |
| D4 evidence | 帰省 / 帰国 実物表 ×4 → chain 生成ロジック調整 | itsuki が次回老師に会った時に持ち帰る |
| 食事時刻 | 朝 7:00 / 昼 12:00 / 夕 18:00 (暫定) | itsuki 確認後 services/meals.py 定数調整 |

evidence 入手次第、`app/services/approval_chain.py` の `EXTERNAL_ROLES_BY_KIND` と `PROVISIONAL_CHAINS` を更新。

---

## 📚 関連ドキュメント

- 権威設計 → `../BACKEND_DESIGN_LOG.md`
- 38 条要件（老師フィードバック backlog）→ 内部管理ドキュメント（公開リポジトリ対象外）
- 実物表 evidence → `../BACKEND_DESIGN_LOG.md §10 D4` + `system_features.md §7.2.2`
- demo 版 (4-28 管理員 demo, ロック中) → `../demo/`

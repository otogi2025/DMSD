# VPS 部署 + Reviewer Notes 文案（5-08 demo seed 修复后）

> 本文件 = 一次性操作清单，部署完毕可删 / 移到归档。

---

## Step 1 — Mac 端：把修复 rsync 到 fork（保留 fork 的 VPS 部署专用文件）

```bash
cd ~/dev/DMSD

# 1.1 同步 app/ 整个目录（含 routers + models + schemas）
rsync -avz --delete \
  03_dev/backend/v1/app/ \
  ~/dev/Tomoshibi-AppStore/backend/app/

# 1.2 同步新 migration 文件
cp 03_dev/backend/v1/alembic/versions/f6a7b8c9d0e1_add_demo_reviewer_flags.py \
   ~/dev/Tomoshibi-AppStore/backend/alembic/versions/

# 1.3 同步 seed.py
cp 03_dev/backend/v1/seed.py \
   ~/dev/Tomoshibi-AppStore/backend/seed.py

# 1.4 同步 test（部署不用但带去无害）
cp 03_dev/backend/v1/tests/test_demo_reviewer.py \
   ~/dev/Tomoshibi-AppStore/backend/tests/
```

**注意**：fork 里的 `Caddyfile` / `Dockerfile` / `docker-compose.yml` / `DEPLOY.md` 保持不动 — 这些是 VPS 部署专用，主项目还没接进来。Task 7（v1.0.1 时）再合回主项目。

---

## Step 2 — Mac → VPS rsync

```bash
# 2.1 推到 VPS
rsync -avz --delete \
  ~/dev/Tomoshibi-AppStore/backend/app/ \
  itsuki@34.85.74.70:~/tomoshibi-backend/app/

rsync -avz \
  ~/dev/Tomoshibi-AppStore/backend/alembic/versions/f6a7b8c9d0e1_add_demo_reviewer_flags.py \
  ~/dev/Tomoshibi-AppStore/backend/seed.py \
  itsuki@34.85.74.70:~/tomoshibi-backend/
```

**注意**：第二条 rsync 把 migration 和 seed.py 直接 push — migration 进入 alembic/versions 目录，seed.py 覆盖根目录。需要分两条命令避免目标路径混乱：

```bash
# 改用更明确的两条
rsync -avz \
  ~/dev/Tomoshibi-AppStore/backend/alembic/versions/f6a7b8c9d0e1_add_demo_reviewer_flags.py \
  itsuki@34.85.74.70:~/tomoshibi-backend/alembic/versions/

rsync -avz \
  ~/dev/Tomoshibi-AppStore/backend/seed.py \
  itsuki@34.85.74.70:~/tomoshibi-backend/seed.py
```

---

## Step 3 — VPS 端：部署 + reseed

```bash
ssh itsuki@34.85.74.70
cd tomoshibi-backend

# 3.1 设 admin 密码 env（强密码，不进 git）
export ADMIN_INITIAL_PASSWORD="$(openssl rand -base64 24)"
echo "🔑 admin 初始密码: $ADMIN_INITIAL_PASSWORD"
# ⚠️ 把这个密码立刻存进 1Password — 终端关掉就找不回了

# 3.2 跑新 migration（自动 invalidate 旧 999999 行）
docker compose exec -e ADMIN_INITIAL_PASSWORD="$ADMIN_INITIAL_PASSWORD" \
  api alembic upgrade head

# 3.3 reseed（production 模式 — 创建 999999 学号 + is_reviewer=True 注册码）
docker compose exec -e ADMIN_INITIAL_PASSWORD="$ADMIN_INITIAL_PASSWORD" \
  -e APP_ENV=production \
  api python -m seed

# 3.4 重启 api 让新代码生效
docker compose restart api
```

---

## Step 4 — VPS 端：验证

```bash
# 4.1 看 999999 注册码状态（应是 is_reviewer=True / invalidated_at=NULL）
docker compose exec -T postgres psql -U tomoshibi -d tomoshibi -c \
  "SELECT code, is_reviewer, invalidated_at, expires_at FROM student_registration_codes;"

# 期望：
#   code   | is_reviewer | invalidated_at |     expires_at
# ---------+-------------+----------------+---------------------
#  999999  | f           | (timestamp)    | 2030-01-01    ← fork 旧行（被 migration 作废）
#  999999  | t           | (NULL)         | 2099-01-01    ← 新 prod seed 行
# (2 rows)

# 4.2 看 students（应有 060199 旧 + 999999 新）
docker compose exec -T postgres psql -U tomoshibi -d tomoshibi -c \
  "SELECT grade_code||class_code||seat_no AS student_no, name, is_demo FROM students;"

# 期望：
#  student_no |     name     | is_demo
# ------------+--------------+---------
#  060199     | App Reviewer | f       ← fork 旧行（is_demo=False, 因为 migration 不能猜）
#  999999     | App Reviewer | t       ← 新 prod seed
# (2 rows)
```

---

## Step 5 — VPS 端：删旧 reviewer 学生（060199 fork 部署遗留垃圾）

```bash
docker compose exec -T postgres psql -U tomoshibi -d tomoshibi <<'EOF'
DELETE FROM accounts WHERE student_id IN (
    SELECT id FROM students WHERE grade_code='06' AND class_code='01' AND seat_no='99'
);
DELETE FROM students WHERE grade_code='06' AND class_code='01' AND seat_no='99';
EOF
```

---

## Step 6 — VPS 端：iOS 测试（itsuki 在手机或模拟器上）

1. login 输 `999999` + `Tomoshibi-Reviewer-2026!` → 应进 home 看到空数据
2. logout → 注册流程随便填到 Step5 → 输 `999999` → 应卡在 STUDENT_NO_TAKEN（学号已注册）
3. logout → 注册流程换学号到 Step5 → 输 `999999` → 应注册成功（用了 reviewer 码）
4. 老师 web 后台 login `admin` / `<env 密码>` → 学生列表不应看到 999999 reviewer

---

## Apple Reviewer Notes 文案（提交时填）

**英文版**：

```
Demo Account (no registration needed):

Student ID: 999999
Password: Tomoshibi-Reviewer-2026!

Tap "Login" on first screen → enter the credentials above → see Home screen.

Note: This is a private dormitory roll-call app. Real registration requires
a code issued by the dormitory teacher. The demo account above bypasses
that gate so you can test all features.

If you encounter any issues, please contact: otogi2025@gmail.com
```

**日本語版**（双语模式 — 跟 fork METADATA §6 风格）：

```
デモアカウント（登録不要）:

学籍番号: 999999
パスワード: Tomoshibi-Reviewer-2026!

最初の画面で「ログイン」をタップ → 上記の認証情報を入力 → ホーム画面が表示されます。

備考: これは寮の点呼用の私的な app です。通常の新規登録には寮の教師が発行する
コードが必要ですが、上記のデモアカウントはそのゲートをバイパスして
全ての機能をテストできるようにしてあります。

問題が発生した場合: otogi2025@gmail.com
```

**绝不写入 Reviewer Notes**：
- ❌ 注册码 `999999`（防 Apple 审核员截图被第三方 OCR）
- ❌ admin 教师凭证（审核员不需要测试老师端）

---

## 完成后 itsuki 操作

- [ ] Step 1-6 全跑完
- [ ] admin 密码已存进 1Password
- [ ] iOS 测试 4 项全过
- [ ] Reviewer Notes 文案已粘进 ASC
- [ ] Xcode Archive → Validate → Upload → Submit

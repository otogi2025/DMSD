"""seed — 上架版生产 seed（最小必要数据）。

跟 v1/seed.py 的 dev dummy 不同 — 上架版 backend 部署到 VPS 后，跑这个 seed
只产生上线必需的最小数据：
    1. 1 个超级管理员教师账号（itsuki 自己用，role = 寮務部長）
    2. 1 个 reviewer 学生账号（给 Apple 审核员登录用 — Reviewer Notes 里给凭证）
    3. 1 个 reviewer 注册码（让审核员能跑通完整 6 步注册流程 — 2030 过期）

不再 seed 一堆 dummy 学生 + 教师 + 点呼 session + 学习名簿（生产环境从 0 开始，
真实学生数据由 itsuki / 教师上线后通过 web 后台 + 学生 app 注册流程自然创建）。

执行（VPS 上首次部署后跑一次即可，幂等）：
    cd /opt/tomoshibi/backend
    python -m seed
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app import models, security
from app.database import SessionLocal, create_all

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("seed")


# ---- 超级管理员教师（itsuki 自己用，上线第一个 admin） ----
# password 上线前必须改 — 默认值仅初始化用
ADMIN_TEACHER = dict(
    login_id="admin",
    name="管理者",
    email="otogi2025@gmail.com",
    role="寮務部長",
    assigned_dorm=None,  # 跨寮可见全部
)
ADMIN_PASSWORD_INITIAL = "ChangeMe-2026-05"  # 上线后立刻在 web 后台改


# ---- Apple 审核员账号（Reviewer Notes 里给凭证） ----
# Apple 审核员第一次登录用：直接 login（绕过注册门）→ 看到 home / apply / mypage 完整 UX
REVIEWER_STUDENT = dict(
    grade_code="06",  # 高 3
    class_code="01",  # A 组
    seat_no="99",     # 末尾保留座号给审核员（真实学生不会用 99）
    name="App Reviewer",
    name_kana="アップル レビュアー",
    gender="male",
    category="一般寮生",
    room_no="M999",
    dorm_unit=1,
    is_overseas=False,
    email="reviewer@tomoshibi.cc",
)
REVIEWER_PASSWORD = "Reviewer-2026"  # Reviewer Notes 里给 Apple 审核员

# Apple 审核员可选：用上面账号直接 login OR 用此码跑 6 步注册流程（注册时座号要换）
# 此码不走正常 5 分钟 TTL，远期 expires 让审核员任何时候都能用
REVIEWER_REGISTRATION_CODE = "999999"  # 6 桁 / 文档归档 + Reviewer Notes


def main() -> None:
    create_all()
    db = SessionLocal()
    try:
        admin_pw_hash = security.hash_password(ADMIN_PASSWORD_INITIAL)
        reviewer_pw_hash = security.hash_password(REVIEWER_PASSWORD)

        # 1. admin 教师
        existing_admin = db.scalars(
            select(models.Teacher).where(models.Teacher.login_id == ADMIN_TEACHER["login_id"])
        ).first()
        if existing_admin:
            log.info("admin teacher 已存在 — skip")
        else:
            db.add(models.Teacher(**ADMIN_TEACHER, password_hash=admin_pw_hash))
            log.info("已加 admin 教师 login_id=%s role=%s", ADMIN_TEACHER["login_id"], ADMIN_TEACHER["role"])

        # 2. reviewer 学生
        existing_reviewer = db.scalars(
            select(models.Student).where(
                models.Student.grade_code == REVIEWER_STUDENT["grade_code"],
                models.Student.class_code == REVIEWER_STUDENT["class_code"],
                models.Student.seat_no == REVIEWER_STUDENT["seat_no"],
            )
        ).first()
        if existing_reviewer:
            log.info("reviewer 学生 已存在 — skip")
        else:
            student = models.Student(**REVIEWER_STUDENT)
            db.add(student)
            db.flush()
            db.add(models.Account(student_id=student.id, password_hash=reviewer_pw_hash))
            log.info("已加 reviewer 学生 student_no=%s", student.student_no)

        db.commit()

        # 3. reviewer 注册码（先要找 admin teacher.id 作 created_by）
        admin = db.scalars(
            select(models.Teacher).where(models.Teacher.login_id == ADMIN_TEACHER["login_id"])
        ).first()
        existing_code = db.scalars(
            select(models.StudentRegistrationCode).where(
                models.StudentRegistrationCode.code == REVIEWER_REGISTRATION_CODE,
                models.StudentRegistrationCode.invalidated_at.is_(None),
            )
        ).first()
        if existing_code:
            log.info("reviewer 注册码 已存在 — skip")
        elif admin:
            # 远期 expires（2030-01-01 UTC）让 Apple 审核员任何时候都能跑通注册流程
            far_future = datetime(2030, 1, 1, tzinfo=timezone.utc)
            db.add(
                models.StudentRegistrationCode(
                    code=REVIEWER_REGISTRATION_CODE,
                    created_by=admin.id,
                    expires_at=far_future,
                )
            )
            log.info("已加 reviewer 注册码 code=%s 有效期至 2030-01-01", REVIEWER_REGISTRATION_CODE)

        db.commit()

        log.info("=" * 60)
        log.info("生产 seed 完成（最小必要数据）")
        log.info("admin login: %s / 密码: %s（上线后立刻在 web 后台改）",
                 ADMIN_TEACHER["login_id"], ADMIN_PASSWORD_INITIAL)
        log.info("reviewer 学号: 0601%s / 密码: %s", REVIEWER_STUDENT["seat_no"], REVIEWER_PASSWORD)
        log.info("reviewer 注册码: %s（2030 过期）", REVIEWER_REGISTRATION_CODE)
        log.info("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    main()

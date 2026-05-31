"""pytest fixtures — 专用文件 SQLite 测试库（./test_tomoshibi.db），与真实库 tomoshibi_dev.db 隔离。"""

from __future__ import annotations

import os

# 测试环境固定：专用文件测试库 + 固定 JWT secret + 关掉 SendGrid。
# migtest-02: DATABASE_URL 用直接赋值【不能用 setdefault】—— 否则外部已 export 的 DATABASE_URL
# 或 .env 指向真实库时，下面 _engine 的 drop_all / _truncate_tables 会清空真实库（数据破坏风险）。
os.environ["DATABASE_URL"] = "sqlite:///./test_tomoshibi.db"
os.environ.setdefault("JWT_SECRET", "test-secret-32-bytes-aaaaaaaaaa")
os.environ.setdefault("SENDGRID_API_KEY", "")
os.environ.setdefault("APP_ENV", "dev")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database, models, security
from app.config import get_settings
from app.database import Base
from app.main import app


@pytest.fixture(scope="session")
def _engine():
    # テスト用 engine (session scope, スキーマだけ用意)
    settings = get_settings()
    # migtest-02 安全闸：连的库地址必须含 "test"，否则拒绝建表 / drop_all（双保险，防误清真库）
    assert "test" in settings.database_url, (
        f"测试库地址必须含 'test' 才允许 drop_all / create_all，实际为 {settings.database_url}"
    )
    eng = create_engine(
        settings.database_url, connect_args={"check_same_thread": False}
    )
    Base.metadata.drop_all(bind=eng)
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture(autouse=True)
def _truncate_tables(_engine):
    """各テスト前に全テーブルを空に — テスト間でデータが漏れないように。"""
    from sqlalchemy import text

    with _engine.begin() as conn:
        # 外部キーを一旦無効化 (SQLite 専用)
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.execute(text("PRAGMA foreign_keys=ON"))
    yield


@pytest.fixture
def db_session(_engine):
    SessionTest = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    s = SessionTest()
    try:
        yield s
    finally:
        s.rollback()
        s.close()


@pytest.fixture
def client(_engine):
    SessionTest = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

    def override_get_db():
        s = SessionTest()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[database.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seed_data(db_session):
    """テスト用 minimal seed — 役职 5 人 + 担任 1 + 学生 (留学生)。"""
    from datetime import date

    pw = security.hash_password("test-password-12345")

    # 学生 (留学生 → 5 役职 chain trigger)
    student = models.Student(
        grade_code="06",
        class_code="02",
        seat_no="18",
        name="リュウ イヒ",
        gender="male",
        room_no="M101",
        dorm_unit=1,
        is_overseas=True,
        email="ryu@test.jp",
    )
    db_session.add(student)
    db_session.flush()
    db_session.add(models.Account(student_id=student.id, password_hash=pw))

    # 役职 5 + 担任 1
    teachers_data = [
        ("ryomu_buchou", "寮務太郎", "rb@test.jp", "寮務部長", None),
        ("ryomu_kachou", "寮務次郎", "rk@test.jp", "寮務課長", None),
        ("kokukou_buchou", "国際三郎", "kb@test.jp", "国際交流部長", None),
        ("kokukou_kachou", "国際四郎", "kk@test.jp", "国際交流課長", None),
        ("kanri", "管理五郎", "kn@test.jp", "管理係", None),
        ("tannin", "担任太郎", "tn@test.jp", "寮務一般教師", 1),
    ]
    teachers: dict[str, models.Teacher] = {}
    for login_id, name, email, role, dorm in teachers_data:
        t = models.Teacher(
            login_id=login_id,
            name=name,
            email=email,
            password_hash=pw,
            role=role,
            assigned_dorm=dorm,
        )
        db_session.add(t)
        db_session.flush()
        teachers[login_id] = t

    # 担任紐付け
    db_session.add(
        models.ClassTeacherAssignment(
            teacher_id=teachers["tannin"].id,
            grade_code="06",
            class_code="02",
            academic_year=2026,
            is_homeroom=True,
            effective_from=date(2026, 4, 1),
        )
    )
    db_session.commit()
    return {"student": student, "teachers": teachers}


@pytest.fixture
def student_token(client, seed_data):
    res = client.post(
        "/api/v1/sessions/student",
        json={"student_no": "060218", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture
def teacher_token(client, seed_data):
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "ryomu_kachou", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]

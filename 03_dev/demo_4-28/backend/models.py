"""
数据库表定义（SQLAlchemy ORM）

对应 db_schema.sql，但由 SQLAlchemy 自动建表（main.py 里 Base.metadata.create_all）。
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Student(Base):
    """学生表。demo 版最小字段。"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    card_uid = Column(String, unique=True, nullable=True, index=True)  # NTAG215 卡 UID（绑卡后填）
    created_at = Column(DateTime, default=datetime.utcnow)

    checkins = relationship("Checkin", back_populates="student")
    outstay_requests = relationship("OutstayRequest", back_populates="student")
    return_home_requests = relationship("ReturnHomeRequest", back_populates="student")


class RollCallSession(Base):
    """点呼会话（一次"开始点呼"到"结束点呼"为一个 session）。"""
    __tablename__ = "roll_call_sessions"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String, default="active")  # "active" / "ended"

    checkins = relationship("Checkin", back_populates="session")


class Checkin(Base):
    """签到记录。每次学生签到产生一条。"""
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    session_id = Column(Integer, ForeignKey("roll_call_sessions.id"), nullable=True)
    checkin_at = Column(DateTime, default=datetime.utcnow)
    method = Column(String)  # "card" / "shortcut" / "app"

    student = relationship("Student", back_populates="checkins")
    session = relationship("RollCallSession", back_populates="checkins")


class OutstayRequest(Base):
    """外宿申请（学生提交 → 老师审批）。"""
    __tablename__ = "outstay_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    destination = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String, default="pending")  # "pending" / "approved" / "rejected"
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="outstay_requests")


class ReturnHomeRequest(Base):
    """归国申请（学生寒暑假归国前提交 → 老师审批）。"""
    __tablename__ = "return_home_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    flight_number = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="return_home_requests")

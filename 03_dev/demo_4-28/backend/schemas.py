"""
Pydantic 数据模型（API 输入输出的验证 + 自动文档）

FastAPI 用这些类型自动验证请求 body 和序列化响应。
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional


# === Student ===
class StudentBase(BaseModel):
    name: str
    card_uid: Optional[str] = None


class StudentCreate(StudentBase):
    pass


class StudentOut(StudentBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# === Checkin ===
class CheckinCreate(BaseModel):
    student_id: int
    method: str = "shortcut"  # "card" / "shortcut" / "app"


class CheckinOut(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None  # 便于前端直接显示
    session_id: Optional[int] = None
    checkin_at: datetime
    method: str
    model_config = ConfigDict(from_attributes=True)


# === RollCallSession ===
class RollCallSessionOut(BaseModel):
    id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str
    model_config = ConfigDict(from_attributes=True)


# === Outstay ===
class OutstayCreate(BaseModel):
    student_id: int
    start_date: date
    end_date: date
    destination: Optional[str] = None
    reason: Optional[str] = None


class OutstayUpdate(BaseModel):
    status: str  # "approved" / "rejected"


class OutstayOut(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    start_date: date
    end_date: date
    destination: Optional[str]
    reason: Optional[str]
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


# === ReturnHome ===
class ReturnHomeCreate(BaseModel):
    student_id: int
    start_date: date
    end_date: date
    flight_number: Optional[str] = None
    reason: Optional[str] = None


class ReturnHomeUpdate(BaseModel):
    status: str


class ReturnHomeOut(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    start_date: date
    end_date: date
    flight_number: Optional[str]
    reason: Optional[str]
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


# === Login（demo 硬编码）===
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    message: str

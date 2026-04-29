"""
Tomoshibi Backend Main (Demo Sprint v1)

系统名：Tomoshibi（灯火 / ともしび）
项目代号：DMSD

FastAPI 主程序。启动：
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

自动文档：http://localhost:8000/docs
"""
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, date as date_type
from typing import Optional

from database import engine, get_db, Base
import models
import schemas
from ws_manager import manager


# 启动时自动建表（demo 方便，生产用 Alembic 迁移）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tomoshibi Backend API",
    description="Tomoshibi（灯火）宿舍点呼系统后端 — Demo Sprint v1（4-28 管理员 demo）。项目代号 DMSD。",
    version="0.1.0-demo",
)

# CORS 允许 iPad / iPhone 快捷指令访问（demo 宽松配置）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Health =====
@app.get("/")
def root():
    return {"status": "ok", "service": "Tomoshibi Backend Demo v1"}


# ===== Login（demo 硬编码）=====
DEMO_TEACHER = {"username": "teacher", "password": "1234"}


@app.post("/api/login", response_model=schemas.LoginResponse)
def login(req: schemas.LoginRequest):
    if req.username == DEMO_TEACHER["username"] and req.password == DEMO_TEACHER["password"]:
        return schemas.LoginResponse(
            success=True,
            token="demo-token-" + str(datetime.utcnow().timestamp()),
            message="登录成功",
        )
    return schemas.LoginResponse(success=False, message="账号或密码错误")


# ===== Students =====
@app.get("/api/students", response_model=list[schemas.StudentOut])
def list_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()


@app.post("/api/students", response_model=schemas.StudentOut)
def create_student(s: schemas.StudentCreate, db: Session = Depends(get_db)):
    student = models.Student(**s.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


# ===== Roll Call Sessions =====
@app.post("/api/roll-call/start", response_model=schemas.RollCallSessionOut)
async def start_roll_call(db: Session = Depends(get_db)):
    # 结束所有进行中的 session（确保只有一个 active）
    active = db.query(models.RollCallSession).filter_by(status="active").all()
    for s in active:
        s.status = "ended"
        s.ended_at = datetime.utcnow()

    session = models.RollCallSession(status="active")
    db.add(session)
    db.commit()
    db.refresh(session)

    await manager.broadcast("roll_call_started", {
        "session_id": session.id,
        "started_at": session.started_at.isoformat(),
    })
    return session


@app.post("/api/roll-call/end", response_model=schemas.RollCallSessionOut)
async def end_roll_call(db: Session = Depends(get_db)):
    session = db.query(models.RollCallSession).filter_by(status="active").first()
    if not session:
        raise HTTPException(status_code=404, detail="没有进行中的点呼")
    session.status = "ended"
    session.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(session)

    await manager.broadcast("roll_call_ended", {"session_id": session.id})
    return session


@app.get("/api/roll-call/sessions", response_model=list[schemas.RollCallSessionOut])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(models.RollCallSession).order_by(models.RollCallSession.started_at.desc()).all()


# ===== Checkin =====
@app.post("/api/checkin", response_model=schemas.CheckinOut)
async def checkin(c: schemas.CheckinCreate, db: Session = Depends(get_db)):
    """学生签到。三路径都走这个 API：
    - iOS App / 快捷指令：method="shortcut" 或 "app"
    - 点呼机卡：method="card"（Pi 读到 UID 后转 student_id 再调本 API，或 Pi 直接发 card_uid 由后端反查）
    """
    student = db.query(models.Student).filter_by(id=c.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 找当前 active session
    session = db.query(models.RollCallSession).filter_by(status="active").first()

    # 幂等：同一 session 同一学生重复签到，返回已有记录
    if session:
        existing = db.query(models.Checkin).filter_by(
            student_id=c.student_id, session_id=session.id
        ).first()
        if existing:
            out = schemas.CheckinOut.model_validate(existing)
            out.student_name = student.name
            return out

    checkin = models.Checkin(
        student_id=c.student_id,
        session_id=session.id if session else None,
        method=c.method,
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    out = schemas.CheckinOut.model_validate(checkin)
    out.student_name = student.name

    # 推实时事件给老师 Web
    await manager.broadcast("checkin", {
        "checkin_id": checkin.id,
        "student_id": student.id,
        "student_name": student.name,
        "session_id": checkin.session_id,
        "checkin_at": checkin.checkin_at.isoformat(),
        "method": checkin.method,
    })

    return out


@app.get("/api/checkins", response_model=list[schemas.CheckinOut])
def list_checkins(
    date: Optional[date_type] = None,
    session_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Checkin).join(models.Student)
    if date:
        # 按日期筛选（那天 00:00 到 23:59）
        from datetime import datetime as dt, time
        start = dt.combine(date, time.min)
        end = dt.combine(date, time.max)
        q = q.filter(models.Checkin.checkin_at.between(start, end))
    if session_id:
        q = q.filter(models.Checkin.session_id == session_id)

    results = q.order_by(models.Checkin.checkin_at.desc()).all()
    out = []
    for c in results:
        item = schemas.CheckinOut.model_validate(c)
        item.student_name = c.student.name
        out.append(item)
    return out


# ===== Outstay =====
@app.post("/api/outstay", response_model=schemas.OutstayOut)
async def create_outstay(o: schemas.OutstayCreate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter_by(id=o.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    req = models.OutstayRequest(**o.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)

    out = schemas.OutstayOut.model_validate(req)
    out.student_name = student.name

    await manager.broadcast("outstay_new", out.model_dump(mode="json"))
    return out


@app.get("/api/outstay", response_model=list[schemas.OutstayOut])
def list_outstay(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.OutstayRequest)
    if status:
        q = q.filter_by(status=status)
    results = q.order_by(models.OutstayRequest.created_at.desc()).all()
    out = []
    for r in results:
        item = schemas.OutstayOut.model_validate(r)
        item.student_name = r.student.name
        out.append(item)
    return out


@app.patch("/api/outstay/{req_id}", response_model=schemas.OutstayOut)
async def review_outstay(req_id: int, u: schemas.OutstayUpdate, db: Session = Depends(get_db)):
    req = db.query(models.OutstayRequest).filter_by(id=req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="申请不存在")
    if u.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="status 必须是 approved 或 rejected")

    req.status = u.status
    req.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(req)

    out = schemas.OutstayOut.model_validate(req)
    out.student_name = req.student.name

    await manager.broadcast("outstay_updated", out.model_dump(mode="json"))
    return out


# ===== ReturnHome =====
@app.post("/api/return-home", response_model=schemas.ReturnHomeOut)
async def create_return_home(r: schemas.ReturnHomeCreate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter_by(id=r.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    req = models.ReturnHomeRequest(**r.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)

    out = schemas.ReturnHomeOut.model_validate(req)
    out.student_name = student.name

    await manager.broadcast("return_home_new", out.model_dump(mode="json"))
    return out


@app.get("/api/return-home", response_model=list[schemas.ReturnHomeOut])
def list_return_home(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.ReturnHomeRequest)
    if status:
        q = q.filter_by(status=status)
    results = q.order_by(models.ReturnHomeRequest.created_at.desc()).all()
    out = []
    for r in results:
        item = schemas.ReturnHomeOut.model_validate(r)
        item.student_name = r.student.name
        out.append(item)
    return out


@app.patch("/api/return-home/{req_id}", response_model=schemas.ReturnHomeOut)
async def review_return_home(req_id: int, u: schemas.ReturnHomeUpdate, db: Session = Depends(get_db)):
    req = db.query(models.ReturnHomeRequest).filter_by(id=req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="申请不存在")
    if u.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="status 必须是 approved 或 rejected")

    req.status = u.status
    req.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(req)

    out = schemas.ReturnHomeOut.model_validate(req)
    out.student_name = req.student.name

    await manager.broadcast("return_home_updated", out.model_dump(mode="json"))
    return out


# ===== WebSocket =====
@app.websocket("/ws/teacher")
async def ws_teacher(websocket: WebSocket):
    """老师 Web 连这里订阅实时事件。"""
    await manager.connect(websocket)
    try:
        while True:
            # 老师 Web 一般不往后端发消息，但保持连接
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

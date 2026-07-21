"""通知 (admin / dev) endpoint。

POST /api/v1/notifications/test  — SendGrid 送達 smoke テスト (#6 完成定義)
"""

from __future__ import annotations

import logging
from datetime import datetime
from uuid import NAMESPACE_URL, UUID, uuid5
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import exists, func, or_, select, true
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    assert_not_demo_teacher,
    get_current_teacher,
    require_permission,
)
from ..services import email as email_svc
from .discipline import CLEANING_THRESHOLD, CURFEW_THRESHOLD

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

_logger = logging.getLogger(__name__)


@router.post("/test", response_model=schemas.NotificationTestOut)
def send_test(
    body: schemas.NotificationTestIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ANNOUNCE, permissions.MANAGE)
    ),
):
    # 演示老师禁用真实发邮件通道（防滥发 / 钓鱼 / 耗 SendGrid 配额 / 损发信域名信誉）→ 403
    assert_not_demo_teacher(teacher)

    log, status_code, error = email_svc.send_test_email(
        db,
        to=body.to,
        subject=body.subject,
        body_text=body.body_text,
        actor_id=teacher.id,
    )
    db.commit()

    return schemas.NotificationTestOut(
        sent=(log.status == "sent"),
        notification_log_id=log.id,
        sendgrid_status_code=status_code,
        error=error,
    )


# ---------------------------------------------------------------
# 老师通知中心（UI「通知センター」）— 阶段1（itsuki 2026-06-13）
#
# 填充策略：不在各事件产生点写钩子，而是取 feed 时扫现有事件表
# （申请提交 / 扣分 / 点呼上报）幂等同步成通知行（按 source_table+source_id 去重）。
# 好处：只改 models/schemas/本文件 + 迁移，不碰 applications/discipline/rollcall 路由
# （降低与其它会话改后端文件的冲突面）。代价：通知在取 feed 时生成，非事件即时。
# ---------------------------------------------------------------

# 每张事件表每次同步最多生成的新通知数（漏斗速率，不是「只看最新 N 条」窗口）。
# 旧实现是「按时间倒序取最新 200 条再内存去重」—— 一旦某表积压超过 200 条未同步事件，
# 第 201 条往后的更早事件会被永远挡在窗口外、再也不会生成通知（codex F-codex-中-02）。
# 现实现改成「只查该表里『还没有对应通知行』的事件、按时间正序（最旧优先）取 N 条」，
# 于是每次轮询都从最旧的积压开始补，跨多次轮询把整段积压逐批排空，不会永久漏掉任何事件。
_SYNC_SCAN_LIMIT = 200

_JST = ZoneInfo("Asia/Tokyo")

# 自动告警（UI「自動アラート」，itsuki 2026-06-15）：学生当月累计扣分达阈值 → 自动给该生所属寮的老师发通知。
# 两级阈值复用 discipline 的罚扫线(4) / 禁足线(8)，单源对齐；每生每月每级只发一次（uuid5 去重）。
# (阈值, level 标识, 日语线名)
_DEMERIT_ALERT_LEVELS = [
    (CLEANING_THRESHOLD, "cleaning", "清掃ライン"),
    (CURFEW_THRESHOLD, "curfew", "外出禁止ライン"),
]
# 固定命名空间 → source_id 确定性，幂等去重不重复发
_ALERT_NS = uuid5(NAMESPACE_URL, "tomoshibi/demerit-alert")

# 点呼上报 kind → 日语标题
_ROLLCALL_KIND_LABEL = {
    "health": "体調報告",
    "absence": "欠席の申請",
    "other": "その他の問題",
}

# 学習欠席届 period → 日语标签
_STUDY_PERIOD_LABEL = {
    "first_half": "前半節",
    "second_half": "後半節",
    "full": "終日",
}

# 杂项申请 kind → 日语标签
_MISC_KIND_LABEL = {
    "repair": "修繕",
    "guest": "来訪者",
    "proxy_receipt": "代理受取",
}

# 第二批通知来源（阶段2）：7 类「学生提交、老师该知道」的申请表。
# 每条配置一种表的同步参数，避免 8 段几乎一样的代码：
#   model       该表的 ORM 模型类
#   student_fk  关联学生的外键列（多数是 student_id，行事企画是 proposer_id）
#   time_col    事件时间列（多数 submitted_at，杂项 created_at）
#   source_table 去重用的源表名（与 Notification.source_table 对应）
#   category    通知分类（老师网页据此显示标签 + 决定点击跳哪页）
#   title       通知标题（日语 UI）
#   body        构造正文的函数 (申请行, 学生) → 日语字符串
_REQUEST_SOURCES = [
    {
        "model": models.Outing,
        "student_fk": models.Outing.student_id,
        "time_col": models.Outing.submitted_at,
        "source_table": "outings",
        "category": "outing",
        "title": "外出申請",
        "body": lambda r, s: (
            f"{s.name} さん：{r.destination or '外出'}（{r.outing_date}）"
        ),
    },
    {
        "model": models.StudyAbsenceRequest,
        "student_fk": models.StudyAbsenceRequest.student_id,
        "time_col": models.StudyAbsenceRequest.submitted_at,
        "source_table": "study_absence_requests",
        "category": "study_absence",
        "title": "晩自習欠席届",
        "body": lambda r, s: (
            f"{s.name} さん：{r.target_date}（{_STUDY_PERIOD_LABEL.get(r.period, r.period)}）"
        ),
    },
    {
        "model": models.StudyOnlineRequest,
        "student_fk": models.StudyOnlineRequest.student_id,
        "time_col": models.StudyOnlineRequest.submitted_at,
        "source_table": "study_online_requests",
        "category": "study_online",
        "title": "オンライン学習申請",
        "body": lambda r, s: f"{s.name} さん：{r.period_from}〜{r.period_to}",
    },
    {
        "model": models.DormEventProposal,
        "student_fk": models.DormEventProposal.proposer_id,
        "time_col": models.DormEventProposal.submitted_at,
        "source_table": "dorm_event_proposals",
        "category": "dorm_event",
        "title": "寮生行事企画申請",
        "body": lambda r, s: f"{s.name} さん：{r.title}",
    },
    {
        "model": models.FridgePurchaseRequest,
        "student_fk": models.FridgePurchaseRequest.student_id,
        "time_col": models.FridgePurchaseRequest.submitted_at,
        "source_table": "fridge_purchase_requests",
        "category": "fridge",
        "title": "冷蔵庫購入届",
        "body": lambda r, s: f"{s.name} さん：タイプ{r.product}",
    },
    {
        "model": models.ItemPossessionRequest,
        "student_fk": models.ItemPossessionRequest.student_id,
        "time_col": models.ItemPossessionRequest.submitted_at,
        "source_table": "item_possession_requests",
        "category": "item",
        "title": "物品所持許可願",
        "body": lambda r, s: f"{s.name} さん：{r.item}",
    },
    {
        "model": models.MiscRequest,
        "student_fk": models.MiscRequest.student_id,
        "time_col": models.MiscRequest.created_at,
        "source_table": "misc_requests",
        "category": "misc",
        "title": "雑項申請",
        "body": lambda r, s: (
            f"{s.name} さん：{_MISC_KIND_LABEL.get(r.kind, r.kind)}／{r.subject}"
        ),
    },
]


def _fmt_points(points: float) -> str:
    """0.5 → "0.5" / 1.0 → "1"（整数去小数点）。"""
    return str(int(points)) if points == int(points) else str(points)


def _insert_skip_conflicts(db: Session, rows: list[models.Notification]) -> None:
    """逐条插入通知行，撞唯一约束就跳过（并发安全）。

    内存去重（existing 集合）只在单请求内有效；多个老师同时在线 + 侧栏每 30 秒
    轮询 unread-count + 通知页拉 feed → 两个请求可能都读到「还没有某新事件」的
    快照、都尝试插同一 (source_table, source_id)，第二个会撞 uq_notif_source。
    这里每条用 savepoint（嵌套事务）包起来，撞约束就回滚该 savepoint 并跳过，
    外层事务不受影响（SQLite + PostgreSQL 都支持 savepoint）。
    """
    for row in rows:
        try:
            with db.begin_nested():
                db.add(row)
                db.flush()
        except IntegrityError as e:
            # 只吞「同一来源被并发插了重复」这一种（撞 uq_notif_source）；
            # 其余完整性错误（外键 / 非空 / check）不掩盖 —— 重新抛出暴露真问题，
            # 否则会静默丢数据还让接口返回成功。
            # 跨方言匹配：PostgreSQL 报约束名 uq_notif_source；
            # SQLite 报「UNIQUE constraint failed: ...source_id」。
            msg = str(getattr(e, "orig", e)).lower()
            if "uq_notif_source" in msg or ("unique" in msg and "source_id" in msg):
                continue  # 预期的并发重复 — 跳过这条，外层事务继续
            raise


def _not_yet_synced(source_id_col, *, source_table: str, is_demo: bool):
    """SQL 层反连接：排除本 realm 已同步过的 source_id。

    等价于旧「先拉全量 source_id 进 Python 再 notin_(巨型列表)」——结果集相同，
    但不把 id 列表搬进绑定参数（避 PostgreSQL 参数上限 / 膨胀触顶 500）。
    """
    return ~exists(
        select(models.Notification.id).where(
            models.Notification.source_table == source_table,
            models.Notification.is_demo == is_demo,
            models.Notification.source_id == source_id_col,
        )
    )


def _synced_source_ids(db: Session, *, source_table: str, is_demo: bool) -> set:
    """取「本 realm 内、这张源表已生成过通知」的 source_id 集合。

    仅留给 demerit_alert：告警的 source_id 在 Python 里用 uuid5 算出来，
    无法用外键列做 SQL 关联反连接，只能先拉集合再 `in` 判断。
    其它源表已改走 `_not_yet_synced`（NOT EXISTS）。
    """
    return {
        sid
        for (sid,) in db.query(models.Notification.source_id)
        .filter(
            models.Notification.source_table == source_table,
            models.Notification.is_demo == is_demo,
        )
        .all()
    }


def _sync_notifications(db: Session, *, is_demo: bool) -> bool:
    """把现有事件幂等同步成通知行（只处理与 realm[is_demo] 匹配的事件）。

    每张源表用 SQL NOT EXISTS 排除已同步 source_id，再只查「还没同步」的事件、
    按时间正序（最旧优先）取最多 _SYNC_SCAN_LIMIT 条 —— 跨多次轮询逐批排空积压，
    不会像旧实现那样把超过窗口的更早事件永久漏掉。
    并发请求间的竞争由 _insert_skip_conflicts 的 savepoint+跳过兜底
    （防撞 uq_notif_source 变 500）。

    审查 backend#35：返回本次是否新增了通知行——调用方（只读 GET）据此只在真有
    新行时才 commit，稳态无新事件时省掉每请求一次的写 commit（减多老师轮询写压力）。
    不引入延迟、同步结果与原来完全一致（区别于节流方案会让新通知最多晚 N 秒可见）。
    """
    new_rows: list[models.Notification] = []

    # ① 申请提交
    apps = (
        db.query(models.Application, models.Student)
        .join(models.Student, models.Application.student_id == models.Student.id)
        .filter(
            models.Student.is_demo == is_demo,
            _not_yet_synced(
                models.Application.id, source_table="applications", is_demo=is_demo
            ),
        )
        .order_by(models.Application.submitted_at.asc())
        .limit(_SYNC_SCAN_LIMIT)
        .all()
    )
    for app, stu in apps:
        new_rows.append(
            models.Notification(
                category="application",
                source_table="applications",
                source_id=app.id,
                title=f"出寮届の申請（{app.kind}）",
                body=f"{stu.name} さんが{app.kind}を申請しました",
                related_student_id=stu.id,
                is_demo=is_demo,
                event_at=app.submitted_at,
            )
        )

    # ② 扣分（未撤销）
    demerits = (
        db.query(models.DemeritEvent, models.Student)
        .join(models.Student, models.DemeritEvent.student_id == models.Student.id)
        .filter(
            models.Student.is_demo == is_demo,
            models.DemeritEvent.revoked_at.is_(None),
            _not_yet_synced(
                models.DemeritEvent.id, source_table="demerit_event", is_demo=is_demo
            ),
        )
        .order_by(models.DemeritEvent.created_at.asc())
        .limit(_SYNC_SCAN_LIMIT)
        .all()
    )
    for ev, stu in demerits:
        new_rows.append(
            models.Notification(
                category="demerit",
                source_table="demerit_event",
                source_id=ev.id,
                title=f"減点（{_fmt_points(ev.points)}点）",
                body=f"{stu.name} さん：{ev.reason}",
                related_student_id=stu.id,
                is_demo=is_demo,
                event_at=ev.created_at,
            )
        )

    # ③ 点呼上报
    reports = (
        db.query(models.RollCallReport, models.Student)
        .join(models.Student, models.RollCallReport.student_id == models.Student.id)
        .filter(
            models.Student.is_demo == is_demo,
            _not_yet_synced(
                models.RollCallReport.id,
                source_table="rollcall_reports",
                is_demo=is_demo,
            ),
        )
        .order_by(models.RollCallReport.created_at.asc())
        .limit(_SYNC_SCAN_LIMIT)
        .all()
    )
    for rep, stu in reports:
        label = _ROLLCALL_KIND_LABEL.get(rep.kind, "点呼の報告")
        new_rows.append(
            models.Notification(
                category="rollcall_report",
                source_table="rollcall_reports",
                source_id=rep.id,
                title=f"点呼報告：{label}",
                body=f"{stu.name} さん：{rep.body}",
                related_student_id=stu.id,
                is_demo=is_demo,
                event_at=rep.created_at,
            )
        )

    # ④ 第二批：7 类申请表（外出 / 学习缺席 / 在线学习 / 行事企划 /
    #    冰箱购入 / 物品持有 / 杂项）— 配置见 _REQUEST_SOURCES
    for cfg in _REQUEST_SOURCES:
        rows = (
            db.query(cfg["model"], models.Student)
            .join(models.Student, cfg["student_fk"] == models.Student.id)
            .filter(
                models.Student.is_demo == is_demo,
                _not_yet_synced(
                    cfg["model"].id,
                    source_table=cfg["source_table"],
                    is_demo=is_demo,
                ),
            )
            .order_by(cfg["time_col"].asc())
            .limit(_SYNC_SCAN_LIMIT)
            .all()
        )
        for row, stu in rows:
            new_rows.append(
                models.Notification(
                    category=cfg["category"],
                    source_table=cfg["source_table"],
                    source_id=row.id,
                    title=cfg["title"],
                    body=cfg["body"](row, stu),
                    related_student_id=stu.id,
                    is_demo=is_demo,
                    event_at=getattr(row, cfg["time_col"].key),
                )
            )

    # ⑤ 自动告警：当月累计扣分达罚扫/禁足线的学生 → 给该生所属寮的老师发通知。
    #    口径与 /ranking 一致（当月 month + 排除已撤销）。每生每月每级一条（uuid5 去重）。
    month = datetime.now(_JST).strftime("%Y-%m")
    synced_alert = _synced_source_ids(db, source_table="demerit_alert", is_demo=is_demo)
    totals = (
        db.query(
            models.Student.id,
            models.Student.name,
            models.Student.dorm_unit,
            func.coalesce(func.sum(models.DemeritEvent.points), 0.0).label("total"),
            func.max(models.DemeritEvent.created_at).label("last_at"),
        )
        .join(
            models.DemeritEvent,
            models.DemeritEvent.student_id == models.Student.id,
        )
        .filter(
            models.Student.is_demo == is_demo,
            models.DemeritEvent.month == month,
            models.DemeritEvent.revoked_at.is_(None),
        )
        .group_by(models.Student.id, models.Student.name, models.Student.dorm_unit)
        .all()
    )
    for sid, sname, dorm_unit, total, last_at in totals:
        for threshold, level, line_label in _DEMERIT_ALERT_LEVELS:
            if total < threshold:
                continue
            source_id = uuid5(_ALERT_NS, f"{sid}:{month}:{level}")
            if source_id in synced_alert:
                continue
            new_rows.append(
                models.Notification(
                    category="demerit_alert",
                    source_table="demerit_alert",
                    source_id=source_id,
                    title=f"減点警告：{line_label}到達",
                    body=(
                        f"{sname} さんの今月の累計減点が {_fmt_points(total)}点"
                        f"（{line_label}{_fmt_points(threshold)}点）に達しました"
                    ),
                    related_student_id=sid,
                    is_demo=is_demo,
                    event_at=last_at or datetime.now(_JST),
                    target_dorm=dorm_unit,
                )
            )

    if new_rows:
        _insert_skip_conflicts(db, new_rows)
    return bool(new_rows)


def _alert_dorm_units(teacher: models.Teacher):
    """该老师作为自动告警定向对象时覆盖的 dorm_unit 集合（None = 全寮役职、看全部）。

    不用 deps.dorm_units_for_teacher —— itsuki 2026-06-13 全局取消寮过滤后它恒返回
    [1,2,4]（所有老师可查看所有学生）。但本次自动告警要求「只通知该学生所在寮的老师」，
    故这里按 assigned_dorm 直接判男女寮组（1,2=男 / 4=女）。注意：这只影响告警「推给谁」，
    不改「谁能查看学生」的全局放开。
    """
    d = teacher.assigned_dorm
    if d is None:
        return None  # 跨寮役职（寮務部長/課長 等）→ 所有寮的告警都收
    if d in (1, 2):
        return [1, 2]  # 男寮老师 → 收男寮（一寮/二寮）告警
    if d == 4:
        return [4]  # 女寮老师 → 收女寮告警
    # 宿舍只有 1/2/4。assigned_dorm 是非法值（如误配成 3/0/99 — 表上无 CHECK 约束）时，
    # 原来 else 兜底 return [d] 会让该老师只匹配 target_dorm==[d]，而真实告警 target_dorm
    # 恒为 1/2/4，导致该老师永久静默漏收所有告警。改为返回 None（宁可多收全寮告警也不
    # 静默漏收）+ 记 warning 让非法配置可观测。根治应在 teachers.assigned_dorm 加取值约束。
    _logger.warning(
        "teacher %s assigned_dorm=%r 非法（应为 1/2/4），告警定向回退为全寮",
        teacher.id,
        d,
    )
    return None


def _dorm_visibility_filter(teacher: models.Teacher):
    """通知可见范围：target_dorm 为空（全员通知，所有现有类型）人人可见；
    非空（自动告警定向到学生寮）的，仅该寮老师 + 跨寮役职可见。"""
    allowed = _alert_dorm_units(teacher)
    if allowed is None:
        return true()
    return or_(
        models.Notification.target_dorm.is_(None),
        models.Notification.target_dorm.in_(allowed),
    )


def _notif_visible_to(teacher: models.Teacher, notif: models.Notification) -> bool:
    """单条通知对该老师是否可见（mark_read 用）—— 与 _dorm_visibility_filter 同语义的对象版。"""
    if notif.target_dorm is None:
        return True
    allowed = _alert_dorm_units(teacher)
    return allowed is None or notif.target_dorm in allowed


def _unread_count(db: Session, teacher: models.Teacher) -> int:
    """当前老师在自己 realm + 管辖寮范围内的未读通知数 = 可见总数 − 本人已读数。"""
    dorm_filter = _dorm_visibility_filter(teacher)
    total = (
        db.query(models.Notification)
        .filter(models.Notification.is_demo == teacher.is_demo, dorm_filter)
        .count()
    )
    read = (
        db.query(models.NotificationRead)
        .join(
            models.Notification,
            models.NotificationRead.notification_id == models.Notification.id,
        )
        .filter(
            models.Notification.is_demo == teacher.is_demo,
            dorm_filter,
            models.NotificationRead.teacher_id == teacher.id,
        )
        .count()
    )
    return max(0, total - read)


@router.get("/feed", response_model=schemas.NotificationFeedOut)
def get_feed(
    limit: int = 50,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """通知中心「最近の通知」流 + 未读数。任意已登录老师可看自己 realm 的通知。"""
    # 只读路径：只在真同步出新行时才 commit（省稳态无事件时的空 commit；审查 backend#35）
    if _sync_notifications(db, is_demo=teacher.is_demo):
        db.commit()

    read_ids = {
        nid
        for (nid,) in db.query(models.NotificationRead.notification_id)
        .filter(models.NotificationRead.teacher_id == teacher.id)
        .all()
    }
    rows = (
        db.query(models.Notification)
        .filter(
            models.Notification.is_demo == teacher.is_demo,
            _dorm_visibility_filter(teacher),
        )
        .order_by(models.Notification.event_at.desc())
        .limit(max(1, min(limit, 200)))
        .all()
    )
    items = [
        schemas.NotificationItem(
            id=n.id,
            category=n.category,
            title=n.title,
            body=n.body,
            related_student_id=n.related_student_id,
            event_at=n.event_at,
            is_read=(n.id in read_ids),
        )
        for n in rows
    ]
    return schemas.NotificationFeedOut(
        items=items, unread_count=_unread_count(db, teacher)
    )


@router.get("/unread-count", response_model=schemas.NotificationUnreadCountOut)
def get_unread_count(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """侧栏「通知」徽章用 — 当前老师未读数（顺带同步新事件）。"""
    # 只读路径：只在真同步出新行时才 commit（审查 backend#35）
    if _sync_notifications(db, is_demo=teacher.is_demo):
        db.commit()
    return schemas.NotificationUnreadCountOut(unread_count=_unread_count(db, teacher))


@router.post(
    "/{notification_id}/read", response_model=schemas.NotificationUnreadCountOut
)
def mark_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """标记单条通知为已读（幂等）。返回更新后的未读数。"""
    notif = db.get(models.Notification, notification_id)
    # codex 复审 major：除 realm(is_demo) 外还要按寮可见性过滤 —— 否则别寮老师能把定向到本寮的
    # 自动告警标记已读。不可见的当 404 隐藏存在性（与 feed 过滤口径一致）。
    if (
        notif is None
        or notif.is_demo != teacher.is_demo
        or not _notif_visible_to(teacher, notif)
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "通知が見つかりません"},
        )
    already = (
        db.query(models.NotificationRead)
        .filter(
            models.NotificationRead.notification_id == notification_id,
            models.NotificationRead.teacher_id == teacher.id,
        )
        .first()
    )
    if already is None:
        # 多个老师同时点「既読」可能并发撞 uq_notif_read — 用 savepoint 兜底：
        # 撞唯一约束时只回滚本条 savepoint，外层事务不受影响，接口正常返回。
        try:
            with db.begin_nested():
                db.add(
                    models.NotificationRead(
                        notification_id=notification_id, teacher_id=teacher.id
                    )
                )
                db.flush()
        except IntegrityError as exc:
            msg = str(getattr(exc, "orig", exc)).lower()
            if "uq_notif_read" in msg or (
                "unique" in msg and "notification_read" in msg
            ):
                pass  # 并发重复写 — 已读状态已存在，直接跳过
            else:
                raise
        db.commit()
    return schemas.NotificationUnreadCountOut(unread_count=_unread_count(db, teacher))


@router.post("/read-all", response_model=schemas.NotificationUnreadCountOut)
def mark_all_read(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """把当前老师 realm 内所有通知标记为已读。返回未读数（= 0）。"""
    _sync_notifications(db, is_demo=teacher.is_demo)
    db.commit()
    read_ids = {
        nid
        for (nid,) in db.query(models.NotificationRead.notification_id)
        .filter(models.NotificationRead.teacher_id == teacher.id)
        .all()
    }
    all_ids = [
        nid
        for (nid,) in db.query(models.Notification.id)
        .filter(
            models.Notification.is_demo == teacher.is_demo,
            _dorm_visibility_filter(teacher),
        )
        .all()
    ]
    for nid in all_ids:
        if nid not in read_ids:
            # 多老师同时点「全部既読」会并发撞 uq_notif_read — 每条用 savepoint 包起来：
            # 撞唯一约束就跳过这条，外层事务继续，不让并发请求打出 500。
            try:
                with db.begin_nested():
                    db.add(
                        models.NotificationRead(
                            notification_id=nid, teacher_id=teacher.id
                        )
                    )
                    db.flush()
            except IntegrityError as exc:
                msg = str(getattr(exc, "orig", exc)).lower()
                if "uq_notif_read" in msg or (
                    "unique" in msg and "notification_read" in msg
                ):
                    continue  # 并发重复写 — 已读状态已存在，跳过
                raise
    db.commit()
    return schemas.NotificationUnreadCountOut(unread_count=_unread_count(db, teacher))

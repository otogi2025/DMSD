# Teacher Web v1.0 完整体上线 — Backend Model + Router Propose

> **作用**：CC 5-27 凌晨深夜推进时无法替 itsuki 决策的 backend schema 字段。itsuki 起床后 review + 拍板 → 接着加 `models.py` + alembic migration + `routers/*.py` + `schemas.py` + teacher_web 接 `client.js` helper 即可。
> **由来**：5-26 23:45 itsuki 设 `/goal v1.0 完整体上线` → CC 25 commits 推 teacher_web 边界 → backend 剩 5+ router 缺数据 model → 字段决策非 CC 能决 → 本 doc 是 CC propose 等 itsuki 拍板。
> **预估全部实装**：backend 10-15 小时（3-5 次会话）+ teacher_web 接入 2-3 小时（1 次会话）。
> **5 端对齐**：iOS / Android 当前都不使用这 5 个 model，本 doc 主要影响 backend + teacher_web。未来 iOS 「我自己的扣分情况」类页面才会触及 DemeritEvent。

---

## 0. 优先度排序（itsuki 拍板时按这个顺序考虑）

| 优先 | model + router | teacher_web page | 阻塞性 |
|---|---|---|---|
| P0 | DemeritEvent + discipline.py | DisciplinePage 扣分排名 + 罚扫 + 禁足 + 警告 | spec §7.5 老师 38 条要求 |
| P0 | RecordsAggregation (从 rollcall + study 派生 view) | RecordsPage 签到历史 | spec §5.12 + 5-27 部分实装 backend GET /rollcall/sessions ✅ |
| P1 | CleaningAssignment + cleaning.py | CleaningPage 清扫审核 | spec §7.10 |
| P1 | FrontDeskItem + front-desk.py | FrontDeskPage 宅配 + 忘れ物 | spec §7.12 wapper |
| P2 | CommunityPost + CommunityComment + community.py | CommunityPage 寮掲示板 + リクエスト曲 + 匿名建議 | spec §7.13 |
| P2 | Notice + notice.py | InfoPage notice tab + 行事 + バス | spec §7.11（跟既存 Announcement 区别） |

加补充：
- **FC-027 announcements 权限重做**（修 `routers/announcements.py` 让 list/detail 同时支持老师 token）— 1 小时单独修
- **NotificationsPage 聚合 endpoint** — 设计聚合 view 含 4 数字 (pending_apps / pending_absence_requests / health_issues / front_desk_unread)，没新 table

---

## 1. DemeritEvent (P0 最重要)

### 1.1 spec 来源 + 业务规则
- spec §7.5 「規律・処分」: 全员月排名 + 罚扫名单 + 禁足名单 + 警告リスト
- itsuki 5-22 cleaning 阈值: 4 点 (清掃罰則) / 8 点 (外出禁止)
- spec §4.1 5 色: ok/late/absent/exempt/late_overlay — late 1 点 / absent 2 点 (待 itsuki 拍板)

### 1.2 字段提案

```python
class DemeritEvent(Base):
    """扣分事件 (DisciplinePage / CleaningPage / 警告リスト 全部依赖)。
    
    出处：spec §7.5 + itsuki 5-22 8 点禁足阈值。
    """
    __tablename__ = "demerit_event"
    
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("student.id"), nullable=False, index=True)
    
    # 扣分事件来源 ⏳ itsuki 拍板取值
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # 提案候选: 'rollcall_late' / 'rollcall_absent' / 'cleaning_failed' / 'curfew_violation' / 'study_absent' / 'manual'
    source_event_id: Mapped[Optional[UUID]] = mapped_column(Uuid)
    # source_type='rollcall_late' 时 = RollCallEvent.id 等
    
    # 扣分点数 ⏳ itsuki 拍板
    points: Mapped[float] = mapped_column(Float, nullable=False)
    # 提案: late=1.0 / absent=2.0 / cleaning=2.5 / curfew=5.0 / study_absent=1.5
    
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    # 自由文本说明：「12-04 晩点呼 5 分超 late」
    
    # 月份 (汇总用，避免每次 GROUP BY)
    month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    # YYYY-MM 格式：'2026-05'
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_by_teacher_id: Mapped[Optional[UUID]] = mapped_column(Uuid, ForeignKey("teacher.id"))
    # NULL = 系统自动判定 (cron 跑 rollcall settle)
    
    # 撤销机制 ⏳ itsuki 拍板
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    revoked_by_teacher_id: Mapped[Optional[UUID]] = mapped_column(Uuid, ForeignKey("teacher.id"))
    revoke_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    __table_args__ = (
        CheckConstraint(
            "source_type IN ('rollcall_late','rollcall_absent','cleaning_failed','curfew_violation','study_absent','manual')",
            name="ck_demerit_source"
        ),
        Index("idx_demerit_student_month", "student_id", "month"),
    )
```

### 1.3 待 itsuki 拍板项

- **source_type 取值范围** — 6 个候选够吗？还有「無断外宿」「寮内禁止物品携入」等？
- **points 数值** — late=1 / absent=2 / cleaning=2.5 / curfew=5 / study_absent=1.5 — 这些数对吗？
- **points 用 float 还是 int** — 当前 propose float (允许 0.5 分罚扫)。float 还是 int？
- **revoke 后是否保留** — propose 软删除（revoked_at 不为 null = 被撤销但记录在）。或者硬删？
- **manual 类型权限** — 谁能手动加扣分？只寮監？寮務全员？

### 1.4 router endpoint propose

```python
# routers/discipline.py 新文件
GET  /api/v1/discipline/ranking?month=YYYY-MM&dorm=N    # 全员排名 (含 0 分的)
GET  /api/v1/discipline/cleaning-list?month=YYYY-MM     # 罚扫名单 (4 分以上)
GET  /api/v1/discipline/curfew-list?month=YYYY-MM       # 禁足名单 (8 分以上)
GET  /api/v1/discipline/warnings?month=YYYY-MM          # 警告リスト (连续超标)
GET  /api/v1/discipline/student/{id}                    # 学生个人 timeline
POST /api/v1/discipline/manual                          # 手动加扣分 (寮監权限)
POST /api/v1/discipline/{id}/revoke                     # 撤销扣分 (寮監权限 + 24h 内)
```

---

## 2. CleaningAssignment + cleaning.py (P1)

### 2.1 spec 来源
- spec §7.10 清扫审査
- 业务：分配 → 学生扫 → 老师审核（通过 / 不通过）→ 不通过则 DemeritEvent.source_type='cleaning_failed'

### 2.2 字段提案 (粗)
```python
class CleaningAssignment(Base):
    id, student_id, area, scheduled_at, status (assigned/done/passed/failed),
    inspected_by_teacher_id, inspected_at, failure_reason, created_at
```

### 2.3 待 itsuki 拍板
- 清扫区域 ENUM (浴室 / 廊下 / トイレ / リビング / ...) — 实际宿舍区域清单
- 是否系统自动分配 vs 老师手动分配
- 不通过 → 自动 DemeritEvent 还是老师手动加？

---

## 3. FrontDeskItem + front-desk.py (P1)

### 3.1 spec 来源
- spec §7.12 宅配通知 + 忘れ物（CommunityPage 4-23 拆分出来）

### 3.2 字段提案 (粗)
```python
class FrontDeskItem(Base):
    id, kind (delivery/lost_and_found),
    student_id (delivery 时学生 / lost_and_found 时 nullable),
    description, location_picked_up, status (pending/notified/picked_up/expired),
    created_by_teacher_id, created_at, picked_up_at, expires_at
```

### 3.3 待 itsuki 拍板
- 宅配 expires_at 多久后过期？
- 忘れ物 expires_at 多久销毁？
- 学生取走时怎么确认 (老师手动 / 学生 NFC tap)？

---

## 4. CommunityPost + CommunityComment + community.py (P2)

### 4.1 spec 来源
- spec §7.13 寮掲示板 + リクエスト曲 + 匿名建議

### 4.2 字段提案 (粗)
```python
class CommunityPost(Base):
    id, board_type (notice_board/song_request/anonymous_suggestion),
    author_type (student/teacher/anonymous), author_id,
    title, body, status (active/pinned/resolved/deleted), 
    created_at, pinned_at, resolved_at, resolved_by_teacher_id

class CommunityComment(Base):
    id, post_id, author_id, body, created_at, deleted_at
```

### 4.3 待 itsuki 拍板
- 匿名建議的真实 author_id 是否 backend 保留（防滥用） vs 完全匿名（连 backend 也不知道）
- リクエスト曲 朝/晩 字段（5-23 §8.5.4 (b) pending）
- 老师 pin 权限范围

---

## 5. Notice + notice.py (P2 — 跟 Announcement 区别)

### 5.1 既存 Announcement vs 新 Notice 区别

- **Announcement** (既存 `models.py:Announcement`): 老师 → 学生的官方通知 (FC-027 权限要修)
- **Notice** (新提案): 寮内一般公告 + 行事カレンダー + バス時刻 — 显示在 InfoPage notice/行事/バス 3 tab

### 5.2 字段提案 (粗)
```python
class Notice(Base):
    id, kind (general/event/bus_schedule),
    title, body, event_date (kind=event 时), bus_route_id (kind=bus_schedule 时),
    visible_from, visible_to, created_by_teacher_id, created_at, deleted_at
```

### 5.3 待 itsuki 拍板
- 跟既存 Announcement 是否合并？合并的话 Announcement.kind 加 'general'/'event'/'bus' 字段
- Bus 时刻表是单独 model 还是 Notice.kind='bus_schedule' 的 entry
- 历史 notice 是否给学生看 history

---

## 6. FC-027 announcements 权限重做

### 6.1 当前问题
- `routers/announcements.py` GET /list /detail 依赖 `get_current_student`（学生 token）
- 老师 token 调 → 401 (但老师也要看公告 list 决定要不要发新的)

### 6.2 改法 propose
- 加 `get_current_teacher_or_student` deps function: 同时接受 teacher / student token
- routers/announcements.py GET 端点改用此 deps
- POST 创建仍只老师

### 6.3 工程量 ~1 小时单独修，不依赖其他 model

---

## 7. 推进路径 propose

itsuki 起床后建议路径:

1. **30 分钟 review 本 doc** — 拍板 6 个 model 的字段范围 + ENUM 取值 + points 数值
2. **CC next session 第 1 步**: backend P0 = DemeritEvent + discipline.py + alembic migration (3-4 小时)
3. **CC next session 第 2 步**: teacher_web DisciplinePage 接 backend client.js helper + 渲染真数据 (1 小时)
4. **CC next next session**: 剩 P1 P2 backend + 接入 (重复同样模式)

每一轮 backend → migration → teacher_web fetch + 渲染 = 单 page 真接通。

8 个次要 page 全部接通后 = **v1.0 完整体真上线水平达成**。

---

## 8. CC 5-27 凌晨已替 itsuki 做的（让 itsuki 起床能直接 review 决策）

- ✅ 列出全部 backend 缺失 router 清单（本 doc §0）
- ✅ Propose 主要 model 字段结构（本 doc §1-§5）
- ✅ 标出每个 model 「⏳ 待 itsuki 拍板」字段（避免我替 itsuki 做 spec 决策）
- ✅ Propose 推进路径 + 单会话工作量评估（本 doc §7）

itsuki 起床后**最快 30 分钟 review + 拍板**就能让 next CC session 开始实装 backend P0。

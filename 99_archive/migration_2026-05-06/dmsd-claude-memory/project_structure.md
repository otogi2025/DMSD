# DMSD Project Deep Understanding

## Architecture Overview
- Student App: iOS + Android (students use both, cross-platform solution needed)
- Teacher Web: browser-based management console
- Backend API: FastAPI + PostgreSQL
- Communication: REST API + WebSocket/SSE for real-time seat updates

## Core Business Logic: Roll Call (点呼)

### Time Windows (JST)
Morning weekday normal: 07:37 start → 07:40 on_time_end → 07:45 late_end → 07:45 auto_end
Morning weekday soccer: 07:17 → 07:20 → 07:25 → 07:25
Morning weekend normal: 08:47 → 08:50 → 08:55 → 08:55
Morning weekend soccer: 07:17 → 07:20 → 07:25 → 07:25
Evening weekday all: 21:57 → 22:00 → 22:05 → 22:10
Evening weekend all: 19:57 → 20:00 → 20:05 → 20:10

### Early start by teacher: entire window shifts (preserves durations)
effective_window_start = started_at
effective_on_time_end = started_at + (scheduled_on_time_end - scheduled_window_start)
...etc

### Status Logic
- Seat colors: grey(init) → green(present) → yellow(late) → red(absent)
- Overlay badges: health_flag(red cross), exempt_range(免), absence_request_pending(申)
- Priority: exempt > override > request > auto
- Settle at: min(ended_at, effective_auto_end_at), init→absent (excluding exempt/pending)

### Discipline
- Late: +0.5 points, Absent: +1.0 points
- Monthly >= 4.0 → cleaning duty next month
- Monthly >= 9.0 → confinement next month
- Override triggers score correction (冲正) in ledger

## API Conventions
- Envelope: { "ok": true/false, "data": {}, "error": { "code", "message", "detail" } }
- Auth: Bearer token, student→/student/*, teacher→/teacher/*
- Time: all judgments use server_now (JST), frontend only shows countdown
- remaining_seconds = max(0, effective_late_end_at - server_now)

## 8 Error Codes
UNAUTHORIZED, FORBIDDEN, INVALID_INPUT, NOT_FOUND, SESSION_NOT_RUNNING, TIMEOUT, DUPLICATE_REQUEST, ALREADY_RUNNING

## Key Student API Endpoints
- POST /student/rollcall/checkin
- POST /student/health/report
- GET /student/rollcall/home
- GET /student/rollcall/history/overview
- GET /student/rollcall/history/month

## Database: 30+ tables across 16 modules
Core tables: users, students, teachers, devices, binding_tokens, rooms, entry_points, seat_layouts, seats, rollcall_sessions, rollcall_seat_snapshots, rollcall_events, health_reports, no_show_requests, exempt_ranges, score_ledger, monthly_summaries, disciplinary_actions, audit_logs

## Acceptance Test Scenarios (8)
RC-01: On-time checkin
RC-02: Late checkin
RC-03: Auto absent settlement
RC-04: Teacher manual override (补签)
RC-05: Teacher override "tap and run" (碰了就跑)
RC-06: Dual NFC point verification (A/B)
H-01: Health flag overlay
H-02: Normal health no overlay
AR-01: Absence request submission
AR-02: Teacher approval/rejection

## Dev Checklist Milestones
Stage 0: Scope freeze (done)
Stage 1: Project scaffold (FastAPI + SQLAlchemy + Alembic + PostgreSQL)
Stage 2: Database migration
Stage 3: Auth, permissions, device binding
Stage 4: Roll call main loop (Milestone 1)
Stage 5: Override, audit, score consistency
Stage 6: Health, leave, exemption
Stage 7: Discipline reports (Milestone 2)
Stage 8: Contract lock + test suite
Stage 9: Deploy + trial run
Stage 10: 5 immediate actions (A1-A5)

## File Notes
- .pages files are binary (Apple IWA protobuf), unreadable on Linux
- All .pages content available as PDFs in 99_archive/ (14 files)
- 99_archive PDFs are exported from Google Drive (ファイル - 2026-02-17 naming)
- Some archive PDFs are duplicates

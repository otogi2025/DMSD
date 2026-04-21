-- Tomoshibi Backend 数据库表结构参考（项目代号 DMSD；SQLAlchemy 实际建表用 models.py，本文件供人类阅读）
-- Demo 阶段用 SQLite，部署阶段迁 PostgreSQL 只改 database.py

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    card_uid TEXT UNIQUE,           -- NTAG215 UID（绑卡后填，未绑定为 NULL）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roll_call_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    status TEXT DEFAULT 'active'    -- 'active' / 'ended'
);

CREATE TABLE checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id),
    session_id INTEGER REFERENCES roll_call_sessions(id),
    checkin_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    method TEXT                     -- 'card' / 'shortcut' / 'app'
);

CREATE TABLE outstay_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    destination TEXT,
    reason TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending' / 'approved' / 'rejected'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

CREATE TABLE return_home_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    flight_number TEXT,
    reason TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

-- Demo 用的种子数据（也可以跑 seed.py 生成）
-- INSERT INTO students (name) VALUES ('itsuki'), ('张三'), ('李四');

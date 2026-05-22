# 会话 A 启动 prompt — 第一档必审（维度 1-5）

## 背景

itsuki（伊月 / 中国留学生 / 日本高三 / 零编程基础 / 目标筑波 AC 入试）正在做 DMSD 整体审查作战。

4 个 Claude Code 会话并行：
- 主会话（ID `1779195127-2539`）：计划 + 最终修复 + 汇总
- **你（会话 A）**：第一档维度 1-5（必审 / 上线前最高风险）
- 会话 B：第二档维度 6-10
- 会话 C：第三档维度 11-16 + 逐字精读

## 时间盒

- 现在 ~21:50 日本时间
- 撞墙后 REPL alive 但 API 拒绝
- **01:03（5-20）**：你的 cron 自动 fire 续审（你在启动时必须注册）
- 01:03 - 完成：第二段续审

## 启动动作（按顺序）

1. `cd ~/dev/DMSD`
2. 用 Skill 工具加载 `ac-radar` + `cc-comm-rules`（CLAUDE.md 铁律）
3. 读 `00_admin/WIP.md` 全文 + `CLAUDE.md` 全文 + `05_logs/audit_2026-05-19/_session_prompts/MASTER.md`
4. 注册 session-coord：
   ```
   bash ~/.claude/skills/session-coord/scripts/register.sh "$(hostname -s)-A" "审查作战会话A·第一档维度1-5"
   ```
5. 记下返回的 SESSION_ID
6. 跑 scan：
   ```
   bash ~/.claude/skills/session-coord/scripts/scan.sh <你的 SESSION_ID>
   ```
7. **注册 1:03 自动续命 cron**（用 CronCreate 工具，cron 表达式 `3 1 20 5 *`，recurring=false，durable=true）：

   prompt 内容：
   ```
   续审作战会话 A 自动启动（5-20 01:03）。
   立刻：cd ~/dev/DMSD → 加载 ac-radar + cc-comm-rules → 读 05_logs/audit_2026-05-19/checkpoint_A.md → 从断点续审 → scan.sh 看主会话 + B/C 状态 → 继续写 findings + checkpoint
   ```

8. 留言给主会话报到：
   ```
   bash ~/.claude/skills/session-coord/scripts/message.sh 1779195127-2539 "会话 A 上线，开始审第一档维度 1-5。1:03 cron 已注册。"
   ```

## 你负责的 5 个维度

### 维度 1 — 跨端字段对齐

**审范围**：
- backend：`03_dev/backend/app/models.py` / `app/schemas.py` / `app/routers/*.py` / `alembic/versions/*`
- iOS：`03_dev/student_ios/.../NetworkModels.swift` / `Endpoints/*API.swift`
- Android：`03_dev/student_android/.../entity/*` + 任何 API model 类

**找**：
- 字段命名漂移（如 `student_id` vs `studentId` vs `studentID`）
- 类型不一致（如 backend `Optional[str]` vs iOS 非 Optional）
- 缺字段（backend 有但客户端没 / 客户端有但 backend 没）
- API endpoint 路径 / 参数 / 返回类型对不上

**参考工具**：`spec-sync` skill（用 Skill 工具加载跑）

### 维度 2 — 联动矩阵全过

**审范围**：`CLAUDE.md` §文件连锁结构 列的 17 条「改 A 必查 B」规则。

**找**：每条规则，检查最近 commit history 有没有违反过 — 改了 A 但 B 没跟上。

**参考工具**：`bash bin/sync-check.sh` + `file-linkage` skill

### 维度 3 — 设计文档分层一致

**审范围**：
- `02_design/system_features.md`（≥2 端共用层真值）
- 5 端 `*_DESIGN_LOG.md`：`student_ios` / `student_android` / `teacher_web` / `backend` / `rollcall_device`

**找**：
- 共用层有的功能在某端 DESIGN_LOG 没引用
- 某端 DESIGN_LOG 跟共用层冲突
- 字段 / 流程 / 状态机定义跟实际代码对不上

### 维度 4 — demo scaffold 清单 vs 实际代码

**审范围**：读 memory `/Users/kurekoduki/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/project_demo_scaffolds_to_remove_before_v1.md` 列的所有 demo-only 代码。

**找**：
- 清单里列的 demo 代码现在还在哪些文件
- 漏列的明显 demo 痕迹（hardcoded "demo" / "test" / "TODO: remove before prod"）

### 维度 5 — NFC 安全审查

**审范围**：
- backend：`auth.py` / `routers/checkin*.py` / `routers/auth*.py` / 涉及 ECDSA 签名验证的代码
- iOS / Android：NFC 读取 + 签名验证逻辑
- 点呼机：`03_dev/rollcall_device/src/` 涉及 NFC 写卡 / nonce 生成

**找**：
- 鉴权漏洞（无认证端点 / 弱认证）
- 输入验证缺失（SQL 注入 / XSS）
- 密钥管理（硬编码 secret / .env 泄露）
- 权限提升路径（学生越权改老师权限）
- 防作弊完整性：NFC nonce / ECDSA 签名 / 学生注册码各自漏洞

**建议**：用 Skill 工具加载 `security-reviewer` 子代理跑这个维度。

## 硬约束

1. **只审 + 列问题，不改文件 / 代码 / spec**（CLAUDE.md memory `audit_means_find_not_fix` 铁律）
2. 每条问题：`file:line` + 描述 + 建议改法 + 严重程度（🔴 阻塞上线 / 🟡 该修 / 🟢 优化）
3. 跨文件关联是重点 — 找「A 改了 B 没跟上」
4. 不删 / 不 commit / 不 push
5. 改共享文件（`_board.md` / `_master_issues.md`）前 `claim.sh`，改完 `release.sh`
6. 每次回合自动跑 `scan.sh <你的 SESSION_ID>` 顺手刷心跳（3 分钟没动作会被判死）

## findings 写到这里

`05_logs/audit_2026-05-19/session_A_findings.md`

### 格式

```
### [A-001] 🔴 跨端字段命名漂移：student_id 不一致

- **文件**：`03_dev/backend/app/models.py:42` vs `03_dev/student_ios/.../NetworkModels.swift:18`
- **维度**：1
- **描述**：backend 是 `student_id` snake_case，iOS 是 `studentId` camelCase，没 JSON key mapping
- **建议改法**：iOS 加 `CodingKeys` 或 backend 用 `alias_generator`
- **跨会话**：N/A
```

## checkpoint 写到这里（撞墙前必写）

`05_logs/audit_2026-05-19/checkpoint_A.md`

### 格式

```
# 会话 A checkpoint — 2026-05-19 撞墙前

## 已审完
- 维度 1：backend models.py ✅ / iOS NetworkModels.swift ✅ / Android entity ⏳

## findings 总数
12 条（已写到 session_A_findings.md）

## 没审完
- Android entity 全扫
- 维度 5 NFC 安全：auth.py 剩 line 200-450

## 01:03 续审起点
1. 先续 NFC auth.py
2. 再续 Android entity
3. 维度 3 设计分层（还没开始）
```

## 沟通

- 留言给主会话：`bash ~/.claude/skills/session-coord/scripts/message.sh 1779195127-2539 "msg"`
- 留言给 B / C：先 scan 看对方 ID，再 message.sh

## 第一段优先级

1. **维度 5 NFC 安全** — 全审完（上线前最高风险）
2. **维度 1 字段对齐** — 全审完
3. 维度 2 联动 — 至少过半
4. 维度 3 / 4 — 时间允许就审

开始吧。

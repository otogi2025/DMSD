# 会话 C 启动 prompt — 第三档长尾 + 逐字精读（维度 11-16+）

## 背景

itsuki（伊月 / 中国留学生 / 日本高三 / 零编程基础 / 筑波 AC 入试）正在做 DMSD 全量审查作战。

4 个 Claude Code 会话并行：
- 主会话（ID `1779195127-2539`）：计划 + 最终修复 + 汇总
- 会话 A：第一档维度 1-5
- 会话 B：第二档维度 6-10
- **你（会话 C）**：第三档维度 11-16 + 逐字精读

## 时间盒

- 现在 ~21:50
- 01:03（5-20）：你的 cron 自动 fire 续审
- 01:03 - 完成：第二段

## 启动动作（按顺序）

1. `cd ~/dev/DMSD`
2. 加载 `ac-radar` + `cc-comm-rules`
3. 读 `00_admin/WIP.md` + `CLAUDE.md` + `05_logs/audit_2026-05-19/_session_prompts/MASTER.md`
4. 注册：
   ```
   bash ~/.claude/skills/session-coord/scripts/register.sh "$(hostname -s)-C" "审查作战会话C·第三档维度11-16+精读"
   ```
5. 记下 SESSION_ID
6. `bash ~/.claude/skills/session-coord/scripts/scan.sh <SESSION_ID>`
7. **注册 1:03 cron**（CronCreate，cron `3 1 20 5 *`，recurring=false，durable=true）：

   prompt：
   ```
   续审作战会话 C 自动启动（5-20 01:03）。
   立刻：cd ~/dev/DMSD → 加载 ac-radar + cc-comm-rules → 读 05_logs/audit_2026-05-19/checkpoint_C.md → 从断点续审 → scan 看 4 会话状态 → 继续写 findings + checkpoint
   ```

8. 报到主会话：
   ```
   bash ~/.claude/skills/session-coord/scripts/message.sh 1779195127-2539 "会话 C 上线，开始审第三档维度 11-16 + 逐字精读。1:03 cron 已注册。"
   ```

## 你负责的 6 个维度 + 逐字精读

### 维度 11 — AC 叙事时间线连贯

**审范围**：
- `05_logs/decision_log.md`
- `05_logs/project_evolution.md`
- `05_logs/learning_path.md`
- `05_logs/raw/*.md`（按日期）

**找**：
- 同一事件 3 个文件时间不一致（decision_log 说 5-04，project_evolution 说 5-05）
- raw/ 文件名日期跟内容日期不符
- 引用了不存在的 raw 文件
- 内部时间顺序矛盾（5-10 的事件引用了 5-12 才发生的事）

### 维度 12 — commit history vs 实际改动

**审范围**：
- `git log --oneline -200` 最近 200 commits
- 每个 commit 的 `git show <hash>` 跟 commit message 比对

**找**：
- commit message 说改了 X 但 diff 完全没碰 X
- commit message 说改了 X 但同时还改了 Y（混议题）
- 多个 commit 描述模糊（"修一些 bug" 这种）

### 维度 13 — AC 素材漏抓

**审范围**：
- `05_logs/raw/2026-05-*.md` 全部 5 月份
- 中央 inbox：跑 `python3 ~/.claude/skills/ac-radar/scripts/find_ac_root.py` 拿 root → `{AC_ROOT}/06_radar_inbox/`

**找**：
- raw/ 里有"决策 / 拍板 / 反思 / 学到"标记但中央 inbox 没记
- raw/ 里有「以前我 / 原来 / 我之前以为」模式 5 触发词但没打 AC tag
- 5-19 当天 raw 有候选但 ac-radar 没抓

### 维度 14 — 跨项目残留

**审范围**：
- `~/dev/Tango/`（5-14 立项）
- `~/dev/SC26/`（如果存在）
- `~/dev/cc-project-template/`（如果存在）
- 6 个 skill 的 5-14 / 5-16 改动

**找**：
- DMSD 路径硬编码在别的项目（197 处 5-16 立 TODO §🛠️ G 跟进项）
- skill 描述里写 DMSD 但跑到别项目里
- hook 路径错位

### 维度 15 — 依赖 CVE（已知漏洞编号）

**审范围**：
- `03_dev/backend/requirements.txt` 或 `pyproject.toml`
- iOS `Package.swift` / `Podfile`
- Android `build.gradle` / `build.gradle.kts`

**找**：
- 列出所有 third-party 依赖 + 版本号
- 标记主要依赖（不深扫，只识别常见 CVE 数据库已收录的旧版）
- 建议：哪些版本明显该升

**注意**：不真跑 `pip-audit` / `npm audit`（不改 lockfile / 不动 venv），只读列表。

### 维度 16 — 后端测试

**审范围**：
- `03_dev/backend/tests/`（如果存在）
- `03_dev/backend/pytest.ini` / `pyproject.toml` 测试配置
- 看 CI 配置文件（`.github/workflows/*` 如果存在）

**找**：
- 有没有真测试代码（不是空壳）
- 测试覆盖关键路径吗（auth / checkin / nfc 验证）
- 测试能跑通吗（读测试代码逻辑，不真跑）

### 维度 17（额外）— 逐字精读

**审范围**：所有「声明性文件」（不是代码）：
- `CLAUDE.md`
- `00_admin/WIP.md` / `TODO.md` / `progress_overview.md` / `文档同步点清单.md` / `文件结构指南.md`
- `CHANGELOG.md`
- `01_specs/rollcall/*.md`
- `02_design/*.md`
- 5 端 `*_DESIGN_LOG.md`
- `README.md`

**找**：
- 笔误 / 错字 / 中日英混杂的明显错误
- 引用文件不存在
- 不准确措辞（如「v1.0 一次上线」但实际是「v1.0 不一次上线」）
- 数字 / 日期 / 版本号自相矛盾
- 描述 vs 实际状态不符（说"已完成"实际没做）

## 硬约束

1. **只审 + 列问题，不改**
2. 每条：`file:line` + 描述 + 建议改法 + 严重程度
3. 跨文件关联是重点
4. 不删 / 不 commit / 不 push
5. 改共享文件前 `claim.sh`
6. 每回合 `scan.sh` 刷心跳

## findings 写到

`05_logs/audit_2026-05-19/session_C_findings.md`

## checkpoint 写到（撞墙前必写）

`05_logs/audit_2026-05-19/checkpoint_C.md`

## 第一段优先级

1. **维度 17 逐字精读** — 最容易出活 + 影响面广（先扫 CLAUDE.md / WIP / TODO / system_features）
2. **维度 12 commit vs 改动** — 中等量
3. **维度 11 AC 时间线** — 中等量
4. 维度 13 / 14 / 15 / 16 — 时间允许就审

开始吧。

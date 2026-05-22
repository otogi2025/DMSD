# 会话 B 启动 prompt — 第二档该审（维度 6-10）

## 背景

itsuki（伊月 / 中国留学生 / 日本高三 / 零编程基础 / 筑波 AC 入试）正在做 DMSD 全量审查作战。

4 个 Claude Code 会话并行：
- 主会话（ID `1779195127-2539`）：计划 + 最终修复 + 汇总
- 会话 A：第一档维度 1-5
- **你（会话 B）**：第二档维度 6-10
- 会话 C：第三档维度 11-16 + 逐字精读

## 时间盒

- 现在 ~21:50
- 01:03（5-20）：你的 cron 自动 fire 续审
- 01:03 - 完成：第二段

## 启动动作（按顺序）

1. `cd ~/dev/DMSD`
2. 用 Skill 工具加载 `ac-radar` + `cc-comm-rules`
3. 读 `00_admin/WIP.md` + `CLAUDE.md` + `05_logs/audit_2026-05-19/_session_prompts/MASTER.md`
4. 注册：
   ```
   bash ~/.claude/skills/session-coord/scripts/register.sh "$(hostname -s)-B" "审查作战会话B·第二档维度6-10"
   ```
5. 记下 SESSION_ID
6. `bash ~/.claude/skills/session-coord/scripts/scan.sh <SESSION_ID>`
7. **注册 1:03 自动续命 cron**（用 CronCreate，cron `3 1 20 5 *`，recurring=false，durable=true）：

   prompt：
   ```
   续审作战会话 B 自动启动（5-20 01:03）。
   立刻：cd ~/dev/DMSD → 加载 ac-radar + cc-comm-rules → 读 05_logs/audit_2026-05-19/checkpoint_B.md → 从断点续审 → scan 看 4 会话状态 → 继续写 findings + checkpoint
   ```

8. 报到主会话：
   ```
   bash ~/.claude/skills/session-coord/scripts/message.sh 1779195127-2539 "会话 B 上线，开始审第二档维度 6-10。1:03 cron 已注册。"
   ```

## 你负责的 5 个维度

### 维度 6 — 规格主体一致性

**审范围**：
- `01_specs/rollcall/RollCall_Spec_v0.1.md`（主体）
- `01_specs/rollcall/dictionary_v0.1_v0.2_v0.3.md`（字典三件套）
- 其他 `01_specs/rollcall/*` 文件

**找**：
- 字典三件套术语 vs 主体术语对齐（同一个概念两边用不同词）
- 主体引用字典定义但字典没那一项
- 字典定义但主体没用到（孤儿术语）

### 维度 7 — 物理硬件 vs 点呼机软件

**审范围**：
- `02_design/hardware_design.md`（板子选型 / 模块 / BOM / 接线）
- `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md`（点呼机软件层）
- `03_dev/rollcall_device/src/`（实际代码）

**找**：
- GPIO 针脚定义跟硬件 design doc 对不上
- 模块选型（PN532 NFC reader / ST25DV16K 卡）跟软件代码引用的模块不一致
- BOM 列的零件软件没用 / 软件用的零件 BOM 没列

### 维度 8 — memory 索引完整性

**审范围**：
- `~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/MEMORY.md`（索引）
- 同目录下所有 `feedback_*.md` / `project_*.md` / `user_*.md`

**找**：
- MEMORY.md 索引指的文件不存在（链接死）
- 实际存在但 MEMORY.md 没索引的文件（孤儿文件）
- 两条 memory 内容自相矛盾
- 描述说一回事，正文写另一回事

### 维度 9 — 挂钩系统审查

**审范围**：
- `00_admin/hooks/README.md`（挂钩清单）
- `00_admin/hooks/*.sh`（实际脚本）
- `00_admin/hooks/pre-commit`（git pre-commit）
- `00_admin/hooks/lib/sync-rules.sh`（规则源）
- `.claude/settings.json`（Claude Code 挂钩注册）
- `~/.claude/hooks/`（全局挂钩）

**找**：
- README.md 列的挂钩实际不存在 / 实际存在但 README 没列
- 重复挂钩（两个脚本做同一件事）
- 失效挂钩（脚本里 path 已迁但没更新）
- 漏配（settings.json 没注册的脚本）

### 维度 10 — TODO.md 真值审查

**审范围**：
- `00_admin/TODO.md`（完整 backlog）
- `00_admin/WIP.md`（书签 / 最近 5 会话）

**找**：
- TODO 里已完成项还挂着（应该删 / 标完成）
- TODO 跟 WIP 内容重叠（违反 WIP.md 铁律 §职责分工）
- 优先级跟当前阶段不匹配（demo 已过但还在 demo 任务）
- 描述过期（项目状态变了但 TODO 没更新）

## 硬约束

1. **只审 + 列问题，不改**（CLAUDE.md memory `audit_means_find_not_fix`）
2. 每条问题：`file:line` + 描述 + 建议改法 + 严重程度（🔴 / 🟡 / 🟢）
3. 跨文件关联是重点
4. 不删 / 不 commit / 不 push
5. 改共享文件前 `claim.sh`
6. 每次回合 `scan.sh <SESSION_ID>` 刷心跳

## findings 写到

`05_logs/audit_2026-05-19/session_B_findings.md`

格式同 A.md（见 `_session_prompts/A.md` 维度 1 example）

## checkpoint 写到（撞墙前必写）

`05_logs/audit_2026-05-19/checkpoint_B.md`

## 第一段优先级

1. **维度 10 TODO 真值** — 最快出活（找完成项还挂着的）
2. **维度 8 memory 索引** — 中等量
3. **维度 9 挂钩系统** — 跟最近 5-19 改动相关
4. 维度 6 / 7 — 时间允许就审

开始吧。

# 4 会话审查作战 — 启动说明（给 itsuki）

## 怎么开 3 个子会话

打开 3 个新的 Claude Code 窗口（独立进程），分别在第一个对话框贴：

### 会话 A（第一档·必审）

```
读 ~/dev/DMSD/05_logs/audit_2026-05-19/_session_prompts/A.md 按里面执行
```

### 会话 B（第二档·该审）

```
读 ~/dev/DMSD/05_logs/audit_2026-05-19/_session_prompts/B.md 按里面执行
```

### 会话 C（第三档·长尾+精读）

```
读 ~/dev/DMSD/05_logs/audit_2026-05-19/_session_prompts/C.md 按里面执行
```

## 主会话（这个 — 你正在用的）

已经注册：
- session-coord ID = `1779195127-2539`
- 1:03 cron 已 schedule（撞墙后自动续）

## 撞墙后会发生什么

- 4 个会话 REPL alive，API 拒绝
- 3:00 配额重置
- **1:03**：4 个 cron 同时 fire → 4 会话自动续审

## 早上你醒来

- 打开 4 个窗口看进度
- 主会话已经汇总好 `_master_issues.md`
- 跟主会话过一遍清单 → 拍板修哪些 → 主会话动手修

## 关键文件位置

```
05_logs/audit_2026-05-19/
├── _session_prompts/
│   ├── _README.md      ← 你正在读
│   ├── MASTER.md       ← 主会话角色说明
│   ├── A.md            ← 子会话 A 启动 prompt
│   ├── B.md            ← 子会话 B 启动 prompt
│   └── C.md            ← 子会话 C 启动 prompt
├── _master_issues.md   ← 主会话汇总用
├── session_A_findings.md  ← 子会话 A 写
├── session_B_findings.md  ← 子会话 B 写
├── session_C_findings.md  ← 子会话 C 写
├── checkpoint_A.md     ← 子会话 A 写（撞墙前）
├── checkpoint_B.md     ← 子会话 B 写（撞墙前）
└── checkpoint_C.md     ← 子会话 C 写（撞墙前）
```

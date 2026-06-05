# GOAL 提示词 · 老师网页 React+TS+Vite 迁移

> compact 后把下面「===」之间的全部内容粘进对话，新会话照此自主执行。

```
===

【任务】把老师网页（teacher_web）从「单文件 index.html + 浏览器内 Babel 编译 React」
迁移成「React + TypeScript + Vite」正规工程，界面 100% 不变，部署到服务器。

【第一件事 — 必做】先读这三份，恢复全部上下文：
1. 施工清单（单源真值，照它干）：03_dev/teacher_web/Vite迁移_施工清单.md
2. memory：project_teacher_web_vite_migration.md（迁移决策）
   + feedback_no_zero_basis_excuse.md（别拿零基础说事）
3. 5-26 失败复盘：05_logs/raw/2026-05-26_teacher_web_vite废弃+polish回滚.md
   + 归档配置参考：99_archive/2026-05-26_teacher_web_vite实装作废/（只参考工程配置，界面不可用）

【铁律 — 违反就是重蹈 5-26 覆辙】
- 界面 100% 冻结：现在的页面布局/内联样式/Ryō 配色，逐页原样搬，一个像素不改外观，绝不重新设计
- 每搬完一页，跟旧 index.html 版肉眼对比该页，一致了再搬下一页
- 样式保持内联 style + RYO 配色（迁成 import 的 theme 模块），不改 Tailwind
- 状态用 React 自带 useState + Context，不引 Zustand 等库
- 别拿「itsuki 零基础/维护难」当任何论据

【技术栈 — 已定】React 18 + TypeScript（一步到位）+ Vite + 内联样式 + React Context。
node v25 / npm 11 已确认可用。

【按施工清单 §4 五阶段执行】
阶段1 搭 Vite+TS 骨架 → 阶段2 抽公共层(theme/api/types) → 阶段3 逐页搬 16 页 →
阶段4 组装外壳+路由+全局状态 → 阶段5 切换托管+全面逐页对比回归。
每阶段做完先验证（见清单 §4 各阶段验证 + §5 总验证标准）再进下一阶段。

【执行约束】
- 每个有意义的节点 git commit：中文 message，不写 Co-Authored-By，绝不 git push
- 多会话共用 git 工作区：commit 前 git diff --cached 核对，只提交本次改的、用显式 pathspec，
  不 git add -A（防带走别会话改动）
- 不碰：后端业务逻辑（接口不变）、iOS、Android、specs(01_specs/)。只动 teacher_web 前端 +
  必要的启动/托管脚本
- 进度实时更新到施工清单 §8

【审查 — 每完成一个阶段】
- 派 workflow 多审查员并行审（界面是否真没变 / 类型对不对 / 字段对齐后端 / 构建是否通）+ 对抗验证
- 派 codex（gpt-5.5 xhigh）只读审，CC 自己逐条裁决+核实再修，不盲信
- 自己也要审（不只靠 agent），改完独立验证 agent 自报

【完成条件（任一不满足就继续）】
施工清单 §5 全绿：npm run build 0 错误 + tsc 0 错误 + 16 页+登录逐页界面跟旧版一致 +
核心功能(登录/代録/出寮者一覧/审批/点呼/学習)跑通 + 后端 295 测试仍全过。

【顺带的独立任务（可并行、不阻塞迁移）】
后端邮件换 Resend：改 03_dev/backend/v1/app/services/email.py（现在是 SendGrid），
没密钥时 dev 模式不真发。待 itsuki 注册 Resend 拿密钥。带 pytest。

===
```

---

## 配套文件

- **施工清单（要做的全部）**：`03_dev/teacher_web/Vite迁移_施工清单.md`
- **本 GOAL 提示词**：`00_admin/老师网页Vite迁移_GOAL提示词.md`

## 给 itsuki 的话

- 现在**没开工**，等你 compact 完粘贴上面 GOAL 触发
- 迁移期间老师网页旧版（`index.html`）照常能用，迁完才切换
- 邮件 Resend 那条独立，等你注册拿密钥

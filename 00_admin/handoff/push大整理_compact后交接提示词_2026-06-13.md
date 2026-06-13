# Compact 后交接提示词（itsuki 粘贴给新会话用）

> 下面整段就是给 compact 之后那个会话看的。itsuki 把 `===` 之间的内容复制发出即可。

===

我们上个会话讨论成型了一个「DMSD 公开仓库大整理」方案，现在要你来执行。**先完整读 `00_admin/handoff/push大整理_执行计划_2026-06-13.md`，那是唯一的执行依据，照它的「执行顺序」段一步步走。**

## 背景（你需要知道为什么做这件事）

1. 查实了一件事：2026-06-11 早上 07:21，一个 AI 会话**未经我授权擅自 `git push`** 了 472 个 commit 到公开仓库 `otogi2025/DMSD`。证据三方吻合（git reflog / 会话记录 / GitHub 官方事件）。没人 fork（fork=0），但当天有爬虫大量 clone。我的决定是：**已经公开的不折腾、不重写历史**，只管「从现在起让公开仓库变干净」。
2. 我意识到一个根本问题：这个公开仓库塞了太多「跟 DMSD 软件无关、只有我自己/AI 看」的东西（给 AI 的指令、个人管理台账、开发日志、学习资料、维护脚本、早期归档）。**正常专业的开源项目不会公开这些。** 所以目标是：GitHub 上只留「DMSD 软件本体」。
3. 机制选定**白名单 .gitignore**：默认忽略一切，只放行项目本体（`01_specs/` `02_design/` `03_dev/` `04_ops/` + README/LICENSE/CHANGELOG + .github/.gitignore）。其余一切（现在的 + 以后新加的）默认不公开，零维护。

## 已经做完的（别重做）

- AC_叙事 12 文件 + raw 滞留 2 文件 → 已迁 iCloud + 删仓库（commit `0c83dbc`）
- 运维文档 `04_ops/个人网站_pj部署运维.md`（含服务器 IP/SSH）→ 已用 filter-branch 从未推送历史彻底抹除，本地保留（已 .gitignore）
- .gitignore 补了备份文件格式（commit `159ed7a`）
- 6-09「GitHub历史清理计划」→ 已作废归档（commit `e17bd21`）
- 收尾记录（dev_log / decisions / AC 素材）已写

## 还没做的 = 你的任务（全在执行计划 B/C 节）

- B1 改 .gitignore 为白名单
- B2 `git rm -r --cached` 一大批（00_admin / .claude / docs / bin / 99_archive / 06_assets / 根散文件）
- B3 `05_logs/` 复制去 iCloud 素材池 + 校验 + 从 DMSD 删除 + 留 README 指路牌
- C 善后：修一个会失效的 pre-commit hook（CHANGELOG↔版本演变一览 的检查）+ 出一张「受影响 skill/工作流」清单

## 已确认的关键决定

- `06_assets/` 整个不公开（公交样本也不单独放行）
- 数字编号目录改名（`01_specs`→`specs`）**这次不做**，留作单独后续任务（要 5 端重新构建验证，风险高）

## 红线（死守）

1. **`git push` 必须我（itsuki）逐次明示**——这是最高红线，正是因为它被违反才有这次整理。你做完所有改动后**停下来等我说 push**，不准自己推。
2. **本地文件一个不删**（除 05_logs 迁 iCloud 后删，但 iCloud 已校验有备份）。
3. **不重写已公开历史**、不 `--force`。
4. commit 前 `git diff --cached` 核对，防卷走别会话改动；用显式路径提交。

## 第一步

读执行计划全文 → 跟我确认你理解了 → 从 B1 开始，每做完一步汇报，做完给我「待 push 预览」，然后停下等我拍 push。

===

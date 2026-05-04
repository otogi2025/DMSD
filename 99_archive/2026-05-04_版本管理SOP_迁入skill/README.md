# 版本管理 SOP 归档说明

> **归档时间**：2026-05-04 深夜
> **替代物**：`.claude/skills/version-bump/SKILL.md`
> **归档原因**：v3 → v4 迁入 Claude Code Skill 系统

## 为什么归档

原文件 `00_admin/版本管理SOP.md` 整体迁入 `.claude/skills/version-bump/` skill，理由：

1. **触发型规则适合做 skill** — 不是每次会话都用，bump 时才用
2. **按需加载省 CLAUDE.md token** — 旧 SOP 341 行每次会话都不会主动读，做成 skill 后触发关键词命中时才加载
3. **强制铁律落地** — 实战发现 v0.6.0 / v0.8.0 没更新到`版本演变一览.md`，做成 skill 后能用 skill §0.2 铁律强制
4. **加 itsuki 4 条新指令** — CC 否决权 / 版本演变一览必更新 / 全量扫描 / 加「迭代」关键词

## 跟 skill 的差异

| 维度 | 旧 SOP | 新 skill |
|---|---|---|
| 联动文件数量 | 6 处 | **7 处**（加 `项目文件总览.md` 半必）|
| CC 否决权 | 隐含 | **显式 §0.1 铁律 + 否决话术** |
| 版本演变一览强制 | §4 第 3 行 | **§0.2 铁律 + 历史漂移 case study** |
| 全量扫描 | 无 | **§0.3 + §4 全量扫描清单（grep VERSION_OK / git log diff-filter）** |
| 触发关键词 | 「bump / 打 tag / 迭代版本」 | **加「迭代 / 升级版本 / 发布 / release」** |

## 历史价值

本 SOP（v0.4.0 建立）记录了 DMSD 早期版本管理踩过的坑：
- 4-21 → 4-29 9 天没 bump 的根因
- 0.x SemVer 约定（破坏性也用 minor）
- staging area 污染防御（4-29 实战教训）
- 文件名版本号规则演变

→ 这些 case study 在新 skill 里都保留了。

## 不再用旧 SOP，请直接调用 skill

```
itsuki 输入：
- 「迭代」/「bump」/「发版本」/「打 tag」/「升级版本」 → CC 自动激活 version-bump skill
- /version-bump → 显式调用
```

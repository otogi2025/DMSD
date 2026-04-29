# 03_dev/teacher_web/v1/

**老师 Web v1.0 正式版 — 未开始**。

## 启动条件

v1.0 Web 开发需要先完成：
- [ ] `02_design/system_features.md` 重写
- [ ] `RollCall_Spec.md` 5 处修订完成（2026-04-29 已改）
- [ ] 「点呼総結」中层页设计（详见 `RollCall_Spec.md §5.6`）
- [ ] 共用功能完整：出寮届承认 / 行事予定編集 / 寮生特别运航便录入 / 学生数据查看 / 事案录入 / 指导履歴

## 起点

从 `../demo/` 复制 round3 代码作为起点（design system Ryō tokens / Cobalt 配色 / Noto Sans JP / 已实装的座席表 + roll-call landing），重写：
- 真后端连接（替换 demo_server.py 的内存模拟）
- 角色 / 权限分流（5 角色见 `system_features.md`）
- 1·2 寮 / 4 寮 分别显示（R4）
- 邮件通知（R1）
- 事务室 PC 出寮者一覧打印功能（●）
- 砍掉社区功能、学生发帖、匿名建议（4-29 itsuki 砍/留）

## 设计权威

- 共用规则: `02_design/system_features.md`
- Web 専属设计: `../WEB_DESIGN_LOG.md`

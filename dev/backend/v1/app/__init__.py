"""Tomoshibi Backend v1.0 — application package.

DMSD (项目代号) / Tomoshibi (产品名 = 灯火 / ともしび).
对称 demo/ — demo 锁定不动, v1/ は本会话 (Mac-轨道C 后续) 起从零搭建。

P0 范围 (会话 B 担当, 2026-04-30):
- #2 出寮届 schema (帰省 / 外泊 / 帰国)
- #5 承认状态查询
- #6 SendGrid メール通知 (R1)
- #7 食堂食数计算 + Excel 导出
"""

# 本后端包自身的版本号（v1 后端首个完整版）。独立于项目 SemVer（见 CHANGELOG.md 的 v0.x.y）——
# 喂给 FastAPI(version=)，只出现在 /docs、/openapi.json、根路由等技术接口面，不进用户可见的 app 界面。
__version__ = "1.0.0"

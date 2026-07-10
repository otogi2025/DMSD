"""
Tomoshibi 点呼机主程序入口

⚠️ 实装进度: 0% — 当前 placeholder（A-009 / A-027）
    src/ 下所有 module（nfc / api / led / audio）均为空 __init__.py。
    spec / 设计文档已完整，硬件采购 + Pi 上手编程未开始。

详细设计 / 模块边界 / 状态机 → ROLLCALL_DEVICE_DESIGN_LOG.md §3 主循环 + §4 模块设计
启动前提 / 硬件清单 → ROLLCALL_DEVICE_DESIGN_LOG.md §1.2 + hardware_design.md §2

骨架占位 — 实装见 ROLLCALL_DEVICE_DESIGN_LOG.md §3 主循环 + §4 模块设计。
"""

# 实装时填充
# 状态机: IDLE → SUBMITTING → SUCCESS / FAIL → IDLE
# NFC 路径: PN532 轮询读卡 UID + 被动收手机写入 ST25DV16K 邮箱的身份数据
# （nonce 10 秒刷新方案已随 2026-06-02 架构反转废弃 — 手机不联网、点呼机不再主动写贴纸）

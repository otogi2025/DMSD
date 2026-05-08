"""
Tomoshibi 点呼机主程序入口

骨架占位 — 实装见 ROLLCALL_DEVICE_DESIGN_LOG.md §3 主循环 + §4 模块设计。
"""

# 实装时填充
# 状态机: IDLE → SUBMITTING → SUCCESS / FAIL → IDLE
# 后台线程: 每 10s 写 nonce 到 ST25DV16K

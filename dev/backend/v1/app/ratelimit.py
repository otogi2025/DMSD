"""限速器单例（slowapi）— 按客户端 IP 识别。

全后端共用这一个 limiter 实例：main.py 挂中间件 + 异常处理器，
accounts / auth 等接口用 @limiter.limit 装饰器。集中成单例保证计数真正共享、
enabled 开关只控一处（原先 main/accounts/auth 各建独立实例，计数互不相通）。

enabled 策略：仅 staging / production 启用限速；dev（含 pytest 测试套件）关闭。
否则测试里大量登录会瞬间撞 429，且本地开发不需要限速。
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import get_settings

# dev（含测试）关、staging / production 开
_rate_limit_enabled = get_settings().app_env in ("staging", "production")

limiter = Limiter(key_func=get_remote_address, enabled=_rate_limit_enabled)
